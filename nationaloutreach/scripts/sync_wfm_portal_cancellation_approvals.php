#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

const STATE_DIR = '/Users/admin/.nationaloutreach-launch/state';
const RECORDER = '/Users/werkstatt/ai_workspace/scripts/scheduled_actions_mysql_recorder.php';
const ROBERT_EMAIL = 'robert@kovaldistillery.com';
const WFM_APPROVAL_MARKER = 'wfm-portal-cancel-approval';

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

function has_flag(array $argv, string $name): bool
{
    return in_array($name, $argv, true);
}

function format_time_label(?string $start, ?string $end): string
{
    $fmt = static function (?string $value): string {
        $raw = trim((string) $value);
        if ($raw === '') {
            return '';
        }
        $dt = DateTimeImmutable::createFromFormat('H:i:s', $raw) ?: DateTimeImmutable::createFromFormat('H:i', $raw);
        return $dt ? $dt->format('g:i A') : $raw;
    };
    $a = $fmt($start);
    $b = $fmt($end);
    return ($a !== '' && $b !== '') ? $a . ' to ' . $b : ($a !== '' ? $a : $b);
}

function event_start_datetime(array $event, DateTimeZone $tz): ?DateTimeImmutable
{
    $date = trim((string) ($event['event_date'] ?? ''));
    if ($date === '') {
        return null;
    }
    $time = trim((string) ($event['start_time'] ?? '')) ?: '00:00:00';
    try {
        return new DateTimeImmutable($date . ' ' . $time, $tz);
    } catch (Throwable) {
        return null;
    }
}

function extract_marker(string $text, string $name): string
{
    if (preg_match('/\[' . preg_quote($name, '/') . ':([^\]]+)\]/', $text, $m)) {
        return trim((string) $m[1]);
    }
    return '';
}

function wfm_time_key(array $event): string
{
    $start = trim((string) ($event['start_time'] ?? ''));
    if ($start >= '16:00:00') {
        return 'late';
    }
    return 'early';
}

function upsert_scheduled_actions(array $rows): array
{
    $descriptor = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $proc = proc_open(['/usr/local/bin/php', RECORDER, 'upsert', 'nationaloutreach'], $descriptor, $pipes, '/Users/werkstatt/ai_workspace');
    if (!is_resource($proc)) {
        throw new RuntimeException('Unable to start scheduled actions recorder.');
    }
    fwrite($pipes[0], json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $code = proc_close($proc);
    if ($code !== 0) {
        throw new RuntimeException('scheduled action upsert failed: ' . trim((string) $stderr));
    }
    $decoded = json_decode((string) $stdout, true);
    return is_array($decoded) ? $decoded : ['ok' => false, 'raw' => $stdout];
}

function build_approval_row(array $event, array $summary, DateTimeImmutable $now): array
{
    $eventId = (int) ($event['id'] ?? 0);
    $notes = (string) ($event['notes'] ?? '') . "\n" . (string) ($event['important_information'] ?? '');
    $request = extract_marker($notes, 'wfm-request');
    $store = extract_marker($notes, 'wfm-store');
    $start = event_start_datetime($event, new DateTimeZone('America/Chicago'));
    $dateLabel = $start ? $start->format('l, F j, Y') : (string) ($event['event_date'] ?? '');
    $timeLabel = format_time_label((string) ($event['start_time'] ?? ''), (string) ($event['end_time'] ?? ''));
    $timeKey = wfm_time_key($event);
    $shiftIds = array_values(array_filter(array_map('intval', $summary['shift_ids'] ?? [])));
    $actionId = WFM_APPROVAL_MARKER . '-ops' . $eventId . '-' . ($start ? $start->format('Ymd-Hi') : date('Ymd-His'));
    $approvalToken = 'APPROVE WFM CANCEL OPS ' . $eventId;
    $command = 'NODE_PATH=/Users/werkstatt/playwright-scraper/node_modules node /Users/werkstatt/ai_workspace/.private/wholefoods-sync/cancel_wfm_tasting.js --request '
        . escapeshellarg($request)
        . ' --date ' . escapeshellarg((string) ($event['event_date'] ?? ''))
        . ' --store ' . escapeshellarg($store !== '' ? $store : (string) ($event['event_name'] ?? ''))
        . ' --time ' . escapeshellarg($timeKey)
        . ' --cancel --confirm';

    $body = [
        'Hi Robert,',
        '',
        'This Whole Foods tasting is still far enough out to cancel in the WFM demo portal, and it is currently uncovered:',
        '',
        'Event: ' . (string) ($event['event_name'] ?? ''),
        'Date/time: ' . $dateLabel . ($timeLabel !== '' ? ', ' . $timeLabel : ''),
        'WFM request/store: ' . ($request !== '' ? $request : 'unknown request') . ' / ' . ($store !== '' ? $store : 'unknown store'),
        'OPS reference: OPS event ' . $eventId . ($shiftIds ? ' / TrackTime shift ' . implode(',', $shiftIds) : ''),
        'Coverage: ' . (int) ($summary['assigned_shifts'] ?? 0) . ' assigned active shifts out of ' . (int) ($summary['total_shifts'] ?? 0),
        '',
        'Reply with exactly this line if you want me to cancel it in the WFM portal:',
        $approvalToken,
        '',
        'If we wait until the under-24-hour window, the fallback is a Robert/Sonat store-call reminder instead.',
        '',
        'Internal command target after approval:',
        $command,
        '',
        'Vanessa',
    ];

    return [
        'id' => $actionId,
        'status' => 'pending',
        'due_at' => $now->format(DateTimeInterface::ATOM),
        'source_ref' => $actionId,
        'ops_task_id' => 'OPS event ' . $eventId,
        'kind' => 'wfm_portal_cancellation_approval',
        'approval_token' => $approvalToken,
        'email' => [
            'from' => 'vanessa.sterling@kovaldistillery.com',
            'from_name' => 'Vanessa Sterling',
            'to' => [ROBERT_EMAIL],
            'cc' => [],
            'subject' => 'Approval needed: cancel WFM tasting ' . ($request !== '' ? '#' . $request . ' ' : '') . 'OPS ' . $eventId,
            'body' => implode("\n", $body),
            'source_ref' => $actionId,
            'requester' => 'WFM cancellation automation',
            'owner_lane' => 'outreach-coordinator',
            'approval_gates' => 'Internal Robert approval email only; no WFM portal mutation until Robert replies with the exact approval token.',
            'verification_readback' => 'Queued approval request for uncovered WFM tasting before the under-24-hour store-call fallback.',
            'task_packet' => [
                'source_ref' => $actionId,
                'dedupe_key' => 'taskflow-' . $actionId,
                'intake_channel' => 'scheduled-action:nationaloutreach',
                'owner_lane' => 'outreach-coordinator',
                'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
                'ops_portal_or_domain_task' => 'WFM request ' . $request . ' / OPS event ' . $eventId,
                'status' => 'waiting',
                'scheduled_action' => $actionId,
                'approval_gates' => 'Robert must approve before WFM portal cancellation.',
                'verification_readback' => 'Approval prompt queued for Robert.',
                'next_update' => 'Wait for exact approval token: ' . $approvalToken,
                'requested_deliverable' => 'Approve or decline WFM portal cancellation before it becomes a store-call reminder.',
                'human_owner_or_recipient' => 'Robert Birnecker <' . ROBERT_EMAIL . '>',
                'output_channel' => 'email',
                'proof_required' => 'sent Message-ID for approval prompt, then WFM portal readback if approved',
            ],
        ],
    ];
}

$tz = new DateTimeZone('America/Chicago');
$now = new DateTimeImmutable(arg_value($argv, '--now', 'now') ?? 'now', $tz);
$hours = max(25, (int) (arg_value($argv, '--hours', '48') ?? '48'));
$dryRun = has_flag($argv, '--dry-run');
$queue = has_flag($argv, '--queue');
$eventId = (int) (arg_value($argv, '--event-id', '0') ?? '0');

$pdo = get_event_pdo();
if ($eventId > 0) {
    $stmt = $pdo->prepare("SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information FROM event_bookings WHERE id = ?");
    $stmt->execute([$eventId]);
} else {
    $end = $now->modify('+' . $hours . ' hours');
    $stmt = $pdo->prepare(
        "SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information
           FROM event_bookings
          WHERE event_category = 'Outreach'
            AND event_date BETWEEN ? AND ?
            AND event_name NOT LIKE 'CANCELED - %'
          ORDER BY event_date ASC, COALESCE(NULLIF(start_time, ''), '23:59:59') ASC, id ASC"
    );
    $stmt->execute([$now->format('Y-m-d'), $end->format('Y-m-d')]);
}
$events = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
$eventIds = array_values(array_filter(array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $events)));
$linksByEvent = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];
$rows = [];
$results = [];

