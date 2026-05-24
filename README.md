<p align="center">
  <img src="assets/octorig_logo.png" alt="OctoRig" width="200"/>
</p>

<h1 align="center">OctoRig</h1>
<p align="center"><em>Spin up realistic vulnerable environments for pentesting, security research, and offensive security training — with a single command.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/Shell-Bash-green.svg" />
  <img src="https://img.shields.io/badge/Runtime-Docker-blue.svg" />
  <img src="https://img.shields.io/badge/focus-offensive--security-darkred.svg" />
</p>

---

OctoRig is a modular vulnerable lab platform that spins up realistic Docker-based targets for penetration testing practice, security research, red team training, and security tool validation — all with a single command.

Unlike traditional CTF-style machines, OctoRig labs are designed to feel closer to real-world applications and infrastructure. Each environment contains layered vulnerabilities, insecure business logic, hidden attack paths, weak operational security, and realistic application flows for deeper testing and exploration.

## Features

- One-command lab deployment
- Fully isolated Docker environments
- Realistic vulnerable applications
- Multiple vulnerability classes per lab
- Designed for DAST and offensive tooling
- Beginner to advanced attack paths
- Hidden easter eggs and chained exploits
- Fast teardown and reset workflows
- Ideal for workshops, demos, and practice environments

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
| 1 | [**Rewind**](labs/rewindrange/README.md) | Retro gaming and media storefront featuring SQL injection, XSS, IDOR, and insecure legacy functionality | `8082` |
| 2 | [**TradeFloor**](labs/tradefloor/README.md) | Vulnerable trading platform with XXE, CSRF, mass assignment, SQLi, IDOR, and stored XSS | `8086` |
| 3 | [**GoldenAce**](labs/goldenace/README.md) | Online casino environment containing SQLi, JWT flaws, IDOR, stored XSS, CSRF, and business logic vulnerabilities | `8087` |
| 4 | [**HumanBank**](labs/humanbank/README.md) | Vulnerable online banking application with authentication flaws, SQLi, XSS, insecure uploads, and business logic abuse | `8083` |
| 5 | [**MediHuman**](labs/medihuman/README.md) | Healthcare patient portal exposing SQLi, IDOR, XSS, insecure file handling, and weak SSH/FTP configurations | `8084`, `2224`, `2121` |
| 6 | [**NetPulse**](labs/netpulse/README.md) | 90s-inspired ISP management portal vulnerable to SSRF, SSTI, command injection, open redirects, SQLi, IDOR, and XSS | `8085` |
| 7 | [**Limelight**](labs/limelight/README.md) | Vulnerable cinema booking platform with SQLi, XSS, IDOR, SSTI, CSRF, business logic abuse, and mass assignment | `8088` |
| 8 | [**BreachSQL**](labs/firerange/README.md) | Tiered SQL injection challenges (T1-T5) for SQLi practice | `17476` |
| 9 | [**StingXSS**](labs/stingxss/README.md) | Tiered XSS challenges (T1-T8) for XSS injection practice | `17477` |
| 10 | [**VaultGate**](labs/vaultgate/README.md) | IDOR challenges for benchmarking | `17478` |
| 11 | [**VaultRip**](labs/vaultriprange/README.md) | SSH credential-rich target for VaultRip passive and remote harvesting | `2222` |
| 12 | **Juice Shop** | OWASP Juice Shop — OWASP Top 10 web vulnerabilities | `3000` |
| 13 | **DVWA** | Damn Vulnerable Web App — PHP/MySQL classic | `8080` |
| 14 | **Metasploitable2** | Linux VM with intentionally vulnerable services | `8081`, `2222`, `21`, `445`, … |
| 15 | **WebGoat** | OWASP WebGoat — lesson-based Java security training | `8888`, `9191` |
| 16 | **HTB Style** | HackTheBox-style CTFd platform + vulnerable challenge | `8001`, `8090` |
| 17 | **VulnAD** | Vulnerable Active Directory — Samba4 AD with AD attack paths | `88`, `389`, `4445` |

---

## Requirements

- Docker (daemon running)
- Bash 4.0+
- `nc` (netcat)
- Internet access on first run (image pulls)

---

## Philosophy

OctoRig focuses on realistic offensive security training rather than artificial puzzle-based challenges.

The goal is to provide reproducible vulnerable environments that resemble modern applications, internal tooling, and operational mistakes commonly encountered during real assessments.

## Legal & Ethical Use

OctoRig is intended for use in **isolated lab environments only**.

- Run on a dedicated machine or VM — never expose lab containers to a public network
- All labs contain intentionally vulnerable software — treat accordingly
