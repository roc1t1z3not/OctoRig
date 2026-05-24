#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# OctoRig — Security Lab Manager
# Spin up / tear down vulnerable security lab environments via Docker
# =============================================================================

set -euo pipefail

trap 'echo ""; info "Caught interrupt — exiting OctoRig."; exit 0' INT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABS_DIR="${SCRIPT_DIR}/labs"

# ---------------- colours / output helpers -----------------------------------
RED='\033[0;31m'
GREEN='\033[38;5;46m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

good()  { echo -e "  ${GREEN}[+]${RESET} $*"; }
bad()   { echo -e "  ${RED}[-]${RESET} $*"; }
info()  { echo -e "  ${GRAY}[*]${RESET} $*"; }
warn()  { echo -e "  ${YELLOW}[!]${RESET} $*"; }
header(){ echo -e "\n  ${GREEN}${BOLD}$*${RESET}"; }

# ---------------- self-update ------------------------------------------------
update_self() {
  if ! command -v git &>/dev/null; then
    return
  fi
  if [[ ! -d "${SCRIPT_DIR}/.git" ]]; then
    return
  fi
  if ! git -C "${SCRIPT_DIR}" diff --quiet || \
     ! git -C "${SCRIPT_DIR}" diff --cached --quiet || \
     [[ -n "$(git -C "${SCRIPT_DIR}" ls-files --others --exclude-standard)" ]]; then
    info "Skipping self-update: local changes detected."
    return
  fi
  info "Checking for updates..."
  if git -C "${SCRIPT_DIR}" pull --ff-only --quiet 2>/dev/null; then
    good "Up to date."
  else
    warn "Self-update failed (non-fast-forward or remote issue). Continuing."
  fi
}

# ---------------- lab registry -----------------------------------------------
# Format: "ID|NAME|SCRIPT|DESCRIPTION"
LABS=(
  "1|Rewind|rewindrange.sh|Retro video and games store — SQLi, XSS and IDOR"
  "2|TradeFloor|tradefloor.sh|Vulnerable trading portal — XXE, CSRF, mass assignment, SQLi, IDOR, stored XSS"
  "3|GoldenAce|goldenace.sh|Vulnerable online casino — SQLi, IDOR, stored XSS, CSRF, business logic, JWT alg:none"
  "4|HumanBank|humanbank.sh|Vulnerable online banking app — SQLi, IDOR, XSS, auth flaws, file upload, business logic"
  "5|MediHuman|medihuman.sh|Vulnerable healthcare patient portal — SQLi, IDOR, XSS, file upload, SSH/FTP weak creds"
  "6|NetPulse|netpulse.sh|Vulnerable 90s ISP portal — SSRF, SSTI, command injection, open redirect, SQLi, IDOR, XSS"
  "7|Limelight|limelight.sh|Vulnerable cinema booking app — SQLi, XSS, IDOR, CSRF, SSTI, business logic, mass assignment"
  "8|BreachSQL|breachsql.sh|Tiered SQL injection challenges (T1-T5) for SQLi practice"
  "9|StingXSS|stingxss.sh|Tiered XSS challenges (T1-T8) for XSS injection practice"
  "10|VaultGate|vaultgate.sh|IDOR challenges for benchmarking"
  "11|VaultRip|vaultriprange.sh|SSH credential-rich target for VaultRip passive and remote harvesting"
  "12|Juice Shop|juiceshop.sh|OWASP Juice Shop - OWASP Top 10 web vulnerabilities"
  "13|DVWA|dvwa.sh|Damn Vulnerable Web App - PHP/MySQL classic"
  "14|Metasploitable2|metasploitable.sh|Linux VM with intentionally vulnerable services"
  "15|WebGoat|webgoat.sh|OWASP WebGoat - PortSwigger-style lesson-based labs"
  "16|HTB Style|htb_style.sh|HackTheBox-style CTFd platform + vulnerable challenge"
  "17|VulnAD|vulnad.sh|Vulnerable Active Directory - Samba4 AD with AD attack paths"
)

# IDs of real-world scenario labs (for "start world")
WORLD_LAB_IDS=(1 2 3 4 5 6 7)

# ---------------- dependency checks ------------------------------------------
install_docker() {
  warn "Docker not found — attempting to install..."
  if [[ $EUID -ne 0 ]]; then
    bad "Root privileges required to install Docker. Re-run with sudo."
    exit 1
  fi
  apt-get update -qq
  apt-get install -y -qq docker.io
  systemctl enable --now docker
  if ! command -v docker &>/dev/null; then
    bad "Docker installation failed. Install it manually: apt install docker.io"
    exit 1
  fi
  good "Docker installed successfully"
}

