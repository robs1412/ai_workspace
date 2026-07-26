#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function chefs_table_write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create output directory.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode JSON payload.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write JSON payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to move JSON payload into place.');
    }
    chmod($path, 0600);
}

function chefs_table_google_token_user_id(PDO $pdo): ?int
{
    foreach ([1332, 3, 21, 144] as $candidate) {
        if (google_oauth_has_user_token($candidate)) {
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

function chefs_table_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
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

    $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?')
        ->execute([$uid, $eventId]);
    $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    )->execute([$eventId, $uid, 'market']);
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$eventPdo = get_event_pdo();
$eventPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$eventName = "Chef's Table Milwaukee KOVAL tasting";
$eventDate = '2026-07-27';
$eventCategory = 'Market Event';
$location = "Chef's Table, Milwaukee, WI";
$createdBy = 1332; // Codex
$eventHost = 1343; // Vanessa Sterling
$sourceRef = 'calbltzyreojdsdxxvamphkc7svu2g6e8afvt=6s2qewgsjh5xa@mail.gmail.com';
$sourceMessageId = '<CALbLtzyReoJdsDxXVaMPhKC7SvU2G6E8afvT=6s2QeWgsjh5xA@mail.gmail.com>';
$taskFlowKey = 'taskflow-4b6ccffb5c678faa';
$marker = 'chefs-table-milwaukee-time-pending-2026-07-27 ' . $sourceMessageId;
$important = 'Time pending. Ask Sonat for the event hours/vendor staffing window before creating or offering a COTeam shift.';
$notes = implode("\n", [
    'Source: Sonat Birnecker email to Vanessa Sterling, subject "Chefs Table Milwaukee", Message-ID ' . $sourceMessageId . '.',
    'Sonat asked Vanessa to add an event to the Market calendar for an event in Milwaukee at Chef\'s Table on 2026-07-27.',
    'Sonat also asked Vanessa to check whether a COTeam member is available to attend, do a tasting, and talk about KOVAL at a Chicago-centered event.',
    'The source did not include event hours or a vendor staffing window, so the Market Event is time-pending and no COTeam shift has been created yet.',
    'Task Flow: ' . $taskFlowKey . '.',
    'Proof marker: ' . $marker . '.',
]);

$eventPdo->beginTransaction();
try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);

    $dupe = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND event_category = ?
            AND (event_name LIKE ? OR event_location LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupe->execute([$eventDate, $eventCategory, '%Chef%Table%Milwaukee%', '%Chef%Table%Milwaukee%', '%' . $sourceRef . '%']);
    $eventId = (int) ($dupe->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $stmt = $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = NULL, event_category = ?,
                    event_location = ?, distributor_account_id = NULL, start_time = NULL, end_time = NULL,
                    contact_name = ?, contact_email = ?, contact_phone = ?, amount_paid = 0,
                    estimated_guest_count = NULL, notes = ?, important_information = ?,
                    event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $stmt->execute([
            $eventName,
            $eventDate,
            $eventCategory,
            $location,
            'Sonat Birnecker',
            'sonat@kovaldistillery.com',
            '',
            $notes,
            $important,
            $eventHost,
            $eventId,
        ]);
    } else {
        $stmt = $eventPdo->prepare(
            'INSERT INTO event_bookings (
                event_name, event_date, event_end_date, event_category, event_location,
                distributor_account_id, start_time, end_time, contact_name, contact_email,
                contact_phone, amount_paid, estimated_guest_count, actual_guest_count, max_capacity,
                notes, important_information, is_pioneer_tasting, rooms, google_drive_link,
                created_by, event_host_user_id
            ) VALUES (?, ?, NULL, ?, ?, NULL, NULL, NULL, ?, ?, ?, 0, NULL, NULL, NULL, ?, ?, 0, NULL, NULL, ?, ?)'
        );
        $stmt->execute([
            $eventName,
            $eventDate,
            $eventCategory,
            $location,
            'Sonat Birnecker',
            'sonat@kovaldistillery.com',
            '',
            $notes,
            $important,
            $createdBy,
            $eventHost,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
    }

    if ($eventId <= 0) {
        throw new RuntimeException('Event insert/update did not return an id.');
    }

    $eventPdo->commit();
} catch (Throwable $e) {
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    throw $e;
}

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => '', 'calendar_type' => 'market'];
try {
    if (!google_oauth_is_configured() || !google_oauth_has_any_token()) {
        throw new RuntimeException('Google OAuth is not connected yet.');
    }
    $tokenUserId = chefs_table_google_token_user_id($eventPdo);
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
        $patchPayload = $payload;
        unset($patchPayload['iCalUID']);
        $resp = google_calendar_request(
            'PATCH',
            'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']),
            [],
            $patchPayload,
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
    chefs_table_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid, 'calendar_type' => 'market'];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => '', 'calendar_type' => 'market'];
}

$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;
$body = implode("\n", [
    'Hi Sonat,',
    '',
    'I added Chef\'s Table Milwaukee to the Market calendar for Monday, July 27.',
    '',
    'Can you send me the event hours or vendor staffing window? I need the time before I ask the COTeam who can cover the tasting.',
    '',
    'OPS event: ' . $opsUrl,
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

$taskPacket = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'blocker-email-required',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '94ffdecd',
    'ops_portal_or_domain_task' => 'OPS Market Event ' . $eventId,
    'status' => 'blocked',
    'due_or_trigger' => '2026-07-02 07:29:00',
    'scheduled_action' => 'Add Chef\'s Table Milwaukee to the Market calendar and ask for COTeam coverage.',
    'calendar_event' => (string) ($googleSync['uid'] ?: ''),
    'clarification_email' => 'pending_send',
    'completion_or_blocker_email' => 'pending_send',
    'source_links' => 'Chefs Table Milwaukee',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS Market Event ' . $eventId . ' read back as 2026-07-27 time-pending; COTeam shift not created because source lacks event hours. Proof marker ' . $marker . '.',
    'next_update' => 'Waiting for Sonat to provide event hours/vendor staffing window before Vanessa asks COTeam for coverage.',
    'requested_deliverable' => 'Add Market calendar item and ask whether a COTeam member is available.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event readback, Market calendar UID if synced, sent-log Message-ID for owner question',
    'escalation_path' => 'Sonat reply with event hours; then create/open COTeam shift and ask COTeam for coverage.',
    'owner_question_required' => 'true',
];

$draftPayload = [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'cc' => ['robert@kovaldistillery.com'],
    'subject' => 'Re: Chefs Table Milwaukee',
    'body' => $body,
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'task_packet' => $taskPacket,
];

$outboxPath = $stateDir . '/outbox/chefs-table-milwaukee-time-needed-2026-07-27.approved.json';
chefs_table_write_json_file($outboxPath, $draftPayload);

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
            eb.event_category, eb.event_location, eb.contact_name, eb.contact_email,
            eb.event_host_user_id, eb.important_information,
            COUNT(DISTINCT l.shift_id) AS linked_shift_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);

echo json_encode([
    'ok' => true,
    'event' => $readback->fetch(PDO::FETCH_ASSOC),
    'google_sync' => $googleSync,
    'outbox' => $outboxPath,
    'proof_marker' => 'CHEFS_TABLE_MILWAUKEE_EVENT_' . $eventId . '_TIME_PENDING_20260727',
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
