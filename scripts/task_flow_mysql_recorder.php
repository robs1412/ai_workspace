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
    fwrite(STDERR, "Usage: php scripts/task_flow_mysql_recorder.php install|record|status|report|due|projected|validate|archive-safe|archive-watchdog-history|archive-stale-routed-proof-backed\n");
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
            archived_at timestamp NULL DEFAULT NULL,
            archive_reason varchar(255) DEFAULT NULL,
            archive_batch varchar(128) DEFAULT NULL,
            packet_json json NOT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (dedupe_key),
            KEY idx_status (status),
            KEY idx_owner_lane (owner_lane),
            KEY idx_due_or_trigger (due_or_trigger),
            KEY idx_archived_at (archived_at),
            KEY idx_ops_portal_or_domain_task (ops_portal_or_domain_task)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
    task_flow_ensure_column($pdo, TASK_FLOW_PACKETS, 'archived_at', 'timestamp NULL DEFAULT NULL');
    task_flow_ensure_column($pdo, TASK_FLOW_PACKETS, 'archive_reason', 'varchar(255) DEFAULT NULL');
    task_flow_ensure_column($pdo, TASK_FLOW_PACKETS, 'archive_batch', 'varchar(128) DEFAULT NULL');
    task_flow_ensure_index($pdo, TASK_FLOW_PACKETS, 'idx_archived_at', 'archived_at');

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

function task_flow_ensure_column(PDO $pdo, string $table, string $column, string $definition): void
{
    $stmt = $pdo->prepare(
        'SELECT COUNT(*)
         FROM information_schema.COLUMNS
         WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table AND COLUMN_NAME = :column'
    );
    $stmt->execute([':schema' => TASK_FLOW_DB, ':table' => $table, ':column' => $column]);
    if ((int) $stmt->fetchColumn() === 0) {
        $pdo->exec('ALTER TABLE ' . TASK_FLOW_DB . '.' . $table . ' ADD COLUMN ' . $column . ' ' . $definition);
    }
}

