#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

function usage(): void
{
    fwrite(STDERR, "Usage: php scripts/stale_task_cleanup.php [--rules=path] [--apply] [--json]\n");
}

function read_rules(string $path): array
{
    if (!is_file($path)) {
        throw new RuntimeException("Rules file not found: {$path}");
    }
    $raw = file_get_contents($path);
    if ($raw === false) {
        throw new RuntimeException("Unable to read rules file: {$path}");
    }
    $decoded = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
    if (!is_array($decoded)) {
        throw new RuntimeException("Rules file must decode to an array: {$path}");
    }
    return $decoded;
}

function fetch_task(PDO $pdo, int $taskId): ?array
{
    $stmt = $pdo->prepare(
        "SELECT act.activityid, act.subject, act.status, act.due_date, act.date_start, act.sendnotification,
                ent.smownerid, ent.smcreatorid, ent.deleted
           FROM koval_crm.vtiger_activity act
           JOIN koval_crm.vtiger_crmentity ent ON ent.crmid = act.activityid
          WHERE act.activityid = ?
          LIMIT 1"
    );
    $stmt->execute([$taskId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return is_array($row) ? $row : null;
}

function mark_task_completed_silent(PDO $pdo, int $taskId): void
{
    $stmt = $pdo->prepare(
        "UPDATE koval_crm.vtiger_activity act
           JOIN koval_crm.vtiger_crmentity ent ON ent.crmid = act.activityid
           SET act.status = 'Completed',
               act.sendnotification = 0
         WHERE act.activityid = ?
           AND ent.deleted = 0"
    );
    $stmt->execute([$taskId]);
}

function normalize_status(?string $status): string
{
    return trim((string) $status);
}

function subject_matches(array $task, array $rule): bool
{
    $expected = trim((string) ($rule['expected_subject'] ?? ''));
    if ($expected === '') {
        return true;
    }
    return trim((string) ($task['subject'] ?? '')) === $expected;
}

function owner_matches(array $task, array $rule): bool
{
    $expected = (int) ($rule['expected_owner_id'] ?? 0);
    if ($expected <= 0) {
        return true;
    }
    return (int) ($task['smownerid'] ?? 0) === $expected;
}

function file_contains_all(array $check): array
{
    $path = (string) ($check['path'] ?? '');
    if ($path === '' || !is_file($path)) {
        return [false, "missing file {$path}"];
    }
    $content = file_get_contents($path);
    if ($content === false) {
        return [false, "unreadable file {$path}"];
    }
    $all = is_array($check['all'] ?? null) ? $check['all'] : [];
    foreach ($all as $needle) {
        $needle = (string) $needle;
        if ($needle === '') {
            continue;
        }
        if (strpos($content, $needle) === false) {
            return [false, "missing marker in {$path}: {$needle}"];
        }
    }
    return [true, "matched file markers in {$path}"];
}

function evaluate_rule(PDO $pdo, array $rule): array
{
    $taskId = (int) ($rule['task_id'] ?? 0);
    if ($taskId <= 0) {
        return [
            'rule_id' => (string) ($rule['rule_id'] ?? ''),
            'task_id' => $taskId,
            'status' => 'invalid-rule',
            'reason' => 'missing task_id',
            'closable' => false,
            'evidence' => [],
        ];
    }

    $task = fetch_task($pdo, $taskId);
    if (!is_array($task) || (int) ($task['deleted'] ?? 0) !== 0) {
        return [
            'rule_id' => (string) ($rule['rule_id'] ?? ''),
            'task_id' => $taskId,
            'status' => 'missing-task',
            'reason' => 'task missing or deleted',
            'closable' => false,
            'evidence' => [],
        ];
    }

    $taskStatus = normalize_status((string) ($task['status'] ?? ''));
    if (in_array($taskStatus, ['Completed', 'Cancelled', 'Canceled'], true)) {
        return [
            'rule_id' => (string) ($rule['rule_id'] ?? ''),
            'task_id' => $taskId,
            'status' => 'already-closed',
            'reason' => "task already {$taskStatus}",
            'closable' => false,
            'task' => $task,
            'evidence' => [],
        ];
    }

    if (!subject_matches($task, $rule)) {
        return [
            'rule_id' => (string) ($rule['rule_id'] ?? ''),
            'task_id' => $taskId,
            'status' => 'guard-failed',
            'reason' => 'subject mismatch',
            'closable' => false,
            'task' => $task,
            'evidence' => [],
        ];
    }
    if (!owner_matches($task, $rule)) {
        return [
            'rule_id' => (string) ($rule['rule_id'] ?? ''),
            'task_id' => $taskId,
            'status' => 'guard-failed',
            'reason' => 'owner mismatch',
            'closable' => false,
            'task' => $task,
            'evidence' => [],
        ];
    }

    $evidence = [];
    $closable = true;

    $taskChecks = is_array($rule['require_task_statuses'] ?? null) ? $rule['require_task_statuses'] : [];
    foreach ($taskChecks as $check) {
        $depId = (int) ($check['task_id'] ?? 0);
        $dep = $depId > 0 ? fetch_task($pdo, $depId) : null;
        $allowed = is_array($check['allowed_statuses'] ?? null) ? $check['allowed_statuses'] : [];
        $depStatus = normalize_status((string) ($dep['status'] ?? ''));
        if (!is_array($dep)) {
            $closable = false;
            $evidence[] = "missing dependency task {$depId}";
            continue;
        }
        if ($allowed !== [] && !in_array($depStatus, array_map('strval', $allowed), true)) {
            $closable = false;
            $evidence[] = "dependency task {$depId} status {$depStatus} not in [" . implode(', ', $allowed) . "]";
            continue;
        }
        $evidence[] = "dependency task {$depId} status {$depStatus}";
    }

    $fileChecks = is_array($rule['require_file_contains'] ?? null) ? $rule['require_file_contains'] : [];
    foreach ($fileChecks as $check) {
        [$ok, $detail] = file_contains_all(is_array($check) ? $check : []);
        if (!$ok) {
            $closable = false;
        }
        $evidence[] = $detail;
    }

    return [
        'rule_id' => (string) ($rule['rule_id'] ?? ''),
        'task_id' => $taskId,
        'status' => $closable ? 'closable' : 'blocked',
        'reason' => (string) ($rule['close_reason'] ?? ''),
        'closable' => $closable,
        'task' => $task,
        'evidence' => $evidence,
    ];
}

$options = getopt('', ['rules::', 'apply', 'json']);
$rulesPath = (string) ($options['rules'] ?? (__DIR__ . '/stale_task_cleanup_rules.json'));
$apply = array_key_exists('apply', $options);
$asJson = array_key_exists('json', $options);

try {
    $rules = read_rules($rulesPath);
    $pdo = get_tracktime_pdo();
    $results = [];
    $changed = 0;
    $closable = 0;
    foreach ($rules as $rule) {
        if (!is_array($rule)) {
            continue;
        }
        $result = evaluate_rule($pdo, $rule);
        if (($result['closable'] ?? false) === true) {
            $closable++;
            if ($apply) {
                mark_task_completed_silent($pdo, (int) $result['task_id']);
                $result['status'] = 'closed';
                $result['task_after'] = fetch_task($pdo, (int) $result['task_id']);
                $changed++;
            } else {
                $result['status'] = 'would-close';
            }
        }
        $results[] = $result;
    }

    $payload = [
        'ok' => true,
        'checked_at' => gmdate('c'),
        'rules_path' => $rulesPath,
        'apply' => $apply,
        'checked' => count($results),
        'closable' => $closable,
        'changed' => $changed,
        'items' => $results,
    ];
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit(0);
} catch (Throwable $e) {
    $payload = [
        'ok' => false,
        'checked_at' => gmdate('c'),
        'rules_path' => $rulesPath,
        'apply' => $apply,
        'error' => $e->getMessage(),
    ];
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
    exit(1);
}
