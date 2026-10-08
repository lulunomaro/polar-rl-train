"""Install new CPU-only corrected-world publication; no production source changes."""
from pathlib import Path
import sys,shlex,json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
assert not (R/'WORLD_PUBLICATION_DEPLOYED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D4_WORLD_DISPATCH_REVIEW_20261008'
try:
    _,o,e=c.exec_command('mkdir -p '+shlex.quote(root+'/reports'),timeout=15);assert o.channel.recv_exit_status()==0,e.read().decode()
    with c.open_sftp() as f:
        for name in ('build_world_package.py','supervise_world_evidence_publication.py'):
            raw=(D/name).read_bytes()
            with f.open(root+'/'+name,'wb') as out:out.write(raw)
            assert hashlib.sha256(f.open(root+'/'+name).read()).hexdigest()==hashlib.sha256(raw).hexdigest()
    _,o,e=c.exec_command('/usr/bin/python3 '+shlex.quote(root+'/build_world_package.py'),timeout=30)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    (R/'WORLD_DISPATCH_PACKAGE.json').write_bytes(raw)
    code=r'''
from pathlib import Path
import subprocess,json,os,time
D=Path('/home/egde/rl_candidates/MOD4_D4_WORLD_DISPATCH_REVIEW_20261008')
assert not (D/'reports/PUBLISHER_STARTED.json').exists()
with (D/'publisher.log').open('x') as f:
 p=subprocess.Popen(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(D/'supervise_world_evidence_publication.py')],cwd=D,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.5)
st=Path('/proc/'+str(p.pid)+'/stat').read_text();tail=st[st.rfind(')')+2:].split();argv=Path('/proc/'+str(p.pid)+'/cmdline').read_bytes().decode().strip('\0').split('\0')
assert tail[0]!='Z' and str(D/'supervise_world_evidence_publication.py') in argv
v=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),argv=argv,CPU_only=True,production243_source_unchanged=True,no_GPU_PPO_or_canonical_write=True)
(D/'reports/WORLD_PUBLICATION_DEPLOYED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=15)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    (R/'WORLD_PUBLICATION_DEPLOYED.json').write_bytes(raw);print(raw.decode())
finally:c.close()
