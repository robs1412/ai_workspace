#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const HANDOFF_DB = 'koval_crm';
const HANDOFF_ENTRIES = 'ai_task_flow_handoff_entries';
const HANDOFF_SOURCES = 'ai_task_flow_handoff_sources';
const HANDOFF_SNAPSHOTS = 'ai_task_flow_handoff_snapshots';
const HANDOFF_LEGACY_ENTRIES = 'ai_handoff_entries';
const HANDOFF_LEGACY_SOURCES = 'ai_handoff_sources';
const HANDOFF_LEGACY_SNAPSHOTS = 'ai_handoff_snapshots';
const HANDOFF_TIMEZONE = 'America/Chicago';

date_default_timezone_set(HANDOFF_TIMEZONE);

function handoff_usage(): void
{
    fwrite(STDERR, "Usage: php scripts/handoff_mysql_recorder.php install|status|record|report|projection\n");
}

function handoff_pdo(): PDO
{
    $pdo = get_event_pdo();
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}

function handoff_install(PDO $pdo): void
{
    handoff_migrate_legacy_tables($pdo);

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . HANDOFF_DB . '.' . HANDOFF_ENTRIES . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            entry_uuid varchar(128) NOT NULL,
            occurred_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            workspace varchar(128) NOT NULL,
            repo_path varchar(512) DEFAULT NULL,
            repo_name varchar(128) DEFAULT NULL,
            handoff_path varchar(512) DEFAULT NULL,
            task_flow_dedupe_key varchar(128) DEFAULT NULL,
            workspaceboard_session varchar(128) DEFAULT NULL,
            ops_portal_or_domain_task varchar(128) DEFAULT NULL,
            state varchar(64) NOT NULL DEFAULT 'note',
            visibility varchar(64) NOT NULL DEFAULT 'internal',
            author varchar(128) DEFAULT NULL,
            agent varchar(128) DEFAULT NULL,
            summary text NOT NULL,
            next_step text,
            blocker text,
            proof_json json DEFAULT NULL,
            metadata_json json DEFAULT NULL,
            supersedes_entry_id bigint unsigned DEFAULT NULL,
            correction_of_entry_id bigint unsigned DEFAULT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uniq_entry_uuid (entry_uuid),
            KEY idx_workspace_occurred (workspace, occurred_at),
            KEY idx_repo_path (repo_path),
            KEY idx_state (state),
            KEY idx_task_flow_dedupe_key (task_flow_dedupe_key),
            KEY idx_workspaceboard_session (workspaceboard_session),
            KEY idx_ops_portal_or_domain_task (ops_portal_or_domain_task)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . HANDOFF_DB . '.' . HANDOFF_SOURCES . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            entry_id bigint unsigned NOT NULL,
            source_type varchar(128) NOT NULL,
            source_value varchar(512) NOT NULL,
            label varchar(255) DEFAULT NULL,
            url text,
            metadata_json json DEFAULT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_entry_id (entry_id),
            KEY idx_source_type_value (source_type, source_value),
            CONSTRAINT fk_ai_task_flow_handoff_sources_entry
                FOREIGN KEY (entry_id) REFERENCES " . HANDOFF_DB . '.' . HANDOFF_ENTRIES . " (id)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . HANDOFF_DB . '.' . HANDOFF_SNAPSHOTS . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            snapshot_key varchar(255) NOT NULL,
            workspace varchar(128) NOT NULL,
            repo_path varchar(512) DEFAULT NULL,
            generated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            entry_count int unsigned NOT NULL DEFAULT 0,
            snapshot_markdown mediumtext NOT NULL,
            metadata_json json DEFAULT NULL,
            PRIMARY KEY (id),
            KEY idx_snapshot_key (snapshot_key),
            KEY idx_workspace_generated (workspace, generated_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
}

function handoff_table_exists(PDO $pdo, string $table): bool
{
    $stmt = $pdo->prepare(
        'SELECT COUNT(*)
           FROM information_schema.TABLES
          WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table'
    );
    $stmt->execute([':schema' => HANDOFF_DB, ':table' => $table]);
    return (int) $stmt->fetchColumn() > 0;
}

function handoff_migrate_legacy_tables(PDO $pdo): void
{
    if (handoff_table_exists($pdo, HANDOFF_ENTRIES)) {
        return;
    }
    if (!handoff_table_exists($pdo, HANDOFF_LEGACY_ENTRIES)) {
        return;
    }

    $renames = [];
    foreach ([
        HANDOFF_LEGACY_ENTRIES => HANDOFF_ENTRIES,
        HANDOFF_LEGACY_SOURCES => HANDOFF_SOURCES,
        HANDOFF_LEGACY_SNAPSHOTS => HANDOFF_SNAPSHOTS,
    ] as $legacy => $current) {
        if (handoff_table_exists($pdo, $legacy) && !handoff_table_exists($pdo, $current)) {
            $renames[] = HANDOFF_DB . '.' . $legacy . ' TO ' . HANDOFF_DB . '.' . $current;
        }
    }
    if ($renames === []) {
        return;
    }

    $pdo->exec('SET FOREIGN_KEY_CHECKS=0');
    try {
        $pdo->exec('RENAME TABLE ' . implode(', ', $renames));
    } finally {
        $pdo->exec('SET FOREIGN_KEY_CHECKS=1');
    }
}

function handoff_string(array $row, string $key): string
{
    $value = $row[$key] ?? '';
    if (is_array($value) || is_object($value)) {
        return json_encode($value, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) ?: '';
    }
    return trim((string) $value);
}

function handoff_json($value): ?string
{
    if ($value === null || $value === '' || $value === []) {
        return null;
    }
    return json_encode($value, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
}

function handoff_timestamp(?string $value): string
{
    $raw = trim((string) $value);
    if ($raw === '') {
        return (new DateTimeImmutable('now'))->format('Y-m-d H:i:s');
    }
    return (new DateTimeImmutable($raw))->format('Y-m-d H:i:s');
}

function handoff_slug(string $value): string
{
    $slug = strtolower(trim($value));
    $slug = preg_replace('/[^a-z0-9]+/', '-', $slug) ?? '';
    $slug = trim($slug, '-');
    return $slug !== '' ? substr($slug, 0, 80) : 'handoff-entry';
}

function handoff_entry_uuid(array $entry): string
{
    $provided = handoff_string($entry, 'entry_uuid');
    if ($provided !== '') {
        return $provided;
    }
    $workspace = handoff_slug(handoff_string($entry, 'workspace') ?: 'workspace');
    $stamp = gmdate('YmdHis');
    $hash = substr(hash('sha256', json_encode($entry, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . microtime(true)), 0, 12);
    return 'handoff-' . $workspace . '-' . $stamp . '-' . $hash;
}

function handoff_repo_name(string $repoPath): string
{
    $repoPath = rtrim($repoPath, '/');
    if ($repoPath === '') {
        return '';
    }
    return basename($repoPath);
}

function handoff_record(PDO $pdo, array $payload): array
{
    handoff_install($pdo);
    $entry = is_array($payload['entry'] ?? null) ? $payload['entry'] : $payload;
    $workspace = handoff_string($entry, 'workspace');
    $summary = handoff_string($entry, 'summary');
    if ($workspace === '' || $summary === '') {
        throw new InvalidArgumentException('record requires workspace and summary.');
    }

    $repoPath = handoff_string($entry, 'repo_path');
    $entryUuid = handoff_entry_uuid($entry);
    $repoName = handoff_string($entry, 'repo_name') ?: handoff_repo_name($repoPath);
    $sources = is_array($payload['sources'] ?? null) ? $payload['sources'] : (is_array($entry['sources'] ?? null) ? $entry['sources'] : []);

    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare(
            'INSERT INTO ' . HANDOFF_DB . '.' . HANDOFF_ENTRIES . ' (
                entry_uuid, occurred_at, workspace, repo_path, repo_name, handoff_path,
                task_flow_dedupe_key, workspaceboard_session, ops_portal_or_domain_task,
                state, visibility, author, agent, summary, next_step, blocker,
                proof_json, metadata_json, supersedes_entry_id, correction_of_entry_id
            ) VALUES (
                :entry_uuid, :occurred_at, :workspace, :repo_path, :repo_name, :handoff_path,
                :task_flow_dedupe_key, :workspaceboard_session, :ops_portal_or_domain_task,
                :state, :visibility, :author, :agent, :summary, :next_step, :blocker,
                :proof_json, :metadata_json, :supersedes_entry_id, :correction_of_entry_id
            )'
        );
        $stmt->execute([
            ':entry_uuid' => $entryUuid,
            ':occurred_at' => handoff_timestamp(handoff_string($entry, 'occurred_at')),
            ':workspace' => $workspace,
            ':repo_path' => $repoPath,
            ':repo_name' => $repoName,
            ':handoff_path' => handoff_string($entry, 'handoff_path'),
            ':task_flow_dedupe_key' => handoff_string($entry, 'task_flow_dedupe_key'),
            ':workspaceboard_session' => handoff_string($entry, 'workspaceboard_session'),
            ':ops_portal_or_domain_task' => handoff_string($entry, 'ops_portal_or_domain_task'),
            ':state' => handoff_string($entry, 'state') ?: 'note',
            ':visibility' => handoff_string($entry, 'visibility') ?: 'internal',
            ':author' => handoff_string($entry, 'author'),
            ':agent' => handoff_string($entry, 'agent'),
            ':summary' => $summary,
            ':next_step' => handoff_string($entry, 'next_step'),
            ':blocker' => handoff_string($entry, 'blocker'),
            ':proof_json' => handoff_json($entry['proof'] ?? null),
            ':metadata_json' => handoff_json($entry['metadata'] ?? null),
            ':supersedes_entry_id' => ($entry['supersedes_entry_id'] ?? '') === '' ? null : (int) $entry['supersedes_entry_id'],
            ':correction_of_entry_id' => ($entry['correction_of_entry_id'] ?? '') === '' ? null : (int) $entry['correction_of_entry_id'],
        ]);
        $entryId = (int) $pdo->lastInsertId();

        if ($sources !== []) {
            $sourceStmt = $pdo->prepare(
                'INSERT INTO ' . HANDOFF_DB . '.' . HANDOFF_SOURCES . ' (
                    entry_id, source_type, source_value, label, url, metadata_json
                ) VALUES (
                    :entry_id, :source_type, :source_value, :label, :url, :metadata_json
                )'
            );
            foreach ($sources as $source) {
                if (!is_array($source)) {
                    continue;
                }
                $sourceType = handoff_string($source, 'source_type') ?: handoff_string($source, 'type');
                $sourceValue = handoff_string($source, 'source_value') ?: handoff_string($source, 'value');
                if ($sourceType === '' || $sourceValue === '') {
                    continue;
                }
                $sourceStmt->execute([
                    ':entry_id' => $entryId,
                    ':source_type' => $sourceType,
                    ':source_value' => $sourceValue,
                    ':label' => handoff_string($source, 'label'),
                    ':url' => handoff_string($source, 'url'),
                    ':metadata_json' => handoff_json($source['metadata'] ?? null),
                ]);
            }
        }
        $pdo->commit();
        return ['ok' => true, 'entry_id' => $entryId, 'entry_uuid' => $entryUuid, 'source_count' => count($sources)];
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function handoff_status(PDO $pdo): array
{
    handoff_install($pdo);
    return [
        'ok' => true,
        'database' => HANDOFF_DB,
        'tables' => [
            'entries' => HANDOFF_ENTRIES,
            'sources' => HANDOFF_SOURCES,
            'snapshots' => HANDOFF_SNAPSHOTS,
        ],
        'entries' => (int) $pdo->query('SELECT COUNT(*) FROM ' . HANDOFF_DB . '.' . HANDOFF_ENTRIES)->fetchColumn(),
        'sources' => (int) $pdo->query('SELECT COUNT(*) FROM ' . HANDOFF_DB . '.' . HANDOFF_SOURCES)->fetchColumn(),
        'snapshots' => (int) $pdo->query('SELECT COUNT(*) FROM ' . HANDOFF_DB . '.' . HANDOFF_SNAPSHOTS)->fetchColumn(),
    ];
}

function handoff_report(PDO $pdo, string $workspace, string $repoPath, int $limit): array
{
    handoff_install($pdo);
    $where = [];
    $params = [];
    if ($workspace !== '') {
        $where[] = 'workspace = :workspace';
        $params[':workspace'] = $workspace;
    }
    if ($repoPath !== '') {
        $where[] = 'repo_path = :repo_path';
        $params[':repo_path'] = $repoPath;
    }
    $whereSql = $where === [] ? '' : 'WHERE ' . implode(' AND ', $where);
    $stmt = $pdo->prepare(
        'SELECT *
           FROM ' . HANDOFF_DB . '.' . HANDOFF_ENTRIES . "
          {$whereSql}
          ORDER BY occurred_at DESC, id DESC
          LIMIT :limit"
    );
    foreach ($params as $key => $value) {
        $stmt->bindValue($key, $value);
    }
    $stmt->bindValue(':limit', max(1, min(500, $limit)), PDO::PARAM_INT);
    $stmt->execute();
    $entries = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    if ($entries === []) {
        return ['ok' => true, 'entries' => []];
    }
    $ids = array_map(fn ($row) => (int) $row['id'], $entries);
    $sourceRows = handoff_sources_for_entries($pdo, $ids);
    foreach ($entries as &$entry) {
        $entry['sources'] = $sourceRows[(int) $entry['id']] ?? [];
        $entry['proof'] = json_decode((string) ($entry['proof_json'] ?? 'null'), true);
        $entry['metadata'] = json_decode((string) ($entry['metadata_json'] ?? 'null'), true);
        unset($entry['proof_json'], $entry['metadata_json']);
    }
    return ['ok' => true, 'entries' => $entries];
}

function handoff_sources_for_entries(PDO $pdo, array $entryIds): array
{
    if ($entryIds === []) {
        return [];
    }
    $placeholders = implode(',', array_fill(0, count($entryIds), '?'));
    $stmt = $pdo->prepare(
        'SELECT entry_id, source_type, source_value, label, url, metadata_json
           FROM ' . HANDOFF_DB . '.' . HANDOFF_SOURCES . "
          WHERE entry_id IN ({$placeholders})
          ORDER BY id ASC"
    );
    $stmt->execute($entryIds);
    $grouped = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $entryId = (int) $row['entry_id'];
        $row['metadata'] = json_decode((string) ($row['metadata_json'] ?? 'null'), true);
        unset($row['metadata_json']);
        $grouped[$entryId][] = $row;
    }
    return $grouped;
}

function handoff_projection_markdown(PDO $pdo, string $workspace, string $repoPath, int $limit, bool $storeSnapshot): string
{
    $report = handoff_report($pdo, $workspace, $repoPath, $limit);
    $entries = $report['entries'] ?? [];
    $title = '# Handoff Projection';
    if ($workspace !== '') {
        $title .= ' - ' . $workspace;
    }
    $lines = [
        $title,
        '',
        'Generated: ' . (new DateTimeImmutable('now'))->format('Y-m-d H:i T'),
        '',
    ];
    if ($entries === []) {
        $lines[] = 'No DB-backed handoff entries found for this filter.';
        $lines[] = '';
    } else {
        foreach ($entries as $entry) {
            $stamp = (new DateTimeImmutable((string) $entry['occurred_at']))->format('Y-m-d H:i T');
            $state = (string) ($entry['state'] ?? 'note');
            $lines[] = '- ' . $stamp . ' `' . $state . '` ' . trim((string) $entry['summary']);
            $details = [];
            foreach (['task_flow_dedupe_key', 'workspaceboard_session', 'ops_portal_or_domain_task'] as $field) {
                if (!empty($entry[$field])) {
                    $details[] = $field . '=' . $entry[$field];
                }
            }
            if ($details !== []) {
                $lines[] = '  - Proof refs: `' . implode('`, `', $details) . '`';
            }
            if (!empty($entry['next_step'])) {
                $lines[] = '  - Next: ' . trim((string) $entry['next_step']);
            }
            if (!empty($entry['blocker'])) {
                $lines[] = '  - Blocker: ' . trim((string) $entry['blocker']);
            }
        }
        $lines[] = '';
    }
    $markdown = implode("\n", $lines);

    if ($storeSnapshot) {
        $snapshotKey = 'handoff-projection-' . handoff_slug($workspace ?: 'all') . '-' . date('Ymd-His');
        $stmt = $pdo->prepare(
            'INSERT INTO ' . HANDOFF_DB . '.' . HANDOFF_SNAPSHOTS . ' (
                snapshot_key, workspace, repo_path, entry_count, snapshot_markdown, metadata_json
            ) VALUES (
                :snapshot_key, :workspace, :repo_path, :entry_count, :snapshot_markdown, :metadata_json
            )'
        );
        $stmt->execute([
            ':snapshot_key' => $snapshotKey,
            ':workspace' => $workspace ?: 'all',
            ':repo_path' => $repoPath,
            ':entry_count' => count($entries),
            ':snapshot_markdown' => $markdown,
            ':metadata_json' => handoff_json(['limit' => $limit]),
        ]);
    }

    return $markdown;
}

