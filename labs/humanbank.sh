#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: HumanBank
# Deliberately vulnerable online banking app — SQLi, IDOR, XSS, auth flaws,
# file upload, path traversal, business logic
# Built from source in labs/humanbank/
# =============================================================================

LAB_NAME="HumanBank"
CONTAINER_NAME="octorig-humanbank"
HOST_PORT=8083

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/humanbank"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building HumanBank image..."
    if docker build -q -t octorig-humanbank:latest "$APP_DIR" &>/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/humanbank/"
      exit 1
    fi

    docker run -d \
      --name "$CONTAINER_NAME" \
      -p "${HOST_PORT}:5000" \
      --restart unless-stopped \
      octorig-humanbank:latest

    wait_for_port 127.0.0.1 "$HOST_PORT" 60

    INFO_LINES=(
      "URL|http://127.0.0.1:${HOST_PORT}"
      "Admin|admin / humanbank-admin-2026"
      "User|alice.wang / sunshine1"
      "Stop|./humanbank.sh stop"
    )
    access_card INFO_LINES
    good "HumanBank is up!"
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
