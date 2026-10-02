"""Upload many local paths to the training host inside ONE ssh/sftp session.

The per-file `tsh.py put` helper opens a fresh SSH connection every time, which is fine
for a handful of files but painful for a model directory with ~120 STL assets.  This
helper walks directories recursively and reuses one SFTP channel.

Usage:
    python scripts/tsh_sync.py <local>|<remote> [<local>|<remote> ...]
    python scripts/tsh_sync.py --dry-run <local>|<remote> ...

Directories are uploaded recursively (regular files only); missing remote directories
are created.  Progress goes to stdout and to $TSH_OUT when set.
"""
from __future__ import annotations

import io
import os
import posixpath
import sys

import paramiko

HOST = "10.24.4.210"
USER = "egde"
PWD = "1"


def remote_makedirs(sftp: paramiko.SFTPClient, path: str) -> None:
    parts = path.strip("/").split("/")
    cur = "" if path.startswith("/") else "."
    for part in parts:
        cur = posixpath.join(cur, part)
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)


def push(sftp: paramiko.SFTPClient, local: str, remote: str, out: io.TextIOBase, dry: bool) -> int:
    if os.path.isdir(local):
        count = 0
        for root, _dirs, files in os.walk(local):
            rel = os.path.relpath(root, local)
            target_dir = remote if rel == "." else posixpath.join(remote, rel.replace(os.sep, "/"))
            if not dry:
                remote_makedirs(sftp, target_dir)
            for name in sorted(files):
                src = os.path.join(root, name)
                dst = posixpath.join(target_dir, name)
                if dry:
                    out.write("DRY  %s -> %s\n" % (src, dst))
                else:
                    sftp.put(src, dst)
                    out.write("PUT  %s -> %s (%d bytes)\n" % (src, dst, os.path.getsize(src)))
                count += 1
        return count
    if not dry:
        remote_makedirs(sftp, posixpath.dirname(remote))
        sftp.put(local, remote)
        out.write("PUT  %s -> %s (%d bytes)\n" % (local, remote, os.path.getsize(local)))
    else:
        out.write("DRY  %s -> %s\n" % (local, remote))
    return 1


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    pairs = [a for a in argv[1:] if not a.startswith("--")]
    if not pairs:
        print(__doc__)
        return 2
    out_path = os.environ.get("TSH_OUT") or r"D:\claude2\fangzhen\docs\_tsh_sync.txt"
    out = io.open(out_path, "w", encoding="utf8", newline="\n")
    total = 0
    try:
        if dry:
            for pair in pairs:
                local, remote = pair.split("|", 1)
                total += push(None, local, remote, out, True)  # type: ignore[arg-type]
        else:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(HOST, username=USER, password=PWD, timeout=25, banner_timeout=40, auth_timeout=40)
            sftp = client.open_sftp()
            try:
                for pair in pairs:
                    local, remote = pair.split("|", 1)
                    total += push(sftp, local, remote, out, False)
            finally:
                sftp.close()
                client.close()
    finally:
        out.write("TOTAL %d file(s)\n" % total)
        out.close()
    print("DONE %d" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
