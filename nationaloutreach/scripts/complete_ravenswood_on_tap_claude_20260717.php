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

$sourceRef = '0621941258ec062c4e27e8e35a9cd9a0.claude@kovaldistillery.com';
$taskFlowKey = 'taskflow-22d75d9b304bd7a8';
$outboxPath = '/Users/admin/.nationaloutreach-launch/state/outbox/'
    . $taskFlowKey . '-ravenswood-on-tap-confirmation.approved.json';

$verification = 'Live OPS readback on 2026-07-17: events 866/867 remain active for July 18-19; Saturday shifts show Sofia More and Darla Swango for 12:00-22:00, Cassandra Wilander for 12:00-15:00, and Dereck Atwater for 14:00-20:00; Sunday shifts show Kevin McCarthy, Benjamin Green, and Julie Feyerer for 12:00-20:00. Event notes approve Bourbon Lemonade and Cranberry Gin Spritz and record the July 15 09:30 direct delivery. OPS contains no exact booth/station number.';

$body = implode("\n", [
    'Hi Claude,',
    '',
    'We are attending Ravenswood On Tap, and the event is staffed in OPS for both days:',
    '',
    '- Saturday, July 18, 12:00 PM-10:00 PM: Sofia More and Darla Swango are assigned for the full event; Cassandra Wilander is assigned 12:00 PM-3:00 PM and Dereck Atwater 2:00 PM-8:00 PM.',
    '- Sunday, July 19, 12:00 PM-8:00 PM: Kevin McCarthy, Benjamin Green, and Julie Feyerer are assigned for the full event.',
    '',
    'The approved pours are Bourbon Lemonade and Cranberry Gin Spritz, using KOVAL Bourbon and Cranberry Gin. The direct product delivery was confirmed for July 15 at 9:30 AM.',
    '',
    'OPS lists the location as Ravenswood, Chicago, but does not contain an exact booth or station number. Please leave that detail out of the social copy unless Sonat or Avignon has a newer event map.',
    '',
    'You can close Planner #1488 as handed off and confirmed, and the social post can move through Sonat/Avignon brand approval.',
    '',
    'For attendance ownership: Vanessa owns Consumer Outreach coordination and staffing; attendance sign-off still goes to Robert unless he explicitly delegates it.',
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
    'workspaceboard_session' => 'a602eef3',
    'ops_portal_or_domain_task' => 'OPS Outreach events 866/867; Portal Planner 1488 / record 367667',
    'status' => 'reported',
    'due_or_trigger' => '2026-07-17 before event start on 2026-07-18',
    'scheduled_action' => '',
    'calendar_event' => 'OPS Outreach events 866/867',
    'clarification_email' => '',
    'completion_or_blocker_email' => '',
    'source_links' => 'Ravenswood on Tap (Jul 18-19) - attendance + details',
    'approval_gates' => 'routine-if-clear',
    'verification_readback' => $verification,
    'papers_projection' => 'not_required',
    'next_update' => 'Complete; reply-dependent only if Claude needs a booth/station number not present in OPS.',
    'requested_deliverable' => 'Confirm attendance, staffing, pours, times, booth location, and the current attendance approval owner.',
    'human_owner_or_recipient' => 'claude@kovaldistillery.com',
    'output_channel' => 'email',
    'proof_required' => 'Live OPS event/shift readback plus sent-log Message-ID',
    'due_or_next_update' => 'complete',
    'escalation_path' => 'No blocker; exact booth/station number is not recorded in OPS and was identified as an explicit caveat.',
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
    'next_update' => 'Completion reply queued for approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['claude@kovaldistillery.com'],
    'cc' => [
        'sonat@kovaldistillery.com',
        'avignon.rose@kovaldistillery.com',
        'dmytro.klymentiev@kovaldistillery.com',
        'robert@kovaldistillery.com',
    ],
    'subject' => 'Re: Ravenswood on Tap (Jul 18-19) - attendance + details',
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
