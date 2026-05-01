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

function time_label(?string $start, ?string $end): string
{
    $format = static function (?string $time): string {
        $raw = trim((string) $time);
        if ($raw === '') {
            return '';
        }
        $dt = DateTime::createFromFormat('H:i:s', $raw) ?: DateTime::createFromFormat('H:i', $raw);
        return $dt ? strtolower($dt->format('g:ia')) : $raw;
    };
    $a = $format($start);
    $b = $format($end);
    if ($a !== '' && $b !== '') {
        return $a . ' - ' . $b;
    }
    return $a !== '' ? $a : $b;
}

function product_prep_note(?string $notes): string
{
    $clean = preg_replace('/\[(?:connecteam|ct)[^\]]*\]/i', ' ', (string) $notes) ?? '';
    $clean = trim(preg_replace('/\s+/', ' ', $clean) ?? '');
    $genericNotes = [
        'in-store tasting',
        'in store tasting',
        'tasting',
        'demo',
    ];
    if (in_array(strtolower($clean), $genericNotes, true)) {
        $clean = '';
    }
    if ($clean !== '') {
        return $clean;
    }
    return 'Check Salesreport Chain Store Intelligence / Chain Invoice Report before sending the staff reminder.';
}

$startRaw = arg_value($argv, '--start', date('Y-m-d'));
$startDate = DateTimeImmutable::createFromFormat('Y-m-d', (string) $startRaw);
if (!$startDate) {
    fwrite(STDERR, "Invalid --start date. Use YYYY-MM-DD.\n");
    exit(2);
}
$endDate = $startDate->modify('+6 days');

$pdo = get_event_pdo();
$stmt = $pdo->prepare(
    "SELECT id, event_name, event_date, start_time, end_time, event_location, notes
       FROM event_bookings
      WHERE event_category = 'Outreach'
        AND event_date BETWEEN ? AND ?
      ORDER BY event_date ASC, COALESCE(NULLIF(start_time, ''), '23:59:59') ASC, event_name ASC, id ASC"
);
$stmt->execute([$startDate->format('Y-m-d'), $endDate->format('Y-m-d')]);
$events = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

$eventIds = array_map(static fn(array $row): int => (int) $row['id'], $events);
$shiftLinksByEvent = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];

$rows = [];
$summary = [
    'total' => 0,
    'covered' => 0,
    'open' => 0,
    'needs_linked_shift' => 0,
];

foreach ($events as $event) {
    $eventId = (int) $event['id'];
    $shiftSummary = summarize_event_shift_links($shiftLinksByEvent[$eventId] ?? []);
    $totalShifts = (int) ($shiftSummary['total_shifts'] ?? 0);
    $assignedShifts = (int) ($shiftSummary['assigned_shifts'] ?? 0);
    $assignedNames = array_values(array_filter(array_map('strval', (array) ($shiftSummary['assigned_names'] ?? []))));
    if ($totalShifts <= 0) {
        $staffing = 'Needs linked shift';
        $summary['needs_linked_shift']++;
    } elseif ($assignedShifts >= $totalShifts) {
        $staffing = 'Covered - assigned (' . $assignedShifts . '/' . $totalShifts . ' linked shifts)';
        $summary['covered']++;
    } elseif ($assignedShifts > 0) {
        $staffing = 'Partially assigned (' . $assignedShifts . '/' . $totalShifts . ' linked shifts)';
        $summary['open']++;
    } else {
        $staffing = 'Linked shift open / unassigned (' . $assignedShifts . '/' . $totalShifts . ' linked shifts)';
        $summary['open']++;
    }

    $rows[] = [
        'date' => (string) $event['event_date'],
        'event' => (string) $event['event_name'],
        'time' => time_label($event['start_time'] ?? '', $event['end_time'] ?? ''),
        'ops' => 'OPS #' . $eventId,
        'staffing' => $staffing,
        'assigned' => implode(', ', $assignedNames),
        'product_prep' => product_prep_note($event['notes'] ?? ''),
        'address' => trim((string) ($event['event_location'] ?? '')),
    ];
}
$summary['total'] = count($rows);

