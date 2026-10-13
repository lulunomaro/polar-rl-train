from pathlib import Path
import ast, hashlib, json, os, sys, time, traceback

W = Path('C:/Users/lulu/Desktop/claude/mjcf')
D = Path(__file__).resolve().parent

def connect_linux_only():
    sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret, _ = recover('RM_SSH_PASSWORD')
    assert secret, 'Authorized Linux credential unavailable'
    os.environ['RM_SSH_PASSWORD'] = secret
    sys.path.insert(0, str(W / 'MOD4_AUTONOMY_SLEEP_20261003'))
    from remote_io import connect
    return connect()

REMOTE = r'''
import os,sys,json,time,pathlib,subprocess,hashlib,fcntl,socket
P=pathlib.Path
def run(argv):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=20)
    return dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr)
def blob(p):
    p=P(p)
    if not p.is_file():return dict(path=str(p),exists=False)
    b=p.read_bytes();return dict(path=str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf8',errors='replace'))
def lock(p):
    p=P(p)
    if not p.exists():return dict(path=str(p),exists=False,held=False)
    fd=os.open(p,os.O_RDWR)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return dict(path=str(p),exists=True,held=True)
        fcntl.flock(fd,fcntl.LOCK_UN);return dict(path=str(p),exists=True,held=False)
    finally:os.close(fd)
procs=[]
for p in P('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
        cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
        if not any(s in cmd.lower() for s in ('python','isaac','mod4','kit')):continue
        if p.name==str(os.getpid()):continue
        stat=(p/'stat').read_text(); tail=stat[stat.rfind(')')+2:].split()
        procs.append(dict(pid=int(p.name),start_ticks=int(tail[19]),state=tail[0],ppid=int(tail[1]),argv=cmd,cwd=os.readlink(p/'cwd')))
    except (OSError,ValueError):pass
base=P('/home/egde/rl_candidates')
roots=[]
if base.is_dir():
    for p in sorted(base.iterdir()):
        if any(s in p.name for s in ('LIFETIME','WAVE50','native_floor_continue','scut_spin_rate')):
            roots.append(dict(path=str(p),files=[x.name for x in p.iterdir() if x.is_file()][:100]))
r=dict(epoch=time.time(),hostname=socket.gethostname(),os=run(['uname','-a']),boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),uptime=P('/proc/uptime').read_text(),meminfo=P('/proc/meminfo').read_text(),gpu=run(['nvidia-smi','--query-gpu=name,memory.total,memory.free,driver_version','--format=csv,noheader']),gpu_processes=run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader']),mounts=P('/proc/mounts').read_text(),disks=run(['lsblk','-J','-o','NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS']),processes=procs,roots=roots,budget=blob(base/'MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'),locks=[lock(base/'MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),lock(base/'MOD4_scut_spin_rate_20261002/autonomy_controller.lock')],read_only=True)
print(json.dumps(r,ensure_ascii=False))
'''

def main():
    (D/'reports').mkdir(parents=True,exist_ok=True)
    client=None
    try:
        client=connect_linux_only()
        stdin,stdout,stderr=client.exec_command('python3 -',timeout=30)
        stdin.write(REMOTE);stdin.flush();stdin.channel.shutdown_write()
        raw=stdout.read();err=stderr.read();code=stdout.channel.recv_exit_status()
        receipt=dict(epoch=time.time(),host='10.24.4.210',user='egde',code=code,stderr=err.decode(errors='replace'),read_only=True)
        assert code==0, receipt
        result=json.loads(raw)
        path=D/'reports'/('LINUX_RESUME_BOUNDARY_ACTUAL_'+str(time.time_ns())+'.json')
        path.write_bytes(json.dumps(dict(transport=receipt,actual=result),ensure_ascii=False,indent=2).encode('utf8'))
        print(json.dumps(dict(report=str(path),hostname=result['hostname'],gpu=result['gpu'],gpu_processes=result['gpu_processes'],locks=result['locks'],budget_SHA=result['budget'].get('sha256'),process_count=len(result['processes'])),ensure_ascii=False))
    except BaseException:
        path=D/'reports'/('LINUX_RESUME_BOUNDARY_ERROR_'+str(time.time_ns())+'.json')
        path.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True),indent=2),encoding='utf8')
        print(json.dumps(dict(error_report=str(path))))
        raise
    finally:
        if client:client.close()
        os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':main()
