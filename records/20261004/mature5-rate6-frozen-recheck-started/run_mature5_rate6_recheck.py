"""One isolated frozen6 recheck, only after existing mature5 pairs and idle hold.

Never writes production config, state, status, checkpoints, or budget. No PPO.
"""
import fcntl,hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE=ROOT/'isaac/mod4';REPORTS=D/'reports'
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
SOURCE_SHA='253ed8effd5fe8580859bce1b7731006ae62a5e7bf1c63a9f8825de2c74bc73e'
STATUS=REPORTS/'RUN_STATUS.json'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,value):
 temp=p.with_suffix('.partial');temp.write_text(json.dumps(value,indent=2));temp.replace(p)

def validate_admission(paired,state,source):
 assert paired['pass'] and paired['fixed_cap']==5. and paired['profiles']==['nominal','white_v2']
 assert paired['checkpoint']['sha256']==source['sha256']==SOURCE_SHA
 assert paired['checkpoint']['path']==source['path']==state['mature']['checkpoint']==state['chosen_checkpoint']
 assert state['mature']['cap']==5. and state['mature']['profile']==state['profile']=='white_v2'
 assert state['consecutive']>=2 and state['active_training'] is None and 6. in state['rate_rejected']
 assert len(paired['pairs'])==4
 assert {(v['seed'],v['kind']) for v in paired['pairs']}=={(s,k) for s in (20261002,20261003) for k in ('flat','spin')}
 assert all(v['initial_root_q_exact'] and v['original_plus_individual_safety_gates']==[True,True] and v['actual_parameter_readbacks']==[True,True] for v in paired['pairs'])

def active():
 found=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   args=(p/'cmdline').read_bytes().decode().split('\0');state=(p/'stat').read_text().split(') ',1)[1].split()[0]
   if state!='Z' and '-c' not in args and any(a.endswith(('/train_mod4_ppo.py','/fullscale_worst_diagnostic.py','/supervise_autonomy.py','/supervise_targeted_mature5.py','/spin_rate_probe.py','/validate_speed.py')) for a in args):found.append(int(p.name))
  except OSError:pass
 return found

