#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: OWASP WebGoat
# Lesson-based deliberately insecure Java web app — covers the same vuln
# classes as PortSwigger Web Academy (SQLi, XSS, SSRF, JWT, XXE, etc.)
# Image: webgoat/webgoat
# =============================================================================

LAB_NAME="WebGoat"
CONTAINER_NAME="octorig-webgoat"
HOST_PORT=8888
WOLF_PORT=9191   # WebWolf companion app (internal: 9090)

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"
    docker_pull webgoat/webgoat:latest

    docker run -d \
      --name "$CONTAINER_NAME" \
      --tmpfs /tmp \
      --tmpfs /home/webgoat/.webgoat-2025.3 \
      -p "${HOST_PORT}:8080" \
      -p "${WOLF_PORT}:9090" \
      -e SERVER_ADDRESS=0.0.0.0 \
      -e TZ=UTC \
      --restart unless-stopped \
      webgoat/webgoat:latest &>/dev/null

    wait_for_port 127.0.0.1 "$HOST_PORT" 90

    INFO_LINES=(
      "WebGoat URL|http://127.0.0.1:${HOST_PORT}/WebGoat"
      "WebWolf URL|http://127.0.0.1:${WOLF_PORT}/WebWolf"
      "Register|Create account on first visit"
      "Coverage|SQLi / XSS / XXE / JWT / IDOR / SSRF"
      "Coverage 2|Path traversal / Crypto / Auth bypass"
      "Stop|./webgoat.sh stop"
    )
    access_card INFO_LINES
    good "WebGoat is up!"
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
