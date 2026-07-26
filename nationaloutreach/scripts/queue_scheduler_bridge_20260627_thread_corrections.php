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
for ($i = 1; $i < count($argv); $i++) {
    if ($argv[$i] === '--state-dir' && isset($argv[$i + 1])) {
        $stateDir = rtrim((string) $argv[++$i], '/');
    }
}

$outbox = $stateDir . '/outbox';
if (!is_dir($outbox) && !mkdir($outbox, 0700, true) && !is_dir($outbox)) {
    throw new RuntimeException('Unable to create outbox.');
}

$whiskeySource = 'calbltzwwgc-ldrg-cuy8ucsyu9hty=ml1qgjnlgb8xeo1dmecq@mail.gmail.com';
$whiskeyKey = 'taskflow-e3752e8a4f4faf87';
$whiskeyMessageId = '<CALbLtzwWgC-Ldrg-CUy8uCsyu9hty=mL1qGJNLGB8XEo1dMecQ@mail.gmail.com>';
$whiskeyMarker = 'whiskey-washback-dayof-logistics-2026-06-27';
$whiskeyOpsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=903';

$maltSource = 'calbltzyi9pfmqz5eda7pvwzxwnqcqgdukcgtfk96tuoevbf9zq@mail.gmail.com';
$maltKey = 'taskflow-2c390a4c3d8e5100';
$maltMessageId = '<CALbLtzyi9pFMqz5eDa7pVWzxwnQCqgdukCgtFk96TuOevBF9zQ@mail.gmail.com>';
$maltOpsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=865';

$basePacket = [
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => '6ff9ed4d',
    'approval_gates' => 'routine-if-clear',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'due_or_next_update' => 'first check within 2 minutes; result email, owner question, or exact blocker within 5 minutes',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$whiskeyBody = implode("\n", [
    'Hi Sonat,',
    '',
    'I am sending this on the Whiskey Washback thread so the completion note is tied to the right forwarded details.',
    '',
    'I added the Whiskey Washback logistics to OPS event 903, including the load-in/setup notes, supplies, load-out reminder, and the Thresh and Winnow Millet VIP-hour reminder.',
    '',
    'Because the forward arrived after the June 26 event had already ended, I did not send the day-of logistics to the staff after the fact.',
    '',
    'OPS link: ' . $whiskeyOpsUrl,
    '',
    'Best,',
    '',
    'Vanessa',
    '',
    'Vanessa Sterling',
    '',
    'Outreach Coordinator',
    'KOVAL Distillery',
]);

$whiskeyPacket = [
    ...$basePacket,
    'source_ref' => $whiskeySource,
    'dedupe_key' => $whiskeyKey,
    'ops_portal_or_domain_task' => 'OPS Outreach event 903',
    'status' => 'reported',
    'calendar_event' => 'ops-outreach-903@koval-distillery.com',
    'completion_or_blocker_email' => '',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'verification_readback' => 'OPS event 903 updated with marker ' . $whiskeyMarker . '; no worker post-event logistics email sent because source arrived after the event ended.',
    'next_update' => 'Send proof should land in sent-log, then source can be filed.',
    'requested_deliverable' => 'Add Whiskey Washback logistics to event details and notify signed-up workers if still timely.',
    'proof_required' => 'OPS event readback plus sent-log Message-ID',
];

write_json_file($outbox . '/' . $whiskeyKey . '-whiskey-washback-correct-thread.approved.json', [
    'source_ref' => $whiskeySource,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'calendar_event' => 'ops-outreach-903@koval-distillery.com',
    'source_links' => 'Fwd: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'OPS event 903 updated with marker ' . $whiskeyMarker . '.',
    'next_update' => 'Completion email queued for approved send cycle.',
    'requested_deliverable' => 'Add Whiskey Washback logistics to event details.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS event readback',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: PLEASE READ- IMPORTANT INFO FOR WHISKEY WASHBACK CHICAGO',
    'body' => $whiskeyBody,
    'in_reply_to' => $whiskeyMessageId,
    'references' => $whiskeyMessageId,
    'task_packet' => $whiskeyPacket,
]);

$maltBody = implode("\n", [
    'Hi Sonat,',
    '',
    'Correction on my prior note: that Whiskey Washback update belonged on the Whiskey Washback thread.',
    '',
    'For Malt Row on Damen, the June 24 event had already passed before this forward arrived. I checked OPS event 865 and the prior sent proof: the team-facing details for Bon Femmes, 225 attendees, punch-card sampling, setup, product, and ice had already been recorded and sent before the event.',
    '',
    'I did not send a post-event logistics note to Kevin and Dereck after the fact.',
    '',
    'OPS link: ' . $maltOpsUrl,
    '',
    'Best,',
    '',
    'Vanessa',
    '',
    'Vanessa Sterling',
    '',
    'Outreach Coordinator',
    'KOVAL Distillery',
]);

$maltPacket = [
    ...$basePacket,
    'source_ref' => $maltSource,
    'dedupe_key' => $maltKey,
    'ops_portal_or_domain_task' => 'OPS Outreach event 865',
    'status' => 'reported',
    'calendar_event' => 'ops-outreach-865@koval-distillery.com',
    'completion_or_blocker_email' => '',
    'source_links' => 'Fwd: Malt Row on Damen 2026 Updates + Notes',
    'verification_readback' => 'No-action/filed: Malt Row event date 2026-06-24 had passed before the 2026-06-27 forward; OPS event 865 already contained the team details and prior sent-log proof exists.',
    'next_update' => 'Send proof should land in sent-log, then source can be filed.',
    'requested_deliverable' => 'Send any previously unknown Malt Row on Damen details to the workers if still timely.',
    'proof_required' => 'OPS event 865 readback plus prior/current sent-log Message-ID',
];

write_json_file($outbox . '/' . $maltKey . '-malt-row-past-event-closeout.approved.json', [
    'source_ref' => $maltSource,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'calendar_event' => 'ops-outreach-865@koval-distillery.com',
    'source_links' => 'Fwd: Malt Row on Damen 2026 Updates + Notes',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => 'Malt Row event 865 already had team details; event was past when source arrived.',
    'next_update' => 'Closeout email queued for approved send cycle.',
    'requested_deliverable' => 'Close stale Malt Row worker-notification request.',
    'human_owner_or_recipient' => 'Sonat Birnecker <sonat@kovaldistillery.com>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus OPS event readback',
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['sonat@kovaldistillery.com'],
    'subject' => 'Re: Malt Row on Damen 2026 Updates + Notes',
    'body' => $maltBody,
    'in_reply_to' => $maltMessageId,
    'references' => $maltMessageId,
    'task_packet' => $maltPacket,
]);

echo json_encode([
    'ok' => true,
    'queued' => [
        $whiskeyKey . '-whiskey-washback-correct-thread',
        $maltKey . '-malt-row-past-event-closeout',
    ],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
