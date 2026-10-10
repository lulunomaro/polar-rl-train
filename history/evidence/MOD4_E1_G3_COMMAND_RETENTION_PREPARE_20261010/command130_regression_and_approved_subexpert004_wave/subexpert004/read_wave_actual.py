"""Reusable read-only own-stage observer; missing future reports are pending."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';NEW='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def main():
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import hashlib,json,time
D=Path(ROOT);R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest();B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def identity(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 t=(p/'stat').read_text().split(') ',1)[1].split();return dict(pid=pid,state=t[0],start_ticks=int(t[19]),argv=[x.decode() for x in (p/'cmdline').read_bytes().split(b'\0') if x],cwd=str((p/'cwd').resolve()))
s=read(R/'E1_STATE.json');l=read(B);ids=[]
for loc in [s.get('owner') if s else None,s.get('child') if s else None,read(R/'E1_GUARDIAN_STARTED.json')]:
 if loc:ids.append(dict(locator=loc,actual=identity(loc['pid'])))
reports={};names=['E1_STATE.json','E1_ATTENTION.json','E1_CURRENT_SAVE.json','E1_ACTIVE_HEALTH.json','E1_REVIEW_READY.json','E1_DISPATCH_STARTED.json','E1_INSTALL_BOUNDARY.json','E1_WAVE_OWNERSHIP_FINAL_VERIFIED.json','e1_wave_G3_isolated_observation_PASSED.json','e1_wave_G3_isolated_observation_SAVED_EXIT.json','E1_131-e1-wave-g3-isolated_ASYNC_PUBLISHED.json']
for n in names:
 p=R/n
 if p.exists():reports[n]=read(p)
runs=sorted((D/'learning_logs').glob('*')) if (D/'learning_logs').exists() else []
run=runs[-1] if runs else None;startup={};manifest=None;complete=None;large=[]
if run:
 for p in sorted(run.glob('*STARTUP_VERIFIED.json')):startup[p.name]=read(p)
 manifest=read(run/'run_manifest.json');complete=read(run/'latest_complete.json')
 if complete:
  p=Path(complete['checkpoint']);large.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()),index_only=True,original_retained=True))
remaining=l['authorized_training_seconds']-l['charged_training_seconds'];active=l['active_segment']
v=dict(epoch=time.time(),root=str(D),state=s,actual_identities=ids,reports=reports,startup=startup,run=str(run) if run else None,manifest=manifest,latest_complete=complete,large_originals_index_only=large,canonical=dict(path=str(B),SHA=H(B.read_bytes()),authorized_seconds=l['authorized_training_seconds'],charged_seconds=l['charged_training_seconds'],remaining_before_unaccounted_tail=remaining,active_segment=active),parent_log_tail=(D/'wave_parent.log').read_text(errors='replace')[-2500:],missing_future_final_is_pending=True,no_mutation_or_signal=True)
print(json.dumps(v))
'''.replace('Path(ROOT)','Path('+repr(NEW)+')')
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);p=R/('WAVE_ACTUAL_'+str(int(time.time()))+'.json');assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
  print(json.dumps(dict(report=str(p),phase=v['state']['phase'] if v['state'] else None,attention=v['reports'].get('E1_ATTENTION.json'),actual=v['actual_identities'],startup_files=list(v['startup']),own_checkpoint=v['latest_complete'],canonical=v['canonical'],parent_log_tail=v['parent_log_tail'][-700:])))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
