#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function append_line_once(string $existing, string $line): string
{
    $existing = trim($existing);
    if ($existing !== '' && strpos($existing, $line) !== false) {
        return $existing;
    }
    return trim($existing . ($existing !== '' ? "\n" : '') . $line);
}

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

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
for ($i = 1; $i < count($argv); $i++) {
    if ($argv[$i] === '--state-dir' && isset($argv[$i + 1])) {
        $stateDir = rtrim((string) $argv[++$i], '/');
    }
}

$eventId = 865;
$sourceRef = 'calbltzyitkjrk2bhcttr2q+tdurxwvakac2zxfz_35gni7xsyw@mail.gmail.com';
$taskFlowKey = 'taskflow-b03f625df46ae709';
$actionId = $taskFlowKey . '-malt-row-instructions-complete';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;

$importantInformation = implode("\n", [
    'Malt Row on Damen team notes:',
    '- KOVAL is popping up at Bon Femmes.',
    '- Bon Femmes has tables available for KOVAL setup, so no separate table is needed unless plans change.',
    '- Event is planned for 225 attendees; 115 tickets had sold as of 2026-06-21 and organizer expects sellout.',
    '- Attendees receive one sample of one spirit from KOVAL; punch cards will be used to track samples.',
    '- KOVAL team will bring samples for tasting product.',
    '- Ice will be provided at Bon Femmes.',
    '- WGN highlighted KOVAL ahead of the event.',
]);

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
ensure_event_bookings_important_information_column($eventPdo);
ensure_event_bookings_max_capacity_column($eventPdo);

$eventPdo->beginTransaction();
try {
    $stmt = $eventPdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $stmt->execute([$eventId]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        throw new RuntimeException('OPS event 865 was not found.');
    }

    $notes = 'KOVAL is popping up at Bon Femmes for Malt Row on Damen. Expect about 225 attendees, with punch cards limiting guests to one KOVAL spirit sample. The team should bring tasting samples. Ice will be provided, and Bon Femmes has tables available for KOVAL setup. WGN highlighted KOVAL ahead of the event.';
    $eventLocation = trim((string) ($event['event_location'] ?? ''));
    if ($eventLocation === '' || stripos($eventLocation, 'Bon Femmes') === false) {
        $eventLocation = 'Bon Femmes, Damen Avenue, Ravenswood, Chicago';
    }

    $update = $eventPdo->prepare(
        'UPDATE event_bookings
            SET event_location = ?,
                estimated_guest_count = ?,
                max_capacity = ?,
                notes = ?,
                important_information = ?,
                updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    );
    $update->execute([
        $eventLocation,
        225,
        225,
        $notes,
        $importantInformation,
        $eventId,
    ]);

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
            eb.estimated_guest_count, eb.max_capacity, eb.important_information,
            GROUP_CONCAT(DISTINCT l.shift_id ORDER BY l.shift_id SEPARATOR ',') AS shift_ids,
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
    'I updated the OPS instructions for Malt Row on Damen with the new Bon Femmes placement and day-of details.',
    '',
    'The team-facing notes now include:',
    '- Bon Femmes as the pop-up location.',
    '- Bon Femmes has tables available for KOVAL setup.',
    '- Planned 225 attendees / 115 tickets sold as of today, with sellout expected.',
    '- One sample of one spirit per attendee, tracked by punch cards.',
    '- KOVAL team will bring tasting samples.',
    '- Ice will be provided at Bon Femmes.',
    '',
    'OPS link: ' . $opsUrl,
    '',
    'Best,',
    'Vanessa',
]);

$taskPacket = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '5200de44',
    'ops_portal_or_domain_task' => 'OPS Outreach event 865',
    'status' => 'reported',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'completion_or_blocker_email' => '',
    'source_links' => 'Malt Row on Damen',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 865 important_information updated and completion email queued.',
    'next_update' => 'Send cycle should report Message-ID, then source can be filed.',
    'requested_deliverable' => 'Update team instructions for Malt Row on Damen.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event readback plus sent-log Message-ID',
];

$draftPayload = [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'source_links' => 'Malt Row on Damen',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 865 important_information updated.',
    'next_update' => 'Completion email queued for approved send cycle.',
    'requested_deliverable' => 'Update team instructions for Malt Row on Damen.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS event readback',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: Malt Row on Damen',
    'body' => $body,
    'in_reply_to' => '<CALbLtzyiTKJrk2bHcttr2Q+tDURXWvakac2ZXfz_35gNi7xsYw@mail.gmail.com>',
    'references' => '<CALbLtzyiTKJrk2bHcttr2Q+tDURXWvakac2ZXfz_35gNi7xsYw@mail.gmail.com>',
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
    'google_sync' => $googleSync,
    'readback' => $readback,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