function task_flow_ensure_index(PDO $pdo, string $table, string $index, string $column): void
{
    $stmt = $pdo->prepare(
        'SELECT COUNT(*)
         FROM information_schema.STATISTICS
         WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table AND INDEX_NAME = :index_name'
    );
    $stmt->execute([':schema' => TASK_FLOW_DB, ':table' => $table, ':index_name' => $index]);
    if ((int) $stmt->fetchColumn() === 0) {
        $pdo->exec('ALTER TABLE ' . TASK_FLOW_DB . '.' . $table . ' ADD KEY ' . $index . ' (' . $column . ')');
    }
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
    if (in_array($requestedStatus, ['completed', 'handled', 'reported', 'filed'], true) && $missing !== []) {
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

    $preserveExistingPacket = task_flow_should_preserve_existing_packet($pdo, $dedupeKey, $packet);
    if ($preserveExistingPacket) {
        $payload['task_flow_guard'] = [
            ...($payload['task_flow_guard'] ?? []),
            'preserved_existing_packet' => true,
            'reason' => 'weaker_monitor_event_cannot_overwrite_closeout_or_blocker',
            'requested_status' => task_flow_string($packet, 'status') ?: 'captured',
        ];
        $detailsJson = json_encode($payload, JSON_UNESCAPED_SLASHES);
        if ($detailsJson === false) {
            throw new RuntimeException('Failed to encode task-flow JSON.');
        }
    }

    if (!$preserveExistingPacket) {
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
    }

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

function task_flow_should_preserve_existing_packet(PDO $pdo, string $dedupeKey, array $incomingPacket): bool
{
    $incomingStatus = strtolower(task_flow_string($incomingPacket, 'status') ?: 'captured');
    if (!in_array($incomingStatus, ['captured', 'captured_backlog', 'classified', 'routed', 'working'], true)) {
        return false;
    }
    if (task_flow_string($incomingPacket, 'completion_or_blocker_email') !== '') {
        return false;
    }
    $stmt = $pdo->prepare(
        'SELECT status, completion_or_blocker_email, verification_readback, next_update
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . '
         WHERE dedupe_key = :dedupe_key
         LIMIT 1'
    );
    $stmt->execute([':dedupe_key' => $dedupeKey]);
    $existing = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($existing)) {
        return false;
    }
    $existingStatus = strtolower(trim((string) ($existing['status'] ?? '')));
    $existingProof = trim((string) ($existing['completion_or_blocker_email'] ?? ''));
    $existingText = strtolower(implode("\n", [
        (string) ($existing['verification_readback'] ?? ''),
        (string) ($existing['next_update'] ?? ''),
    ]));
    if (in_array($existingStatus, ['completed', 'handled', 'reported', 'filed'], true) && ($existingProof !== '' || str_contains($existingText, 'message-id'))) {
        return true;
    }
    if ($existingStatus === 'blocked' && ($existingProof !== '' || str_contains($existingText, 'missing_fact') || str_contains($existingText, 'exact blocker'))) {
        return true;
    }
    if (str_contains($existingText, 'logged-no-action') || str_contains($existingText, 'no-action') || str_contains($existingText, 'closed with proof')) {
        return true;
    }
    return false;
}

function task_flow_packet_missing_fields(array $row): array
{
    $status = task_flow_normalized_status($row);
    $missing = task_flow_finish_contract_missing_fields($row);
    foreach (['source_ref', 'intake_channel', 'owner_lane', 'responsible_worker_or_persona'] as $field) {
        if (trim((string) ($row[$field] ?? '')) === '') {
            $missing[] = $field;
        }
    }

    if (in_array($status, ['task_created', 'scheduled', 'working', 'waiting', 'completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof'], true)
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
        && !task_flow_has_handled_filing_marker($row)
        && trim((string) ($row['clarification_email'] ?? '')) === ''
        && trim((string) ($row['completion_or_blocker_email'] ?? '')) === '') {
        $missing[] = 'clarification_or_blocker_email';
    }
    if (in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof', 'review_ready'], true)
        && trim((string) ($row['verification_readback'] ?? '')) === '') {
        $missing[] = 'verification_readback';
    }
    if (in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof', 'review_ready'], true)
        && !task_flow_closeout_has_proof_marker($row)) {
        $missing[] = 'closeout_proof_marker';
    }
    if (in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof'], true)
        && task_flow_closeout_email_still_in_inbox($row)) {
        $missing[] = 'source_email_still_in_inbox';
    }
    if (task_flow_routed_past_next_check($row)) {
        $missing[] = 'past_next_check_still_routed';
    }
    if (task_flow_vague_robert_decision($row)) {
        $missing[] = 'vague_robert_decision';
    }
    if (in_array($status, ['reported', 'filed'], true)
        && trim((string) ($row['completion_or_blocker_email'] ?? '')) === '') {
        $missing[] = 'completion_or_blocker_email';
    }
    if (task_flow_has_handled_filing_marker($row)
        && !task_flow_has_owner_visible_or_no_action_proof($row)) {
        $missing[] = 'owner_visible_completion_or_blocker_missing_after_handled_filing';
    }
    return array_values(array_unique($missing));
}

function task_flow_finish_contract_missing_fields(array $row): array
{
    $missing = [];
    $packet = task_flow_packet_json($row);
    $checks = [
        'requested_deliverable' => [
            ['packet', 'requested_deliverable'],
            ['packet', 'deliverable'],
            ['packet', 'expected_output'],
        ],
        'responsible_worker_or_persona' => [
            ['row', 'responsible_worker_or_persona'],
            ['packet', 'responsible_worker'],
            ['packet', 'responsible_persona'],
        ],
        'human_owner_or_recipient' => [
            ['packet', 'human_owner_or_recipient'],
            ['packet', 'human_owner'],
            ['packet', 'recipient'],
            ['packet', 'completion_report_recipient'],
            ['row', 'requester'],
        ],
        'output_channel' => [
            ['packet', 'output_channel'],
            ['packet', 'completion_output_channel'],
            ['packet', 'closeout_channel'],
        ],
        'proof_required' => [
            ['packet', 'proof_required'],
            ['packet', 'required_proof'],
            ['packet', 'proof_marker_required'],
        ],
        'due_or_next_update' => [
            ['row', 'due_or_trigger'],
            ['row', 'next_update'],
            ['row', 'scheduled_action'],
            ['packet', 'due_or_next_update'],
            ['packet', 'next_update_time'],
        ],
        'escalation_path' => [
            ['packet', 'escalation_path'],
            ['packet', 'escalation_if_incomplete'],
            ['packet', 'if_not_complete_on_time'],
        ],
    ];
    foreach ($checks as $field => $sources) {
        if (!task_flow_any_source_has_value($row, $packet, $sources)
            && task_flow_default_finish_contract_value($row, $packet, $field) === '') {
            $missing[] = $field;
        }
    }
    return $missing;
}

function task_flow_default_finish_contract_value(array $row, array $packet, string $field): string
{
    $emailDerived = task_flow_is_email_derived_packet($row, $packet);
    $worker = strtolower(trim((string) ($row['responsible_worker_or_persona'] ?? $packet['responsible_worker_or_persona'] ?? '')));
    $ownerLane = strtolower(trim((string) ($row['owner_lane'] ?? $packet['owner_lane'] ?? '')));
    return match ($field) {
        'requested_deliverable' => trim((string) ($row['next_update'] ?? $packet['next_update'] ?? '')) !== ''
            ? (string) ($row['next_update'] ?? $packet['next_update'])
            : (trim((string) ($row['source_links'] ?? $packet['source_links'] ?? $row['ops_portal_or_domain_task'] ?? '')) !== ''
                ? (string) ($row['source_links'] ?? $packet['source_links'] ?? $row['ops_portal_or_domain_task'])
                : 'Complete the requested work or return one exact blocker.'),
        'human_owner_or_recipient' => trim((string) ($row['requester'] ?? $packet['requester'] ?? $packet['owner'] ?? $packet['human_owner'] ?? $packet['recipient'] ?? '')) !== ''
            ? (string) ($row['requester'] ?? $packet['requester'] ?? $packet['owner'] ?? $packet['human_owner'] ?? $packet['recipient'])
            : 'Robert / requesting owner',
        'output_channel' => $emailDerived
            ? 'owner-visible email or Task Flow blocker readback'
            : 'Task Flow readback, owner-visible email, or domain artifact',
        'proof_required' => task_flow_default_proof_required($worker, $ownerLane),
        'due_or_next_update' => 'first check within 2 minutes; result email, owner question, or exact blocker within 5 minutes',
        'escalation_path' => 'Task Manager repair at 5 minutes; AI Health escalation at 10 minutes; no handled/filed closeout without Message-ID or explicit no-action proof.',
        default => '',
    };
}

function task_flow_is_email_derived_packet(array $row, array $packet): bool
{
    $haystack = strtolower(implode(' ', [
        (string) ($row['intake_channel'] ?? ''),
        (string) ($packet['intake_channel'] ?? ''),
        (string) ($row['source_ref'] ?? ''),
        (string) ($packet['source_ref'] ?? ''),
        (string) ($row['latest_event'] ?? ''),
    ]));
    return str_contains($haystack, 'email')
        || str_contains($haystack, 'gmail')
        || str_contains($haystack, 'nationaloutreach');
}

function task_flow_default_proof_required(string $worker, string $ownerLane): string
{
    $haystack = $worker . ' ' . $ownerLane;
    if (str_contains($haystack, 'ezra')) {
        return 'Ezra owner-visible email Message-ID, document/artifact link, or one exact blocker';
    }
    if (str_contains($haystack, 'vanessa') || str_contains($haystack, 'outreach')) {
        return 'OPS/calendar/event readback, owner-visible email Message-ID, or one exact blocker';
    }
    if (str_contains($haystack, 'naomi') || str_contains($haystack, 'finance')) {
        return 'Naomi owner-visible email Message-ID, finance readback, or one exact blocker';
    }
    return 'owner-visible completion email Message-ID, durable readback, changed file/artifact path, domain ID, or one exact blocker';
}

function task_flow_packet_json(array $row): array
{
    $raw = $row['packet_json'] ?? [];
    if (is_array($raw)) {
        return $raw;
    }
    if (!is_string($raw) || trim($raw) === '') {
        return [];
    }
    $decoded = json_decode($raw, true);
    return is_array($decoded) ? $decoded : [];
}

function task_flow_any_source_has_value(array $row, array $packet, array $sources): bool
{
    foreach ($sources as $source) {
        [$scope, $key] = $source;
        $value = $scope === 'row' ? ($row[$key] ?? '') : ($packet[$key] ?? '');
        if (is_array($value) || is_object($value)) {
            if ($value !== []) {
                return true;
            }
            continue;
        }
        if (trim((string) $value) !== '') {
            return true;
        }
    }
    return false;
}

function task_flow_normalized_status(array $row): string
{
    $status = strtolower(trim((string) ($row['status'] ?? '')));
    $status = str_replace('-', '_', $status);
    return match ($status) {
        'complete', 'done' => 'completed',
        'reviewready' => 'review_ready',
        'closed_withproof' => 'closed_with_proof',
        default => $status,
    };
}

function task_flow_first_source_value(array $row, array $packet, array $sources): string
{
    foreach ($sources as $source) {
        [$scope, $key] = $source;
        $value = $scope === 'row' ? ($row[$key] ?? '') : ($packet[$key] ?? '');
        if (is_array($value) || is_object($value)) {
            $value = json_encode($value, JSON_UNESCAPED_SLASHES) ?: '';
        }
        $value = trim((string) $value);
        if ($value !== '') {
            return $value;
        }
    }
    return '';
}

function task_flow_normalize_recurrence_cadence(string $value): string
{
    $value = trim($value);
    if ($value === '') {
        return '';
    }

    $normalized = strtolower(preg_replace('/[\s_-]+/', ' ', $value) ?? $value);
    if (preg_match('/\bcontinuous\b|\bstanding\b/', $normalized)) {
        return 'Continuous';
    }
    if (preg_match('/\bweekday(s)?\b|\bmonday through friday\b|\bmon fri\b|\bmon-fri\b/', $normalized)) {
        return 'Weekdays';
    }
    if (preg_match('/\bdaily\b|\bevery day\b|\beach day\b/', $normalized)) {
        return 'Daily';
    }
    if (preg_match('/\bweekly\b|\bevery week\b|\beach week\b/', $normalized)) {
        return 'Weekly';
    }
    if (preg_match('/\bmonthly\b|\bevery month\b|\beach month\b/', $normalized)) {
        return 'Monthly';
    }
    if (preg_match('/\bquarterly\b|\bevery quarter\b/', $normalized)) {
        return 'Quarterly';
    }
    if (preg_match('/\bhourly\b|\bevery hour\b/', $normalized)) {
        return 'Hourly';
    }
    if (preg_match('/\bad hoc\b|\bon demand\b/', $normalized)) {
        return 'Ad Hoc';
    }

    return ucwords($normalized);
}

function task_flow_infer_recurrence_cadence(string $text): string
{
    $text = strtolower($text);
    if (preg_match('/\bcontinuous\b|\bstanding\b/', $text)) {
        return 'Continuous';
    }
    if (preg_match('/\bweekday(s)?\b|\bmonday through friday\b|\bmon[ -]?fri\b/', $text)) {
        return 'Weekdays';
    }
    if (preg_match('/\bdaily\b|\bevery day\b|\beach day\b/', $text)) {
        return 'Daily';
    }
    if (preg_match('/\bweekly\b|\bevery week\b|\beach week\b/', $text)) {
        return 'Weekly';
    }
    if (preg_match('/\bmonthly\b|\bevery month\b|\beach month\b/', $text)) {
        return 'Monthly';
    }
    if (preg_match('/\bquarterly\b|\bevery quarter\b/', $text)) {
        return 'Quarterly';
    }
    if (preg_match('/\bhourly\b|\bevery hour\b/', $text)) {
        return 'Hourly';
    }
    if (preg_match('/\breminder\b|\bscheduled\b|\bschedule\b|\bnext update\b|\bnext run\b/', $text)) {
        return 'Ad Hoc';
    }
    return '';
}

function task_flow_recurrence_data(array $row): array
{
    $packet = task_flow_packet_json($row);
    $text = strtolower(implode(' ', [
        (string) ($row['owner_lane'] ?? ''),
        (string) ($row['responsible_worker_or_persona'] ?? ''),
        (string) ($row['status'] ?? ''),
        (string) ($row['due_or_trigger'] ?? ''),
        (string) ($row['scheduled_action'] ?? ''),
        (string) ($row['calendar_event'] ?? ''),
        (string) ($row['next_update'] ?? ''),
        (string) ($row['latest_event'] ?? ''),
        (string) ($packet['dedupe_key'] ?? ''),
    ]));

    $parentPacketIdRaw = task_flow_first_source_value($row, $packet, [
        ['row', 'parent_packet_id'],
        ['packet', 'parent_packet_id'],
        ['row', 'recurrence_parent_packet_id'],
        ['packet', 'recurrence_parent_packet_id'],
        ['row', 'recurrence_parent_id'],
        ['packet', 'recurrence_parent_id'],
    ]);
    $parentPacketId = preg_match('/^\d+$/', $parentPacketIdRaw) ? $parentPacketIdRaw : '';

    $parentPacketDedupeKey = task_flow_first_source_value($row, $packet, [
        ['row', 'parent_packet_dedupe_key'],
        ['packet', 'parent_packet_dedupe_key'],
        ['row', 'recurrence_parent_dedupe_key'],
        ['packet', 'recurrence_parent_dedupe_key'],
    ]);

    $cadenceRaw = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_cadence'],
        ['packet', 'recurrence_cadence'],
        ['row', 'cadence'],
        ['packet', 'cadence'],
        ['row', 'recurring_type'],
        ['packet', 'recurring_type'],
        ['row', 'recurrence_type'],
        ['packet', 'recurrence_type'],
    ]);
    $cadence = task_flow_normalize_recurrence_cadence($cadenceRaw);
    if ($cadence === '') {
        $cadence = task_flow_infer_recurrence_cadence($text);
    }

    $pattern = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_pattern'],
        ['packet', 'recurrence_pattern'],
        ['row', 'recurrence_rule'],
        ['packet', 'recurrence_rule'],
        ['row', 'rrule'],
        ['packet', 'rrule'],
        ['row', 'recurrence_text'],
        ['packet', 'recurrence_text'],
    ]);

    $rule = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_rule_text'],
        ['packet', 'recurrence_rule_text'],
        ['row', 'recurrence_rule'],
        ['packet', 'recurrence_rule'],
        ['row', 'rule'],
        ['packet', 'rule'],
    ]);

    $anchor = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_anchor'],
        ['packet', 'recurrence_anchor'],
        ['row', 'recurrence_start'],
        ['packet', 'recurrence_start'],
        ['row', 'recurrence_start_at'],
        ['packet', 'recurrence_start_at'],
    ]);
    if ($anchor === '') {
        $anchor = task_flow_first_source_value($row, $packet, [
            ['row', 'due_or_trigger'],
            ['packet', 'due_or_trigger'],
            ['row', 'scheduled_action'],
            ['packet', 'scheduled_action'],
        ]);
    }

    $until = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_until'],
        ['packet', 'recurrence_until'],
    ]);

    $interval = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_interval'],
        ['packet', 'recurrence_interval'],
    ]);

    $time = task_flow_first_source_value($row, $packet, [
        ['row', 'recurrence_time'],
        ['packet', 'recurrence_time'],
        ['row', 'time'],
        ['packet', 'time'],
    ]);
    if ($time === '') {
        $due = task_flow_first_source_value($row, $packet, [
            ['row', 'due_or_trigger'],
            ['packet', 'due_or_trigger'],
        ]);
        if ($due !== '') {
            try {
                $date = new DateTimeImmutable($due, new DateTimeZone(TASK_FLOW_TIMEZONE));
                $time = $date->format('g:i A');
            } catch (Throwable) {
                $time = '';
            }
        }
    }

    $enabled = $parentPacketId !== ''
        || $parentPacketDedupeKey !== ''
        || $cadence !== ''
        || $pattern !== ''
        || $rule !== ''
        || $time !== ''
        || task_flow_infer_recurrence_cadence($text) !== '';

    $kind = strtolower(str_replace([' ', '/'], '_', $cadence));
    if ($kind === '') {
        $kind = $enabled ? 'recurring' : '';
    }

    $summaryParts = [];
    if ($parentPacketId !== '') {
        $summaryParts[] = 'parent #' . $parentPacketId;
    } elseif ($parentPacketDedupeKey !== '') {
        $summaryParts[] = 'parent key ' . $parentPacketDedupeKey;
    }
    if ($cadence !== '') {
        $summaryParts[] = $cadence;
    }
    if ($pattern !== '' && $pattern !== $cadence) {
        $summaryParts[] = $pattern;
    } elseif ($rule !== '' && $rule !== $cadence && $rule !== $pattern) {
        $summaryParts[] = $rule;
    }
    if ($time !== '') {
        $summaryParts[] = $time;
    }
    if ($anchor !== '' && !in_array($anchor, $summaryParts, true)) {
        $summaryParts[] = 'anchor ' . $anchor;
    }
    if ($until !== '') {
        $summaryParts[] = 'until ' . $until;
    }

    return [
        'enabled' => $enabled,
        'kind' => $kind,
        'parent_packet_id' => $parentPacketId,
        'parent_packet_dedupe_key' => $parentPacketDedupeKey,
        'cadence' => $cadence,
        'pattern' => $pattern,
        'rule' => $rule,
        'anchor' => $anchor,
        'until' => $until,
        'interval' => $interval,
        'time' => $time,
        'summary' => implode(' · ', $summaryParts),
    ];
}