check_docker() {
  if ! command -v docker &>/dev/null; then
    install_docker
  fi
  if ! docker info &>/dev/null 2>&1; then
    info "Docker daemon is not running — attempting to start it..."
    if [[ $EUID -ne 0 ]]; then
      sudo systemctl start docker 2>/dev/null || { bad "Failed to start Docker daemon. Try: sudo systemctl start docker"; exit 1; }
    else
      systemctl start docker 2>/dev/null || { bad "Failed to start Docker daemon. Try: systemctl start docker"; exit 1; }
    fi
    sleep 2
    if ! docker info &>/dev/null 2>&1; then
      bad "Docker daemon still not running after start attempt."
      exit 1
    fi
  fi
  good "Docker is running"
}

# ---------------- banner ------------------------------------------------------
banner() {
  echo ""
  echo -e "${GREEN}${BOLD}"
  echo "   ____       __        ____  _      "
  echo "  / __ \_____/ /_____  / __ \(_)___ _"
  echo " / / / / ___/ __/ __ \/ /_/ / / __ \`/"
  echo "/ /_/ / /__/ /_/ /_/ / _, _/ / /_/ / "
  echo "\____/\___/\__/\____/_/ |_/_/\__, /  "
  echo "                            /____/   "
  echo -e "${RESET}"
  echo -e "  ${BOLD}OctoRig — Security Lab Manager${RESET} — Docker-based vulnerable environment launcher"
  echo ""
}

# ---------------- list labs ---------------------------------------------------
list_labs() {
  header "Available Labs"
  echo ""
  printf "  ${BOLD}%-4s %-20s %s${RESET}\n" "ID" "NAME" "DESCRIPTION"
  echo "  ─────────────────────────────────────────────────────────────────────"
  for entry in "${LABS[@]}"; do
    IFS='|' read -r id name _script desc <<< "$entry"
    printf "  ${GREEN}%-4s${RESET} ${BOLD}%-20s${RESET} ${GRAY}%s${RESET}\n" "$id" "$name" "$desc"
  done
  echo ""
}

