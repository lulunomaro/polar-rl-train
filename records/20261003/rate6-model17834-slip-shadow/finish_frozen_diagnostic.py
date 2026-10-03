"""One bounded freeze-window continuation. Never stop a running trainer."""
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_slip_diagnostic_20261003')
PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
PARENT=2490960;TICKS='17250655'
REPORT=ROOT/'reports/FROZEN_WINDOW_CONTINUATION.json'
PATTERNS=('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/autonomy_turn_probe.py','/spin_slip_probe.py')
def identity(pid):
 try:
  p=Path('/proc')/str(pid);st=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=st[19],state=st[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def owner():
 x=identity(PARENT)
 return bool(x and x['start_ticks']==TICKS and x['cwd']==str(PROD) and any(a.endswith('/supervise_autonomy.py') for a in x['argv']))
def probes(exclude=None):
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==exclude:continue
  try:args=(p/'cmdline').read_bytes().decode().split('\0')
  except OSError:continue
  if '-c' not in args and any(any(a.endswith(k) for k in PATTERNS) for a in args):out.append(int(p.name))
 return out
def write(v):
 p=REPORT.with_suffix('.partial');p.write_text(json.dumps(v,indent=2));p.replace(REPORT)
def resume():
 if owner():os.kill(PARENT,signal.SIGCONT)
if '--watchdog' in sys.argv:
 worker=int(sys.argv[-1]);start=time.time()
 while identity(worker) and identity(worker)['state']!='Z' and time.time()-start<540:time.sleep(2)
 resume();sys.exit()
assert not REPORT.exists(),'Do not repeat a completed freeze transaction'
assert owner() and identity(PARENT)['state']!='T'
status=json.loads((PROD/'status.json').read_text());state=json.loads((PROD/'reports/AUTONOMY_STATE.json').read_text());ledger=json.loads(LEDGER.read_text())
assert status['stage'].startswith('frozen_') and not status.get('training_pid')
assert not state.get('active_training') and not ledger.get('active_segment'),'Must be a settled no-PPO window'
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=(p/'cmdline').read_bytes().decode().split('\0')
 except OSError:continue
 assert not (any(a.endswith('/train_mod4_ppo.py') for a in args) and str(PROD) in str((p/'cwd').resolve())),'Live owned trainer'
started=time.time();child=None
receipt=dict(stage='holding_settled_freeze',owner_identity=identity(PARENT),canonical_before=ledger,charged_before=ledger['charged_training_seconds'],PPO_interrupted=False,ledger_written=False,physics_or_gates_changed=False,begin_epoch=started)
os.kill(PARENT,signal.SIGSTOP)
watch=subprocess.Popen([sys.executable,__file__,'--watchdog',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
receipt['watchdog_pid']=watch.pid;write(receipt)
try:
 while probes():
  assert time.time()-started<180,'Existing evaluations did not finish promptly'
  assert owner() and identity(PARENT)['state']=='T'
  time.sleep(2)
 job=json.loads((Path(__file__).parent/'REQUESTS.json').read_text())[1]
 assert hashlib.sha256(Path(job['checkpoint']).read_bytes()).hexdigest()==job['sha256']
 out=ROOT/'reports/model17834_seed20261002_shadow15s_retry1.json';assert not out.exists()
 env=os.environ.copy();env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
 with out.with_suffix('.log').open('x') as log:
  child=subprocess.Popen([sys.executable,str(ROOT/'isaac/mod4/spin_slip_probe.py'),'--headless','--checkpoint',job['checkpoint'],'--steps','1500','--num_envs','88','--seed','20261002','--dr-profile','white_v1','--max-rate','6','--output',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
  receipt.update(stage='frozen_retry_evaluation',evaluation_pid=child.pid,output=str(out));write(receipt)
  while child.poll() is None:
   assert time.time()-started<500,'Bounded freeze deadline reached'
   assert owner() and identity(PARENT)['state']=='T','Parent resumed; yield diagnostic'
   assert not probes(child.pid),'Another evaluator appeared; yield'
   assert not json.loads(LEDGER.read_text()).get('active_segment'),'PPO resumed; yield'
   time.sleep(2)
 assert child.returncode==0 and out.exists(),'Diagnostic program fault'
 r=json.loads(out.read_text());assert not r['ppo_performed']
 receipt.update(stage='completed',old_gate_skill_pass=r['spin_skill_pass'],report_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
except BaseException as e:
 receipt.update(stage='diagnostic_error',error=repr(e))
 if child and child.poll() is None:
  child.send_signal(signal.SIGINT)
  try:child.wait(timeout=20)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 raise
finally:
 resume();receipt['parent_resumed_identity']=identity(PARENT)
 after=json.loads(LEDGER.read_text());receipt.update(end_epoch=time.time(),charged_after=after['charged_training_seconds'],authorized_seconds_after=after['authorized_training_seconds'],charged_unchanged_in_frozen_window=after['charged_training_seconds']==receipt['charged_before'])
 write(receipt)
