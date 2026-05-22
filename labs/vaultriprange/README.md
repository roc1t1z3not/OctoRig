# VaultRip Range

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-SSH-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A deliberately credential-rich SSH target built to exercise every harvesting module in [VaultRip](https://github.com/CommonHuman-Lab/vaultrip). Two user accounts hold credentials in every format VaultRip recognises — SSH keys, AWS profiles, kubeconfig bearer tokens, Docker auth, git credentials, pgpass, netrc, my.cnf, shell history, and `.env` files. A background process holds secrets in environment variables so the memory scanner fires too.

> Do not expose this service on a public network.

---

## What to Try

- Run VaultRip in **remote SSH mode** against the lab and watch it sweep both user accounts for every credential type. Check how many distinct secret types it finds.
- Shell into the container as `labuser` and run VaultRip locally to test the **memory scanner** — a background process holds `DATABASE_PASSWORD`, `API_SECRET`, `STRIPE_SECRET_KEY`, and more in its environment.
- Try **restricting to a single user** with `--ssh-user deploy` — VaultRip should find the deploy-specific AWS profile, service `.env`, and bash history entries.
- Dig into `~/.bash_history` on both accounts manually: commands with plaintext credentials in flags are common in real environments and easy to miss without automation.
- Each credential file has its own format quirks — compare what VaultRip extracts from `.netrc` vs `.pgpass` vs `.my.cnf` to understand per-format parsing behaviour.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start vaultriprange

# Stop
./octorig.sh stop vaultriprange
```

SSH is available on **127.0.0.1:2222**.

---

## Access

| Account | Username | Password |
|---------|----------|----------|
| Lab user | `labuser` | `LabUser123!` |
| Deploy user | `deploy` | `Deploy456!` |

```bash
# Shell access
ssh -p 2222 labuser@127.0.0.1
ssh -p 2222 deploy@127.0.0.1
```

---

## VaultRip Test Commands

```bash
# Remote sweep — files, Kerberos, system (memory scanner skipped)
vaultrip --remote 127.0.0.1 --ssh-port 2222 \
         --ssh-user labuser --ssh-pass 'LabUser123!' \
         --no-memory --no-browser

# Deploy user only
vaultrip --remote 127.0.0.1 --ssh-port 2222 \
         --ssh-user deploy --ssh-pass 'Deploy456!'

# Local memory scan (run inside the container)
docker exec -it octorig-vaultriprange bash
# then: vaultrip /home   (if vaultrip is installed in the container)
```

---

## Credential Inventory

### labuser

| Type | Location |
|------|----------|
| SSH private key (RSA 2048) | `~/.ssh/id_rsa` |
| AWS credentials (2 profiles) | `~/.aws/credentials` |
| Kubernetes bearer token | `~/.kube/config` |
| Docker Hub auth | `~/.docker/config.json` |
| GitHub PAT + GitLab token | `~/.git-credentials` |
| PostgreSQL passwords | `~/.pgpass` |
| FTP / API credentials | `~/.netrc` |
| MySQL password | `~/.my.cnf` |
| Commands with plaintext creds | `~/.bash_history` |
| App secrets (.env) | `~/app/.env` |
| Terraform vars | `~/infra/terraform.tfvars` |
| Fake Kerberos ccache | `/tmp/krb5cc_1000` |

### deploy

| Type | Location |
|------|----------|
| SSH private key (Ed25519) | `~/.ssh/id_ed25519` |
| AWS credentials (1 profile) | `~/.aws/credentials` |
| Service secrets (.env) | `~/service/.env` |
| Commands with plaintext creds | `~/.bash_history` |

### Memory (background process)

| Variable | Value |
|----------|-------|
| `DATABASE_PASSWORD` | `MemoryExposed123!` |
| `API_SECRET` | `sk-memory-test-secret-key-abcdef123456` |
| `REDIS_URL` | `redis://:CachedPass789@127.0.0.1:6379/0` |
| `STRIPE_SECRET_KEY` | `sk_live_FakeStripeKeyForLabTesting1234` |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