# ---------------- status of all running labs ----------------------------------
status_all() {
  header "Running Lab Containers"
  echo ""
  local running
  running=$(docker ps --filter "name=octorig-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true)
  if [[ -z "$running" ]] || [[ "$running" == *"NAMES"$'\n' ]]; then
    info "No OctoRig lab containers are currently running."
  else
    echo "$running" | sed 's/^/  /'
  fi
  echo ""
}

# ---------------- dispatch to a lab script ------------------------------------
dispatch() {
  local action="$1"
  local query="$2"

  local matched="" matched_name=""

  if [[ "$query" =~ ^[0-9]+$ ]]; then
    for entry in "${LABS[@]}"; do
      IFS='|' read -r lid lname lscript _desc <<< "$entry"
      if [[ "$lid" == "$query" ]]; then
        matched="$lscript"; matched_name="$lname"; break
      fi
    done
  else
    local qnorm
    qnorm=$(echo "$query" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
    for entry in "${LABS[@]}"; do
      IFS='|' read -r _lid lname lscript _desc <<< "$entry"
      local nnorm
      nnorm=$(echo "$lname" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
      if [[ "$nnorm" == "$qnorm"* ]]; then
        matched="$lscript"; matched_name="$lname"; break
      fi
    done
  fi

  if [[ -z "$matched" ]]; then
    bad "Unknown lab: $query"
    echo ""
    list_labs
    exit 1
  fi

  local script_path="${LABS_DIR}/${matched}"
  if [[ ! -f "$script_path" ]]; then
    bad "Lab script not found: $script_path"
    exit 1
  fi

  bash "$script_path" "$action"
}

# ---------------- start all / stop all ----------------------------------------
all_action() {
  local action="$1"
  if [[ "$action" == "stop" ]]; then
    local stopped=()
    for entry in "${LABS[@]}"; do
      IFS='|' read -r _id name lscript _desc <<< "$entry"
      [[ -f "${LABS_DIR}/${lscript}" ]] || continue
      # Check if any of this lab's containers are actually running (not just exited).
      local cnames was_running=false
      cnames=$(grep -oP '(?<==")(octorig-[^"]+)(?=")' "${LABS_DIR}/${lscript}" 2>/dev/null | sort -u)
      while IFS= read -r cname; do
        [[ -z "$cname" ]] && continue
        if docker ps --filter "name=^${cname}$" --format "{{.Names}}" 2>/dev/null | grep -q "^${cname}$"; then
          was_running=true
          break
        fi
      done <<< "$cnames"
      bash "${LABS_DIR}/${lscript}" stop &>/dev/null
      [[ "$was_running" == true ]] && stopped+=("$name")
    done
    if [[ ${#stopped[@]} -eq 0 ]]; then
      info "No labs were running."
    else
      good "Stopped: $(IFS=', '; echo "${stopped[*]}")"
    fi
  else
    for entry in "${LABS[@]}"; do
      IFS='|' read -r id name lscript _desc <<< "$entry"
      header "${action^}: $name"
      bash "${LABS_DIR}/${lscript}" "$action" || warn "Failed to $action $name (continuing)"
    done
  fi
}

# ---------------- start real-world labs in parallel ---------------------------
start_world() {
  header "Starting all real-world labs in parallel..."
  echo ""

  local tmpdir
  tmpdir=$(mktemp -d)
  local pids=() names=() lids=()

  for entry in "${LABS[@]}"; do
    IFS='|' read -r lid lname lscript _desc <<< "$entry"
    local is_world=false
    for wid in "${WORLD_LAB_IDS[@]}"; do
      [[ "$lid" == "$wid" ]] && is_world=true && break
    done
    [[ "$is_world" == false ]] && continue
    [[ ! -f "${LABS_DIR}/${lscript}" ]] && continue

    info "Queuing: $lname"
    bash "${LABS_DIR}/${lscript}" start > "${tmpdir}/${lid}.log" 2>&1 &
    pids+=($!)
    names+=("$lname")
    lids+=("$lid")
  done

  echo ""
  info "${#pids[@]} labs launching in parallel — waiting for them to come up..."
  echo ""

  local all_ok=true
  local i
  for i in "${!pids[@]}"; do
    local pid="${pids[$i]}" name="${names[$i]}" lid="${lids[$i]}"
    if wait "$pid"; then
      good "$name is up"
    else
      bad "$name failed to start"
      all_ok=false
    fi
    cat "${tmpdir}/${lid}.log"
    echo ""
  done

  rm -rf "$tmpdir"

  if [[ "$all_ok" == true ]]; then
    good "All real-world labs are running."
  else
    warn "Some labs failed to start — check output above."
  fi
}

# ---------------- interactive menu --------------------------------------------
interactive_menu() {
  list_labs
  echo -e "  ${BOLD}Commands:${RESET}"
  echo -e "  ${GREEN}start <id|name>${RESET}    — Start a lab by ID or name (e.g. start 3, start goldenace)"
  echo -e "  ${GREEN}stop <id|name>${RESET}     — Stop a lab by ID or name"
  echo -e "  ${GREEN}restart <id|name>${RESET}  — Restart a lab by ID or name"
  echo -e "  ${GREEN}status${RESET}         — Show running lab containers"
  echo -e "  ${GREEN}start all${RESET}      — Start all labs"
  echo -e "  ${GREEN}start world${RESET}    — Start all real-world scenario labs in parallel"
  echo -e "  ${GREEN}stop all${RESET}       — Stop all labs"
  echo -e "  ${GREEN}restart all${RESET}    — Restart all labs"
  echo -e "  ${GREEN}list${RESET}           — List available labs"
  echo -e "  ${GREEN}quit${RESET}           — Exit"
  echo ""

  while true; do
    echo -ne "  ${BOLD}lab>${RESET} "
    read -r cmd arg1 || break
    case "$cmd" in
      start)
        check_docker
        if   [[ "${arg1:-}" == "all"   ]]; then all_action start
        elif [[ "${arg1:-}" == "world" ]]; then start_world
        else dispatch start "${arg1:-}"; fi ;;
      stop)
        if [[ "${arg1:-}" == "all" ]]; then all_action stop
        else dispatch stop "${arg1:-}"; fi ;;
      restart)
        check_docker
        if [[ "${arg1:-}" == "all" ]]; then all_action stop; all_action start
        else dispatch stop "${arg1:-}"; dispatch start "${arg1:-}"; fi ;;
      status) status_all ;;
      list)   list_labs ;;
      quit|exit|q) info "Bye!"; exit 0 ;;
      "") ;;
      *) warn "Unknown command: $cmd — type 'quit' to exit" ;;
    esac
    echo ""
  done
}

# ---------------- main --------------------------------------------------------
update_self
banner

case "${1:-menu}" in
  menu)
    check_docker
    interactive_menu ;;
  list)
    list_labs ;;
  status)
    status_all ;;
  start)
    check_docker
    if   [[ "${2:-}" == "all"   ]]; then all_action start
    elif [[ "${2:-}" == "world" ]]; then start_world
    else dispatch start "${2:-}"; fi ;;
  stop)
    if [[ "${2:-}" == "all" ]]; then all_action stop
    else dispatch stop "${2:-}"; fi ;;
  restart)
    check_docker
    if [[ "${2:-}" == "all" ]]; then all_action stop; all_action start
    else dispatch stop "${2:-}"; dispatch start "${2:-}"; fi ;;
  help|-h|--help)
    list_labs
    echo "Usage: $0 [menu|list|status|start <id|name|all|world>|stop <id|name|all>|restart <id|name|all>]"
    echo "" ;;
  *)
    bad "Unknown command: ${1}"
    echo "Usage: $0 [menu|list|status|start <id|name|all|world>|stop <id|name|all>|restart <id|name|all>]"
    exit 1 ;;
esac
