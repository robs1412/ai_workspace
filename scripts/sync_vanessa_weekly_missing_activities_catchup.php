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

function parse_id_list(?string $value): array
{
    $parts = preg_split('/\s*,\s*/', trim((string) $value), -1, PREG_SPLIT_NO_EMPTY) ?: [];
    return array_values(array_unique(array_filter(array_map('intval', $parts), static fn(int $id): bool => $id > 0)));
}

function normalize_label(string $value): string
{
    $value = strtolower(trim($value));
    $value = str_replace(["\u{2019}", "'"], '', $value);
    $value = preg_replace('/\([^)]*\)/', ' ', $value) ?? $value;
    $value = preg_replace('/[^a-z0-9]+/', ' ', $value) ?? $value;
    return trim(preg_replace('/\s+/', ' ', $value) ?? $value);
}

function label_tokens(string $value): array
{
    $normalized = normalize_label($value);
    if ($normalized === '') {
        return [];
    }
    return preg_split('/\s+/', $normalized, -1, PREG_SPLIT_NO_EMPTY) ?: [];
}

function event_name_search_variants(string $eventName): array
{
    $variants = [$eventName];
    $withoutParens = trim(preg_replace('/\([^)]*\)/', ' ', $eventName) ?? $eventName);
    if ($withoutParens !== '' && $withoutParens !== $eventName) {
        $variants[] = preg_replace('/\s+/', ' ', $withoutParens) ?? $withoutParens;
    }
    if (stripos($eventName, 'Square Chicago') !== false) {
        $variants[] = str_ireplace('Square Chicago', 'Chicago Square', $eventName);
        if ($withoutParens !== '') {
            $variants[] = str_ireplace('Square Chicago', 'Chicago Square', $withoutParens);
        }
    }
    return array_values(array_unique(array_filter(array_map('trim', $variants), static fn(string $value): bool => $value !== '')));
}

function account_match_score(string $eventName, string $accountLabel): int
{
    $eventTokens = label_tokens($eventName);
    $accountTokens = label_tokens($accountLabel);
    if ($eventTokens === [] || $accountTokens === []) {
        return -1;
    }
    if (implode(' ', $eventTokens) === implode(' ', $accountTokens)) {
        return 1000;
    }

    $shared = array_values(array_intersect($eventTokens, $accountTokens));
    if (count($shared) < 2) {
        return -1;
    }

    $locationPart = str_contains($eventName, '-') ? trim(substr($eventName, strpos($eventName, '-') + 1)) : $eventName;
    $locationTokens = array_values(array_filter(
        label_tokens($locationPart),
        static fn(string $token): bool => !in_array($token, ['whole', 'foods', 'mariano', 'marianos', 'garfield', 'garfields', 'beverage', 'warehouse'], true)
    ));
    $locationMatched = false;
    foreach ($locationTokens as $token) {
        if (in_array($token, $accountTokens, true)) {
            $locationMatched = true;
            break;
        }
    }
    if (!$locationMatched) {
        return -1;
    }

    $extraTokenCount = count(array_diff($accountTokens, $eventTokens));
    return (count($shared) * 10) - $extraTokenCount;
}

function resolve_portal_account_links(array $event, array $accountMetadata): array
{
    $links = [];
    foreach (parse_id_list((string) ($event['account_ids'] ?? '')) as $accountId) {
        if (isset($accountMetadata[$accountId])) {
            $links[] = $accountMetadata[$accountId];
        }
    }
    if ($links !== []) {
        return $links;
    }

    $eventName = trim((string) ($event['event_name'] ?? ''));
    if ($eventName === '' || !function_exists('suggest_crm_accounts_for_event_name')) {
        return [];
    }

    $bestCandidate = null;
    $bestScore = -1;
    foreach (event_name_search_variants($eventName) as $variant) {
        foreach (suggest_crm_accounts_for_event_name($variant, 5) as $candidate) {
            $score = account_match_score($variant, (string) ($candidate['label'] ?? ''));
            if ($score > $bestScore) {
                $bestScore = $score;
                $bestCandidate = $candidate;
            }
        }
    }

    return $bestCandidate !== null ? [$bestCandidate] : [];
}

