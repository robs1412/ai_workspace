#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const AI_MANAGER_DB = 'koval_crm';
const AI_MANAGER_TABLE = 'ai_manager_inputs';
const AI_MANAGER_EVENT_TABLE = 'ai_manager_input_events';

function usage(): void
{
    fwrite(STDERR, "Usage: php scripts/ai_manager_input_recorder.php install|record|update|recent|backfill-events [limit]\n");
}

function pdo_conn(): PDO
{
    $pdo = get_event_pdo();
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}

function install(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            input_uuid varchar(64) NOT NULL,
            user_id int unsigned DEFAULT NULL,
            user_label varchar(255) DEFAULT NULL,
            source_channel varchar(64) DEFAULT NULL,
            source_path text,
            input_text longtext,
            assessment_text longtext,
            output_text longtext,
            answer_text longtext,
            related_session_id varchar(128) DEFAULT NULL,
            related_task_id varchar(128) DEFAULT NULL,
            related_taskflow_key varchar(128) DEFAULT NULL,
            status varchar(64) NOT NULL DEFAULT 'captured',
            proof_marker varchar(255) DEFAULT NULL,
            session_env_json json DEFAULT NULL,
            shell_snapshot_json json DEFAULT NULL,
            metadata_json json NOT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY idx_input_uuid (input_uuid),
            KEY idx_status (status),
            KEY idx_user_id (user_id),
            KEY idx_related_taskflow_key (related_taskflow_key),
            KEY idx_related_session_id (related_session_id),
            KEY idx_proof_marker (proof_marker),
            KEY idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . AI_MANAGER_DB . '.' . AI_MANAGER_EVENT_TABLE . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            input_id bigint unsigned DEFAULT NULL,
            input_uuid varchar(64) NOT NULL,
            event varchar(64) NOT NULL,
            details_json longtext NOT NULL,
            logged_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_input_id (input_id),
            KEY idx_input_uuid (input_uuid),
            KEY idx_event (event),
            KEY idx_logged_at (logged_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
    foreach ([
        'proof_marker' => 'varchar(255) DEFAULT NULL',
        'session_env_json' => 'json DEFAULT NULL',
        'shell_snapshot_json' => 'json DEFAULT NULL',
    ] as $column => $definition) {
        try {
            $pdo->exec('ALTER TABLE ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . ' ADD COLUMN ' . $column . ' ' . $definition);
        } catch (Throwable) {
            // Existing deployments may already have the current schema.
        }
    }
}

function log_input_event(PDO $pdo, int $inputId, string $inputUuid, string $event, array $details): void
{
    install($pdo);

    $payload = $details;
    $payload['input_id'] = $inputId;
    $payload['input_uuid'] = $inputUuid;
    $payload['event'] = $event;

    $stmt = $pdo->prepare(
        'INSERT INTO ' . AI_MANAGER_DB . '.' . AI_MANAGER_EVENT_TABLE . ' (
            input_id, input_uuid, event, details_json
        ) VALUES (
            :input_id, :input_uuid, :event, :details_json
        )'
    );
    $stmt->execute([
        ':input_id' => $inputId,
        ':input_uuid' => $inputUuid,
        ':event' => $event,
        ':details_json' => json_encode($payload, JSON_UNESCAPED_SLASHES),
    ]);
}

function read_payload(): array
{
    $raw = stream_get_contents(STDIN);
    $data = json_decode($raw ?: 'null', true);
    if (!is_array($data)) {
        throw new InvalidArgumentException('Recorder payload must be JSON.');
    }
    return $data;
}

function string_value(array $payload, string $key): string
{
    $value = $payload[$key] ?? '';
    if (is_array($value) || is_object($value)) {
        return json_encode($value, JSON_UNESCAPED_SLASHES) ?: '';
    }
    return trim((string) $value);
}

function int_value(array $payload, string $key): ?int
{
    $value = $payload[$key] ?? null;
    if ($value === null || $value === '') {
        return null;
    }
    return (int) $value;
}

function upsert_input(PDO $pdo, array $payload, string $event = 'recorded'): array
{
    install($pdo);

    $uuid = trim((string) ($payload['input_uuid'] ?? ''));
    if ($uuid === '') {
        throw new InvalidArgumentException('Missing input_uuid.');
    }

    $metadata = $payload['metadata'] ?? [];
    if (!is_array($metadata)) {
        $metadata = ['value' => $metadata];
    }
    $sessionEnv = $payload['session_env'] ?? null;
    if ($sessionEnv !== null && !is_array($sessionEnv)) {
        $sessionEnv = ['value' => $sessionEnv];
    }
    $shellSnapshot = $payload['shell_snapshot'] ?? null;
    if ($shellSnapshot !== null && !is_array($shellSnapshot)) {
        $shellSnapshot = ['value' => $shellSnapshot];
    }

    $stmt = $pdo->prepare(
        'INSERT INTO ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . ' (
            input_uuid, user_id, user_label, source_channel, source_path,
            input_text, assessment_text, output_text, answer_text,
            related_session_id, related_task_id, related_taskflow_key, status, proof_marker,
            session_env_json, shell_snapshot_json, metadata_json
        ) VALUES (
            :input_uuid, :user_id, :user_label, :source_channel, :source_path,
            :input_text, :assessment_text, :output_text, :answer_text,
            :related_session_id, :related_task_id, :related_taskflow_key, :status, :proof_marker,
            :session_env_json, :shell_snapshot_json, :metadata_json
        )
        ON DUPLICATE KEY UPDATE
            user_id = VALUES(user_id),
            user_label = VALUES(user_label),
            source_channel = VALUES(source_channel),
            source_path = VALUES(source_path),
            input_text = VALUES(input_text),
            assessment_text = VALUES(assessment_text),
            output_text = VALUES(output_text),
            answer_text = VALUES(answer_text),
            related_session_id = VALUES(related_session_id),
            related_task_id = VALUES(related_task_id),
            related_taskflow_key = VALUES(related_taskflow_key),
            status = VALUES(status),
            proof_marker = VALUES(proof_marker),
            session_env_json = VALUES(session_env_json),
            shell_snapshot_json = VALUES(shell_snapshot_json),
            metadata_json = VALUES(metadata_json)'
    );

    $stmt->execute([
        ':input_uuid' => $uuid,
        ':user_id' => int_value($payload, 'user_id'),
        ':user_label' => string_value($payload, 'user_label'),
        ':source_channel' => string_value($payload, 'source_channel'),
        ':source_path' => string_value($payload, 'source_path'),
        ':input_text' => string_value($payload, 'input_text'),
        ':assessment_text' => string_value($payload, 'assessment_text'),
        ':output_text' => string_value($payload, 'output_text'),
        ':answer_text' => string_value($payload, 'answer_text'),
        ':related_session_id' => string_value($payload, 'related_session_id'),
        ':related_task_id' => string_value($payload, 'related_task_id'),
        ':related_taskflow_key' => string_value($payload, 'related_taskflow_key'),
        ':status' => string_value($payload, 'status') ?: 'captured',
        ':proof_marker' => string_value($payload, 'proof_marker'),
        ':session_env_json' => $sessionEnv === null ? null : json_encode($sessionEnv, JSON_UNESCAPED_SLASHES),
        ':shell_snapshot_json' => $shellSnapshot === null ? null : json_encode($shellSnapshot, JSON_UNESCAPED_SLASHES),
        ':metadata_json' => json_encode($metadata, JSON_UNESCAPED_SLASHES),
    ]);

    $idStmt = $pdo->prepare(
        'SELECT id
         FROM ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . '
         WHERE input_uuid = :input_uuid
         LIMIT 1'
    );
    $idStmt->execute([':input_uuid' => $uuid]);
    $id = (int) ($idStmt->fetchColumn() ?: 0);

    log_input_event($pdo, $id, $uuid, $event, $payload);

    return [
        'ok' => true,
        'input_id' => $id,
        'input_uuid' => $uuid,
    ];
}

function recent_inputs(PDO $pdo, int $limit): array
{
    install($pdo);
    $limit = max(1, min(500, $limit));
    $stmt = $pdo->prepare(
        'SELECT id, input_uuid, user_id, user_label, source_channel, source_path, input_text,
                assessment_text, output_text, answer_text, related_session_id,
                related_task_id, related_taskflow_key, status, proof_marker,
                created_at, updated_at
         FROM ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . '
         ORDER BY id DESC
         LIMIT ' . $limit
    );
    $stmt->execute();
    return [
        'ok' => true,
        'items' => $stmt->fetchAll(PDO::FETCH_ASSOC),
    ];
}

function backfill_events(PDO $pdo, int $limit): array
{
    install($pdo);
    $limit = max(1, min(1000, $limit));
    $stmt = $pdo->prepare(
        'SELECT i.*
         FROM ' . AI_MANAGER_DB . '.' . AI_MANAGER_TABLE . ' i
         LEFT JOIN ' . AI_MANAGER_DB . '.' . AI_MANAGER_EVENT_TABLE . ' e
           ON e.input_uuid = i.input_uuid
         WHERE e.input_uuid IS NULL
         ORDER BY i.id ASC
         LIMIT ' . $limit
    );
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    $inserted = 0;
    foreach ($rows as $row) {
        $eventPayload = [
            'input_id' => (int) ($row['id'] ?? 0),
            'input_uuid' => (string) ($row['input_uuid'] ?? ''),
            'event' => 'backfilled',
            'source' => 'ai_manager_inputs_missing_legacy_event',
            'input' => $row,
        ];
        $eventStmt = $pdo->prepare(
            'INSERT INTO ' . AI_MANAGER_DB . '.' . AI_MANAGER_EVENT_TABLE . ' (
                input_id, input_uuid, event, details_json
            ) VALUES (
                :input_id, :input_uuid, :event, :details_json
            )'
        );
        $eventStmt->execute([
            ':input_id' => (int) ($row['id'] ?? 0),
            ':input_uuid' => (string) ($row['input_uuid'] ?? ''),
            ':event' => 'backfilled',
            ':details_json' => json_encode($eventPayload, JSON_UNESCAPED_SLASHES),
        ]);
        $inserted++;
    }

    return [
        'ok' => true,
        'missing_count' => count($rows),
        'backfilled_count' => $inserted,
    ];
}

try {
    $command = $argv[1] ?? '';
    $pdo = pdo_conn();
    if ($command === 'install') {
        install($pdo);
        echo json_encode(['ok' => true], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'record' || $command === 'update') {
        $payload = read_payload();
        echo json_encode(upsert_input($pdo, $payload, $command === 'update' ? 'updated' : 'recorded'), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'recent') {
        $limit = isset($argv[2]) ? (int) $argv[2] : 25;
        echo json_encode(recent_inputs($pdo, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'backfill-events') {
        $limit = isset($argv[2]) ? (int) $argv[2] : 500;
        echo json_encode(backfill_events($pdo, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    usage();
    exit(1);
} catch (Throwable $error) {
    fwrite(STDERR, $error->getMessage() . PHP_EOL);
    exit(1);
}
