"""Read actual formal identity, own fullsave/source and live startup contracts."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,re
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_path_review as w
w.verify();st=w.read(R/'D5_STATE.json');assert st['phase']=='bounded_E0_D5_spring_stiffness_learning'
owner=w.identity(st['owner']['pid']);child=w.identity(st['child']['pid']);g=w.read(R/'D5_GUARDIAN_STARTED.json');guardian=w.identity(g['pid'])
for actual,expected in [(owner,st['owner']),(child,st['child']),(guardian,g)]:assert actual and actual['start_ticks']==expected['start_ticks'] and actual['state']!='Z'
assert owner['ppid']==1 and str(D/'isaac/mod4/train_spring_resume_ppo.py') in child['argv']
b=w.s.q.base.budget_state();assert b['active_segment']['pid']==child['pid'] and w.read(w.s.q.ctl.STATE_PATH)['active_training']['pid']==child['pid']
run=w.s.q.w.rate.trainer_run(D/'learning_logs',child['pid']);m=w.read(run/'run_manifest.json');rec=w.read(run/'latest_complete.json')
assert rec['pid']==child['pid'] and rec['log_dir']==str(run)
assert m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256']==w.read(run/'rolling_source_freeze.json')['sha256']
for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
assert m['init_checkpoint_sha256']==st['source']['sha256']
assert m['env']['RM_KEEP_STD']=='1' and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
assert m['spring_pressure_recipe']['profile']=='gas_stiffness_independent_episode_090_110_v1'
spring=w.read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json');action=w.read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')
assert spring['pid']==child['pid'] and spring['source_sha256']==m['init_checkpoint_sha256']
assert spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once'] and spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']
assert action['source_sha256']==m['init_checkpoint_sha256'] and action['predecessor_had_action_queue'] and action['action_queue_targets_timestamps_both_RNG_restored_exact'] and not action['explicitly_new_D4_queue']
assert action['action_episode_incremented_once'] and action['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not action['PhysX_exact_resume_claimed']
if not spring['predecessor_had_spring_pressure_state']:assert spring['explicitly_new_D5_pressure']
else:assert spring['spring_factor_episode_two_CUDA_RNG_restored_exact'] and not spring['explicitly_new_D5_pressure']
ck=w.fullsave(Path(rec['checkpoint']));log=Path(st['active_log']).read_text(errors='replace');updates=re.findall(r'Learning iteration\s+(\d+)',log)
assert updates and 'Traceback (most recent call last)' not in log
assert not (run/'STOP_AFTER_SAVE').exists() and not (R/'D5_ATTENTION.json').exists()
health=w.read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None
tail=max(0,time.time()-b['active_segment']['accounted_through_epoch'])
v=dict(epoch=time.time(),phase=st['phase'],owner=owner,guardian=guardian,trainer=child,run=str(run),active_log=st['active_log'],deadline_epoch=st['deadline_epoch'],
 own_receipt=rec,checkpoint=ck,source=st['source'],source_count=len(m['source_map']),snapshots=len(m['src_sha256']),spring_startup=spring,action_startup=action,
 PPO_iteration_log_count=len(updates),last_logged_iteration=int(updates[-1]),live_health=health,live_health_is_not_final=True,new_behavior_replay_pending=True,
 budget=b,actual_tail_adjusted_remaining_seconds=b['remaining_training_seconds']-tail,read_only_no_GPU_or_canonical_write=True)
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D5_FORMAL_OWN_SOURCE_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v[k] for k in ('epoch','phase','trainer','run','checkpoint','source_count','snapshots','PPO_iteration_log_count','live_health','actual_tail_adjusted_remaining_seconds')}))
finally:c.close()
