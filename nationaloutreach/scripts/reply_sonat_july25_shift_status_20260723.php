#!/usr/local/bin/php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const SOURCE_REF = 'calbltzw0fk3qo_2qbx=uzh-=ao9+=g4sqv9b8pxvxo1urte9jw@mail.gmail.com';
const SOURCE_MESSAGE_ID = '<CALbLtzw0fk3Qo_2qbx=UZh-=aO9+=g4SQV9b8PxvXo1URte9Jw@mail.gmail.com>';
const TASK_FLOW_KEY = 'taskflow-30b182e60714850e';
const SESSION_ID = '603c05bd';
const EVENT_IDS = [1031, 1030, 1037];
const STATE_DIR = '/Users/werkstatt/ai_workspace/.private/mailboxes/nationaloutreach/state';

/** @param array<string,mixed> $payload */
function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create outbox directory.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode approved reply.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write approved reply.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install approved reply.');
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
        throw new RuntimeException('Unable to start Task Flow recorder.');
    }
    fwrite($pipes[0], json_encode(['event' => $event, 'packet' => $packet], JSON_UNESCAPED_SLASHES) ?: '{}');
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    if (proc_close($process) !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

$eventNames = [
    1031 => "Binny's Geneva Tasting",
    1030 => "Binny's Orland Park Tasting",
    1037 => "Binny's Hyde Park Tasting",
];
$links = fetch_event_booking_shift_links(EVENT_IDS, false);
$statuses = [];
foreach (EVENT_IDS as $eventId) {
    $active = array_values(array_filter(
        $links[$eventId] ?? [],
        static fn(array $row): bool => (int) ($row['deleted'] ?? 0) === 0
    ));
    if (count($active) !== 1) {
        throw new RuntimeException('Expected one active linked shift for OPS event ' . $eventId . '.');
    }
    $shift = $active[0];
    $statuses[] = [
        'event_id' => $eventId,
        'event' => $eventNames[$eventId],
        'shift_id' => (int) ($shift['shift_id'] ?? 0),
        'assigned_count' => (int) ($shift['assigned_count'] ?? 0),
    ];
}

$claimed = array_values(array_filter(
    $statuses,
    static fn(array $row): bool => $row['assigned_count'] > 0
));
$statusLines = [];
foreach ($statuses as $row) {
    $statusLines[] = sprintf(
        '- %s (OPS #%d / shift #%d): %s',
        $row['event'],
        $row['event_id'],
        $row['shift_id'],
        $row['assigned_count'] > 0 ? 'claimed' : 'still unassigned'
    );
}
$summary = count($claimed) === 0
    ? 'I just checked OPS. None of the three shifts has been claimed yet.'
    : sprintf(
        'I just checked OPS. %d of the three shifts %s now claimed.',
        count($claimed),
        count($claimed) === 1 ? 'is' : 'are'
    );

$body = implode("\n", [
    'Hi Sonat,',
    '',
    $summary,
    '',
    ...$statusLines,
    '',
    'I will keep monitoring the coverage.',
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

$verification = implode('; ', array_map(
    static fn(array $row): string => sprintf(
        'OPS #%d shift #%d assigned_count=%d',
        $row['event_id'],
        $row['shift_id'],
        $row['assigned_count']
    ),
    $statuses
));
$proofMarker = 'OPS_JULY25_COT_SHIFT_STATUS_' . implode('_', array_map(
    static fn(array $row): string => $row['event_id'] . '_' . $row['shift_id'] . '_' . $row['assigned_count'],
    $statuses
));

$packet = [
    'source_ref' => SOURCE_REF,
    'dedupe_key' => TASK_FLOW_KEY,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => SESSION_ID,
    'ops_portal_or_domain_task' => 'OPS events 1031, 1030, 1037 / shifts 5559, 5558, 5565',
    'status' => 'working',
    'due_or_trigger' => 'Immediate reply requested 2026-07-23',
    'scheduled_action' => '',
    'calendar_event' => '',
    'clarification_email' => '',
    'completion_or_blocker_email' => 'pending_send',
    'source_links' => 'Re: Open COT shifts for Saturday, July 25',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification . '; proof marker=' . $proofMarker,
    'papers_projection' => 'not_required_routine_staffing_status',
    'next_update' => 'Complete after same-thread sent-log Message-ID and source archive proof.',
    'requested_deliverable' => 'Tell Sonat whether the three July 25 COT shifts have been claimed.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email + Task Flow + Workspaceboard',
    'proof_required' => 'Live OPS assignment readback, sent-log Message-ID, source archive proof',
    'due_or_next_update' => 'immediate',
    'escalation_path' => 'No owner question; report current OPS status directly to Sonat.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$outboxPath = STATE_DIR . '/outbox/' . TASK_FLOW_KEY . '-sonat-july25-shift-status.approved.json';
write_json_file($outboxPath, [
    'action_id' => TASK_FLOW_KEY . '-sonat-july25-shift-status',
    'source_ref' => SOURCE_REF,
    'source_message_id' => SOURCE_REF,
    'status' => 'working',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'cc' => [],
    'subject' => 'Re: Open COT shifts for Saturday, July 25',
    'body' => $body,
    'in_reply_to' => SOURCE_MESSAGE_ID,
    'references' => SOURCE_MESSAGE_ID,
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $packet['verification_readback'],
    'output_channel' => $packet['output_channel'],
    'task_packet' => $packet,
]);

record_task_flow($packet, 'live_ops_shift_status_reply_queued');

echo json_encode([
    'ok' => true,
    'outbox' => basename($outboxPath),
    'statuses' => $statuses,
    'proof_marker' => $proofMarker,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
