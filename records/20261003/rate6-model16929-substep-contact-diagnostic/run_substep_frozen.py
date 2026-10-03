"""One bounded, guarded diagnostic in a settled production save window."""
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_substep_diagnostic_20261003')
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
REPORT=ROOT/'reports/SUBSTEP_FROZEN_READBACK.json';PARENT=2490960;TICKS='17250655'
PATTERNS=('spin_rate_probe.py','validate_speed.py','spin_substep_probe.py','spin_contact_probe.py','autonomy_turn_probe.py','spin_probe.py','spin_rate_fullscale_probe.py')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(x):
 p=REPORT.with_suffix('.partial');p.write_text(json.dumps(x,indent=2));p.replace(REPORT)
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def owner():
 p=identity(PARENT)
 return p and p['start_ticks']==TICKS and p['cwd']==str(PROD) and any(a.endswith('/supervise_autonomy.py') for a in p['argv'])
def trainers():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  x=identity(int(p.name))
  if x and x['state']!='Z' and x['cwd']==str(PROD) and any(a.endswith('/train_mod4_ppo.py') for a in x['argv']):out.append(x)
 return out
def probes(except_pid=None):
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==except_pid:continue
  x=identity(int(p.name))
  if x and '-c' not in x['argv'] and x['state']!='Z' and any(Path(a).name in PATTERNS for a in x['argv']):out.append(x)
 return out
def resume():
 if owner():os.kill(PARENT,signal.SIGCONT)
if '--watchdog' in sys.argv:
 worker=int(sys.argv[-1]);started=time.time()
 while identity(worker) and identity(worker)['state']!='Z' and time.time()-started<1100:time.sleep(2)
 r=read(REPORT);pid=r.get('evaluation_pid');x=identity(pid) if pid else None
 if x and x['cwd']==str(ROOT) and r.get('output') in x['argv']:
  os.kill(pid,signal.SIGINT)
  for _ in range(20):
   if not identity(pid) or identity(pid)['state']=='Z':break
   time.sleep(1)
  if identity(pid) and identity(pid)['state']!='Z':os.kill(pid,signal.SIGKILL)
 resume();sys.exit()
assert not REPORT.exists(),'Unique diagnostic already started; inspect instead'
prepared=read(ROOT/'reports/SUBSTEP_DIAGNOSTIC_PREPARED.json');assert prepared['stage']=='prepared_cpu_passed'
for n,h in prepared['source_hashes'].items():assert sha(ROOT/'isaac/mod4'/n)==h
assert owner() and identity(PARENT)['state']!='T'
receipt=dict(stage='preparing_frozen_substep_readback',worker_pid=os.getpid(),PPO_performed=False,ledger_written=False,production_sources_changed=False,begin_epoch=time.time(),owner_before=identity(PARENT))
atomic(receipt)
live=trainers();assert len(live)<=1
if live:
 x=live[0];matches=[]
 for p in (PROD/'logs').glob('*/latest_complete.json'):
  if read(p).get('pid')==x['pid']:matches.append(p.parent)
 assert len(matches)==1,'Cannot bind live trainer save directory'
 run=matches[0];manifest=read(run/'run_manifest.json')
 assert float(manifest['env']['RM_SPIN_MAX_RAD_S'])==4. and manifest['env']['RM_MILD_DR_PROFILE']=='white_v2'
 assert not (run/'STOP_AFTER_SAVE').exists(),'Existing save request must be inspected'
 (run/'STOP_AFTER_SAVE').write_text('Authorized targeted spin diagnosis; preserve complete checkpoint.\n')
 receipt.update(stage='waiting_complete_save',stop_requested=True,trainer=x,run=str(run));atomic(receipt)
 while trainers() or read(LEDGER).get('active_segment') or read(PROD/'reports/AUTONOMY_STATE.json').get('active_training'):
  assert owner() and time.time()-receipt['begin_epoch']<600,'Save not settled within one save interval'
  time.sleep(2)
 receipt['saved_checkpoint_receipt']=read(run/'latest_complete.json')
