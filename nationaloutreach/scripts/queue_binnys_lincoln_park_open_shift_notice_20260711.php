#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';
require_once '/Users/werkstatt/ops/outreach_team_chat_notifier.php';

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

function coteam_bcc_recipients(): array
{
    $stmt = get_event_pdo()->prepare(
        "SELECT LOWER(TRIM(u.email)) AS email
           FROM koval_plst1.phplist_user_user u
           JOIN koval_plst1.phplist_listuser lu ON lu.userid = u.id
           JOIN koval_plst1.phplist_list l ON l.id = lu.listid
          WHERE lu.listid = 73
            AND l.active = 1
            AND u.confirmed = 1
            AND COALESCE(u.blacklisted, 0) = 0
            AND COALESCE(u.disabled, 0) = 0
            AND TRIM(u.email) <> ''
          ORDER BY LOWER(TRIM(u.email))"
    );
    $stmt->execute();
    $emails = [];
    foreach ($stmt->fetchAll(PDO::FETCH_COLUMN) ?: [] as $email) {
        $email = trim((string) $email);
        if ($email !== '' && filter_var($email, FILTER_VALIDATE_EMAIL) && !in_array($email, $emails, true)) {
            $emails[] = $email;
        }
    }
    return $emails;
}

function time_label(?string $start, ?string $end): string
{
    $fmt = static function (?string $time): string {
        $raw = trim((string) $time);
        if ($raw === '') {
            return '';
        }
        $dt = DateTime::createFromFormat('H:i:s', $raw) ?: DateTime::createFromFormat('H:i', $raw);
        return $dt ? $dt->format('g:i A') : $raw;
    };
    return $fmt($start) . '-' . $fmt($end);
}

$eventId = 1064;
$shiftId = 5667;
$sourceRef = 'caatx44boqdjouv6ullvnfyp33qvkikjrdts=k=mozsobaqnlpw@mail.gmail.com';
$sourceMessageId = '<CAAtX44boQdJoUv6ULLVnFyp33qvkiKjRdts=K=moZSObAqnLpw@mail.gmail.com>';
$dedupeKey = 'taskflow-153aa5262d295656';
$workspaceboardSession = 'bff97684';
$actionId = $dedupeKey . '-binnys-lincoln-park-open-shift-reminder-20260711';

$stmt = get_event_pdo()->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_location,
            l.shift_id, s.group_id, s.notes, COUNT(s2u.user_id) AS assigned_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ? AND l.shift_id = ?
      GROUP BY eb.id, l.shift_id, s.group_id, s.notes, gl.google_event_uid, gl.calendar_type
      LIMIT 1"
);
$stmt->execute([$eventId, $shiftId]);
$event = $stmt->fetch(PDO::FETCH_ASSOC);
if (!is_array($event)) {
    throw new RuntimeException('OPS event/shift readback failed.');
}
if ((int) ($event['assigned_count'] ?? 0) !== 0) {
    throw new RuntimeException('Shift is no longer open; no reminder queued.');
}

$bcc = coteam_bcc_recipients();
if ($bcc === []) {
    throw new RuntimeException('COTeam phpList list 73 returned no sendable recipients.');
}

$opsUrl = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;
$shiftUrl = 'https://www.koval-distillery.com/ops/index.php?view=shifts&focus=' . $shiftId;
$date = (string) $event['event_date'];
$time = time_label((string) $event['start_time'], (string) $event['end_time']);
$location = (string) $event['event_location'];

