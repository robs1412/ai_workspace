#!/usr/local/bin/python3.13

from __future__ import annotations

import json
import subprocess
from pathlib import Path


WORKDIR = Path("/Users/werkstatt/ai_workspace")
PHP = "/usr/local/bin/php"


def run_sql(sql: str) -> str:
    cmd = [
        PHP,
        "-r",
        (
            "require '/Users/werkstatt/ops/bootstrap.php'; "
            "$pdo=get_event_pdo(); "
            "$sql=stream_get_contents(STDIN); "
            "$stmt=$pdo->prepare($sql); "
            "$stmt->execute(); "
            "$rows=$stmt->fetchAll(PDO::FETCH_ASSOC) ?: []; "
            "echo json_encode($rows, JSON_UNESCAPED_SLASHES);"
        ),
    ]
    result = subprocess.run(
        cmd,
        input=sql,
        text=True,
        capture_output=True,
        cwd=WORKDIR,
        check=True,
    )
    return result.stdout.strip()


def run_exec(sql: str) -> None:
    cmd = [
        PHP,
        "-r",
        (
            "require '/Users/werkstatt/ops/bootstrap.php'; "
            "$pdo=get_event_pdo(); "
            "$sql=stream_get_contents(STDIN); "
            "$pdo->exec($sql);"
        ),
    ]
    subprocess.run(cmd, input=sql, text=True, cwd=WORKDIR, check=True)


def main() -> int:
    before = json.loads(
        run_sql(
            """
SELECT COUNT(*) AS waiting_count
FROM koval_crm.ai_task_flow_packets
WHERE dedupe_key LIKE 'taskflow-owner-reply-%'
  AND status = 'waiting'
  AND (
    due_or_trigger = 'owner_reply_pending_response'
    OR COALESCE(JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.recurrence_rule')), '') <> 'owner_reply_daily_repeat'
  )
"""
        )
        or "[]"
    )
    waiting_count = int((before[0] or {}).get("waiting_count") or 0) if before else 0
    update_sql = """
UPDATE koval_crm.ai_task_flow_packets
SET due_or_trigger = CASE
        WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
        ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
    END,
    packet_json = JSON_SET(
        COALESCE(packet_json, JSON_OBJECT()),
        '$.due_or_trigger', CASE
            WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
            ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
        END,
        '$.verification_readback', CASE
            WHEN JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.verification_readback')) LIKE '%daily repeat reminder enabled.%'
                THEN JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.verification_readback'))
            WHEN JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.verification_readback')) = 'owner_reply_pending_response: newest primary-owner reply has no later assistant sent proof yet.'
                THEN 'owner_reply_pending_response: newest primary-owner reply has no later assistant sent proof yet; daily repeat reminder enabled.'
            ELSE CONCAT(TRIM(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.verification_readback')), 'owner_reply_pending_response')), '; daily repeat reminder enabled.')
        END,
        '$.next_update', CONCAT('Daily repeat reminder set for ',
            CASE
                WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
                ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
            END,
            '; worker must send result, domain proof, or one exact blocker/question.'),
        '$.due_or_next_update', CONCAT('Daily repeat reminder at ',
            CASE
                WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
                ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
            END,
            '; first worker focus within 2 minutes when due; result or exact blocker within 5 minutes'),
        '$.recurrence_enabled', 'true',
        '$.recurrence_kind', 'followup',
        '$.recurrence_cadence', 'daily',
        '$.recurrence_pattern', 'daily owner reply follow-up',
        '$.recurrence_rule', 'owner_reply_daily_repeat',
        '$.recurrence_anchor', CASE
            WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
            ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
        END,
        '$.recurrence_interval', '1',
        '$.recurrence_time', CASE
            WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN DATE_FORMAT(STR_TO_DATE(due_or_trigger, '%Y-%m-%d %H:%i:%s'), '%H:%i:%s')
            ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%H:%i:%s')
        END,
        '$.recurrence_summary', 'Daily repeat reminder until assistant sent proof or an exact owner blocker/question is recorded.'
    ),
    verification_readback = CASE
        WHEN verification_readback LIKE '%daily repeat reminder enabled.%' THEN verification_readback
        WHEN verification_readback = 'owner_reply_pending_response: newest primary-owner reply has no later assistant sent proof yet.'
            THEN 'owner_reply_pending_response: newest primary-owner reply has no later assistant sent proof yet; daily repeat reminder enabled.'
        ELSE CONCAT(TRIM(COALESCE(verification_readback, 'owner_reply_pending_response')), '; daily repeat reminder enabled.')
    END,
    next_update = CASE
        WHEN next_update LIKE 'Daily repeat reminder set for %' THEN next_update
        ELSE CONCAT('Daily repeat reminder set for ',
            CASE
                WHEN due_or_trigger REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' THEN due_or_trigger
                ELSE DATE_FORMAT(DATE_ADD(updated_at, INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s')
            END,
            '; worker must send result, domain proof, or one exact blocker/question.')
    END
WHERE dedupe_key LIKE 'taskflow-owner-reply-%'
  AND status = 'waiting'
  AND (
    due_or_trigger = 'owner_reply_pending_response'
    OR COALESCE(JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.recurrence_rule')), '') <> 'owner_reply_daily_repeat'
  )
"""
    run_exec(update_sql)
    after = json.loads(
        run_sql(
            """
SELECT
  SUM(CASE WHEN status = 'waiting' AND due_or_trigger = 'owner_reply_pending_response' THEN 1 ELSE 0 END) AS remaining_placeholder_waiting,
  SUM(CASE WHEN status = 'waiting'
            AND JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.recurrence_cadence')) = 'daily'
            AND JSON_UNQUOTE(JSON_EXTRACT(packet_json, '$.recurrence_rule')) = 'owner_reply_daily_repeat'
           THEN 1 ELSE 0 END) AS migrated_waiting
FROM koval_crm.ai_task_flow_packets
WHERE dedupe_key LIKE 'taskflow-owner-reply-%'
"""
        )
        or "[]"
    )
    print(
        json.dumps(
            {
                "ok": True,
                "migrated_waiting_before": waiting_count,
                "remaining_placeholder_waiting": int((after[0] or {}).get("remaining_placeholder_waiting") or 0) if after else 0,
                "migrated_waiting": int((after[0] or {}).get("migrated_waiting") or 0) if after else 0,
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
