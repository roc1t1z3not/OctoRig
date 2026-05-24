#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: HTB-Style — CTFd platform + a vulnerable challenge container
# Runs CTFd (the CTF management platform used by HackTheBox / many CTFs)
# alongside a Vulhub-based vulnerable challenge for realistic HTB feel.
#
# Challenge: Apache Struts2 CVE-2017-5638 RCE (classic HTB-style box)
# CTFd:      http://127.0.0.1:8000  (score tracking / flag submission)
# Target:    http://127.0.0.1:8090  (the vulnerable app)
# =============================================================================

LAB_NAME="HTB Style"
CTFD_CONTAINER="octorig-ctfd"
CHALLENGE_CONTAINER="octorig-htb-challenge"
LAB_NET="octorig-htb-net"
LAB_SUBNET="172.28.16.0/24"
CTFD_IP="172.28.16.2"
CHALLENGE_IP="172.28.16.3"

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."

    ensure_network "$LAB_NET" "$LAB_SUBNET"

    # ---- CTFd stack (CTFd + Redis + MySQL) ----
    ensure_container_gone "octorig-ctfd-db"
    ensure_container_gone "octorig-ctfd-redis"
    ensure_container_gone "$CTFD_CONTAINER"

    info "Starting CTFd database..."
    docker run -d \
      --name octorig-ctfd-db \
      --network "$LAB_NET" \
      -e MYSQL_ROOT_PASSWORD=ctfd \
      -e MYSQL_DATABASE=ctfd \
      -e MYSQL_USER=ctfd \
      -e MYSQL_PASSWORD=ctfd \
      --restart unless-stopped \
      mariadb:10.11 \
      --character-set-server=utf8mb4 \
      --collation-server=utf8mb4_unicode_ci \
      --wait_timeout=28800 \
      --log-warnings=0 &>/dev/null

    info "Starting CTFd Redis..."
    docker run -d \
      --name octorig-ctfd-redis \
      --network "$LAB_NET" \
      --restart unless-stopped \
      redis:7-alpine &>/dev/null

    info "Pulling CTFd image..."
    docker_pull ctfd/ctfd:latest
    info "Starting CTFd..."
    docker run -d \
      --name "$CTFD_CONTAINER" \
      --network "$LAB_NET" \
      --ip "$CTFD_IP" \
      -e DATABASE_URL="mysql+pymysql://ctfd:ctfd@octorig-ctfd-db/ctfd" \
      -e REDIS_URL="redis://octorig-ctfd-redis:6379" \
      -e SECRET_KEY="octorig-htb-secret" \
      --restart unless-stopped \
      ctfd/ctfd:latest &>/dev/null

    # ---- Vulnerable challenge: Apache Struts2 S2-045 ----
    ensure_container_gone "$CHALLENGE_CONTAINER"
    info "Pulling Struts2 CVE-2017-5638 challenge image..."
    if docker pull vulhub/struts2:2.3.30 &>/dev/null 2>&1; then
      good "Image vulhub/struts2:2.3.30 ready"
    elif docker pull piesecurity/apache-struts2-cve-2017-5638:latest &>/dev/null 2>&1; then
      good "Image piesecurity/apache-struts2-cve-2017-5638 ready"
    else
      warn "Struts2 image unavailable — using a generic Apache httpd placeholder"
      docker_pull httpd:2.4
      docker run -d --name "$CHALLENGE_CONTAINER" \
        --network "$LAB_NET" --ip "$CHALLENGE_IP" \
        --restart unless-stopped httpd:2.4 &>/dev/null
    fi

    # Try vulhub image first, fall back gracefully (already handled above)
    docker ps --format '{{.Names}}' | grep -qx "$CHALLENGE_CONTAINER" || \
      docker run -d \
        --name "$CHALLENGE_CONTAINER" \
        --network "$LAB_NET" \
        --ip "$CHALLENGE_IP" \
        --restart unless-stopped \
        vulhub/struts2:2.3.30 &>/dev/null 2>&1 || true

    wait_for_port "$CTFD_IP" 8000 90

    INFO_LINES=(
      "CTFd (scoreboard)|http://${CTFD_IP}:8000"
      "CTFd setup|Complete setup wizard on first visit"
      "Challenge target|http://${CHALLENGE_IP}:8080"
      "Vuln|Apache Struts2 CVE-2017-5638 RCE"
      "CVSSv3|10.0 (Critical)"
      "Stop|./htb_style.sh stop"
    )
    access_card INFO_LINES
    info "Tip: set the flag manually in CTFd after you get RCE on the challenge box."
    good "HTB-Style lab is up!"
    ;;

  stop)
    header "Stopping..."
    for c in "$CTFD_CONTAINER" "octorig-ctfd-db" "octorig-ctfd-redis" "$CHALLENGE_CONTAINER"; do
      if docker rm -f "$c" &>/dev/null; then
        good "Removed $c"
      else
        info "$c was not running"
      fi
    done
    remove_network "$LAB_NET"
    ;;

  status)
    for c in "$CTFD_CONTAINER" "octorig-ctfd-db" "octorig-ctfd-redis" "$CHALLENGE_CONTAINER"; do
      container_status "$c"
    done
    ;;
esac
