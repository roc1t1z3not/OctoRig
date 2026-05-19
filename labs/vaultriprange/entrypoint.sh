#!/usr/bin/env bash
# VaultRip Range entrypoint — start sshd and a memory-resident secret process.
set -e

mkdir -p /run/sshd

# Background process that holds secrets in env/memory.
# Run vaultrip locally inside the container to exercise the memory scanner.
python3 -c "
import os, time, signal, sys
os.environ['DATABASE_PASSWORD']  = 'MemoryExposed123!'
os.environ['API_SECRET']         = 'sk-memory-test-secret-key-abcdef123456'
os.environ['REDIS_URL']          = 'redis://:CachedPass789@127.0.0.1:6379/0'
os.environ['STRIPE_SECRET_KEY']  = 'sk_live_FakeStripeKeyForLabTesting1234'
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
while True:
    time.sleep(60)
" &

exec /usr/sbin/sshd -D -e
