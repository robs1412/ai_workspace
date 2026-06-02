#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function tbws_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function tbws_market_token_user_id(PDO $pdo, array $preferredUserIds): ?int
{
    foreach ($preferredUserIds as $candidate) {
        $candidate = (int) $candidate;
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            return $candidate;
        }
    }

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

function tbws_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'market']);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventName = 'Tennessee Beer, Wine & Shine Festival';
$eventDate = '2026-10-17';
$eventStart = '12:00';
$eventEnd = '17:00';
$location = 'Two Rivers Mansion, 3130 McGavock Pike, Nashville, TN 37214';
$createdBy = 1332; // Codex
$eventHost = 1327; // Benjamin Green
$assignedUserId = 1327; // Benjamin Green
$cotGroupId = 169; // COTeam
$sourceMessageId = 'calbltzwaxvqrin8d+x0sz8yh5dxhgygx88suk37=pjlpeckdsq@mail.gmail.com';
$notes = implode("\n", [
    'Source: Sonat Birnecker email to Vanessa Sterling on 2026-05-29, subject "Beer Wine and Shine in Nashville, TN", Message-ID ' . $sourceMessageId . '.',
    'Direct instruction: add this Market Event to the OPS Market Event Calendar and attach Benjamin Green.',
    'Event page readback on 2026-05-30: Tennessee Beer, Wine & Shine Festival, Saturday October 17, 2026, noon-5 PM, Two Rivers Mansion, 3130 McGavock Pike, Nashville, TN 37214.',
    'Participation notes from source: no participation fee; samples billed back at 100%; Lipman Brothers coordinates product delivery and provides signage; booth setup includes tent, tables, chairs, ice, tub, signage, volunteers to pour, trash removal, and water.',
    'Source registration link: https://lipmanbrothers.wufoo.com/forms/tennessee-beer-wine-shine-festival-101726/',
    'Event website: https://tnbeerfestival.com/',
]);
$importantInformation = 'Market Event. Benjamin Green assigned for 12:00 PM-5:00 PM. VIP starts at 11:00 AM per source; public event page lists noon-5:00 PM.';

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupeStmt = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND (event_name LIKE ? OR event_location LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$eventDate, '%Beer%Wine%Shine%', '%Two Rivers Mansion%', '%' . $sourceMessageId . '%']);
    $eventId = (int) ($dupeStmt->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $updateEvent = $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = ?, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                    contact_name = ?, contact_email = ?, contact_phone = ?, amount_paid = ?,
                    estimated_guest_count = ?, notes = ?, important_information = ?,
                    event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $updateEvent->execute([
            $eventName,
            $eventDate,
            null,
            'Market Event',
            $location,
            null,
            $eventStart,
            $eventEnd,
            'Jonny Hobbs / Bill LaFollette',
            '',
            '',
            0,
            2000,
            $notes,
            $importantInformation,
            $eventHost,
            $eventId,
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
            $eventName,
            $eventDate,
            null,
            'Market Event',
            $location,
            null,
            $eventStart,
            $eventEnd,
            'Jonny Hobbs / Bill LaFollette',
            '',
            '',
            0,
            2000,
            null,
            null,
            $notes,
            $importantInformation,
            0,
            null,
            null,
            $createdBy,
            $eventHost,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = 'Market Event: Tennessee Beer, Wine & Shine Festival - Benjamin Green coverage';
    if ($shiftId > 0) {
        $updateShift = $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = 0, activity_id = 0, updated_by = ?
              WHERE id = ?"
        );
        $updateShift->execute([
            tbws_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
            $createdBy,
            $shiftId,
        ]);
    } else {
        $insertShift = $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, 0, 0, ?, ?)"
        );
        $insertShift->execute([
            tbws_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
            $createdBy,
            $createdBy,
        ]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $eventPdo->prepare('INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by) VALUES (?, ?, ?)')->execute([$eventId, $shiftId, $createdBy]);
    }

    $trackPdo->prepare("DELETE FROM " . TRACKTIME_DB_NAME . ".shift2user WHERE shift_id = ?")->execute([$shiftId]);
    $trackPdo->prepare("INSERT INTO " . TRACKTIME_DB_NAME . ".shift2user (shift_id, user_id) VALUES (?, ?)")->execute([$shiftId, $assignedUserId]);

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

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => '', 'calendar_type' => 'market'];
try {
    if (!google_oauth_is_configured() || !google_oauth_has_any_token()) {
        throw new RuntimeException('Google OAuth is not connected yet.');
    }
    $tokenUserId = tbws_market_token_user_id($eventPdo, [$createdBy, $eventHost]);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $calendarId = google_calendar_market_id();
    if ($calendarId === '') {
        throw new RuntimeException('Market calendar ID is not configured.');
    }
    $eventStmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $eventStmt->execute([$eventId]);
    $eventRow = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-market-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
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
    tbws_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid, 'calendar_type' => 'market'];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => '', 'calendar_type' => 'market'];
}

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
            eb.event_location, eb.estimated_guest_count, eb.event_host_user_id,
            CONCAT(vu.first_name, ' ', vu.last_name) AS event_host_name,
            l.shift_id, s.start_time AS shift_start, s.end_time AS shift_end, s.group_id,
            GROUP_CONCAT(s2u.user_id ORDER BY s2u.user_id SEPARATOR ',') AS assigned_user_ids,
            GROUP_CONCAT(CONCAT(avu.first_name, ' ', avu.last_name) ORDER BY avu.id SEPARATOR ', ') AS assigned_names,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN koval_crm.vtiger_users vu ON vu.id = eb.event_host_user_id
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN koval_crm.vtiger_users avu ON avu.id = s2u.user_id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);
echo json_encode(['event' => $readback->fetch(PDO::FETCH_ASSOC), 'google_sync' => $googleSync], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
