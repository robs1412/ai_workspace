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

function load_jsonl_rows(string $path): array
{
    if (!is_file($path)) {
        return [];
    }
    $rows = [];
    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [];
    foreach ($lines as $line) {
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
    exec($cmd, $_out, $exitCode);
    @unlink($tmp);
}

function normalize_ref(string $value): string
{
    return strtolower(trim($value));
}

function format_short_time(?string $value): string
{
    $raw = trim((string) $value);
    if ($raw === '') {
        return '';
    }
    $dt = DateTime::createFromFormat('H:i:s', $raw) ?: DateTime::createFromFormat('H:i', $raw);
    return $dt ? strtolower($dt->format('g:ia')) : $raw;
}

function event_time_label(array $event): string
{
    $start = format_short_time((string) ($event['start_time'] ?? ''));
    $end = format_short_time((string) ($event['end_time'] ?? ''));
    if ($start !== '' && $end !== '') {
        return $start . ' - ' . $end;
    }
    return $start !== '' ? $start : $end;
}

function build_body(string $dateLabel, array $events): string
{
    $lines = [
        'Hi Vanessa,',
        '',
        'This is your 9:30 PM post-tasting check-in reminder for today, ' . $dateLabel . '.',
        '',
        "Today's staffed Outreach tastings:",
        '',
    ];

    foreach ($events as $event) {
        $staff = implode(', ', (array) ($event['assigned_names'] ?? []));
        $parts = array_filter([
            event_time_label($event),
            (string) ($event['event_name'] ?? 'Outreach Event'),
            $staff !== '' ? 'Staff: ' . $staff : '',
        ]);
        $lines[] = '- ' . implode(' | ', $parts);
        $location = trim((string) ($event['event_location'] ?? ''));
        if ($location !== '') {
            $lines[] = '  Location: ' . $location;
        }
        $lines[] = '  OPS event link: https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . (int) ($event['id'] ?? 0);
    }

    $lines = array_merge($lines, [
        '',
        'Action tonight:',
        '- verify whether the last tasting of the day needs any immediate owner-visible follow-up',
        '- if a staff issue, schedule problem, or customer follow-up surfaced, reply on the relevant thread or record the exact blocker',
        '- if nothing needs action, treat this reminder as complete with no further reply required',
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

    return implode("\n", $lines);
}

$dateRaw = arg_value($argv, '--date', date('Y-m-d'));
$stateDir = rtrim((string) arg_value($argv, '--state-dir', '/Users/admin/.nationaloutreach-launch/state'), '/');
$date = DateTimeImmutable::createFromFormat('Y-m-d', (string) $dateRaw);
if (!$date || $date->format('Y-m-d') !== $dateRaw) {
    fwrite(STDERR, "Invalid --date. Use YYYY-MM-DD.\n");
    exit(2);
}

if ($stateDir === '') {
    $stateDir = '/Users/admin/.nationaloutreach-launch/state';
}
if (!is_dir($stateDir)) {
    mkdir($stateDir, 0700, true);
}

$pdo = get_event_pdo();
$eventStmt = $pdo->prepare(
    "SELECT eb.id,
            eb.event_name,
            eb.event_date,
            eb.start_time,
            eb.end_time,
            eb.event_location
       FROM event_bookings eb
      WHERE eb.event_category = 'Outreach'
        AND eb.event_date = ?
      ORDER BY COALESCE(NULLIF(eb.end_time, ''), '23:59:59') ASC, eb.id ASC"
);
$eventStmt->execute([$date->format('Y-m-d')]);
$eventRows = $eventStmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

$eventIds = array_values(array_filter(array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $eventRows)));
$linkedShifts = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];

$staffedEvents = [];
$shiftIds = [];
foreach ($eventRows as $row) {
    $eventId = (int) ($row['id'] ?? 0);
    if ($eventId <= 0) {
        continue;
    }
    $assignedNames = [];
    foreach (($linkedShifts[$eventId] ?? []) as $link) {
        if ((int) ($link['deleted'] ?? 0) === 1) {
            continue;
        }
        $assigned = array_values(array_filter((array) ($link['assigned_names'] ?? []), static fn($name): bool => trim((string) $name) !== ''));
        if (empty($assigned)) {
            continue;
        }
        $assignedNames = array_values(array_unique(array_merge($assignedNames, $assigned)));
        $shiftId = (int) ($link['shift_id'] ?? 0);
        if ($shiftId > 0) {
            $shiftIds[$shiftId] = $shiftId;
        }
    }
    if (empty($assignedNames)) {
        continue;
    }
    $row['assigned_names'] = $assignedNames;
    $staffedEvents[] = $row;
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

$sentRows = load_jsonl_rows($stateDir . '/sent-log.jsonl');
foreach ($sentRows as $row) {
    $taskPacket = is_array($row['task_packet'] ?? null) ? $row['task_packet'] : [];
    $sourceRef = (string) ($taskPacket['source_ref'] ?? $row['source_ref'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[normalize_ref($sourceRef)] = true;
    }
}

$sourceRef = 'vanessa-post-tasting-checkin-' . $date->format('Y-m-d') . '-2130';
$queued = 0;
$skipped = 0;
$rowsForDbSync = [];

if (empty($staffedEvents)) {
    $skipped = 1;
} elseif (!isset($existingRefs[normalize_ref($sourceRef)])) {
    $dateLabel = $date->format('l, F j');
    $lastEvent = $staffedEvents[count($staffedEvents) - 1];
    $lastEnd = format_short_time((string) ($lastEvent['end_time'] ?? ''));
    $eventIdList = array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $staffedEvents);
    $body = build_body($dateLabel, $staffedEvents);

    $newRow = [
        'id' => $sourceRef,
        'kind' => 'outreach_post_tasting_checkin',
        'status' => 'pending',
        'ops_task_id' => 368770,
        'due_at' => $date->format('Y-m-d') . 'T21:30:00-05:00',
        'owner' => 'Robert Birnecker',
        'worker' => 'Vanessa Sterling',
        'dependency' => '9:30 PM post-tasting check-in for staffed Outreach tastings on ' . $date->format('Y-m-d'),
        'resolution_checks' => [],
        'event_ids' => $eventIdList,
        'shift_ids' => array_values($shiftIds),
        'email' => [
            'from' => 'vanessa.sterling@kovaldistillery.com',
            'from_name' => 'Vanessa Sterling',
            'to' => ['vanessa.sterling@kovaldistillery.com'],
            'cc' => ['robert@kovaldistillery.com'],
            'subject' => '9:30 PM post-tasting check-in for ' . $dateLabel,
            'body' => $body,
        ],
        'source_ref' => $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'source_links' => 'OPS task 368770 + Outreach event IDs ' . implode(', ', $eventIdList),
        'approval_gates' => 'Internal scheduled reminder only; no external send beyond Vanessa/Robert.',
        'verification_readback' => 'Generated from live staffed Outreach event data for same-day post-tasting check-in.',
        'papers_projection' => 'not_applicable',
        'next_update' => 'Pending 9:30 PM scheduled-action queue for the approved send cycle.',
        'last_tasting_end' => $lastEnd,
    ];
    $scheduledRows[] = $newRow;
    $rowsForDbSync[] = $newRow;
    $existingRefs[normalize_ref($sourceRef)] = true;
    $queued = 1;
} else {
    $skipped = 1;
}

write_jsonl_rows($scheduledPath, $scheduledRows);
sync_scheduled_actions_db($rowsForDbSync);

echo json_encode([
    'ok' => true,
    'date' => $date->format('Y-m-d'),
    'source_ref' => $sourceRef,
    'staffed_events_found' => count($staffedEvents),
    'event_ids' => array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $staffedEvents),
    'shift_ids' => array_values($shiftIds),
    'queued' => $queued,
    'skipped' => $skipped,
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
