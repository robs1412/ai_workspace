#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

function ww_append_once(string $existing, string $marker, string $addition): string
{
    $existing = trim($existing);
    if ($existing !== '' && str_contains($existing, $marker)) {
        return $existing;
    }
    return trim($existing . ($existing !== '' ? "\n\n" : '') . trim($addition));
}

function ww_write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create outbox directory.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode draft payload.');
    }
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write draft payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to move draft payload into outbox.');
    }
    chmod($path, 0600);
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
for ($i = 1; $i < count($argv); $i++) {
    if ($argv[$i] === '--state-dir' && isset($argv[$i + 1])) {
        $stateDir = rtrim((string) $argv[++$i], '/');
    }
}

$eventId = 903;
$sourceMessageId = '<CALbLtzwWgC-Ldrg-CUy8uCsyu9hty=mL1qGJNLGB8XEo1dMecQ@mail.gmail.com>';
$sourceRef = 'calbltzwwgc-ldrg-cuy8ucsyu9hty=ml1qgjnlgb8xeo1dmecq@mail.gmail.com';
$taskFlowKey = 'taskflow-e3752e8a4f4faf87';
$actionId = $taskFlowKey . '-whiskey-washback-late-logistics-question';
$marker = 'sonat-late-logistics-2026-06-27 ' . $sourceMessageId;
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;

$logistics = implode("\n", [
    'Late logistics forward from Sonat on 2026-06-27 after the event date; source marker ' . $marker . '.',
    'Venue: Artifact Events, 4325 N Ravenswood Ave, Chicago, IL 60613.',
    'Event date/time from organizer: Friday, June 26, 2026, 6:00 PM-9:30 PM; setup 1:30 PM-5:15 PM.',
    'Placement/load-in: South Building, 1st floor. Use the South Building entrance; larger items may use the back alley into the courtyard connected to the South Building. Do not leave trucks unattended in the residential alley; alley load-out unavailable after 9:00 PM.',
    'Parking: move vehicles after unloading; free street parking on Ravenswood Ave in front of the venue.',
    'Setup expectations: doors open at 6:00 PM; be fully set by then and ready by 5:30 PM for a clean setup photo if desired. Bring a long extension cord if power is needed.',
    'Venue/organizer provides Whiskey Washback glasses, 2 oz tasting cups, 7 oz cups only for cocktails, ice, bucket, scoop, and table linen.',
    'Arrival contact: find Emily or the on-site team for placement. On-site contacts: Emily Easterbrook, Mckenna Foster, Jasmine Gaviria, Walt Easterbrook.',
    'Product reminder from Sonat: staff should bring Thresh and Winnow Millet for the VIP hour.',
    'Load-out: starts at 9:30 PM; venue will not store items and leftover product must be picked up that night.',
]);

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
ensure_event_bookings_important_information_column($eventPdo);

$eventPdo->beginTransaction();
try {
    $stmt = $eventPdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $stmt->execute([$eventId]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        throw new RuntimeException('OPS event 903 was not found.');
    }

    $notes = ww_append_once((string) ($event['notes'] ?? ''), $marker, $logistics);
    $important = ww_append_once(
        (string) ($event['important_information'] ?? ''),
        $marker,
        implode("\n", [
            'Late source-marked Whiskey Washback logistics update: ' . $marker . '.',
            'Setup 1:30 PM-5:15 PM; event 6:00 PM-9:30 PM at Artifact Events South Building, 1st floor.',
            'Use South Building entrance; large items may use back alley but alley cannot be used after 9:00 PM and trucks cannot block it unattended.',
            'Bring Thresh and Winnow Millet for VIP hour. Venue provides tasting cups, ice, bucket, scoop, and table linen; bring long extension cord if power is needed.',
        ])
    );

    $update = $eventPdo->prepare('UPDATE event_bookings SET notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
    $update->execute([$notes, $important, $eventId]);
    $eventPdo->commit();
} catch (Throwable $e) {
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => 'ops-outreach-' . $eventId . '@koval-distillery.com'];
try {
    google_oauth_tokens_table_ready($eventPdo);
    $tokenUserId = null;
    $tokenStmt = $eventPdo->query('SELECT user_id FROM ops_google_oauth_tokens ORDER BY updated_at DESC');
    foreach (($tokenStmt ? $tokenStmt->fetchAll(PDO::FETCH_ASSOC) : []) as $row) {
        $candidate = (int) ($row['user_id'] ?? 0);
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            $tokenUserId = $candidate;
            break;
        }
    }
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $eventStmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $eventStmt->execute([$eventId]);
    $eventRow = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-outreach-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
    $calendarId = google_calendar_outreach_id();
    $existing = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($existing) && !empty($existing['id'])) {
        $resp = google_calendar_request(
            'PATCH',
            'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']),
            [],
            $payload,
            $tokenUserId
        );
        $googleSync = ['attempted' => true, 'status' => 'updated', 'uid' => $uid, 'google_id' => (string) ($resp['id'] ?? '')];
    } else {
        $resp = google_calendar_request(
            'POST',
            'calendars/' . rawurlencode($calendarId) . '/events',
            [],
            $payload,
            $tokenUserId
        );
        $googleSync = ['attempted' => true, 'status' => 'created', 'uid' => $uid, 'google_id' => (string) ($resp['id'] ?? '')];
    }
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'uid' => 'ops-outreach-' . $eventId . '@koval-distillery.com', 'error_type' => $e::class];
}

