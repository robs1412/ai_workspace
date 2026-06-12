#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';
require_once '/Users/werkstatt/ops/outreach_team_chat_notifier.php';

const EVENT_ID = 1054;
const SHIFT_ID = 5582;
const UPDATED_BY = 1332; // Codex
const GOOGLE_UID = 'ops-outreach-1054@koval-distillery.com';

function wild_onion_google_token_user_id(PDO $pdo): ?int
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

function wild_onion_readback(PDO $eventPdo, PDO $trackPdo): array
{
    $eventStmt = $eventPdo->prepare(
        "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
                eb.event_category, eb.event_location, l.shift_id, gl.google_event_uid
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
           LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
          WHERE eb.id = ?"
    );
    $eventStmt->execute([EVENT_ID]);
    $events = $eventStmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $shiftStmt = $trackPdo->prepare(
        "SELECT s.id, s.start_date, s.start_time, s.end_time, s.deleted,
                COUNT(s2u.user_id) AS assigned_count
           FROM " . TRACKTIME_DB_NAME . ".shifts s
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
          WHERE s.id = ?
          GROUP BY s.id, s.start_date, s.start_time, s.end_time, s.deleted"
    );
    $shiftStmt->execute([SHIFT_ID]);
    $shift = $shiftStmt->fetch(PDO::FETCH_ASSOC) ?: null;

    return [
        'event_rows' => $events,
        'shift_row' => $shift,
    ];
}

function wild_onion_delete_google(PDO $eventPdo): array
{
    $calendarId = google_calendar_outreach_id();
    if ($calendarId === '') {
        return ['attempted' => false, 'status' => 'no_outreach_calendar_id'];
    }
    $tokenUserId = wild_onion_google_token_user_id($eventPdo);
    if ($tokenUserId === null) {
        return ['attempted' => true, 'status' => 'failed', 'error' => 'No usable Google OAuth refresh token user found.'];
    }
    $existing = google_calendar_find_event_by_icaluid($calendarId, GOOGLE_UID, false, $tokenUserId);
    if (!is_array($existing) || empty($existing['id'])) {
        $eventPdo->prepare('DELETE FROM event_booking_google_links WHERE event_booking_id = ? AND calendar_type = ?')
            ->execute([EVENT_ID, 'outreach']);
        return ['attempted' => true, 'status' => 'not_found_link_removed', 'uid' => GOOGLE_UID];
    }
    $resp = google_calendar_request(
        'DELETE',
        'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']),
        [],
        null,
        $tokenUserId
    );
    if (empty($resp['success'])) {
        return [
            'attempted' => true,
            'status' => 'failed',
            'error' => (string) ($resp['error'] ?? 'Unable to delete Google event.'),
            'uid' => GOOGLE_UID,
        ];
    }
    $eventPdo->prepare('DELETE FROM event_booking_google_links WHERE event_booking_id = ? AND calendar_type = ?')
        ->execute([EVENT_ID, 'outreach']);
    return ['attempted' => true, 'status' => 'deleted', 'uid' => GOOGLE_UID];
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$before = wild_onion_readback($eventPdo, $trackPdo);
if (empty($before['event_rows']) && empty($before['shift_row'])) {
    echo json_encode([
        'ok' => true,
        'already_removed' => true,
        'event_id' => EVENT_ID,
        'shift_id' => SHIFT_ID,
        'before' => $before,
        'after' => $before,
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
    exit(0);
}

$google = wild_onion_delete_google($eventPdo);
if (($google['status'] ?? '') === 'failed') {
    fwrite(STDERR, json_encode(['ok' => false, 'google_delete' => $google], JSON_UNESCAPED_SLASHES) . "\n");
    exit(1);
}

$eventSnapshot = $before['event_rows'][0] ?? [];
$shiftSnapshot = is_array($before['shift_row']) ? $before['shift_row'] : [];

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();
try {
    if (!empty($shiftSnapshot)) {
        $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET deleted = 1, updated_by = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?"
        )->execute([UPDATED_BY, SHIFT_ID]);
    }

    $eventPdo->prepare('DELETE FROM event_bookings WHERE id = ?')->execute([EVENT_ID]);

    $trackPdo->commit();
    $eventPdo->commit();
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

try {
    if (!empty($shiftSnapshot)) {
        notify_outreach_team_chat_shift_canceled(SHIFT_ID, $shiftSnapshot, true);
    }
} catch (Throwable $ignored) {
}

record_shift_reliability_event('event_deleted', EVENT_ID, null, null, UPDATED_BY, 'Event deleted', [
    'event_name' => $eventSnapshot['event_name'] ?? '',
    'event_date' => $eventSnapshot['event_date'] ?? '',
    'start_time' => $eventSnapshot['start_time'] ?? '',
    'end_time' => $eventSnapshot['end_time'] ?? '',
    'event_category' => $eventSnapshot['event_category'] ?? '',
    'source' => 'Robert same-thread request 2026-06-12: remove the event in OPS.',
]);

$after = wild_onion_readback($eventPdo, $trackPdo);
echo json_encode([
    'ok' => true,
    'event_id' => EVENT_ID,
    'shift_id' => SHIFT_ID,
    'google_delete' => $google,
    'before' => $before,
    'after' => $after,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
