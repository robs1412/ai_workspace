#!/usr/local/bin/python3.13
"""Create/update the AI Cloud server improvement Google Doc."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


CLIENT_FILE = Path("/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json")
TOKEN_FILE = Path("/Users/werkstatt/ai_workspace/.private/google-oauth/frank-google-drive-token.json")
STATE_FILE = Path("/Users/werkstatt/ai_workspace/project_hub/artifacts/ai-codex-server-improvement-2026-06-10.json")
DRIVE_ID = "0AP-Yf32mH4IHUk9PVA"
DOC_TITLE = "2026-06-10-AI-Codex-server-improvement"
TOKEN_URI = "https://oauth2.googleapis.com/token"


DEFAULT_TASKS = [
    {
        "id": "plan-doc",
        "title": "Create AI Cloud IT planning document with checklist and live update path",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "record-taskflow",
        "title": "Record the plan and progress in Task Flow plus DB handoff",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "dirty-state",
        "title": "Inspect current dirty state before changing server/process code",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "workspaceboard-reconcile",
        "title": "Verify and harden Workspaceboard selected-session reconcile/read-model patch",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "session-auto-close",
        "title": "Add/verify automatic close path for proof-closed or finished live sessions",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "process-memory-diagnostics",
        "title": "Add compact process-memory diagnostics that do not print prompt command lines",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "mailbox-runner-bounds",
        "title": "Convert or cap high-memory mailbox runners with bounded one-shot cycle behavior",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "token-output-caps",
        "title": "Add token/output-budget guardrails for broad rg, ps, logs, and session reads",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "ops-bridge-pickup",
        "title": "Patch OPS bridge stale pickup logic to validate real live worker state",
        "status": "todo",
        "proof": "",
    },
    {
        "id": "handoff-closeout",
        "title": "Record final handoff with proof, exact blockers, and next phase",
        "status": "todo",
        "proof": "",
    },
]


def load_credentials() -> Credentials:
    client_payload = json.loads(CLIENT_FILE.read_text(encoding="utf-8"))
    client_config = client_payload.get("installed") or client_payload.get("web") or client_payload
    token_payload = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    scopes = token_payload.get("scope") or "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents"
    if isinstance(scopes, str):
        scopes = scopes.split()
    creds = Credentials(
        token=token_payload.get("access_token"),
        refresh_token=token_payload.get("refresh_token"),
        token_uri=client_config.get("token_uri", TOKEN_URI),
        client_id=client_config["client_id"],
        client_secret=client_config.get("client_secret"),
        scopes=scopes,
    )
    if not creds.valid:
        creds.refresh(Request())
    return creds


def services():
    creds = load_credentials()
    return (
        build("drive", "v3", credentials=creds),
        build("docs", "v1", credentials=creds),
    )


def quoted(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_it_folder(drive) -> dict:
    query = "name = 'IT' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    result = drive.files().list(
        q=query,
        corpora="drive",
        driveId=DRIVE_ID,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id,name,parents,webViewLink)",
        pageSize=20,
    ).execute()
    files = result.get("files", [])
    if not files:
        raise RuntimeError("AI Cloud IT folder not found.")
    return files[0]


def find_doc(drive, folder_id: str) -> dict | None:
    query = (
        f"name = '{quoted(DOC_TITLE)}' and mimeType = 'application/vnd.google-apps.document' "
        f"and '{folder_id}' in parents and trashed = false"
    )
    result = drive.files().list(
        q=query,
        corpora="drive",
        driveId=DRIVE_ID,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id,name,webViewLink,modifiedTime)",
        pageSize=10,
    ).execute()
    files = result.get("files", [])
    return files[0] if files else None


def create_doc(drive, docs, folder_id: str) -> dict:
    created = docs.documents().create(body={"title": DOC_TITLE}).execute()
    file_id = created["documentId"]
    meta = drive.files().get(fileId=file_id, fields="parents", supportsAllDrives=True).execute()
    previous = ",".join(meta.get("parents", []))
    drive.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous,
        supportsAllDrives=True,
        fields="id,name,webViewLink,parents",
    ).execute()
    return drive.files().get(
        fileId=file_id,
        fields="id,name,webViewLink,modifiedTime",
        supportsAllDrives=True,
    ).execute()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "title": DOC_TITLE,
        "created_at": now(),
        "updated_at": now(),
        "tasks": DEFAULT_TASKS,
        "notes": [
            "Goal: lower server memory, reduce token burn, and make the recursive loop advance without repeated owner nudges.",
            "Rule: update this document and DB-backed Task Flow/handoff as tasks complete.",
        ],
    }


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now()
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M:%S %Z")


def mark_task(state: dict, task_id: str, status: str, proof: str = "") -> None:
    for task in state["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            if proof:
                task["proof"] = proof
            return
    raise RuntimeError(f"Unknown task id: {task_id}")


def checkbox(status: str) -> str:
    return "[x]" if status in {"done", "completed"} else "[ ]"


def render_doc(state: dict, web_link: str = "") -> str:
    lines = [
        DOC_TITLE,
        "",
        f"Updated: {state.get('updated_at', now())}",
        "Owner: Robert / Codex",
        "Workspace: /Users/werkstatt/ai_workspace",
        "",
        "Objective",
    ]
    lines.extend(f"- {note}" for note in state.get("notes", []))
    lines.extend(["", "Checklist"])
    for task in state["tasks"]:
        lines.append(f"{checkbox(task.get('status', 'todo'))} {task['title']}")
        if task.get("proof"):
            lines.append(f"    Proof: {task['proof']}")
    lines.extend(
        [
            "",
            "Current next step",
            state.get("next_step", "Start with dirty-state inspection and Workspaceboard reconcile verification."),
        ]
    )
    if web_link:
        lines.extend(["", f"Live doc: {web_link}"])
    return "\n".join(lines) + "\n"


def replace_doc_body(docs, doc_id: str, text: str) -> None:
    doc = docs.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    end_index = content[-1].get("endIndex", 1) if content else 1
    requests = []
    if end_index > 2:
        requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index - 1}}})
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})
    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mark", action="append", default=[], help="task_id=status=proof")
    parser.add_argument("--next-step", default="")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()

    state = load_state()
    for item in args.mark:
        parts = item.split("=", 2)
        if len(parts) < 2:
            raise RuntimeError("--mark expects task_id=status=proof")
        mark_task(state, parts[0], parts[1], parts[2] if len(parts) == 3 else "")
    if args.next_step:
        state["next_step"] = args.next_step
    save_state(state)

    drive, docs = services()
    folder = find_it_folder(drive)
    doc = find_doc(drive, folder["id"]) or create_doc(drive, docs, folder["id"])
    replace_doc_body(docs, doc["id"], render_doc(state, doc.get("webViewLink", "")))
    readback = docs.documents().get(documentId=doc["id"], fields="title,body/content/endIndex").execute()
    result = {
        "ok": True,
        "doc_id": doc["id"],
        "title": readback.get("title"),
        "webViewLink": doc.get("webViewLink"),
        "folder_id": folder["id"],
        "task_count": len(state["tasks"]),
        "done_count": sum(1 for task in state["tasks"] if task.get("status") in {"done", "completed"}),
    }
    if args.print_json:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
