#!/usr/local/bin/php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const PARK_RIDGE_EVENT_ID = 955;
const PARK_RIDGE_SHIFT_ID = 5396;
const SOFIA_USER_ID = 1350;
const CASSANDRA_USER_ID = 1338;
const TASK_FLOW_KEY = 'taskflow-64c954204007b204';
const SOURCE_REF = 'cak4b=+7blcbst=+90_nhkuva2csww_j2w0mzlft+hv-bd4p8vg@mail.gmail.com';
const SOURCE_MESSAGE_ID = '<CAK4B=+7bLCBSt=+90_nHKUVa2csWw_J2w0mZLFT+hV-bd4p8vg@mail.gmail.com>';
const SESSION_ID = 'd959f9f5';
const STATE_DIR = '/Users/admin/.nationaloutreach-launch/state';

/** @param array<string,mixed> $payload */
function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create the National Outreach outbox.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode the approved reply.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write the approved reply.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install the approved reply.');
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
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    if (proc_close($process) !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

/** @return array<string,mixed> */
function readback(PDO $eventPdo): array
{
    $stmt = $eventPdo->prepare(
        'SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
                l.shift_id, s.group_id,
                GROUP_CONCAT(CONCAT(COALESCE(vu.first_name, ""), " ", COALESCE(vu.last_name, ""), "#", s2u.user_id)
                             ORDER BY s2u.user_id SEPARATOR "|") AS assignees,
                COUNT(s2u.user_id) AS assigned_count,
                gl.google_event_uid, gl.calendar_type
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
           LEFT JOIN ' . TRACKTIME_DB_NAME . '.shifts s ON s.id = l.shift_id
           LEFT JOIN ' . TRACKTIME_DB_NAME . '.shift2user s2u ON s2u.shift_id = s.id
           LEFT JOIN koval_crm.vtiger_users vu ON vu.id = s2u.user_id
           LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
          WHERE eb.id = ?
          GROUP BY eb.id, l.shift_id, s.group_id, gl.google_event_uid, gl.calendar_type'
    );
    $stmt->execute([PARK_RIDGE_EVENT_ID]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($row)) {
        throw new RuntimeException('OPS event 955 is missing.');
    }
    return $row;
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();
$eventPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$trackPdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$before = readback($eventPdo);
if ((string) $before['event_name'] !== 'Park Ridge Market After Dark'
    || (string) $before['event_date'] !== '2026-07-25'
    || (int) $before['shift_id'] !== PARK_RIDGE_SHIFT_ID) {
    throw new RuntimeException('OPS event 955 no longer matches the reviewed Park Ridge event and shift.');
}

$trackPdo->beginTransaction();
try {
    $assignment = $trackPdo->prepare(
        'SELECT user_id FROM ' . TRACKTIME_DB_NAME . '.shift2user
          WHERE shift_id = ? AND user_id IN (?, ?)
          FOR UPDATE'
    );
    $assignment->execute([PARK_RIDGE_SHIFT_ID, SOFIA_USER_ID, CASSANDRA_USER_ID]);
    $assignedIds = array_map('intval', $assignment->fetchAll(PDO::FETCH_COLUMN) ?: []);
    if (!in_array(CASSANDRA_USER_ID, $assignedIds, true)) {
        throw new RuntimeException('Cassandra is no longer assigned to Park Ridge shift 5396; refusing to alter coverage.');
    }
    $delete = $trackPdo->prepare(
        'DELETE FROM ' . TRACKTIME_DB_NAME . '.shift2user WHERE shift_id = ? AND user_id = ?'
    );
    $delete->execute([PARK_RIDGE_SHIFT_ID, SOFIA_USER_ID]);
    $trackPdo->commit();
} catch (Throwable $e) {
    if ($trackPdo->inTransaction()) {
        $trackPdo->rollBack();
    }
    throw $e;
}

$after = readback($eventPdo);
if ((int) $after['assigned_count'] !== 1
    || !str_contains((string) $after['assignees'], 'Cassandra Wilander#' . CASSANDRA_USER_ID)
    || str_contains((string) $after['assignees'], 'Sofia More#' . SOFIA_USER_ID)) {
    throw new RuntimeException('Park Ridge staffing readback did not match the intended one-person coverage state.');
}

$proofMarker = 'OPS_PARK_RIDGE_955_SHIFT_5396_SOFIA_REMOVED_CASSANDRA_REMAINS_20260723';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . PARK_RIDGE_EVENT_ID;
$verification = 'Live OPS readback: Park Ridge Market After Dark event 955 remains scheduled for 2026-07-25 16:00-21:00; '
    . 'Sofia More user 1350 was removed from linked COTeam shift 5396 after her withdrawal; '
    . 'Cassandra Wilander user 1338 remains assigned; assigned_count=1; Outreach Google UID '
    . (string) $after['google_event_uid'] . '; proof marker=' . $proofMarker . '.';

$packet = [
    'source_ref' => SOURCE_REF,
    'dedupe_key' => TASK_FLOW_KEY,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sofia More <sofia.more@koval-distillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => SESSION_ID,
    'ops_portal_or_domain_task' => 'OPS Outreach event 955 / COTeam shift 5396',
    'status' => 'working',
    'due_or_trigger' => '2026-07-25 16:00:00',
    'scheduled_action' => '',
    'calendar_event' => (string) $after['google_event_uid'],
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Park Ridge After Dark; ' . $opsUrl,
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification,
    'papers_projection' => 'not_required_event_staffing_update',
    'next_update' => 'Send Sofia the threaded confirmation, then archive the source after sent-log proof.',
    'requested_deliverable' => 'Remove Sofia from Saturday Park Ridge coverage after her withdrawal while preserving remaining event coverage.',
    'human_owner_or_recipient' => 'Sofia More <sofia.more@koval-distillery.com>; Sonat Birnecker <sonat@kovaldistillery.com>; Robert Birnecker <robert@kovaldistillery.com>',
    'output_channel' => 'OPS + email + Workspaceboard',
    'proof_required' => 'OPS shift2user readback, sent-log Message-ID, source archive proof',
    'due_or_next_update' => 'immediate',
    'escalation_path' => 'None while Cassandra remains assigned; reopen if coverage changes.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$body = implode("\n", [
    'Hi Sofia,',
    '',
    'Thank you for letting me know. I removed you from the Park Ridge Market After Dark shift this Saturday. Cassandra remains assigned, so the event still has coverage.',
    '',
    'I am sorry to hear about the family emergency, and I hope everything is okay.',
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

$outboxPath = STATE_DIR . '/outbox/' . TASK_FLOW_KEY . '-parkridge-sofia-withdrawal.approved.json';
write_json_file($outboxPath, [
    'action_id' => TASK_FLOW_KEY . '-parkridge-sofia-withdrawal',
    'source_ref' => SOURCE_REF,
    'source_message_id' => SOURCE_REF,
    'status' => 'working',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sofia.more@koval-distillery.com'],
    'cc' => ['robert@kovaldistillery.com', 'sonat@kovaldistillery.com'],
    'subject' => 'Re: Park Ridge After Dark',
    'body' => $body,
    'in_reply_to' => SOURCE_MESSAGE_ID,
    'references' => SOURCE_MESSAGE_ID,
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $verification,
    'output_channel' => 'OPS + email + Workspaceboard',
    'task_packet' => $packet,
]);

record_task_flow($packet, 'ops_staffing_updated_reply_queued');

echo json_encode([
    'ok' => true,
    'event' => $after,
    'outbox' => basename($outboxPath),
    'proof_marker' => $proofMarker,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