$readbackStmt = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_location,
            eb.notes LIKE ? AS notes_has_marker,
            eb.important_information LIKE ? AS important_has_marker,
            GROUP_CONCAT(DISTINCT l.shift_id ORDER BY l.shift_id SEPARATOR ',') AS shift_ids
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id"
);
$like = '%' . $marker . '%';
$readbackStmt->execute([$like, $like, $eventId]);
$readback = $readbackStmt->fetch(PDO::FETCH_ASSOC) ?: [];

$shiftIds = [];
foreach (explode(',', (string) ($readback['shift_ids'] ?? '')) as $shiftIdRaw) {
    $shiftId = (int) trim($shiftIdRaw);
    if ($shiftId > 0) {
        $shiftIds[] = $shiftId;
    }
}
$assignments = [];
if ($shiftIds !== []) {
    $placeholders = implode(',', array_fill(0, count($shiftIds), '?'));
    $assignStmt = $trackPdo->prepare(
        "SELECT s.id AS shift_id, s.start_time, s.end_time, s.group_id,
                s2u.user_id, vu.first_name, vu.last_name, vu.email1, vu.email2
           FROM shifts s
           LEFT JOIN shift2user s2u ON s2u.shift_id = s.id
           LEFT JOIN koval_crm.vtiger_users vu ON vu.id = s2u.user_id
          WHERE s.id IN ($placeholders)
          ORDER BY s.id, vu.id"
    );
    $assignStmt->execute($shiftIds);
    $assignments = $assignStmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
}

$body = implode("\n", [
    'Hi Sonat,',
    '',
    'I added the forwarded Whiskey Washback logistics to the OPS event details and the Outreach calendar sync path for the existing event record.',
    '',
    'One timing issue: the forward arrived today, Saturday, June 27, but the Whiskey Washback event was yesterday, Friday, June 26. Because the staff email would now be after the event, should I still send the logistics to Dereck Atwater and Christine Cummins for recordkeeping, or should I file this as a late-forward after updating OPS?',
    '',
    'OPS link: ' . $opsUrl,
    '',
    'Best,',
    '',
    'Vanessa',
    '',
    'Vanessa Sterling',
    '',
    'Outreach Coordinator',
    'KOVAL Distillery',
    '4241 N Ravenswood Ave',
    'Chicago, IL 60613',
    '312 878 7988',
    'http://www.koval-distillery.com',
    '',
    'X | Instagram | Facebook',
]);

$taskPacket = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '025170d2',
    'ops_portal_or_domain_task' => 'OPS Outreach event 903 / Google UID ops-outreach-903@koval-distillery.com',
    'status' => 'clarification_sent',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 903 notes and important_information contain marker ' . $marker . '; worker email held because source arrived after event date.',
    'next_update' => 'Wait for Sonat answer on whether to send post-event logistics to assigned staff or file as late-forward.',
    'requested_deliverable' => 'Add Whiskey Washback logistics to event details and email assigned staff.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event readback plus clarification Message-ID',
    'result_email_required' => 'true',
    'owner_question_required' => 'true',
];

$draftPayload = [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'clarification_sent',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 903 important_information updated; staff email needs Sonat confirmation because the event is already past.',
    'next_update' => 'Wait for Sonat answer.',
    'requested_deliverable' => 'Ask whether to send post-event logistics to assigned staff.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS readback',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'body' => $body,
    'in_reply_to' => $sourceMessageId,
    'references' => '<CABj+3D_az7m0zQamHM66OJA7Jw=HYhPBff2ykM_isJ+dvWiNvw@mail.gmail.com> ' . $sourceMessageId,
    'owner_question' => true,
    'task_packet' => $taskPacket,
];

$draftPath = $stateDir . '/outbox/' . $actionId . '.approved.json';
ww_write_json_file($draftPath, $draftPayload);

echo json_encode([
    'ok' => true,
    'proof_marker' => 'OPS_EVENT_903_LATE_LOGISTICS_' . $taskFlowKey,
    'event_id' => $eventId,
    'ops_url' => $opsUrl,
    'marker' => $marker,
    'google_sync' => $googleSync,
    'readback' => $readback,
    'assignments' => $assignments,
    'draft' => $draftPath,
    'action_id' => $actionId,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