function task_flow_closeout_has_proof_marker(array $row): bool
{
    if (task_flow_is_no_action_closed($row)) {
        return true;
    }
    if (task_flow_normalized_status($row) === 'review_ready') {
        return false;
    }
    if (task_flow_has_handled_filing_marker($row)) {
        return false;
    }
    $packet = task_flow_packet_json($row);
    if (task_flow_has_sent_proof($row)) {
        return true;
    }
    foreach (['proof', 'proof_marker', 'message_id', 'no_action_reason'] as $field) {
        if (task_flow_non_pending_value((string) ($packet[$field] ?? '')) !== '') {
            return true;
        }
    }
    foreach (['file_path', 'artifact_path', 'sheet_range'] as $field) {
        if (task_flow_non_pending_value((string) ($packet[$field] ?? '')) !== ''
            && task_flow_has_result_readback($row)) {
            return true;
        }
    }
    foreach ([
        (string) ($row['ops_portal_or_domain_task'] ?? ''),
        (string) ($packet['task_id'] ?? ''),
        (string) ($packet['portal_id'] ?? ''),
        (string) ($packet['ops_id'] ?? ''),
    ] as $value) {
        if (task_flow_non_pending_value($value) !== '' && task_flow_has_domain_result_readback($row)) {
            return true;
        }
    }
    return false;
}

