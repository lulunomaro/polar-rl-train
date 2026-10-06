"""Stage a fresh fallback authority only after the actual failed owner settled and exited."""
from pathlib import Path
import sys,shlex,json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
ROOT='/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_LONGRUN_RECOVERY_20261007'
assert not (R/'CLOCK1000_FALLBACK_LAUNCHED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
audit=read(R/'DT2000_LONGRUN_FAILURE_AUDIT.json')
assert audit['actual_old_authorities_exited'] and audit['active_segment'] is None
assert not audit['formal_health']['adoption_retained'] and audit['full_save']['finite_tensors']==68
event=dict(id='MOD4-DT2000-LONGRUN-REJECTION-001',epoch=time.time(),status='DT2000_BASELINE_SUSPENDED_AFTER_ACTUAL_CLOSURE_FAILURE',
 original_baseline_id='MOD4-DT2000-BASELINE-LOCK-001',original_baseline_sha256='9c3f1e0427592f5d72089b4ccd685fc4a64505dd43562442a5fe9adb1ee737d5',
 audit=audit,approved_plan_version='1.5',approved_fallback_physics_dt_s=.001,fallback_root=ROOT,
 fallback_not_adopted_before_checks=True,failed_checkpoint_not_selected=True,original23509_initialization=True,
 no_old_tail_recharged=True,new_budget_seconds=0,actor_encoder_training_pending=True,
 reason='Human2ms lock was conditional on health. Actual long-run closure termination invalidated that condition. Existing approved v1.5 permits isolated1ms fallback; no threshold or nominal model change.')
(R/'DT2000_BASELINE_SUSPENDED.json').write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
E=W/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'
contract=W/'polar-rl-train/history/plans/MOD4_MOE_EXECUTION_CONTRACT.json';cc=read(contract)
cc['actual_clock_failure']=event
cc['execution_state']=dict(stage='S0P/S1A',status='DT2000_LONGRUN_REJECTED_ISOLATED1MS_VALIDATION',runtime_root=ROOT,actual_failure_source=audit['full_save'])
contract.write_text(json.dumps(cc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks=read(E/'EXECUTION_TRACKS.json')
tracks['physics_performance']=dict(status=event['status'],actual_failure_audit=audit,fallback_root=ROOT,physics_dt_s=.001,decimation=10,policy_period_s=.01,contact_bin_s=.005,new_candidate_not_adopted=True)
tracks['learning'].update(status='Actual2ms stopped after physical failure; isolated1ms full validation pending',root=ROOT,actual_phase='fallback_validation_pending',active_training=None)
(E/'EXECUTION_TRACKS.json').write_text(json.dumps(tracks,indent=2),encoding='utf8')
approval=read(E/'PLAN_APPROVAL.json');approval.setdefault('execution_events',{})[event['id']]=dict(status=event['status'],source='Actual task failure under already-approved fallback contract',event_file='DT2000_BASELINE_SUSPENDED.json',new_human_approval_inferred=False)
(E/'PLAN_APPROVAL.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2),encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(ROOT);raise AssertionError('Named fallback candidate already exists; audit actual state instead of repeat.')
  except FileNotFoundError:pass
  s.mkdir(ROOT);s.mkdir(ROOT+'/reports');s.mkdir(ROOT+'/new_changes')
  names=['supervise_dt1000_longrun_recovery.py','contact_aligned_sdk.py','aligned_contact_oracle.py']
  for n in names:s.put(str(D/n),ROOT+'/new_changes/'+n)
  for n in ['DT2000_LONGRUN_FAILURE_AUDIT.json','DT2000_BASELINE_SUSPENDED.json']:s.put(str(R/n),ROOT+'/reports/'+n)
  er='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  for p in [R/'DT2000_BASELINE_SUSPENDED.json',R/'DT2000_LONGRUN_FAILURE_AUDIT.json',contract,E/'EXECUTION_TRACKS.json',E/'PLAN_APPROVAL.json']:
   s.put(str(p),er+p.name+'.actual_failure');s.posix_rename(er+p.name+'.actual_failure',er+p.name)
  s.put(str(R/'DT2000_BASELINE_SUSPENDED.json'),'/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007/reports/DT2000_BASELINE_SUSPENDED.json')
 code=r'''
from pathlib import Path
import json,sys,hashlib,shutil,time,subprocess,ast
OLD=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007');D=Path('ROOT');R=D/'reports';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==184
for n,h in f['sha256'].items():
 assert sha(OLD/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
changes=['supervise_dt1000_longrun_recovery.py','contact_aligned_sdk.py','aligned_contact_oracle.py']
for n in changes:shutil.copy2(D/'new_changes'/n,D/n);ast.parse((D/n).read_text())
cfg=json.loads((D/'isaac/mod4/env.json').read_text());assert cfg['RM_PHYSICS_DT_S']=='0.002';cfg['RM_PHYSICS_DT_S']='0.001'
(D/'isaac/mod4/env.json').write_text(json.dumps(cfg,indent=2))
sources={n:sha(D/n) for n in set(f['sha256'])|set(changes)}
assert len(sources)==187
assert all(sources[n]==h for n,h in f['sha256'].items() if n!='isaac/mod4/env.json')
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=sources,base_root=str(OLD),original184_preserved_except_env_clock=True,
 explicit_changes=changes+['isaac/mod4/env.json'],scope='New1ms fallback after actual2ms long-run closure failure; original source/model/task/reward/PPO/DR/limits retained'),indent=2))
test=subprocess.run([sys.executable,str(D/'test_clock2000_cpu.py')],cwd=D,capture_output=True,text=True)
(R/'CLOCK_CPU_REUSED.txt').write_text(test.stdout+test.stderr);assert test.returncode==0,(test.stdout,test.stderr)
sys.path.insert(0,str(D));import supervise_dt1000_longrun_recovery as q
q.verify();audit=q.w.read(R/'DT2000_LONGRUN_FAILURE_AUDIT.json')
assert q.base.sha(q.ctl.CANONICAL)==audit['canonical_sha256'],'Unexpected ledger change at frozen boundary: inspect before launch'
assert q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
assert q.base.checkpoint(Path(audit['full_save']['path']))==audit['full_save']
source=q.base.checkpoint(q.SOURCE);assert source['finite_tensors']==68 and source['sha256']==q.SHA
q.write('FALLBACK_CPU_SOURCE_CONTRACT.json',dict(epoch=time.time(),source_count=187,base184_exact_except_explicit_dt=True,clock_CPU_passed=True,
 source_original23509=source,failed23875_preserved=True,nominal_robot_task_DR_reward_PPO_hardware_unchanged=True,canonical_write_operations=0))
before=q.ctl.CANONICAL.read_bytes()
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'supervise_dt1000_longrun_recovery.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
q.write('SELECTED_CLOCK_LAUNCHED.json',dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=187,
 sole_new_authority=True,old_entries_not_resumed=True,new_budget_seconds=0,native_PPO_then_bounded_A0_if_pass=True))
assert q.ctl.CANONICAL.read_bytes()==before
print(json.dumps(q.w.read(R/'SELECTED_CLOCK_LAUNCHED.json')))
'''.replace('ROOT',ROOT)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'CLOCK1000_STAGING_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 v=json.loads(raw);(R/'CLOCK1000_FALLBACK_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
 with c.open_sftp() as s:
  for n in ['SOURCE_FREEZE.json','FALLBACK_CPU_SOURCE_CONTRACT.json','CLOCK_CPU_REUSED.txt']:
   s.get(ROOT+'/reports/'+n,str(R/n))
finally:c.close()
