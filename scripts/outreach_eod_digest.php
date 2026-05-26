#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

function arg_value(array $argv, string $name, ?string $default = null): ?string
{
    foreach ($argv as $arg) {
        if (str_starts_with($arg, $name . '=')) {
            return substr($arg, strlen($name) + 1);
        }
    }
    return $default;
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
    return $a !== '' ? $a : ($b !== '' ? $b : 'all day');
}

$dateRaw = arg_value($argv, '--date', date('Y-m-d'));
$limit = max(1, (int) arg_value($argv, '--limit', '8'));
$date = DateTimeImmutable::createFromFormat('Y-m-d', (string) $dateRaw);
if (!$date || $date->format('Y-m-d') !== $dateRaw) {
    fwrite(STDERR, "Invalid --date. Use YYYY-MM-DD.\n");
    exit(2);
}

$pdo = get_event_pdo();
$stmt = $pdo->prepare(
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
$stmt->execute([$date->format('Y-m-d')]);
$eventRows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
$eventIds = array_values(array_filter(array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $eventRows)));
$linkedShifts = function_exists('fetch_event_booking_shift_links') && $eventIds
    ? fetch_event_booking_shift_links($eventIds, false)
    : [];

$allAccountIds = [];
$allProductIds = [];
$eventsById = [];
foreach ($eventRows as $row) {
    $eventId = (int) ($row['id'] ?? 0);
    if ($eventId <= 0) {
        continue;
    }
    $accountIds = function_exists('fetch_event_booking_accounts') ? fetch_event_booking_accounts($eventId) : [];
    $productIds = function_exists('fetch_event_booking_products') ? fetch_event_booking_products($eventId) : [];
    $row['account_ids'] = $accountIds;
    $row['product_ids'] = $productIds;
    $eventsById[$eventId] = $row;
    $allAccountIds = array_merge($allAccountIds, $accountIds);
    $allProductIds = array_merge($allProductIds, $productIds);
}

$accountRows = function_exists('fetch_crm_accounts_by_ids') ? fetch_crm_accounts_by_ids($allAccountIds) : [];
$productRows = function_exists('fetch_crm_products_by_ids') ? fetch_crm_products_by_ids($allProductIds) : [];
$latestInvoiceProducts = function_exists('fetch_latest_invoice_products_by_account_ids')
    ? fetch_latest_invoice_products_by_account_ids($allAccountIds)
    : [];

$userIds = [];
foreach ($linkedShifts as $links) {
    foreach ((array) $links as $link) {
        if ((int) ($link['deleted'] ?? 0) === 1) {
            continue;
        }
        foreach ((array) ($link['assigned_user_ids'] ?? []) as $assignedId) {
            $uid = (int) $assignedId;
            if ($uid > 0) {
                $userIds[$uid] = $uid;
            }
        }
    }
}

$userLabels = [];
if ($userIds !== []) {
    $placeholders = implode(',', array_fill(0, count($userIds), '?'));
    $userStmt = $pdo->prepare(
        "SELECT id, first_name, last_name, user_name
           FROM koval_crm.vtiger_users
          WHERE id IN ($placeholders)"
    );
    $userStmt->execute(array_values($userIds));
    foreach (($userStmt->fetchAll(PDO::FETCH_ASSOC) ?: []) as $row) {
        $label = trim(((string) ($row['first_name'] ?? '')) . ' ' . ((string) ($row['last_name'] ?? '')));
        if ($label === '') {
            $label = trim((string) ($row['user_name'] ?? ''));
        }
        if ($label !== '') {
            $userLabels[(int) ($row['id'] ?? 0)] = $label;
        }
    }
}

$items = [];
foreach ($eventsById as $eventId => $row) {
    $accountLabels = [];
    foreach ((array) ($row['account_ids'] ?? []) as $accountId) {
        $accountRow = $accountRows[(int) $accountId] ?? null;
        $label = is_array($accountRow) ? trim((string) ($accountRow['label'] ?? '')) : '';
        if ($label !== '' && !in_array($label, $accountLabels, true)) {
            $accountLabels[] = $label;
        }
    }

    $productLabels = [];
    foreach ((array) ($row['product_ids'] ?? []) as $productId) {
        $productRow = $productRows[(int) $productId] ?? null;
        $label = is_array($productRow) ? trim((string) ($productRow['label'] ?? '')) : '';
        if ($label !== '' && !in_array($label, $productLabels, true)) {
            $productLabels[] = $label;
        }
    }
    if ($productLabels === []) {
        foreach ((array) ($row['account_ids'] ?? []) as $accountId) {
            $invoiceRow = $latestInvoiceProducts[(int) $accountId] ?? null;
            if (!is_array($invoiceRow)) {
                continue;
            }
            foreach ((array) ($invoiceRow['products'] ?? []) as $productRow) {
                $label = trim((string) ($productRow['label'] ?? ''));
                if ($label !== '' && !in_array($label, $productLabels, true)) {
                    $productLabels[] = $label;
                }
            }
        }
    }

    $assigned = [];
    $shiftCount = 0;
    foreach ((array) ($linkedShifts[$eventId] ?? []) as $link) {
        if ((int) ($link['deleted'] ?? 0) === 1) {
            continue;
        }
        $shiftCount++;
        foreach ((array) ($link['assigned_user_ids'] ?? []) as $assignedId) {
            $label = $userLabels[(int) $assignedId] ?? '';
            if ($label !== '' && !in_array($label, $assigned, true)) {
                $assigned[] = $label;
            }
        }
    }

    $items[] = [
        'event_id' => $eventId,
        'title' => (string) ($row['event_name'] ?? 'Outreach Event'),
        'time_label' => format_time_label((string) ($row['start_time'] ?? ''), (string) ($row['end_time'] ?? '')),
        'location' => trim((string) ($row['event_location'] ?? '')),
        'account_labels' => $accountLabels,
        'display_products' => $productLabels,
        'assigned_users' => $assigned,
        'assigned_count' => count($assigned),
        'shift_count' => $shiftCount,
        'ops_link' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
        'notes' => trim((string) ($row['important_information'] ?? '') . ' ' . (string) ($row['notes'] ?? '')),
    ];
}

echo json_encode([
    'ok' => true,
    'date' => $date->format('Y-m-d'),
    'count' => count($items),
    'items' => array_slice($items, 0, $limit),
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
