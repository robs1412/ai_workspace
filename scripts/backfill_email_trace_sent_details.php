#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const EMAIL_TRACE_DB = 'koval_crm';
const EMAIL_TRACE_MESSAGES = 'ai_email_messages';

function usage(): void
{
    fwrite(STDERR, "Usage: php scripts/backfill_email_trace_sent_details.php [--apply] [--limit N]\n");
}

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

function decode_json(?string $value): array
{
    if ($value === null || trim($value) === '') {
        return [];
    }
    $decoded = json_decode($value, true);
    return is_array($decoded) ? $decoded : [];
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

function sent_draft_path(array $row): string
{
    foreach (['metadata_json', 'last_event_details_json'] as $field) {
        $decoded = decode_json((string) ($row[$field] ?? ''));
        $path = trim((string) ($decoded['draft'] ?? ''));
        if ($path !== '') {
            return $path;
        }
    }
    return '';
}

function safe_sent_artifact(string $path): bool
{
    if ($path === '' || !is_file($path)) {
        return false;
    }
    $real = realpath($path);
    if ($real === false) {
        return false;
    }
    $allowedRoots = [
        '/Users/admin/.nationaloutreach-launch/state/sent/',
        '/Users/admin/.frank-launch/state/sent/',
        '/Users/admin/.avignon-launch/state/sent/',
        '/Users/admin/.asher-launch/state/sent/',
        '/Users/admin/.venetia-launch/state/sent/',
        '/Users/werkstatt/ai_workspace/nationaloutreach/',
        '/Users/werkstatt/ai_workspace/frank/',
        '/Users/werkstatt/ai_workspace/avignon/',
        '/Users/werkstatt/ai_workspace/asher/',
        '/Users/werkstatt/ai_workspace/venetia/',
    ];
    foreach ($allowedRoots as $root) {
        if (str_starts_with($real, $root)) {
            return true;
        }
    }
    return false;
}

$apply = in_array('--apply', $argv, true);
$limit = max(1, min(5000, (int) arg_value($argv, '--limit', '5000')));

if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    usage();
    exit(0);
}

$pdo = get_event_pdo();
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$stmt = $pdo->prepare(
    'SELECT message_key, metadata_json, last_event_details_json, to_addresses, cc_addresses, bcc_addresses, body_summary, body_chars, body_path
       FROM ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . "
      WHERE direction = 'outbound'
        AND (metadata_json LIKE '%\"draft\"%' OR last_event_details_json LIKE '%\"draft\"%')
      ORDER BY last_event_at DESC
      LIMIT :limit"
);
$stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
$stmt->execute();
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];

$update = $pdo->prepare(
    'UPDATE ' . EMAIL_TRACE_DB . '.' . EMAIL_TRACE_MESSAGES . '
        SET to_addresses = :to_addresses,
            cc_addresses = :cc_addresses,
            bcc_addresses = :bcc_addresses,
            body_path = :body_path,
            body_chars = :body_chars,
            body_summary = :body_summary
      WHERE message_key = :message_key'
);

$checked = 0;
$eligible = 0;
$updated = 0;
$missingArtifact = 0;
$missingBody = 0;

foreach ($rows as $row) {
    $checked++;
    $draftPath = sent_draft_path($row);
    if (!safe_sent_artifact($draftPath)) {
        $missingArtifact++;
        continue;
    }
    $data = decode_json(file_get_contents($draftPath) ?: '');
    $to = normalize_addresses($data['to'] ?? []);
    $cc = normalize_addresses($data['cc'] ?? []);
    $bcc = normalize_addresses($data['bcc'] ?? []);
    $body = trim((string) ($data['body'] ?? $data['text'] ?? ''));
    if ($body === '') {
        $missingBody++;
    }
    if ($to === [] && $cc === [] && $bcc === [] && $body === '') {
        continue;
    }
    $eligible++;
    if ($apply) {
        $update->execute([
            ':to_addresses' => json_encode($to, JSON_UNESCAPED_SLASHES),
            ':cc_addresses' => json_encode($cc, JSON_UNESCAPED_SLASHES),
            ':bcc_addresses' => json_encode($bcc, JSON_UNESCAPED_SLASHES),
            ':body_path' => $draftPath,
            ':body_chars' => $body === '' ? null : strlen($body),
            ':body_summary' => $body,
            ':message_key' => (string) $row['message_key'],
        ]);
        $updated++;
    }
}

echo json_encode([
    'ok' => true,
    'apply' => $apply,
    'checked' => $checked,
    'eligible' => $eligible,
    'updated' => $updated,
    'missing_artifact' => $missingArtifact,
    'missing_body' => $missingBody,
], JSON_UNESCAPED_SLASHES) . PHP_EOL;
