#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

const EVENT_ID = 1054;
const SHIFT_ID = 5582;
const TARGET_DATE = '2026-06-13';
const TARGET_START = '13:00';
const TARGET_END = '15:00';
const UPDATED_BY = 1332; // Codex
const GOOGLE_UID = 'ops-outreach-1054@koval-distillery.com';

function wild_onion_note_contains(string $haystack, string $needle): bool
{
    return str_contains(strtolower($haystack), strtolower($needle));
}

function wild_onion_append_note(string $current, string $note): string
{
    $current = rtrim($current);
    if (wild_onion_note_contains($current, $note)) {
        return $current;
    }
    return trim($current . "\n" . $note);
}

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

function wild_onion_sync_google(PDO $eventPdo): array
{
    $tokenUserId = wild_onion_google_token_user_id($eventPdo);
    if ($tokenUserId === null) {
        return ['attempted' => true, 'status' => 'failed', 'error' => 'No usable Google OAuth refresh token user found.'];
    }

    $stmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $stmt->execute([EVENT_ID]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($event)) {
        return ['attempted' => true, 'status' => 'failed', 'error' => 'Event readback failed before Google sync.'];
    }

    $payload = google_calendar_build_event_payload($event, GOOGLE_UID);
    $payload['status'] = 'confirmed';
    $calendarId = google_calendar_outreach_id();
    $existing = google_calendar_find_event_by_icaluid($calendarId, GOOGLE_UID, true, $tokenUserId);
    $operation = 'created';
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
    }
    if (empty($resp['success'])) {
        return ['attempted' => true, 'status' => 'failed', 'error' => (string) ($resp['error'] ?? 'Google Calendar request failed.')];
    }

    $eventPdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    )->execute([EVENT_ID, GOOGLE_UID, 'outreach']);

    return ['attempted' => true, 'status' => $operation, 'uid' => GOOGLE_UID];
}

function wild_onion_readback(PDO $eventPdo): array
{
    $stmt = $eventPdo->prepare(
        "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
                eb.event_location, eb.important_information, eb.updated_at,
                l.shift_id, s.start_date, s.end_date, s.start_time AS shift_start, s.end_time AS shift_end,
                s.notes AS shift_notes, s.group_id, COUNT(s2u.user_id) AS assigned_user_count,
                gl.google_event_uid, gl.calendar_type
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
           LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
          WHERE eb.id = ? AND l.shift_id = ?
          GROUP BY eb.id, l.shift_id, s.id, gl.google_event_uid, gl.calendar_type"
    );
    $stmt->execute([EVENT_ID, SHIFT_ID]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return is_array($row) ? $row : [];
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$before = wild_onion_readback($eventPdo);
if ($before === []) {
    fwrite(STDERR, "Event " . EVENT_ID . " with shift " . SHIFT_ID . " was not found.\n");
    exit(1);
}

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();
try {
    $note = 'Updated shift note: covered taster should bring swag and tour passes.';
    $important = wild_onion_append_note((string) ($before['important_information'] ?? ''), $note);
    $shiftNotes = wild_onion_append_note((string) ($before['shift_notes'] ?? ''), $note);

    $eventPdo->prepare(
        'UPDATE event_bookings
            SET event_date = ?, event_end_date = NULL, start_time = ?, end_time = ?,
                important_information = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    )->execute([TARGET_DATE, TARGET_START, TARGET_END, $important, EVENT_ID]);

    $trackPdo->prepare(
        "UPDATE " . TRACKTIME_DB_NAME . ".shifts
            SET start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                notes = ?, updated_by = ?
          WHERE id = ?"
    )->execute([TARGET_DATE, TARGET_DATE, TARGET_START, TARGET_END, $shiftNotes, UPDATED_BY, SHIFT_ID]);

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

$google = wild_onion_sync_google($eventPdo);
$after = wild_onion_readback($eventPdo);

echo json_encode([
    'ok' => true,
    'before' => $before,
    'after' => $after,
    'google_sync' => $google,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
