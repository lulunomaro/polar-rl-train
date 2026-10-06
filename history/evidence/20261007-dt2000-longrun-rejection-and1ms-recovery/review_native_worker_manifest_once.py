"""Repair a missing frozen-worker path in a new root; reuse completed aligned SDK exactly."""
from pathlib import Path
import sys,shlex,json,ast,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
OLD='/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_LONGRUN_RECOVERY_20261007'
ROOT='/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007'
assert not (R/'CLOCK1000_WORKER_REVIEW_LAUNCHED.json').exists()
s=(D/'supervise_dt1000_longrun_recovery.py').read_text(encoding='utf8')
anchor=" before_frozen=ctl.CANONICAL.read_bytes()"
addition=anchor+"""
 previous=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_LONGRUN_RECOVERY_20261007')
 for n,h in w.read(previous/'reports/SOURCE_FREEZE.json')['sha256'].items():assert base.sha(D/n)==h,n
 prior_error=w.read(previous/'reports/SELECTED_CLOCK_ATTENTION.json')
 assert 'native20k.json' in prior_error['error'] and not prior_error['active_segment']
 assert not helpers.identity(w.read(previous/'reports/SELECTED_CLOCK_LAUNCHED.json')['owner']['pid'])
 sdk=w.read(previous/'reports/ALIGNED_SDK_PASSED.json')
 assert sdk['physical_task_passed'] and sdk['clock']==clock and sdk['source_sha256']==SHA and base.sha(Path(sdk['output']))==sdk['sha256']
 assert sdk['SDK_oracle']['selected_reset_events']>=1
 write('ALIGNED_SDK_PASSED.json',sdk)
 write('SDK_REUSED_AFTER_WORKER_MANIFEST_REVIEW.json',dict(epoch=time.time(),previous_error=prior_error,
  native_worker_failed_before_Kit_launch=True,SDK_exact_reused=sdk,prior187_byte_exact=True,new_actual_GPU_probes_not_repeated=True,canonical_bytes_exact=True))
 for required in ('contact_aligned_sdk.py','native1000_probe.py','isaac/mod4/train_mod4_ppo.py'):
  assert (D/required).is_file(),('Missing declared worker before launch',required)
"""
assert anchor in s;s=s.replace(anchor,addition,1)
old="[('aligned_sdk','contact_aligned_sdk.py',10,300),('native20k','physics_speed_probe.py',20000,120)]"
assert old in s;s=s.replace(old,"[('native20k','native1000_probe.py',20000,120)]",1)
ast.parse(s);(D/'continue_clock1000_worker_manifest_review_once.py').write_text(s,encoding='utf8')
native=(W/'MOD4_PHYSICS_SPEED_REVIEW_20261007/physics_speed2000_probe.py').read_text(encoding='utf8')
assert 'assert args.dt==.002' in native;native=native.replace('assert args.dt==.002','assert args.dt==.001',1)
ast.parse(native);(D/'native1000_probe.py').write_text(native,encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sftp:
  try:sftp.stat(ROOT);raise AssertionError('Named worker review already exists')
  except FileNotFoundError:pass
  sftp.mkdir(ROOT);sftp.mkdir(ROOT+'/reports');sftp.mkdir(ROOT+'/new_changes')
  for n in ('continue_clock1000_worker_manifest_review_once.py','native1000_probe.py'):
   sftp.put(str(D/n),ROOT+'/new_changes/'+n)
 code=r'''
from pathlib import Path
import json,sys,hashlib,shutil,time,subprocess,ast
OLD=Path('OLD');D=Path('ROOT');R=D/'reports';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==187
for n,h in f['sha256'].items():
 assert sha(OLD/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
changes=['continue_clock1000_worker_manifest_review_once.py','native1000_probe.py']
for n in changes:shutil.copy2(D/'new_changes'/n,D/n);ast.parse((D/n).read_text())
for n in ('DT2000_LONGRUN_FAILURE_AUDIT.json','DT2000_BASELINE_SUSPENDED.json'):shutil.copy2(OLD/'reports'/n,R/n)
sources={n:sha(D/n) for n in set(f['sha256'])|set(changes)};assert len(sources)==189
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=sources,prior187_byte_exact=True,explicit_changes=changes,
 scope='Missing native-worker path reviewed before native/optimizer start; actual aligned SDK explicitly reused; no runtime change'),indent=2))
sys.path.insert(0,str(D));import continue_clock1000_worker_manifest_review_once as q;q.verify()
before=q.ctl.CANONICAL.read_bytes();assert q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
attention=q.w.read(OLD/'reports/SELECTED_CLOCK_ATTENTION.json');assert attention['active_segment'] is None
assert q.helpers.identity(q.w.read(OLD/'reports/SELECTED_CLOCK_LAUNCHED.json')['owner']['pid']) is None
log=(OLD/'native20k.log').read_text();assert "can't open file" in log and 'No such file or directory' in log
sdk=q.w.read(OLD/'reports/ALIGNED_SDK_PASSED.json');assert sdk['physical_task_passed'] and q.base.sha(Path(sdk['output']))==sdk['sha256']
q.write('WORKER_MANIFEST_REVIEW.json',dict(epoch=time.time(),old_manifest_source_count=187,error=attention,missing_native_worker_before_Kit=True,
 original187_byte_exact=True,new_workers=[dict(path=n,sha256=sha(D/n)) for n in changes],all_declared_workers_exist=True,
 actual_SDK_reused=sdk,canonical_bytes_exact=True,no_PPO_or_old_tail_transactions=True))
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'continue_clock1000_worker_manifest_review_once.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=189,previous187_exact=True,completed_SDK_reused=True,new_budget_seconds=0)
q.write('SELECTED_CLOCK_LAUNCHED.json',v);assert q.ctl.CANONICAL.read_bytes()==before;print(json.dumps(v))
'''.replace("Path('OLD')","Path("+repr(OLD)+")").replace("Path('ROOT')","Path("+repr(ROOT)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'WORKER_MANIFEST_REVIEW_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 v=json.loads(raw);(R/'CLOCK1000_WORKER_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
 with c.open_sftp() as sftp:
  for n in ('SOURCE_FREEZE.json','WORKER_MANIFEST_REVIEW.json','SELECTED_CLOCK_LAUNCHED.json'):
   sftp.get(ROOT+'/reports/'+n,str(R/('WORKER_'+n)))
finally:c.close()