function task_flow_has_sent_proof(array $row): bool
{
    $packet = task_flow_packet_json($row);
    $text = strtolower(implode(' ', [
        (string) ($row['completion_or_blocker_email'] ?? ''),
        (string) ($row['verification_readback'] ?? ''),
        (string) ($row['next_update'] ?? ''),
        (string) ($packet['completion_or_blocker_email'] ?? ''),
        (string) ($packet['verification_readback'] ?? ''),
        (string) ($packet['message_id'] ?? ''),
        (string) ($packet['proof'] ?? ''),
        (string) ($packet['proof_marker'] ?? ''),
    ]));
    $hasMessageId = preg_match('/<[^<>\s]+@[^<>\s]+>/', $text) === 1
        || str_contains($text, 'message-id')
        || str_contains($text, 'sent-log');
    if (!$hasMessageId) {
        return false;
    }
    return str_contains($text, 'sent')
        || str_contains($text, 'emailed')
        || str_contains($text, 'delivered')
        || str_contains($text, 'scheduled national outreach email');
}

function task_flow_non_pending_value(string $value): string
{
    $value = trim($value);
    $lower = strtolower($value);
    foreach (['', 'pending', 'pending-', 'required:', 'required-', 'todo', 'tbd', 'n/a'] as $prefix) {
        if ($prefix === '' && $value === '') {
            return '';
        }
        if ($prefix !== '' && str_starts_with($lower, $prefix)) {
            return '';
        }
    }
    return $value;
}

function task_flow_has_result_readback(array $row): bool
{
    $packet = task_flow_packet_json($row);
    $text = strtolower(implode(' ', [
        (string) ($row['verification_readback'] ?? ''),
        (string) ($packet['verification_readback'] ?? ''),
        (string) ($packet['readback'] ?? ''),
    ]));
    foreach (['verified', 'readback', 'saved', 'created', 'updated', 'sent', 'file path', 'artifact', 'sheet range', 'owner-visible'] as $needle) {
        if (str_contains($text, $needle)) {
            return true;
        }
    }
    return false;
}

function task_flow_has_domain_result_readback(array $row): bool
{
    if (!task_flow_has_result_readback($row)) {
        return false;
    }
    $packet = task_flow_packet_json($row);
    $text = strtolower(implode(' ', [
        (string) ($row['verification_readback'] ?? ''),
        (string) ($packet['verification_readback'] ?? ''),
        (string) ($packet['readback'] ?? ''),
    ]));
    foreach (['ops', 'portal', 'task flow', 'task id', 'domain task', 'crm', 'calendar', 'event', 'dashboard'] as $needle) {
        if (str_contains($text, $needle)) {
            return true;
        }
    }
    return false;
}

function task_flow_effective_status(array $row): string
{
    $status = task_flow_normalized_status($row);
    if (task_flow_is_no_action_closed($row)) {
        return 'no_action_closed';
    }
    if ($status === 'blocked' && task_flow_has_sent_proof($row)) {
        return 'reported';
    }
    return $status;
}

