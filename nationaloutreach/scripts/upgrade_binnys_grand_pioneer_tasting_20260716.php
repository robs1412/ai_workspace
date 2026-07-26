#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';
require_once '/Users/werkstatt/ops/outreach_team_chat_notifier.php';

const EVENT_ID = 1040;
const SHIFT_ID = 5568;
const SOURCE_REF = 'caatx44y1qjf_+es_fz47mxhzfspe8sahnvtmfzvrf9klbcm0za@mail.gmail.com';
const SOURCE_MESSAGE_ID = '<CAAtX44Y1Qjf_+Es_Fz47mxHzFsPE8SaHNvtMfZVRF9kLbCM0ZA@mail.gmail.com>';
const TASK_FLOW_KEY = 'taskflow-4faa205460a17035';
const WORKSPACEBOARD_SESSION = '90a98885';
const PROOF_MARKER = 'OPS_1040_PIONEER_1_CHAT_POSTED_SHIFT_5568';

/** @param array<string,mixed> $payload */
function write_json_file(string $path, array $payload): void
{
    $directory = dirname($path);
    if (!is_dir($directory) && !mkdir($directory, 0700, true) && !is_dir($directory)) {
        throw new RuntimeException('Unable to create the National Outreach outbox.');
    }
    $encoded = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($encoded === false) {
        throw new RuntimeException('Unable to encode the completion draft.');
    }
    $temporary = $path . '.tmp.' . getmypid();
    if (file_put_contents($temporary, $encoded . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write the completion draft.');
    }
    chmod($temporary, 0600);
    if (!rename($temporary, $path)) {
        @unlink($temporary);
        throw new RuntimeException('Unable to install the completion draft.');
    }
    chmod($path, 0600);
}

/** @param array<string,mixed> $packet */
function record_task_flow(array $packet, string $event): void
{
    $process = proc_open(
        ['/usr/local/bin/php', '/Users/werkstatt/workspaceboard/scripts/planner/task_flow_mysql_recorder.php', 'record'],
        [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
        $pipes,
        '/Users/werkstatt/workspaceboard'
    );
    if (!is_resource($process)) {
        throw new RuntimeException('Unable to start the Task Flow recorder.');
    }
    fwrite($pipes[0], json_encode(['event' => $event, 'packet' => $packet], JSON_UNESCAPED_SLASHES) ?: '{}');
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    $exitCode = proc_close($process);
    if ($exitCode !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

/** @return array<string,mixed> */
function fetch_readback(PDO $pdo, bool $forUpdate = false): array
{
    $sql = "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
                   eb.event_category, eb.event_location, eb.is_pioneer_tasting,
                   l.shift_id, COUNT(s2u.user_id) AS assigned_count,
                   gl.google_event_uid, gl.calendar_type
              FROM event_bookings eb
              LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
              LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = l.shift_id
              LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
             WHERE eb.id = ?
             GROUP BY eb.id, l.shift_id, gl.google_event_uid, gl.calendar_type";
    if ($forUpdate) {
        $sql .= ' FOR UPDATE';
    }
    $stmt = $pdo->prepare($sql);
    $stmt->execute([EVENT_ID]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($row)) {
        throw new RuntimeException('OPS event 1040 was not found.');
    }
    return $row;
}

$eventPdo = get_event_pdo();
$eventPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$eventPdo->beginTransaction();
try {
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    $before = fetch_readback($eventPdo, true);
    if ((string) $before['event_name'] !== "Binny's Grand Downtown Tasting"
        || (string) $before['event_date'] !== '2026-07-18'
        || (int) $before['shift_id'] !== SHIFT_ID) {
        throw new RuntimeException('OPS event 1040 no longer matches the reviewed Binny\'s Grand Downtown packet.');
    }
    if ((string) ($before['calendar_type'] ?? '') !== 'outreach'
        || trim((string) ($before['google_event_uid'] ?? '')) === '') {
        throw new RuntimeException('OPS event 1040 is missing its Outreach Google Calendar linkage.');
    }
    if ((int) $before['is_pioneer_tasting'] !== 1) {
        $update = $eventPdo->prepare(
            'UPDATE event_bookings
                SET is_pioneer_tasting = 1, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $update->execute([EVENT_ID]);
        if ($update->rowCount() !== 1) {
            throw new RuntimeException('OPS event 1040 Pioneer flag update did not affect one row.');
        }
    }
    $eventPdo->commit();
} catch (Throwable $exception) {
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    throw $exception;
}

$event = fetch_readback($eventPdo);
if ((int) $event['is_pioneer_tasting'] !== 1) {
    throw new RuntimeException('OPS event 1040 Pioneer flag readback failed.');
}

ensure_outreach_team_chat_log_table($eventPdo);
$chatType = 'pioneer_upgrade';
$existingChat = outreach_team_chat_event_already_sent(
    $eventPdo,
    EVENT_ID,
    SHIFT_ID,
    $chatType,
    OUTREACH_TEAM_CHAT_TARGET
);
$chatMessageName = '';
$chatStatus = 'skipped_already_sent';
if ($existingChat) {
    $chatLookup = $eventPdo->prepare(
        'SELECT chat_message_name
           FROM ' . OUTREACH_TEAM_CHAT_LOG_TABLE . '
          WHERE event_booking_id = ? AND shift_id = ? AND notification_type = ? AND chat_target = ?
          LIMIT 1'
    );
    $chatLookup->execute([EVENT_ID, SHIFT_ID, $chatType, OUTREACH_TEAM_CHAT_TARGET]);
    $chatMessageName = trim((string) ($chatLookup->fetchColumn() ?: ''));
} else {
    $chatMessage = implode("\n", [
        "Binny's Grand Downtown is now a Pioneer Tasting:",
        '',
        '- Saturday, July 18, 12:00 PM-3:00 PM',
        '- OPS event #1040 / open shift #5568',
        '- Location: Binny\'s Grand Downtown',
        '- OPS: https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=1040',
        '',
        'The event has been marked as a Pioneer Tasting in OPS. The linked COTeam shift is still open; please reply here or claim it in OPS if you can cover.',
    ]);
    $chatResult = send_outreach_team_chat_message($chatMessage);
    if (!($chatResult['ok'] ?? false)) {
        throw new RuntimeException('Outreach Team chat post failed: ' . (string) ($chatResult['error'] ?? 'unknown error'));
    }
    $chatMessageName = trim((string) (($chatResult['message']['name'] ?? '') ?: ''));
    if ($chatMessageName === '') {
        throw new RuntimeException('Outreach Team chat post returned no message id.');
    }
    record_outreach_team_chat_notification($eventPdo, [
        'event_id' => EVENT_ID,
        'shift_id' => SHIFT_ID,
        'notification_type' => $chatType,
        'notification_key' => 'outreach-team-chat|pioneer-upgrade|' . TASK_FLOW_KEY,
        'chat_target' => OUTREACH_TEAM_CHAT_TARGET,
        'chat_message_name' => $chatMessageName,
    ]);
    $chatStatus = 'sent';
}

$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . EVENT_ID;
$verification = 'Live OPS readback: event 1040 is_pioneer_tasting=1; linked open shift 5568 assigned_count=' . (int) $event['assigned_count']
    . '; Outreach Calendar UID remains linked; Outreach Team chat message id recorded.';
$packet = [
    'source_ref' => SOURCE_REF,
    'dedupe_key' => TASK_FLOW_KEY,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => WORKSPACEBOARD_SESSION,
    'ops_portal_or_domain_task' => 'OPS Outreach event 1040; open shift 5568',
    'status' => 'reported',
    'due_or_trigger' => 'Robert instructed Vanessa to upgrade the event to a Pioneer Tasting and post it in chat.',
    'calendar_event' => 'OPS event 1040, Outreach calendar',
    'source_links' => 'Re: Open COT shifts for Saturday, July 18',
    'approval_gates' => 'Direct Robert instruction; routine OPS update and internal team chat post approved.',
    'verification_readback' => $verification,
    'next_update' => 'Await COTeam claim for open shift 5568.',
    'requested_deliverable' => 'Mark Binny\'s Grand Downtown as a Pioneer Tasting and post the update in team chat.',
    'human_owner_or_recipient' => 'Robert Birnecker; Outreach Team Google Chat',
    'output_channel' => 'OPS, Outreach Team Google Chat, and same-thread email',
    'proof_required' => 'OPS flag readback, Outreach calendar linkage, chat message id, and sent Message-ID',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
    'proof_marker' => PROOF_MARKER,
];

$body = implode("\n", [
    'Robert,',
    '',
    "Binny's Grand Downtown on Saturday, July 18 is now marked as a Pioneer Tasting in OPS. I also posted the update in the Outreach Team chat; the linked COTeam shift is still open.",
    '',
    'OPS: ' . $opsUrl,
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
]);

$draftPath = '/Users/admin/.nationaloutreach-launch/state/outbox/'
    . TASK_FLOW_KEY . '-binnys-grand-pioneer-completion.approved.json';
write_json_file($draftPath, [
    'action_id' => TASK_FLOW_KEY . '-binnys-grand-pioneer-completion',
    'source_ref' => SOURCE_REF,
    'source_message_id' => SOURCE_REF,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'reported',
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $verification,
    'next_update' => $packet['next_update'],
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['robert@kovaldistillery.com'],
    'cc' => [],
    'bcc' => [],
    'subject' => 'Re: Open COT shifts for Saturday, July 18',
    'body' => $body,
    'in_reply_to' => SOURCE_MESSAGE_ID,
    'references' => SOURCE_MESSAGE_ID,
    'task_packet' => $packet,
]);

record_task_flow($packet, 'ops_updated_chat_posted');

echo json_encode([
    'ok' => true,
    'event_id' => EVENT_ID,
    'is_pioneer_tasting' => (int) $event['is_pioneer_tasting'],
    'shift_id' => SHIFT_ID,
    'assigned_count' => (int) $event['assigned_count'],
    'calendar_type' => (string) $event['calendar_type'],
    'calendar_link_present' => trim((string) $event['google_event_uid']) !== '',
    'chat_status' => $chatStatus,
    'chat_message_recorded' => $chatMessageName !== '',
    'draft_queued' => is_file($draftPath),
    'proof_marker' => PROOF_MARKER,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
