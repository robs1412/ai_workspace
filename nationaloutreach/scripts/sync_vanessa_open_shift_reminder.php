#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

function arg_value(array $argv, string $name, ?string $default = null): ?string
{
    foreach ($argv as $idx => $arg) {
        if ($arg === $name && isset($argv[$idx + 1])) {
            return (string) $argv[$idx + 1];
        }
        if (str_starts_with($arg, $name . '=')) {
            return substr($arg, strlen($name) + 1);
        }
    }
    return $default;
}

function h(?string $value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function load_jsonl_rows(string $path): array
{
    if (!is_file($path)) {
        return [];
    }
    $rows = [];
    foreach ((file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: []) as $line) {
        $row = json_decode($line, true);
        if (is_array($row)) {
            $rows[] = $row;
        }
    }
    return $rows;
}

function write_jsonl_rows(string $path, array $rows): void
{
    $dir = dirname($path);
    if (!is_dir($dir)) {
        mkdir($dir, 0700, true);
    }
    $tmp = $path . '.tmp';
    $payload = '';
    foreach ($rows as $row) {
        $payload .= json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
    }
    file_put_contents($tmp, $payload);
    chmod($tmp, 0600);
    rename($tmp, $path);
    chmod($path, 0600);
}

function sync_scheduled_actions_db(array $rows, string $mailboxLane = 'nationaloutreach'): void
{
    $recorder = '/Users/werkstatt/ai_workspace/scripts/scheduled_actions_mysql_recorder.php';
    if (!is_file($recorder) || $rows === []) {
        return;
    }
    $payload = json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    if ($payload === false) {
        return;
    }
    $tmp = tempnam(sys_get_temp_dir(), 'sched-actions-');
    if ($tmp === false) {
        return;
    }
    file_put_contents($tmp, $payload);
    $cmd = 'php ' . escapeshellarg($recorder) . ' upsert ' . escapeshellarg($mailboxLane)
        . ' < ' . escapeshellarg($tmp) . ' >/dev/null 2>/dev/null';
    exec($cmd);
    @unlink($tmp);
}

function normalize_ref(string $value): string
{
    return strtolower(trim($value));
}

function time_label(?string $start, ?string $end): string
{
    $fmt = static function (?string $time): string {
        $raw = trim((string) $time);
        if ($raw === '') {
            return '';
        }
        $dt = DateTime::createFromFormat('H:i:s', $raw) ?: DateTime::createFromFormat('H:i', $raw);
        return $dt ? strtolower($dt->format('g:ia')) : $raw;
    };
    $a = $fmt($start);
    $b = $fmt($end);
    if ($a !== '' && $b !== '') {
        return $a . ' - ' . $b;
    }
    return $a !== '' ? $a : $b;
}

function product_prep_note(?string $notes): string
{
    $clean = preg_replace('/\[(?:connecteam|ct)[^\]]*\]/i', ' ', (string) $notes) ?? '';
    $clean = trim(preg_replace('/\s+/', ' ', $clean) ?? '');
    return $clean !== '' ? $clean : 'Check OPS/event notes before claiming the shift.';
}

function coteam_bcc_recipients(): array
{
    $override = trim((string) getenv('NATIONALOUTREACH_COTEAM_BCC_JSON'));
    if ($override !== '') {
        $decoded = json_decode($override, true);
        if (is_array($decoded)) {
            return array_values(array_filter(array_map('strval', $decoded)));
        }
    }
    return [
        'abbiejbrenner@gmail.com',
        'benngoodman@gmail.com',
        'chayarsmolensky@gmail.com',
        'christina.pinciotti@gmail.com',
        'christine.cummins37@gmail.com',
        'clwilander@gmail.com',
        'darla.swango@kovaldistillery.com',
        'dereck.atwater@kovaldistillery.com',
        'dylancollinsgphs@gmail.com',
        'gabriele.thormann99@gmail.com',
        'jth2d@hotmail.com',
        'julie.feyerer@kovaldistillery.com',
        'kmccarthy1991@gmail.com',
        'kyle.combs@kovaldistillery.com',
        'lsargent313@gmail.com',
        'matt.andrews@kovaldistillery.com',
        'mattdevens22@icloud.com',
        'sarahelizabethwelford@gmail.com',
        'sddulman@gmail.com',
        'sebastian.saller@kovaldistillery.com',
        'sonat@kovaldistillery.com',
        'stephen.desena@gmail.com',
    ];
}

$dateRaw = arg_value($argv, '--date', date('Y-m-d'));
$stateDir = rtrim((string) arg_value($argv, '--state-dir', '/Users/admin/.nationaloutreach-launch/state'), '/');
$date = DateTimeImmutable::createFromFormat('Y-m-d', (string) $dateRaw);
if (!$date || $date->format('Y-m-d') !== $dateRaw) {
    fwrite(STDERR, "Invalid --date. Use YYYY-MM-DD.\n");
    exit(2);
}
$targetDate = $date->modify('+2 days');
$stateDir = $stateDir !== '' ? $stateDir : '/Users/admin/.nationaloutreach-launch/state';
if (!is_dir($stateDir)) {
    mkdir($stateDir, 0700, true);
}

$pdo = get_event_pdo();
$stmt = $pdo->prepare(
    "SELECT id, event_name, event_date, start_time, end_time, event_location, notes
       FROM event_bookings
      WHERE event_category = 'Outreach'
        AND event_date = ?
      ORDER BY COALESCE(NULLIF(start_time, ''), '23:59:59') ASC, event_name ASC, id ASC"
);
$stmt->execute([$targetDate->format('Y-m-d')]);
$events = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
$eventIds = array_map(static fn(array $row): int => (int) $row['id'], $events);
$shiftLinksByEvent = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];

