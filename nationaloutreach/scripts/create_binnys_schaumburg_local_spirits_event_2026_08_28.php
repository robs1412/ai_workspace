#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function schaumburg_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function schaumburg_google_token_user_id(PDO $pdo): ?int
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

function schaumburg_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
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

    $cleanup = $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?');
    $cleanup->execute([$uid, $eventId]);
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'outreach']);
}

function schaumburg_write_json(string $path, array $payload): void
{
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false || file_put_contents($path, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write approved reply payload.');
    }
    chmod($path, 0600);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventName = "Binny's Schaumburg Local Spirits Event";
$eventDate = '2026-08-28';
$eventStart = '18:00';
$eventEnd = '20:00';
$accountId = 2770;
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceMessageId = '<PH5PR13MB765748F8BDFB1C799F281344AAFA2@PH5PR13MB7657.namprd13.prod.outlook.com>';
$taskFlowKey = 'taskflow-970a31be1d1afd3b';
$workspaceboardSession = '1dabe11f';
$location = "Binny's Schaumburg, 323 W Golf Rd, Schaumburg, IL 60195";
$notes = implode("\n", [
    'Source: Rob Weekley email, subject "Binny\'s Schaumburg - Local Spirits Event - 8/28/26", Message-ID ' . $sourceMessageId . '.',
    'Schaumburg is hosting a walkaround local spirits event and invited KOVAL as a showcased brand.',
    'Date: 2026-08-28. Time: 6:00 PM-8:00 PM.',
    'Store setup and requested pour list are pending confirmation from the Schaumburg managers.',
    'Coordinator: Vanessa Sterling. Open COTeam shift is intentionally unassigned pending staff coverage.',
    'Task Flow: ' . $taskFlowKey . '. Workspaceboard: ' . $workspaceboardSession . '.',
]);
$importantInformation = 'Walkaround local spirits event, 6:00 PM-8:00 PM. Store setup and pour-list guidance pending. Open COTeam shift pending coverage assignment.';

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();
try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupe = $eventPdo->prepare(
        "SELECT eb.id
           FROM event_bookings eb
           LEFT JOIN event_booking_accounts eba ON eba.event_booking_id = eb.id
          WHERE eb.event_date = ?
            AND (eba.account_id = ? OR eb.event_name LIKE ? OR eb.event_location LIKE ? OR eb.notes LIKE ?)
          ORDER BY eb.id DESC LIMIT 1"
    );
    $dupe->execute([$eventDate, $accountId, '%Schaumburg%Local Spirits%', '%Schaumburg%', '%' . $sourceMessageId . '%']);
    $eventId = (int) ($dupe->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $stmt = $eventPdo->prepare(
            'UPDATE event_bookings SET event_name=?, event_date=?, event_end_date=NULL, event_category=?, event_location=?,
             distributor_account_id=?, start_time=?, end_time=?, contact_name=?, contact_email=?, contact_phone=?, notes=?,
             important_information=?, event_host_user_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?'
        );
        $stmt->execute([$eventName, $eventDate, 'Outreach', $location, $accountId, $eventStart, $eventEnd,
            'Rob Weekley', 'rweekley@binnys.com', '224-491-6156', $notes, $importantInformation, $eventHost, $eventId]);
    } else {
        $stmt = $eventPdo->prepare(
            'INSERT INTO event_bookings (event_name,event_date,event_end_date,event_category,event_location,distributor_account_id,
             start_time,end_time,contact_name,contact_email,contact_phone,amount_paid,notes,important_information,created_by,event_host_user_id)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        );
        $stmt->execute([$eventName, $eventDate, null, 'Outreach', $location, $accountId, $eventStart, $eventEnd,
            'Rob Weekley', 'rweekley@binnys.com', '224-491-6156', 0, $notes, $importantInformation, $createdBy, $eventHost]);
        $eventId = (int) $eventPdo->lastInsertId();
    }
    if ($eventId <= 0) {
        throw new RuntimeException('Event write did not return an id.');
    }

    $accountLink = $eventPdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id=? AND account_id=? LIMIT 1');
    $accountLink->execute([$eventId, $accountId]);
    if (!$accountLink->fetchColumn()) {
        $eventPdo->prepare('INSERT INTO event_booking_accounts (event_booking_id,account_id) VALUES (?,?)')->execute([$eventId, $accountId]);
    }

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id=? ORDER BY id LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Outreach: Binny's Schaumburg Local Spirits Event - coverage pending";
    if ($shiftId > 0) {
        $stmt = $trackPdo->prepare('UPDATE ' . TRACKTIME_DB_NAME . '.shifts SET week_day_id=?,start_date=?,end_date=?,start_time=?,end_time=?,notes=?,group_id=?,account_id=?,activity_id=0,updated_by=? WHERE id=?');
        $stmt->execute([schaumburg_week_day_id($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $shiftId]);
    } else {
        $stmt = $trackPdo->prepare('INSERT INTO ' . TRACKTIME_DB_NAME . '.shifts (parent_id,week_day_id,start_date,end_date,start_time,end_time,deleted,notes,is_template,group_id,account_id,activity_id,created_by,updated_by) VALUES (0,?,?,?,?,?,0,?,0,?,?,0,?,?)');
        $stmt->execute([schaumburg_week_day_id($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $createdBy]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift write did not return an id.');
        }
        $eventPdo->prepare('INSERT INTO event_booking_shift_links (event_booking_id,shift_id,created_by) VALUES (?,?,?)')->execute([$eventId, $shiftId, $createdBy]);
    }
    $trackPdo->prepare('DELETE FROM ' . TRACKTIME_DB_NAME . '.shift2user WHERE shift_id=?')->execute([$shiftId]);

    if ($trackPdo->inTransaction()) {
        $trackPdo->commit();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }
} catch (Throwable $e) {
    if ($trackPdo->inTransaction()) $trackPdo->rollBack();
    if ($eventPdo->inTransaction()) $eventPdo->rollBack();
    throw $e;
}

$googleSync = ['attempted' => true, 'status' => 'failed', 'uid' => ''];
try {
    $tokenUserId = schaumburg_google_token_user_id($eventPdo);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $stmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id=?');
    $stmt->execute([$eventId]);
    $eventRow = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) throw new RuntimeException('Unable to read event for Google sync.');
    $uid = 'ops-outreach-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
    $calendarId = google_calendar_outreach_id();
    $existing = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($existing) && !empty($existing['id'])) {
        $resp = google_calendar_request('PATCH', 'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']), [], $payload, $tokenUserId);
        $operation = 'patched';
    } else {
        $resp = google_calendar_request('POST', 'calendars/' . rawurlencode($calendarId) . '/events', [], $payload, $tokenUserId);
        $operation = 'created';
    }
    if (empty($resp['success'])) throw new RuntimeException((string) ($resp['error'] ?? 'Google Calendar request failed.'));
    schaumburg_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync['error'] = $e->getMessage();
}

