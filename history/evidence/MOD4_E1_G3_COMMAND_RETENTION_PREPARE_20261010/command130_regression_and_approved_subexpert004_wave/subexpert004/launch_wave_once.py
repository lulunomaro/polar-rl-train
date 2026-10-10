"""Dispatch only the newly admitted isolated Wave root, once."""
from pathlib import Path
import json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';NEW='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 assert json.loads((R/'WAVE_TARGET_CPU_ADMITTED.json').read_bytes())['passed'] and not (R/'WAVE_DISPATCH_STARTED.json').exists()
 save('WAVE_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='E1-WAVE-INDEPENDENT-REVISION004-DISPATCH-01',only_new_entry=True,seconds=300,new_budget_seconds=0))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import json,subprocess,time
D=Path(ROOT);assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'wave_parent.log').exists()
entry=D/'supervise_e1_wave_isolated_revision004_once.py';assert entry.exists()
with (D/'wave_parent.log').open('x') as out:p=subprocess.Popen(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(entry)],cwd=str(D),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
proc=Path('/proc')/str(p.pid);tail=(proc/'stat').read_text().split(') ',1)[1].split();argv=(proc/'cmdline').read_bytes().split(b'\0');assert any(str(entry).encode()==a for a in argv)
v=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),argv=[a.decode() for a in argv if a],cwd=str((proc/'cwd').resolve()),new_root=str(D),only_new_isolated_wave_entry=True,no_duplicate_preflight_or_budget_extension=True)
(D/'reports/WAVE_PARENT_DISPATCH_RECEIPT.json').write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(v))
'''.replace('Path(ROOT)','Path('+repr(NEW)+')')
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');v=json.loads(out);save('WAVE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('WAVE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),new_parent_may_exist_do_not_repeat=True));raise
