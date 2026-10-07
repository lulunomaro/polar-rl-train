"""Use the actual runtime-injected sensor profile; preserve failed staged entry."""
from pathlib import Path
import sys,json,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ast.parse((D/'supervise_validated_1ms_runtime_review.py').read_text())
c=connect()
try:
 with c.open_sftp() as sf:sf.put(str(D/'supervise_validated_1ms_runtime_review.py'),ROOT+'/supervise_validated_1ms_runtime_review.py')
 code=r'''
from pathlib import Path
import sys,json,hashlib,time,subprocess,shutil
D=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008');R=D/'reports';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'RUNTIME_READER_REVIEW.json').exists() and not (R/'RECOVERY_LAUNCHED.json').exists()
old=R/'SOURCE_FREEZE.json';backup=R/'SOURCE_FREEZE_FIRST_STAGED.json';assert not backup.exists();shutil.copy2(old,backup)
f=read(old);f['sha256']['supervise_validated_1ms_runtime_review.py']=sha(D/'supervise_validated_1ms_runtime_review.py');f['source_count']=len(f['sha256']);old.write_text(json.dumps(f,indent=2))
(R/'SECOND_PREFLIGHT_READER_ERROR.json').write_text(json.dumps(dict(error="KeyError: RM_SENSOR_PROFILE in cfg/env.json",stage='Prelaunch guard only, after23health+9resume CPU completed; no SDK/PPO/segment',actual_schema='sensor profile injected by runtime() from immutable wrapper; original env.json intentionally unchanged',production_failure=False),indent=2))
sys.path.insert(0,str(D));import supervise_validated_1ms_runtime_review as w;w.verify()
assert read(R/'HEALTH_1MS_CPU_PASSED.json')['count']==23 and read(R/'SOURCE24827_RESUME_CPU_PASSED.json')['count']==9
assert not w.s.trainers() and w.s.q.base.budget_state()['active_segment'] is None and not w.s.q.w.read(w.s.q.ctl.STATE_PATH).get('active_training')
before=w.s.q.ctl.CANONICAL.read_bytes()
(R/'RUNTIME_READER_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,source_count=len(f['sha256']),actual_runtime_sensor_profile=w.s.runtime()['RM_SENSOR_PROFILE'],prior_staged_controller_and_freeze_retained=True,no_runtime_physics_PPO_reward_reset_change=True,old_copied_entries_forbidden=True),indent=2))
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_validated_1ms_runtime_review.py')],cwd=w.s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),owner=w.s.identity(p.pid),source_count=len(f['sha256']),entry='supervise_validated_1ms_runtime_review.py',first_frozen_SDK_then_same_scope_learning=True,no_new_budget_seconds=0)
w.s.write('RECOVERY_LAUNCHED.json',row);assert before==w.s.q.ctl.CANONICAL.read_bytes();print(json.dumps(row))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'RECOVERY_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(raw.decode())
finally:c.close()
