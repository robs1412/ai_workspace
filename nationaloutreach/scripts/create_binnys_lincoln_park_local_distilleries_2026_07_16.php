#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function blp_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function blp_google_token_user_id(PDO $pdo): ?int
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

function blp_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
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

function blp_write_json_file(string $path, array $payload): void
{
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode JSON payload.');
    }
    if (file_put_contents($path, $json . "\n") === false) {
        throw new RuntimeException('Unable to write ' . $path);
    }
    chmod($path, 0600);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventName = "Binny's Lincoln Park Local Distilleries Event";
$eventDate = '2026-07-16';
$eventStart = '18:00';
$eventEnd = '20:00';
$accountId = 240363;
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceMessageId = '<ds5pr13mb765321f1cae2c26ada008f56aaed2@ds5pr13mb7653.namprd13.prod.outlook.com>';
$taskFlowKey = 'taskflow-d648c4645e10e892';
$location = "Binny's Lincoln Park, 1720 N Marcey St, Chicago, IL 60614";
$notes = implode("\n", [
    'Source: Rob Weekley email, subject "Binny\'s Lincoln Park - Local Distilleries Event - 7/16/26", Message-ID ' . $sourceMessageId . '.',
    'Binny\'s asked KOVAL to attend its Local Distilleries event and complete the attached pour list form.',
    'Event details from source: Binny\'s Lincoln Park, Thursday, July 16, 2026, 6:00 PM-8:00 PM.',
    'The National Outreach runtime did not expose a saved pour-list attachment for this source message, so Vanessa asked Rob to resend it.',
    'Coordinator: Vanessa Sterling. Open COTeam shift is intentionally unassigned pending staff coverage.',
    'Task Flow: ' . $taskFlowKey . '.',
]);
$importantInformation = 'Local Distilleries event. Vanessa Sterling confirmed KOVAL attendance and asked Rob Weekley to resend the pour-list form because no attachment was available in the National Outreach runtime.';

$eventPdo->beginTransaction();
if (!$trackPdo->inTransaction()) {
    $trackPdo->beginTransaction();
}

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupeStmt = $eventPdo->prepare(
        "SELECT eb.id
           FROM event_bookings eb
           LEFT JOIN event_booking_accounts eba ON eba.event_booking_id = eb.id
          WHERE eb.event_date = ?
            AND (eba.account_id = ? OR eb.event_name LIKE ? OR eb.event_location LIKE ? OR eb.notes LIKE ?)
          ORDER BY eb.id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$eventDate, $accountId, '%Local Distilleries%', '%Lincoln Park%', '%' . trim($sourceMessageId, '<>') . '%']);
    $eventId = (int) ($dupeStmt->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $updateEvent = $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = ?, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                    contact_name = ?, contact_email = ?, contact_phone = ?, estimated_guest_count = ?,
                    notes = ?, important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $updateEvent->execute([
            $eventName, $eventDate, null, 'Outreach', $location, $accountId, $eventStart, $eventEnd,
            'Rob Weekley', 'rweekley@binnys.com', '224-491-6156', null, $notes, $importantInformation,
            $eventHost, $eventId,
        ]);
    } else {
        $insertEvent = $eventPdo->prepare(
            'INSERT INTO event_bookings (
                event_name, event_date, event_end_date, event_category, event_location, distributor_account_id,
                start_time, end_time, contact_name, contact_email, contact_phone, amount_paid,
                estimated_guest_count, actual_guest_count, max_capacity, notes, important_information,
                is_pioneer_tasting, rooms, google_drive_link, created_by, event_host_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        );
        $insertEvent->execute([
            $eventName, $eventDate, null, 'Outreach', $location, $accountId, $eventStart, $eventEnd,
            'Rob Weekley', 'rweekley@binnys.com', '224-491-6156', 0, null, null, null, $notes,
            $importantInformation, 0, null, null, $createdBy, $eventHost,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    $accountExists = $eventPdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id = ? AND account_id = ? LIMIT 1');
    $accountExists->execute([$eventId, $accountId]);
    if (!$accountExists->fetchColumn()) {
        $eventPdo->prepare('INSERT INTO event_booking_accounts (event_booking_id, account_id) VALUES (?, ?)')->execute([$eventId, $accountId]);
    }

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Outreach: Binny's Lincoln Park Local Distilleries Event - coverage pending";
    if ($shiftId > 0) {
        $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = ?, activity_id = 0, updated_by = ?
              WHERE id = ?"
        )->execute([$eventDate ? blp_week_day_id($eventDate) : 0, $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $shiftId]);
    } else {
        $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, 0, ?, ?)"
        )->execute([blp_week_day_id($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $createdBy]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $eventPdo->prepare('INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by) VALUES (?, ?, ?)')->execute([$eventId, $shiftId, $createdBy]);
    }

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

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => ''];
try {
    $tokenUserId = blp_google_token_user_id($eventPdo);
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
        $resp = google_calendar_request('PATCH', 'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']), [], $payload, $tokenUserId);
        $operation = 'patched';
    } else {
        $resp = google_calendar_request('POST', 'calendars/' . rawurlencode($calendarId) . '/events', [], $payload, $tokenUserId);
        $operation = 'created';
    }
    if (empty($resp['success'])) {
        throw new RuntimeException((string) ($resp['error'] ?? 'Google Calendar request failed.'));
    }
    blp_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => ''];
}

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
            eb.event_location, eb.distributor_account_id, eb.contact_name, eb.contact_email,
            eb.event_host_user_id, l.shift_id, s.start_time AS shift_start, s.end_time AS shift_end,
            s.group_id, COUNT(s2u.user_id) AS assigned_user_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);