def main():
 assert not STATUS.exists(),'One-shot diagnostic already started: inspect, never repeat'
 record=dict(stage='waiting_existing_mature5_pairs',PPO_performed=False,production_changed=False,budget_authority=False,begin_epoch=time.time())
 atomic(STATUS,record)
 # All waiting happens locally on the target; no repeated SSH/ping monitoring.
 deadline=time.time()+1800
 while True:
  candidates=list((ROOT/'reports').glob('auto_0037_*paired_decision.json'))
  assert len(candidates)<=1
  if candidates:
   paired=read(candidates[0])
   if not paired['pass']:
    atomic(STATUS,dict(record,stage='mature5_not_admitted',paired_receipt=str(candidates[0]),no_probe_started=True));return
   if read(ROOT/'status.json')['stage']=='targeted_repair_hold' and not active():break
  if time.time()>deadline:
   atomic(STATUS,dict(record,stage='waiting_window_expired',no_probe_started=True));return
  time.sleep(10)
 locks=[];child=None
 try:
  for p in (ROOT/'autonomy_controller.lock',LEDGER.parent/'native_floor_supervisor.lock'):
   stream=p.open('a+');fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(stream)
  budget_raw=LEDGER.read_bytes();budget=json.loads(budget_raw)
  assert budget['authorized_training_seconds']==252000 and not budget.get('active_segment') and budget['owner_root']==str(ROOT)
  assert not active()
  state=read(ROOT/'reports/AUTONOMY_STATE.json')
  sys.path.insert(0,str(CODE));import supervise_autonomy as ctl
  source=ctl.base.checkpoint(Path(state['chosen_checkpoint']));assert source['finite_tensors']==68
  validate_admission(paired,state,source);ctl.verify()
  prepared=read(REPORTS/'PREPARED.json')
  for name,digest in prepared['candidate_source_hashes'].items():assert sha(D/name)==digest,name
  assert read(D/'isaac/mod4/env.json')['RM_SPIN_MAX_RAD_S']=='6.0'
  inherited=[]
  for seed in (20261002,20261003):
   for kind in ('flat','spin'):
    reports=[read(ROOT/'reports'/f'auto_0037_mature_multiseed_cap5_white_v2_{kind}_{profile}_{seed}.json') for profile in ('nominal','white_v2')]
    assert all(r['checkpoint']==source['path'] and ctl.gate(r,kind) for r in reports)
    assert all(all(r[k]==reports[0][k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics')) for r in reports)
    if kind=='flat':
     inherited.extend(dict(path=str(ROOT/'reports'/f'auto_0037_mature_multiseed_cap5_white_v2_flat_{profile}_{seed}.json'),sha256=sha(ROOT/'reports'/f'auto_0037_mature_multiseed_cap5_white_v2_flat_{profile}_{seed}.json'),reused_existing_mature5_flat=True) for profile in ('nominal','white_v2'))
  record.update(stage='source_verified',source=source,paired_receipt=str(candidates[0]),reused_flat=inherited,old_rejections_retained=state['rate_rejected'],charged_before=budget['charged_training_seconds'])
  atomic(STATUS,record)
  env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
  env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
  outputs=[]
  jobs=[(20261002,'white_v2',300,22)]+[(seed,profile,1500,88) for seed in (20261002,20261003) for profile in ('nominal','white_v2')]
  for seed,profile,steps,count in jobs:
   assert not active() and LEDGER.read_bytes()==budget_raw
   name=f'model17039_rate6_{profile}_{seed}_{steps}steps';out=REPORTS/(name+'.json');assert not out.exists()
   args=[sys.executable,str(D/'isaac/mod4/spin_rate_probe.py'),'--headless','--checkpoint',source['path'],'--seed',str(seed),'--dr-profile',profile,'--num_envs',str(count),'--steps',str(steps),'--max-rate','6','--output',str(out)]
   with out.with_suffix('.log').open('x') as log:
    child=subprocess.Popen(args,cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    record.update(stage='frozen_rate6_recheck',child_pid=child.pid,active_output=str(out),completed_outputs=outputs)
    atomic(STATUS,record);rc=child.wait(timeout=360);child=None
   assert rc==0 and out.exists(),f'Isolated probe error: {name}, exit={rc}'
   r=read(out);assert r['checkpoint']==source['path'] and not r['ppo_performed'] and r['target_rate_rad_s']==6.
   assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
   outputs.append(str(out));assert LEDGER.read_bytes()==budget_raw
   if not r['physical_smoke_pass'] or not ctl.safety_veto(r):
    atomic(STATUS,dict(record,stage='physical_recheck_rejected',completed_outputs=outputs,frozen_ledger_exact=True));return
  rows=[]
  for seed in (20261002,20261003):
   reports=[read(REPORTS/f'model17039_rate6_{profile}_{seed}_1500steps.json') for profile in ('nominal','white_v2')]
   assert all(all(r[k]==reports[0][k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics')) for r in reports)
   initial_with5=[]
   for profile,r in zip(('nominal','white_v2'),reports):
    old=read(ROOT/'reports'/f'auto_0037_mature_multiseed_cap5_white_v2_spin_{profile}_{seed}.json')
    exact=all(r[k]==old[k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics'))
    assert exact;initial_with5.append(exact)
   rows.append(dict(seed=seed,profiles=['nominal','white_v2'],initial_root_q_exact=True,initial_with_existing_cap5_exact=initial_with5,original_rate_skill=[r['spin_skill_pass'] for r in reports],legacy_rate_skill=[r['spin_skill_pass_legacy_reference'] for r in reports],original_plus_individual_safety=[ctl.gate(r,'spin') for r in reports]))
  result=dict(record,stage='completed',rate6_frozen_all_pass=all(all(p['original_plus_individual_safety']) for p in rows),pairs=rows,completed_outputs=outputs,frozen_ledger_exact=LEDGER.read_bytes()==budget_raw,charged_after=read(LEDGER)['charged_training_seconds'],no_formal6_PPO_started=True,old_rejections_not_deleted=True,scope='Frozen transfer from current mature5; not a trained6 expert or permission to skip fullscale/PPO preflight and bounded trial')
  atomic(REPORTS/'MATURE5_RATE6_RECHECK.json',result);atomic(STATUS,result)
 except BaseException:
  atomic(STATUS,dict(record,stage='isolated_error_preserved',error=traceback.format_exc()));raise
 finally:
  if child is not None and child.poll() is None:
   child.terminate()
   try:child.wait(timeout=20)
   except subprocess.TimeoutExpired:child.kill();child.wait()
  for stream in locks:stream.close()

if __name__=='__main__':main()
