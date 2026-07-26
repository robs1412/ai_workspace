#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

const EVENT_ID = 1037;
const SHIFT_ID = 5565;
const UPDATED_BY = 1332; // Codex
const SOURCE_REF = 'caatx44zzygr8egvfavqoho_58fhzojot=x_=lebda_538e=_aa@mail.gmail.com';
const MARKER = '[binnys-phone-canceled:2026-07-25]';

function readback(PDO $eventPdo, PDO $trackPdo): array
{
    $eventStmt = $eventPdo->prepare(
        'SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
                eb.event_category, eb.event_location, eb.notes, eb.important_information,
                gl.google_event_uid, gl.calendar_type
           FROM event_bookings eb
           LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
          WHERE eb.id = ?'
    );
    $eventStmt->execute([EVENT_ID]);

    $shiftStmt = $trackPdo->prepare(
        'SELECT s.id, s.start_date, s.start_time, s.end_time, s.deleted, s.notes,
                COUNT(s2u.user_id) AS assigned_count
           FROM ' . TRACKTIME_DB_NAME . '.shifts s
           LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id = s.id
          WHERE s.id = ?
          GROUP BY s.id, s.start_date, s.start_time, s.end_time, s.deleted, s.notes'
    );
    $shiftStmt->execute([SHIFT_ID]);

    return [
        'event' => $eventStmt->fetch(PDO::FETCH_ASSOC) ?: null,
        'shift' => $shiftStmt->fetch(PDO::FETCH_ASSOC) ?: null,
    ];
}

function google_token_user_id(PDO $eventPdo, int $createdBy): ?int
{
    foreach (array_filter([$createdBy, UPDATED_BY]) as $candidate) {
        if (google_oauth_has_user_token((int) $candidate)) {
            return (int) $candidate;
        }
    }
    google_oauth_tokens_table_ready($eventPdo);
    $stmt = $eventPdo->query('SELECT user_id FROM ops_google_oauth_tokens ORDER BY updated_at DESC');
    foreach (($stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : []) as $row) {
        $candidate = (int) ($row['user_id'] ?? 0);
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            return $candidate;
        }
    }
    return null;
}