$summaryText = $summary['total'] . ' OPS Outreach rows from '
    . $startDate->format('Y-m-d') . ' through ' . $endDate->format('Y-m-d') . '; '
    . $summary['covered'] . ' fully covered; '
    . $summary['open'] . ' open/unassigned or partially assigned; '
    . $summary['needs_linked_shift'] . ' need linked shifts.';

$tableRows = '';
foreach ($rows as $row) {
    $staffing = (string) $row['staffing'];
    $highlight = (str_contains($staffing, 'open / unassigned') || str_contains($staffing, 'Needs linked shift') || str_contains($staffing, 'Partially assigned'))
        ? ' style="background:#fce4e4;"'
        : '';
    $tableRows .= '<tr' . $highlight . '>'
        . '<td>' . h($row['date']) . '</td>'
        . '<td>' . h($row['event']) . '</td>'
        . '<td>' . h($row['time']) . '</td>'
        . '<td>' . h($row['ops']) . '</td>'
        . '<td>' . h($row['staffing']) . '</td>'
        . '<td>' . h($row['assigned']) . '</td>'
        . '<td>' . h($row['product_prep']) . '</td>'
        . '<td>' . h($row['address']) . '</td>'
        . '</tr>' . "\n";
}

$html = '<!doctype html><html><body style="font-family:Arial,sans-serif;">'
    . '<p>Hi Robert,</p>'
    . '<p>Draft for approval: this is the current weekly upcoming tastings report for Mitch Conti. It has not been sent to Mitch.</p>'
    . '<p><strong>Summary:</strong> ' . h($summaryText) . '</p>'
    . '<p>Open, partially assigned, or missing linked-shift rows are highlighted in light red. The Product / sample prep column should be used when reminding staff what products the account appears to carry and what samples/materials to bring.</p>'
    . '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px;">'
    . '<thead><tr style="background:#f2f2f2;">'
    . '<th>Date</th><th>Event</th><th>Time</th><th>OPS</th><th>Staffing coverage</th><th>Assigned</th><th>Product / sample prep</th><th>Address</th>'
    . '</tr></thead><tbody>' . $tableRows . '</tbody></table>'
    . '<p>Best,<br><br>Vanessa</p>'
    . '<p>Vanessa Sterling<br><br>Outreach Coordinator<br>KOVAL Distillery<br>4241 N Ravenswood Ave<br>Chicago, IL 60613<br>312 878 7988<br>http://www.koval-distillery.com<br><br>X | Instagram | Facebook</p>'
    . '</body></html>';

$plain = [
    'Hi Robert,',
    '',
    'Draft for approval: this is the current weekly upcoming tastings report for Mitch Conti. It has not been sent to Mitch.',
    '',
    'Summary: ' . $summaryText,
    '',
    'Use Product / sample prep when reminding staff what products the account appears to carry and what samples/materials to bring.',
    '',
    'Date | Event | Time | OPS | Staffing coverage | Assigned | Product / sample prep | Address',
];
foreach ($rows as $row) {
    $plain[] = implode(' | ', [
        $row['date'],
        $row['event'],
        $row['time'],
        $row['ops'],
        $row['staffing'],
        $row['assigned'],
        $row['product_prep'],
        $row['address'],
    ]);
}
$plain[] = '';
$plain[] = 'Best,';
$plain[] = '';
$plain[] = 'Vanessa';
$plain[] = '';
$plain[] = 'Vanessa Sterling';
$plain[] = '';
$plain[] = 'Outreach Coordinator';
$plain[] = 'KOVAL Distillery';
$plain[] = '4241 N Ravenswood Ave';
$plain[] = 'Chicago, IL 60613';
$plain[] = '312 878 7988';
$plain[] = 'http://www.koval-distillery.com';
$plain[] = '';
$plain[] = 'X | Instagram | Facebook';

echo json_encode([
    'from' => 'vanessa.sterling@kovaldistillery.com',
    'from_name' => 'Vanessa Sterling',
    'to' => ['robert@kovaldistillery.com'],
    'subject' => 'Draft for approval: Mitch weekly upcoming tastings report',
    'body' => implode("\n", $plain),
    'html_body' => $html,
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
