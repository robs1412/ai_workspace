#!/usr/bin/env php
<?php
declare(strict_types=1);
require_once '/Users/werkstatt/ops/bootstrap.php';
require_once __DIR__ . '/handoff_session_context.php';
$plan = json_decode((string) stream_get_contents(STDIN), true, flags: JSON_THROW_ON_ERROR);
$apply = in_array('--apply', $argv, true);
$rows = $plan['links'] ?? [];
if (!is_array($rows) || count($rows) > 100) throw new InvalidArgumentException('Use a reviewed batch of at most 100 links.');
$pdo = get_event_pdo();
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->exec('SET SESSION max_statement_time=5');
$pdo->beginTransaction();
try {
    $results = [];
    foreach ($rows as $link) {
        $id = (int) ($link['entry_id'] ?? 0);
        $session = (string) ($link['session_id'] ?? '');
        $evidence = trim((string) ($link['evidence'] ?? ''));
        if ($id < 1 || !handoff_valid_terminal_id($session) || !array_key_exists('expected_session', $link) || $evidence === '') {
            throw new InvalidArgumentException('Every link requires entry_id, exact session, expected old value and evidence.');
        }
        $stmt = $pdo->prepare('SELECT workspaceboard_session, metadata_json FROM koval_crm.ai_task_flow_handoff_entries WHERE id=? FOR UPDATE');
        $stmt->execute([$id]); $old = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$old) throw new RuntimeException('Handoff missing: ' . $id);
        $before = (string) ($old['workspaceboard_session'] ?? '');
        if ($before === $session) { $results[] = ['id'=>$id,'session'=>$session,'status'=>'already_linked']; continue; }
        if ($before !== (string) $link['expected_session']) throw new RuntimeException('Session changed since review: ' . $id);
        $metadata = json_decode($old['metadata_json'] ?? '{}', true) ?: [];
        if (!is_array($metadata)) throw new RuntimeException('Invalid metadata: ' . $id);
        $metadata['session_link_backfill'][] = ['at'=>gmdate('c'),'from'=>$before,'to'=>$session,'evidence'=>$evidence,'actor'=>'codex','authorization'=>'Robert requested automatic linking and backfill'];
        if ($apply) {
            $update = $pdo->prepare('UPDATE koval_crm.ai_task_flow_handoff_entries SET workspaceboard_session=?, metadata_json=? WHERE id=?');
            $update->execute([$session,json_encode($metadata,JSON_THROW_ON_ERROR),$id]);
        }
        $results[] = ['id'=>$id,'session'=>$session,'status'=>$apply?'linked':'candidate'];
    }
    if ($apply) $pdo->commit(); else $pdo->rollBack();
    echo json_encode(['ok'=>true,'applied'=>$apply,'results'=>$results], JSON_THROW_ON_ERROR) . PHP_EOL;
} catch (Throwable $e) { if ($pdo->inTransaction()) $pdo->rollBack(); throw $e; }
