#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const TASK_FLOW_DB = 'koval_crm';
const TASK_FLOW_PACKETS = 'ai_task_flow_packets';
const TASK_FLOW_EVENTS = 'ai_task_flow_events';
const TASK_FLOW_TIMEZONE = 'America/Chicago';
const TASK_FLOW_RUNNER_STATE = '/Users/admin/.task-flow-launch/state/task-flow-due-runner-last.json';

date_default_timezone_set(TASK_FLOW_TIMEZONE);

function task_flow_usage(): void
{
    fwrite(STDERR, "Usage: php scripts/task_flow_mysql_recorder.php install|record|status|report|due|projected\n");
}

function task_flow_pdo(): PDO
{
    $pdo = get_event_pdo();
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}

function task_flow_install(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . " (
            dedupe_key varchar(128) NOT NULL,
            source_ref varchar(255) DEFAULT NULL,
            intake_channel varchar(128) DEFAULT NULL,
            requester varchar(255) DEFAULT NULL,
            owner_lane varchar(128) DEFAULT NULL,
            responsible_worker_or_persona varchar(128) DEFAULT NULL,
            workspaceboard_session varchar(128) DEFAULT NULL,
            ops_portal_or_domain_task varchar(128) DEFAULT NULL,
            status varchar(64) NOT NULL,
            due_or_trigger varchar(255) DEFAULT NULL,
            scheduled_action varchar(255) DEFAULT NULL,
            calendar_event varchar(255) DEFAULT NULL,
            clarification_email varchar(255) DEFAULT NULL,
            completion_or_blocker_email varchar(255) DEFAULT NULL,
            source_links text,
            approval_gates text,
            verification_readback text,
            papers_projection varchar(255) DEFAULT NULL,
            next_update text,
            packet_json json NOT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (dedupe_key),
            KEY idx_status (status),
            KEY idx_owner_lane (owner_lane),
            KEY idx_due_or_trigger (due_or_trigger),
            KEY idx_ops_portal_or_domain_task (ops_portal_or_domain_task)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            logged_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event varchar(128) NOT NULL,
            dedupe_key varchar(128) DEFAULT NULL,
            status varchar(64) DEFAULT NULL,
            details_json json NOT NULL,
            PRIMARY KEY (id),
            KEY idx_dedupe_key (dedupe_key),
            KEY idx_event (event),
            KEY idx_logged_at (logged_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
}

function task_flow_string(array $packet, string $key): string
{
    $value = $packet[$key] ?? '';
    if (is_array($value) || is_object($value)) {
        return json_encode($value, JSON_UNESCAPED_SLASHES) ?: '';
    }
    return trim((string) $value);
}

function task_flow_record(PDO $pdo, array $payload): void
{
    task_flow_install($pdo);

    $event = trim((string) ($payload['event'] ?? ''));
    $packet = $payload['packet'] ?? null;
    if ($event === '' || !is_array($packet)) {
        throw new InvalidArgumentException('record payload requires event and packet.');
    }

    $dedupeKey = task_flow_string($packet, 'dedupe_key');
    if ($dedupeKey === '') {
        throw new InvalidArgumentException('packet requires dedupe_key.');
    }
    $missing = task_flow_packet_missing_fields($packet);
    $requestedStatus = task_flow_string($packet, 'status') ?: 'captured';
    if (in_array($requestedStatus, ['completed', 'reported', 'filed'], true) && $missing !== []) {
        $packet['status'] = 'blocked';
        $packet['verification_readback'] = task_flow_string($packet, 'verification_readback') ?: ('task_flow_closeout_guard_missing:' . implode(',', $missing));
        $packet['next_update'] = task_flow_string($packet, 'next_update') ?: 'Complete required task-flow closeout fields before filing/reporting complete.';
        $payload['task_flow_guard'] = [
            'requested_status' => $requestedStatus,
            'missing_fields' => $missing,
            'closeout_allowed' => false,
        ];
    } elseif (task_flow_projection_missing($packet)) {
        $packet['papers_projection'] = task_flow_string($packet, 'papers_projection') ?: 'papers_pending';
        $payload['task_flow_guard'] = [
            'requested_status' => $requestedStatus,
            'missing_fields' => [],
            'closeout_allowed' => true,
            'papers_projection_missing' => true,
        ];
    }

    $packetJson = json_encode($packet, JSON_UNESCAPED_SLASHES);
    $detailsJson = json_encode($payload, JSON_UNESCAPED_SLASHES);
    if ($packetJson === false || $detailsJson === false) {
        throw new RuntimeException('Failed to encode task-flow JSON.');
    }

    $stmt = $pdo->prepare(
        'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' (
            dedupe_key, source_ref, intake_channel, requester, owner_lane,
            responsible_worker_or_persona, workspaceboard_session,
            ops_portal_or_domain_task, status, due_or_trigger,
            scheduled_action, calendar_event, clarification_email,
            completion_or_blocker_email, source_links, approval_gates,
            verification_readback, papers_projection, next_update, packet_json
        ) VALUES (
            :dedupe_key, :source_ref, :intake_channel, :requester, :owner_lane,
            :responsible_worker_or_persona, :workspaceboard_session,
            :ops_portal_or_domain_task, :status, :due_or_trigger,
            :scheduled_action, :calendar_event, :clarification_email,
            :completion_or_blocker_email, :source_links, :approval_gates,
            :verification_readback, :papers_projection, :next_update, :packet_json
        )
        ON DUPLICATE KEY UPDATE
            source_ref = VALUES(source_ref),
            intake_channel = VALUES(intake_channel),
            requester = VALUES(requester),
            owner_lane = VALUES(owner_lane),
            responsible_worker_or_persona = VALUES(responsible_worker_or_persona),
            workspaceboard_session = VALUES(workspaceboard_session),
            ops_portal_or_domain_task = VALUES(ops_portal_or_domain_task),
            status = VALUES(status),
            due_or_trigger = VALUES(due_or_trigger),
            scheduled_action = VALUES(scheduled_action),
            calendar_event = VALUES(calendar_event),
            clarification_email = VALUES(clarification_email),
            completion_or_blocker_email = VALUES(completion_or_blocker_email),
            source_links = VALUES(source_links),
            approval_gates = VALUES(approval_gates),
            verification_readback = VALUES(verification_readback),
            papers_projection = VALUES(papers_projection),
            next_update = VALUES(next_update),
            packet_json = VALUES(packet_json)'
    );
    $stmt->execute([
        ':dedupe_key' => $dedupeKey,
        ':source_ref' => task_flow_string($packet, 'source_ref'),
        ':intake_channel' => task_flow_string($packet, 'intake_channel'),
        ':requester' => task_flow_string($packet, 'requester'),
        ':owner_lane' => task_flow_string($packet, 'owner_lane'),
        ':responsible_worker_or_persona' => task_flow_string($packet, 'responsible_worker_or_persona'),
        ':workspaceboard_session' => task_flow_string($packet, 'workspaceboard_session'),
        ':ops_portal_or_domain_task' => task_flow_string($packet, 'ops_portal_or_domain_task'),
        ':status' => task_flow_string($packet, 'status') ?: 'captured',
        ':due_or_trigger' => task_flow_string($packet, 'due_or_trigger'),
        ':scheduled_action' => task_flow_string($packet, 'scheduled_action'),
        ':calendar_event' => task_flow_string($packet, 'calendar_event'),
        ':clarification_email' => task_flow_string($packet, 'clarification_email'),
        ':completion_or_blocker_email' => task_flow_string($packet, 'completion_or_blocker_email'),
        ':source_links' => task_flow_string($packet, 'source_links'),
        ':approval_gates' => task_flow_string($packet, 'approval_gates'),
        ':verification_readback' => task_flow_string($packet, 'verification_readback'),
        ':papers_projection' => task_flow_string($packet, 'papers_projection'),
        ':next_update' => task_flow_string($packet, 'next_update'),
        ':packet_json' => $packetJson,
    ]);

    $eventStmt = $pdo->prepare(
        'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' (event, dedupe_key, status, details_json)
         VALUES (:event, :dedupe_key, :status, :details_json)'
    );
    $eventStmt->execute([
        ':event' => $event,
        ':dedupe_key' => $dedupeKey,
        ':status' => task_flow_string($packet, 'status') ?: 'captured',
        ':details_json' => $detailsJson,
    ]);
}

function task_flow_packet_missing_fields(array $row): array
{
    $status = trim((string) ($row['status'] ?? ''));
    $missing = [];
    foreach (['source_ref', 'intake_channel', 'owner_lane', 'responsible_worker_or_persona'] as $field) {
        if (trim((string) ($row[$field] ?? '')) === '') {
            $missing[] = $field;
        }
    }

    if (in_array($status, ['task_created', 'scheduled', 'working', 'waiting', 'completed', 'reported', 'filed'], true)
        && trim((string) ($row['ops_portal_or_domain_task'] ?? '')) === '') {
        $missing[] = 'ops_portal_or_domain_task';
    }
    if (in_array($status, ['scheduled', 'waiting'], true)
        && trim((string) ($row['due_or_trigger'] ?? '')) === ''
        && trim((string) ($row['scheduled_action'] ?? '')) === ''
        && trim((string) ($row['calendar_event'] ?? '')) === '') {
        $missing[] = 'due_or_trigger_or_scheduled_action';
    }
    if (in_array($status, ['clarification_sent', 'blocked'], true)
        && !task_flow_is_no_action_closed($row)
        && trim((string) ($row['clarification_email'] ?? '')) === ''
        && trim((string) ($row['completion_or_blocker_email'] ?? '')) === '') {
        $missing[] = 'clarification_or_blocker_email';
    }
    if (in_array($status, ['completed', 'reported', 'filed'], true)
        && trim((string) ($row['verification_readback'] ?? '')) === '') {
        $missing[] = 'verification_readback';
    }
    if (in_array($status, ['reported', 'filed'], true)
        && trim((string) ($row['completion_or_blocker_email'] ?? '')) === '') {
        $missing[] = 'completion_or_blocker_email';
    }
    return array_values(array_unique($missing));
}

function task_flow_is_no_action_closed(array $row): bool
{
    $haystack = strtolower(
        trim((string) ($row['verification_readback'] ?? '')) . ' ' .
        trim((string) ($row['next_update'] ?? '')) . ' ' .
        trim((string) ($row['approval_gates'] ?? ''))
    );
    foreach ([
        'logged-no-action',
        'filed-previously-logged-to-handled',
        'duplicate',
        'already-routed',
        'already-handled',
        'no-action',
        'no_action_logged',
    ] as $marker) {
        if ($marker !== '' && str_contains($haystack, $marker)) {
            return true;
        }
    }
    return false;
}

function task_flow_projection_missing(array $row): bool
{
    $status = trim((string) ($row['status'] ?? ''));
    return in_array($status, ['completed', 'reported', 'filed'], true)
        && trim((string) ($row['papers_projection'] ?? '')) === '';
}

function task_flow_packet_severity(array $row, array $missing): string
{
    $status = trim((string) ($row['status'] ?? ''));
    if (task_flow_is_no_action_closed($row)) {
        return 'closed';
    }
    if ($status === 'blocked') {
        return 'blocked';
    }
    if (in_array($status, ['completed', 'reported', 'filed'], true) && $missing !== []) {
        return 'closeout_gap';
    }
    if ($missing !== []) {
        return 'attention';
    }
    if (task_flow_projection_missing($row)) {
        return 'papers_pending';
    }
    if (in_array($status, ['completed', 'reported', 'filed', 'papers_pending', 'projected'], true)) {
        return 'closed';
    }
    return 'open';
}

function task_flow_report(PDO $pdo, int $limit = 100): array
{
    task_flow_install($pdo);
    $limit = max(1, min(500, $limit));

    $packets = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS)->fetchColumn();
    $events = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS)->fetchColumn();

    $statusRows = $pdo->query(
        'SELECT status, COUNT(*) AS count
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . '
         GROUP BY status
         ORDER BY count DESC, status ASC'
    )->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $ownerRows = $pdo->query(
        'SELECT COALESCE(NULLIF(owner_lane, \'\'), \'unknown\') AS owner_lane, COUNT(*) AS count
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . '
         GROUP BY COALESCE(NULLIF(owner_lane, \'\'), \'unknown\')
         ORDER BY count DESC, owner_lane ASC'
    )->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $stmt = $pdo->prepare(
        'SELECT p.*,
            (SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key) AS event_count,
            (SELECT MAX(e.logged_at) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key) AS latest_event_at,
            (SELECT e.event FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key ORDER BY e.logged_at DESC, e.id DESC LIMIT 1) AS latest_event
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p
         ORDER BY p.updated_at DESC
         LIMIT :limit'
    );
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $items = [];
    $severityCounts = [];
    $missingFieldCounts = [];
    foreach ($rows as $row) {
        $missing = task_flow_packet_missing_fields($row);
        $severity = task_flow_packet_severity($row, $missing);
        $severityCounts[$severity] = ($severityCounts[$severity] ?? 0) + 1;
        foreach ($missing as $field) {
            $missingFieldCounts[$field] = ($missingFieldCounts[$field] ?? 0) + 1;
        }
        $items[] = [
            'dedupe_key' => (string) ($row['dedupe_key'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'intake_channel' => (string) ($row['intake_channel'] ?? ''),
            'requester' => (string) ($row['requester'] ?? ''),
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
            'responsible_worker_or_persona' => (string) ($row['responsible_worker_or_persona'] ?? ''),
            'workspaceboard_session' => (string) ($row['workspaceboard_session'] ?? ''),
            'ops_portal_or_domain_task' => (string) ($row['ops_portal_or_domain_task'] ?? ''),
            'status' => (string) ($row['status'] ?? ''),
            'due_or_trigger' => (string) ($row['due_or_trigger'] ?? ''),
            'scheduled_action' => (string) ($row['scheduled_action'] ?? ''),
            'calendar_event' => (string) ($row['calendar_event'] ?? ''),
            'clarification_email' => (string) ($row['clarification_email'] ?? ''),
            'completion_or_blocker_email' => (string) ($row['completion_or_blocker_email'] ?? ''),
            'verification_readback' => (string) ($row['verification_readback'] ?? ''),
            'papers_projection' => (string) ($row['papers_projection'] ?? ''),
            'next_update' => (string) ($row['next_update'] ?? ''),
            'updated_at' => (string) ($row['updated_at'] ?? ''),
            'created_at' => (string) ($row['created_at'] ?? ''),
            'latest_event' => (string) ($row['latest_event'] ?? ''),
            'latest_event_at' => (string) ($row['latest_event_at'] ?? ''),
            'event_count' => (int) ($row['event_count'] ?? 0),
            'missing_fields' => $missing,
            'papers_projection_missing' => task_flow_projection_missing($row),
            'effective_status' => task_flow_is_no_action_closed($row) ? 'no_action_closed' : (string) ($row['status'] ?? ''),
            'severity' => $severity,
        ];
    }

    $closeoutIssues = 0;
    $openItems = 0;
    foreach ($items as $item) {
        if (in_array($item['severity'], ['closeout_gap', 'attention', 'blocked'], true)) {
            $closeoutIssues++;
        }
        if (in_array($item['severity'], ['open', 'attention', 'blocked'], true)) {
            $openItems++;
        }
    }

    ksort($missingFieldCounts);
    ksort($severityCounts);

    $runnerState = task_flow_runner_state();
    $duePreview = task_flow_due_report($pdo, 10);
    $upcomingPreview = task_flow_upcoming_report($pdo, 10);

    return [
        'ok' => true,
        'database' => TASK_FLOW_DB,
        'generated_at' => date(DATE_ATOM),
        'limit' => $limit,
        'totals' => [
            'packets' => $packets,
            'events' => $events,
            'shown' => count($items),
            'open_items_shown' => $openItems,
            'closeout_issues_shown' => $closeoutIssues,
        ],
        'status_counts' => array_map(static fn(array $row): array => [
            'status' => (string) ($row['status'] ?? ''),
            'count' => (int) ($row['count'] ?? 0),
        ], $statusRows),
        'owner_counts' => array_map(static fn(array $row): array => [
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
            'count' => (int) ($row['count'] ?? 0),
        ], $ownerRows),
        'severity_counts' => $severityCounts,
        'missing_field_counts' => $missingFieldCounts,
        'reminder_runner' => $runnerState,
        'due_preview' => [
            'due_count' => $duePreview['due_count'] ?? 0,
            'items' => $duePreview['items'] ?? [],
        ],
        'upcoming_preview' => [
            'upcoming_count' => $upcomingPreview['upcoming_count'] ?? 0,
            'items' => $upcomingPreview['items'] ?? [],
        ],
        'items' => $items,
    ];
}

function task_flow_runner_state(): array
{
    if (!is_readable(TASK_FLOW_RUNNER_STATE)) {
        return [
            'available' => false,
            'path' => TASK_FLOW_RUNNER_STATE,
            'message' => 'No due-runner state file has been written yet.',
        ];
    }
    $raw = file_get_contents(TASK_FLOW_RUNNER_STATE);
    $decoded = is_string($raw) ? json_decode($raw, true) : null;
    if (!is_array($decoded)) {
        return [
            'available' => false,
            'path' => TASK_FLOW_RUNNER_STATE,
            'message' => 'Due-runner state file is not valid JSON.',
        ];
    }
    return [
        'available' => true,
        'path' => TASK_FLOW_RUNNER_STATE,
        'checked_at' => (string) ($decoded['checked_at'] ?? ''),
        'due_count' => (int) ($decoded['due_count'] ?? 0),
        'recorded' => (int) ($decoded['recorded'] ?? 0),
        'skipped_existing' => (int) ($decoded['skipped_existing'] ?? 0),
        'actions' => is_array($decoded['actions'] ?? null) ? $decoded['actions'] : [],
        'notification' => is_array($decoded['notification'] ?? null) ? $decoded['notification'] : [],
    ];
}

function task_flow_due_report(PDO $pdo, int $limit = 100): array
{
    task_flow_install($pdo);
    $limit = max(1, min(500, $limit));
    $now = (new DateTimeImmutable('now', new DateTimeZone(TASK_FLOW_TIMEZONE)))->format('Y-m-d H:i:s');
    $stmt = $pdo->prepare(
        'SELECT *
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
         WHERE status IN ('scheduled', 'waiting')
           AND due_or_trigger IS NOT NULL
           AND due_or_trigger <> ''
           AND due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'
           AND due_or_trigger <= :now
         ORDER BY due_or_trigger ASC, updated_at ASC
         LIMIT :limit"
    );
    $stmt->bindValue(':now', $now, PDO::PARAM_STR);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    return [
        'ok' => true,
        'database' => TASK_FLOW_DB,
        'generated_at' => date(DATE_ATOM),
        'limit' => $limit,
        'due_count' => count($rows),
        'items' => array_map(static fn(array $row): array => [
            'dedupe_key' => (string) ($row['dedupe_key'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
            'responsible_worker_or_persona' => (string) ($row['responsible_worker_or_persona'] ?? ''),
            'status' => (string) ($row['status'] ?? ''),
            'due_or_trigger' => (string) ($row['due_or_trigger'] ?? ''),
            'scheduled_action' => (string) ($row['scheduled_action'] ?? ''),
            'calendar_event' => (string) ($row['calendar_event'] ?? ''),
            'workspaceboard_session' => (string) ($row['workspaceboard_session'] ?? ''),
            'ops_portal_or_domain_task' => (string) ($row['ops_portal_or_domain_task'] ?? ''),
            'next_update' => (string) ($row['next_update'] ?? ''),
        ], $rows),
    ];
}

function task_flow_upcoming_report(PDO $pdo, int $limit = 100): array
{
    task_flow_install($pdo);
    $limit = max(1, min(500, $limit));
    $now = (new DateTimeImmutable('now', new DateTimeZone(TASK_FLOW_TIMEZONE)))->format('Y-m-d H:i:s');
    $stmt = $pdo->prepare(
        'SELECT *
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
         WHERE status IN ('scheduled', 'waiting')
           AND due_or_trigger IS NOT NULL
           AND due_or_trigger <> ''
           AND due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'
           AND due_or_trigger >= :now
         ORDER BY due_or_trigger ASC, updated_at ASC
         LIMIT :limit"
    );
    $stmt->bindValue(':now', $now, PDO::PARAM_STR);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    return [
        'ok' => true,
        'database' => TASK_FLOW_DB,
        'generated_at' => date(DATE_ATOM),
        'limit' => $limit,
        'upcoming_count' => count($rows),
        'items' => array_map(static fn(array $row): array => [
            'dedupe_key' => (string) ($row['dedupe_key'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
            'responsible_worker_or_persona' => (string) ($row['responsible_worker_or_persona'] ?? ''),
            'status' => (string) ($row['status'] ?? ''),
            'due_or_trigger' => (string) ($row['due_or_trigger'] ?? ''),
            'scheduled_action' => (string) ($row['scheduled_action'] ?? ''),
            'calendar_event' => (string) ($row['calendar_event'] ?? ''),
            'workspaceboard_session' => (string) ($row['workspaceboard_session'] ?? ''),
            'ops_portal_or_domain_task' => (string) ($row['ops_portal_or_domain_task'] ?? ''),
            'next_update' => (string) ($row['next_update'] ?? ''),
        ], $rows),
    ];
}

function task_flow_mark_projected(PDO $pdo, string $dedupeKey, string $projectionRef): void
{
    task_flow_install($pdo);
    if ($dedupeKey === '' || $projectionRef === '') {
        throw new InvalidArgumentException('projected command requires dedupe key and projection ref.');
    }
    $stmt = $pdo->prepare(
        'UPDATE ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
         SET status = 'projected', papers_projection = :projection_ref
         WHERE dedupe_key = :dedupe_key"
    );
    $stmt->execute([':projection_ref' => $projectionRef, ':dedupe_key' => $dedupeKey]);
    $eventStmt = $pdo->prepare(
        'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . " (event, dedupe_key, status, details_json)
         VALUES ('papers_projected', :dedupe_key, 'projected', :details_json)"
    );
    $eventStmt->execute([
        ':dedupe_key' => $dedupeKey,
        ':details_json' => json_encode(['event' => 'papers_projected', 'dedupe_key' => $dedupeKey, 'papers_projection' => $projectionRef], JSON_UNESCAPED_SLASHES),
    ]);
}

$command = $argv[1] ?? '';
if (!in_array($command, ['install', 'record', 'status', 'report', 'due', 'projected'], true)) {
    task_flow_usage();
    exit(2);
}

try {
    $pdo = task_flow_pdo();
    if ($command === 'install') {
        task_flow_install($pdo);
        echo json_encode(['ok' => true, 'installed' => true, 'database' => TASK_FLOW_DB], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'status') {
        task_flow_install($pdo);
        $packets = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS)->fetchColumn();
        $events = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS)->fetchColumn();
        echo json_encode(['ok' => true, 'database' => TASK_FLOW_DB, 'packets' => $packets, 'events' => $events], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'report') {
        $limit = isset($argv[2]) ? (int) $argv[2] : 100;
        echo json_encode(task_flow_report($pdo, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'due') {
        $limit = isset($argv[2]) ? (int) $argv[2] : 100;
        echo json_encode(task_flow_due_report($pdo, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'projected') {
        task_flow_mark_projected($pdo, trim((string) ($argv[2] ?? '')), trim((string) ($argv[3] ?? '')));
        echo json_encode(['ok' => true], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }

    $stdin = stream_get_contents(STDIN);
    $payload = json_decode($stdin === false ? '' : $stdin, true);
    if (!is_array($payload)) {
        throw new InvalidArgumentException('record command requires JSON object on stdin.');
    }
    task_flow_record($pdo, $payload);
    echo json_encode(['ok' => true], JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit(0);
} catch (Throwable $e) {
    fwrite(STDERR, $e->getMessage() . PHP_EOL);
    exit(1);
}
