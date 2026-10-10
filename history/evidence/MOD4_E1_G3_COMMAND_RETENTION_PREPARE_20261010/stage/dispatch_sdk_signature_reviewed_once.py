"""One dispatch of the new scope; its parent alone accounts its eventual PPO segments."""
from pathlib import Path
import json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_SDK_REVIEWED_20261010'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert json.loads((R/'SDK_REPAIR_TARGET_CPU_ADMITTED.json').read_bytes())['passed']
 save('SDK_REPAIR_DISPATCH_REQUESTED.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-RETENTION-DISPATCH-01',only_new_scope_once=True,no_budget_extension=True))
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import sys,json,subprocess,time,os
D=Path(NEW_VALUE);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_e1_command_retention_sdk_reviewed_once as m
m.verify();m.wait_existing();m.source()
# The separate dispatch guard also recognizes any old/new PPO entry, beyond
# the copied controller's historical list. No signals or state clearing.
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  argv=[Path(a.decode(errors='replace')).name for a in p.read_bytes().split(b'\0')]
  assert not any((a.startswith('train_') and a.endswith('_ppo.py')) or (a.startswith('native_e1_') and a.endswith('_probe.py')) for a in argv),(p.parent.name,argv)
 except OSError:continue
assert not (D/'dispatch.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'dispatch.log').open('x') as out:
 p=subprocess.Popen([PY_VALUE,str(D/'supervise_e1_command_retention_sdk_reviewed_once.py')],cwd='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002',stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(3);assert p.poll() is None,(D/'dispatch.log').read_text()
q=Path('/proc')/str(p.pid);st=(q/'stat').read_text().split(') ',1)[1].split()
print(json.dumps(dict(epoch=time.time(),parent=dict(pid=p.pid,state=st[0],start_ticks=int(st[19]),cwd=os.readlink(q/'cwd'),argv=(q/'cmdline').read_bytes().decode().split('\0')),source_count=len(m.read(D/'reports/SOURCE_FREEZE.json')['sha256']),root=str(D),only_new_command_scope=True,first_formal_seconds_after_actual_contracts=300,new_budget_seconds=0,actual_native_and_PPO_results_pending=True)))
'''.replace('NEW_VALUE',repr(NEW)).replace('PY_VALUE',repr(PY))
  _,o,e=c.exec_command(PY+' -c '+shlex.quote(code),timeout=180);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');v=json.loads(b);save('SDK_REPAIR_DISPATCH_ACTUAL.json',v);print(json.dumps(v))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('SDK_REPAIR_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_dispatch_or_blind_resume=True));raise
