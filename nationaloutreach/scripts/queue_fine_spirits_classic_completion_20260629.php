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

$sourceRef = 'calbltzzqozfklpx_cqjxq2hnelmatyvkrsy=1rxn5xt+hm55dw@mail.gmail.com';
$dedupeKey = 'taskflow-7b66e7936f22d806';
$actionId = $dedupeKey . '-fine-spirits-classic-completion-20260629';
$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=edit&id=1062';

$body = implode("\n", [
    'Hi Sonat,',
    '',
    'I added the Fine Spirits Classic welcome-packet details to OPS event 1062 and created the reminder tasks for you.',
    '',
    'OPS event:',
    $opsUrl,
    '',
    'Tasks now assigned to you:',
    '- Confirm brand listing, due June 30',
    '- Decide on the Crafted Cocktail Contest and send cocktail details if participating, due July 4 for the July 6 deadline',
    '- Send or ship at least 35 press-kit items, due July 11 for the July 13 deadline',
    '- Provide social media giveaway product, due July 11 for the July 13 deadline',
    '- Send product and flavor list for tasting notes, due July 30 for the August 1 deadline',
    '- Submit required operations forms and permit request, due August 3 for the August 5 deadline',
    '',
    'I also added the sponsor portal, Beth/Rick contact details, drop-off address, and ticket code to the OPS event notes.',
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
    'workspaceboard_session' => '0b18545a',
    'ops_portal_or_domain_task' => 'OPS Market Event 1062; Portal tasks 373509-373514',
    'status' => 'reported',
    'calendar_event' => 'ops-market-1062-1782247171@koval-distillery.com',
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Fwd: Fine Spirits Classic 2026 | Welcome!',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 1062 readback showed Fine Spirits Classic on 2026-08-20 18:00-21:00 at Orchestra Hall with six linked Sonat-owned Portal tasks 373509-373514.',
    'papers_projection' => 'not_required',
    'next_update' => 'Complete unless Sonat replies with a change or confirms contest/product decisions.',
    'requested_deliverable' => 'Add Fine Spirits Classic welcome packet details to the event and create Sonat reminder tasks two days before each deadline.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'OPS event/task readback plus sent-log Message-ID',
    'due_or_next_update' => 'complete',
    'escalation_path' => 'No blocker; reply-dependent only.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$draftPath = $outbox . '/' . $actionId . '.approved.json';
write_json_file($draftPath, [
    'source_ref' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => 'Fwd: Fine Spirits Classic 2026 | Welcome!',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $packet['verification_readback'],
    'next_update' => 'Completion reply queued for approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: Fine Spirits Classic 2026 | Welcome!',
    'body' => $body,
    'in_reply_to' => '<CALbLtzzqozfKLpx_CQJXQ2HneLmaTyVKrsy=1RXn5xT+Hm55Dw@mail.gmail.com>',
    'references' => '<BN8PR20MB2260CC22744E14CB836094DEB5E82@BN8PR20MB2260.namprd20.prod.outlook.com> <CALbLtzzqozfKLpx_CQJXQ2HneLmaTyVKrsy=1RXn5xT+Hm55Dw@mail.gmail.com>',
    'task_packet' => $packet,
]);

echo json_encode([
    'ok' => true,
    'draft' => $draftPath,
    'source_ref' => $sourceRef,
    'dedupe_key' => $dedupeKey,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