function task_flow_has_handled_filing_marker(array $row): bool
{
    $closeoutText = strtolower(implode(' ', [
        (string) ($row['latest_event'] ?? ''),
        (string) ($row['completion_or_blocker_email'] ?? ''),
        (string) ($row['verification_readback'] ?? ''),
    ]));
    return str_contains($closeoutText, 'email_filed_to_handled')
        || str_contains($closeoutText, 'filed-to-handled-after-durable-route')
        || str_contains($closeoutText, 'filed out of inbox to handled');
}

function task_flow_has_owner_visible_or_no_action_proof(array $row): bool
{
    if (task_flow_is_no_action_closed($row)) {
        return true;
    }
    $packet = task_flow_packet_json($row);
    $sources = [
        ['row', 'completion_or_blocker_email'],
        ['row', 'clarification_email'],
        ['packet', 'completion_or_blocker_email'],
        ['packet', 'clarification_email'],
        ['packet', 'message_id'],
        ['packet', 'proof'],
        ['packet', 'proof_marker'],
        ['packet', 'no_action_reason'],
    ];
    foreach ($sources as [$source, $field]) {
        $value = $source === 'row'
            ? trim((string) ($row[$field] ?? ''))
            : trim((string) ($packet[$field] ?? ''));
        if (task_flow_non_pending_value($value) !== '') {
            return true;
        }
    }
    return false;
}

function task_flow_closeout_email_still_in_inbox(array $row): bool
{
    $packet = task_flow_packet_json($row);
    foreach ([
        'mailbox_state',
        'source_mailbox_state',
        'mailbox_folder',
        'source_mailbox_folder',
        'email_folder',
        'source_email_folder',
        'gmail_label',
        'gmail_labels',
        'labels',
    ] as $field) {
        $value = strtolower(trim((string) ($row[$field] ?? $packet[$field] ?? '')));
        if ($value !== '' && str_contains($value, 'inbox')
            && !str_contains($value, 'handled')
            && !str_contains($value, 'archived')
            && !str_contains($value, 'filed')) {
            return true;
        }
    }
    return ($packet['in_inbox'] ?? $row['in_inbox'] ?? false) === true;
}

function task_flow_routed_past_next_check(array $row): bool
{
    if (trim((string) ($row['status'] ?? '')) !== 'routed') {
        return false;
    }
    $packet = task_flow_packet_json($row);
    foreach (['due_or_trigger', 'next_update', 'scheduled_action', 'due_or_next_update', 'next_update_time'] as $field) {
        $value = trim((string) ($row[$field] ?? $packet[$field] ?? ''));
        if ($value === '') {
            continue;
        }
        try {
            $due = new DateTimeImmutable($value, new DateTimeZone(TASK_FLOW_TIMEZONE));
        } catch (Throwable) {
            continue;
        }
        if ($due <= new DateTimeImmutable('now', new DateTimeZone(TASK_FLOW_TIMEZONE))) {
            return true;
        }
    }
    return false;
}

function task_flow_vague_robert_decision(array $row): bool
{
    $packet = task_flow_packet_json($row);
    $decisionText = strtolower(trim(implode(' ', array_map(static fn(string $field): string => trim((string) ($row[$field] ?? $packet[$field] ?? '')), [
        'approval_gates',
        'next_update',
        'clarification_email',
        'completion_or_blocker_email',
        'decision',
        'needed',
        'blocker',
    ]))));
    $phrases = [
        'approval needed',
        'needs approval',
        'need approval',
        'needs decision',
        'decision needed',
        'missing workflow',
        'exact next step',
        'needs input',
        'review needed',
        'please advise',
    ];
    $hasVaguePhrase = false;
    foreach ($phrases as $phrase) {
        if (str_contains($decisionText, $phrase)) {
            $hasVaguePhrase = true;
            break;
        }
    }
    if (!$hasVaguePhrase) {
        return false;
    }
    $ownerText = strtolower(trim(implode(' ', array_map(static fn(string $field): string => trim((string) ($row[$field] ?? $packet[$field] ?? '')), [
        'human_owner_or_recipient',
        'recipient',
        'requester',
        'owner_lane',
        'escalation_path',
    ]))));
    if (!str_contains($ownerText, 'robert') && !str_contains($ownerText, 'decision driver')) {
        return false;
    }
    return !str_contains($decisionText, '?')
        && !str_contains($decisionText, 'approve')
        && !str_contains($decisionText, 'decline')
        && !str_contains($decisionText, 'change')
        && !str_contains($decisionText, 'yes')
        && !str_contains($decisionText, 'no');
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
    $status = task_flow_normalized_status($row);
    return in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof'], true)
        && trim((string) ($row['papers_projection'] ?? '')) === '';
}

function task_flow_packet_severity(array $row, array $missing): string
{
    $status = task_flow_normalized_status($row);
    if (task_flow_is_no_action_closed($row)) {
        return 'closed';
    }
    if ($status === 'blocked' && task_flow_has_sent_proof($row)) {
        return 'closed';
    }
    if ($status === 'blocked') {
        return 'blocked';
    }
    if (in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof', 'review_ready'], true) && $missing !== []) {
        return 'closeout_gap';
    }
    if ($missing !== []) {
        return 'attention';
    }
    if (task_flow_projection_missing($row)) {
        return 'papers_pending';
    }
    if (in_array($status, ['completed', 'handled', 'reported', 'filed', 'closed', 'closed_with_proof', 'papers_pending', 'projected'], true)) {
        return 'closed';
    }
    return 'open';
}

