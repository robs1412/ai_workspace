#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function asia_argyle_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function asia_argyle_google_token_user_id(PDO $pdo): ?int
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

function asia_argyle_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
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

    $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?')->execute([$uid, $eventId]);
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'outreach']);
}

function asia_argyle_sync_google(PDO $pdo, int $eventId): array
{
    try {
        $tokenUserId = asia_argyle_google_token_user_id($pdo);
        if ($tokenUserId === null) {
            throw new RuntimeException('No usable Google OAuth refresh token user found.');
        }
        $eventStmt = $pdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
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
        asia_argyle_upsert_google_link($pdo, $eventId, $uid);
        return ['attempted' => true, 'status' => $operation, 'uid' => $uid];
    } catch (Throwable $e) {
        return ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => ''];
    }
}

function asia_argyle_upsert_event(PDO $eventPdo, PDO $trackPdo, array $spec): int
{
    $eventName = 'Asia on Argyle Night Market tasting';
    $eventStart = '18:00';
    $eventEnd = '20:00';
    $accountId = 25981; // Foremost Liquors - Argyle, existing CRM account for 1040 W Argyle St.
    $createdBy = 1332; // Codex
    $eventHost = 1343; // Vanessa Sterling
    $cotGroupId = 169; // COTeam
    $sourceMessageId = '92edeefa-f77f-43f4-a088-ed7b2e6457c6@rndc-usa.com';
    $sourceRef = 'taskflow-6ff5de79c7b87321 / taskflow-5bdfed26c4dd7f75';
    $location = 'Asia on Argyle Night Market / Hops & Grapes #3, 1040 W Argyle St, Chicago, IL 60640';
    $notes = implode("\n", [
        'Source: Taylor Oller / Sonat Birnecker thread, subject "Re: Industry Tours", Message-ID ' . $sourceMessageId . '.',
        'Taylor offered Asia on Argyle Night Market tasting opportunities through Hops & Grapes #3, which took over the license from Foremost on Argyle.',
        'Sonat accepted participation for July 9, 2026 and August 20, 2026.',
        'Event details from source: setup a street table, pour samples, and encourage guests to purchase KOVAL at the store.',
        'Products currently carried at the store per source: vodka, barrel aged gin, cranberry gin liqueur, dry gin, bourbon, rye, and two RTDs.',
        'Coordinator: Vanessa Sterling. Open COTeam shift is intentionally unassigned pending staff coverage.',
        'Task Flow: ' . $sourceRef . '.',
    ]);
    $importantInformation = 'Open COTeam coverage needed. Bring products carried at Hops & Grapes #3: vodka, barrel aged gin, cranberry gin liqueur, dry gin, bourbon, rye, and two RTDs.';

    $dupeStmt = $eventPdo->prepare(
        "SELECT eb.id
           FROM event_bookings eb
           LEFT JOIN event_booking_accounts eba ON eba.event_booking_id = eb.id
          WHERE eb.event_date = ?
            AND (eba.account_id = ? OR eb.distributor_account_id = ? OR eb.notes LIKE ? OR eb.event_location LIKE ?)
          ORDER BY eb.id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$spec['date'], $accountId, $accountId, '%' . $sourceMessageId . '%', '%Asia on Argyle%']);
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
            $spec['date'],
            null,
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            'Taylor Oller',
            'Taylor.Oller@RNDC-USA.COM',
            '224-463-1465',
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
            $spec['date'],
            null,
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            'Taylor Oller',
            'Taylor.Oller@RNDC-USA.COM',
            '224-463-1465',
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

    $eventPdo->prepare(
        'INSERT INTO event_booking_accounts (event_booking_id, account_id)
         VALUES (?, ?)
         ON DUPLICATE KEY UPDATE account_id = VALUES(account_id)'
    )->execute([$eventId, $accountId]);

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = 'Outreach: Asia on Argyle Night Market tasting - open COTeam coverage';
    if ($shiftId > 0) {
        $updateShift = $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = ?, activity_id = 0, updated_by = ?
              WHERE id = ?"
        );
        $updateShift->execute([
            asia_argyle_week_day_id($spec['date']),
            $spec['date'],
            $spec['date'],
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
            asia_argyle_week_day_id($spec['date']),
            $spec['date'],
            $spec['date'],
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

    return $eventId;
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$specs = [
    ['date' => '2026-07-09'],
    ['date' => '2026-08-20'],
];
$eventIds = [];

$eventPdo->beginTransaction();
if (!$trackPdo->inTransaction()) {
    $trackPdo->beginTransaction();
}

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    foreach ($specs as $spec) {
        $eventIds[] = asia_argyle_upsert_event($eventPdo, $trackPdo, $spec);
    }

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

$googleSync = [];
foreach ($eventIds as $eventId) {
    $googleSync[$eventId] = asia_argyle_sync_google($eventPdo, $eventId);
}

$placeholders = implode(',', array_fill(0, count($eventIds), '?'));
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
      WHERE eb.id IN ($placeholders)
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type
      ORDER BY eb.event_date ASC"
);
$readback->execute($eventIds);
echo json_encode(['events' => $readback->fetchAll(PDO::FETCH_ASSOC), 'google_sync' => $googleSync], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
