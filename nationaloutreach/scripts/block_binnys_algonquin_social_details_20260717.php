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
    if ($json === false || file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write approved email payload.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install approved email payload.');
    }
}

$sourceRef = 'cdd7a19bc9e087da5d3f49674a289447.claude@kovaldistillery.com';
$taskFlowKey = 'taskflow-8fa5820cba93a5ff';
$workspaceboardSession = 'ece81cf9';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=1032';
$outboxPath = '/Users/admin/.nationaloutreach-launch/state/outbox/'
    . $taskFlowKey . '-binnys-algonquin-social-details-question.approved.json';

$verification = 'Live OPS readback on 2026-07-17: Outreach event 1032 is approved for 2026-07-24 17:00-20:00 at Binny\'s Algonquin; Google Outreach UID ops-outreach-1032@koval-distillery.com exists; linked COTeam shift 5560 has zero shift2user assignments. Event notes explicitly say products and assignee are not specified. Exact Task Flow, mailbox/sent logs, HANDOFF, and project-hub searches found no pour list or promotion details.';

$body = implode("\n", [
    'Hi Claude,',
    '',
    'OPS confirms that we are approved to attend the Binny\'s Algonquin tasting on Friday, July 24, from 5:00 PM to 8:00 PM. The event is on the Outreach calendar:',
    $opsUrl,
    '',
    'It is not staffed yet. The linked COTeam shift is still open with no one assigned.',
    '',
    'The remaining blocker for the social copy is the pour list. OPS does not name any products, in-store special, or featured release, and I did not find those details in the existing thread or handoff records.',
    '',
    'Robert, please confirm which KOVAL products we should pour and whether there is any special or featured release Claude should mention. Once that is confirmed, Claude will have the missing copy details; I will keep the staffing follow-up in the Outreach lane.',
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
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'claude@kovaldistillery.com',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $workspaceboardSession,
    'ops_portal_or_domain_task' => 'OPS Outreach event 1032 / COTeam shift 5560',
    'status' => 'clarification_sent',
    'due_or_trigger' => 'Before social copy is finalized for 2026-07-24 tasting',
    'scheduled_action' => 'Keep shift 5560 open and continue staffing follow-up in the Outreach lane.',
    'calendar_event' => $opsUrl,
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Binny\'s Algonquin tasting (Jul 24) - details for social',
    'approval_gates' => 'Robert must supply the missing pour list and any promotion/featured-release detail; attendance is already marked approved in OPS.',
    'verification_readback' => $verification,
    'papers_projection' => 'not_required',
    'next_update' => 'Await Robert\'s product/promotion reply; then provide Claude the final social-copy facts.',
    'requested_deliverable' => 'Confirm attendance, staffing, time, pour list, and any promotion details for social copy.',
    'human_owner_or_recipient' => 'claude@kovaldistillery.com; owner question to robert@kovaldistillery.com',
    'output_channel' => 'email',
    'proof_required' => 'OPS event/shift/calendar readback plus clarification Message-ID',
    'due_or_next_update' => 'On Robert reply, or 2026-07-20 10:00 CDT if no reply',
    'escalation_path' => 'Vanessa follows up with Robert; no product list should be inferred.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'true',
];

write_json_file($outboxPath, [
    'source_ref' => $sourceRef,
    'source_message_id' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'claude@kovaldistillery.com',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'clarification_sent',
    'source_links' => $packet['source_links'],
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $verification,
    'next_update' => $packet['next_update'],
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'owner_question' => true,
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['claude@kovaldistillery.com'],
    'cc' => [
        'robert@kovaldistillery.com',
        'sonat@kovaldistillery.com',
        'avignon.rose@kovaldistillery.com',
        'dmytro.klymentiev@kovaldistillery.com',
        'frank.cannoli@kovaldistillery.com',
    ],
    'subject' => 'Re: Binnys Algonquin tasting (Jul 24) - details for social',
    'body' => $body,
    'in_reply_to' => '<' . $sourceRef . '>',
    'references' => '<' . $sourceRef . '>',
    'task_packet' => $packet,
]);

echo json_encode([
    'ok' => true,
    'draft' => basename($outboxPath),
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
