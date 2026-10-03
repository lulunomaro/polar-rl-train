"""One save-boundary evaluation-only fix, with independent bounded resume guard."""
import ast,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent
PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CANDIDATE=Path('/home/egde/rl_candidates/MOD4_contact_reference_fix_candidate_20261003')
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
PARENT=2490960;TICKS='17250655';TRAINER=2688768;TRAIN_TICKS='18219579'
REPORT=PROD/'reports/CONTACT_REFERENCE_FIX_FROZEN_V2_20261003.json'
NAMES=['contact_geometry.py','spin_rate_probe.py','validate_speed.py']
PATTERNS=('/validate_speed.py','/spin_probe.py','/spin_rate_probe.py','/autonomy_turn_probe.py','/spin_slip_probe.py','/spin_contact_probe.py')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def owned_parent():
 p=identity(PARENT)
 return p and p['start_ticks']==TICKS and p['cwd']==str(PROD) and any(a.endswith('/supervise_autonomy.py') for a in p['argv'])
def probes(exclude=None):
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==exclude:continue
  x=identity(int(p.name))
  if x and '-c' not in x['argv'] and any(any(a.endswith(k) for k in PATTERNS) for a in x['argv']):out.append(int(p.name))
 return out
def trainers():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  x=identity(int(p.name))
  if x and x['cwd']==str(PROD) and any(a.endswith('/train_mod4_ppo.py') for a in x['argv']) and x['state']!='Z':out.append(x)
 return out
def resume():
 if owned_parent():os.kill(PARENT,signal.SIGCONT)
if '--watchdog' in sys.argv:
 worker=int(sys.argv[-1]);began=time.time()
 while identity(worker) and identity(worker)['state']!='Z' and time.time()-began<1100:time.sleep(2)
 if REPORT.exists():
  r=read(REPORT);pid=r.get('own_evaluation_pid');p=identity(pid) if pid else None
  if p and p['cwd']==str(CANDIDATE) and str(r.get('own_output','')) in p['argv']:
   os.kill(pid,signal.SIGINT)
   for _ in range(20):
    if not identity(pid) or identity(pid)['state']=='Z':break
    time.sleep(1)
   if identity(pid) and identity(pid)['state']!='Z':os.kill(pid,signal.SIGKILL)
 resume();sys.exit()