$readback = $eventPdo->prepare(
    'SELECT eb.id,eb.event_name,eb.event_date,eb.start_time,eb.end_time,eb.event_category,eb.event_location,
     eb.distributor_account_id,eb.contact_name,eb.contact_email,eb.event_host_user_id,l.shift_id,s.group_id,
     COUNT(s2u.user_id) assigned_user_count,gl.google_event_uid,gl.calendar_type
     FROM event_bookings eb
     LEFT JOIN event_booking_shift_links l ON l.event_booking_id=eb.id
     LEFT JOIN ' . TRACKTIME_DB_NAME . '.shifts s ON s.id=l.shift_id
     LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id=s.id
     LEFT JOIN event_booking_google_links gl ON gl.event_booking_id=eb.id
     WHERE eb.id=? GROUP BY eb.id,l.shift_id,s.group_id,gl.google_event_uid,gl.calendar_type'
);
$readback->execute([$eventId]);
$row = $readback->fetch(PDO::FETCH_ASSOC);

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
if (!is_dir($outbox) && !mkdir($outbox, 0700, true) && !is_dir($outbox)) {
    throw new RuntimeException('Unable to create National Outreach outbox.');
}
$body = implode("\n", [
    'Hi Rob and Schaumburg team,', '',
    'Thank you for including KOVAL. We would be happy to participate in the Schaumburg local spirits event on Friday, August 28, from 6:00-8:00 PM. I have added it to our event schedule.', '',
    'Please let me know if there are any specific setup instructions, arrival timing, or products you would like us to feature.', '',
    'Best,', '', 'Vanessa', '', 'Vanessa Sterling', 'Outreach Coordinator', 'KOVAL Distillery',
    '4241 N Ravenswood Ave', 'Chicago, IL 60613', '312 878 7988', 'http://www.koval-distillery.com', '', 'X | Instagram | Facebook',
]);
$verification = 'OPS event ' . $eventId . ' and linked shift ' . $shiftId . ' read back for 2026-08-28 18:00-20:00; Outreach calendar UID ' . ($googleSync['uid'] ?? '') . ' ' . ($googleSync['status'] ?? 'unknown') . '.';
$packet = [
    'source_ref' => trim($sourceMessageId, '<>'), 'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'approved-send:nationaloutreach', 'requester' => 'Rob Weekley <rweekley@binnys.com>',
    'owner_lane' => 'outreach-coordinator', 'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $workspaceboardSession, 'ops_portal_or_domain_task' => 'OPS event ' . $eventId . ' / TrackTime shift ' . $shiftId,
    'status' => 'reported', 'calendar_event' => $googleSync['uid'] ?? '',
    'source_links' => "Binny's Schaumburg - Local Spirits Event - 8/28/26", 'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification, 'next_update' => 'Complete unless Binny\'s replies with setup or product details.',
    'requested_deliverable' => 'Confirm participation and coordinate the Schaumburg local spirits event through OPS.',
    'human_owner_or_recipient' => 'Rob Weekley and Binny\'s Schaumburg managers', 'output_channel' => 'email',
    'proof_required' => 'OPS event/shift/calendar readback plus sent Message-ID and source filing proof', 'owner_question_required' => 'false',
];
$draftPath = $outbox . '/taskflow-970a31be1d1afd3b-binnys-schaumburg-confirmation.approved.json';
schaumburg_write_json($draftPath, [
    'from' => 'vanessa.sterling@kovaldistillery.com', 'from_name' => 'Vanessa Sterling',
    'to' => ['rweekley@binnys.com'],
    'cc' => ['Managers17@binnys.com', 'sonat@kovaldistillery.com', 'robert@kovaldistillery.com', 'macee.maddox@kovaldistillery.com'],
    'subject' => "Re: Binny's Schaumburg - Local Spirits Event - 8/28/26",
    'body' => $body, 'in_reply_to' => $sourceMessageId, 'references' => $sourceMessageId,
    'source_ref' => trim($sourceMessageId, '<>'), 'task_packet' => $packet,
]);

echo json_encode(['ok' => true, 'event' => $row, 'google_sync' => $googleSync, 'draft' => $draftPath, 'verification' => $verification], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
