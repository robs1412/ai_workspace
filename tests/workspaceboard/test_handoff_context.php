<?php
declare(strict_types=1);
require __DIR__ . '/../../scripts/handoff_session_context.php';
function check(bool $ok, string $label): void { if (!$ok) throw new RuntimeException($label); }
$thread='01a16935-af1e-7503-9c78-aa8d13205095';
$env=['CODEX_SESSION_ID'=>$thread,'WORKSPACEBOARD_SESSION_ID'=>'3339bac44fbdbed5','CODEX_OWNER_USER_ID'=>'1'];
$r=handoff_apply_session_context(['summary'=>'test'], $env);
check($r['workspaceboard_session']==='3339bac44fbdbed5','missing ID inferred');
check($r['metadata']['codex_thread_id']===$thread,'thread preserved');
check(handoff_apply_session_context(['workspaceboard_session'=>$thread],$env)['workspaceboard_session']==='3339bac44fbdbed5','thread UUID corrected');
check(handoff_apply_session_context(['workspaceboard_session'=>'abcdef01'],$env)['workspaceboard_session']==='abcdef01','explicit other target preserved');
check(handoff_apply_session_context([],[])['workspaceboard_session']==='','unknown stays unlinked');
check(handoff_apply_session_context([],['WORKSPACEBOARD_SESSION_ID'=>'bad;command'])['workspaceboard_session']==='','invalid ignored');
$dir=__DIR__.'/map-test-'.getmypid();mkdir($dir);
try {
 file_put_contents($dir.'/'.$thread.'.json',json_encode(['codex_thread_id'=>$thread,'workspaceboard_session'=>'3339bac44fbdbed5','owner_user_id'=>1]));
 unset($env['WORKSPACEBOARD_SESSION_ID']);
 check(handoff_apply_session_context([],$env,$dir)['workspaceboard_session']==='3339bac44fbdbed5','verified fallback');
 $otherThread='01a1696e-f2a4-7e22-9adb-4bb4a68b976e';
 $aliasEnv=['CODEX_THREAD_ID'=>$otherThread,'CODEX_OWNER_USER_ID'=>'1'];
 $alias=handoff_apply_session_context(['workspaceboard_session'=>$thread],$aliasEnv,$dir);
 check($alias['workspaceboard_session']==='3339bac44fbdbed5','known legacy UUID alias resolves after thread changes');
 check($alias['metadata']['codex_thread_id']===$otherThread,'new recording thread retained');
 check($alias['metadata']['requested_session_ref']===$thread,'legacy alias audited');
 $env['CODEX_OWNER_USER_ID']='3';
 check(handoff_apply_session_context([],$env,$dir)['workspaceboard_session']==='','owner isolation');
} finally {unlink($dir.'/'.$thread.'.json');rmdir($dir);}
echo "PASS: 11 handoff context checks\n";
