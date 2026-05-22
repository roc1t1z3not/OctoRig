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

# ---------------- lab registry -----------------------------------------------
# Format: "ID|NAME|SCRIPT|DESCRIPTION"
LABS=(
  "1|Juice Shop|juiceshop.sh|OWASP Juice Shop - OWASP Top 10 web vulnerabilities"
  "2|DVWA|dvwa.sh|Damn Vulnerable Web App - PHP/MySQL classic"
  "3|Metasploitable2|metasploitable.sh|Linux VM with intentionally vulnerable services"
  "4|WebGoat|webgoat.sh|OWASP WebGoat - PortSwigger-style lesson-based labs"
  "5|HTB Style|htb_style.sh|HackTheBox-style CTFd platform + vulnerable challenge"
  "6|VulnAD|vulnad.sh|Vulnerable Active Directory - Samba4 AD with AD attack paths"
  "7|BreachSQL Fire Range|breachsql.sh|Tiered SQL injection challenges (T1-T5) for SQLi practice"
  "8|StingXSS Fire Range|stingxss.sh|Tiered XSS challenges (T1-T8) for XSS injection practice"
  "9|VaultGate IDOR Range|vaultgate.sh|IDOR challenges for benchmarking"
  "10|VaultRip Range|vaultriprange.sh|SSH credential-rich target for VaultRip passive and remote harvesting"
  "11|REWIND|rewindrange.sh|Retro video and games store — SQLi, XSS and IDOR"
  "12|HumanBank|humanbank.sh|Vulnerable online banking app — SQLi, IDOR, XSS, auth flaws, file upload, business logic"
  "13|MediHuman|medihuman.sh|Vulnerable healthcare patient portal — SQLi, IDOR, XSS, file upload, SSH/FTP weak creds"
)

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
  local id="$2"

  local matched=""
  for entry in "${LABS[@]}"; do
    IFS='|' read -r lid _name lscript _desc <<< "$entry"
    if [[ "$lid" == "$id" ]]; then
      matched="$lscript"
      break
    fi
  done

  if [[ -z "$matched" ]]; then
    bad "Unknown lab ID: $id"
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

# ---------------- interactive menu --------------------------------------------
interactive_menu() {
  list_labs
  echo -e "  ${BOLD}Commands:${RESET}"
  echo -e "  ${GREEN}start <id>${RESET}   — Start a lab by ID (e.g. start 1)"
  echo -e "  ${GREEN}stop <id>${RESET}    — Stop a lab by ID"
  echo -e "  ${GREEN}status${RESET}       — Show running lab containers"
  echo -e "  ${GREEN}start all${RESET}    — Start all labs"
  echo -e "  ${GREEN}stop all${RESET}     — Stop all labs"
  echo -e "  ${GREEN}list${RESET}         — List available labs"
  echo -e "  ${GREEN}quit${RESET}         — Exit"
  echo ""

  while true; do
    echo -ne "  ${BOLD}lab>${RESET} "
    read -r cmd arg1 || break
    case "$cmd" in
      start)
        check_docker
        if [[ "${arg1:-}" == "all" ]]; then all_action start
        else dispatch start "${arg1:-}"; fi ;;
      stop)
        if [[ "${arg1:-}" == "all" ]]; then all_action stop
        else dispatch stop "${arg1:-}"; fi ;;
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
    if [[ "${2:-}" == "all" ]]; then all_action start
    else dispatch start "${2:-}"; fi ;;
  stop)
    if [[ "${2:-}" == "all" ]]; then all_action stop
    else dispatch stop "${2:-}"; fi ;;
  help|-h|--help)
    list_labs
    echo "Usage: $0 [menu|list|status|start <id|all>|stop <id|all>]"
    echo "" ;;
  *)
    bad "Unknown command: ${1}"
    echo "Usage: $0 [menu|list|status|start <id|all>|stop <id|all>]"
    exit 1 ;;
esac
