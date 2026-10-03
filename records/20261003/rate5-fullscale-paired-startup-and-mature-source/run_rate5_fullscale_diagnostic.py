"""Two frozen fullscale diagnostic attempts in a verified settled hold."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');REPORTS=D/'reports';REPORTS.mkdir(exist_ok=True)
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_text())
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def active():
 rows=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   args=(p/'cmdline').read_bytes().decode().split('\0');state=(p/'stat').read_text().split(') ',1)[1].split()[0]
   if state!='Z' and '-c' not in args and any(a.endswith(('/train_mod4_ppo.py','/spin_rate_fullscale_probe.py','/fullscale_worst_diagnostic.py','/spin_rate_probe.py','/validate_speed.py','/supervise_autonomy.py')) for a in args):rows.append(int(p.name))
  except OSError:pass
 return rows
assert not (REPORTS/'COMPARISON.json').exists() and not (REPORTS/'STATUS.json').exists()
budget=read(LEDGER);assert budget['authorized_training_seconds']==252000 and not budget.get('active_segment')
assert read(ROOT/'status.json')['stage']=='targeted_repair_hold' and not read(ROOT/'reports/AUTONOMY_STATE.json').get('active_training')
assert not active(),active()
source=ROOT/'logs/2026-10-03_20-47-43_auto_0024_autonomous_continued_cap4_white_v2/model_16450.pt'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0904737799adc6e3f71545fb03bfd70730abf04e3aae42ede38e56233d48c9bb'
env={k:v for k,v in os.environ.items() if not k.startswith('RM_')};env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
proof={'stage':'running','source':str(source),'charged_before':budget['charged_training_seconds'],'budget_total':252000,'PPO_performed':False,'runs':[],'begin_epoch':time.time()};atomic(REPORTS/'STATUS.json',proof)
for cap in [4.,5.]:
 assert not active() and read(LEDGER)==budget
 out=REPORTS/f'model16450_cap{cap:g}_20k.json';assert not out.exists()
 with out.with_suffix('.log').open('x') as stream:
  child=subprocess.Popen([sys.executable,str(D/'fullscale_worst_diagnostic.py'),'--headless','--checkpoint',str(source),'--max-rate',str(cap),'--num_envs','20000','--steps','120','--output',str(out)],cwd=D,stdout=stream,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  proof.update(child_pid=child.pid,active_cap=cap);atomic(REPORTS/'STATUS.json',proof)
  exit_code=child.wait(timeout=600)
 assert exit_code==0 and out.exists(),out
 r=read(out);proof['runs'].append({'cap':cap,'report':str(out),'max_tilt_deg':r['max_tilt_deg'],'worst':r['top_tilt_environments'][0]});atomic(REPORTS/'STATUS.json',proof)
a=read(REPORTS/'model16450_cap4_20k.json');b=read(REPORTS/'model16450_cap5_20k.json')
x=np.load(a['initial_state_arrays_path']);y=np.load(b['initial_state_arrays_path'])
assert all(np.array_equal(x[k],y[k]) for k in ['root','q'])
original=read(ROOT/'reports/auto_0029_rate_candidate_cap4_white_v2_20k.json')
fields=['nonfinite','terminations','max_closure_m','max_mimic_rad','max_tilt_deg','max_height_error_m','raw_contact_evidence','mild_initial_parameters','mild_final_parameters']
assert all(original[k]==b[k] for k in fields),'Instrumentation changed original cap5 physical output'
proof.update(stage='completed',initial_root_q_arrays_exact=True,original_cap5_output_exact=True,charged_after=read(LEDGER)['charged_training_seconds'],frozen_ledger_exact=(read(LEDGER)==budget),end_epoch=time.time(),child_pid=None)
assert proof['frozen_ledger_exact'];atomic(REPORTS/'COMPARISON.json',proof);atomic(REPORTS/'STATUS.json',proof)
print(json.dumps(proof))
