#!/usr/bin/env php
<?php
declare(strict_types=1);

function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create output directory.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode JSON payload.');
    }
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write draft payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to move draft payload into place.');
    }
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
if (!is_dir($outbox) && !mkdir($outbox, 0700, true) && !is_dir($outbox)) {
    throw new RuntimeException('Unable to create outbox.');
}

$sourceRef = 'calbltzxsfydd5atisizgeuz3d17b7se3wvvam8wfbhaystqwza@mail.gmail.com';
$dedupeKey = 'taskflow-87d79cb5813ff678';
$actionId = $dedupeKey . '-parkridge-after-dark-availability-20260628';

$body = implode("\n", [
    'Hi Cassandra and Sofia,',
    '',
    'Could you let me know whether either of you can cover these upcoming Park Ridge Market After Dark events?',
    '',
    '- Saturday, July 25, 2026, 4:00 PM-9:00 PM',
    '- Saturday, August 22, 2026, 4:00 PM-9:00 PM',
    '',
    'Both shifts are currently open in OPS. If you can do one or both dates, please reply with the date or dates that work for you.',
    '',
    'Best,',
    '',
    'Vanessa',
    '',
    'Vanessa Sterling',
    '',
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
    'dedupe_key' => $dedupeKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '9231cebd',
    'ops_portal_or_domain_task' => 'OPS Outreach events 955/956; shifts 5396/5397',
    'status' => 'reported',
    'calendar_event' => 'ops-outreach-955@koval-distillery.com; ops-outreach-956@koval-distillery.com',
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Re: Park Ridge After Dark',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'Live OPS readback showed Park Ridge Market After Dark events 955 and 956 / shifts 5396 and 5397 still unassigned; availability request queued to Cassandra Wilander and Sofia More with Sonat copied.',
    'papers_projection' => 'not_required',
    'next_update' => 'Await Cassandra or Sofia reply; assign confirmed coverage in OPS when a date is accepted.',
    'requested_deliverable' => 'Ask Cassandra and Sofia whether they can cover both July and August Park Ridge After Dark events.',
    'human_owner_or_recipient' => 'Cassandra Wilander <clwilander@gmail.com>; Sofia More <sofiamore7@gmail.com>; Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS open-shift readback',
    'due_or_next_update' => 'reply-dependent; next check by 2026-06-30 10:00 CDT if no response',
    'escalation_path' => 'If no reply by next check, Vanessa should follow up with Cassandra and Sofia or ask Sonat for another coverage option.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

write_json_file($outbox . '/' . $actionId . '.approved.json', [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => 'Re: Park Ridge After Dark',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $packet['verification_readback'],
    'next_update' => 'Availability request queued for approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['clwilander@gmail.com', 'sofiamore7@gmail.com'],
    'cc' => ['sonat@kovaldistillery.com'],
    'subject' => 'Park Ridge Market After Dark coverage',
    'body' => $body,
    'task_packet' => $packet,
]);

echo json_encode([
    'ok' => true,
    'draft' => $outbox . '/' . $actionId . '.approved.json',
    'source_ref' => $sourceRef,
    'dedupe_key' => $dedupeKey,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
