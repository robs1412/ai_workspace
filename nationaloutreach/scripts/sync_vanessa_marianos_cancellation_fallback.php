#!/usr/bin/env php
<?php
declare(strict_types=1);

require '/Users/werkstatt/ops/bootstrap.php';

const DEFAULT_STATE_DIR = '/Users/admin/.nationaloutreach-launch/state';
const MARIANOS_CANCEL_TO = 'abseventrequest@abstastings.com';
const MARIANOS_CANCEL_CC = 'rafael@abstastings.com';
const BINNYS_CANCEL_TO = 'rpaquin@binnys.com';

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

function append_jsonl_row(string $path, array $row): void
{
    $dir = dirname($path);
    if (!is_dir($dir)) {
        mkdir($dir, 0700, true);
    }
    file_put_contents($path, json_encode($row, JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND | LOCK_EX);
    chmod($path, 0600);
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
    if ($a !== '' && $b !== '') {
        return $a . ' to ' . $b;
    }
    return $a !== '' ? $a : $b;
}

function safe_slug(string $value): string
{
    $slug = preg_replace('/[^A-Za-z0-9_.-]+/', '-', strtolower(trim($value))) ?? '';
    return trim($slug, '-') !== '' ? trim($slug, '-') : 'tasting-cancellation';
}

function cancellation_rule_for_event(array $event): array
{
    $name = strtolower(trim((string) ($event['event_name'] ?? '')));
    $location = strtolower(trim((string) ($event['event_location'] ?? '')));
    $haystack = $name . ' ' . $location;

    if (str_contains($haystack, 'mariano')) {
        return [
            'key' => 'marianos',
            'label' => "Mariano's",
            'channel' => 'email',
            'to' => [MARIANOS_CANCEL_TO],
            'cc' => [MARIANOS_CANCEL_CC],
            'recipient_label' => 'Adult Beverage Solutions event request; Rafael Morales copied',
            'approval_gates' => "Approved Mariano's cancellation path: use the ABS event-request address and copy Rafael Morales. Cancellation requires prior approval before sending.",
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
            'approval_gates' => "Approved Binny's cancellation path: ask before canceling; with approval, Vanessa can send the cancellation email to Rene Paquin.",
        ];
    }

    if (str_contains($haystack, 'whole foods') || str_contains($haystack, 'wfm')) {
        return [
            'key' => 'whole-foods',
            'label' => 'Whole Foods',
            'channel' => 'manual',
            'manual_rule' => 'Under 24 hours, call the store. With more than 24 hours notice, cancel in the portal.',
        ];
    }

    return [
        'key' => 'unknown',
            'label' => 'unknown account',
        'channel' => 'blocked',
        'manual_rule' => 'No approved cancellation recipient/rule recorded for this event.',
    ];
}

function event_start_datetime(array $event, DateTimeZone $tz): ?DateTimeImmutable
{
    $date = trim((string) ($event['event_date'] ?? ''));
    if ($date === '') {
        return null;
    }
    $time = trim((string) ($event['start_time'] ?? ''));
    if ($time === '') {
        $time = '00:00:00';
    }
    try {
        return new DateTimeImmutable($date . ' ' . $time, $tz);
    } catch (Throwable) {
        return null;
    }
}

function existing_action_refs(string $stateDir): array
{
    $seen = [];
    foreach (load_jsonl_rows($stateDir . '/sent-log.jsonl') as $row) {
        foreach ([
            (string) ($row['action_id'] ?? ''),
            (string) ($row['source_ref'] ?? ''),
            (string) (($row['task_packet'] ?? [])['source_ref'] ?? ''),
            (string) (($row['task_packet'] ?? [])['scheduled_action'] ?? ''),
        ] as $value) {
            if ($value !== '') {
                $seen[strtolower($value)] = true;
            }
        }
    }
    foreach (glob($stateDir . '/outbox/*.approved.json') ?: [] as $path) {
        $seen[strtolower(basename($path, '.approved.json'))] = true;
        $payload = json_decode((string) file_get_contents($path), true);
        if (is_array($payload)) {
            foreach ([
                (string) ($payload['source_ref'] ?? ''),
                (string) (($payload['task_packet'] ?? [])['source_ref'] ?? ''),
                (string) (($payload['task_packet'] ?? [])['scheduled_action'] ?? ''),
            ] as $value) {
                if ($value !== '') {
                    $seen[strtolower($value)] = true;
                }
            }
        }
    }
    foreach (glob($stateDir . '/failed/*.json') ?: [] as $path) {
        $basename = (string) preg_replace('/\.failed-\d+\.json$/', '', basename($path));
        if ($basename !== '') {
            $seen[strtolower($basename)] = true;
        }
        $payload = json_decode((string) file_get_contents($path), true);
        if (is_array($payload)) {
            foreach ([
                (string) ($payload['source_ref'] ?? ''),
                (string) (($payload['task_packet'] ?? [])['source_ref'] ?? ''),
                (string) (($payload['task_packet'] ?? [])['scheduled_action'] ?? ''),
            ] as $value) {
                if ($value !== '') {
                    $seen[strtolower($value)] = true;
                }
            }
        }
    }
    return $seen;
}

function build_cancel_payload(array $event, array $shiftSummary, string $actionId, DateTimeImmutable $now, string $reason, array $rule): array
{
    $eventId = (int) ($event['id'] ?? 0);
    $eventName = trim((string) ($event['event_name'] ?? 'Mariano\'s tasting'));
    $eventDate = (string) ($event['event_date'] ?? '');
    $start = event_start_datetime($event, new DateTimeZone('America/Chicago'));
    $dateLabel = $start ? $start->format('l, F j, Y') : $eventDate;
    $timeLabel = format_time_label((string) ($event['start_time'] ?? ''), (string) ($event['end_time'] ?? ''));
    $location = trim((string) ($event['event_location'] ?? ''));
    $shiftIds = array_values(array_filter(array_map('intval', $shiftSummary['shift_ids'] ?? [])));
    $opsTask = 'OPS event ' . $eventId . ($shiftIds ? ' / TrackTime shift ' . implode(',', $shiftIds) : '');
    $subject = 'Cancellation: KOVAL tasting at ' . $eventName . ' on ' . ($start ? $start->format('l, F j') : $eventDate);

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
        'subject' => $subject,
        'body' => implode("\n", $body),
        'source_ref' => $actionId,
        'task_packet' => [
            'source_ref' => $actionId,
            'dedupe_key' => 'taskflow-' . $actionId,
            'intake_channel' => 'scheduled-action:nationaloutreach',
            'requester' => 'Vanessa Sterling <vanessa.sterling@kovaldistillery.com>',
            'owner_lane' => 'outreach-coordinator',
            'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
            'ops_portal_or_domain_task' => $opsTask,
            'status' => 'working',
            'due_or_trigger' => $now->format('Y-m-d H:i:s T'),
            'scheduled_action' => $actionId,
            'calendar_event' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
            'approval_gates' => (string) ($rule['approval_gates'] ?? 'Approved cancellation path.'),
            'verification_readback' => 'Live OPS readback: ' . $eventName . ' on ' . $eventDate . ' has active linked shifts=' . (int) ($shiftSummary['total_shifts'] ?? 0) . ' and assigned active shifts=' . (int) ($shiftSummary['assigned_shifts'] ?? 0) . '.',
            'next_update' => 'Approved cancellation draft queued for National Outreach send cycle.',
            'requested_deliverable' => 'Cancel ' . (string) ($rule['label'] ?? 'approved') . ' tasting because cancellation fallback condition was met: ' . $reason . '.',
            'human_owner_or_recipient' => (string) ($rule['recipient_label'] ?? 'Approved cancellation recipient'),
            'output_channel' => 'email',
            'proof_required' => 'sent Message-ID plus sent-log readback',
            'owner_question_required' => 'false',
        ],
    ];
}

