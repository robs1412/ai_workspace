#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create output directory.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode JSON payload.');
    }
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write draft payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to move draft payload into place.');
    }
}

function append_section_once(string $existing, string $marker, string $section): string
{
    $existing = trim($existing);
    if ($existing !== '' && strpos($existing, $marker) !== false) {
        return $existing;
    }
    return trim($existing . ($existing !== '' ? "\n\n" : '') . trim($section));
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
for ($i = 1; $i < count($argv); $i++) {
    if ($argv[$i] === '--state-dir' && isset($argv[$i + 1])) {
        $stateDir = rtrim((string) $argv[++$i], '/');
    }
}

$eventId = 903;
$sourceRef = 'calbltzyi9pfmqz5eda7pvwzxwnqcqgdukcgtfk96tuoevbf9zq@mail.gmail.com';
$taskFlowKey = 'taskflow-2c390a4c3d8e5100';
$actionId = $taskFlowKey . '-whiskey-washback-stale-forward';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;
$marker = 'whiskey-washback-dayof-logistics-2026-06-27';

$dayOfDetails = implode("\n", [
    'Whiskey Washback day-of logistics from the 2026-06-27 Sonat forward (' . $marker . '):',
    '- Vendor setup window was 1:30pm-5:15pm for the Friday, June 26 event.',
    '- Event time was 6:00pm-9:30pm at Artifact Events, 4325 N Ravenswood Ave.',
    '- KOVAL was directed to the South Building, 1st Floor; load-in through the South Building entrance or back alley for larger items.',
    '- Vehicles should move after unloading; free street parking was available on Ravenswood Ave.',
    '- Team should be fully set by doors at 6:00pm, with clean setup photos ready by 5:30pm if desired.',
    '- Bring a long extension cord if power is needed.',
    '- Event provides 2oz tasting cups, 7oz cocktail cups if needed, ice, bucket, scoop, and table linen.',
    '- Leftover product must be picked up the event night; venue will not store items.',
    '- Product reminder from Sonat: bring Thresh and Winnow Millet for the VIP hour.',
]);

$eventPdo = get_event_pdo();
ensure_event_bookings_important_information_column($eventPdo);

$eventPdo->beginTransaction();
try {
    $stmt = $eventPdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $stmt->execute([$eventId]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        throw new RuntimeException('OPS event 903 was not found.');
    }

    $notes = append_section_once((string) ($event['notes'] ?? ''), $marker, $dayOfDetails);
    $important = append_section_once((string) ($event['important_information'] ?? ''), $marker, $dayOfDetails);

    $update = $eventPdo->prepare(
        'UPDATE event_bookings
            SET notes = ?,
                important_information = ?,
                updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    );
    $update->execute([$notes, $important, $eventId]);
    $eventPdo->commit();
} catch (Throwable $e) {
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => ''];
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
            eb.important_information,
            GROUP_CONCAT(DISTINCT CONCAT(vu.first_name, ' ', vu.last_name) ORDER BY vu.id SEPARATOR ', ') AS assigned_names
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN koval_crm.vtiger_users vu ON vu.id = s2u.user_id
      WHERE eb.id = ?
      GROUP BY eb.id"
);
$readbackStmt->execute([$eventId]);
$readback = $readbackStmt->fetch(PDO::FETCH_ASSOC) ?: [];

$body = implode("\n", [
    'Hi Sonat,',
    '',
    'I added the forwarded Whiskey Washback logistics to the OPS event notes so the record now has the load-in, setup, supplies, load-out, and Thresh and Winnow Millet VIP-hour reminder.',
    '',
    'Because the forward arrived after the June 26 event had already ended, I did not send the day-of logistics to the staff after the fact.',
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
]);

$taskPacket = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '6ff9ed4d',
    'ops_portal_or_domain_task' => 'OPS Outreach event 903',
    'status' => 'reported',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'completion_or_blocker_email' => '',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 903 updated with marker ' . $marker . '; no worker post-event logistics email sent because source arrived after the event ended.',
    'next_update' => 'Send proof should land in sent-log, then source can be filed.',
    'requested_deliverable' => 'Add Whiskey Washback logistics to event details and notify signed-up workers if still timely.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event readback plus sent-log Message-ID',
    'due_or_next_update' => 'first check within 2 minutes; result email, owner question, or exact blocker within 5 minutes',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$draftPayload = [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 903 updated with marker ' . $marker . '.',
    'next_update' => 'Completion email queued for approved send cycle.',
    'requested_deliverable' => 'Add Whiskey Washback logistics to event details.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS event readback',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'body' => $body,
    'in_reply_to' => '<CALbLtzyi9pFMqz5eDa7pVWzxwnQCqgdukCgtFk96TuOevBF9zQ@mail.gmail.com>',
    'references' => '<CALbLtzyi9pFMqz5eDa7pVWzxwnQCqgdukCgtFk96TuOevBF9zQ@mail.gmail.com>',
    'task_packet' => $taskPacket,
];

$draftPath = $stateDir . '/outbox/' . $actionId . '.approved.json';
write_json_file($draftPath, $draftPayload);

echo json_encode([
    'ok' => true,
    'event_id' => $eventId,
    'ops_url' => $opsUrl,
    'draft' => $draftPath,
    'action_id' => $actionId,
    'marker' => $marker,
    'google_sync' => $googleSync,
    'readback_marker_present' => strpos((string) ($readback['important_information'] ?? ''), $marker) !== false,
    'assigned_names' => $readback['assigned_names'] ?? '',
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
