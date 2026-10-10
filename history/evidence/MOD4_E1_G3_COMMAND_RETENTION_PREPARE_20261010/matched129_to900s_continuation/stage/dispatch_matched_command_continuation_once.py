"""One dispatch of the actual129-admitted365 matched900s; never reuse old dispatch."""
from pathlib import Path
import json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode())
def main():
 assert json.loads((R/'COMMAND_MATCHED_TARGET_CPU_ADMITTED.json').read_bytes())['passed']
 save('COMMAND_MATCHED_DISPATCH_REQUESTED.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-900S-DEPLOY-01',same_scope900s_only=True,new_budget_seconds=0))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import sys,json,subprocess,time,os
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_e1_command_retention_matched_once as m
m.verify();m.wait_existing();m.source()
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  argv=[Path(x.decode(errors='replace')).name for x in p.read_bytes().split(b'\0')]
  assert not any((a.startswith('train_') and a.endswith('_ppo.py')) or (a.startswith('native_e1_') and a.endswith('_probe.py')) for a in argv),(p.parent.name,argv)
 except OSError:continue
assert not (D/'dispatch.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'dispatch.log').open('x') as out:p=subprocess.Popen([PYTHON,str(D/'supervise_e1_command_retention_matched_once.py')],cwd='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002',stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(3);assert p.poll() is None,(D/'dispatch.log').read_text()
q=Path('/proc')/str(p.pid);tail=(q/'stat').read_text().split(') ',1)[1].split()
print(json.dumps(dict(epoch=time.time(),parent=dict(pid=p.pid,state=tail[0],start_ticks=int(tail[19]),cwd=os.readlink(q/'cwd'),argv=(q/'cmdline').read_bytes().decode().split('\0')),source_count=365,root=str(D),same_scope900s_only=True,no_SDK_native_PPO_preflight_clock_replay=True,fullsameG3_and_command_CUDA_startup_pending_actual=True,new_budget_seconds=0)))
'''.replace('Path(ROOT)','Path('+repr(NEW)+')').replace('[PYTHON,','['+repr(PY)+',')
  compile(code,'<dispatch365>','exec');_,o,e=c.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);save('COMMAND_MATCHED_DISPATCH_ACTUAL.json',v);print(json.dumps(v))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_MATCHED_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_launch_or_blind_resume=True));raise
