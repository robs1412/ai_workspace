#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const SCHEDULED_ACTIONS_DB = 'koval_crm';
const SCHEDULED_ACTIONS_TABLE = 'ai_scheduled_actions';

function scheduled_actions_usage(): void
{
    fwrite(STDERR, "Usage: php scripts/scheduled_actions_mysql_recorder.php install|rows|upsert\n");
}

function scheduled_actions_pdo(): PDO
{
    $pdo = get_event_pdo();
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}

function scheduled_actions_install(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . SCHEDULED_ACTIONS_DB . '.' . SCHEDULED_ACTIONS_TABLE . " (
            mailbox_lane varchar(128) NOT NULL,
            action_id varchar(255) NOT NULL,
            source_ref varchar(255) DEFAULT NULL,
            status varchar(64) NOT NULL DEFAULT 'pending',
            due_at varchar(64) DEFAULT NULL,
            ops_task_id varchar(128) DEFAULT NULL,
            row_json json NOT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (mailbox_lane, action_id),
            KEY idx_mailbox_lane_status (mailbox_lane, status),
            KEY idx_due_at (due_at),
            KEY idx_source_ref (source_ref)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
}

function scheduled_actions_string(array $row, string $key): string
{
    $value = $row[$key] ?? '';
    if (is_array($value) || is_object($value)) {
        return json_encode($value, JSON_UNESCAPED_SLASHES) ?: '';
    }
    return trim((string) $value);
}

function scheduled_actions_rows(PDO $pdo, string $mailboxLane): array
{
    if ($mailboxLane === '') {
        return [];
    }
    $stmt = $pdo->prepare(
        'SELECT row_json
           FROM ' . SCHEDULED_ACTIONS_DB . '.' . SCHEDULED_ACTIONS_TABLE . '
          WHERE mailbox_lane = :mailbox_lane
          ORDER BY COALESCE(NULLIF(due_at, \'\'), \'9999-12-31T23:59:59Z\') ASC, updated_at ASC'
    );
    $stmt->execute([':mailbox_lane' => $mailboxLane]);
    $rows = [];
    while ($encoded = $stmt->fetchColumn()) {
        $decoded = json_decode((string) $encoded, true);
        if (is_array($decoded)) {
            $rows[] = $decoded;
        }
    }
    return $rows;
}

function scheduled_actions_upsert(PDO $pdo, string $mailboxLane, array $rows): array
{
    if ($mailboxLane === '') {
        throw new InvalidArgumentException('mailbox_lane is required');
    }
    scheduled_actions_install($pdo);
    $stmt = $pdo->prepare(
        'INSERT INTO ' . SCHEDULED_ACTIONS_DB . '.' . SCHEDULED_ACTIONS_TABLE . ' (
            mailbox_lane, action_id, source_ref, status, due_at, ops_task_id, row_json
        ) VALUES (
            :mailbox_lane, :action_id, :source_ref, :status, :due_at, :ops_task_id, :row_json
        )
        ON DUPLICATE KEY UPDATE
            source_ref = VALUES(source_ref),
            status = VALUES(status),
            due_at = VALUES(due_at),
            ops_task_id = VALUES(ops_task_id),
            row_json = VALUES(row_json)'
    );
    $count = 0;
    foreach ($rows as $row) {
        if (!is_array($row)) {
            continue;
        }
        $actionId = scheduled_actions_string($row, 'id');
        if ($actionId === '') {
            continue;
        }
        $rowJson = json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        if ($rowJson === false) {
            continue;
        }
        $stmt->execute([
            ':mailbox_lane' => $mailboxLane,
            ':action_id' => $actionId,
            ':source_ref' => scheduled_actions_string($row, 'source_ref') ?: $actionId,
            ':status' => scheduled_actions_string($row, 'status') ?: 'pending',
            ':due_at' => scheduled_actions_string($row, 'due_at'),
            ':ops_task_id' => scheduled_actions_string($row, 'ops_task_id'),
            ':row_json' => $rowJson,
        ]);
        $count++;
    }
    return ['ok' => true, 'mailbox_lane' => $mailboxLane, 'row_count' => $count];
}

$command = $argv[1] ?? '';
if ($command === '' || in_array($command, ['-h', '--help'], true)) {
    scheduled_actions_usage();
    exit($command === '' ? 1 : 0);
}

$pdo = scheduled_actions_pdo();
if ($command === 'install') {
    scheduled_actions_install($pdo);
    fwrite(STDOUT, json_encode(['ok' => true, 'table' => SCHEDULED_ACTIONS_DB . '.' . SCHEDULED_ACTIONS_TABLE], JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'rows') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    fwrite(STDOUT, json_encode(scheduled_actions_rows($pdo, $mailboxLane), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'upsert') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    $raw = stream_get_contents(STDIN);
    if ($raw === false || trim($raw) === '') {
        throw new InvalidArgumentException('upsert requires JSON array payload on stdin');
    }
    $rows = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
    if (!is_array($rows)) {
        throw new InvalidArgumentException('upsert payload must decode to an array');
    }
    fwrite(STDOUT, json_encode(scheduled_actions_upsert($pdo, $mailboxLane, $rows), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}

scheduled_actions_usage();
exit(1);
