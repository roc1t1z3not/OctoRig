<p align="center">
  <img src="assets/octorig_logo.png" alt="OctoRig" width="200"/>
</p>

<h1 align="center">OctoRig</h1>
<p align="center"><em>Bash-based Docker lab launcher for offensive security practice</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/Shell-Bash-green.svg" />
  <img src="https://img.shields.io/badge/Runtime-Docker-blue.svg" />
  <img src="https://img.shields.io/badge/Use-Security%20Labs-red.svg" />
</p>

---

OctoRig spins up and tears down intentionally vulnerable Docker environments for penetration testing practice, security research, and tool testing — with a single command.

---

## Quick Start

```bash
git clone https://github.com/CommonHuman-Lab/OctoRig.git
cd OctoRig
./octorig.sh
```

Or non-interactively:

```bash
./octorig.sh start 1     # Start a specific lab
./octorig.sh start all   # Start all labs
./octorig.sh status      # Show running labs
./octorig.sh stop all    # Tear everything down
```

---

## Available Labs

| ID | Name | Description | Port(s) |
| -- | ---- | ----------- | ------- |
| 1 | **Juice Shop** | OWASP Top 10 + 82 challenges | `3000` |
| 2 | **DVWA** | Classic PHP/MySQL vulnerable app | `8080` |
| 3 | **Metasploitable2** | Linux VM with intentionally vulnerable services | `8081`, `2222`, `445`… |
| 4 | **WebGoat** | Lesson-based Java security training | `8888` |
| 5 | **HTB Style** | CTFd scoreboard + Struts2 CVE-2017-5638 | `8000`, `8090` |
| 6 | **VulnAD** | Vulnerable Active Directory via Samba4 | `389`, `88`, `4445` |
| 7 | **BreachSQL Firerange** | Tiered SQL injection challenges | `17476` |
| 8 | **StingXSS Firerange** | Tiered XSS challenges | `17477` |
| 9 | **VaultGate** | Tiered IDOR challenges | `17478` |
| 10 | **VaultRip Range** | SSH credential-rich target for passive and remote harvesting | `2222` |
| 11 | **REWIND** | Retro video and games store — SQLi, XSS and IDOR | `8082` |
| 12 | **HumanBank** | Vulnerable online banking app — SQLi, IDOR, XSS, auth flaws, file upload, business logic | `8083` |
| 13 | **MediHuman** | Vulnerable healthcare patient portal — SQLi, IDOR, XSS, file upload, SSH/FTP weak creds | `8084`, `2224`, `2121` |
| 14 | **NetPulse** | Vulnerable 90s ISP portal — SSRF, SSTI, command injection, open redirect, SQLi, IDOR, XSS | `8085` |
| 15 | **TradeFloor** | Vulnerable stock trading portal — XXE, CSRF, mass assignment, SQLi, IDOR, stored XSS | `8086` |

---

## Requirements

- Docker (daemon running)
- Bash 4.0+
- `nc` (netcat)
- Internet access on first run (image pulls)

---

## Legal & Ethical Use

OctoRig is intended for use in **isolated lab environments only**.

- Run on a dedicated machine or VM — never expose lab containers to a public network
- All labs contain intentionally vulnerable software — treat accordingly