function sync_google_canceled_event(PDO $eventPdo): array
{
    $stmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $stmt->execute([EVENT_ID]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$event) {
        return ['ok' => false, 'status' => 'event_missing'];
    }

    $linkStmt = $eventPdo->prepare(
        'SELECT google_event_uid, calendar_type
           FROM event_booking_google_links
          WHERE event_booking_id = ? AND calendar_type = ?
          LIMIT 1'
    );
    $linkStmt->execute([EVENT_ID, 'outreach']);
    $link = $linkStmt->fetch(PDO::FETCH_ASSOC) ?: [];
    $uid = trim((string) ($link['google_event_uid'] ?? ''));
    if ($uid === '') {
        return ['ok' => false, 'status' => 'google_link_missing'];
    }

    $calendarId = google_calendar_outreach_id();
    if ($calendarId === '') {
        return ['ok' => false, 'status' => 'outreach_calendar_not_configured'];
    }
    $tokenUserId = google_token_user_id($eventPdo, (int) ($event['created_by'] ?? 0));
    if ($tokenUserId === null) {
        return ['ok' => false, 'status' => 'google_token_unavailable'];
    }
    $googleEvent = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (!is_array($googleEvent) || empty($googleEvent['id'])) {
        return ['ok' => false, 'status' => 'google_event_not_found', 'uid' => $uid];
    }
    $payload = google_calendar_build_event_payload($event, $uid);
    $payload['status'] = 'confirmed';
    $response = google_calendar_request(
        'PATCH',
        'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $googleEvent['id']),
        [],
        $payload,
        $tokenUserId
    );
    if (empty($response['success'])) {
        return [
            'ok' => false,
            'status' => 'google_patch_failed',
            'error' => (string) ($response['error'] ?? 'unknown Google Calendar error'),
            'uid' => $uid,
        ];
    }
    return ['ok' => true, 'status' => 'patched_canceled_title', 'uid' => $uid];
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$before = readback($eventPdo, $trackPdo);
$event = $before['event'];
$shift = $before['shift'];

if (!is_array($event) || !is_array($shift)) {
    throw new RuntimeException('Expected OPS event 1037 and TrackTime shift 5565 were not both found.');
}
if ((int) ($event['id'] ?? 0) !== EVENT_ID
    || (int) ($shift['id'] ?? 0) !== SHIFT_ID
    || (string) ($event['event_date'] ?? '') !== '2026-07-25'
    || stripos((string) ($event['event_name'] ?? ''), "Binny's Hyde Park") === false) {
    throw new RuntimeException('Live OPS target does not match the approved Binny\'s Hyde Park cancellation.');
}
if ((int) ($shift['assigned_count'] ?? 0) !== 0) {
    throw new RuntimeException('Refusing cancellation because shift 5565 now has an assignee.');
}

$alreadyCanceled = stripos((string) $event['event_name'], 'CANCELED - ') === 0
    && str_contains((string) ($event['notes'] ?? ''), MARKER)
    && (int) ($shift['deleted'] ?? 0) === 1;

if (!$alreadyCanceled) {
    $note = 'Cancellation handled by Sonat by phone per Robert source ' . SOURCE_REF
        . '; no cancellation email sent. ' . MARKER;
    $eventName = stripos((string) $event['event_name'], 'CANCELED - ') === 0
        ? (string) $event['event_name']
        : 'CANCELED - ' . (string) $event['event_name'];
    $notes = str_contains((string) ($event['notes'] ?? ''), MARKER)
        ? (string) ($event['notes'] ?? '')
        : rtrim((string) ($event['notes'] ?? '')) . "\n\n" . $note;
    $important = str_contains((string) ($event['important_information'] ?? ''), MARKER)
        ? (string) ($event['important_information'] ?? '')
        : rtrim((string) ($event['important_information'] ?? '')) . "\n\n" . $note;
    $shiftNotes = str_contains((string) ($shift['notes'] ?? ''), MARKER)
        ? (string) ($shift['notes'] ?? '')
        : rtrim((string) ($shift['notes'] ?? '')) . "\n\n" . $note;

    $eventPdo->beginTransaction();
    $trackPdo->beginTransaction();
    try {
        $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        )->execute([$eventName, $notes, $important, EVENT_ID]);
        $trackPdo->prepare(
            'UPDATE ' . TRACKTIME_DB_NAME . '.shifts
                SET deleted = 1, notes = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        )->execute([$shiftNotes, UPDATED_BY, SHIFT_ID]);
        $trackPdo->commit();
        $eventPdo->commit();
    } catch (Throwable $error) {
        if ($trackPdo->inTransaction()) {
            $trackPdo->rollBack();
        }
        if ($eventPdo->inTransaction()) {
            $eventPdo->rollBack();
        }
        throw $error;
    }
}

$google = sync_google_canceled_event($eventPdo);
$after = readback($eventPdo, $trackPdo);
$ok = str_starts_with((string) ($after['event']['event_name'] ?? ''), 'CANCELED - ')
    && str_contains((string) ($after['event']['notes'] ?? ''), MARKER)
    && (int) ($after['shift']['deleted'] ?? 0) === 1
    && (int) ($after['shift']['assigned_count'] ?? -1) === 0
    && ($google['ok'] ?? false);

echo json_encode([
    'ok' => $ok,
    'already_canceled' => $alreadyCanceled,
    'event_id' => EVENT_ID,
    'shift_id' => SHIFT_ID,
    'marker' => MARKER,
    'google' => $google,
    'after' => [
        'event_name' => $after['event']['event_name'] ?? '',
        'event_date' => $after['event']['event_date'] ?? '',
        'shift_deleted' => (int) ($after['shift']['deleted'] ?? -1),
        'assigned_count' => (int) ($after['shift']['assigned_count'] ?? -1),
        'marker_present' => str_contains((string) ($after['event']['notes'] ?? ''), MARKER),
    ],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";

exit($ok ? 0 : 1);
