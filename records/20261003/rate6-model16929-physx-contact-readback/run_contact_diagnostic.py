"""One authorized, bounded no-PPO diagnostic. Never run copied training code."""
import ast,hashlib,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_contact_repair_20261003')
PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
PARENT=2490960;TICKS='17250655'
REPORT=ROOT/'reports/BOUNDED_CONTACT_DIAGNOSTIC.json'
PATTERNS=('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/autonomy_turn_probe.py','/spin_slip_probe.py','/spin_contact_probe.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(pid):
 try:
  p=Path('/proc')/str(pid);st=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=st[19],state=st[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def owner():
 x=identity(PARENT)
 return bool(x and x['start_ticks']==TICKS and x['cwd']==str(PROD) and any(a.endswith('/supervise_autonomy.py') for a in x['argv']))
def probes(exclude=None):
 found=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==exclude:continue
  x=identity(int(p.name))
  if x and '-c' not in x['argv'] and any(any(a.endswith(k) for k in PATTERNS) for a in x['argv']):found.append(int(p.name))
 return found
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def resume():
 if owner():os.kill(PARENT,signal.SIGCONT)
if '--watchdog' in sys.argv:
 worker=int(sys.argv[-1]);began=time.time()
 while identity(worker) and identity(worker)['state']!='Z' and time.time()-began<660:time.sleep(2)
 if REPORT.exists():
  r=json.loads(REPORT.read_text());pid=r.get('evaluation_pid');x=identity(pid) if pid else None
  if x and x['cwd']==str(ROOT) and str(r.get('output','')) in x['argv']:
   os.kill(pid,signal.SIGINT)
   for _ in range(15):
    if not identity(pid) or identity(pid)['state']=='Z':break
    time.sleep(1)
   if identity(pid) and identity(pid)['state']!='Z':os.kill(pid,signal.SIGKILL)
 resume();sys.exit()
assert not ROOT.exists(),'A unique run already exists. Inspect, never repeat.'
freeze=json.loads((PROD/'reports/SPIN_SOURCE_FREEZE.json').read_text())['sha256']
for name,expected in freeze.items():assert sha(Path(name) if Path(name).is_absolute() else PROD/name)==expected,name
ROOT.mkdir();shutil.copytree(PROD/'isaac',ROOT/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(PROD/'train/deploy',ROOT/'train/deploy');(ROOT/'reports').mkdir();code=ROOT/'isaac/mod4'
for name in ['spin_contact_probe.py','physx_contact_readback.py','slip_shadow.py','test_contact_readback.py']:
 shutil.copyfile(FILES/name,code/name);ast.parse((code/name).read_text())
cfg=json.loads((code/'env.json').read_text());assert cfg['RM_MILD_DR_PROFILE']=='white_v2' and float(cfg['RM_SPIN_MAX_RAD_S'])==4.
cfg.update(RM_SPIN_MAX_RAD_S='6.0',RM_MILD_DR_PROFILE='white_v1');(code/'env.json').write_text(json.dumps(cfg,indent=2))
cpu=subprocess.run([sys.executable,str(code/'test_contact_readback.py')],cwd=ROOT,capture_output=True,text=True)
assert cpu.returncode==0,cpu.stderr
atomic(ROOT/'reports/CONTACT_DIAGNOSTIC_SOURCE.json',dict(source_production=str(PROD),candidate_only=True,PPO_performed=False,ledger_authority=False,source_hashes={n:sha(code/n) for n in ['spin_contact_probe.py','physx_contact_readback.py','slip_shadow.py','mod4_task.py','mod4_env.py','contact_geometry.py','contact_capture.py']},cpu_validation=cpu.stdout,original_gates_unchanged=True,only_sensor_reporting_filter_and_capacity_differ=True))
assert owner() and identity(PARENT)['state']!='T'
status=json.loads((PROD/'status.json').read_text());state=json.loads((PROD/'reports/AUTONOMY_STATE.json').read_text());ledger=json.loads(LEDGER.read_text())
assert status['stage'].startswith('frozen_') and not status.get('training_pid') and not state.get('active_training') and not ledger.get('active_segment'),'No settled freeze window; do not stop PPO'
assert ledger['authorized_training_seconds']==252000
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 x=identity(int(p.name))
 assert not(x and x['cwd']==str(PROD) and any(a.endswith('/train_mod4_ppo.py') for a in x['argv'])),'Live owned trainer'
began=time.time();child=None;receipt=dict(stage='holding_natural_freeze',begin_epoch=began,owner_identity=identity(PARENT),canonical_charged_before=ledger['charged_training_seconds'],PPO_interrupted=False,ledger_written=False)
os.kill(PARENT,signal.SIGSTOP)
watch=subprocess.Popen([sys.executable,__file__,'--watchdog',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
receipt['watchdog_pid']=watch.pid;atomic(REPORT,receipt)
try:
 while probes():
  assert time.time()-began<240,'Existing evaluation did not finish within safe window'
  assert owner() and identity(PARENT)['state']=='T'
  time.sleep(2)
 checkpoint=PROD/'logs/2026-10-03_07-57-17_auto_0003_autonomous_continued_cap6_white_v1/model_16929.pt'
 assert sha(checkpoint)=='e4973a3a300ad81660b62b46e2bdeeea3e788d04c8266f11ada81871982cecac'
 out=ROOT/'reports/model16929_physx_contacts15s.json';assert not out.exists()
 env=os.environ.copy();env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
 with out.with_suffix('.log').open('x') as log:
  child=subprocess.Popen([sys.executable,str(code/'spin_contact_probe.py'),'--headless','--checkpoint',str(checkpoint),'--steps','1500','--num_envs','88','--seed','20261002','--dr-profile','white_v1','--max-rate','6','--output',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
  receipt.update(stage='individual_contact_replay',evaluation_pid=child.pid,output=str(out));atomic(REPORT,receipt)
  while child.poll() is None:
   assert time.time()-began<620,'Bounded no-PPO window reached'
   assert owner() and identity(PARENT)['state']=='T' and not probes(child.pid),'Owner resumed or competing evaluation'
   assert not json.loads(LEDGER.read_text()).get('active_segment'),'PPO resumed; abort diagnostic'
   time.sleep(2)
 assert child.returncode==0 and out.exists(),'Isolated contact diagnostic fault'
 result=json.loads(out.read_text());assert not result['ppo_performed']
 receipt.update(stage='completed',report_sha256=sha(out),old_gate=result['spin_skill_pass'],contact_report_version=result['physx_contact_readback']['version'])
except BaseException as e:
 receipt.update(stage='isolated_diagnostic_error',error=repr(e))
 if child and child.poll() is None:
  child.send_signal(signal.SIGINT)
  try:child.wait(timeout=20)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 raise
finally:
 resume();after=json.loads(LEDGER.read_text());receipt.update(end_epoch=time.time(),owner_after=identity(PARENT),charged_after=after['charged_training_seconds'],authorized_seconds_after=after['authorized_training_seconds'],charged_unchanged=after['charged_training_seconds']==receipt['canonical_charged_before']);atomic(REPORT,receipt)
