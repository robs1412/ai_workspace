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

$sourceRef = 'fcd23603b69d8e135b93981aa3f42c49.claude@kovaldistillery.com';
$taskFlowKey = 'taskflow-ad9ecce929a64e30';
$sessionId = 'aab65b9e';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=1032';
$outboxPath = '/Users/admin/.nationaloutreach-launch/state/outbox/'
    . $taskFlowKey . '-binnys-algonquin-anchor-review.approved.json';

$verification = 'Live OPS readback on 2026-07-20 confirms Outreach event 1032 for Binny\'s Algonquin on 2026-07-24 from 17:00 to 20:00. The review preserves the generic lineup language because no exact pour list is recorded, while requesting copy edits for retailer styling, compound modifiers, and the overbroad single-barrel claim.';

$body = implode("\n", [
    'MODIFY',
    '',
    'Please make these copy edits before closing:',
    '',
    '- Change “Binnys Beverage Depot” to “Binny\'s Beverage Depot.”',
    '- Hyphenate “grain-to-bottle” and “non-chill-filtered.”',
    '- Revise the second paragraph so “single barrel” does not appear to describe every spirit in the lineup.',
    '',
    'Suggested replacement:',
    '',
    'Everything we make starts with organic Midwestern grain and stays in our hands from mill to bottle. Our whiskies are single-barrel and non-chill-filtered, using only the heart of the run. It is Chicago craft made the honest way.',
    '',
    'The July 24 event date and 5:00-8:00 PM time match OPS. Please keep the lineup generic because OPS still does not list an exact pour list.',
]);

$packet = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'claude@kovaldistillery.com',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $sessionId,
    'ops_portal_or_domain_task' => 'OPS Outreach event 1032',
    'status' => 'reported',
    'due_or_trigger' => 'Review requested 2026-07-20 for the 2026-07-24 tasting',
    'scheduled_action' => '',
    'calendar_event' => $opsUrl,
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Re: Binnys Algonquin tasting (Jul 24) - details for social',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification,
    'papers_projection' => 'not_required',
    'next_update' => 'Claude should revise the copy and return a new review notice.',
    'requested_deliverable' => 'Review the proposed Anchor caption and reply DONE, MODIFY, or INCIDENT.',
    'human_owner_or_recipient' => 'claude@kovaldistillery.com',
    'output_channel' => 'email',
    'proof_required' => 'Live OPS event readback plus same-thread sent-log Message-ID and source archive proof.',
    'due_or_next_update' => 'Complete after MODIFY send and archive readback; reply-dependent thereafter.',
    'escalation_path' => 'No owner question; wait for Claude\'s revised review notice.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

write_json_file($outboxPath, [
    'source_ref' => $sourceRef,
    'source_message_id' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'claude@kovaldistillery.com',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => $packet['source_links'],
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $verification,
    'next_update' => 'MODIFY review reply queued for the approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
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
    'references' => '<cdd7a19bc9e087da5d3f49674a289447.claude@kovaldistillery.com> <178430928916.8408.5568874501313566666@kovaldistillery.com> <' . $sourceRef . '>',
    'task_packet' => $packet,
]);

echo json_encode([
    'ok' => true,
    'draft' => basename($outboxPath),
    'source_ref' => $sourceRef,
    'dedupe_key' => $taskFlowKey,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
