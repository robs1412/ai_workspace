#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

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
    $pdo = get_event_pdo();
    $stmt = $pdo->prepare(
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
        $dt = DateTime::createFromFormat('H:i', $raw) ?: DateTime::createFromFormat('H:i:s', $raw);
        return $dt ? $dt->format('g:i A') : $raw;
    };
    return $fmt($start) . '-' . $fmt($end);
}

$stateDir = '/Users/admin/.nationaloutreach-launch/state';
$outbox = $stateDir . '/outbox';
$runtimeDir = __DIR__ . '/../runtime';
if (!is_dir($outbox) && !mkdir($outbox, 0700, true) && !is_dir($outbox)) {
    throw new RuntimeException('Unable to create outbox.');
}
if (!is_dir($runtimeDir) && !mkdir($runtimeDir, 0700, true) && !is_dir($runtimeDir)) {
    throw new RuntimeException('Unable to create runtime directory.');
}

$sourceRef = 'caatx44bsvgz-p0zptygmigerdce9ydb8ws+fyeg1q8fltnhuza@mail.gmail.com';
$sourceMessageId = '<CAAtX44bSvgz-P0zptyGMigErDCe9ydB8WS+Fyeg1q8fLtNHUzA@mail.gmail.com>';
$dedupeKey = 'taskflow-9e941923f3cd6971';
$actionId = $dedupeKey . '-ravenswood-on-tap-open-shift-notice-20260707';

$events = [];
$stmt = get_event_pdo()->query(
    "SELECT id, event_name, event_date, start_time, end_time, event_location, important_information
       FROM event_bookings
      WHERE id IN (866, 867)
      ORDER BY id"
);
foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) ?: [] as $event) {
    $events[(int) $event['id']] = $event;
}
$links = fetch_event_booking_shift_links([866, 867], false);
$open = [];
$summaries = [];
foreach ([866, 867] as $eventId) {
    $summaries[$eventId] = summarize_event_shift_links($links[$eventId] ?? []);
    foreach (($links[$eventId] ?? []) as $shift) {
        if ((int) ($shift['deleted'] ?? 0) === 1 || (int) ($shift['assigned_count'] ?? 0) > 0) {
            continue;
        }
        $event = $events[$eventId] ?? [];
        $open[] = [
            'event_id' => $eventId,
            'shift_id' => (int) ($shift['shift_id'] ?? 0),
            'date' => (string) ($shift['start_date'] ?: ($event['event_date'] ?? '')),
            'time' => time_label($shift['start_time'] ?? '', $shift['end_time'] ?? ''),
            'event' => (string) ($event['event_name'] ?? 'Ravenswood On Tap'),
            'location' => (string) ($event['event_location'] ?? 'Ravenswood, Chicago'),
            'notes' => (string) ($shift['notes'] ?? ''),
            'ops_link' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
            'shift_link' => 'https://www.koval-distillery.com/ops/index.php?view=shifts&focus=' . (int) ($shift['shift_id'] ?? 0),
        ];
    }
}
if ($open === []) {
    throw new RuntimeException('No unassigned Ravenswood On Tap linked shifts found for OPS events 866/867.');
}

$bcc = coteam_bcc_recipients();
if ($bcc === []) {
    throw new RuntimeException('COTeam phpList list 73 returned no sendable recipients.');
}

