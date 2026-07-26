#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

$eventId = 1028;
$shiftId = 5556;
$eventDate = '2026-07-18';
$startTime = '18:00';
$endTime = '20:00';
$googleUserId = 1;
$uid = 'ops-outreach-1028@koval-distillery.com';

if (!google_oauth_has_user_token($googleUserId)) {
    throw new RuntimeException('Robert OPS user has no usable Google refresh token.');
}
$accessMeta = google_oauth_fetch_access_token($googleUserId);
if (empty($accessMeta['token'])) {
    throw new RuntimeException('Google access-token exchange failed for Robert OPS user.');
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventCheck = $eventPdo->prepare(
    'SELECT eb.id, eb.event_date, l.shift_id
       FROM event_bookings eb
       JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
      WHERE eb.id = ? AND l.shift_id = ?'
);
$eventCheck->execute([$eventId, $shiftId]);
$existing = $eventCheck->fetch(PDO::FETCH_ASSOC);
if (!is_array($existing) || (string) $existing['event_date'] !== $eventDate) {
    throw new RuntimeException('Expected OPS event/shift link or event date did not read back.');
}

$eventPdo->beginTransaction();
if (!$trackPdo->inTransaction()) {
    $trackPdo->beginTransaction();
}
try {
    $eventPdo->prepare(
        'UPDATE event_bookings
            SET start_time = ?, end_time = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ? AND event_date = ?'
    )->execute([$startTime, $endTime, $eventId, $eventDate]);

    $trackPdo->prepare(
        'UPDATE ' . TRACKTIME_DB_NAME . '.shifts
            SET start_time = ?, end_time = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ? AND start_date = ?'
    )->execute([$startTime, $endTime, 1332, $shiftId, $eventDate]);

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
    throw $e;
}

$eventStmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
$eventStmt->execute([$eventId]);
$eventRow = $eventStmt->fetch(PDO::FETCH_ASSOC);
if (!is_array($eventRow)) {
    throw new RuntimeException('Updated event could not be read for Google sync.');
}

$calendarId = google_calendar_outreach_id();
if ($calendarId === '') {
    throw new RuntimeException('Outreach Google Calendar is not configured.');
}
$payload = google_calendar_build_event_payload($eventRow, $uid);
$payload['status'] = 'confirmed';
$googleExisting = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $googleUserId);
if (!is_array($googleExisting) || empty($googleExisting['id'])) {
    throw new RuntimeException('Existing Outreach Google event was not found by UID.');
}
$response = google_calendar_request(
    'PATCH',
    'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $googleExisting['id']),
    [],
    $payload,
    $googleUserId
);
if (empty($response['success'])) {
    throw new RuntimeException((string) ($response['error'] ?? 'Google Calendar update failed.'));
}

$googleReadback = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $googleUserId);
if (!is_array($googleReadback) || empty($googleReadback['id'])) {
    throw new RuntimeException('Updated Google event could not be read back by UID.');
}

$readback = $eventPdo->prepare(
    'SELECT eb.id, eb.event_date, eb.start_time, eb.end_time, l.shift_id,
            s.start_time AS shift_start, s.end_time AS shift_end,
            COUNT(s2u.user_id) AS assigned_users,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       JOIN ' . TRACKTIME_DB_NAME . '.shifts s ON s.id = l.shift_id
       LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ? AND l.shift_id = ?
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, gl.google_event_uid, gl.calendar_type'
);
$readback->execute([$eventId, $shiftId]);

echo json_encode([
    'ok' => true,
    'ops' => $readback->fetch(PDO::FETCH_ASSOC),
    'oauth' => [
        'user_id' => $googleUserId,
        'usable_refresh_token' => true,
        'access_exchange_success' => true,
    ],
    'google' => [
        'ical_uid' => (string) ($googleReadback['iCalUID'] ?? $uid),
        'status' => (string) ($googleReadback['status'] ?? ''),
        'start' => $googleReadback['start'] ?? null,
        'end' => $googleReadback['end'] ?? null,
        'location' => (string) ($googleReadback['location'] ?? ''),
    ],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
