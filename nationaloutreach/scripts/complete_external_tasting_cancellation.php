#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

const DEFAULT_STATE_DIR = '/Users/admin/.nationaloutreach-launch/state';
const MARIANOS_CANCEL_TO = 'abseventrequest@abstastings.com';
const MARIANOS_CANCEL_CC = 'rafael@abstastings.com';
const BINNYS_CANCEL_TO = 'rpaquin@binnys.com';

function complete_format_time_label(?string $start, ?string $end): string
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

function complete_safe_slug(string $value): string
{
    $slug = preg_replace('/[^A-Za-z0-9_.-]+/', '-', strtolower(trim($value))) ?? '';
    return trim($slug, '-') !== '' ? trim($slug, '-') : 'tasting-cancellation';
}

function complete_event_start_datetime(array $event, DateTimeZone $tz): ?DateTimeImmutable
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

function complete_cancellation_rule_for_event(array $event): array
{
    $haystack = strtolower(trim((string) ($event['event_name'] ?? '') . ' ' . (string) ($event['event_location'] ?? '')));
    if (str_contains($haystack, 'mariano')) {
        return [
            'key' => 'marianos',
            'label' => "Mariano's",
            'channel' => 'email',
            'to' => [MARIANOS_CANCEL_TO],
            'cc' => [MARIANOS_CANCEL_CC],
            'recipient_label' => 'Adult Beverage Solutions event request; Rafael Morales copied',
        ];
    }
    if (str_contains($haystack, 'binny')) {
        return [
            'key' => 'binnys',
            'label' => "Binny's",
            'channel' => 'email',
            'to' => [BINNYS_CANCEL_TO],
            'cc' => [],
            'recipient_label' => "Rene Paquin at Binny's",
        ];
    }
    return ['key' => 'unknown', 'label' => 'unknown account', 'channel' => 'blocked'];
}

