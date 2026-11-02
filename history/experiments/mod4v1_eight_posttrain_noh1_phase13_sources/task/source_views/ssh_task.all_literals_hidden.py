"""<string-literal-1>"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, pathlib, posixpath, sys
sys.path.insert(0, '<string-literal-2>')
import paramiko
HOST = '<string-literal-3>'
PIN = '<string-literal-4>'
ROOT = '<string-literal-5>'

class Pin(paramiko.MissingHostKeyPolicy):

    def missing_host_key(self, client, hostname, key):
        actual = base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('<string-literal-6>')
        if actual != PIN:
            raise paramiko.SSHException('<string-literal-7>')

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(Pin())
    c.connect(HOST, username='<string-literal-8>', password=os.environ['<string-literal-9>'], timeout=12, auth_timeout=15, look_for_keys=False, allow_agent=False)
    return c

def mkdirs(s, path):
    if not (path == ROOT or path.startswith(ROOT + '<string-literal-10>')):
        raise ValueError('<string-literal-11>')
    parts = path.split('<string-literal-12>')
    acc = '<string-literal-13>'
    for part in parts:
        if not part:
            continue
        acc += '<string-literal-14>' + part
        try:
            s.stat(acc)
        except FileNotFoundError:
            if not (acc == ROOT or acc.startswith(ROOT + '<string-literal-15>')):
                raise
            s.mkdir(acc)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('<string-literal-16>')
    p.add_argument('<string-literal-17>')
    p.add_argument('<string-literal-18>', nargs=2, action='<string-literal-19>', default=[])
    p.add_argument('<string-literal-20>', nargs=2, action='<string-literal-21>', default=[])
    p.add_argument('<string-literal-22>')
    p.add_argument('<string-literal-23>')
    p.add_argument('<string-literal-24>', type=int, default=180)
    a = p.parse_args()
    c = connect()
    try:
        if a.upload or a.download or a.list or a.read:
            s = c.open_sftp()
            for local, rel in a.upload:
                dst = posixpath.normpath(ROOT + '<string-literal-25>' + rel)
                if not dst.startswith(ROOT + '<string-literal-26>'):
                    raise ValueError('<string-literal-27>')
                mkdirs(s, posixpath.dirname(dst))
                s.put(local, dst)
                print(json.dumps({'<string-literal-28>': rel, '<string-literal-29>': pathlib.Path(local).stat().st_size}), flush=True)
            for rel, local in a.download:
                src = posixpath.normpath(ROOT + '<string-literal-30>' + rel)
                if not src.startswith(ROOT + '<string-literal-31>'):
                    raise ValueError('<string-literal-32>')
                pathlib.Path(local).parent.mkdir(parents=True, exist_ok=True)
                s.get(src, local)
                print(json.dumps({'<string-literal-33>': rel}), flush=True)
            if a.list:
                print(json.dumps([{'<string-literal-34>': v.filename, '<string-literal-35>': v.st_size} for v in s.listdir_attr(a.list)], ensure_ascii=False), flush=True)
            if a.read:
                with s.open(a.read, '<string-literal-36>') as f:
                    data = f.read(160000)
                print(data.decode('<string-literal-37>', '<string-literal-38>'), flush=True)
            s.close()
        command = a.cmd
        if a.script:
            command = pathlib.Path(a.script).read_text(encoding='<string-literal-39>')
        if command:
            si, so, se = c.exec_command(command, timeout=a.timeout)
            si.close()
            ch = so.channel
            import select, time
            while not ch.exit_status_ready() or ch.recv_ready() or ch.recv_stderr_ready():
                if ch.recv_ready():
                    sys.stdout.write(ch.recv(65536).decode('<string-literal-40>', '<string-literal-41>'))
                    sys.stdout.flush()
                if ch.recv_stderr_ready():
                    sys.stderr.write(ch.recv_stderr(65536).decode('<string-literal-42>', '<string-literal-43>'))
                    sys.stderr.flush()
                if not ch.recv_ready() and (not ch.recv_stderr_ready()):
                    time.sleep(0.05)
            code = ch.recv_exit_status()
            print('<string-literal-44>' + str(code), flush=True)
            if code:
                raise SystemExit(code)
    finally:
        c.close()
if __name__ == '<string-literal-45>':
    main()