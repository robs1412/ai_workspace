#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

const AI_MANAGER_CHAT_ADAPTER_RECORDER = '/Users/werkstatt/ai_workspace/scripts/ai_manager_input_recorder.php';
const AI_MANAGER_CHAT_ADAPTER_MCP_ENV = '/Users/werkstatt/ai_workspace/scripts/mcp_runtime_env.py';
const AI_MANAGER_CHAT_ADAPTER_PAPERS_WRITER = '/Users/werkstatt/ai_workspace/scripts/papers_write_note.py';

function usage(): void
{
    fwrite(STDERR, "Usage: php scripts/ai_manager_chat_entry_adapter.php [--message TEXT] [--user-id N] [--user-label TEXT] [--source-path TEXT] [--source-channel TEXT] [--related-session-id TEXT] [--related-task-id TEXT] [--related-taskflow-key TEXT] [--proof-marker TEXT] [--status TEXT] [--durable] [--papers-kind TEXT] [--papers-title TEXT] [--papers-path TEXT] [--papers-summary TEXT] [--papers-tags TEXT] [--papers-created-by TEXT] [--papers-dry-run] [--skip-db]\n");
}

function currentCdtStamp(): array
{
    $now = new DateTimeImmutable('now', new DateTimeZone('America/Chicago'));
    return [
        'date' => $now->format('Y-m-d'),
        'stamp' => $now->format('Y-m-d H:i T'),
    ];
}

function readStdinText(): string
{
    $raw = stream_get_contents(STDIN);
    return trim((string) $raw);
}

function slugify(string $value): string
{
    $value = strtolower(trim($value));
    $value = preg_replace('/[^a-z0-9]+/', '-', $value) ?? '';
    $value = trim($value, '-');
    return $value !== '' ? substr($value, 0, 80) : 'durable-note';
}

function firstMeaningfulLine(string $message): string
{
    foreach (preg_split("/\r\n?|\n/", trim($message)) as $line) {
        $line = trim((string) $line);
        if ($line !== '') {
            return $line;
        }
    }
    return 'Durable AI Manager note';
}

function parseArgs(array $argv): array
{
    $options = [
        'message' => '',
        'user_id' => null,
        'user_label' => 'Robert',
        'source_path' => 'ai-manager-mode',
        'source_channel' => 'ai-manager-chat',
        'related_session_id' => '',
        'related_task_id' => '',
        'related_taskflow_key' => '',
        'proof_marker' => '',
        'status' => 'captured',
        'durable' => false,
        'papers_kind' => 'decision',
        'papers_title' => '',
        'papers_path' => '',
        'papers_summary' => '',
        'papers_tags' => '',
        'papers_created_by' => 'codex-ai-manager',
        'papers_dry_run' => false,
        'skip_db' => false,
    ];

    for ($i = 1; $i < count($argv); $i++) {
        $arg = $argv[$i];
        if ($arg === '--append-daily') {
            throw new InvalidArgumentException('Legacy daily-input Markdown writes are disabled; record AI Manager inputs in DB only.');
        }
        if ($arg === '--skip-daily') {
            throw new InvalidArgumentException('Legacy daily-input Markdown writes are disabled; --skip-daily is no longer needed.');
        }
        if ($arg === '--skip-db') {
            $options['skip_db'] = true;
            continue;
        }
        if ($arg === '--durable') {
            $options['durable'] = true;
            continue;
        }
        if ($arg === '--papers-dry-run') {
            $options['papers_dry_run'] = true;
            continue;
        }
        if ($arg === '--message' && isset($argv[$i + 1])) {
            $options['message'] = (string) $argv[++$i];
            continue;
        }
        if (preg_match('/^--([a-z0-9-]+)$/i', $arg, $matches) && isset($argv[$i + 1])) {
            $key = str_replace('-', '_', $matches[1]);
            if (array_key_exists($key, $options)) {
                $options[$key] = (string) $argv[++$i];
                continue;
            }
        }
        if (preg_match('/^--([^=]+)=(.*)$/', $arg, $matches)) {
            $key = str_replace('-', '_', $matches[1]);
            if (in_array($key, ['append_daily', 'skip_daily'], true)) {
                throw new InvalidArgumentException('Legacy daily-input Markdown writes are disabled; record AI Manager inputs in DB only.');
            }
            if (array_key_exists($key, $options)) {
                if (in_array($key, ['skip_db', 'durable', 'papers_dry_run'], true)) {
                    $options[$key] = in_array(strtolower($matches[2]), ['1', 'true', 'yes', 'on'], true);
                } else {
                    $options[$key] = $matches[2];
                }
            }
        }
    }

    return $options;
}