$row = $readback->fetch(PDO::FETCH_ASSOC);

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
if (!is_dir($outbox)) {
    mkdir($outbox, 0700, true);
}
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;
$body = implode("\n", [
    'Hi Rob,',
    '',
    'Thanks for sending this over. I have KOVAL down for the Local Distilleries event at Binny\'s Lincoln Park on Thursday, July 16 from 6:00-8:00 PM.',
    '',
    'I do not see the pour list form attachment on my side. Could you please resend it so I can complete that for you?',
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
    'source_ref' => trim($sourceMessageId, '<>'),
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'approved-send:nationaloutreach',
    'requester' => 'Rob Weekley <rweekley@binnys.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'ops_portal_or_domain_task' => 'OPS event ' . $eventId . ' / TrackTime shift ' . (string) ($row['shift_id'] ?? ''),
    'status' => 'completion_with_external_followup',
    'calendar_event' => 'ops-outreach-' . $eventId . '@koval-distillery.com',
    'source_links' => "Binny's Lincoln Park - Local Distilleries Event - 7/16/26",
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event readback completed; pour-list attachment unavailable in National Outreach runtime; reply queued asking Rob to resend it.',
    'next_update' => 'Watch for Rob Weekley to resend the pour-list form.',
    'requested_deliverable' => 'Confirm KOVAL attendance and fill out the Binny\'s pour list form.',
    'human_owner_or_recipient' => 'Rob Weekley <rweekley@binnys.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent Message-ID plus OPS event readback',
    'owner_question_required' => 'false',
];
$draftPayload = [
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['rweekley@binnys.com'],
    'cc' => ['sonat@kovaldistillery.com', 'brittney.barcelona@rndc-usa.com', 'robert@kovaldistillery.com'],
    'subject' => "Re: Binny's Lincoln Park - Local Distilleries Event - 7/16/26",
    'body' => $body,
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'source_ref' => trim($sourceMessageId, '<>'),
    'task_packet' => $taskPacket,
];
$draftPath = $outbox . '/binnys-lincoln-park-local-distilleries-2026-07-16.approved.json';
blp_write_json_file($draftPath, $draftPayload);

echo json_encode([
    'ok' => true,
    'event' => $row,
    'ops_url' => $opsUrl,
    'google_sync' => $googleSync,
    'draft' => $draftPath,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