$lines = [
    'Hi COTeam,',
    '',
    'We still need coverage for this important Binny\'s event. Please claim the open shift in OPS if you can cover it:',
    '',
    '- Thursday, July 16, ' . $time . ': ' . (string) $event['event_name'] . ' at ' . $location . ' (Shift #' . $shiftId . ', OPS #' . $eventId . ')',
    '  OPS: ' . $opsUrl,
    '  Shift: ' . $shiftUrl,
    '',
    'This is the Binny\'s Lincoln Park Local Distilleries event. Robert asked that we remind the team because the shift is important.',
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
];
$body = implode("\n", $lines);
$html = '<!doctype html><html><body style="font-family:Arial,sans-serif;">'
    . '<p>Hi COTeam,</p>'
    . '<p>We still need coverage for this important Binny\'s event. Please claim the open shift in OPS if you can cover it:</p>'
    . '<p><strong>Thursday, July 16, ' . htmlspecialchars($time, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</strong><br>'
    . htmlspecialchars((string) $event['event_name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '<br>'
    . htmlspecialchars($location, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '<br>'
    . 'Shift #' . $shiftId . ', OPS #' . $eventId . '<br>'
    . '<a href="' . htmlspecialchars($opsUrl, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '">OPS event</a> | '
    . '<a href="' . htmlspecialchars($shiftUrl, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '">Shift</a></p>'
    . '<p>This is the Binny\'s Lincoln Park Local Distilleries event. Robert asked that we remind the team because the shift is important.</p>'
    . '<p>Best,<br><br>Vanessa</p>'
    . '<p>Vanessa Sterling<br><br>Outreach Coordinator<br>KOVAL Distillery<br>4241 N Ravenswood Ave<br>Chicago, IL 60613<br>312 878 7988<br>http://www.koval-distillery.com<br><br>X | Instagram | Facebook</p>'
    . '</body></html>';

$packet = [
    'source_ref' => $sourceRef,
    'dedupe_key' => $dedupeKey,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'workspaceboard_session' => $workspaceboardSession,
    'ops_portal_or_domain_task' => 'OPS Outreach event ' . $eventId . '; open shift ' . $shiftId,
    'status' => 'reported',
    'source_links' => 'Event July 16',
    'approval_gates' => 'Robert explicitly requested Vanessa remind COTeam and post in chat.',
    'verification_readback' => 'Live OPS readback: event ' . $eventId . ' / shift ' . $shiftId . ' is open with assigned_count=0; Outreach Google UID ' . (string) ($event['google_event_uid'] ?? '') . '; phpList COTeam list 73 active with ' . count($bcc) . ' sendable recipients.',
    'next_update' => 'Await COTeam claim for open shift ' . $shiftId . '.',
    'requested_deliverable' => 'Remind COTeam about the July 16 Binny\'s open shift and post in chat.',
    'human_owner_or_recipient' => 'COTeam list 73 BCC; Robert copied; Outreach Team Google Chat',
    'output_channel' => 'email and Google Chat',
    'proof_required' => 'sent-log Message-ID plus Google Chat message id and OPS open-shift readback',
    'due_or_next_update' => 'reply-dependent; next check before 2026-07-16 if shift remains open',
    'escalation_path' => 'If no one claims shift ' . $shiftId . ', Vanessa should ask Robert/Sonat for another coverage option.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
$draftPath = $outbox . '/' . $actionId . '.approved.json';
write_json_file($draftPath, [
    'source_ref' => $sourceRef,
    'source_message_id' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => 'Event July 16',
    'approval_gates' => $packet['approval_gates'],
    'verification_readback' => $packet['verification_readback'],
    'next_update' => 'Team notice queued for approved send cycle.',
    'requested_deliverable' => $packet['requested_deliverable'],
    'human_owner_or_recipient' => $packet['human_owner_or_recipient'],
    'output_channel' => 'email',
    'proof_required' => $packet['proof_required'],
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['vanessa.sterling@kovaldistillery.com'],
    'cc' => ['robert@kovaldistillery.com'],
    'bcc' => $bcc,
    'subject' => 'Open COTeam shift: Binny\'s Lincoln Park Local Distilleries - July 16',
    'body' => $body,
    'html_body' => $html,
    'in_reply_to' => $sourceMessageId,
    'references' => $sourceMessageId,
    'task_packet' => $packet,
]);

$chatMessage = implode("\n", [
    'Open Binny\'s Lincoln Park shift:',
    '',
    '- Thursday, July 16, ' . $time . ': Shift #' . $shiftId . ' for OPS #' . $eventId . ' is still unassigned.',
    '  ' . $shiftUrl,
    '',
    'This is the Binny\'s Lincoln Park Local Distilleries event. Robert asked for a reminder because this shift is important. Please claim it in OPS if you can cover.',
]);
$chatPath = __DIR__ . '/../runtime/binnys-lincoln-park-open-shift-chat-20260711.txt';
file_put_contents($chatPath, $chatMessage . "\n");
chmod($chatPath, 0600);

$chatResult = notify_outreach_team_chat_available_shift([
    'event_id' => $eventId,
    'shift_id' => $shiftId,
    'reminder_key' => $dedupeKey . '|manual-robert-reminder',
    'event_name' => (string) $event['event_name'],
    'shift_start_local' => $date . ' ' . substr((string) $event['start_time'], 0, 5),
    'shift_end_time' => substr((string) $event['end_time'], 0, 5),
    'location' => $location,
], true);

echo json_encode([
    'ok' => true,
    'draft' => $draftPath,
    'chat_message_file' => $chatPath,
    'chat_result' => $chatResult,
    'event_id' => $eventId,
    'shift_id' => $shiftId,
    'assigned_count' => (int) $event['assigned_count'],
    'google_event_uid' => (string) ($event['google_event_uid'] ?? ''),
    'coteam_sendable_count' => count($bcc),
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