function handoff_arg(array $argv, string $name, string $default = ''): string
{
    for ($i = 2; $i < count($argv); $i++) {
        if ($argv[$i] === $name && isset($argv[$i + 1])) {
            return (string) $argv[$i + 1];
        }
        if (str_starts_with($argv[$i], $name . '=')) {
            return substr($argv[$i], strlen($name) + 1);
        }
    }
    return $default;
}

$command = $argv[1] ?? '';
if ($command === '' || in_array($command, ['-h', '--help'], true)) {
    handoff_usage();
    exit($command === '' ? 1 : 0);
}

try {
    $pdo = handoff_pdo();
    if ($command === 'install') {
        handoff_install($pdo);
        echo json_encode(['ok' => true, 'database' => HANDOFF_DB], JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'status') {
        echo json_encode(handoff_status($pdo), JSON_UNESCAPED_SLASHES) . PHP_EOL;
        exit(0);
    }
    if ($command === 'record') {
        $stdin = stream_get_contents(STDIN);
        $payload = json_decode($stdin === false ? '' : $stdin, true, flags: JSON_THROW_ON_ERROR);
        if (!is_array($payload)) {
            throw new InvalidArgumentException('record requires JSON object on stdin.');
        }
        echo json_encode(handoff_record($pdo, $payload), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
        exit(0);
    }
    if ($command === 'report') {
        $workspace = handoff_arg($argv, '--workspace');
        $repoPath = handoff_arg($argv, '--repo-path');
        $limit = (int) handoff_arg($argv, '--limit', '25');
        echo json_encode(handoff_report($pdo, $workspace, $repoPath, $limit), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
        exit(0);
    }
    if ($command === 'projection') {
        $workspace = handoff_arg($argv, '--workspace');
        $repoPath = handoff_arg($argv, '--repo-path');
        $limit = (int) handoff_arg($argv, '--limit', '25');
        $storeSnapshot = in_array('--store-snapshot', $argv, true);
        echo handoff_projection_markdown($pdo, $workspace, $repoPath, $limit, $storeSnapshot);
        exit(0);
    }
    handoff_usage();
    exit(2);
} catch (Throwable $e) {
    fwrite(STDERR, $e->getMessage() . PHP_EOL);
    exit(1);
}
