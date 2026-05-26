#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const EMAIL_TRACE_DB = 'koval_crm';
const EMAIL_TRACE_MESSAGES = 'ai_email_messages';
const EMAIL_TRACE_EVENTS = 'ai_email_events';

function email_trace_usage(): void
{
    fwrite(STDERR, "Usage: php scripts/email_trace_mysql_recorder.php install|record|sent-entries|owner-replies|active-inbox|seen-source-ids\n");
}

function email_trace_pdo(): PDO
{
    $pdo = get_event_pdo();
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}

function email_trace_install(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . " (
            message_key varchar(128) NOT NULL,
            message_id_norm varchar(255) DEFAULT NULL,
            source_message_id varchar(255) DEFAULT NULL,
            source_ref varchar(255) DEFAULT NULL,
            thread_key varchar(128) DEFAULT NULL,
            mailbox_lane varchar(128) DEFAULT NULL,
            worker varchar(128) DEFAULT NULL,
            direction varchar(32) DEFAULT NULL,
            email_account varchar(255) DEFAULT NULL,
            subject varchar(512) DEFAULT NULL,
            from_address varchar(255) DEFAULT NULL,
            from_name varchar(255) DEFAULT NULL,
            to_addresses json DEFAULT NULL,
            cc_addresses json DEFAULT NULL,
            bcc_addresses json DEFAULT NULL,
            header_date varchar(255) DEFAULT NULL,
            body_path text,
            body_chars int DEFAULT NULL,
            body_summary text,
            task_flow_dedupe_key varchar(128) DEFAULT NULL,
            workspaceboard_session varchar(128) DEFAULT NULL,
            ops_portal_or_domain_task varchar(128) DEFAULT NULL,
            current_status varchar(64) DEFAULT NULL,
            latest_event varchar(128) DEFAULT NULL,
            last_event_details_json json DEFAULT NULL,
            metadata_json json DEFAULT NULL,
            first_seen_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_event_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            archived_at timestamp NULL DEFAULT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (message_key),
            KEY idx_message_id_norm (message_id_norm),
            KEY idx_source_ref (source_ref),
            KEY idx_task_flow_dedupe_key (task_flow_dedupe_key),
            KEY idx_workspaceboard_session (workspaceboard_session),
            KEY idx_ops_portal_or_domain_task (ops_portal_or_domain_task),
            KEY idx_mailbox_lane (mailbox_lane),
            KEY idx_last_event_at (last_event_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_EVENTS . " (
            id bigint unsigned NOT NULL AUTO_INCREMENT,
            logged_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event varchar(128) NOT NULL,
            message_key varchar(128) DEFAULT NULL,
            message_id_norm varchar(255) DEFAULT NULL,
            source_ref varchar(255) DEFAULT NULL,
            task_flow_dedupe_key varchar(128) DEFAULT NULL,
            workspaceboard_session varchar(128) DEFAULT NULL,
            ops_portal_or_domain_task varchar(128) DEFAULT NULL,
            status varchar(64) DEFAULT NULL,
            mailbox_lane varchar(128) DEFAULT NULL,
            worker varchar(128) DEFAULT NULL,
            details_json json NOT NULL,
            PRIMARY KEY (id),
            KEY idx_message_key (message_key),
            KEY idx_message_id_norm (message_id_norm),
            KEY idx_source_ref (source_ref),
            KEY idx_task_flow_dedupe_key (task_flow_dedupe_key),
            KEY idx_mailbox_lane (mailbox_lane),
            KEY idx_logged_at (logged_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
}

function email_trace_string(array $row, string $key): string
{
    $value = $row[$key] ?? '';
    if (is_array($value) || is_object($value)) {
        return json_encode($value, JSON_UNESCAPED_SLASHES) ?: '';
    }
    return trim((string) $value);
}

function email_trace_json($value): ?string
{
    if ($value === null || $value === '' || $value === []) {
        return null;
    }
    return json_encode($value, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
}

function email_trace_timestamp(?string $value): ?string
{
    $raw = trim((string) $value);
    if ($raw === '') {
        return null;
    }
    try {
        return (new DateTimeImmutable($raw))->format('Y-m-d H:i:s');
    } catch (Throwable $e) {
        return null;
    }
}

function email_trace_record(PDO $pdo, array $payload): void
{
    email_trace_install($pdo);
    $message = is_array($payload['message'] ?? null) ? $payload['message'] : [];
    $taskPacket = is_array($payload['task_packet'] ?? null) ? $payload['task_packet'] : [];
    $event = email_trace_string($payload, 'event') ?: 'email_event';
    $status = email_trace_string($message, 'status');
    $messageKey = email_trace_string($message, 'message_key');
    if ($messageKey === '') {
        throw new InvalidArgumentException('message.message_key is required');
    }
    $detailsJson = email_trace_json($payload['details'] ?? []) ?? '{}';
    $metadataJson = email_trace_json($message['metadata'] ?? []);
    $archivedAt = email_trace_timestamp(email_trace_string($message, 'archived_at'));
    $eventAt = email_trace_timestamp(email_trace_string($message, 'event_at')) ?: (new DateTimeImmutable('now'))->format('Y-m-d H:i:s');
    $taskFlowDedupeKey = email_trace_string($message, 'task_flow_dedupe_key') ?: email_trace_string($taskPacket, 'dedupe_key');
    $workspaceboardSession = email_trace_string($message, 'workspaceboard_session') ?: email_trace_string($taskPacket, 'workspaceboard_session');
    $opsTask = email_trace_string($message, 'ops_portal_or_domain_task') ?: email_trace_string($taskPacket, 'ops_portal_or_domain_task');

    $stmt = $pdo->prepare(
        'INSERT INTO ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . ' (
            message_key, message_id_norm, source_message_id, source_ref, thread_key,
            mailbox_lane, worker, direction, email_account, subject, from_address, from_name,
            to_addresses, cc_addresses, bcc_addresses, header_date, body_path, body_chars, body_summary,
            task_flow_dedupe_key, workspaceboard_session, ops_portal_or_domain_task,
            current_status, latest_event, last_event_details_json, metadata_json,
            first_seen_at, last_event_at, archived_at
        ) VALUES (
            :message_key, :message_id_norm, :source_message_id, :source_ref, :thread_key,
            :mailbox_lane, :worker, :direction, :email_account, :subject, :from_address, :from_name,
            :to_addresses, :cc_addresses, :bcc_addresses, :header_date, :body_path, :body_chars, :body_summary,
            :task_flow_dedupe_key, :workspaceboard_session, :ops_portal_or_domain_task,
            :current_status, :latest_event, :last_event_details_json, :metadata_json,
            COALESCE(:first_seen_at, CURRENT_TIMESTAMP), :last_event_at, :archived_at
        )
        ON DUPLICATE KEY UPDATE
            message_id_norm = COALESCE(NULLIF(VALUES(message_id_norm), \'\'), message_id_norm),
            source_message_id = COALESCE(NULLIF(VALUES(source_message_id), \'\'), source_message_id),
            source_ref = COALESCE(NULLIF(VALUES(source_ref), \'\'), source_ref),
            thread_key = COALESCE(NULLIF(VALUES(thread_key), \'\'), thread_key),
            mailbox_lane = COALESCE(NULLIF(VALUES(mailbox_lane), \'\'), mailbox_lane),
            worker = COALESCE(NULLIF(VALUES(worker), \'\'), worker),
            direction = COALESCE(NULLIF(VALUES(direction), \'\'), direction),
            email_account = COALESCE(NULLIF(VALUES(email_account), \'\'), email_account),
            subject = COALESCE(NULLIF(VALUES(subject), \'\'), subject),
            from_address = COALESCE(NULLIF(VALUES(from_address), \'\'), from_address),
            from_name = COALESCE(NULLIF(VALUES(from_name), \'\'), from_name),
            to_addresses = COALESCE(VALUES(to_addresses), to_addresses),
            cc_addresses = COALESCE(VALUES(cc_addresses), cc_addresses),
            bcc_addresses = COALESCE(VALUES(bcc_addresses), bcc_addresses),
            header_date = COALESCE(NULLIF(VALUES(header_date), \'\'), header_date),
            body_path = COALESCE(NULLIF(VALUES(body_path), \'\'), body_path),
            body_chars = COALESCE(VALUES(body_chars), body_chars),
            body_summary = COALESCE(NULLIF(VALUES(body_summary), \'\'), body_summary),
            task_flow_dedupe_key = COALESCE(NULLIF(VALUES(task_flow_dedupe_key), \'\'), task_flow_dedupe_key),
            workspaceboard_session = COALESCE(NULLIF(VALUES(workspaceboard_session), \'\'), workspaceboard_session),
            ops_portal_or_domain_task = COALESCE(NULLIF(VALUES(ops_portal_or_domain_task), \'\'), ops_portal_or_domain_task),
            current_status = COALESCE(NULLIF(VALUES(current_status), \'\'), current_status),
            latest_event = VALUES(latest_event),
            last_event_details_json = VALUES(last_event_details_json),
            metadata_json = COALESCE(VALUES(metadata_json), metadata_json),
            last_event_at = VALUES(last_event_at),
            archived_at = COALESCE(VALUES(archived_at), archived_at)'
    );
    $stmt->execute([
        ':message_key' => $messageKey,
        ':message_id_norm' => email_trace_string($message, 'message_id_norm'),
        ':source_message_id' => email_trace_string($message, 'source_message_id'),
        ':source_ref' => email_trace_string($message, 'source_ref'),
        ':thread_key' => email_trace_string($message, 'thread_key'),
        ':mailbox_lane' => email_trace_string($message, 'mailbox_lane'),
        ':worker' => email_trace_string($message, 'worker'),
        ':direction' => email_trace_string($message, 'direction'),
        ':email_account' => email_trace_string($message, 'email_account'),
        ':subject' => email_trace_string($message, 'subject'),
        ':from_address' => email_trace_string($message, 'from_address'),
        ':from_name' => email_trace_string($message, 'from_name'),
        ':to_addresses' => email_trace_json($message['to_addresses'] ?? null),
        ':cc_addresses' => email_trace_json($message['cc_addresses'] ?? null),
        ':bcc_addresses' => email_trace_json($message['bcc_addresses'] ?? null),
        ':header_date' => email_trace_string($message, 'header_date'),
        ':body_path' => email_trace_string($message, 'body_path'),
        ':body_chars' => ($message['body_chars'] ?? '') === '' ? null : (int) $message['body_chars'],
        ':body_summary' => email_trace_string($message, 'body_summary'),
        ':task_flow_dedupe_key' => $taskFlowDedupeKey,
        ':workspaceboard_session' => $workspaceboardSession,
        ':ops_portal_or_domain_task' => $opsTask,
        ':current_status' => $status,
        ':latest_event' => $event,
        ':last_event_details_json' => $detailsJson,
        ':metadata_json' => $metadataJson,
        ':first_seen_at' => email_trace_timestamp(email_trace_string($message, 'first_seen_at')),
        ':last_event_at' => $eventAt,
        ':archived_at' => $archivedAt,
    ]);

    $eventStmt = $pdo->prepare(
        'INSERT INTO ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_EVENTS . ' (
            event, message_key, message_id_norm, source_ref, task_flow_dedupe_key,
            workspaceboard_session, ops_portal_or_domain_task, status, mailbox_lane, worker, details_json
        ) VALUES (
            :event, :message_key, :message_id_norm, :source_ref, :task_flow_dedupe_key,
            :workspaceboard_session, :ops_portal_or_domain_task, :status, :mailbox_lane, :worker, :details_json
        )'
    );
    $eventStmt->execute([
        ':event' => $event,
        ':message_key' => $messageKey,
        ':message_id_norm' => email_trace_string($message, 'message_id_norm'),
        ':source_ref' => email_trace_string($message, 'source_ref'),
        ':task_flow_dedupe_key' => $taskFlowDedupeKey,
        ':workspaceboard_session' => $workspaceboardSession,
        ':ops_portal_or_domain_task' => $opsTask,
        ':status' => $status,
        ':mailbox_lane' => email_trace_string($message, 'mailbox_lane'),
        ':worker' => email_trace_string($message, 'worker'),
        ':details_json' => $detailsJson,
    ]);
}

function email_trace_decode_json_value($value)
{
    if ($value === null || $value === '') {
        return [];
    }
    if (is_array($value)) {
        return $value;
    }
    $decoded = json_decode((string) $value, true);
    return is_array($decoded) ? $decoded : [];
}

function email_trace_query_sent_entries(PDO $pdo, string $mailboxLane, int $limit): array
{
    $limit = max(1, min($limit, 10000));
    $sql = 'SELECT message_key, message_id_norm, source_ref, subject, from_address, to_addresses, cc_addresses, bcc_addresses,
                   header_date, metadata_json, body_summary, current_status, last_event_at
            FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . '
            WHERE direction = :direction
              AND latest_event = :latest_event';
    $params = [
        ':direction' => 'outbound',
        ':latest_event' => 'email_sent',
    ];
    if ($mailboxLane !== '') {
        $sql .= ' AND mailbox_lane = :mailbox_lane';
        $params[':mailbox_lane'] = $mailboxLane;
    }
    $sql .= ' ORDER BY last_event_at DESC LIMIT ' . $limit;
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $rows = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        if (!is_array($row)) {
            continue;
        }
        $metadata = email_trace_decode_json_value($row['metadata_json'] ?? null);
        $rows[] = [
            'message_key' => (string) ($row['message_key'] ?? ''),
            'message_id' => (string) ($row['message_id_norm'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'subject' => (string) ($row['subject'] ?? ''),
            'from' => (string) ($row['from_address'] ?? ''),
            'to' => email_trace_decode_json_value($row['to_addresses'] ?? null),
            'cc' => email_trace_decode_json_value($row['cc_addresses'] ?? null),
            'bcc' => email_trace_decode_json_value($row['bcc_addresses'] ?? null),
            'date' => (string) ($row['header_date'] ?? ''),
            'logged_at' => (string) ($row['last_event_at'] ?? ''),
            'body_summary' => (string) ($row['body_summary'] ?? ''),
            'generic_acknowledgement' => !empty($metadata['generic_acknowledgement']),
            'task_packet_status' => (string) ($row['current_status'] ?? ''),
        ];
    }
    return $rows;
}

function email_trace_query_owner_replies(PDO $pdo, string $mailboxLane, array $owners, int $limit): array
{
    $owners = array_values(array_filter(array_map(static fn ($value) => strtolower(trim((string) $value)), $owners)));
    if ($mailboxLane === '' || $owners === []) {
        return [];
    }
    $limit = max(1, min($limit, 10000));
    $placeholders = implode(',', array_fill(0, count($owners), '?'));
    $sql = 'SELECT source_message_id, source_ref, message_id_norm, subject, from_address, from_name, header_date, body_summary,
                   current_status, latest_event, task_flow_dedupe_key, workspaceboard_session, ops_portal_or_domain_task,
                   metadata_json, last_event_at, archived_at
            FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . '
            WHERE mailbox_lane = ?
              AND direction = ?
              AND from_address IN (' . $placeholders . ')
              AND (archived_at IS NULL)
              AND latest_event <> ?
            ORDER BY last_event_at DESC
            LIMIT ' . $limit;
    $params = array_merge([$mailboxLane, 'inbound'], $owners, ['email_archived']);
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $rows = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        if (!is_array($row)) {
            continue;
        }
        $metadata = email_trace_decode_json_value($row['metadata_json'] ?? null);
        $rows[] = [
            'source_message_id' => (string) ($row['source_message_id'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'message_id_norm' => (string) ($row['message_id_norm'] ?? ''),
            'subject' => (string) ($row['subject'] ?? ''),
            'from' => (string) ($row['from_address'] ?? ''),
            'from_name' => (string) ($row['from_name'] ?? ''),
            'date' => (string) ($row['header_date'] ?? ''),
            'body_summary' => (string) ($row['body_summary'] ?? ''),
            'current_status' => (string) ($row['current_status'] ?? ''),
            'latest_event' => (string) ($row['latest_event'] ?? ''),
            'task_flow_dedupe_key' => (string) ($row['task_flow_dedupe_key'] ?? ''),
            'workspaceboard_session' => (string) ($row['workspaceboard_session'] ?? ''),
            'ops_portal_or_domain_task' => (string) ($row['ops_portal_or_domain_task'] ?? ''),
            'metadata' => $metadata,
            'last_event_at' => (string) ($row['last_event_at'] ?? ''),
        ];
    }
    return $rows;
}

function email_trace_query_active_inbox(PDO $pdo, string $mailboxLane, int $limit): array
{
    if ($mailboxLane === '') {
        return [];
    }
    $limit = max(1, min($limit, 10000));
    $stmt = $pdo->prepare(
        'SELECT m.source_message_id, m.source_ref, m.message_id_norm, m.subject, m.from_address, m.header_date, m.body_path, m.body_chars,
                m.current_status, m.metadata_json, m.first_seen_at, m.last_event_at
           FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . ' m
           INNER JOIN (
                SELECT COALESCE(NULLIF(source_message_id, \'\'), NULLIF(source_ref, \'\'), NULLIF(message_id_norm, \'\')) AS active_source_id,
                       MAX(last_event_at) AS latest_last_event_at
                  FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . '
                 WHERE mailbox_lane = :inner_mailbox_lane
                   AND direction = :inner_direction
                 GROUP BY COALESCE(NULLIF(source_message_id, \'\'), NULLIF(source_ref, \'\'), NULLIF(message_id_norm, \'\'))
           ) latest
             ON latest.active_source_id = COALESCE(NULLIF(m.source_message_id, \'\'), NULLIF(m.source_ref, \'\'), NULLIF(m.message_id_norm, \'\'))
            AND latest.latest_last_event_at = m.last_event_at
          WHERE m.mailbox_lane = :mailbox_lane
            AND m.direction = :direction
            AND m.latest_event = :latest_event
            AND JSON_UNQUOTE(JSON_EXTRACT(m.metadata_json, \'$.active_inbox\')) = \'true\'
          ORDER BY m.last_event_at DESC
          LIMIT ' . $limit
    );
    $stmt->execute([
        ':inner_mailbox_lane' => $mailboxLane,
        ':inner_direction' => 'inbound',
        ':mailbox_lane' => $mailboxLane,
        ':direction' => 'inbound',
        ':latest_event' => 'email_reviewed',
    ]);
    $rows = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        if (!is_array($row)) {
            continue;
        }
        $metadata = email_trace_decode_json_value($row['metadata_json'] ?? null);
        $rows[] = [
            'source_message_id' => (string) ($row['source_message_id'] ?? ''),
            'source_ref' => (string) ($row['source_ref'] ?? ''),
            'message_id' => (string) ($row['message_id_norm'] ?? ''),
            'date' => (string) ($row['header_date'] ?? ''),
            'from' => (string) ($row['from_address'] ?? ''),
            'subject' => (string) ($row['subject'] ?? ''),
            'route' => (string) ($metadata['route'] ?? ''),
            'send_allowed' => (string) ($metadata['send_allowed'] ?? ''),
            'suggestion' => (string) ($metadata['suggestion'] ?? ''),
            'body_path' => (string) ($row['body_path'] ?? ''),
            'body_chars' => ($row['body_chars'] ?? '') === '' ? null : (int) $row['body_chars'],
            'seen_before' => !empty($metadata['seen_before']),
            'first_seen_at' => (string) ($row['first_seen_at'] ?? ''),
            'last_seen_at' => (string) ($row['last_event_at'] ?? ''),
            'status' => 'active_inbox',
        ];
    }
    return $rows;
}

function email_trace_query_seen_source_ids(PDO $pdo, string $mailboxLane, int $limit): array
{
    if ($mailboxLane === '') {
        return [];
    }
    $limit = max(1, min($limit, 50000));
    $stmt = $pdo->prepare(
        'SELECT source_message_id, source_ref, message_id_norm
           FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . '
          WHERE mailbox_lane = :mailbox_lane
            AND direction = :direction
          ORDER BY last_event_at DESC
          LIMIT ' . $limit
    );
    $stmt->execute([
        ':mailbox_lane' => $mailboxLane,
        ':direction' => 'inbound',
    ]);
    $rows = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        if (!is_array($row)) {
            continue;
        }
        $sourceId = trim((string) ($row['source_message_id'] ?? ''));
        if ($sourceId === '') {
            $sourceId = trim((string) ($row['source_ref'] ?? ''));
        }
        if ($sourceId === '') {
            $sourceId = trim((string) ($row['message_id_norm'] ?? ''));
        }
        if ($sourceId === '') {
            continue;
        }
        $rows[] = ['source_message_id' => $sourceId];
    }
    return $rows;
}

$command = $argv[1] ?? '';
if ($command === '' || in_array($command, ['-h', '--help'], true)) {
    email_trace_usage();
    exit($command === '' ? 1 : 0);
}

$pdo = email_trace_pdo();
if ($command === 'install') {
    email_trace_install($pdo);
    fwrite(STDOUT, json_encode(['ok' => true, 'database' => EMAIL_TRACE_DB, 'messages_table' => EMAIL_TRACE_MESSAGES, 'events_table' => EMAIL_TRACE_EVENTS], JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'record') {
    $raw = stream_get_contents(STDIN);
    if ($raw === false || trim($raw) === '') {
        throw new InvalidArgumentException('record requires JSON payload on stdin');
    }
    $payload = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
    if (!is_array($payload)) {
        throw new InvalidArgumentException('record payload must decode to an object');
    }
    email_trace_record($pdo, $payload);
    fwrite(STDOUT, json_encode(['ok' => true], JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'sent-entries') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    $limit = isset($argv[3]) ? (int) $argv[3] : 6000;
    fwrite(STDOUT, json_encode(email_trace_query_sent_entries($pdo, $mailboxLane, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'owner-replies') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    $ownersCsv = trim((string) ($argv[3] ?? ''));
    $limit = isset($argv[4]) ? (int) $argv[4] : 6000;
    $owners = $ownersCsv === '' ? [] : array_map('trim', explode(',', $ownersCsv));
    fwrite(STDOUT, json_encode(email_trace_query_owner_replies($pdo, $mailboxLane, $owners, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'active-inbox') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    $limit = isset($argv[3]) ? (int) $argv[3] : 6000;
    fwrite(STDOUT, json_encode(email_trace_query_active_inbox($pdo, $mailboxLane, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}
if ($command === 'seen-source-ids') {
    $mailboxLane = trim((string) ($argv[2] ?? ''));
    $limit = isset($argv[3]) ? (int) $argv[3] : 20000;
    fwrite(STDOUT, json_encode(email_trace_query_seen_source_ids($pdo, $mailboxLane, $limit), JSON_UNESCAPED_SLASHES) . PHP_EOL);
    exit(0);
}

email_trace_usage();
exit(1);
