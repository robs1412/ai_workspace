#!/usr/bin/env bash
set -euo pipefail

export GOOGLE_DRIVE_CLIENT_FILE="/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json"
export GOOGLE_DRIVE_LOCAL_TOKEN_FILE="/Users/werkstatt/ai_workspace/.private/google-oauth/nationaloutreach-google-drive-token.json"
export GOOGLE_DRIVE_USE_LOCAL_TOKEN=1
export GOOGLE_DRIVE_REFRESH_TOKEN_SECRET_NAME="GOOGLE_DRIVE_CODEX_NATIONALOUTREACH_REFRESH_TOKEN"
export GOOGLE_DRIVE_SCOPE="https://www.googleapis.com/auth/drive.metadata.readonly https://www.googleapis.com/auth/drive.file"
export GOOGLE_DRIVE_LOGIN_HINT="nationaloutreach@kovaldistillery.com"
export GOOGLE_DRIVE_TEST_DRIVE_ID="${GOOGLE_DRIVE_TEST_DRIVE_ID:-0AP-Yf32mH4IHUk9PVA}"
export PYTHON="${PYTHON:-/Users/werkstatt/ai_workspace/.private/venvs/gdrive/bin/python}"