function normalizeMessage(string $message): string
{
    $message = trim($message);
    if ($message === '') {
        return '';
    }
    return preg_replace("/\r\n?/", "\n", $message) ?? $message;
}

function buildUuid(string $message): string
{
    return 'ai-manager-chat-' . gmdate('YmdHis') . '-' . substr(hash('sha256', $message . '|' . microtime(true)), 0, 12);
}

function invokeRecorder(array $payload): array
{
    $cmd = ['php', AI_MANAGER_CHAT_ADAPTER_RECORDER, 'record'];
    $descriptors = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $process = proc_open($cmd, $descriptors, $pipes, null, null, ['bypass_shell' => true]);
    if (!is_resource($process)) {
        throw new RuntimeException('Unable to start AI Manager recorder.');
    }
    fwrite($pipes[0], json_encode($payload, JSON_UNESCAPED_SLASHES));
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $exit = proc_close($process);
    if ($exit !== 0) {
        $message = trim((string) $stderr);
        throw new RuntimeException($message !== '' ? $message : 'AI Manager recorder failed.');
    }
    $decoded = json_decode($stdout ?: 'null', true);
    if (!is_array($decoded)) {
        throw new RuntimeException('AI Manager recorder returned invalid JSON.');
    }
    return $decoded;
}

function buildPapersDefaults(array $options, string $message): array
{
    $stampInfo = currentCdtStamp();
    $headline = firstMeaningfulLine($message);
    $slug = slugify($headline);
    $kind = slugify((string) $options['papers_kind']);
    $path = trim((string) $options['papers_path']);
    if ($path === '') {
        $path = sprintf('ai-manager/durability/%s-%s-%s.md', $stampInfo['date'], $kind, $slug);
    }
    $title = trim((string) $options['papers_title']);
    if ($title === '') {
        $title = sprintf('AI Manager %s - %s', ucfirst($kind), $headline);
    }
    $summary = trim((string) $options['papers_summary']);
    if ($summary === '') {
        $summary = sprintf('Non-secret AI Manager durable %s.', $kind);
    }
    $tags = trim((string) $options['papers_tags']);
    if ($tags === '') {
        $tags = implode(',', ['ai-manager', 'durable', $kind]);
    }
    return [
        'date' => $stampInfo['date'],
        'stamp' => $stampInfo['stamp'],
        'path' => $path,
        'title' => $title,
        'summary' => $summary,
        'tags' => $tags,
        'created_by' => trim((string) $options['papers_created_by']) !== ''
            ? trim((string) $options['papers_created_by'])
            : 'codex-ai-manager',
    ];
}

function buildPapersMarkdown(string $message, array $payload, array $papersConfig, ?array $recorderResult): string
{
    $sections = [];
    $sections[] = '# ' . $papersConfig['title'];
    $sections[] = '';
    $sections[] = 'Recorded: ' . $papersConfig['stamp'];
    $sections[] = '';
    $sections[] = '## Durable Note';
    $sections[] = '';
    $sections[] = $message;
    $sections[] = '';
    $sections[] = '## Source Context';
    $sections[] = '';
    $sections[] = '- Source channel: `' . ($payload['source_channel'] ?: 'unknown') . '`';
    $sections[] = '- Source path: `' . ($payload['source_path'] ?: 'unknown') . '`';
    $sections[] = '- Status: `' . ($payload['status'] ?: 'captured') . '`';
    if (!empty($payload['proof_marker'])) {
        $sections[] = '- Proof marker: `' . $payload['proof_marker'] . '`';
    }
    if (!empty($payload['related_session_id'])) {
        $sections[] = '- Related session: `' . $payload['related_session_id'] . '`';
    }
    if (!empty($payload['related_task_id'])) {
        $sections[] = '- Related task: `' . $payload['related_task_id'] . '`';
    }
    if (!empty($payload['related_taskflow_key'])) {
        $sections[] = '- Related Task Flow key: `' . $payload['related_taskflow_key'] . '`';
    }
    if (is_array($recorderResult) && isset($recorderResult['input_id'])) {
        $sections[] = '- AI Manager input row: `' . $recorderResult['input_id'] . '`';
    }
    $sections[] = '';
    $sections[] = 'This note is intentionally limited to non-secret durable operating context.';
    $sections[] = '';
    return implode("\n", $sections);
}