function complete_append_jsonl_row(string $path, array $row): void
{
    $dir = dirname($path);
    if (!is_dir($dir)) {
        mkdir($dir, 0700, true);
    }
    file_put_contents($path, json_encode($row, JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND | LOCK_EX);
    chmod($path, 0600);
}

function complete_queue_payload(string $stateDir, array $payload, string $actionId, int $eventId, string $status): string
{
    $outbox = $stateDir . '/outbox';
    if (!is_dir($outbox)) {
        mkdir($outbox, 0700, true);
    }
    $draftPath = $outbox . '/' . complete_safe_slug($actionId) . '.approved.json';
    file_put_contents($draftPath, json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n", LOCK_EX);
    chmod($draftPath, 0600);
    complete_append_jsonl_row($stateDir . '/scheduled-actions-log.jsonl', [
        'logged_at' => (new DateTimeImmutable('now', new DateTimeZone('America/Chicago')))->format('Y-m-d\TH:i:sO'),
        'action_id' => $actionId,
        'status' => $status,
        'draft' => $draftPath,
        'event_id' => $eventId,
    ]);
    return $draftPath;
}

function complete_build_cancel_payload(array $event, array $shiftSummary, string $actionId, DateTimeImmutable $now, string $reason, array $rule): array
{
    $eventId = (int) ($event['id'] ?? 0);
    $eventName = trim((string) ($event['event_name'] ?? 'tasting'));
    $eventDate = (string) ($event['event_date'] ?? '');
    $start = complete_event_start_datetime($event, new DateTimeZone('America/Chicago'));
    $dateLabel = $start ? $start->format('l, F j, Y') : $eventDate;
    $timeLabel = complete_format_time_label((string) ($event['start_time'] ?? ''), (string) ($event['end_time'] ?? ''));
    $location = trim((string) ($event['event_location'] ?? ''));
    $shiftIds = array_values(array_filter(array_map('intval', $shiftSummary['shift_ids'] ?? [])));
    $opsTask = 'OPS event ' . $eventId . ($shiftIds ? ' / TrackTime shift ' . implode(',', $shiftIds) : '');
    $body = [
        'Hello,',
        '',
        'Please cancel the KOVAL tasting scheduled for ' . $dateLabel
            . ($timeLabel !== '' ? ', from ' . $timeLabel : '')
            . ' at ' . $eventName
            . ($location !== '' ? ', ' . $location : '')
            . '.',
        '',
        'We were not able to secure coverage for this tasting.',
        '',
        'Thank you,',
        '',
        'Vanessa',
        '',
        'Vanessa Sterling',
        'Outreach Coordinator',
        'KOVAL Distillery',
        '4241 N Ravenswood Ave',
        'Chicago, IL 60613',
        '312 878 7988',
        'http://www.koval-distillery.com',
        '',
        'X | Instagram | Facebook',
    ];
    return [
        'from' => 'vanessa.sterling@kovaldistillery.com',
        'from_name' => 'Vanessa Sterling',
        'to' => $rule['to'] ?? [],
        'cc' => $rule['cc'] ?? [],
        'subject' => 'Cancellation: KOVAL tasting at ' . $eventName . ' on ' . ($start ? $start->format('l, F j') : $eventDate),
        'body' => implode("\n", $body),
        'source_ref' => $actionId,
        'task_packet' => [
            'source_ref' => $actionId,
            'dedupe_key' => 'taskflow-' . $actionId,
            'intake_channel' => 'approved-send:nationaloutreach',
            'requester' => 'Vanessa Sterling <vanessa.sterling@kovaldistillery.com>',
            'owner_lane' => 'outreach-coordinator',
            'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
            'ops_portal_or_domain_task' => $opsTask,
            'status' => 'working',
            'due_or_trigger' => $now->format('Y-m-d H:i:s T'),
            'scheduled_action' => $actionId,
            'calendar_event' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
            'approval_gates' => 'Approved external cancellation path.',
            'verification_readback' => 'Owner approved external cancellation; draft queued for approved send cycle.',
            'next_update' => 'Approved external cancellation draft queued for National Outreach send cycle.',
            'requested_deliverable' => 'Cancel ' . (string) ($rule['label'] ?? 'approved') . ' tasting because cancellation fallback condition was met: ' . $reason . '.',
            'human_owner_or_recipient' => (string) ($rule['recipient_label'] ?? 'Approved cancellation recipient'),
            'output_channel' => 'email',
            'proof_required' => 'sent Message-ID plus sent-log readback',
            'owner_question_required' => 'false',
        ],
    ];
}

function complete_arg_value(array $argv, string $name, ?string $default = null): ?string
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

function complete_has_flag(array $argv, string $name): bool
{
    return in_array($name, $argv, true);
}

function complete_mark_ops_canceled(int $eventId, array $shiftIds, string $approvalRef, string $accountKey): array
{
    $eventPdo = get_event_pdo();
    $trackPdo = get_tracktime_pdo();
    $today = (new DateTimeImmutable('now', new DateTimeZone('America/Chicago')))->format('Y-m-d');
    $marker = '[' . $accountKey . '-canceled:' . $today . ']';
    $note = ucfirst($accountKey) . ' external cancellation email queued after approval ' . $approvalRef . '. ' . $marker;

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
    if (strpos($notes, $marker) === false) {
        $notes = rtrim($notes) . "\n\n" . $note;
    }
    $important = (string) ($event['important_information'] ?? '');
    if (strpos($important, $marker) === false) {
        $important = rtrim($important) . "\n\n" . $note;
    }
    $eventPdo->prepare('UPDATE event_bookings SET event_name = ?, notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
        ->execute([$eventName, $notes, $important, $eventId]);
    $eventPdo->commit();

    foreach ($shiftIds as $shiftId) {
        $shiftId = (int) $shiftId;
        if ($shiftId <= 0) {
            continue;
        }
        $trackPdo->beginTransaction();
        $stmt = $trackPdo->prepare('SELECT notes FROM shifts WHERE id = ? FOR UPDATE');
        $stmt->execute([$shiftId]);
        $shift = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($shift) {
            $shiftNotes = (string) ($shift['notes'] ?? '');
            if (strpos($shiftNotes, $marker) === false) {
                $shiftNotes = rtrim($shiftNotes) . "\n\n" . $note;
            }
            $trackPdo->prepare('UPDATE shifts SET deleted = 1, notes = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
                ->execute([$shiftNotes, 1332, $shiftId]);
        }
        $trackPdo->commit();
    }

    return ['event_id' => $eventId, 'event_name' => $eventName, 'shift_ids' => array_values($shiftIds), 'marker' => $marker];
}

$eventId = (int) (complete_arg_value($argv, '--event-id', '0') ?? '0');
$approvalRef = trim((string) complete_arg_value($argv, '--approval-ref', ''));
$stateDir = rtrim((string) complete_arg_value($argv, '--state-dir', DEFAULT_STATE_DIR), '/');
if ($eventId <= 0 || $approvalRef === '' || !complete_has_flag($argv, '--confirm')) {
    fwrite(STDERR, "Usage: php complete_external_tasting_cancellation.php --event-id ID --approval-ref REF --confirm\n");
    exit(2);
}

$pdo = get_event_pdo();
$stmt = $pdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, event_category, notes, important_information FROM event_bookings WHERE id = ?');
$stmt->execute([$eventId]);
$event = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$event) {
    throw new RuntimeException('OPS event not found.');
}
$rule = complete_cancellation_rule_for_event($event);
if (($rule['channel'] ?? '') !== 'email' || !in_array((string) ($rule['key'] ?? ''), ['marianos', 'binnys'], true)) {
    throw new RuntimeException('Event is not a supported external email cancellation target.');
}
$links = fetch_event_booking_shift_links([$eventId], false)[$eventId] ?? [];
$summary = summarize_event_shift_links($links);
$shiftIds = [];
foreach ($links as $link) {
    if ((int) ($link['deleted'] ?? 0) === 0 && (int) ($link['shift_id'] ?? 0) > 0) {
        $shiftIds[] = (int) $link['shift_id'];
    }
}
$summary['shift_ids'] = array_values(array_unique($shiftIds));
if ((int) ($summary['assigned_shifts'] ?? 0) > 0) {
    throw new RuntimeException('Refusing cancellation because the event now has an assigned active shift.');
}

$start = complete_event_start_datetime($event, new DateTimeZone('America/Chicago'));
$reason = $shiftIds === [] ? 'no linked shift exists at approval time' : 'linked shift is unassigned at approval time';
$actionId = 'approved-' . (string) $rule['key'] . '-external-cancellation-ops' . $eventId . '-' . ($start ? $start->format('Ymd-Hi') : date('Ymd-His'));
$payload = complete_build_cancel_payload($event, $summary, $actionId, new DateTimeImmutable('now', new DateTimeZone('America/Chicago')), $reason, $rule);
$payload['approval_ref'] = $approvalRef;
$payload['task_packet']['approval_ref'] = $approvalRef;
$payload['task_packet']['approval_gates'] = 'Robert approved external cancellation: ' . $approvalRef;
$payload['task_packet']['next_update'] = 'Approved external cancellation draft queued for National Outreach send cycle.';

$draft = complete_queue_payload($stateDir, $payload, $actionId, $eventId, 'queued_approved_external_cancellation_after_owner_approval');
$ops = complete_mark_ops_canceled($eventId, $shiftIds, $approvalRef, (string) $rule['key']);

echo json_encode(['ok' => true, 'draft' => $draft, 'action_id' => $actionId, 'ops' => $ops], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