assert not trainers() and not read(LEDGER).get('active_segment') and not read(PROD/'reports/AUTONOMY_STATE.json').get('active_training')
assert read(PROD/'status.json')['stage'].startswith('frozen_')
assert read(LEDGER)['authorized_training_seconds']==252000
watch=subprocess.Popen([sys.executable,__file__,'--watchdog',str(os.getpid())],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
held=time.time();child=None
receipt.update(watchdog_pid=watch.pid,guard_installed_before_signal=True,freeze_epoch=held,charged_at_freeze=read(LEDGER)['charged_training_seconds']);atomic(receipt)
try:
 os.kill(PARENT,signal.SIGSTOP)
 for _ in range(100):
  if identity(PARENT)['state']=='T':break
  time.sleep(.01)
 assert owner() and identity(PARENT)['state']=='T' and not trainers() and not read(LEDGER).get('active_segment')
 while probes():
  assert time.time()-held<240 and owner() and identity(PARENT)['state']=='T','Existing scheduled evaluation must finish'
  time.sleep(2)
 checkpoint=PROD/'logs/2026-10-03_07-57-17_auto_0003_autonomous_continued_cap6_white_v1/model_16929.pt'
 assert sha(checkpoint)=='e4973a3a300ad81660b62b46e2bdeeea3e788d04c8266f11ada81871982cecac'
 env=os.environ.copy();env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
 results=[]
 for mode in ['control','substep']:
  out=ROOT/'reports'/f'model16929_{mode}3s.json';assert not out.exists()
  args=[sys.executable,str(ROOT/'isaac/mod4/spin_substep_probe.py'),'--headless','--checkpoint',str(checkpoint),'--steps','300','--num_envs','88','--seed','20261002','--dr-profile','white_v1','--max-rate','6','--output',str(out)]
  if mode=='substep':args+=['--substep-readback']
  with out.with_suffix('.log').open('x') as log:
   child=subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   receipt.update(stage='frozen_substep_diagnostic',mode=mode,evaluation_pid=child.pid,output=str(out));atomic(receipt)
   while child.poll() is None:
    assert time.time()-held<1000 and owner() and identity(PARENT)['state']=='T' and not probes(child.pid) and not trainers() and not read(LEDGER).get('active_segment'),'Diagnostic ownership/timeout guard'
    time.sleep(2)
  assert child.returncode==0 and out.exists(),'Isolated diagnostic program error'
  result=read(out);assert not result['ppo_performed'];results.append(result)
 baseline,current=results
 assert baseline['reset_root_before_physics']==current['reset_root_before_physics'] and baseline['reset_joint_pos_before_physics']==current['reset_joint_pos_before_physics']
 differences=[k for k,v in baseline['per_environment'].items() if current['per_environment'].get(k)!=v]
 assert not differences,'Read-only diagnostic changed frozen behavior: '+str(differences)
 sub=current['substep_contact_readback'];assert sub['callbacks']==6000 and all(x==5000 for row in sub['per_environment']['valid_ticks'] for x in row)
 receipt.update(stage='completed',initial_root_q_exact=True,all_original_per_environment_arrays_exact=True,callbacks=sub['callbacks'],sampling_s=sub['sampling_s'],baseline_sha256=sha(ROOT/'reports/model16929_control3s.json'),substep_sha256=sha(ROOT/'reports/model16929_substep3s.json'),rate6_graduated=False,rate6_rejection_retained=True)
except BaseException as e:
 receipt.update(stage='isolated_program_error_or_diagnostic_rejected',error=repr(e))
 if child and child.poll() is None:
  child.send_signal(signal.SIGINT)
  try:child.wait(timeout=20)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 raise
finally:
 resume();after=read(LEDGER)
 receipt.update(end_epoch=time.time(),owner_after=identity(PARENT),charged_after=after['charged_training_seconds'],frozen_charged_unchanged=after['charged_training_seconds']==receipt['charged_at_freeze'],authorized_seconds_after=after['authorized_training_seconds']);atomic(receipt)
