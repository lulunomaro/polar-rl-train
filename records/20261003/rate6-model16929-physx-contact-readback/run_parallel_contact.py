"""One unique small frozen replay beside the single PPO; yield to planned evaluation."""
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_contact_repair_20261003')
PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
REPORT=ROOT/'reports/PARALLEL_CONTACT_RETRY1.json'
PATTERNS=('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/autonomy_turn_probe.py','/spin_slip_probe.py','/spin_contact_probe.py')
def atomic(x):
 p=REPORT.with_suffix('.partial');p.write_text(json.dumps(x,indent=2));p.replace(REPORT)
def probes(exclude=None):
 found=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==exclude:continue
  try:a=(p/'cmdline').read_bytes().decode().split('\0')
  except OSError:continue
  if '-c' not in a and any(any(k.endswith(t) for t in PATTERNS) for k in a):found.append(int(p.name))
 return found
assert not REPORT.exists(),'Do not repeat unique retry'
assert json.loads((ROOT/'reports/CONTACT_DIAGNOSTIC_SOURCE.json').read_text())['PPO_performed']==False
assert not probes(),'Existing evaluation must have priority'
checkpoint=PROD/'logs/2026-10-03_07-57-17_auto_0003_autonomous_continued_cap6_white_v1/model_16929.pt'
assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()=='e4973a3a300ad81660b62b46e2bdeeea3e788d04c8266f11ada81871982cecac'
out=ROOT/'reports/model16929_physx_contacts15s_retry1.json';assert not out.exists()
env=os.environ.copy();env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
with out.with_suffix('.log').open('x') as log:
 child=subprocess.Popen([sys.executable,str(ROOT/'isaac/mod4/spin_contact_probe.py'),'--headless','--checkpoint',str(checkpoint),'--steps','1500','--num_envs','88','--seed','20261002','--dr-profile','white_v1','--max-rate','6','--output',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
 receipt=dict(stage='isolated_contact_replay',worker_pid=os.getpid(),evaluation_pid=child.pid,output=str(out),PPO_performed=False,production_paused=False,ledger_written=False,begin_epoch=time.time());atomic(receipt)
 try:
  while child.poll() is None:
   competing=probes(child.pid)
   if competing or time.time()-receipt['begin_epoch']>660:
    receipt.update(stage='yielded_to_planned_evaluation' if competing else 'isolated_timeout',competing=competing)
    child.send_signal(signal.SIGINT)
    try:child.wait(timeout=25)
    except subprocess.TimeoutExpired:child.kill();child.wait()
    atomic(receipt);sys.exit(0)
   time.sleep(2)
  assert child.returncode==0 and out.exists(),'Contact program fault'
  receipt.update(stage='completed',report_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),exit_code=child.returncode,end_epoch=time.time());atomic(receipt)
 except BaseException as e:
  receipt.update(stage='isolated_program_error',error=repr(e),exit_code=child.poll(),end_epoch=time.time());atomic(receipt)
  if child.poll() is None:child.kill();child.wait()
  raise
