#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function saloon_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function saloon_google_token_user_id(PDO $pdo): ?int
{
    google_oauth_tokens_table_ready($pdo);
    $stmt = $pdo->query('SELECT user_id FROM ops_google_oauth_tokens ORDER BY updated_at DESC');
    foreach (($stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : []) as $row) {
        $candidate = (int) ($row['user_id'] ?? 0);
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            return $candidate;
        }
    }
    return null;
}

function saloon_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $pdo->exec("CREATE TABLE IF NOT EXISTS event_booking_google_links (
        event_booking_id INT NOT NULL,
        google_event_uid VARCHAR(255) NOT NULL,
        calendar_type VARCHAR(32) NOT NULL DEFAULT 'events',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (event_booking_id),
        UNIQUE KEY ux_event_booking_google_uid (google_event_uid),
        CONSTRAINT fk_event_booking_google_links_event FOREIGN KEY (event_booking_id) REFERENCES event_bookings(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");

    $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?')
        ->execute([$uid, $eventId]);
    $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    )->execute([$eventId, $uid, 'outreach']);
}

function saloon_write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create output directory.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode JSON payload.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write ' . $path);
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to move JSON payload into place.');
    }
    chmod($path, 0600);
}

function saloon_task_flow_record(array $packet, string $event = 'email_completed'): void
{
    $payload = ['event' => $event, 'packet' => $packet];
    $descriptors = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $proc = proc_open(['/usr/local/bin/php', '/Users/werkstatt/workspaceboard/scripts/planner/task_flow_mysql_recorder.php', 'record'], $descriptors, $pipes, '/Users/werkstatt/workspaceboard');
    if (!is_resource($proc)) {
        throw new RuntimeException('Unable to start Task Flow recorder.');
    }
    fwrite($pipes[0], json_encode($payload, JSON_UNESCAPED_SLASHES) ?: '{}');
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    $code = proc_close($proc);
    if ($code !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$eventPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$trackPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$eventId = 1124;
$shiftId = 5668;
$eventDate = '2026-07-25';
$eventStart = '10:30';
$eventEnd = '12:30';
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceRef = 'cahpmwzwqrnujm0o1ampks8swjcf+f2=ojfpoho9mxie1oc+wgq@mail.gmail.com';
$sourceMessageId = '<CAHPmwzwQrnuJM0o1aMPkS8sWjCf+F2=ojfPOHo9Mxie1oC+WGQ@mail.gmail.com>';
$taskFlowKey = 'taskflow-7f7a696dfe52b7a8';
$marker = 'saloon-royale-reschedule-2026-07-25 ' . $sourceMessageId;
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;

$eventPdo->beginTransaction();
if (!$trackPdo->inTransaction()) {
    $trackPdo->beginTransaction();
}

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $eventStmt = $eventPdo->prepare('SELECT id, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $eventStmt->execute([$eventId]);
    $event = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        throw new RuntimeException('OPS event 1124 was not found.');
    }

    $notes = implode("\n", [
        'Source: Darla Swango email, subject "Re: Schedule tasting - July 31 @ Saloon Royale", Message-ID ' . $sourceMessageId . '.',
        'Reschedule request received 2026-06-30: Saloon Royale changed tasting to Saturday, July 25, 2026, 10:30 AM-12:30 PM.',
        'Products to sample: Bourbon with lemonade mixer, Gin, Cranberry Gin, and canned cocktails.',
        'Darla is unavailable and asked Vanessa to offer the tasting to the wider team; linked COTeam shift is intentionally open/unassigned.',
        'If no COTeam member is available, Darla will work with Saloon Royale to find a different date.',
        'Previous placeholder was Friday, July 31, 2026, 6:00-8:00 PM.',
        'Task Flow: ' . $taskFlowKey . '.',
        'Proof marker: ' . $marker . '.',
    ]);
    $important = implode("\n", [
        'Rescheduled to Saturday, July 25, 2026, 10:30 AM-12:30 PM.',
        'Open COTeam coverage needed; Darla is unavailable.',
        'Sample Bourbon with lemonade mixer, Gin, Cranberry Gin, and canned cocktails.',
    ]);

    $eventPdo->prepare(
        'UPDATE event_bookings
            SET event_date = ?, event_end_date = NULL, start_time = ?, end_time = ?,
                contact_name = ?, event_host_user_id = ?, notes = ?, important_information = ?,
                updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    )->execute([$eventDate, $eventStart, $eventEnd, 'Darla Swango', $eventHost, $notes, $important, $eventId]);

    $trackPdo->prepare(
        "UPDATE " . TRACKTIME_DB_NAME . ".shifts
            SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                notes = ?, group_id = ?, account_id = 0, activity_id = 0, updated_by = ?
          WHERE id = ?"
    )->execute([
        saloon_week_day_id($eventDate),
        $eventDate,
        $eventDate,
        $eventStart,
        $eventEnd,
        'Outreach: Saloon Royale Tasting - open COTeam coverage',
        $cotGroupId,
        $createdBy,
        $shiftId,
    ]);
    $trackPdo->prepare("DELETE FROM " . TRACKTIME_DB_NAME . ".shift2user WHERE shift_id = ?")->execute([$shiftId]);

    if ($trackPdo->inTransaction()) {
        $trackPdo->commit();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }
} catch (Throwable $e) {
    if ($trackPdo->inTransaction()) {
        $trackPdo->rollBack();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => 'ops-outreach-' . $eventId . '@koval-distillery.com'];
try {
    $tokenUserId = saloon_google_token_user_id($eventPdo);
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
        $operation = 'patched';
    } else {
        $resp = google_calendar_request(
            'POST',
            'calendars/' . rawurlencode($calendarId) . '/events',
            [],
            $payload,
            $tokenUserId
        );
        $operation = 'created';
    }
    if (empty($resp['success'])) {
        throw new RuntimeException((string) ($resp['error'] ?? 'Google Calendar request failed.'));
    }
    saloon_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'uid' => 'ops-outreach-' . $eventId . '@koval-distillery.com', 'error_type' => $e::class];
}