function queue_payload(string $stateDir, array $payload, string $actionId, int $eventId, string $status): string
{
    $outbox = $stateDir . '/outbox';
    if (!is_dir($outbox)) {
        mkdir($outbox, 0700, true);
    }
    $draftPath = $outbox . '/' . safe_slug($actionId) . '.approved.json';
    file_put_contents($draftPath, json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n", LOCK_EX);
    chmod($draftPath, 0600);
    append_jsonl_row($stateDir . '/scheduled-actions-log.jsonl', [
        'logged_at' => (new DateTimeImmutable('now', new DateTimeZone('America/Chicago')))->format('Y-m-d\TH:i:sO'),
        'action_id' => $actionId,
        'status' => $status,
        'draft' => $draftPath,
        'event_id' => $eventId,
    ]);
    return $draftPath;
}

function load_candidate_events(PDO $pdo, DateTimeImmutable $now, int $hours, ?int $eventId): array
{
    if ($eventId !== null && $eventId > 0) {
        $stmt = $pdo->prepare(
            "SELECT id, event_name, event_date, start_time, end_time, event_location, event_category, notes, important_information
               FROM event_bookings
              WHERE id = ?"
        );
        $stmt->execute([$eventId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    }

    $end = $now->modify('+' . $hours . ' hours');
    $stmt = $pdo->prepare(
        "SELECT id, event_name, event_date, start_time, end_time, event_location, event_category, notes, important_information
           FROM event_bookings
          WHERE event_category = 'Outreach'
            AND event_date BETWEEN ? AND ?
          ORDER BY event_date ASC, COALESCE(NULLIF(start_time, ''), '23:59:59') ASC, id ASC"
    );
    $stmt->execute([$now->format('Y-m-d'), $end->format('Y-m-d')]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
}

$stateDir = rtrim((string) arg_value($argv, '--state-dir', DEFAULT_STATE_DIR), '/');
$queueApproved = has_flag($argv, '--queue-approved');
$hours = max(1, (int) arg_value($argv, '--hours', '24'));
$eventIdRaw = arg_value($argv, '--event-id');
$eventId = $eventIdRaw !== null ? (int) $eventIdRaw : null;
$tz = new DateTimeZone('America/Chicago');
$nowRaw = arg_value($argv, '--now');
$now = $nowRaw ? new DateTimeImmutable($nowRaw, $tz) : new DateTimeImmutable('now', $tz);

$pdo = get_event_pdo();
$events = load_candidate_events($pdo, $now, $hours, $eventId);
$eventIds = array_values(array_filter(array_map(static fn(array $row): int => (int) ($row['id'] ?? 0), $events)));
$linksByEvent = $eventIds ? fetch_event_booking_shift_links($eventIds, false) : [];
$seen = existing_action_refs($stateDir);

$results = [];
$queued = 0;
$eligible = 0;
$blocked = 0;
$skipped = 0;

foreach ($events as $event) {
    $id = (int) ($event['id'] ?? 0);
    $name = trim((string) ($event['event_name'] ?? ''));
    $start = event_start_datetime($event, $tz);
    $links = $linksByEvent[$id] ?? [];
    $summary = summarize_event_shift_links($links);
    $shiftIds = [];
    foreach ($links as $link) {
        if ((int) ($link['deleted'] ?? 0) === 0 && (int) ($link['shift_id'] ?? 0) > 0) {
            $shiftIds[] = (int) $link['shift_id'];
        }
    }
    $summary['shift_ids'] = array_values(array_unique($shiftIds));
    $result = [
        'event_id' => $id,
        'event_name' => $name,
        'event_start' => $start ? $start->format(DateTimeInterface::ATOM) : null,
        'total_shifts' => (int) ($summary['total_shifts'] ?? 0),
        'assigned_shifts' => (int) ($summary['assigned_shifts'] ?? 0),
        'shift_ids' => $summary['shift_ids'],
    ];

    if ($start === null || $start <= $now || $start > $now->modify('+' . $hours . ' hours')) {
        $result['status'] = 'skipped_outside_window';
        $skipped++;
        $results[] = $result;
        continue;
    }
    $rule = cancellation_rule_for_event($event);
    $result['cancellation_rule'] = $rule['key'];
    if (($rule['channel'] ?? '') === 'manual') {
        $result['status'] = 'manual_cancellation_required';
        $result['next_step'] = $rule['manual_rule'];
        $blocked++;
        $results[] = $result;
        continue;
    }
    if (($rule['channel'] ?? '') !== 'email') {
        $result['status'] = 'blocked_missing_cancellation_rule';
        $result['blocker'] = $rule['manual_rule'] ?? 'No approved cancellation recipient/rule recorded for this event.';
        $blocked++;
        $results[] = $result;
        continue;
    }

    $totalShifts = (int) ($summary['total_shifts'] ?? 0);
    $assignedShifts = (int) ($summary['assigned_shifts'] ?? 0);
    $reason = '';

    if ($totalShifts > 0 && $assignedShifts > 0) {
        $result['status'] = 'skipped_covered';
        $skipped++;
        $results[] = $result;
        continue;
    }

    if ($totalShifts <= 0) {
        $reason = 'no linked shift exists inside the 24-hour cancellation window';
        $actionId = 'vanessa-' . (string) $rule['key'] . '-cancellation-no-linked-shift-ops' . $id . '-' . $start->format('Ymd-Hi');
    } else {
        $reason = 'linked shift is unassigned inside the 24-hour cancellation window';
        $actionId = 'vanessa-' . (string) $rule['key'] . '-cancellation-unassigned-linked-shift-ops' . $id . '-' . $start->format('Ymd-Hi');
    }
    $result['action_id'] = $actionId;
    $result['reason'] = $reason;
    if (isset($seen[strtolower($actionId)])) {
        $result['status'] = 'skipped_duplicate';
        $skipped++;
        $results[] = $result;
        continue;
    }

    $eligible++;
    if ($queueApproved) {
        $payload = build_cancel_payload($event, $summary, $actionId, $now, $reason, $rule);
        $draftPath = queue_payload($stateDir, $payload, $actionId, $id, 'queued_approved_cancellation_fallback');
        $result['status'] = 'queued_approved';
        $result['draft'] = $draftPath;
        $queued++;
    } else {
        $result['status'] = 'eligible_dry_run';
    }
    $results[] = $result;
}

echo json_encode([
    'ok' => true,
    'mode' => $queueApproved ? 'queue-approved' : 'dry-run',
    'now' => $now->format(DateTimeInterface::ATOM),
    'window_hours' => $hours,
    'events_checked' => count($events),
    'eligible_email_cancellations_uncovered' => $eligible,
    'queued' => $queued,
    'blocked' => $blocked,
    'skipped' => $skipped,
    'results' => $results,
], JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . "\n";
