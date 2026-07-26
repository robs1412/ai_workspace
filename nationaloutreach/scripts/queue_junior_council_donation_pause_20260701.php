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

$sourceRef = 'cagh0mbgewmkvgjcgusokuy17lnvxvkqht0nmrak4z7rvu2nm0w@mail.gmail.com';
$sourceMessageId = '<CAGh0MbgeWMkVGJcGusokUY17LNVXVKQHt0nMRAk4Z7RVu2nM0w@mail.gmail.com>';
$dedupeKey = 'taskflow-63d3e6e51781aa1f';
$actionId = $dedupeKey . '-junior-council-donation-pause-20260701';

$body = implode("\n", [
    'Hi Erin,',
    '',
    'Thank you for reaching out and for thinking of KOVAL again for Junior Council\'s upcoming events.',
    '',
    'We are currently taking a short break from accepting new donation inquiries while we catch up on the existing backlog, so we are not able to take on a new raffle or silent-auction donation request right now.',
    '',
    'You are welcome to check back on our donation request page later for the current status:',
    'https://www.koval-distillery.com/donation-request/',
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
    'intake_channel' => 'approved-send:nationaloutreach',
    'requester' => 'silentauction@juniorcouncil.org',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => 'ca07b046',
    'ops_portal_or_domain_task' => '',
    'status' => 'reported',
    'due_or_trigger' => '',
    'scheduled_action' => '',
    'calendar_event' => '',
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Junior Council Introduction / Upcoming Donation Opportunities',
    'approval_gates' => 'owner decision: donations paused; send holding/decline reply with public donation-request link',
    'verification_readback' => 'Owner decision received; same-thread donation pause reply queued for approved send cycle.',
    'papers_projection' => 'not_required',
    'next_update' => 'Complete after sent-log Message-ID and archive proof.',
    'requested_deliverable' => 'Reply to Junior Council donation request with current donation-pause status and public page link.',
    'human_owner_or_recipient' => 'Erin Bylina <silentauction@juniorcouncil.org>',
    'output_channel' => 'email',
    'proof_required' => 'sent-log Message-ID plus archive/readback proof',
    'due_or_next_update' => 'complete after send/archive',
    'escalation_path' => 'No blocker unless SMTP or archive fails.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$draftPath = $outbox . '/' . $actionId . '.approved.json';
write_json_file($draftPath, [
    'source_ref' => $sourceRef,
    'intake_channel' => 'approved-send:nationaloutreach',
    'requester' => 'silentauction@juniorcouncil.org',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => 'Junior Council Introduction / Upcoming Donation Opportunities',
    'approval_gates' => 'owner-approved donation pause reply',
    'verification_readback' => $packet['verification_readback'],
    'next_update' => 'Donation pause reply queued for approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['silentauction@juniorcouncil.org'],
    'subject' => 'Re: Junior Council Introduction / Upcoming Donation Opportunities',
    'body' => $body,
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'task_packet' => $packet,
]);

echo json_encode([
    'ok' => true,
    'draft' => $draftPath,
    'source_ref' => $sourceRef,
    'dedupe_key' => $dedupeKey,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
