#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: MediHuman
# Deliberately vulnerable healthcare patient portal — SQLi, IDOR, XSS,
# unrestricted file upload, path traversal, SSH weak creds, anonymous FTP
# Built from source in labs/medihuman/
# =============================================================================

LAB_NAME="MediHuman"
CONTAINER_NAME="octorig-medihuman"
HOST_PORT=8084
SSH_PORT=2224
FTP_PORT=2121

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/medihuman"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building MediHuman image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-medihuman:latest "$APP_DIR" &>/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/medihuman/"
      exit 1
    fi

    docker run -d \
      --name "$CONTAINER_NAME" \
      -p "${HOST_PORT}:5000" \
      -p "${SSH_PORT}:22" \
      -p "${FTP_PORT}:21" \
      -p "30000-30009:30000-30009" \
      --restart unless-stopped \
      octorig-medihuman:latest

    wait_for_port 127.0.0.1 "$HOST_PORT" 90

    INFO_LINES=(
      "URL|http://127.0.0.1:${HOST_PORT}"
      "SSH|ssh sysadmin@127.0.0.1 -p ${SSH_PORT}  (pw: medihuman123)"
      "FTP|ftp 127.0.0.1 ${FTP_PORT}"
      "Stop|./medihuman.sh stop"
    )
    access_card INFO_LINES
    good "MediHuman is up!"
    ;;

  stop)
    header "Stopping..."
    if docker rm -f "$CONTAINER_NAME" &>/dev/null; then
      good "Container $CONTAINER_NAME removed."
    else
      warn "Container $CONTAINER_NAME was not running."
    fi
    ;;

  status)
    container_status "$CONTAINER_NAME"
    ;;
esac