function invokePapersWriter(string $body, array $papersConfig, bool $dryRun): array
{
    $tempFile = tempnam(sys_get_temp_dir(), 'aimgr-papers-');
    if ($tempFile === false) {
        throw new RuntimeException('Unable to allocate temporary file for Papers write.');
    }
    file_put_contents($tempFile, $body);
    $cmd = [
        '/usr/local/bin/python3.13',
        AI_MANAGER_CHAT_ADAPTER_MCP_ENV,
        'exec',
        '--',
        '/usr/local/bin/python3.13',
        AI_MANAGER_CHAT_ADAPTER_PAPERS_WRITER,
        '--path',
        $papersConfig['path'],
        '--title',
        $papersConfig['title'],
        '--summary',
        $papersConfig['summary'],
        '--tags',
        $papersConfig['tags'],
        '--created-by',
        $papersConfig['created_by'],
        '--input-file',
        $tempFile,
    ];
    if ($dryRun) {
        $cmd[] = '--dry-run';
    }
    $descriptors = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $process = proc_open($cmd, $descriptors, $pipes, null, null, ['bypass_shell' => true]);
    if (!is_resource($process)) {
        @unlink($tempFile);
        throw new RuntimeException('Unable to start Papers writer.');
    }
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $exit = proc_close($process);
    @unlink($tempFile);
    if ($exit !== 0) {
        $message = trim((string) $stderr);
        throw new RuntimeException($message !== '' ? $message : 'Papers writer failed.');
    }
    $decoded = json_decode($stdout ?: 'null', true);
    if (!is_array($decoded)) {
        throw new RuntimeException('Papers writer returned invalid JSON.');
    }
    return $decoded;
}

try {
    $options = parseArgs($argv);
    $message = normalizeMessage($options['message'] !== '' ? (string) $options['message'] : readStdinText());
    if ($message === '') {
        throw new InvalidArgumentException('Missing message text.');
    }

    if ($options['skip_db']) {
        throw new InvalidArgumentException('DB recording is the canonical AI Manager input path; --skip-db is reserved for tests and disabled here.');
    }

    $payload = [
        'input_uuid' => buildUuid($message),
        'user_id' => $options['user_id'] !== null && $options['user_id'] !== '' ? (int) $options['user_id'] : null,
        'user_label' => (string) $options['user_label'],
        'source_channel' => (string) $options['source_channel'],
        'source_path' => (string) $options['source_path'],
        'input_text' => $message,
        'related_session_id' => (string) $options['related_session_id'],
        'related_task_id' => (string) $options['related_task_id'],
        'related_taskflow_key' => (string) $options['related_taskflow_key'],
        'status' => (string) $options['status'],
        'proof_marker' => (string) $options['proof_marker'],
        'metadata' => [
            'transport' => 'ai_manager_chat_entry_adapter',
            'origin' => 'ai_manager_control_lane',
            'daily_inputs' => 'disabled',
            'db' => 'record',
        ],
    ];

    $recorderResult = null;
    $recorderResult = invokeRecorder($payload);

    $papersResult = null;
    if ($options['durable']) {
        $papersConfig = buildPapersDefaults($options, $message);
        $papersBody = buildPapersMarkdown($message, $payload, $papersConfig, $recorderResult);
        $papersResult = invokePapersWriter($papersBody, $papersConfig, (bool) $options['papers_dry_run']);
    }

    echo json_encode([
        'ok' => true,
        'recorder' => $recorderResult,
        'papers' => $papersResult,
        'input_uuid' => $payload['input_uuid'],
    ], JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit(0);
} catch (Throwable $error) {
    fwrite(STDERR, $error->getMessage() . PHP_EOL);
    exit(1);
}