$lines = [
    'Hi COTeam,',
    '',
    'We still have an unassigned Ravenswood On Tap shift in OPS. Please claim it in OPS if you can cover it:',
    '',
];
foreach ($open as $row) {
    $lines[] = '- ' . $row['date'] . ', ' . $row['time'] . ': ' . $row['event'] . ' at ' . $row['location'] . ' (Shift #' . $row['shift_id'] . ', OPS #' . $row['event_id'] . ')';
    $lines[] = '  OPS: ' . $row['ops_link'];
    $lines[] = '  Shift: ' . $row['shift_link'];
}
$lines = array_merge($lines, [
    '',
    'Current OPS readback: Saturday, July 18 is covered by Sofia More and Dereck Atwater. Sunday, July 19 has Kevin McCarthy assigned and one additional open COTeam shift remaining.',
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
$body = implode("\n", $lines);

$htmlRows = '';
foreach ($open as $row) {
    $htmlRows .= '<tr>'
        . '<td>' . htmlspecialchars($row['date'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</td>'
        . '<td>' . htmlspecialchars($row['time'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</td>'
        . '<td>' . htmlspecialchars('Shift #' . $row['shift_id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</td>'
        . '<td>' . htmlspecialchars('OPS #' . $row['event_id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</td>'
        . '<td>' . htmlspecialchars($row['location'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</td>'
        . '<td><a href="' . htmlspecialchars($row['ops_link'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '">OPS</a></td>'
        . '</tr>';
}
$html = '<!doctype html><html><body style="font-family:Arial,sans-serif;">'
    . '<p>Hi COTeam,</p>'
    . '<p>We still have an unassigned Ravenswood On Tap shift in OPS. Please claim it in OPS if you can cover it:</p>'
    . '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px;">'
    . '<thead><tr><th>Date</th><th>Time</th><th>Shift</th><th>Event</th><th>Location</th><th>Link</th></tr></thead><tbody>'
    . $htmlRows . '</tbody></table>'
    . '<p>Current OPS readback: Saturday, July 18 is covered by Sofia More and Dereck Atwater. Sunday, July 19 has Kevin McCarthy assigned and one additional open COTeam shift remaining.</p>'
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
    'workspaceboard_session' => '369f3711',
    'ops_portal_or_domain_task' => 'OPS Outreach events 866/867; open shift 5795',
    'status' => 'reported',
    'source_links' => 'Re: Ravenswood on Tap',
    'approval_gates' => 'Robert explicitly requested Vanessa send team notice and post in Google Chat.',
    'verification_readback' => 'Live OPS readback: event 866 covered by Sofia More and Dereck Atwater; event 867 partially covered by Kevin McCarthy with shift 5795 unassigned. phpList COTeam list 73 active with ' . count($bcc) . ' sendable recipients.',
    'next_update' => 'Await COTeam claim for Sunday open shift 5795.',
    'requested_deliverable' => 'Notify the team by email and Google Chat about current unassigned Ravenswood On Tap shifts.',
    'human_owner_or_recipient' => 'COTeam list 73 BCC; Robert copied; Outreach Team Google Chat',
    'output_channel' => 'email and Google Chat',
    'proof_required' => 'sent-log Message-ID plus Google Chat message id and OPS open-shift readback',
    'due_or_next_update' => 'reply-dependent; next check before 2026-07-18 if shift 5795 remains open',
    'escalation_path' => 'If no one claims shift 5795, Vanessa should ask Robert/Sonat for another coverage option.',
    'first_check_sla_seconds' => '120',
    'response_sla_seconds' => '300',
    'result_email_required' => 'true',
    'owner_question_required' => 'false',
];

$draftPath = $outbox . '/' . $actionId . '.approved.json';
write_json_file($draftPath, [
    'source_ref' => $sourceRef,
    'source_message_id' => $sourceRef,
    'intake_channel' => 'email:nationaloutreach',
    'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
    'owner_lane' => 'outreach-coordinator',
    'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
    'status' => 'draft',
    'source_links' => 'Re: Ravenswood on Tap',
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
    'subject' => 'Open Ravenswood On Tap shift for Sunday, July 19',
    'body' => $body,
    'html_body' => $html,
    'in_reply_to' => $sourceMessageId,
    'references' => '<CALbLtzzXUj7sD=xWd37DKqFwuCycV6L8vfozNoKNpP3+bQVm_w@mail.gmail.com> <178347459582.13529.16469836963885836081@kovaldistillery.com> ' . $sourceMessageId,
    'task_packet' => $packet,
]);

$chatLines = [
    'Open Ravenswood On Tap shift:',
    '',
];
foreach ($open as $row) {
    $chatLines[] = '- ' . $row['date'] . ', ' . $row['time'] . ': Shift #' . $row['shift_id'] . ' for OPS #' . $row['event_id'] . ' is still unassigned.';
    $chatLines[] = '  ' . $row['shift_link'];
}
$chatLines[] = '';
$chatLines[] = 'Saturday 7/18 is covered by Sofia More and Dereck Atwater. Sunday 7/19 has Kevin McCarthy assigned plus the open shift above. Please claim it in OPS if you can cover.';
$chatPath = $runtimeDir . '/ravenswood-on-tap-open-shift-chat-20260707.txt';
file_put_contents($chatPath, implode("\n", $chatLines) . "\n");
chmod($chatPath, 0600);

echo json_encode([
    'ok' => true,
    'draft' => $draftPath,
    'chat_message_file' => $chatPath,
    'source_ref' => $sourceRef,
    'dedupe_key' => $dedupeKey,
    'open_shift_ids' => array_map(static fn(array $row): int => (int) $row['shift_id'], $open),
    'coteam_sendable_count' => count($bcc),
    'summaries' => $summaries,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
