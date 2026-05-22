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
| 1 | [**Rewind**](labs/rewindrange/README.md) | Retro video and games store — SQLi, XSS and IDOR | `8082` |
| 2 | [**TradeFloor**](labs/tradefloor/README.md) | Vulnerable trading portal — XXE, CSRF, mass assignment, SQLi, IDOR, stored XSS | `8086` |
| 3 | [**GoldenAce**](labs/goldenace/README.md) | Vulnerable online casino — SQLi, IDOR, stored XSS, CSRF, business logic, JWT alg:none | `8087` |
| 4 | [**HumanBank**](labs/humanbank/README.md) | Vulnerable online banking app — SQLi, IDOR, XSS, auth flaws, file upload, business logic | `8083` |
| 5 | [**MediHuman**](labs/medihuman/README.md) | Vulnerable healthcare patient portal — SQLi, IDOR, XSS, file upload, SSH/FTP weak creds | `8084`, `2224`, `2121` |
| 6 | [**NetPulse**](labs/netpulse/README.md) | Vulnerable 90s ISP portal — SSRF, SSTI, command injection, open redirect, SQLi, IDOR, XSS | `8085` |
| 7 | [**BreachSQL**](labs/firerange/README.md) | Tiered SQL injection challenges (T1-T5) for SQLi practice | `17476` |
| 8 | [**StingXSS**](labs/stingxss/README.md) | Tiered XSS challenges (T1-T8) for XSS injection practice | `17477` |
| 9 | [**VaultGate**](labs/vaultgate/README.md) | IDOR challenges for benchmarking | `17478` |
| 10 | [**VaultRip**](labs/vaultriprange/README.md) | SSH credential-rich target for VaultRip passive and remote harvesting | `2222` |
| 11 | **Juice Shop** | OWASP Juice Shop — OWASP Top 10 web vulnerabilities | `3000` |
| 12 | **DVWA** | Damn Vulnerable Web App — PHP/MySQL classic | `8080` |
| 13 | **Metasploitable2** | Linux VM with intentionally vulnerable services | `8081`, `2222`, `21`, `445`, … |
| 14 | **WebGoat** | OWASP WebGoat — lesson-based Java security training | `8888`, `9191` |
| 15 | **HTB Style** | HackTheBox-style CTFd platform + vulnerable challenge | `8001`, `8090` |
| 16 | **VulnAD** | Vulnerable Active Directory — Samba4 AD with AD attack paths | `88`, `389`, `4445` |

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
