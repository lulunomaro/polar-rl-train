"""Read-only proof and evaluation API inventory; no launch, learning or ledger write."""
from pathlib import Path
import sys,json,shlex,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True);REF=D/'reference';REF.mkdir(exist_ok=True)
W=D.parent;ROOT='/home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007';ER='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','LATEST_HANDOFF.md','MOD4_DT1000_WORKING_BASELINE.json','S1A_HISTORY_FULL_GIT_RECORDED.json'):
   s.get(ER+'/'+n,str(R/n))
  names=['isaac/mod4/validate_speed.py','isaac/mod4/contact_calibration_probe.py','isaac/mod4/world_spin_probe.py','isaac/mod4/policy_migration.py',
   'isaac/mod4/contact_aligned_clock.py','isaac/mod4/mod4_env.py','isaac/mod4/env.json']
  index={}
  for n in names:
   p=REF/n;p.parent.mkdir(parents=True,exist_ok=True)
   try:s.get(ROOT+'/'+n,str(p));index[n]=hashlib.sha256(p.read_bytes()).hexdigest()
   except FileNotFoundError:index[n]='missing'
  (R/'EVALUATION_SOURCE_API_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
 code=r'''
from pathlib import Path
import sys,json,time
ROOT=Path('ROOT');sys.path.insert(0,str(ROOT));import supervise_matched_history_launch_review_once as q
q.verify();ready=q.q.w.read(ROOT/'reports/S1A_MATCHED_HISTORY_REVIEW_READY.json')
rows={}
for variant in ('A0','A1','A2'):
 row=ready[variant];run=Path(row['run']);rc=q.q.w.read(run/'latest_complete.json');mf=q.q.w.read(run/'run_manifest.json')
 assert rc['pid']==row['PID_bound_receipt']['pid'] and rc['checkpoint']==row['checkpoint']['path']
 if variant=='A0':info=q.q.base.checkpoint(Path(rc['checkpoint']));meta=None
 else:info,meta=q.fullsave(Path(rc['checkpoint']))
 assert info==row['checkpoint'];assert q.q.w.read(run/'rolling_source_freeze.json')['sha256']==q.q.w.read((q.N if variant=='A0' else ROOT)/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in mf['src_sha256'].items():assert q.q.base.sha(run/'src_snapshot'/n)==h
 health=q.q.w.read(run/'CLOCK_TRAINING_HEALTH.json');assert health['actual_task_reset_events']==0 and health['control_steps']==6600 and health['actual_physics_callbacks']==66000
 rows[variant]=dict(checkpoint=info,architecture=meta,health=health,manifest=mf,receipt=rc)
budget=q.q.base.budget_state();assert budget['active_segment'] is None and not q.q.w.read(q.q.ctl.STATE_PATH).get('active_training')
assert not q.q.base.trainers()
print(json.dumps(dict(epoch=time.time(),matched_ready=ready,verified=rows,budget=budget,stage_used_seconds=q.stage_used(),no_new_PPO=True)))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'MATCHED_ARCHITECTURE_COMPLETE_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],stage_used=v['stage_used_seconds'],remaining=v['budget']['remaining_training_seconds'],
  verified={k:dict(sha256=x['checkpoint']['sha256'],finite=x['checkpoint']['finite_tensors'],closure_mm=x['health']['max_closure_error_m']*1000,control_steps=x['health']['control_steps']) for k,x in v['verified'].items()})))
finally:c.close()