foreach ($events as $event) {
    $id = (int) ($event['id'] ?? 0);
    $haystack = strtolower((string) ($event['event_name'] ?? '') . ' ' . (string) ($event['event_location'] ?? '') . ' ' . (string) ($event['notes'] ?? ''));
    if (!str_contains($haystack, 'whole foods') && !str_contains($haystack, 'wfm')) {
        continue;
    }
    if (str_contains((string) ($event['notes'] ?? ''), '[wfm-canceled:')) {
        continue;
    }
    $start = event_start_datetime($event, $tz);
    if ($start === null || $start <= $now->modify('+24 hours') || $start > $now->modify('+' . $hours . ' hours')) {
        continue;
    }
    $links = $linksByEvent[$id] ?? [];
    $summary = summarize_event_shift_links($links);
    $shiftIds = [];
    foreach ($links as $link) {
        if ((int) ($link['deleted'] ?? 0) === 0 && (int) ($link['shift_id'] ?? 0) > 0) {
            $shiftIds[] = (int) $link['shift_id'];
        }
    }
    $summary['shift_ids'] = array_values(array_unique($shiftIds));
    if ((int) ($summary['total_shifts'] ?? 0) > 0 && (int) ($summary['assigned_shifts'] ?? 0) > 0) {
        $results[] = ['event_id' => $id, 'status' => 'skipped_covered'];
        continue;
    }
    $row = build_approval_row($event, $summary, $now);
    $rows[] = $row;
    $results[] = ['event_id' => $id, 'status' => $queue ? 'queued_for_upsert' : 'eligible', 'action_id' => $row['id'], 'approval_token' => $row['approval_token']];
}

$upsert = null;
if ($queue && $rows !== []) {
    $upsert = upsert_scheduled_actions($rows);
}

echo json_encode([
    'ok' => true,
    'mode' => $queue ? 'queue' : ($dryRun ? 'dry-run' : 'preview'),
    'now' => $now->format(DateTimeInterface::ATOM),
    'window_hours' => $hours,
    'eligible' => count($rows),
    'upsert' => $upsert,
    'results' => $results,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
