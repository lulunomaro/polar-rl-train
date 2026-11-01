"""Task-scoped SSH operations; password is supplied only in process environment."""
from __future__ import annotations
import argparse, base64, hashlib, json, os, pathlib, posixpath, sys
sys.path.insert(0, r'C:\Users\lulu\AppData\Local\Temp\dsh-ssh-e70a94a1\deps')
import paramiko
HOST='10.24.0.72'
PIN='MBqYN+hQO2ZPpM7d4gQHdp2PG4auWdmlSvsja9+kF5U'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
class Pin(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self,client,hostname,key):
        actual=base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
        if actual!=PIN: raise paramiko.SSHException('Host key differs from verified host72')
def connect():
    c=paramiko.SSHClient(); c.set_missing_host_key_policy(Pin())
    c.connect(HOST, username='lc01', password=os.environ['MOD4_SSH_PASSWORD'], timeout=12,auth_timeout=15,look_for_keys=False,allow_agent=False)
    return c

def mkdirs(s,path):
    if not (path==ROOT or path.startswith(ROOT+'/')):raise ValueError('write outside task root')
    parts=path.split('/'); acc=''
    for part in parts:
        if not part:continue
        acc+='/'+part
        try:s.stat(acc)
        except FileNotFoundError:
            if not (acc==ROOT or acc.startswith(ROOT+'/')):raise
            s.mkdir(acc)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cmd');p.add_argument('--script');p.add_argument('--upload',nargs=2,action='append',default=[]);p.add_argument('--download',nargs=2,action='append',default=[]);p.add_argument('--list');p.add_argument('--read');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    c=connect()
    try:
        if a.upload or a.download or a.list or a.read:
            s=c.open_sftp()
            for local,rel in a.upload:
                dst=posixpath.normpath(ROOT+'/'+rel)
                if not dst.startswith(ROOT+'/'):raise ValueError('outside root')
                mkdirs(s,posixpath.dirname(dst));s.put(local,dst);print(json.dumps({'uploaded':rel,'bytes':pathlib.Path(local).stat().st_size}),flush=True)
            for rel,local in a.download:
                src=posixpath.normpath(ROOT+'/'+rel)
                if not src.startswith(ROOT+'/'):raise ValueError('outside root')
                pathlib.Path(local).parent.mkdir(parents=True,exist_ok=True);s.get(src,local);print(json.dumps({'downloaded':rel}),flush=True)
            if a.list:print(json.dumps([{'name':v.filename,'bytes':v.st_size} for v in s.listdir_attr(a.list)],ensure_ascii=False),flush=True)
            if a.read:
                with s.open(a.read,'rb') as f:data=f.read(160000)
                print(data.decode('utf-8','replace'),flush=True)
            s.close()
        command=a.cmd
        if a.script:command=pathlib.Path(a.script).read_text(encoding='utf-8')
        if command:
            si,so,se=c.exec_command(command,timeout=a.timeout);si.close()
            # Drain both streams to avoid a remote pipe deadlock.
            ch=so.channel
            import select,time
            while not ch.exit_status_ready() or ch.recv_ready() or ch.recv_stderr_ready():
                if ch.recv_ready():sys.stdout.write(ch.recv(65536).decode('utf-8','replace'));sys.stdout.flush()
                if ch.recv_stderr_ready():sys.stderr.write(ch.recv_stderr(65536).decode('utf-8','replace'));sys.stderr.flush()
                if not ch.recv_ready() and not ch.recv_stderr_ready():time.sleep(.05)
            code=ch.recv_exit_status();print('\nREMOTE_EXIT='+str(code),flush=True)
            if code:raise SystemExit(code)
    finally:c.close()
if __name__=='__main__':main()
