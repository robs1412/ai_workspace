#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function ftcc_market_token_user_id(PDO $pdo, array $preferredUserIds): ?int
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

function ftcc_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'market']);
}

$eventPdo = get_event_pdo();

$eventName = 'The Fox Theater Cocktail Competition';
$eventDate = '2026-07-18';
$location = 'Atlanta, GA';
$createdBy = 1332; // Codex
$sourceMessageId = 'CALbLtzwmu1K4tq0urqkCgdkXyfRcFPOw5SWh==YpEopwEgfeeA@mail.gmail.com';
$notes = implode("\n", [
    'Source: Sonat Birnecker email to Vanessa Sterling on 2026-06-15, subject "Market Visit for Fox Theater Competition July 18th", Message-ID <' . $sourceMessageId . '>.',
    'Direct instruction: add a Market event into OPS for The Fox Theater Cocktail Competition in Atlanta, GA.',
    'Attendee is not known yet per source; no shift, host, account, contact, products, costs, or tasks were added.',
]);
$importantInformation = 'Market Event placeholder. Attendee not yet known; add staffing/shift details when Sonat confirms who will attend.';

$eventPdo->beginTransaction();

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupeStmt = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND event_category = 'Market Event'
            AND (event_name LIKE ? OR event_location LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$eventDate, '%Fox%Theater%Cocktail%Competition%', '%Atlanta%', '%' . $sourceMessageId . '%']);
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
            null,
            null,
            '',
            '',
            '',
            0,
            null,
            $notes,
            $importantInformation,
            null,
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
            null,
            null,
            '',
            '',
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
            null,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }
} catch (Throwable $e) {
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
    $tokenUserId = ftcc_market_token_user_id($eventPdo, [$createdBy, 3, 21, 144]);
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
    ftcc_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid, 'calendar_type' => 'market'];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => '', 'calendar_type' => 'market'];
}

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.event_end_date, eb.start_time, eb.end_time,
            eb.event_category, eb.event_location, eb.event_host_user_id, eb.created_by,
            CONCAT(cu.first_name, ' ', cu.last_name) AS created_by_name,
            COUNT(DISTINCT l.shift_id) AS linked_shift_count,
            COUNT(DISTINCT ebs.user_id) AS staff_count,
            COUNT(DISTINCT ebt.id) AS task_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN koval_crm.vtiger_users cu ON cu.id = eb.created_by
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN event_booking_staff ebs ON ebs.event_booking_id = eb.id
       LEFT JOIN event_booking_tasks ebt ON ebt.event_booking_id = eb.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);

echo json_encode(['event' => $readback->fetch(PDO::FETCH_ASSOC), 'google_sync' => $googleSync], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