assert not REPORT.exists(),'Do not repeat frozen v2 transaction'
assert owned_parent() and identity(PARENT)['state']!='T'
assert not trainers() and not read(LEDGER).get('active_segment') and not read(PROD/'reports/AUTONOMY_STATE.json').get('active_training'),'Must be a settled no-PPO window'
assert read(PROD/'status.json')['stage'].startswith('frozen_')
old=read(PROD/'reports/CONTACT_REFERENCE_FIX_SAVED_WINDOW_20261003.json');run=Path(old['run'])
assert read(run/'latest_complete.json')['pid']==TRAINER
receipt=dict(old,stage='preparing_guarded_frozen_validation',worker_pid=os.getpid(),save_request_reused=True,new_stop_request_written=False,continuation_epoch=time.time(),charged_at_freeze=read(LEDGER)['charged_training_seconds'])
atomic(REPORT,receipt)
watch=subprocess.Popen([sys.executable,__file__,'--watchdog',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
held=time.time();child=None
receipt.update(watchdog_pid=watch.pid,freeze_epoch=held,guard_installed_before_signal=True);atomic(REPORT,receipt)
try:
 os.kill(PARENT,signal.SIGSTOP)
 for _ in range(100):
  if identity(PARENT)['state']=='T':break
  time.sleep(.01)
 assert identity(PARENT)['state']=='T' and not trainers() and not read(LEDGER).get('active_segment'),'Settled freeze ownership changed'
 receipt.update(stage='settled_saved_freeze',original_supervisor_settled=True);atomic(REPORT,receipt)
 complete=read(run/'latest_complete.json');assert complete['pid']==TRAINER
 checkpoint_saved=Path(complete['checkpoint']);assert checkpoint_saved.parent==run
 import torch
 payload=torch.load(checkpoint_saved,map_location='cpu',weights_only=False)
 assert all(k in payload for k in ['actor_state_dict','critic_state_dict','optimizer_state_dict','iter'])
 def tensors(x):
  if isinstance(x,torch.Tensor):return [x]
  if isinstance(x,dict):return sum((tensors(v) for v in x.values()),[])
  if isinstance(x,(list,tuple)):return sum((tensors(v) for v in x),[])
  return []
 floats=[t for t in tensors(payload) if t.is_floating_point()];assert len(floats)==68 and all(torch.isfinite(t).all() for t in floats)
 receipt['complete_saved_checkpoint']=dict(path=str(checkpoint_saved),sha256=sha(checkpoint_saved),iteration_stored=payload['iter'],finite_float_tensors=len(floats),actor_critic_optimizer_std_iter_preserved=True)
 atomic(REPORT,receipt)
 while probes():
  assert time.time()-held<250 and owned_parent() and identity(PARENT)['state']=='T','Existing scheduled evaluation timeout'
  time.sleep(2)
 manifest=read(FILES/'REFERENCE_REPAIR_PREPARED.json');checkpoint=PROD/'logs/2026-10-03_16-57-58_auto_0018_autonomous_continued_cap4_white_v2/model_16317.pt'
 sys.path.insert(0,str(CANDIDATE/'isaac/mod4'));from admission_gate import assess
 comparisons={};env=os.environ.copy();env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
 for kind,n in [('spin',88),('flat',80)]:
  out=CANDIDATE/'reports'/f'model16317_reference_fixed_{kind}_frozen_v2.json';assert not out.exists()
  args=[sys.executable,str(CANDIDATE/'isaac/mod4'/('spin_rate_probe.py' if kind=='spin' else 'validate_speed.py')),'--headless','--checkpoint',str(checkpoint),'--seed','20261002','--dr-profile','white_v2','--num_envs',str(n),'--steps','1500','--output',str(out)]
  args+=['--max-rate','4'] if kind=='spin' else ['--speed_limit','1.5','--ramp_suite']
  with out.with_suffix('.log').open('x') as log:
   child=subprocess.Popen(args,cwd=CANDIDATE,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   receipt.update(stage='frozen_reference_regression',own_evaluation_pid=child.pid,own_output=str(out),kind=kind);atomic(REPORT,receipt)
   while child.poll() is None:
    assert time.time()-held<1000 and owned_parent() and identity(PARENT)['state']=='T' and not trainers() and not probes(child.pid) and not read(LEDGER).get('active_segment'),'Bounded frozen ownership lost'
    time.sleep(2)
  assert child.returncode==0 and out.exists(),'Frozen reference regression fault'
  current=read(out);baseline_path=PROD/'reports'/f'auto_0020_mature_multiseed_cap4_white_v2_{kind}_white_v2_20261002.json';baseline=read(baseline_path)
  assert current['reset_root_before_physics']==baseline['reset_root_before_physics'] and current['reset_joint_pos_before_physics']==baseline['reset_joint_pos_before_physics']
  mapping={'left_slip':'left_slip_legacy_reference','right_slip':'right_slip_legacy_reference'} if kind=='spin' else {'left_support_slip_control':'left_support_slip_legacy_reference','right_support_slip_control':'right_support_slip_legacy_reference'}
  different=[k for k,v in baseline['per_environment'].items() if current['per_environment'].get(mapping.get(k,k))!=v]
  assert not different,'Physical/RNG regression '+str(different)
  if kind=='spin':assert current['spin_skill_pass'] and current['spin_skill_pass_legacy_reference'] and current['physical_smoke_pass']
  else:assert assess(current)['eligible_for_mild_dr_trial']
  comparisons[kind]=dict(initial_root_q_exact=True,all_original_physical_arrays_and_legacy_slip_exact=True,corrected_gate_pass=True,baseline=str(baseline_path),baseline_sha256=sha(baseline_path),report=str(out),report_sha256=sha(out),admission=assess(current) if kind=='flat' else None);receipt['comparisons']=comparisons;atomic(REPORT,receipt)
 assert not probes() and not trainers() and owned_parent() and identity(PARENT)['state']=='T'
 assert read(PROD/'isaac/mod4/env.json')['RM_MILD_DR_PROFILE']=='white_v2' and float(read(PROD/'isaac/mod4/env.json')['RM_SPIN_MAX_RAD_S'])==4.
 freeze=read(PROD/'reports/SPIN_SOURCE_FREEZE.json')
 for name,expected in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else PROD/name)==expected,name
 backup=PROD/'reports/contact_reference_fix_before_20261003';backup.mkdir()
 for name in NAMES:
  target=PROD/'isaac/mod4'/name;assert sha(target)==manifest['source_hashes'][name]
  data=(FILES/'reference_fixed'/name).read_bytes();assert hashlib.sha256(data).hexdigest()==manifest['candidate_hashes'][name]
  ast.parse(data.decode());(backup/name).write_bytes(target.read_bytes());temp=target.with_suffix('.ref_fix_partial');temp.write_bytes(data);temp.replace(target);freeze['sha256']['isaac/mod4/'+name]=manifest['candidate_hashes'][name]
 (backup/'SPIN_SOURCE_FREEZE.json').write_text((PROD/'reports/SPIN_SOURCE_FREEZE.json').read_text())
 freeze.setdefault('evaluation_reference_repairs',[]).append(dict(id='LINK_REFERENCE_FIX_20261003',files=manifest['candidate_hashes'],physics_reward_PPO_changed=False,original_thresholds_unchanged=True,legacy_arrays_retained=True))
 atomic(PROD/'reports/SPIN_SOURCE_FREEZE.json',freeze)
 for name,expected in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else PROD/name)==expected,name
 receipt.update(stage='reference_fix_applied',production_modified=True,only_evaluation_sources_modified=NAMES,source_count_verified=len(freeze['sha256']),source_hashes=manifest['candidate_hashes'],thresholds_unchanged=True,legacy_reports_unchanged=True,rate6_rejection_retained=True,physics_reward_PPO_DR_hardware_unchanged=True)
except BaseException as e:
 receipt.update(stage='repair_rejected_or_program_error',error=repr(e))
 if child and child.poll() is None:
  child.send_signal(signal.SIGINT)
  try:child.wait(timeout=20)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 raise
finally:
 resume();after=read(LEDGER);receipt.update(end_epoch=time.time(),parent_after=identity(PARENT),charged_after=after['charged_training_seconds'],charged_unchanged_in_frozen_window=after['charged_training_seconds']==receipt['charged_at_freeze'],authorized_seconds_after=after['authorized_training_seconds']);atomic(REPORT,receipt)
