#!/usr/local/bin/python3.13
"""
Google Drive metadata-only bundle for the first Frank Mac mini slice.

Derived from Claude Task #1326 server bundle with Mac mini adaptations:
- configurable Infisical machine-identity env path
- configurable refresh-token secret key
- metadata-only default scope
- test path narrowed to the approved shared Drive
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SECRETS_ENV = os.environ.get("INFISICAL_MACHINE_ENV_FILE", "/srv/secrets/machine-identity.env")
DEFAULT_CLIENT_FILE = Path(
    os.environ.get(
        "GOOGLE_DRIVE_CLIENT_FILE",
        "/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json",
    )
)
DEFAULT_LOCAL_TOKEN_FILE = Path(
    os.environ.get(
        "GOOGLE_DRIVE_LOCAL_TOKEN_FILE",
        "/Users/werkstatt/ai_workspace/.private/google-oauth/frank-google-drive-token.json",
    )
)
USE_LOCAL_TOKEN = os.environ.get("GOOGLE_DRIVE_USE_LOCAL_TOKEN", "").lower() in {
    "1",
    "true",
    "yes",
}

SECRET_CLIENT_ID = os.environ.get("GOOGLE_DRIVE_CLIENT_ID_SECRET_NAME", "GOOGLE_DRIVE_CLIENT_ID")
SECRET_CLIENT_SECRET = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET_SECRET_NAME", "GOOGLE_DRIVE_CLIENT_SECRET")
SECRET_REFRESH_TOKEN = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN_SECRET_NAME", "GOOGLE_DRIVE_FRANK_REFRESH_TOKEN")

DEFAULT_SCOPE = os.environ.get(
    "GOOGLE_DRIVE_SCOPE",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
)
DEFAULT_TEST_DRIVE_ID = os.environ.get("GOOGLE_DRIVE_TEST_DRIVE_ID", "0AP-Yf32mH4IHUk9PVA")
ALLOW_BROAD_LIST = os.environ.get("GOOGLE_DRIVE_ALLOW_BROAD_LIST", "").lower() in {
    "1",
    "true",
    "yes",
}
TOKEN_URI = "https://oauth2.googleapis.com/token"


def configured_scopes():
    return [scope for scope in str(DEFAULT_SCOPE).split() if scope]


def load_machine_identity_env():
    env = {}
    with open(SECRETS_ENV, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_infisical_token():
    env = load_machine_identity_env()
    resp = subprocess.run(
        [
            "curl",
            "-sk",
            "--request",
            "POST",
            "--url",
            f"{env.get('INFISICAL_DOMAIN', 'https://secrets.koval.lan')}/api/v1/auth/universal-auth/login",
            "--header",
            "Content-Type: application/json",
            "--data",
            json.dumps(
                {
                    "clientId": env.get("INFISICAL_CLIENT_ID", ""),
                    "clientSecret": env.get("INFISICAL_CLIENT_SECRET", ""),
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(resp.stdout)
    return data["accessToken"], env


def get_secret(name, access_token, env):
    result = subprocess.run(
        [
            "infisical",
            "secrets",
            "get",
            name,
            "--projectId",
            env.get("INFISICAL_PROJECT_ID", ""),
            "--env",
            "dev",
            "--domain",
            env.get("INFISICAL_DOMAIN", "https://secrets.koval.lan"),
            "--token",
            access_token,
            "--plain",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    if not value:
        raise RuntimeError(
            f"Secret '{name}' not found in Infisical.\n"
            f"Expected secret names:\n"
            f"  {SECRET_CLIENT_ID}\n"
            f"  {SECRET_CLIENT_SECRET}\n"
            f"  {SECRET_REFRESH_TOKEN}"
        )
    return value


def load_oauth_client(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    config = payload.get("installed") or payload.get("web") or payload
    if not config.get("client_id"):
        raise RuntimeError(f"OAuth client file missing client_id: {path}")
    return config


def build_local_credentials():
    from google.oauth2.credentials import Credentials

    client_config = load_oauth_client(DEFAULT_CLIENT_FILE)
    if not DEFAULT_LOCAL_TOKEN_FILE.exists():
        raise RuntimeError(
            "Local Google Drive token file is missing. Run authorize_frank_drive.py authorize first."
        )
    token_payload = json.loads(DEFAULT_LOCAL_TOKEN_FILE.read_text(encoding="utf-8"))
    refresh_token = token_payload.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("Local Google Drive token file does not contain a refresh_token.")
    scopes = token_payload.get("scope", DEFAULT_SCOPE)
    if isinstance(scopes, str):
        scopes = scopes.split()
    return Credentials(
        token=token_payload.get("access_token"),
        refresh_token=refresh_token,
        token_uri=client_config.get("token_uri", TOKEN_URI),
        client_id=client_config["client_id"],
        client_secret=client_config.get("client_secret"),
        scopes=scopes or configured_scopes(),
    )


def build_infisical_credentials():
    from google.oauth2.credentials import Credentials

    access_token, env = get_infisical_token()
    client_id = get_secret(SECRET_CLIENT_ID, access_token, env)
    client_secret = get_secret(SECRET_CLIENT_SECRET, access_token, env)
    refresh_token = get_secret(SECRET_REFRESH_TOKEN, access_token, env)

    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=configured_scopes(),
    )


def build_credentials():
    if USE_LOCAL_TOKEN or (not Path(SECRETS_ENV).exists() and DEFAULT_LOCAL_TOKEN_FILE.exists()):
        return build_local_credentials()
    return build_infisical_credentials()


def build_service():
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    creds = build_credentials()
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def cmd_list(args):
    service = build_service()
    target_id = args.folder_id or DEFAULT_TEST_DRIVE_ID

    base_kwargs = dict(
        fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, owners(emailAddress))",
        pageSize=200,
        orderBy="name",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    )

    if target_id:
        try:
            service.drives().get(driveId=target_id).execute()
            base_kwargs["corpora"] = "drive"
            base_kwargs["driveId"] = target_id
            base_kwargs["q"] = "trashed = false"
        except Exception:
            base_kwargs["q"] = f"'{target_id}' in parents and trashed = false"
    elif ALLOW_BROAD_LIST:
        base_kwargs["q"] = "trashed = false"
    else:
        raise RuntimeError(
            "Broad Drive listing is disabled for Frank's metadata-only slice. "
            "Set GOOGLE_DRIVE_TEST_DRIVE_ID or pass an approved folder/shared Drive ID."
        )

    results = []
    page_token = None
    while True:
        kwargs = dict(base_kwargs)
        if page_token:
            kwargs["pageToken"] = page_token
        resp = service.files().list(**kwargs).execute()
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("(no files found)")
        for item in results:
            size_str = f"{int(item.get('size', 0)):,}" if item.get("size") else "-"
            mime = item.get("mimeType", "").replace("application/vnd.google-apps.", "gdoc:")
            print(f"{item['id']}\t{item['name']:<60}\t{mime:<35}\t{size_str}")


def cmd_upload_text(args):
    from googleapiclient.http import MediaFileUpload

    service = build_service()
    target_id = args.folder_id or DEFAULT_TEST_DRIVE_ID
    source_path = Path(args.path).expanduser()
    if not source_path.exists():
        raise RuntimeError(f"Upload source does not exist: {source_path}")
    metadata = {
        "name": args.name or source_path.name,
        "mimeType": "text/plain",
    }
    if target_id:
        metadata["parents"] = [target_id]
    media = MediaFileUpload(str(source_path), mimetype="text/plain", resumable=False)
    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,mimeType,parents,webViewLink",
        supportsAllDrives=True,
    ).execute()
    if args.json:
        print(json.dumps(created, indent=2))
    else:
        print(f"uploaded {created.get('id')} {created.get('name')}")


def cmd_folder_id(args):
    import re

    patterns = [
        r"/folders/([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
        r"^([a-zA-Z0-9_-]{25,})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, args.url)
        if match:
            print(match.group(1))
            return
    print(f"ERROR: cannot extract ID from: {args.url}", file=sys.stderr)
    sys.exit(1)


def cmd_test(args):
    service = build_service()
    drive_id = args.drive_id or DEFAULT_TEST_DRIVE_ID
    resp = service.files().list(
        corpora="drive",
        driveId=drive_id,
        q="trashed = false",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        pageSize=5,
        fields="files(id,name,mimeType)",
        orderBy="modifiedTime desc",
    ).execute()
    files = resp.get("files", [])
    print(f"Authentication OK for shared Drive {drive_id}. Sample files ({len(files)}):")
    for item in files:
        print(f"  {item['id']}  {item['name']}")


def cmd_whoami(args):
    service = build_service()
    resp = service.about().get(fields="user(emailAddress,displayName,permissionId)").execute()
    user = resp.get("user", {})
    print(f"Drive authentication OK for {user.get('emailAddress', '(unknown email)')}")
    if user.get("displayName"):
        print(f"Display name: {user['displayName']}")
    if user.get("permissionId"):
        print(f"Permission ID: {user['permissionId']}")


def main():
    parser = argparse.ArgumentParser(description="Google Drive metadata-only tool for Frank")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="List files in a folder or Shared Drive")
    p.add_argument("--folder-id")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("folder-id", help="Extract a folder or file ID from a Drive URL")
    p.add_argument("url")

    p = sub.add_parser("test", help="Test authentication against the approved shared Drive")
    p.add_argument("--drive-id")

    sub.add_parser("whoami", help="Test authentication and print non-secret Drive user metadata")

    p = sub.add_parser("upload-text", help="Upload one text file to an approved folder or Shared Drive")
    p.add_argument("path")
    p.add_argument("--folder-id", default=DEFAULT_TEST_DRIVE_ID)
    p.add_argument("--name")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    dispatch = {
        "list": cmd_list,
        "folder-id": cmd_folder_id,
        "test": cmd_test,
        "whoami": cmd_whoami,
        "upload-text": cmd_upload_text,
    }
    try:
        dispatch[args.command](args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