$openRows = [];
foreach ($events as $event) {
    $eventId = (int) $event['id'];
    $summary = summarize_event_shift_links($shiftLinksByEvent[$eventId] ?? []);
    $totalShifts = (int) ($summary['total_shifts'] ?? 0);
    $assignedShifts = (int) ($summary['assigned_shifts'] ?? 0);
    if ($totalShifts > 0 && $assignedShifts >= $totalShifts) {
        continue;
    }
    $staffing = $totalShifts <= 0
        ? 'Needs linked shift'
        : ($assignedShifts > 0 ? 'Partially assigned (' . $assignedShifts . '/' . $totalShifts . ')' : 'Open / unassigned (' . $assignedShifts . '/' . $totalShifts . ')');
    $openRows[] = [
        'date' => (string) $event['event_date'],
        'event' => (string) $event['event_name'],
        'time' => time_label($event['start_time'] ?? '', $event['end_time'] ?? ''),
        'ops' => 'OPS #' . $eventId,
        'staffing' => $staffing,
        'product_prep' => product_prep_note($event['notes'] ?? ''),
        'address' => trim((string) ($event['event_location'] ?? '')),
        'link' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
    ];
}

$scheduledPath = $stateDir . '/scheduled-actions.jsonl';
$scheduledRows = load_jsonl_rows($scheduledPath);
$existingRefs = [];
foreach ($scheduledRows as $row) {
    $sourceRef = (string) ($row['source_ref'] ?? $row['id'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[normalize_ref($sourceRef)] = true;
    }
}
foreach (load_jsonl_rows($stateDir . '/sent-log.jsonl') as $row) {
    $taskPacket = is_array($row['task_packet'] ?? null) ? $row['task_packet'] : [];
    $sourceRef = (string) ($taskPacket['source_ref'] ?? $row['source_ref'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[normalize_ref($sourceRef)] = true;
    }
}

$sourceRef = 'vanessa-open-cot-shifts-48h-' . $targetDate->format('Y-m-d') . '-0800';
$queued = 0;
$skipped = 0;
$rowsForDbSync = [];

if ($openRows === []) {
    $skipped = 1;
} elseif (!isset($existingRefs[normalize_ref($sourceRef)])) {
    $targetLabel = $targetDate->format('l, F j');
    $subject = 'Open COT shifts for ' . $targetLabel;
    $tableRows = '';
    foreach ($openRows as $row) {
        $tableRows .= '<tr style="background:#fce4e4;">'
            . '<td>' . h($row['date']) . '</td>'
            . '<td>' . h($row['event']) . '</td>'
            . '<td>' . h($row['time']) . '</td>'
            . '<td>' . h($row['ops']) . '</td>'
            . '<td>' . h($row['staffing']) . '</td>'
            . '<td>' . h($row['product_prep']) . '</td>'
            . '<td>' . h($row['address']) . '</td>'
            . '<td><a href="' . h($row['link']) . '">OPS</a></td>'
            . '</tr>' . "\n";
    }
    $html = '<!doctype html><html><body style="font-family:Arial,sans-serif;">'
        . '<p>Hi team,</p>'
        . '<p>These COT shifts are still open or not fully assigned for ' . h($targetLabel) . '. Please claim coverage in OPS if you can take one.</p>'
        . '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px;">'
        . '<thead><tr style="background:#f2f2f2;"><th>Date</th><th>Event</th><th>Time</th><th>OPS</th><th>Coverage</th><th>Product / sample prep</th><th>Address</th><th>Link</th></tr></thead><tbody>'
        . $tableRows . '</tbody></table>'
        . '<p>Best,<br><br>Vanessa</p>'
        . '<p>Vanessa Sterling<br><br>Outreach Coordinator<br>KOVAL Distillery<br>4241 N Ravenswood Ave<br>Chicago, IL 60613<br>312 878 7988<br>http://www.koval-distillery.com<br><br>X | Instagram | Facebook</p>'
        . '</body></html>';
    $plain = [
        'Hi team,',
        '',
        'These COT shifts are still open or not fully assigned for ' . $targetLabel . '. Please claim coverage in OPS if you can take one.',
        '',
        'Date | Event | Time | OPS | Coverage | Product / sample prep | Address | Link',
    ];
    foreach ($openRows as $row) {
        $plain[] = implode(' | ', [$row['date'], $row['event'], $row['time'], $row['ops'], $row['staffing'], $row['product_prep'], $row['address'], $row['link']]);
    }
    $plain = array_merge($plain, ['', 'Best,', '', 'Vanessa', '', 'Vanessa Sterling', '', 'Outreach Coordinator', 'KOVAL Distillery', '4241 N Ravenswood Ave', 'Chicago, IL 60613', '312 878 7988', 'http://www.koval-distillery.com', '', 'X | Instagram | Facebook']);

    $emailPayload = [
        'from' => 'vanessa.sterling@kovaldistillery.com',
        'from_name' => 'Vanessa Sterling',
        'to' => ['vanessa.sterling@kovaldistillery.com'],
        'cc' => ['robert@kovaldistillery.com'],
        'bcc' => coteam_bcc_recipients(),
        'subject' => $subject,
        'body' => implode("\n", $plain),
        'html_body' => $html,
        'source_ref' => $sourceRef,
        'task_packet' => [
            'source_ref' => $sourceRef,
            'dedupe_key' => 'taskflow-' . $sourceRef,
            'intake_channel' => 'scheduled-action:nationaloutreach',
            'requester' => 'Robert Birnecker',
            'owner_lane' => 'outreach-coordinator',
            'responsible_worker_or_persona' => 'Vanessa Sterling',
            'ops_portal_or_domain_task' => 'OPS 370309',
            'status' => 'reported',
            'due_or_trigger' => $date->format('Y-m-d') . ' 08:00 America/Chicago',
            'scheduled_action' => $sourceRef,
            'requested_deliverable' => '48-hour open/unassigned COT shift reminder for ' . $targetDate->format('Y-m-d') . ', Robert copied.',
            'human_owner_or_recipient' => 'COTeam list 73 BCC; Robert copied',
            'output_channel' => 'email',
            'proof_required' => 'sent Message-ID plus sent-log recipient counts',
            'verification_readback' => 'Generated from live Outreach linked-shift assignment readback for target date ' . $targetDate->format('Y-m-d') . '.',
            'papers_projection' => 'not_required',
            'next_update' => 'Pending 8:00 AM scheduled-action queue for approved send cycle.',
            'proof_marker' => 'COT_OPEN_SHIFT_48H_REMINDER_QUEUED_' . $targetDate->format('Ymd'),
        ],
    ];

    $newRow = [
        'id' => $sourceRef,
        'kind' => 'cot_open_shift_48h_reminder',
        'status' => 'pending',
        'ops_task_id' => 370309,
        'due_at' => $date->format('Y-m-d') . 'T08:00:00-05:00',
        'owner' => 'Robert Birnecker',
        'worker' => 'Vanessa Sterling',
        'dependency' => '48-hour open/unassigned COT shift reminder for ' . $targetDate->format('Y-m-d'),
        'resolution_checks' => [],
        'event_ids' => array_map(static fn(array $row): int => (int) preg_replace('/\D+/', '', $row['ops']), $openRows),
        'email' => $emailPayload,
        'source_ref' => $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'source_links' => 'OPS task 370309 + open Outreach event IDs ' . implode(', ', array_map(static fn(array $row): int => (int) preg_replace('/\D+/', '', $row['ops']), $openRows)),
        'approval_gates' => 'Approved internal COTeam reminder; Robert cc required.',
        'verification_readback' => 'Generated from live Outreach linked-shift assignment readback for target date ' . $targetDate->format('Y-m-d') . '.',
        'papers_projection' => 'not_applicable',
        'next_update' => 'Pending 8:00 AM scheduled-action queue for approved send cycle.',
        'target_event_date' => $targetDate->format('Y-m-d'),
    ];
    $scheduledRows[] = $newRow;
    $rowsForDbSync[] = $newRow;
    $queued = 1;
} else {
    $skipped = 1;
}

write_jsonl_rows($scheduledPath, $scheduledRows);
sync_scheduled_actions_db($rowsForDbSync);

echo json_encode([
    'ok' => true,
    'date' => $date->format('Y-m-d'),
    'target_event_date' => $targetDate->format('Y-m-d'),
    'source_ref' => $sourceRef,
    'open_events_found' => count($openRows),
    'queued' => $queued,
    'skipped' => $skipped,
], JSON_UNESCAPED_SLASHES) . "\n";
