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

function has_flag(array $argv, string $name): bool
{
    return in_array($name, $argv, true);
}

function extract_marker(string $text, string $name): string
{
    if (preg_match('/\[' . preg_quote($name, '/') . ':([^\]]+)\]/', $text, $m)) {
        return trim((string) $m[1]);
    }
    return '';
}

function time_key(array $event): string
{
    return ((string) ($event['start_time'] ?? '') >= '16:00:00') ? 'late' : 'early';
}

function run_portal_cancel(string $request, string $date, string $store, string $time): array
{
    $cmd = [
        'node',
        '/Users/werkstatt/ai_workspace/.private/wholefoods-sync/cancel_wfm_tasting.js',
        '--request', $request,
        '--date', $date,
        '--store', $store,
        '--time', $time,
        '--cancel',
        '--confirm',
    ];
    $descriptor = [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
    $env = array_merge($_ENV, ['NODE_PATH' => '/Users/werkstatt/playwright-scraper/node_modules']);
    $proc = proc_open($cmd, $descriptor, $pipes, '/Users/werkstatt/ai_workspace', $env);
    if (!is_resource($proc)) {
        throw new RuntimeException('Unable to start WFM portal cancel helper.');
    }
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $code = proc_close($proc);
    $decoded = json_decode((string) $stdout, true);
    if ($code !== 0 || !is_array($decoded) || empty($decoded['ok'])) {
        throw new RuntimeException('WFM portal cancellation failed: ' . trim((string) ($stderr ?: $stdout)));
    }
    return $decoded;
}

function reconcile_ops(int $eventId, int $shiftId, string $approvalRef, array $portal): array
{
    $eventPdo = get_event_pdo();
    $trackPdo = get_tracktime_pdo();
    $marker = '[wfm-canceled:' . (new DateTimeImmutable('now', new DateTimeZone('America/Chicago')))->format('Y-m-d') . ']';
    $target = is_array($portal['target'] ?? null) ? $portal['target'] : [];
    $note = 'WFM portal cancellation confirmed after approval ' . $approvalRef
        . ': Request ' . (string) ($target['request'] ?? '')
        . ', store ' . (string) ($target['store'] ?? '')
        . ', date ' . (string) ($target['date'] ?? '')
        . ', time ' . (string) ($target['time'] ?? '')
        . ', reason ' . (string) ($portal['reason'] ?? 'Unable to Attend')
        . '. Portal scheduled-day readback no longer lists the target row. ' . $marker;

    $eventPdo->beginTransaction();
    $stmt = $eventPdo->prepare('SELECT event_name, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $stmt->execute([$eventId]);
    $event = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$event) {
        throw new RuntimeException('OPS event not found.');
    }
    $eventName = (string) $event['event_name'];
    if (stripos($eventName, 'CANCELED - ') !== 0) {
        $eventName = 'CANCELED - ' . $eventName;
    }
    $notes = (string) ($event['notes'] ?? '');
    if (strpos($notes, '[wfm-canceled:') === false) {
        $notes = rtrim($notes) . "\n\n" . $note;
    }
    $important = (string) ($event['important_information'] ?? '');
    if (strpos($important, '[wfm-canceled:') === false) {
        $important = rtrim($important) . "\n\n" . $note;
    }
    $eventPdo->prepare('UPDATE event_bookings SET event_name = ?, notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
        ->execute([$eventName, $notes, $important, $eventId]);
    $eventPdo->commit();

    if ($shiftId > 0) {
        $trackPdo->beginTransaction();
        $stmt = $trackPdo->prepare('SELECT notes FROM shifts WHERE id = ? FOR UPDATE');
        $stmt->execute([$shiftId]);
        $shift = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($shift) {
            $shiftNotes = (string) ($shift['notes'] ?? '');
            if (strpos($shiftNotes, '[wfm-canceled:') === false) {
                $shiftNotes = rtrim($shiftNotes) . "\n\n" . $note;
            }
            $trackPdo->prepare('UPDATE shifts SET deleted = 1, notes = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
                ->execute([$shiftNotes, 1332, $shiftId]);
        }
        $trackPdo->commit();
    }

    return ['event_id' => $eventId, 'event_name' => $eventName, 'shift_id' => $shiftId, 'marker' => $marker];
}

$eventId = (int) (arg_value($argv, '--event-id', '0') ?? '0');
$approvalRef = trim((string) arg_value($argv, '--approval-ref', ''));
if ($eventId <= 0 || $approvalRef === '' || !has_flag($argv, '--confirm')) {
    fwrite(STDERR, "Usage: php complete_wfm_portal_cancellation.php --event-id ID --approval-ref REF --confirm\n");
    exit(2);
}

$pdo = get_event_pdo();
$stmt = $pdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
$stmt->execute([$eventId]);
$event = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$event) {
    throw new RuntimeException('OPS event not found.');
}
$notes = (string) ($event['notes'] ?? '') . "\n" . (string) ($event['important_information'] ?? '');
$request = arg_value($argv, '--request', extract_marker($notes, 'wfm-request')) ?? '';
$store = arg_value($argv, '--store', extract_marker($notes, 'wfm-store')) ?? '';
$date = arg_value($argv, '--date', (string) ($event['event_date'] ?? '')) ?? '';
$time = arg_value($argv, '--time', time_key($event)) ?? '';
$links = fetch_event_booking_shift_links([$eventId], false)[$eventId] ?? [];
$shiftId = 0;
foreach ($links as $link) {
    if ((int) ($link['deleted'] ?? 0) === 0 && (int) ($link['shift_id'] ?? 0) > 0) {
        $shiftId = (int) $link['shift_id'];
        break;
    }
}

if ($request === '' || $store === '' || $date === '' || $time === '') {
    throw new RuntimeException('Missing WFM request/store/date/time target.');
}

$portal = run_portal_cancel($request, $date, $store, $time);
$ops = reconcile_ops($eventId, $shiftId, $approvalRef, $portal);

echo json_encode(['ok' => true, 'portal' => $portal, 'ops' => $ops], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
