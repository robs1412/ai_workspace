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

function slugify_email(string $email): string
{
    $slug = strtolower(trim($email));
    $slug = preg_replace('/[^a-z0-9]+/', '-', $slug) ?? '';
    return trim($slug, '-');
}

function format_time_label(?string $start, ?string $end): string
{
    $fmt = static function (?string $value): string {
        $raw = trim((string) $value);
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

function clean_notes(?string $importantInfo, ?string $notes): string
{
    $parts = [];
    foreach ([$importantInfo, $notes] as $value) {
        $text = trim((string) $value);
        if ($text === '') {
            continue;
        }
        $text = preg_replace("/\r\n?/", "\n", $text) ?? $text;
        if (!in_array($text, $parts, true)) {
            $parts[] = $text;
        }
    }
    if (empty($parts)) {
        return 'Please check the OPS link and reply if anything is missing.';
    }
    return implode("\n", $parts);
}

function greeting_name(array $user): string
{
    $first = trim((string) ($user['first_name'] ?? ''));
    if ($first !== '') {
        return $first;
    }
    $full = trim((string) (($user['first_name'] ?? '') . ' ' . ($user['last_name'] ?? '')));
    if ($full !== '') {
        return $full;
    }
    return 'there';
}

function build_email_body(string $dateLabel, array $user, array $events): string
{
    $userId = (int) ($user['id'] ?? 0);
    $lines = [
        'Hi ' . greeting_name($user) . ',',
        '',
        'Good morning. Here is your COT event detail for today, ' . $dateLabel . ':',
        '',
    ];

    $eventCount = count($events);
    foreach ($events as $index => $event) {
        $linkedShift = null;
        foreach ((array) ($event['linked_shifts'] ?? []) as $shiftRow) {
            $assignedIds = array_values(array_map('intval', (array) ($shiftRow['assigned_user_ids'] ?? [])));
            if ($userId > 0 && in_array($userId, $assignedIds, true)) {
                $linkedShift = $shiftRow;
                break;
            }
        }
        $lines[] = format_time_label((string) ($event['start_time'] ?? ''), (string) ($event['end_time'] ?? ''))
            . ' | ' . (string) ($event['event_name'] ?? 'Outreach Event');
        $location = trim((string) ($event['event_location'] ?? ''));
        if ($location !== '') {
            $lines[] = 'Location: ' . $location;
        }
        $accountLabels = array_values(array_filter(array_map('strval', (array) ($event['account_labels'] ?? []))));
        if (!empty($accountLabels)) {
            $lines[] = 'Account: ' . implode(', ', $accountLabels);
        }
        $displayProducts = array_values(array_filter(array_map('strval', (array) ($event['display_products'] ?? []))));
        if (!empty($displayProducts)) {
            $productSource = (string) ($event['display_product_source'] ?? '');
            $sourceSuffix = $productSource === 'latest_invoice' ? ' (latest invoice)' : '';
            $lines[] = 'Products / sample focus: ' . implode(', ', $displayProducts) . $sourceSuffix;
        }
        if (is_array($linkedShift)) {
            $shiftId = (int) ($linkedShift['shift_id'] ?? 0);
            $groupId = (int) ($linkedShift['group_id'] ?? 0);
            $groupLabel = $groupId > 0 ? ('Group #' . $groupId) : 'No Group';
            $shiftTime = format_time_label((string) ($linkedShift['start_time'] ?? ''), (string) ($linkedShift['end_time'] ?? ''));
            $shiftSummary = trim($shiftTime . ($groupLabel !== '' ? ' | ' . $groupLabel : ''));
            if ($shiftSummary !== '') {
                $lines[] = 'Store shift: ' . $shiftSummary;
            }
            if ($shiftId > 0) {
                $lines[] = 'OPS shift link: https://www.koval-distillery.com/ops/index.php?view=shifts&focus=' . $shiftId;
            }
        }
        $lines[] = 'Details / sample prep:';
        foreach (explode("\n", clean_notes($event['important_information'] ?? '', $event['notes'] ?? '')) as $noteLine) {
            $lines[] = rtrim($noteLine);
        }
        $lines[] = 'OPS event link: https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . (int) ($event['id'] ?? 0);
        if ($index < $eventCount - 1) {
            $lines[] = '';
            $lines[] = '---';
            $lines[] = '';
        }
    }

    $lines = array_merge($lines, [
        '',
        'Please check the OPS link before you head out in case anything changed. If something is missing or unclear, reply to me and I will help confirm it.',
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

$pdo = get_event_pdo();
$eventStmt = $pdo->prepare(
    "SELECT eb.id,
            eb.event_name,
            eb.event_date,
            eb.start_time,
            eb.end_time,
            eb.event_location,
            eb.notes,
            eb.important_information
       FROM event_bookings eb
      WHERE eb.event_category = 'Outreach'
        AND eb.event_date = ?
      ORDER BY COALESCE(NULLIF(eb.start_time, ''), '23:59:59') ASC, eb.id ASC"
);
$eventStmt->execute([$date->format('Y-m-d')]);
$eventRows = $eventStmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

$eventIds = array_values(array_filter(array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $eventRows)));
$linkedShifts = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];

$assignedUserIds = [];
$eventsByUser = [];
$eventsById = [];
foreach ($eventRows as $row) {
    $eventId = (int) ($row['id'] ?? 0);
    if ($eventId <= 0) {
        continue;
    }
    $row['account_labels'] = [];
    $row['display_products'] = [];
    $row['display_product_source'] = '';
    $eventsById[$eventId] = $row;
    foreach (($linkedShifts[$eventId] ?? []) as $link) {
        if ((int) ($link['deleted'] ?? 0) === 1) {
            continue;
        }
        foreach ((array) ($link['assigned_user_ids'] ?? []) as $userId) {
            $uid = (int) $userId;
            if ($uid <= 0) {
                continue;
            }
            $assignedUserIds[$uid] = $uid;
            if (!isset($eventsByUser[$uid])) {
                $eventsByUser[$uid] = [];
            }
            $eventsByUser[$uid][$eventId] = $row;
        }
    }
}

$allAccountIds = [];
$allProductIds = [];
foreach (array_keys($eventsById) as $eventId) {
    $accountIds = fetch_event_booking_accounts((int) $eventId);
    $productIds = fetch_event_booking_products((int) $eventId);
    $eventsById[$eventId]['account_ids'] = $accountIds;
    $eventsById[$eventId]['product_ids'] = $productIds;
    $allAccountIds = array_merge($allAccountIds, $accountIds);
    $allProductIds = array_merge($allProductIds, $productIds);
}
$accountRows = fetch_crm_accounts_by_ids($allAccountIds);
$productRows = fetch_crm_products_by_ids($allProductIds);
$latestInvoiceProducts = fetch_latest_invoice_products_by_account_ids($allAccountIds);
foreach (array_keys($eventsById) as $eventId) {
    $accountLabels = [];
    foreach ((array) ($eventsById[$eventId]['account_ids'] ?? []) as $accountId) {
        $accountRow = $accountRows[(int) $accountId] ?? null;
        if (!is_array($accountRow)) {
            continue;
        }
        $label = trim((string) ($accountRow['label'] ?? ''));
        if ($label !== '') {
            $accountLabels[] = $label;
        }
    }

    $productLabels = [];
    foreach ((array) ($eventsById[$eventId]['product_ids'] ?? []) as $productId) {
        $productRow = $productRows[(int) $productId] ?? null;
        if (!is_array($productRow)) {
            continue;
        }
        $label = trim((string) ($productRow['label'] ?? ''));
        if ($label !== '') {
            $productLabels[] = $label;
        }
    }

    $invoiceProductLabels = [];
    foreach ((array) ($eventsById[$eventId]['account_ids'] ?? []) as $accountId) {
        $invoiceRow = $latestInvoiceProducts[(int) $accountId] ?? null;
        if (!is_array($invoiceRow)) {
            continue;
        }
        foreach ((array) ($invoiceRow['products'] ?? []) as $productRow) {
            $label = trim((string) ($productRow['label'] ?? ''));
            if ($label === '' || in_array($label, $invoiceProductLabels, true)) {
                continue;
            }
            $invoiceProductLabels[] = $label;
        }
    }

    $eventsById[$eventId]['account_labels'] = $accountLabels;
    $eventsById[$eventId]['display_products'] = !empty($productLabels) ? $productLabels : $invoiceProductLabels;
    $eventsById[$eventId]['display_product_source'] = !empty($productLabels)
        ? 'linked_products'
        : (!empty($invoiceProductLabels) ? 'latest_invoice' : '');
    $eventsById[$eventId]['linked_shifts'] = $linkedShifts[$eventId] ?? [];
}

foreach ($eventsByUser as $userId => $userEvents) {
    foreach (array_keys($userEvents) as $eventId) {
        if (isset($eventsById[$eventId])) {
            $eventsByUser[$userId][$eventId] = $eventsById[$eventId];
        }
    }
}

$users = [];
if (!empty($assignedUserIds)) {
    $placeholders = implode(',', array_fill(0, count($assignedUserIds), '?'));
    $userStmt = $pdo->prepare(
        "SELECT id, first_name, last_name, user_name, email1, status, deleted
           FROM koval_crm.vtiger_users
          WHERE id IN ($placeholders)"
    );
    $userStmt->execute(array_values($assignedUserIds));
    foreach (($userStmt->fetchAll(PDO::FETCH_ASSOC) ?: []) as $row) {
        $users[(int) $row['id']] = $row;
    }
}

$scheduledPath = $stateDir . '/scheduled-actions.jsonl';
$scheduledRows = load_jsonl_rows($scheduledPath);
$existingRefs = [];
foreach ($scheduledRows as $row) {
    $sourceRef = (string) ($row['source_ref'] ?? $row['id'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[$sourceRef] = true;
    }
}

$sentRows = load_jsonl_rows($stateDir . '/sent-log.jsonl');
foreach ($sentRows as $row) {
    $taskPacket = is_array($row['task_packet'] ?? null) ? $row['task_packet'] : [];
    $sourceRef = (string) ($taskPacket['source_ref'] ?? $row['source_ref'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[$sourceRef] = true;
    }
}

$dateLabel = $date->format('l, F j');
$queued = 0;
$skipped = 0;
$rowsForDbSync = [];

foreach ($eventsByUser as $userId => $userEvents) {
    $user = $users[$userId] ?? null;
    if (!is_array($user)) {
        $skipped++;
        continue;
    }

    $email = strtolower(trim((string) ($user['email1'] ?? '')));
    $username = strtolower(trim((string) ($user['user_name'] ?? '')));
    $firstName = trim((string) ($user['first_name'] ?? ''));
    $lastName = trim((string) ($user['last_name'] ?? ''));
    if ($email === '' || (int) ($user['deleted'] ?? 0) !== 0 || strtolower((string) ($user['status'] ?? '')) !== 'active') {
        $skipped++;
        continue;
    }
    if (in_array($username, ['robert', 'admin', 'test', 'codex'], true)) {
        $skipped++;
        continue;
    }
    if ($firstName === 'Robert' || $lastName === 'Birnecker') {
        $skipped++;
        continue;
    }

    usort($userEvents, static function (array $a, array $b): int {
        return strcmp((string) ($a['start_time'] ?? ''), (string) ($b['start_time'] ?? ''))
            ?: ((int) ($a['id'] ?? 0) <=> (int) ($b['id'] ?? 0));
    });

    $eventIdList = array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $userEvents);
    $shiftIdList = [];
    foreach ($eventIdList as $eventId) {
        foreach (($linkedShifts[$eventId] ?? []) as $link) {
            if ((int) ($link['deleted'] ?? 0) === 1) {
                continue;
            }
            foreach ((array) ($link['assigned_user_ids'] ?? []) as $assignedId) {
                if ((int) $assignedId === (int) $userId) {
                    $shiftIdList[] = (int) ($link['shift_id'] ?? 0);
                }
            }
        }
    }
    $shiftIdList = array_values(array_unique(array_filter($shiftIdList)));

    $hashSeed = $email . '|' . implode(',', $eventIdList);
    $shortHash = substr(hash('sha256', $hashSeed), 0, 8);
    $sourceRef = 'vanessa-day-of-cot-event-details-' . $date->format('Y-m-d') . '-' . slugify_email($email) . '-' . $shortHash . '-0800';
    if (isset($existingRefs[$sourceRef])) {
        $skipped++;
        continue;
    }

    $subject = 'Your COT event details for ' . $date->format('l, F j');
    $body = build_email_body($dateLabel, $user, $userEvents);
    $actionId = $sourceRef;

    $newRow = [
        'id' => $actionId,
        'kind' => 'cot_day_of_event_details',
        'status' => 'pending',
        'ops_task_id' => 367971,
        'due_at' => $date->format('Y-m-d') . 'T08:00:00-05:00',
        'owner' => 'Robert Birnecker',
        'worker' => 'Vanessa Sterling',
        'dependency' => 'Day-of COT event details for ' . trim($firstName . ' ' . $lastName) . ' on ' . $date->format('Y-m-d'),
        'resolution_checks' => [],
        'event_ids' => $eventIdList,
        'shift_ids' => $shiftIdList,
        'calendar_id' => 'c_ocjnu99l5tpghlvrovtifk1io8@group.calendar.google.com',
        'calendar_event_id' => '',
        'email' => [
            'from' => 'vanessa.sterling@kovaldistillery.com',
            'from_name' => 'Vanessa Sterling',
            'to' => [$email],
            'cc' => ['robert@kovaldistillery.com'],
            'subject' => $subject,
            'body' => $body,
        ],
        'source_ref' => $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'source_links' => 'OPS task 367971 + Outreach event IDs ' . implode(', ', $eventIdList),
        'approval_gates' => 'No external send beyond the approved day-of detail email path.',
        'verification_readback' => 'generated from live OPS Outreach event data for same-day sending',
        'papers_projection' => 'not_applicable',
        'next_update' => 'Pending scheduled-action queue for approved send cycle.',
    ];
    $scheduledRows[] = $newRow;
    $rowsForDbSync[] = $newRow;
    $existingRefs[$sourceRef] = true;
    $queued++;
}

write_jsonl_rows($scheduledPath, $scheduledRows);
sync_scheduled_actions_db($rowsForDbSync);

echo json_encode([
    'ok' => true,
    'date' => $date->format('Y-m-d'),
    'events_found' => count($eventRows),
    'assigned_staff' => count($eventsByUser),
    'queued' => $queued,
    'skipped' => $skipped,
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
