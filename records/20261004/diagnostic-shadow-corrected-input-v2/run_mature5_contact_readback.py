"""Read-only paired5/6 contact evidence from the current mature policy.

No PPO or production writes. The filtered diagnostics do not change admission.
"""
import fcntl,hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
PREVIOUS=Path('/home/egde/rl_candidates/MOD4_RATE6_RECHECK_FROM_MATURE5_20261004')
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(x):
 p=R/'RUN_STATUS.partial';p.write_text(json.dumps(x,indent=2));p.replace(R/'RUN_STATUS.json')
def active():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   a=(p/'cmdline').read_bytes().decode().split('\0');state=(p/'stat').read_text().split(') ',1)[1].split()[0]
   if state!='Z' and '-c' not in a and any(v.endswith(('/train_mod4_ppo.py','/spin_substep_probe.py','/spin_rate_probe.py','/spin_contact_probe.py','/validate_speed.py','/spin_rate_fullscale_probe.py','/supervise_autonomy.py','/supervise_targeted_mature5.py')) for v in a):out.append(int(p.name))
  except OSError:pass
 return out
def main():
 assert not (R/'RUN_STATUS.json').exists(),'One-shot already executed; inspect instead'
 x=dict(stage='verifying_idle_source',PPO_performed=False,production_changed=False,budget_changed=False,begin_epoch=time.time());write(x)
 locks=[];child=None
 try:
  for path in (ROOT/'autonomy_controller.lock',LEDGER.parent/'native_floor_supervisor.lock'):
   f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  assert not active() and read(ROOT/'status.json')['stage']=='targeted_repair_hold'
  budget=LEDGER.read_bytes();assert read(LEDGER)['active_segment'] is None and read(LEDGER)['authorized_training_seconds']==252000
  state=read(ROOT/'reports/AUTONOMY_STATE.json');old=read(PREVIOUS/'reports/MATURE5_RATE6_RECHECK.json')
  assert old['stage']=='completed' and not old['rate6_frozen_all_pass'] and old['frozen_ledger_exact']
  assert state['mature']==dict(checkpoint=old['source']['path'],cap=5.0,profile='white_v2') and state['chosen_checkpoint']==old['source']['path'] and state['active_training'] is None
  assert 6. in state['rate_rejected']
  sys.path.insert(0,str(ROOT/'isaac/mod4'));import supervise_autonomy as ctl
  ctl.verify();source=ctl.base.checkpoint(Path(state['chosen_checkpoint']))
  assert source['sha256']==old['source']['sha256']=='253ed8effd5fe8580859bce1b7731006ae62a5e7bf1c63a9f8825de2c74bc73e' and source['finite_tensors']==68
  for name,h in read(R/'PREPARED.json')['source_hashes'].items():assert sha(D/name)==h,name
  x.update(source=source,charged_before=read(LEDGER)['charged_training_seconds']);write(x)
  env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
  env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
  results={}
  for name,cap,hook in (('control6',6.,False),('substep6',6.,True),('substep5',5.,True)):
   assert not active() and LEDGER.read_bytes()==budget
   out=R/(name+'.json');assert not out.exists()
   args=[sys.executable,str(D/'isaac/mod4/spin_substep_probe.py'),'--headless','--checkpoint',source['path'],'--steps','300','--num_envs','88','--seed','20261002','--dr-profile','white_v2','--max-rate',str(cap),'--output',str(out)]
   if hook:args.append('--substep-readback')
   with out.with_suffix('.log').open('x') as log:
    child=subprocess.Popen(args,cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    x.update(stage='frozen_contact_readback',mode=name,evaluation_pid=child.pid,active_output=str(out),completed_modes=list(results));write(x)
    rc=child.wait(timeout=420);child=None
   assert rc==0 and out.exists(),f'{name}: isolated program error, exit{rc}'
   result=read(out);assert not result['ppo_performed'] and result['checkpoint']==source['path']
   assert result['physical_smoke_pass'] and ctl.safety_veto(result)
   assert all(result['alive']) and result['initial_parameter_audit']['actual_parameters_pass'] and result['final_parameter_audit']['actual_parameters_pass']
   assert LEDGER.read_bytes()==budget
   results[name]=result
  a,b,c=(results[k] for k in ('control6','substep6','substep5'))
  assert all(all(v[k]==a[k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics','initial_parameter_audit','group_ids')) for v in (b,c))
  assert a['per_environment']==b['per_environment'],'Read-only hook changed control behavior'
  for v in (b,c):
   sub=v['substep_contact_readback'];assert sub['callbacks']==6000 and sub['sampling_s']==.0005 and not sub['gate_changed'] and not sub['reward_changed']
   assert all(t==5000 for row in sub['per_environment']['valid_ticks'] for t in row)
  ids=[i for i,g in enumerate(a['group_ids']) if g<7]
  assert all(all(a['per_environment'][k][i]==c['per_environment'][k][i] for i in ids) for k in a['per_environment']),'Unchanged-command groups must remain exact'
  x.update(stage='completed',completed_modes=list(results),same_complete_source=True,initial_root_q_parameters_exact=True,read_only_hook_behavior_exact=True,non_highrate_groups_exact=True,ledger_bytes_exact=LEDGER.read_bytes()==budget,charged_after=read(LEDGER)['charged_training_seconds'],output_sha256={k:sha(R/(k+'.json')) for k in results},scope='Three-second paired contact/load/rolling diagnosis, not15-second skill admission or real-hardware certification; no targeted reward or training deployed')
  (R/'PAIRED_CONTACT_READBACK.json').write_text(json.dumps(x,indent=2));write(x)
 except BaseException:
  x.update(stage='isolated_error_preserved',error=traceback.format_exc());write(x);raise
 finally:
  if child and child.poll() is None:
   child.terminate()
   try:child.wait(timeout=20)
   except subprocess.TimeoutExpired:child.kill();child.wait()
  for f in locks:f.close()
if __name__=='__main__':main()
