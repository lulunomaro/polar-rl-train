"""One isolated frozen evidence batch. No PPO, ledger or production writes."""
import fcntl, hashlib, json, os, subprocess, sys, time, traceback
from pathlib import Path
D=Path(__file__).resolve().parent;R=D/'reports'
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
L=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(x):
 p=R/'RUN_STATUS.partial';p.write_text(json.dumps(x,indent=2));p.replace(R/'RUN_STATUS.json')
def active():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   a=(p/'cmdline').read_bytes().decode().split('\0');st=(p/'stat').read_text().rsplit(')',1)[1].split()
   names=('/train_mod4_ppo.py','/spin_rate_probe.py','/contact_calibration_probe.py','/spin_substep_corrected_shadow_probe.py','/validate_speed.py','/spin_rate_fullscale_probe.py','/supervise_autonomy.py','/supervise_targeted_mature5.py','/supervise_rolling_repair.py')
   if st[0]!='Z' and '-c' not in a and any(v.endswith(names) for v in a):out.append(dict(pid=int(p.name),start_ticks=int(st[19]),argv=a))
  except OSError:pass
 return out
def main():
 assert not (R/'RUN_STATUS.json').exists(),'One-shot already ran; inspect existing output'
 x=dict(stage='verifying_idle_source',begin_epoch=time.time(),PPO=False,production_writes=False,budget_writes=False);write(x)
 locks=[];child=None
 try:
  for path in (P/'autonomy_controller.lock',L.parent/'native_floor_supervisor.lock'):
   f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  assert not active() and read(P/'status.json')['stage']=='targeted_repair_hold'
  assert read(L)['active_segment'] is None and read(P/'reports/AUTONOMY_STATE.json')['active_training'] is None
  assert read(C/'reports/REPAIR_STATE.json')['phase']=='repair_hold'
  ledger=L.read_bytes();prod_status=(P/'status.json').read_bytes();repair_state=(C/'reports/REPAIR_STATE.json').read_bytes()
  for name,h in read(R/'PREPARED.json')['source_hashes'].items():assert sha(D/name)==h,name
  sys.path.insert(0,str(P/'isaac/mod4'));import supervise_autonomy as ctl
  for source in read(D/'PREREGISTERED_PROTOCOL.json')['sources'].values():assert ctl.base.checkpoint(Path(source['path']))==source
  cases=[('latest6_control', 'latest6',6.,20261002,'white_v2',False)]
  cases += [(f'latest6_{seed}_{profile}','latest6',6.,seed,profile,True) for seed in (20261002,20261003) for profile in ('white_v2','nominal')]
  cases += [(f'mature5_{seed}_{profile}','mature5',5.,seed,profile,True) for seed in (20261002,20261003) for profile in ('white_v2','nominal')]
  cases += [('passed6_20261002_white_v2','passed6',6.,20261002,'white_v2',True)]
  completed={};sources=read(D/'PREREGISTERED_PROTOCOL.json')['sources']
  env={k:v for k,v in os.environ.items() if not k.startswith('RM_')};env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
  for name,source,cap,seed,profile,hook in cases:
   assert not active() and L.read_bytes()==ledger
   out=R/(name+'.json');assert not out.exists()
   args=[sys.executable,str(D/'isaac/mod4/contact_calibration_probe.py'),'--headless','--checkpoint',sources[source]['path'],'--steps','1500','--num_envs','88','--seed',str(seed),'--dr-profile',profile,'--max-rate',str(cap),'--output',str(out)]
   if hook:args.append('--contact-readback')
   with out.with_suffix('.log').open('x') as log:
    child=subprocess.Popen(args,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    proc=Path('/proc')/str(child.pid);st=(proc/'stat').read_text().rsplit(')',1)[1].split()
    x.update(stage='frozen_calibration',case=name,evaluation_pid=child.pid,evaluation_start_ticks=int(st[19]),active_output=str(out),completed=list(completed));write(x)
    rc=child.wait(timeout=1000);child=None
   assert rc==0 and out.exists(),f'{name}: isolated probe error exit{rc}'
   r=read(out);assert r['checkpoint']==sources[source]['path'] and not r['ppo_performed'] and r['seconds']==15.
   assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
   assert L.read_bytes()==ledger and (P/'status.json').read_bytes()==prod_status and (C/'reports/REPAIR_STATE.json').read_bytes()==repair_state
   completed[name]=r
   if name=='latest6_20261002_white_v2':
    control=completed['latest6_control'];original=read(P/'reports/auto_0057_assessment_cap6_white_v2_rate.json')
    for a in (control,original):
     assert all(r[k]==a[k] for k in ('per_environment','alive','first_failure_step','group_ids','reset_root_before_physics','reset_joint_pos_before_physics','initial_parameter_audit','final_parameter_audit')),'Read-only contact instrumentation changed behavior'
   if hook:
    sub=r['substep_contact_readback'];assert sub['callbacks']==30000 and sub['sampling_s']==.0005
    assert all(t==29000 for row in sub['per_environment']['valid_ticks'] for t in row),'Incomplete alive-prefix contact evidence'
   x.update(completed=list(completed),completed_output_sha={k:sha(R/(k+'.json')) for k in completed});write(x)
  for seed in (20261002,20261003):
   values=[completed[f'{source}_{seed}_{profile}'] for source in ('latest6','mature5') for profile in ('white_v2','nominal')]
   assert all(all(v[k]==values[0][k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics','group_ids')) for v in values),'Complete initial root/q pairing failed'
  x.update(stage='completed',end_epoch=time.time(),ledger_bytes_exact=L.read_bytes()==ledger,production_status_and_repair_state_exact=True,read_only_hook_behavior_exact=True,original_report_behavior_exact=True,root_q_pairs_exact=True,remaining_effective_s=read(L)['authorized_training_seconds']-read(L)['charged_training_seconds'],acceptance_deployed=False)
  (R/'CALIBRATION_COMPLETED.json').write_text(json.dumps(x,indent=2));write(x)
 except BaseException:
  x.update(stage='isolated_error_preserved',error=traceback.format_exc());write(x);raise
 finally:
  if child and child.poll() is None:
   child.terminate()
   try:child.wait(timeout=20)
   except subprocess.TimeoutExpired:child.kill();child.wait()
  for f in locks:f.close()
if __name__=='__main__':main()
