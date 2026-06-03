#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function downers_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function downers_google_token_user_id(PDO $pdo): ?int
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

function downers_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
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

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventName = "Binny's Downers Grove Midwest Whiskey Event";
$eventDate = '2026-07-18';
$eventStart = '13:00';
$eventEnd = '15:00';
$accountId = 2681;
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceMessageId = '<DS5PR13MB765371A7C1412059B4849DAFAA132@DS5PR13MB7653.namprd13.prod.outlook.com>';
$sourceRef = 'taskflow-49ba6e3ae76507d7';
$location = "Binny's Downers Grove, 2010 Butterfield Rd., Downers Grove, IL 60515";
$notes = implode("\n", [
    'Source: Rob Weekley email, subject "Binny\'s Downers Grove - Midwest Whiskey Event - 7/18/26", Message-ID ' . $sourceMessageId . '.',
    'Downers Grove team is hosting a walkaround whiskey event and asked KOVAL to be one of the showcased distilleries.',
    'Event details from source: Downers Grove, July 18, 2026, 1:00 PM-3:00 PM.',
    'Coordinator: Vanessa Sterling. Open COTeam shift is intentionally unassigned pending staff coverage.',
    'Task Flow: ' . $sourceRef . '.',
]);
$importantInformation = 'Walkaround whiskey event. Vanessa Sterling to coordinate with the copied Binny\'s Downers Grove team; open COTeam shift pending coverage assignment.';

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
    $dupeStmt->execute([$eventDate, $accountId, '%Downers Grove%Whiskey%', '%Downers Grove%', '%' . $sourceMessageId . '%']);
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
            $eventName,
            $eventDate,
            null,
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            'Rob Weekley',
            'rweekley@binnys.com',
            '',
            null,
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
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            'Rob Weekley',
            'rweekley@binnys.com',
            '',
            0,
            null,
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

    $accountExists = $eventPdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id = ? AND account_id = ? LIMIT 1');
    $accountExists->execute([$eventId, $accountId]);
    if (!$accountExists->fetchColumn()) {
        $eventPdo->prepare('INSERT INTO event_booking_accounts (event_booking_id, account_id) VALUES (?, ?)')->execute([$eventId, $accountId]);
    }

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Outreach: Binny's Downers Grove Midwest Whiskey Event - coverage pending";
    if ($shiftId > 0) {
        $updateShift = $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = ?, activity_id = 0, updated_by = ?
              WHERE id = ?"
        );
        $updateShift->execute([
            downers_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
            $accountId,
            $createdBy,
            $shiftId,
        ]);
    } else {
        $insertShift = $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, 0, ?, ?)"
        );
        $insertShift->execute([
            downers_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
            $accountId,
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
    $tokenUserId = downers_google_token_user_id($eventPdo);
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
    downers_upsert_google_link($eventPdo, $eventId, $uid);
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
echo json_encode(['event' => $row, 'google_sync' => $googleSync], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
