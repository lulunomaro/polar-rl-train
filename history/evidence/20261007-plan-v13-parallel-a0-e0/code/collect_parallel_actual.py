"""Read actual same-PID learning and publish composite metadata; no launch or ledger write."""
from pathlib import Path
import hashlib,json,shlex,sys,tomllib
W=Path(__file__).resolve().parents[1];A=Path(__file__).resolve().parent;R=A/'reports'
E=W/'MOD4_MOE_PLAN_EXECUTION_20261007';ER=E/'reports';plans=W/'polar-rl-train/history/plans'
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''
from pathlib import Path
import json,re,subprocess,sys,time
D=Path('/home/egde/rl_candidates/MOD4_MOE_A0_E0_PARALLEL_20261007');sys.path.insert(0,str(D))
import supervise_plan_a0 as q
q.verify();b=q.base.budget_state();active=b.get('active_segment');assert active and active['pid']==670475
trainer=q.helpers.identity(670475);observer=q.helpers.identity(671176);guardian=q.helpers.identity(671219)
assert trainer and trainer['start_ticks']==46556747 and trainer['state']!='Z'
assert observer and observer['state']!='Z' and guardian and guardian['state']!='Z'
log=Path(active['log']).read_text(errors='replace');names=re.findall(r'log_dir=(\S+)',log)
run=Path(names[-1]) if names else None
manifest=q.w.read(run/'run_manifest.json') if run and (run/'run_manifest.json').exists() else None
if manifest:
 assert manifest['init_checkpoint_sha256']==q.SOURCE_SHA
latest=q.w.read(run/'latest_complete.json') if run and (run/'latest_complete.json').exists() else None
saved=None
if latest:
 assert latest['pid']==670475
 saved=q.base.checkpoint(Path(latest['checkpoint']))
freeze=q.w.read(run/'rolling_source_freeze.json') if run and (run/'rolling_source_freeze.json').exists() else None
if freeze:assert freeze['sha256']==q.w.read(q.w.F)['sha256']
g=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True)
progress=q.w.read(q.ER/'S0E_CALIBRATION_PROGRESS.json')
now=time.time();remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,now-active['accounted_through_epoch'])
d=dict(epoch=now,trainer=trainer,observer=observer,guardian=guardian,active=active,remaining=remaining,
 run=str(run) if run else None,manifest=manifest,latest=latest,checkpoint_CPU=saved,run_freeze_exact=bool(freeze),
 PPO_iterations=re.findall(r'Learning iteration\s+(\d+)/(\d+)',log)[-3:],GPU=g.stdout.strip(),
 observed_Traceback='Traceback (most recent call last)' in log,observed_OOM='CUDA out of memory' in log,
 log_tail=log[-4200:],eval_progress={k:progress[k] for k in ['epoch','complete_jobs','expected_jobs','attention']},
 budget_write_operations=0,new_PPO_or_signals=0)
assert not d['observed_Traceback'] and not d['observed_OOM']
q.base.atomic_json(D/'reports/A0_TRAINING_ACTUAL.json',d)
state=q.w.read(q.ER/'EXECUTION_STATE.json')
if 'learning_track_current' not in state:q.base.atomic_json(q.ER/'EXECUTION_STATE_S0E_INITIAL_RETAINED.json',state)
state.update(version='1.3',plan_sha256=q.w.read(q.ER/'PLAN_APPROVAL.json')['approved_plan_sha256'],stage='S1A',phase='bounded_A0_E0_learning',epoch=now,
 new_learning_started=True,learning_track_current=dict(root=str(D),state=str(D/'reports/A0_STATE.json'),trainer_pid=670475,start_ticks=46556747),
 parallel_tracks_path=str(q.ER/'EXECUTION_TRACKS.json'),S0E_parallel_calibration=True,S0E_completed_jobs=progress['complete_jobs'],
 learning_remaining_seconds=remaining,cached_S0E_reader_phase_is_not_global_learning_status=True,
 next_required_evidence='A0 own complete save and matched A1/A2;3060 functional calibration formal use separately')
q.base.atomic_json(q.ER/'EXECUTION_STATE.json',state)
for name in ['MOE_PLAN_EXECUTION_CURRENT.json','MOE_PLAN_REVIEW_REQUIRED.json']:
 path=q.P/'reports'/name;old=q.w.read(path) if path.exists() else {}
 if not (q.ER/(name+'.v12.retained')).exists():q.base.atomic_json(q.ER/(name+'.v12.retained'),old)
 old.update(plan_version='1.3',version='1.3',approved=True,approved_plan_sha256=state['plan_sha256'],plan_sha256=state['plan_sha256'],
  learning_root=str(D),parallel_tracks_path=str(q.ER/'EXECUTION_TRACKS.json'),review_required=False,
  execution_state_reference=str(q.ER/'EXECUTION_STATE.json'),actual_phase_requires_track_readback=True)
 q.base.atomic_json(path,old)
print(json.dumps({k:d[k] for k in ['epoch','PPO_iterations','GPU','run','latest','checkpoint_CPU','run_freeze_exact','remaining','eval_progress','observed_Traceback','observed_OOM']}))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
 out=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err
 with c.open_sftp() as s:
  for name in ['A0_TRAINING_ACTUAL.json','A0_STATE.json','A0_ACTIVE_OBSERVER_STARTED.json']:
   s.get('/home/egde/rl_candidates/'+A.name+'/reports/'+name,str(R/name))
  for name in ['EXECUTION_STATE.json','EXECUTION_STATE_S0E_INITIAL_RETAINED.json','S0E_CALIBRATION_PROGRESS.json']:
   s.get('/home/egde/rl_candidates/'+E.name+'/reports/'+name,str(ER/name))
 print(out)
finally:c.close()
auto=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
args=json.loads((E/'AUTOMATION_UPDATE_ARGS_V13.json').read_text(encoding='utf8'))
assert auto['prompt'].rstrip('\n')==args['prompt'].rstrip('\n') and auto['status']=='ACTIVE' and auto['rrule']=='FREQ=HOURLY;INTERVAL=2'
proof=dict(id=auto['id'],name=auto['name'],status=auto['status'],rrule=auto['rrule'],updated_at=auto['updated_at'],
 prompt_sha256=hashlib.sha256(auto['prompt'].encode()).hexdigest(),prompt=auto['prompt'],purpose_tool_update_verified=True,
 quiet_when_unchanged=True,parallel_learning_and_evaluation=True)
(ER/'AUTOMATION_V13_VERIFIED.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
