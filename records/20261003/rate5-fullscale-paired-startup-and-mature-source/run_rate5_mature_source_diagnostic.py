"""Check the preselected last paired mature source, never search checkpoints."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');REPORTS=D/'reports'
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_text())
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def active():
 found=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   args=(p/'cmdline').read_bytes().decode().split('\0');s=(p/'stat').read_text().split(') ',1)[1].split()[0]
   if s!='Z' and '-c' not in args and any(a.endswith(('/train_mod4_ppo.py','/fullscale_worst_diagnostic.py','/supervise_autonomy.py','/spin_rate_probe.py','/validate_speed.py')) for a in args):found.append(int(p.name))
  except OSError:pass
 return found
record=REPORTS/'MATURE_SOURCE_DIAGNOSTIC.json';assert not record.exists()
budget=read(LEDGER);assert budget['authorized_training_seconds']==252000 and not budget.get('active_segment')
atomic(record,{'stage':'waiting_existing_comparison','charged_before':budget['charged_training_seconds'],'PPO_performed':False})
begin=time.time()
while not (REPORTS/'COMPARISON.json').exists():
 assert time.time()-begin<600 and read(LEDGER)==budget
 time.sleep(5)
comparison=read(REPORTS/'COMPARISON.json');assert comparison['stage']=='completed' and comparison['initial_root_q_arrays_exact'] and comparison['original_cap5_output_exact']
assert not active() and read(ROOT/'status.json')['stage']=='targeted_repair_hold'
state=read(ROOT/'reports/AUTONOMY_STATE.json');mature=state['mature']
source=Path(mature['checkpoint']);assert mature['cap']==4. and mature['profile']=='white_v2'
assert source.name=='model_16425.pt' and hashlib.sha256(source.read_bytes()).hexdigest()=='63662952ea6be6ca6c259a0563fe2495cefc0ebadf9eb729c69ec1e92aba9075'
paired=[read(p) for p in (ROOT/'reports').glob('auto_0023_*paired_decision.json')]
assert len(paired)==1 and paired[0]['pass'] and paired[0]['checkpoint']['path']==str(source)
sys.path.insert(0,str(ROOT/'isaac/mod4'));import supervise_native_floor as base
info=base.checkpoint(source);assert info['finite_tensors']==68
out=REPORTS/'model16425_cap5_20k.json';assert not out.exists()
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')};env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
with out.with_suffix('.log').open('x') as stream:
 child=subprocess.Popen([sys.executable,str(D/'fullscale_worst_diagnostic.py'),'--headless','--checkpoint',str(source),'--max-rate','5','--num_envs','20000','--steps','120','--output',str(out)],cwd=D,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=env)
 atomic(record,dict(stage='running_preselected_mature_source',source=info,paired_receipt=paired[0],child_pid=child.pid,charged_before=budget['charged_training_seconds'],no_checkpoint_search=True))
 exit_code=child.wait(timeout=600)
assert exit_code==0 and out.exists()
r=read(out);raw=r['raw_contact_evidence']
passed=(r['num_envs']==20000 and r['seconds']>=1.2 and r['plane_type']=='Plane' and r['ground_z_m']==0 and r['friction_static']==.9 and r['friction_dynamic']==.9 and not r['nonfinite'] and r['terminations']==0 and r['max_closure_m']<.002 and r['max_mimic_rad']<.01 and r['max_tilt_deg']<15 and raw['loaded_ground_contacts']>0 and raw['loaded_downward_ground_contacts']==0 and raw['minimum_loaded_ground_normal_z']>.9 and raw['max_abs_ground_separation_m']<.01)
import numpy as np
a=np.load(r['initial_state_arrays_path']);b=np.load(read(REPORTS/'model16450_cap5_20k.json')['initial_state_arrays_path'])
assert all(np.array_equal(a[k],b[k]) for k in ['root','q']) and read(LEDGER)==budget
result=dict(stage='completed',source=info,preselected_last_paired_mature=True,no_checkpoint_search=True,physical_smoke_pass=passed,original_combined_pass=r['pass'],max_tilt_deg=r['max_tilt_deg'],worst=r['top_tilt_environments'][0],initial_root_q_with_newer_source_exact=True,actual_material_parameters_pass=r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass'],PPO_performed=False,frozen_ledger_exact=True,charged_before=budget['charged_training_seconds'],charged_after=read(LEDGER)['charged_training_seconds'],report=str(out))
atomic(record,result);print(json.dumps(result))
