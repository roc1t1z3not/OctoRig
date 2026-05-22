#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: Rewind Range
# Deliberately vulnerable retro video & games store — SQLi, XSS, IDOR
# Built from source in labs/rewindrange/
# =============================================================================

LAB_NAME="Rewind Range"
CONTAINER_NAME="octorig-rewindrange"
HOST_PORT=8082

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/rewindrange"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building Rewind Range image..."
    if docker build -q -t octorig-rewindrange:latest "$APP_DIR" &>/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/rewindrange/"
      exit 1
    fi

    docker run -d \
      --name "$CONTAINER_NAME" \
      -p "${HOST_PORT}:5000" \
      --restart unless-stopped \
      octorig-rewindrange:latest

    wait_for_port 127.0.0.1 "$HOST_PORT" 60

    INFO_LINES=(
      "URL|http://127.0.0.1:${HOST_PORT}"
      "Stop|./rewindrange.sh stop"
    )
    access_card INFO_LINES
    good "Rewind Range is up!"
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
