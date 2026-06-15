#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const EMAIL_TRACE_DB = 'koval_crm';
const EMAIL_TRACE_MESSAGES = 'ai_email_messages';
const EMAIL_TRACE_EVENTS = 'ai_email_events';

function arg_value(array $argv, string $name, string $default = ''): string
{
    for ($i = 1; $i < count($argv); $i++) {
        if ($argv[$i] === $name && isset($argv[$i + 1])) {
            return (string) $argv[$i + 1];
        }
        if (str_starts_with($argv[$i], $name . '=')) {
            return substr($argv[$i], strlen($name) + 1);
        }
    }
    return $default;
}

function normalize_message_id($value): string
{
    return strtolower(trim((string) $value, " \t\n\r\0\x0B<>"));
}

function normalize_addresses($value): array
{
    if (is_array($value)) {
        return array_values(array_filter(array_map(static fn ($item) => trim((string) $item), $value)));
    }
    $text = trim((string) $value);
    if ($text === '') {
        return [];
    }
    return array_values(array_filter(array_map('trim', explode(',', $text))));
}

function json_value($value): ?string
{
    if ($value === null || $value === '' || $value === []) {
        return null;
    }
    return json_encode($value, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
}

function timestamp_value($value): string
{
    $raw = trim((string) $value);
    if ($raw === '') {
        return (new DateTimeImmutable('now'))->format('Y-m-d H:i:s');
    }
    try {
        return (new DateTimeImmutable($raw))->format('Y-m-d H:i:s');
    } catch (Throwable $e) {
        return (new DateTimeImmutable('now'))->format('Y-m-d H:i:s');
    }
}

function load_json_file(string $path): array
{
    if ($path === '' || !is_file($path) || !is_readable($path)) {
        return [];
    }
    $decoded = json_decode(file_get_contents($path) ?: '', true);
    return is_array($decoded) ? $decoded : [];
}

function sent_artifact_candidates(string $lane, string $draft): array
{
    $draft = trim($draft);
    if ($draft === '') {
        return [];
    }
    if (str_starts_with($draft, '/')) {
        return [$draft];
    }
    $roots = [
        "/Users/admin/.{$lane}-launch/state/sent",
        "/Users/admin/.{$lane}-launch/state",
        "/Users/werkstatt/ai_workspace/{$lane}/sent",
        "/Users/werkstatt/ai_workspace/{$lane}",
    ];
    $candidates = [];
    foreach ($roots as $root) {
        $candidates[] = $root . '/' . $draft;
        foreach (glob($root . '/' . $draft . '.sent-*.json') ?: [] as $path) {
            $candidates[] = $path;
        }
        foreach (glob($root . '/' . $draft . '.sent-repaired-*.json') ?: [] as $path) {
            $candidates[] = $path;
        }
    }
    return array_values(array_unique($candidates));
}

function sent_artifact_data(string $lane, array $row): array
{
    foreach (sent_artifact_candidates($lane, (string) ($row['draft'] ?? '')) as $path) {
        $data = load_json_file($path);
        if ($data !== []) {
            $data['_artifact_path'] = $path;
            return $data;
        }
    }
    return [];
}

function sent_log_sources(): array
{
    return [
        ['lane' => 'avignon', 'worker' => 'Avignon', 'path' => '/Users/admin/.avignon-launch/state/sent-log.jsonl'],
        ['lane' => 'avignon', 'worker' => 'Avignon', 'path' => '/Users/werkstatt/ai_workspace/avignon/sent-log.jsonl'],
        ['lane' => 'asher', 'worker' => 'Asher', 'path' => '/Users/admin/.asher-launch/state/sent-log.jsonl'],
        ['lane' => 'asher', 'worker' => 'Asher', 'path' => '/Users/werkstatt/ai_workspace/asher/sent-log.jsonl'],
        ['lane' => 'venetia', 'worker' => 'Venetia', 'path' => '/Users/admin/.venetia-launch/state/sent-log.jsonl'],
        ['lane' => 'venetia', 'worker' => 'Venetia', 'path' => '/Users/werkstatt/ai_workspace/venetia/sent-log.jsonl'],
    ];
}

function lane_identity(string $lane): array
{
    return match ($lane) {
        'avignon' => [
            'email_account' => 'avignon.rose@kovaldistillery.com',
            'from_address' => 'Avignon Rose <avignon.rose@kovaldistillery.com>',
            'from_name' => 'Avignon Rose',
        ],
        'asher' => [
            'email_account' => 'asher@thecultivater.com',
            'from_address' => 'Asher Wilde <asher@thecultivater.com>',
            'from_name' => 'Asher Wilde',
        ],
        'venetia' => [
            'email_account' => 'venetia@thecultivater.com',
            'from_address' => 'Venetia Tempest-Dunn <venetia@thecultivater.com>',
            'from_name' => 'Venetia Tempest-Dunn',
        ],
        default => [
            'email_account' => '',
            'from_address' => '',
            'from_name' => '',
        ],
    };
}

$apply = in_array('--apply', $argv, true);
$limit = max(1, min(10000, (int) arg_value($argv, '--limit', '10000')));
$onlyLane = strtolower(trim(arg_value($argv, '--lane', '')));

$pdo = get_event_pdo();
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$messageStmt = $pdo->prepare(
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
        :first_seen_at, :last_event_at, NULL
    )
    ON DUPLICATE KEY UPDATE
        source_ref = COALESCE(NULLIF(VALUES(source_ref), \'\'), source_ref),
        mailbox_lane = VALUES(mailbox_lane),
        worker = VALUES(worker),
        direction = VALUES(direction),
        email_account = COALESCE(NULLIF(email_account, \'\'), NULLIF(VALUES(email_account), \'\')),
        subject = COALESCE(NULLIF(VALUES(subject), \'\'), subject),
        from_address = COALESCE(NULLIF(from_address, \'\'), NULLIF(VALUES(from_address), \'\')),
        from_name = COALESCE(NULLIF(from_name, \'\'), NULLIF(VALUES(from_name), \'\')),
        to_addresses = COALESCE(VALUES(to_addresses), to_addresses),
        cc_addresses = COALESCE(VALUES(cc_addresses), cc_addresses),
        bcc_addresses = COALESCE(VALUES(bcc_addresses), bcc_addresses),
        header_date = COALESCE(NULLIF(VALUES(header_date), \'\'), header_date),
        body_path = COALESCE(NULLIF(VALUES(body_path), \'\'), body_path),
        body_chars = COALESCE(VALUES(body_chars), body_chars),
        body_summary = COALESCE(NULLIF(VALUES(body_summary), \'\'), body_summary),
        current_status = VALUES(current_status),
        latest_event = VALUES(latest_event),
        last_event_details_json = VALUES(last_event_details_json),
        metadata_json = VALUES(metadata_json),
        last_event_at = VALUES(last_event_at)'
);

$eventStmt = $pdo->prepare(
    'INSERT INTO ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_EVENTS . ' (
        event, message_key, message_id_norm, source_ref, task_flow_dedupe_key,
        workspaceboard_session, ops_portal_or_domain_task, status, mailbox_lane, worker, details_json
    ) VALUES (
        :event, :message_key, :message_id_norm, :source_ref, :task_flow_dedupe_key,
        :workspaceboard_session, :ops_portal_or_domain_task, :status, :mailbox_lane, :worker, :details_json
    )'
);

$checked = 0;
$eligible = 0;
$imported = 0;
$skippedNoMessage = 0;

foreach (sent_log_sources() as $source) {
    if ($onlyLane !== '' && $source['lane'] !== $onlyLane) {
        continue;
    }
    $path = $source['path'];
    if (!is_file($path)) {
        continue;
    }
    $handle = fopen($path, 'r');
    if ($handle === false) {
        continue;
    }
    while (($line = fgets($handle)) !== false) {
        if ($checked >= $limit) {
            break 2;
        }
        $checked++;
        $row = json_decode(trim($line), true);
        if (!is_array($row)) {
            continue;
        }
        $event = (string) ($row['event'] ?? 'email_sent');
        if (str_contains($event, 'failed')) {
            continue;
        }
        $messageId = normalize_message_id($row['message_id'] ?? '');
        if ($messageId === '') {
            $skippedNoMessage++;
            continue;
        }
        $artifact = sent_artifact_data($source['lane'], $row);
        $to = normalize_addresses($row['to_addresses'] ?? $row['to'] ?? $artifact['to'] ?? []);
        $cc = normalize_addresses($row['cc_addresses'] ?? $row['cc'] ?? $artifact['cc'] ?? []);
        $bcc = normalize_addresses($row['bcc_addresses'] ?? $row['bcc'] ?? $artifact['bcc'] ?? []);
        $body = trim((string) ($artifact['body'] ?? $artifact['text'] ?? ''));
        $identity = lane_identity($source['lane']);
        $from = (string) ($row['from'] ?? $artifact['from'] ?? $identity['from_address']);
        $fromName = (string) ($artifact['from_name'] ?? $identity['from_name']);
        $subject = (string) ($row['subject'] ?? $artifact['subject'] ?? '');
        $sourceRef = (string) ($row['source_ref'] ?? $artifact['source_ref'] ?? '');
        $date = (string) ($row['date'] ?? $row['logged_at'] ?? $row['started_at'] ?? $artifact['sent_metadata']['sent_at'] ?? '');
        $messageKey = 'email-' . substr(hash('sha256', implode('|', [$source['lane'], $messageId, $sourceRef, strtolower($subject), 'outbound'])), 0, 32);
        $metadata = [
            'event' => 'sent_log_import',
            'sent_log_path' => $path,
            'draft' => (string) ($row['draft'] ?? ''),
            'sent_folder' => (string) ($row['sent_folder'] ?? ''),
            'raw_worker' => (string) ($row['worker'] ?? $source['worker']),
        ];
        $details = [
            'event' => 'sent_log_import',
            'message_id' => $messageId,
            'sent_log_path' => $path,
            'artifact_path' => (string) ($artifact['_artifact_path'] ?? ''),
        ];
        $eligible++;
        if ($apply) {
            $params = [
                ':message_key' => $messageKey,
                ':message_id_norm' => $messageId,
                ':source_message_id' => $messageId,
                ':source_ref' => $sourceRef ?: $messageId,
                ':thread_key' => substr(hash('sha256', implode('|', [$source['lane'], strtolower($subject), strtolower($from)])), 0, 32),
                ':mailbox_lane' => $source['lane'],
                ':worker' => $source['worker'],
                ':direction' => 'outbound',
                ':email_account' => $identity['email_account'],
                ':subject' => $subject,
                ':from_address' => $from,
                ':from_name' => $fromName,
                ':to_addresses' => json_value($to),
                ':cc_addresses' => json_value($cc),
                ':bcc_addresses' => json_value($bcc),
                ':header_date' => $date,
                ':body_path' => (string) ($artifact['_artifact_path'] ?? ''),
                ':body_chars' => $body === '' ? null : strlen($body),
                ':body_summary' => $body,
                ':task_flow_dedupe_key' => '',
                ':workspaceboard_session' => '',
                ':ops_portal_or_domain_task' => (string) ($row['task_id'] ?? ''),
                ':current_status' => 'reported',
                ':latest_event' => 'sent_log_import',
                ':last_event_details_json' => json_value($details),
                ':metadata_json' => json_value($metadata),
                ':first_seen_at' => timestamp_value($date),
                ':last_event_at' => timestamp_value($date),
            ];
            $messageStmt->execute($params);
            $eventStmt->execute([
                ':event' => 'sent_log_import',
                ':message_key' => $messageKey,
                ':message_id_norm' => $messageId,
                ':source_ref' => $sourceRef ?: $messageId,
                ':task_flow_dedupe_key' => '',
                ':workspaceboard_session' => '',
                ':ops_portal_or_domain_task' => (string) ($row['task_id'] ?? ''),
                ':status' => 'reported',
                ':mailbox_lane' => $source['lane'],
                ':worker' => $source['worker'],
                ':details_json' => json_value($details) ?? '{}',
            ]);
            $imported++;
        }
    }
    fclose($handle);
}

echo json_encode([
    'ok' => true,
    'apply' => $apply,
    'checked' => $checked,
    'eligible' => $eligible,
    'imported' => $imported,
    'skipped_no_message_id' => $skippedNoMessage,
], JSON_UNESCAPED_SLASHES) . PHP_EOL;
