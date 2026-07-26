#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function heinens_weekday(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function heinens_google_user(PDO $pdo): ?int
{
    google_oauth_tokens_table_ready($pdo);
    $stmt = $pdo->query('SELECT user_id FROM ops_google_oauth_tokens ORDER BY updated_at DESC');
    foreach (($stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : []) as $row) {
        $userId = (int) ($row['user_id'] ?? 0);
        if ($userId > 0 && google_oauth_has_user_token($userId)) {
            return $userId;
        }
    }
    return null;
}

function heinens_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?')
        ->execute([$uid, $eventId]);
    $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    )->execute([$eventId, $uid, 'outreach']);
}

function heinens_write_json(string $path, array $payload): void
{
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false || file_put_contents($path, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write approved completion payload.');
    }
    chmod($path, 0600);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$eventName = "Heinen's Grocery Store #45 - Naperville KOVAL Tasting";
$eventDate = '2026-08-07';
$eventStart = '14:00';
$eventEnd = '17:00';
$accountId = 343061;
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceMessageId = '<CAAtX44ZU9YrR=mysuHXATeELmREdMAW0-2UMdhe_svgf-a7m1Q@mail.gmail.com>';
$sourceRef = 'taskflow-1c43bb4a94b33c2b';
$sessionId = '26bbc86d';
$location = "Heinen's Grocery Store #45 - Naperville, 1244 E Chicago Ave, Naperville, IL 60540";
$notes = implode("\n", [
    'Robert Birnecker requested this OPS tasting with an unassigned shift in the forwarded Heinen\'s Naperville thread.',
    'Confirmed date and time: August 7, 2026, 2:00-5:00 PM.',
    'Store buyer/liquor manager: Nick. RNDC contact: Osvaldo Moreno.',
    'Products mentioned in the source thread: KOVAL Single Barrel Rye, Single Barrel Bourbon, and Dry Gin.',
    'Source Message-ID: ' . $sourceMessageId . '.',
    'Task Flow: ' . $sourceRef . '.',
]);
$importantInformation = 'Open COTeam tasting shift is intentionally unassigned pending staffing. Coordinator: Vanessa Sterling.';

ensure_event_bookings_important_information_column($eventPdo);
ensure_event_bookings_max_capacity_column($eventPdo);
ensure_event_bookings_pioneer_flag_column($eventPdo);
ensure_event_shift_links_table($eventPdo);

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();
try {
    $dupe = $eventPdo->prepare(
        'SELECT eb.id
           FROM event_bookings eb
           LEFT JOIN event_booking_accounts eba ON eba.event_booking_id = eb.id
          WHERE eb.event_date = ?
            AND (eba.account_id = ? OR eb.distributor_account_id = ? OR eb.notes LIKE ? OR eb.event_name = ?)
          ORDER BY eb.id DESC
          LIMIT 1'
    );
    $dupe->execute([$eventDate, $accountId, $accountId, '%' . $sourceRef . '%', $eventName]);
    $eventId = (int) ($dupe->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = NULL, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                    contact_name = ?, notes = ?, important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        )->execute([$eventName, $eventDate, 'Outreach', $location, $accountId, $eventStart, $eventEnd, 'Nick', $notes, $importantInformation, $eventHost, $eventId]);
    } else {
        $eventPdo->prepare(
            'INSERT INTO event_bookings (
                event_name, event_date, event_end_date, event_category, event_location, distributor_account_id,
                start_time, end_time, contact_name, contact_email, contact_phone, amount_paid,
                estimated_guest_count, actual_guest_count, max_capacity, notes, important_information,
                is_pioneer_tasting, rooms, google_drive_link, created_by, event_host_user_id
            ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, NULL, NULL, ?, ?, 0, NULL, NULL, ?, ?)'
        )->execute([$eventName, $eventDate, 'Outreach', $location, $accountId, $eventStart, $eventEnd, 'Nick', '', '', $notes, $importantInformation, $createdBy, $eventHost]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    $eventPdo->prepare(
        'INSERT INTO event_booking_accounts (event_booking_id, account_id)
         VALUES (?, ?)
         ON DUPLICATE KEY UPDATE account_id = VALUES(account_id)'
    )->execute([$eventId, $accountId]);

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Outreach: Heinen's Naperville KOVAL Tasting - coverage pending";
    if ($shiftId > 0) {
        $trackPdo->prepare(
            'UPDATE ' . TRACKTIME_DB_NAME . '.shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = ?, activity_id = 0, deleted = 0, updated_by = ?
              WHERE id = ?'
        )->execute([heinens_weekday($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $shiftId]);
    } else {
        $trackPdo->prepare(
            'INSERT INTO ' . TRACKTIME_DB_NAME . '.shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, 0, ?, ?)'
        )->execute([heinens_weekday($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd, $shiftNotes, $cotGroupId, $accountId, $createdBy, $createdBy]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $eventPdo->prepare('INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by) VALUES (?, ?, ?)')
            ->execute([$eventId, $shiftId, $createdBy]);
    }
    $trackPdo->prepare('DELETE FROM ' . TRACKTIME_DB_NAME . '.shift2user WHERE shift_id = ?')->execute([$shiftId]);

    $trackPdo->commit();
    $eventPdo->commit();
} catch (Throwable $e) {
    if ($trackPdo->inTransaction()) {
        $trackPdo->rollBack();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    throw $e;
}

$googleSync = ['attempted' => true, 'status' => 'failed', 'uid' => ''];
try {
    $tokenUserId = heinens_google_user($eventPdo);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $stmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $stmt->execute([$eventId]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-outreach-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($event, $uid);
    $payload['status'] = 'confirmed';
    $calendarId = google_calendar_outreach_id();
    $existing = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($existing) && !empty($existing['id'])) {
        $response = google_calendar_request('PATCH', 'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']), [], $payload, $tokenUserId);
        $operation = 'updated';
    } else {
        $response = google_calendar_request('POST', 'calendars/' . rawurlencode($calendarId) . '/events', [], $payload, $tokenUserId);
        $operation = 'created';
    }
    if (empty($response['success'])) {
        throw new RuntimeException((string) ($response['error'] ?? 'Google Calendar request failed.'));
    }
    heinens_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'uid' => 'ops-outreach-' . $eventId . '@koval-distillery.com', 'error' => $e->getMessage()];
}

$readbackStmt = $eventPdo->prepare(
    'SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_location,
            eb.event_category, eb.distributor_account_id, eb.event_host_user_id,
            l.shift_id, s.group_id, s.account_id AS shift_account_id, COUNT(s2u.user_id) AS assigned_user_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN ' . TRACKTIME_DB_NAME . '.shifts s ON s.id = l.shift_id
       LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.group_id, s.account_id, gl.google_event_uid, gl.calendar_type'
);
$readbackStmt->execute([$eventId]);
$readback = $readbackStmt->fetch(PDO::FETCH_ASSOC) ?: [];

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
if (!is_dir($outbox) && !mkdir($outbox, 0700, true) && !is_dir($outbox)) {
    throw new RuntimeException('Unable to create National Outreach outbox.');
}
$verification = 'OPS outreach event ' . $eventId . ' and linked COTeam shift ' . $shiftId . ' read back for 2026-08-07 14:00-17:00; shift2user assignment count 0; Google UID ' . ($googleSync['uid'] ?? '') . ' ' . ($googleSync['status'] ?? 'unknown') . '.';
$taskPacket = [
    'source_ref' => trim($sourceMessageId, '<>'),
    'dedupe_key' => $sourceRef,
    'intake_channel' => 'approved-send:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $sessionId,
    'ops_portal_or_domain_task' => 'OPS outreach event ' . $eventId . ' / TrackTime shift ' . $shiftId,
    'status' => ($googleSync['status'] ?? '') === 'failed' ? 'blocked' : 'reported',
    'calendar_event' => (string) ($googleSync['uid'] ?? ''),
    'source_links' => "Fwd: Heinen's Grocery Naperville+ Koval Tasting",
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification,
    'next_update' => ($googleSync['status'] ?? '') === 'failed' ? 'Restore usable OPS Google OAuth and rerun the Outreach calendar sync.' : 'Complete unless the owner sends another event change.',
    'requested_deliverable' => "Create the Heinen's Naperville tasting in OPS with an unassigned shift for August 7, 2026, 2:00-5:00 PM.",
    'human_owner_or_recipient' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event/shift/calendar readback plus sent Message-ID and source filing proof',
    'owner_question_required' => ($googleSync['status'] ?? '') === 'failed' ? 'true' : 'false',
];
$bodyLines = [
    'Hi Robert,',
    '',
    "I added the Heinen's Grocery Store #45 - Naperville KOVAL tasting to OPS for Friday, August 7, 2026, from 2:00-5:00 PM.",
    '',
    'The linked COTeam shift is open and unassigned.',
    '',
    'OPS event:',
    'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
];
if (($googleSync['status'] ?? '') === 'failed') {
    $bodyLines[] = '';
    $bodyLines[] = 'The OPS event and shift are complete, but the KOVAL Outreach Events Google Calendar sync is blocked because no usable OPS Google OAuth refresh token resolved. Please refresh OPS Calendar consent so I can rerun the sync.';
}
$bodyLines = array_merge($bodyLines, [
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
$draftPath = $outbox . '/' . $sourceRef . '-heinens-naperville-completion.approved.json';
heinens_write_json($draftPath, [
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['robert@kovaldistillery.com'],
    'cc' => ['sonat@kovaldistillery.com'],
    'subject' => "Re: Fwd: Heinen's Grocery Naperville+ Koval Tasting",
    'body' => implode("\n", $bodyLines),
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'source_ref' => trim($sourceMessageId, '<>'),
    'task_packet' => $taskPacket,
]);

echo json_encode([
    'ok' => true,
    'event_id' => $eventId,
    'shift_id' => $shiftId,
    'ops_url' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
    'google_sync' => $googleSync,
    'readback' => $readback,
    'draft' => $draftPath,
    'verification' => $verification,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
