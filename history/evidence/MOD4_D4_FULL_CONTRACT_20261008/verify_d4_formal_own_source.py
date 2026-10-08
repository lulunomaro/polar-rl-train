"""Own formal PID, actual startup/full save and immutable source verification."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,re
D=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d4_full_contract as w
w.verify();st=w.read(R/'D4_STATE.json');assert st['phase']=='bounded_E0_D4_feedback_delay_learning'
owner=w.identity(st['owner']['pid']);child=w.identity(st['child']['pid']);guardian=w.identity(w.read(R/'D4_GUARDIAN_STARTED.json')['pid'])
for actual,expected in [(owner,st['owner']),(child,st['child']),(guardian,w.read(R/'D4_GUARDIAN_STARTED.json'))]:assert actual and actual['start_ticks']==expected['start_ticks'] and actual['state']!='Z'
assert owner['ppid']==1 and str(D/'isaac/mod4/train_action_resume_ppo.py') in child['argv']
assert w.s.q.base.budget_state()['active_segment']['pid']==child['pid'] and w.read(w.s.q.ctl.STATE_PATH)['active_training']['pid']==child['pid']
run=w.s.q.w.rate.trainer_run(D/'learning_logs',child['pid']);m=w.read(run/'run_manifest.json');rec=w.read(run/'latest_complete.json')
assert rec['pid']==child['pid'] and rec['log_dir']==str(run)
assert m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256']==w.read(run/'rolling_source_freeze.json')['sha256']
for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
assert m['init_checkpoint_sha256']=='ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61'
assert m['env']['RM_KEEP_STD']=='1' and m['env']['RM_PHYSICS_ACTION_DELAY_PROFILE']=='physical_target_0_2500_5000us_v1'
assert m['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1'
startup=w.read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')
assert startup['source_sha256']==m['init_checkpoint_sha256'] and startup['explicitly_new_D4_queue'] and not startup['predecessor_had_action_queue']
assert startup['action_episode_incremented_once'] and startup['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
ck=w.fullsave(Path(rec['checkpoint']));text=Path(st['active_log']).read_text(errors='replace');updates=re.findall(r'Learning iteration\s+(\d+)',text)
assert updates and 'Traceback (most recent call last)' not in text
assert not (run/'STOP_AFTER_SAVE').exists() and not (R/'D4_ATTENTION.json').exists()
v=dict(epoch=time.time(),phase=st['phase'],owner=owner,guardian=guardian,trainer=child,run=str(run),active_log=st['active_log'],deadline_epoch=st['deadline_epoch'],own_receipt=rec,checkpoint=ck,source_count=len(m['source_map']),snapshots=len(m['src_sha256']),startup=startup,PPO_iteration_log_count=len(updates),last_logged_iteration=int(updates[-1]),periodic_checkpoint_after_source_iteration=rec['iteration']>m['start_iteration'],new_behavior_replay_pending=True,full_final_health_pending=not (run/'CLOCK_TRAINING_HEALTH.json').exists(),budget=w.s.q.base.budget_state())
w.write('D4_FORMAL_OWN_SOURCE_VERIFIED.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D4_FORMAL_OWN_SOURCE_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
