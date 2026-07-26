#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function ctm_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function ctm_token_user_id(PDO $pdo, array $preferred): ?int
{
    foreach ($preferred as $candidate) {
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

function ctm_write_json(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create outbox directory.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode outbox payload.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write outbox payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install outbox payload.');
    }
    chmod($path, 0600);
}

function ctm_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    )->execute([$eventId, $uid, 'market']);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$eventPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$trackPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$eventId = 1128;
$eventDate = '2026-07-27';
$eventStart = '18:00';
$eventEnd = '21:00';
$createdBy = 1332;
$eventHost = 1343;
$cotGroupId = 169;
$sourceRef = 'calbltzydqc+kwqlxrjxepnjf+5vauf2qbsc_tnx3si4gpm++ca@mail.gmail.com';
$sourceMessageId = '<CALbLtzyDqc+KwqLxRJXEPNjF+5VAUF2qBsc_tNX3si4GPM++cA@mail.gmail.com>';
$taskFlowKey = 'taskflow-45de8ae346ee459f';
$sessionId = 'cc6fc47f';
$proofMarker = 'CHEFS_TABLE_MILWAUKEE_EVENT_1128_SHIFT_TIME_1800_2100_SOFIA_ASK_20260715';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;

$notes = implode("\n", [
    'Source request: Sonat Birnecker email to Vanessa Sterling, subject "Chefs Table Milwaukee", Message-ID <CALbLtzyReoJdsDxXVaMPhKC7SvU2G6E8afvT=6s2QeWgsjh5xA@mail.gmail.com>.',
    'Follow-up details: Sonat Birnecker email to Vanessa Sterling, subject "Chef\'s table event in Milwaukee", Message-ID ' . $sourceMessageId . '.',
    'Event runs 6:00 PM-9:00 PM on Monday, July 27, 2026, with more than 150 guests expected, mostly industry attendees.',
    'KOVAL will be set up in the speakeasy to walk guests through selected products.',
    'The main bar will feature KOVAL cocktails and RTDs for purchase.',
    'Sofia More availability requested by Vanessa; leave the linked COTeam shift unassigned until Sofia confirms.',
    'Task Flow: ' . $taskFlowKey . '.',
    'Proof marker: ' . $proofMarker . '.',
]);
$important = 'Market Event, 6:00 PM-9:00 PM. 150+ expected guests, mostly industry. KOVAL speakeasy setup; KOVAL cocktails and RTDs featured at main bar. Sofia More availability pending.';

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();
try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $existing = $eventPdo->prepare(
        "SELECT id FROM event_bookings
          WHERE id = ? AND event_date = ? AND event_category = 'Market Event'
            AND event_name LIKE '%Chef%Table%Milwaukee%'
          LIMIT 1"
    );
    $existing->execute([$eventId, $eventDate]);
    if ((int) ($existing->fetchColumn() ?: 0) !== $eventId) {
        throw new RuntimeException('Expected OPS Market Event 1128 was not found.');
    }

    $eventPdo->prepare(
        'UPDATE event_bookings
            SET start_time = ?, end_time = ?, estimated_guest_count = ?, notes = ?,
                important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    )->execute([$eventStart, $eventEnd, 150, $notes, $important, $eventHost, $eventId]);

    $shiftLookup = $eventPdo->prepare(
        'SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1'
    );
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Market Event: Chef's Table Milwaukee - Sofia More availability pending";
    if ($shiftId > 0) {
        $trackPdo->prepare(
            'UPDATE ' . TRACKTIME_DB_NAME . '.shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = 0, activity_id = 0, updated_by = ?
              WHERE id = ?'
        )->execute([
            ctm_week_day_id($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd,
            $shiftNotes, $cotGroupId, $createdBy, $shiftId,
        ]);
    } else {
        $trackPdo->prepare(
            'INSERT INTO ' . TRACKTIME_DB_NAME . '.shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes,
              is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, 0, 0, ?, ?)'
        )->execute([
            ctm_week_day_id($eventDate), $eventDate, $eventDate, $eventStart, $eventEnd,
            $shiftNotes, $cotGroupId, $createdBy, $createdBy,
        ]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $eventPdo->prepare(
            'INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by) VALUES (?, ?, ?)'
        )->execute([$eventId, $shiftId, $createdBy]);
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
    throw $e;
}

$googleSync = ['attempted' => true, 'status' => 'failed', 'calendar_type' => 'market', 'uid' => ''];
try {
    if (!google_oauth_is_configured() || !google_oauth_has_any_token()) {
        throw new RuntimeException('Google OAuth is not connected.');
    }
    $tokenUserId = ctm_token_user_id($eventPdo, [$createdBy, $eventHost]);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $calendarId = google_calendar_market_id();
    if ($calendarId === '') {
        throw new RuntimeException('Market calendar ID is not configured.');
    }
    $stmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $stmt->execute([$eventId]);
    $eventRow = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-market-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
    $remote = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($remote) && !empty($remote['id'])) {
        unset($payload['iCalUID']);
        $response = google_calendar_request(
            'PATCH',
            'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $remote['id']),
            [],
            $payload,
            $tokenUserId
        );
        $operation = 'patched';
    } else {
        $response = google_calendar_request(
            'POST',
            'calendars/' . rawurlencode($calendarId) . '/events',
            [],
            $payload,
            $tokenUserId
        );
        $operation = 'created';
    }
    if (empty($response['success'])) {
        throw new RuntimeException((string) ($response['error'] ?? 'Google Calendar request failed.'));
    }
    ctm_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'calendar_type' => 'market', 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync['error'] = $e->getMessage();
}

