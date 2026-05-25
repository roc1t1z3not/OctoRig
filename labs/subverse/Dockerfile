FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor netcat-openbsd curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials for sysadmin user
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash sysadmin && echo "sysadmin:subverse2024" | chpasswd && \
    mkdir -p /home/sysadmin/.ssh && \
    ssh-keygen -t rsa -b 2048 -f /home/sysadmin/.ssh/id_rsa -N "" -q && \
    chown -R sysadmin:sysadmin /home/sysadmin/.ssh && \
    chmod 700 /home/sysadmin/.ssh && chmod 600 /home/sysadmin/.ssh/id_rsa

# Bash history hints
RUN printf 'sqlite3 /data/subverse.db .dump > /tmp/backup.sql\nftp localhost\ncat /app/.env\n' \
    > /home/sysadmin/.bash_history && \
    chown sysadmin:sysadmin /home/sysadmin/.bash_history

# FTP — vsftpd anonymous access
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/subverse.conf
COPY . .

RUN mkdir -p /data /app/static/uploads

# App environment hints (discoverable via SSH)
RUN printf 'SECRET_KEY=subverse-2026-xK9mQp7\nDB_PATH=/data/subverse.db\n' > /app/.env

# Seed FTP pub files
RUN printf '-- SubVerse DB Backup 2024-12-01\n-- WARNING: MD5 password hashes\nCREATE TABLE IF NOT EXISTS users (\n  id INTEGER PRIMARY KEY, username TEXT, email TEXT,\n  password_hash TEXT, role TEXT, karma INTEGER\n);\nINSERT INTO users VALUES\n  (1,"admin","admin@subverse.local","36b809e24478355e344545720ea7e090","admin",9999),\n  (2,"mod_alice","alice@subverse.local","7c6a180b36896a0a8c02787eeafb0e4c","moderator",4500),\n  (3,"mod_bob","bob@subverse.local","0d107d09f5bbe40cade3de5c71e9e9b7","moderator",3200),\n  (4,"sv_dan","dan.foster@mail.example","d5c0607301ad5d5c1528962a83992ac8","user",850),\n  (5,"pixel_kate","kate.p@mail.example","e65c8afc9951f94fed8873a4c1e31a63","user",420),\n  (6,"tech_marcus","marcus.t@mail.example","f25a2fc72690b780b2a14e140ef6a9e0","user",720),\n  (7,"sara_q","sara.q@mail.example","cc25c0f861a83f5efadc6e1ba9d1269e","user",310),\n  (8,"ghost_user","ghost@mail.example","b696aef7776367787253dc2acdd10279","user",55);\n' \
    > /srv/ftp/pub/db_backup_2024.sql && \
    printf 'SubVerse Deployment Notes\n=========================\nSSH:  sysadmin@<host>  pw: subverse2024\nDB:   /data/subverse.db\nApp:  /app/\nFTP passive ports: 30010-30019\n\nNOTE: Change default SSH password before production deployment.\n' \
    > /srv/ftp/pub/deploy_notes.txt && \
    printf 'id,username,email,created_at\n1,admin,admin@subverse.local,2025-01-01 00:00:00\n2,mod_alice,alice@subverse.local,2025-01-05 08:00:00\n3,mod_bob,bob@subverse.local,2025-01-06 09:00:00\n4,sv_dan,dan.foster@mail.example,2025-02-10 12:00:00\n5,pixel_kate,kate.p@mail.example,2025-02-14 15:30:00\n6,tech_marcus,marcus.t@mail.example,2025-02-20 11:00:00\n7,sara_q,sara.q@mail.example,2025-03-01 09:45:00\n8,ghost_user,ghost@mail.example,2025-03-15 20:00:00\n' \
    > /srv/ftp/pub/users_export.csv && \
    chown ftp:ftp /srv/ftp/pub/db_backup_2024.sql /srv/ftp/pub/deploy_notes.txt /srv/ftp/pub/users_export.csv && \
    chmod 644 /srv/ftp/pub/db_backup_2024.sql /srv/ftp/pub/deploy_notes.txt /srv/ftp/pub/users_export.csv

EXPOSE 80 21 22 30010-30019
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
