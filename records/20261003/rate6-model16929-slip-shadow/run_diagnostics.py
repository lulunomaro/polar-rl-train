"""Isolated frozen shadow runs. Yield to production evaluation; never PPO."""
import ast,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent
SOURCE=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_slip_diagnostic_20261003')
PATTERNS=('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/spin_fullscale_probe.py','/spin_rate_fullscale_probe.py','/autonomy_turn_probe.py','/turn_probe.py','/sensor_readback.py','/spin_slip_probe.py')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,v):
 t=p.with_suffix('.partial');t.write_text(json.dumps(v,indent=2));t.replace(p)
def probes(exclude=None):
 found=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==exclude:continue
  try:args=(p/'cmdline').read_bytes().decode().split('\0')
  except OSError:continue
  if '-c' in args:continue
  if any(any(a.endswith(x) for x in PATTERNS) for a in args):found.append(int(p.name))
 return found
def status(stage,**kw):atomic(ROOT/'reports/diagnostic_status.json',dict(stage=stage,worker_pid=os.getpid(),updated_epoch=time.time(),ppo_performed=False,ledger_modified=False,production_modified=False,**kw))

assert not ROOT.exists(),'Already prepared or started; inspect status instead of rerunning'
import shutil
freeze=json.loads((SOURCE/'reports/SPIN_SOURCE_FREEZE.json').read_text())['sha256']
for name,expected in freeze.items():
 p=Path(name) if Path(name).is_absolute() else SOURCE/name
 assert sha(p)==expected,'Source fingerprint mismatch '+name
ROOT.mkdir();shutil.copytree(SOURCE/'isaac',ROOT/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(SOURCE/'train/deploy',ROOT/'train/deploy')
(ROOT/'reports').mkdir();code=ROOT/'isaac/mod4'
baseline={name:sha(code/name) for name in ['mod4_task.py','mod4_env.py','scut_flat_rescue.py','spin_commands.py','mild_dr.py','contact_geometry.py','actuator_clip_diagnostics.py']}
for name in ['slip_shadow.py','spin_slip_probe.py']:shutil.copyfile(FILES/name,code/name);ast.parse((code/name).read_text())
cfg=json.loads((code/'env.json').read_text());assert cfg['RM_SPIN_MAX_RAD_S']=='4.0' and cfg['RM_MILD_DR_PROFILE']=='white_v2'
cfg.update(RM_SPIN_MAX_RAD_S='6.0',RM_MILD_DR_PROFILE='white_v1')
(code/'env.json').write_text(json.dumps(cfg,indent=2))
receipt=dict(candidate_only=True,no_PPO=True,no_budget_authority=True,source_root=str(SOURCE),baseline_source_hash=baseline,current_production_config_unchanged=True,diagnostic_source_hash={name:sha(code/name) for name in ['slip_shadow.py','spin_slip_probe.py']},isolated_command_cap=6.,isolated_profile='white_v1',original_gates_retained=True)
atomic(ROOT/'reports/DIAGNOSTIC_SOURCE_FREEZE.json',receipt)
(ROOT/'CANDIDATE_ONLY.md').write_text('Frozen shadow diagnostics only. No budget, no supervisor authority, no PPO. Do not run copied training or supervisor entrypoints.\n')
requests=json.loads((FILES/'REQUESTS.json').read_text())
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
for job in requests:
 checkpoint=Path(job['checkpoint']);assert sha(checkpoint)==job['sha256']
 output=ROOT/'reports'/f"model{job['model']}_seed20261002_shadow15s.json"
 if probes():status('waiting_existing_evaluation',existing_probes=probes(),next_output=str(output));sys.exit(0)
 assert not output.exists()
 with output.with_suffix('.log').open('x') as log:
  child=subprocess.Popen([sys.executable,str(code/'spin_slip_probe.py'),'--headless','--checkpoint',str(checkpoint),'--steps','1500','--num_envs','88','--seed','20261002','--dr-profile','white_v1','--max-rate','6','--output',str(output)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  status('frozen_shadow_evaluation',evaluation_pid=child.pid,model=job['model'],output=str(output))
  began=time.time()
  while child.poll() is None:
   competing=probes(child.pid)
   if competing or time.time()-began>1200:
    child.send_signal(signal.SIGINT)
    try:child.wait(timeout=35)
    except subprocess.TimeoutExpired:child.kill();child.wait()
    status('yielded_to_existing_evaluation' if competing else 'diagnostic_timeout',output=str(output),existing_probes=competing);sys.exit(0)
   time.sleep(2)
  if child.returncode!=0 or not output.exists():status('diagnostic_program_error',model=job['model'],output=str(output),exit_code=child.returncode);sys.exit(1)
 result=json.loads(output.read_text());assert not result['ppo_performed']
 status('frozen_shadow_completed',model=job['model'],output=str(output),old_gate_skill_pass=result['spin_skill_pass'],shadow_reference_error_max=max(max(v) for v in result['slip_shadow']['per_environment_max']['velocity_reference_error']))
status('completed',outputs=[str(ROOT/'reports'/f"model{j['model']}_seed20261002_shadow15s.json") for j in requests])