function task_flow_report(PDO $pdo, int $limit = 100, string $mode = 'active'): array
{
    task_flow_install($pdo);
    $limit = max(1, min(500, $limit));
    $mode = task_flow_report_mode($mode);
    $where = task_flow_report_where_clause($mode);

    $packets = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS)->fetchColumn();
    $events = (int) $pdo->query('SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS)->fetchColumn();
    $archivedPackets = (int) $pdo->query(
        'SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' WHERE archived_at IS NOT NULL'
    )->fetchColumn();
    $visiblePackets = (int) $pdo->query(
        'SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p ' . $where
    )->fetchColumn();

    $statusRows = $pdo->query(
        'SELECT status, COUNT(*) AS count
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p
         ' . $where . '
         GROUP BY status
         ORDER BY count DESC, status ASC'
    )->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $ownerRows = $pdo->query(
        'SELECT COALESCE(NULLIF(owner_lane, \'\'), \'unknown\') AS owner_lane, COUNT(*) AS count
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p
         ' . $where . '
         GROUP BY COALESCE(NULLIF(owner_lane, \'\'), \'unknown\')
         ORDER BY count DESC, owner_lane ASC'
    )->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $stmt = $pdo->prepare(
        'SELECT p.*,
            (SELECT COUNT(*) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key) AS event_count,
            (SELECT MAX(e.logged_at) FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key) AS latest_event_at,
            (SELECT e.event FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . ' e WHERE e.dedupe_key = p.dedupe_key ORDER BY e.logged_at DESC, e.id DESC LIMIT 1) AS latest_event
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p
         ' . $where . '
         ORDER BY p.updated_at DESC
         LIMIT :limit'
    );
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

    $items = [];
    $severityCounts = [];
    $effectiveStatusCounts = [];
    $missingFieldCounts = [];
    foreach ($rows as $row) {
        $missing = task_flow_packet_missing_fields($row);
        $severity = task_flow_packet_severity($row, $missing);
        $effectiveStatus = task_flow_effective_status($row);
        $recurrence = task_flow_recurrence_data($row);
        $severityCounts[$severity] = ($severityCounts[$severity] ?? 0) + 1;
        $effectiveStatusCounts[$effectiveStatus] = ($effectiveStatusCounts[$effectiveStatus] ?? 0) + 1;
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
            'source_links' => (string) ($row['source_links'] ?? ''),
            'verification_readback' => (string) ($row['verification_readback'] ?? ''),
            'papers_projection' => (string) ($row['papers_projection'] ?? ''),
            'next_update' => (string) ($row['next_update'] ?? ''),
            'parent_packet_id' => $recurrence['parent_packet_id'],
            'parent_packet_dedupe_key' => $recurrence['parent_packet_dedupe_key'],
            'recurrence_enabled' => $recurrence['enabled'],
            'recurrence_kind' => $recurrence['kind'],
            'recurrence_cadence' => $recurrence['cadence'],
            'recurrence_pattern' => $recurrence['pattern'],
            'recurrence_rule' => $recurrence['rule'],
            'recurrence_anchor' => $recurrence['anchor'],
            'recurrence_until' => $recurrence['until'],
            'recurrence_interval' => $recurrence['interval'],
            'recurrence_time' => $recurrence['time'],
            'recurrence_summary' => $recurrence['summary'],
            'recurrence' => $recurrence,
            'updated_at' => (string) ($row['updated_at'] ?? ''),
            'created_at' => (string) ($row['created_at'] ?? ''),
            'archived_at' => (string) ($row['archived_at'] ?? ''),
            'archive_reason' => (string) ($row['archive_reason'] ?? ''),
            'archive_batch' => (string) ($row['archive_batch'] ?? ''),
            'latest_event' => (string) ($row['latest_event'] ?? ''),
            'latest_event_at' => (string) ($row['latest_event_at'] ?? ''),
            'event_count' => (int) ($row['event_count'] ?? 0),
            'missing_fields' => $missing,
            'finish_contract_missing_fields' => task_flow_finish_contract_missing_fields($row),
            'closeout_proof_present' => task_flow_closeout_has_proof_marker($row),
            'sent_proof_present' => task_flow_has_sent_proof($row),
            'email_inbox_after_closeout' => task_flow_closeout_email_still_in_inbox($row),
            'past_due_routed' => task_flow_routed_past_next_check($row),
            'vague_robert_decision' => task_flow_vague_robert_decision($row),
            'papers_projection_missing' => task_flow_projection_missing($row),
            'effective_status' => $effectiveStatus,
            'severity' => $severity,
        ];
    }

    if ($mode === 'queue') {
        $items = array_values(array_filter($items, 'task_flow_queue_visible'));
        [$statusRows, $ownerRows, $severityCounts, $effectiveStatusCounts, $missingFieldCounts] = task_flow_count_report_items($items);
        $visiblePackets = count($items);
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
    ksort($effectiveStatusCounts);

    $runnerState = task_flow_runner_state();
    $duePreview = task_flow_due_report($pdo, 10);
    $upcomingPreview = task_flow_upcoming_report($pdo, 10);

    return [
        'ok' => true,
        'database' => TASK_FLOW_DB,
        'generated_at' => date(DATE_ATOM),
        'limit' => $limit,
        'mode' => $mode,
        'totals' => [
            'packets' => $packets,
            'events' => $events,
            'visible_packets' => $visiblePackets,
            'archived_packets' => $archivedPackets,
            'shown' => count($items),
            'open_items_shown' => $openItems,
            'closeout_issues_shown' => $closeoutIssues,
        ],
        'status_counts' => array_map(static fn(array $row): array => [
            'status' => (string) ($row['status'] ?? ''),
            'count' => (int) ($row['count'] ?? 0),
        ], $statusRows),
        'effective_status_counts' => array_map(
            static fn(string $status, int $count): array => [
                'status' => $status,
                'count' => $count,
            ],
            array_keys($effectiveStatusCounts),
            array_values($effectiveStatusCounts)
        ),
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

function task_flow_queue_visible(array $item): bool
{
    $status = strtolower(trim((string) ($item['effective_status'] ?? $item['status'] ?? '')));
    if (in_array($status, ['completed', 'complete', 'reported', 'filed', 'projected', 'no_action_closed', 'waiting', 'blocked'], true)) {
        return false;
    }
    $text = strtolower(implode("\n", [
        (string) ($item['intake_channel'] ?? ''),
        (string) ($item['verification_readback'] ?? ''),
        (string) ($item['next_update'] ?? ''),
    ]));
    foreach ([
        'visible worker ',
        'routed_visible_worker',
        'task_manager_enforcement_repair',
        'routed to ',
        'excluded from active queue',
        'task manager must create/reuse visible worker',
        'email coordinator must determine responsible lane',
        'ai health should recheck within 1 minute',
    ] as $needle) {
        if (str_contains($text, $needle)) {
            return false;
        }
    }
    if (str_starts_with((string) ($item['intake_channel'] ?? ''), 'automation-health-watchdog')) {
        return false;
    }
    return true;
}

function task_flow_count_report_items(array $items): array
{
    $statusCounts = [];
    $ownerCounts = [];
    $severityCounts = [];
    $effectiveStatusCounts = [];
    $missingFieldCounts = [];
    foreach ($items as $item) {
        $status = (string) ($item['status'] ?? '');
        $owner = trim((string) ($item['owner_lane'] ?? '')) ?: 'unknown';
        $severity = (string) ($item['severity'] ?? 'open');
        $effective = (string) ($item['effective_status'] ?? $status);
        $statusCounts[$status] = ($statusCounts[$status] ?? 0) + 1;
        $ownerCounts[$owner] = ($ownerCounts[$owner] ?? 0) + 1;
        $severityCounts[$severity] = ($severityCounts[$severity] ?? 0) + 1;
        $effectiveStatusCounts[$effective] = ($effectiveStatusCounts[$effective] ?? 0) + 1;
        foreach (($item['missing_fields'] ?? []) as $field) {
            $missingFieldCounts[$field] = ($missingFieldCounts[$field] ?? 0) + 1;
        }
    }
    arsort($statusCounts);
    arsort($ownerCounts);
    ksort($severityCounts);
    ksort($effectiveStatusCounts);
    ksort($missingFieldCounts);
    return [
        array_map(static fn(string $status, int $count): array => ['status' => $status, 'count' => $count], array_keys($statusCounts), array_values($statusCounts)),
        array_map(static fn(string $owner, int $count): array => ['owner_lane' => $owner, 'count' => $count], array_keys($ownerCounts), array_values($ownerCounts)),
        $severityCounts,
        $effectiveStatusCounts,
        $missingFieldCounts,
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
        'items' => array_map(static function (array $row): array {
            $recurrence = task_flow_recurrence_data($row);
            return [
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
                'parent_packet_id' => $recurrence['parent_packet_id'],
                'recurrence_cadence' => $recurrence['cadence'],
                'recurrence_summary' => $recurrence['summary'],
                'recurrence' => $recurrence,
            ];
        }, $rows),
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
        'items' => array_map(static function (array $row): array {
            $recurrence = task_flow_recurrence_data($row);
            return [
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
                'parent_packet_id' => $recurrence['parent_packet_id'],
                'recurrence_cadence' => $recurrence['cadence'],
                'recurrence_summary' => $recurrence['summary'],
                'recurrence' => $recurrence,
            ];
        }, $rows),
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

function task_flow_report_mode(string $mode): string
{
    $mode = strtolower(trim($mode));
    return in_array($mode, ['queue', 'active', 'all', 'archived'], true) ? $mode : 'queue';
}

function task_flow_report_where_clause(string $mode): string
{
    if ($mode === 'all') {
        return '';
    }
    if ($mode === 'archived') {
        return 'WHERE p.archived_at IS NOT NULL';
    }
    return 'WHERE p.archived_at IS NULL';
}

function task_flow_archive_reason(array $row): string
{
    if (trim((string) ($row['archived_at'] ?? '')) !== '') {
        return '';
    }
    $missing = task_flow_packet_missing_fields($row);
    $severity = task_flow_packet_severity($row, $missing);
    $effectiveStatus = task_flow_effective_status($row);

    if ($effectiveStatus === 'no_action_closed') {
        return 'safe_archive_no_action_closed';
    }
    if (in_array($effectiveStatus, ['completed', 'reported', 'filed', 'projected'], true)
        && task_flow_closeout_has_proof_marker($row)
        && !task_flow_closeout_email_still_in_inbox($row)) {
        return 'safe_archive_proof_backed_closeout';
    }
    if (in_array($severity, ['closed', 'papers_pending'], true)
        && task_flow_closeout_has_proof_marker($row)) {
        return 'safe_archive_closed_severity';
    }
    return '';
}

function task_flow_archive_safe(PDO $pdo, int $limit = 500, bool $dryRun = false): array
{
    task_flow_install($pdo);
    $limit = max(1, min(5000, $limit));
    $stmt = $pdo->prepare(
        'SELECT *
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . ' p
         WHERE p.archived_at IS NULL
         ORDER BY p.updated_at DESC
         LIMIT :limit'
    );
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    $batch = 'archive-safe-' . date('Ymd-His');
    $candidates = [];
    foreach ($rows as $row) {
        $reason = task_flow_archive_reason($row);
        if ($reason === '') {
            continue;
        }
        $candidates[] = [
            'dedupe_key' => (string) ($row['dedupe_key'] ?? ''),
            'status' => (string) ($row['status'] ?? ''),
            'effective_status' => task_flow_effective_status($row),
            'severity' => task_flow_packet_severity($row, task_flow_packet_missing_fields($row)),
            'reason' => $reason,
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
        ];
    }
    if (!$dryRun && $candidates !== []) {
        $update = $pdo->prepare(
            'UPDATE ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . '
             SET archived_at = NOW(), archive_reason = :reason, archive_batch = :batch
             WHERE dedupe_key = :dedupe_key AND archived_at IS NULL'
        );
        $event = $pdo->prepare(
            'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . " (event, dedupe_key, status, details_json)
             VALUES ('task_flow_safe_archived', :dedupe_key, 'archived', :details_json)"
        );
        foreach ($candidates as $candidate) {
            $update->execute([
                ':reason' => $candidate['reason'],
                ':batch' => $batch,
                ':dedupe_key' => $candidate['dedupe_key'],
            ]);
            $event->execute([
                ':dedupe_key' => $candidate['dedupe_key'],
                ':details_json' => json_encode([
                    'event' => 'task_flow_safe_archived',
                    'dedupe_key' => $candidate['dedupe_key'],
                    'reason' => $candidate['reason'],
                    'batch' => $batch,
                ], JSON_UNESCAPED_SLASHES),
            ]);
        }
    }
    return [
        'ok' => true,
        'dry_run' => $dryRun,
        'batch' => $batch,
        'scanned' => count($rows),
        'archivable' => count($candidates),
        'archived' => $dryRun ? 0 : count($candidates),
        'items' => array_slice($candidates, 0, 100),
    ];
}

function task_flow_archive_watchdog_history(PDO $pdo, bool $dryRun = false): array
{
    task_flow_install($pdo);
    $stmt = $pdo->query(
        'SELECT dedupe_key, packet_json
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
         WHERE archived_at IS NULL
           AND intake_channel LIKE 'automation-health-watchdog%'
         ORDER BY updated_at ASC"
    );
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    $batch = 'watchdog-history-' . date('Ymd-His');
    $archived = [];
    foreach ($rows as $row) {
        $dedupeKey = (string) ($row['dedupe_key'] ?? '');
        if ($dedupeKey === '') {
            continue;
        }
        $archived[] = [
            'dedupe_key' => $dedupeKey,
            'packet_json' => $row['packet_json'] ?? '{}',
        ];
        if ($dryRun) {
            continue;
        }
        $update = $pdo->prepare(
            'UPDATE ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
             SET archived_at = NOW(), archive_reason = :reason, archive_batch = :batch
             WHERE dedupe_key = :dedupe_key AND archived_at IS NULL"
        );
        $update->execute([
            ':reason' => 'automation_health_watchdog_replaced',
            ':batch' => $batch,
            ':dedupe_key' => $dedupeKey,
        ]);
        $eventStmt = $pdo->prepare(
            'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . " (event, dedupe_key, status, details_json)
             VALUES ('task_flow_watchdog_archived', :dedupe_key, 'archived', :details_json)"
        );
        $eventStmt->execute([
            ':dedupe_key' => $dedupeKey,
            ':details_json' => json_encode([
                'event' => 'task_flow_watchdog_archived',
                'dedupe_key' => $dedupeKey,
                'archive_reason' => 'automation_health_watchdog_replaced',
                'archive_batch' => $batch,
            ], JSON_UNESCAPED_SLASHES),
        ]);
    }
    return [
        'ok' => true,
        'scanned' => count($rows),
        'archived' => $dryRun ? 0 : count($archived),
        'items' => array_slice($archived, 0, 100),
        'batch' => $batch,
        'dry_run' => $dryRun,
    ];
}

function task_flow_archive_stale_routed_proof_backed(PDO $pdo, bool $dryRun = false): array
{
    task_flow_install($pdo);
    $stmt = $pdo->query(
        'SELECT *
         FROM ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . "
         WHERE archived_at IS NULL
           AND status = 'routed'
         ORDER BY updated_at ASC"
    );
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    $batch = 'archive-stale-routed-proof-backed-' . date('Ymd-His');
    $candidates = [];
    foreach ($rows as $row) {
        $missingFinish = task_flow_finish_contract_missing_fields($row);
        $completionEmail = strtolower(trim((string) ($row['completion_or_blocker_email'] ?? '')));
        if ($missingFinish !== []) {
            continue;
        }
        if (!task_flow_closeout_has_proof_marker($row)) {
            continue;
        }
        if (!task_flow_routed_past_next_check($row)) {
            continue;
        }
        if ($completionEmail !== '' && str_starts_with($completionEmail, 'required:')) {
            continue;
        }
        $candidates[] = [
            'dedupe_key' => (string) ($row['dedupe_key'] ?? ''),
            'status' => (string) ($row['status'] ?? ''),
            'effective_status' => task_flow_effective_status($row),
            'severity' => task_flow_packet_severity($row, task_flow_packet_missing_fields($row)),
            'reason' => 'safe_archive_stale_routed_proof_backed',
            'owner_lane' => (string) ($row['owner_lane'] ?? ''),
        ];
    }
    if (!$dryRun && $candidates !== []) {
        $update = $pdo->prepare(
            'UPDATE ' . TASK_FLOW_DB . '.' . TASK_FLOW_PACKETS . '
             SET archived_at = NOW(), archive_reason = :reason, archive_batch = :batch
             WHERE dedupe_key = :dedupe_key AND archived_at IS NULL'
        );
        $event = $pdo->prepare(
            'INSERT INTO ' . TASK_FLOW_DB . '.' . TASK_FLOW_EVENTS . " (event, dedupe_key, status, details_json)
             VALUES ('task_flow_stale_routed_proof_backed_archived', :dedupe_key, 'archived', :details_json)"
        );
        foreach ($candidates as $candidate) {
            $update->execute([
                ':reason' => $candidate['reason'],
                ':batch' => $batch,
                ':dedupe_key' => $candidate['dedupe_key'],
            ]);
            $event->execute([
                ':dedupe_key' => $candidate['dedupe_key'],
                ':details_json' => json_encode([
                    'event' => 'task_flow_stale_routed_proof_backed_archived',
                    'dedupe_key' => $candidate['dedupe_key'],
                    'reason' => $candidate['reason'],
                    'batch' => $batch,
                ], JSON_UNESCAPED_SLASHES),
            ]);
        }
    }
    return [
        'ok' => true,
        'dry_run' => $dryRun,
        'batch' => $batch,
        'scanned' => count($rows),
        'archivable' => count($candidates),
        'archived' => $dryRun ? 0 : count($candidates),
        'items' => array_slice($candidates, 0, 100),
    ];
}

$command = $argv[1] ?? '';
if (!in_array($command, ['install', 'record', 'status', 'report', 'due', 'projected', 'validate', 'archive-safe', 'archive-watchdog-history', 'archive-stale-routed-proof-backed'], true)) {
    task_flow_usage();
    exit(2);
}

if ($command === 'validate') {
    try {
        $stdin = stream_get_contents(STDIN);
        $payload = json_decode($stdin === false ? '' : $stdin, true);
        if (!is_array($payload)) {
            throw new InvalidArgumentException('validate command requires JSON object on stdin.');
        }
        $packet = is_array($payload['packet'] ?? null) ? $payload['packet'] : $payload;
        $packet['packet_json'] = json_encode($packet, JSON_UNESCAPED_SLASHES) ?: '{}';
        $missing = task_flow_packet_missing_fields($packet);
        echo json_encode([
            'ok' => true,
            'status' => task_flow_string($packet, 'status') ?: 'captured',
            'missing_fields' => $missing,
            'closeout_allowed' => $missing === [],
            'finish_contract_missing_fields' => task_flow_finish_contract_missing_fields($packet),
            'closeout_proof_present' => task_flow_closeout_has_proof_marker($packet),
            'email_inbox_after_closeout' => task_flow_closeout_email_still_in_inbox($packet),
            'past_due_routed' => task_flow_routed_past_next_check($packet),
            'vague_robert_decision' => task_flow_vague_robert_decision($packet),
        ], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    } catch (Throwable $e) {
        fwrite(STDERR, $e->getMessage() . PHP_EOL);
        exit(1);
    }
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
        $mode = trim((string) ($argv[3] ?? 'active'));
        echo json_encode(task_flow_report($pdo, $limit, $mode), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'archive-safe') {
        $limit = isset($argv[2]) ? (int) $argv[2] : 500;
        $dryRun = in_array(trim((string) ($argv[3] ?? '')), ['--dry-run', 'dry-run', '1', 'true'], true);
        echo json_encode(task_flow_archive_safe($pdo, $limit, $dryRun), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'archive-watchdog-history') {
        $dryRun = in_array(trim((string) ($argv[2] ?? '')), ['--dry-run', 'dry-run', '1', 'true'], true);
        echo json_encode(task_flow_archive_watchdog_history($pdo, $dryRun), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'archive-stale-routed-proof-backed') {
        $dryRun = in_array(trim((string) ($argv[2] ?? '')), ['--dry-run', 'dry-run', '1', 'true'], true);
        echo json_encode(task_flow_archive_stale_routed_proof_backed($pdo, $dryRun), JSON_UNESCAPED_SLASHES) . PHP_EOL;
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
