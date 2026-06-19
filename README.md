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
./octorig.sh platform start      # API + workers + UI  →  http://localhost:3000
./octorig.sh platform stop       # stop platform services
```

Drive labs directly from the CLI instead:

```bash
./octorig.sh              # interactive menu
./octorig.sh start 1      # Start a specific lab
./octorig.sh start all    # Start all labs
./octorig.sh status       # Show running labs
./octorig.sh stop all     # Tear everything down
```

---

## Available Labs

OctoRig ships with multiple labs across three categories:

- **Real-world scenarios** — full-stack web apps (e-commerce, banking, healthcare, trading, ISP portal, casino, cinema, community forum) with layered, realistic vulnerability chains
- **Scanner fire-ranges** — purpose-built SQLi, XSS, and IDOR challenge sets for tool benchmarking and focused practice
- **Third-party classics** — Juice Shop, DVWA, Metasploitable2, WebGoat, and a Vulnerable Active Directory environment

Full lab list with IPs, credentials, and vulnerability details: [Labs Overview →](https://github.com/CommonHuman-Lab/OctoRig/wiki/Labs-Overview)

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

## Platform

OctoRig includes a self-hosted training platform that layers CTF-style challenge competitions, achievement badges, user profiles, and a content marketplace on top of the lab infrastructure. It runs alongside the labs and feeds fire-range scores into a global scoreboard and badge engine.

→ See [platform/README.md](platform/README.md) for setup and usage.

---

## Legal & Ethical Use

OctoRig is intended for use in **isolated lab environments only**.

- Run on a dedicated machine or VM — never expose lab containers to a public network
- All labs contain intentionally vulnerable software — treat accordingly

---

## License

This project is dual-licensed.

### Community License (AGPL-3.0)

You may use, modify, and distribute this software under the terms of the GNU Affero General Public License v3.0 (AGPL-3.0).

If you distribute this software or make it available as a network service, you must comply with the requirements of the AGPL, including providing access to the corresponding source code.

### Commercial License

A separate commercial license is available for organizations that wish to use this software without the obligations of the AGPL, including proprietary products, closed-source services, OEM integrations, white-label solutions, or commercial redistribution.

For commercial licensing inquiries, contact the author.