$body = implode("\n", [
    'Hi Sofia,',
    '',
    'Could you attend the Chef\'s Table event in Milwaukee on Monday, July 27, from 6:00 PM to 9:00 PM?',
    '',
    'They are expecting more than 150 guests, mostly from the industry. KOVAL will be set up in the speakeasy to walk guests through selected products, and the main bar will feature KOVAL cocktails and RTDs for purchase.',
    '',
    'Please let me know if you can cover it. The shift is open in OPS pending your confirmation:',
    $opsUrl,
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

$packet = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $sessionId,
    'ops_portal_or_domain_task' => 'OPS Market Event 1128 / COTeam shift ' . $shiftId,
    'status' => 'waiting',
    'due_or_trigger' => '2026-07-16 19:30:00',
    'scheduled_action' => 'Check for Sofia More reply if availability remains unanswered.',
    'calendar_event' => (string) ($googleSync['uid'] ?? ''),
    'completion_or_blocker_email' => 'availability request queued to Sofia More with Sonat and Robert copied',
    'source_links' => "Chef's table event in Milwaukee; " . $opsUrl,
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS Market Event 1128 updated to 2026-07-27 18:00-21:00 with 150+ guest and product-placement notes; linked COTeam shift ' . $shiftId . ' left unassigned pending Sofia; Market calendar sync status=' . $googleSync['status'] . '; proof marker=' . $proofMarker . '.',
    'papers_projection' => 'not_required_event_execution',
    'next_update' => 'Await Sofia reply; assign her through shift2user only if she confirms availability.',
    'requested_deliverable' => 'Update the Market Event with final details and ask Sofia if she can attend.',
    'human_owner_or_recipient' => 'Sofia More <sofiamore7@gmail.com>; Sonat Birnecker <sonat@kovaldistillery.com>; Robert Birnecker <robert@kovaldistillery.com>',
    'output_channel' => 'email + OPS + Market Google Calendar + Workspaceboard',
    'proof_required' => 'OPS event/shift readback, market calendar readback, sent-log Message-ID, source archive proof',
    'due_or_next_update' => '2026-07-16 19:30 CDT if Sofia has not replied',
    'escalation_path' => 'If Sofia declines or does not reply, ask Sonat whether Vanessa should open the shift to the broader COTeam.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$outboxPath = '/Users/admin/.nationaloutreach-launch/state/outbox/' . $taskFlowKey . '-chefs-table-sofia-availability.approved.json';
ctm_write_json($outboxPath, [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sofiamore7@gmail.com'],
    'cc' => ['sonat@kovaldistillery.com', 'robert@kovaldistillery.com'],
    'subject' => "Chef's Table Milwaukee coverage - July 27",
    'body' => $body,
    'task_packet' => $packet,
]);

$readback = $eventPdo->prepare(
    'SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
            eb.event_location, eb.estimated_guest_count, eb.important_information,
            l.shift_id, s.start_time AS shift_start, s.end_time AS shift_end, s.group_id,
            GROUP_CONCAT(s2u.user_id ORDER BY s2u.user_id SEPARATOR ",") AS assigned_user_ids,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN ' . TRACKTIME_DB_NAME . '.shifts s ON s.id = l.shift_id
       LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type'
);
$readback->execute([$eventId]);

echo json_encode([
    'ok' => true,
    'event' => $readback->fetch(PDO::FETCH_ASSOC),
    'google_sync' => $googleSync,
    'outbox' => basename($outboxPath),
    'proof_marker' => $proofMarker,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