function build_body(string $startLabel, string $endLabel, array $events): string
{
    $lines = [
        'Hi Vanessa,',
        '',
        'This is your Monday catch-up reminder for potentially missing Outreach activities from ' . $startLabel . ' through ' . $endLabel . '.',
        '',
        'Please review the staffed tastings from that week, confirm activities exist in Portal on the right accounts, and follow up on anything that was missed.',
        '',
        'Week window to audit:',
        '',
    ];

    foreach ($events as $event) {
        $staff = implode(', ', (array) ($event['assigned_names'] ?? []));
        $parts = array_filter([
            (string) ($event['event_date'] ?? ''),
            event_time_label($event),
            (string) ($event['event_name'] ?? 'Outreach Event'),
            $staff !== '' ? 'Staff: ' . $staff : '',
        ]);
        $lines[] = '- ' . implode(' | ', $parts);
        $location = trim((string) ($event['event_location'] ?? ''));
        if ($location !== '') {
            $lines[] = '  Location: ' . $location;
        }
        $accountLinks = array_values(array_filter(
            (array) ($event['portal_account_links'] ?? []),
            static fn($account): bool => is_array($account) && trim((string) ($account['url'] ?? '')) !== ''
        ));
        if (count($accountLinks) === 1) {
            $account = $accountLinks[0];
            $label = trim((string) ($account['label'] ?? 'Portal account'));
            $lines[] = '  Portal account link: ' . $label . ' - ' . (string) $account['url'];
        } elseif ($accountLinks !== []) {
            $lines[] = '  Portal account links:';
            foreach ($accountLinks as $account) {
                $label = trim((string) ($account['label'] ?? 'Portal account'));
                $lines[] = '    - ' . $label . ': ' . (string) $account['url'];
            }
        }
        $lines[] = '  OPS event link: https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . (int) ($event['id'] ?? 0);
    }

    $lines = array_merge($lines, [
        '',
        'Required result:',
        '- confirm activity coverage for the full week window',
        '- if an activity is missing, send the reminder/follow-up or record one exact blocker',
        '- reply with internal Portal readback proof or a no-action reason; do not ask staff to send Portal IDs or links',
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

$stateDir = $stateDir !== '' ? $stateDir : '/Users/admin/.nationaloutreach-launch/state';
if (!is_dir($stateDir)) {
    mkdir($stateDir, 0700, true);
}

$queued = 0;
$skipped = 0;
$windowStart = $date->modify('-14 days');
$windowEnd = $date->modify('-8 days');
$sourceRef = 'vanessa-monday-missing-activities-' . $date->format('Y-m-d') . '-1000';
$rowsForDbSync = [];

if ((int) $date->format('N') !== 1) {
    echo json_encode([
        'ok' => true,
        'date' => $date->format('Y-m-d'),
        'source_ref' => $sourceRef,
        'queued' => 0,
        'skipped' => 1,
        'reason' => 'not_monday',
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
    exit(0);
}

$pdo = get_event_pdo();
$eventStmt = $pdo->prepare(
    "SELECT eb.id,
            eb.event_name,
            eb.event_date,
            eb.start_time,
            eb.end_time,
            eb.event_location,
            GROUP_CONCAT(DISTINCT eba.account_id ORDER BY eba.account_id) AS account_ids
       FROM event_bookings eb
       LEFT JOIN event_booking_accounts eba ON eba.event_booking_id = eb.id
      WHERE eb.event_category = 'Outreach'
        AND eb.event_date BETWEEN ? AND ?
      GROUP BY eb.id
      ORDER BY eb.event_date ASC, COALESCE(NULLIF(eb.end_time, ''), '23:59:59') ASC, eb.id ASC"
);
$eventStmt->execute([$windowStart->format('Y-m-d'), $windowEnd->format('Y-m-d')]);
$eventRows = $eventStmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

$allAccountIds = [];
foreach ($eventRows as $row) {
    $allAccountIds = array_merge($allAccountIds, parse_id_list((string) ($row['account_ids'] ?? '')));
}
$accountMetadata = $allAccountIds !== [] ? fetch_crm_accounts_by_ids($allAccountIds) : [];

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
    $row['portal_account_links'] = resolve_portal_account_links($row, $accountMetadata);
    $staffedEvents[] = $row;
}

$scheduledPath = $stateDir . '/scheduled-actions.jsonl';
$scheduledRows = load_jsonl_rows($scheduledPath);
$existingRefs = [];
foreach ($scheduledRows as $row) {
    $sourceRefKey = (string) ($row['source_ref'] ?? $row['id'] ?? '');
    if ($sourceRefKey !== '') {
        $existingRefs[normalize_ref($sourceRefKey)] = true;
    }
}

$sentRows = load_jsonl_rows($stateDir . '/sent-log.jsonl');
foreach ($sentRows as $row) {
    $taskPacket = is_array($row['task_packet'] ?? null) ? $row['task_packet'] : [];
    $sourceRefKey = (string) ($taskPacket['source_ref'] ?? $row['source_ref'] ?? '');
    if ($sourceRefKey !== '') {
        $existingRefs[normalize_ref($sourceRefKey)] = true;
    }
}

if (empty($staffedEvents)) {
    $skipped = 1;
} elseif (!isset($existingRefs[normalize_ref($sourceRef)])) {
    $startLabel = $windowStart->format('l, F j');
    $endLabel = $windowEnd->format('l, F j');
    $eventIdList = array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $staffedEvents);
    $body = build_body($startLabel, $endLabel, $staffedEvents);
    $newRow = [
        'id' => $sourceRef,
        'kind' => 'outreach_weekly_missing_activities_catchup',
        'status' => 'pending',
        'ops_task_id' => 370193,
        'due_at' => $date->format('Y-m-d') . 'T10:00:00-05:00',
        'owner' => 'Robert Birnecker',
        'worker' => 'Vanessa Sterling',
        'dependency' => 'Monday catch-up reminder for potentially missing Outreach activities from ' . $windowStart->format('Y-m-d') . ' through ' . $windowEnd->format('Y-m-d'),
        'resolution_checks' => [],
        'event_ids' => $eventIdList,
        'shift_ids' => array_values($shiftIds),
        'email' => [
            'from' => 'vanessa.sterling@kovaldistillery.com',
            'from_name' => 'Vanessa Sterling',
            'to' => ['vanessa.sterling@kovaldistillery.com'],
            'cc' => ['robert@kovaldistillery.com'],
            'subject' => 'Monday missing-activities catch-up for outreach week ending ' . $windowEnd->format('F j'),
            'body' => $body,
        ],
        'source_ref' => $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'source_links' => 'OPS task 370193 + Outreach event IDs ' . implode(', ', $eventIdList),
        'approval_gates' => 'Internal scheduled reminder only; no external send beyond Vanessa/Robert.',
        'verification_readback' => 'Generated from live staffed Outreach event data for the prior full-week missing-activities catch-up window.',
        'papers_projection' => 'not_applicable',
        'next_update' => 'Pending Monday 10:00 AM scheduled-action queue for the approved send cycle.',
        'window_start' => $windowStart->format('Y-m-d'),
        'window_end' => $windowEnd->format('Y-m-d'),
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
    'window_start' => $windowStart->format('Y-m-d'),
    'window_end' => $windowEnd->format('Y-m-d'),
    'source_ref' => $sourceRef,
    'staffed_events_found' => count($staffedEvents),
    'event_ids' => array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $staffedEvents),
    'shift_ids' => array_values($shiftIds),
    'queued' => $queued,
    'skipped' => $skipped,
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