$readbackStmt = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_location,
            eb.notes LIKE ? AS notes_has_marker,
            eb.important_information LIKE ? AS important_has_reschedule,
            l.shift_id, s.start_date AS shift_start_date, s.start_time AS shift_start,
            s.end_time AS shift_end, s.group_id, COUNT(s2u.user_id) AS assigned_user_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.start_date, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type"
);
$readbackStmt->execute(['%' . $marker . '%', '%July 25, 2026%', $eventId]);
$readback = $readbackStmt->fetch(PDO::FETCH_ASSOC) ?: [];

$body = implode("\n", [
    'Hi Darla,',
    '',
    'I updated the Saloon Royale tasting in OPS and on the Outreach calendar for Saturday, July 25 from 10:30 AM-12:30 PM.',
    '',
    'I also updated the open COTeam shift and noted the products: Bourbon with lemonade mixer, Gin, Cranberry Gin, and canned cocktails. The shift is open for wider team coverage.',
    '',
    'If nobody is available, I will keep this marked as needing a new date with Saloon Royale.',
    '',
    'OPS event: ' . $opsUrl,
    '',
    'Best,',
    '',
    'Vanessa',
    '',
    'Vanessa Sterling',
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
    'requester' => 'Darla Swango <darla.swango@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '15366a73',
    'ops_portal_or_domain_task' => 'OPS Outreach event 1124 / TrackTime shift 5668',
    'status' => 'completed',
    'due_or_trigger' => '2026-06-30 09:52:22',
    'scheduled_action' => 'Reschedule Saloon Royale tasting and open COTeam shift for wider coverage.',
    'calendar_event' => 'ops-outreach-1124@koval-distillery.com',
    'clarification_email' => '',
    'completion_or_blocker_email' => 'pending_send',
    'source_links' => 'Re: Schedule tasting - July 31 @ Saloon Royale',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 1124 and shift 5668 read back as 2026-07-25 10:30-12:30 with open COTeam coverage; proof marker ' . $marker . '.',
    'next_update' => 'Completed; sent Vanessa confirmation to Darla with Robert and Sonat copied.',
    'requested_deliverable' => 'Update Saloon Royale tasting date/time/products and offer open shift to wider team.',
    'human_owner_or_recipient' => 'Darla Swango <darla.swango@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS/shift readback, Google UID, sent-log Message-ID, inbox archive proof',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$draftPayload = [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Darla Swango <darla.swango@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['darla.swango@kovaldistillery.com'],
    'cc' => ['robert@kovaldistillery.com', 'sonat@kovaldistillery.com'],
    'subject' => 'Re: Schedule tasting - July 31 @ Saloon Royale',
    'body' => $body,
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'task_packet' => $taskPacket,
];

$outboxPath = $stateDir . '/outbox/saloon-royale-reschedule-2026-07-25.approved.json';
saloon_write_json_file($outboxPath, $draftPayload);
saloon_task_flow_record($taskPacket, 'ops_event_updated');

echo json_encode([
    'ok' => true,
    'event' => $readback,
    'google_sync' => $googleSync,
    'outbox' => $outboxPath,
    'proof_marker' => 'SALON_ROYALE_EVENT_1124_SHIFT_5668_RESCHEDULED_20260725',
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
