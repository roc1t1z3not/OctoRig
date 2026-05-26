# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Simulates vsftpd 2.3.4 backdoor (CVE-2011-2523).
Banner and behaviour are identical to the real thing:
  USER with ':)' anywhere in the username → binds /bin/sh to port 6200.
Works with Metasploit: exploit/unix/ftp/vsftpd_234_backdoor
"""
import socket
import subprocess
import threading
import time

BACKDOOR_PORT = 6200

_backdoor_open = False
_lock = threading.Lock()


def _backdoor_listener():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ss.bind(("0.0.0.0", BACKDOOR_PORT))
        ss.listen(5)
        while True:
            conn, _ = ss.accept()
            fd = conn.fileno()
            subprocess.Popen(
                ["/bin/sh"],
                stdin=fd, stdout=fd, stderr=fd,
                close_fds=True,
            )
    except Exception:
        pass


def _handle(conn):
    try:
        conn.sendall(b"220 (vsFTPd 2.3.4)\r\n")
        global _backdoor_open
        while True:
            data = conn.recv(1024)
            if not data:
                break
            line = data.decode(errors="ignore").strip()
            tag = line[:4].upper()

            if tag == "USER":
                arg = line[5:] if len(line) > 5 else ""
                if ":)" in arg:
                    with _lock:
                        if not _backdoor_open:
                            _backdoor_open = True
                            threading.Thread(
                                target=_backdoor_listener, daemon=True
                            ).start()
                            time.sleep(0.15)
                conn.sendall(b"331 Please specify the password.\r\n")

            elif tag == "PASS":
                conn.sendall(b"530 Login incorrect.\r\n")

            elif tag == "QUIT":
                conn.sendall(b"221 Goodbye.\r\n")
                break

            elif tag == "SYST":
                conn.sendall(b"215 UNIX Type: L8\r\n")

            elif tag == "FEAT":
                conn.sendall(
                    b"211-Features:\r\n"
                    b" EPRT\r\n EPSV\r\n MDTM\r\n PASV\r\n"
                    b" REST STREAM\r\n SIZE\r\n TVFS\r\n"
                    b"211 End\r\n"
                )
            else:
                conn.sendall(b"500 Unknown command.\r\n")

    except Exception:
        pass
    finally:
        conn.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 21))
    srv.listen(10)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=_handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
