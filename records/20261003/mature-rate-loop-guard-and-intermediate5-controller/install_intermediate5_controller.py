"""One guarded control-only migration in an already settled diagnostic window."""
import ast,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent;PROD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE=PROD/'isaac/mod4';REPORTS=PROD/'reports'
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
RECEIPT=REPORTS/'INTERMEDIATE5_CONTROLLER_HANDOVER_20261003.json'
PARENT=2490960;TICKS='17250655';GUARD=2490993;GTICKS='17250722'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def owned(pid,ticks):
 p=identity(pid);return p and p['start_ticks']==ticks and p['cwd']==str(PROD)
def active(except_pid=None):
 out=[]
 suffixes=('/train_mod4_ppo.py','/validate_speed.py','/spin_rate_probe.py','/spin_rate_fullscale_probe.py','/spin_substep_probe.py','/spin_contact_probe.py','/autonomy_turn_probe.py')
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==except_pid:continue
  x=identity(int(p.name))
  if x and x['state']!='Z' and '-c' not in x['argv'] and any(a.endswith(suffixes) for a in x['argv']):out.append(x)
 return out
def resume():
 if not RECEIPT.exists() and owned(PARENT,TICKS):os.kill(PARENT,signal.SIGCONT)
if '--watchdog' in sys.argv:
 worker=int(sys.argv[-1]);began=time.time()
 while identity(worker) and identity(worker)['state']!='Z' and time.time()-began<900:time.sleep(2)
 resume();sys.exit()
assert not RECEIPT.exists(),'Completed control migration cannot be repeated'
diag=read(Path('/home/egde/rl_candidates/MOD4_rate6_substep_diagnostic_20261003/reports/SUBSTEP_FROZEN_READBACK_RETRY1.json'))
assert diag['stage']=='completed' and diag['all_original_per_environment_arrays_exact'] and diag['frozen_charged_unchanged'],'Actual diagnostic must pass its read-only regression first'
for pid in [diag['worker_pid'],diag['watchdog_pid']]:
 for _ in range(20):
  p=identity(pid)
  if not p or p['state']=='Z':break
  time.sleep(.5)
 assert not identity(pid) or identity(pid)['state']=='Z','Previous diagnostic guard has not exited'
assert owned(PARENT,TICKS) and identity(PARENT)['state']!='T'
assert not read(LEDGER).get('active_segment') and not read(REPORTS/'AUTONOMY_STATE.json').get('active_training')
assert not any(any(a.endswith('/train_mod4_ppo.py') for a in x['argv']) for x in active()),'Do not interrupt a newly started trainer'
assert read(PROD/'status.json')['stage'].startswith('frozen_')
prepared=read(FILES/'INTERMEDIATE5_CONTROLLER_PREPARED.json')
for name,h in prepared['source_hashes'].items():assert sha(CODE/name)==h,name
for name,h in prepared['candidate_hashes'].items():assert sha(FILES/'intermediate5_controller'/name)==h,name
cpu=subprocess.run([sys.executable,str(FILES/'test_intermediate5_controller.py')],cwd=FILES,capture_output=True,text=True)
assert cpu.returncode==0,cpu.stderr
watch=subprocess.Popen([sys.executable,__file__,'--watchdog',str(os.getpid())],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
progress=REPORTS/'INTERMEDIATE5_CONTROLLER_PROGRESS_20261003.json'
held=time.time();committed=False
record=dict(stage='guarded_settled_migration',old_parent=identity(PARENT),old_guardian=identity(GUARD),watchdog_pid=watch.pid,guard_installed_before_signal=True,charged_before=read(LEDGER)['charged_training_seconds'],begin_epoch=held)
atomic(progress,record)
try:
 os.kill(PARENT,signal.SIGSTOP)
 for _ in range(100):
  if identity(PARENT)['state']=='T':break
  time.sleep(.01)
 assert identity(PARENT)['state']=='T' and not read(LEDGER).get('active_segment')
 while active():
  assert time.time()-held<300 and owned(PARENT,TICKS) and identity(PARENT)['state']=='T','Scheduled evaluation did not leave a settled window'
  time.sleep(2)
 assert not read(LEDGER).get('active_segment') and not read(REPORTS/'AUTONOMY_STATE.json').get('active_training')
 freeze=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
 for name,h in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else PROD/name)==h,name
 save=diag if 'saved_checkpoint_receipt' in diag else read(Path('/home/egde/rl_candidates/MOD4_rate6_substep_diagnostic_20261003/reports/SUBSTEP_FROZEN_READBACK.json'))
 latest=save['saved_checkpoint_receipt'];assert latest['pid']==save['trainer']['pid']
 checkpoint=Path(latest['checkpoint']);assert checkpoint.parent==Path(save['run']) and checkpoint.exists()
 assert read(REPORTS/'AUTONOMY_STATE.json')['chosen_checkpoint']==str(checkpoint),'A newer formal source needs a fresh PID-bound save audit'
 sys.path.insert(0,str(CODE));import supervise_native_floor as base
 info=base.checkpoint(checkpoint);assert info['finite_tensors']==68
 cfg=read(CODE/'env.json');assert float(cfg['RM_SPIN_MAX_RAD_S'])==4. and cfg['RM_MILD_DR_PROFILE']=='white_v2'
 state=read(REPORTS/'AUTONOMY_STATE.json');assert 6. in state['rate_rejected']
 backup=REPORTS/'intermediate5_controller_before_20261003';backup.mkdir()
 for p in [REPORTS/'SPIN_SOURCE_FREEZE.json',REPORTS/'AUTONOMY_STATE.json',PROD/'status.json',CODE/'env.json']:
  (backup/p.name).write_bytes(p.read_bytes())
 for name in prepared['candidate_hashes']:(backup/name).write_bytes((CODE/name).read_bytes())
 for name,h in prepared['candidate_hashes'].items():
  data=(FILES/'intermediate5_controller'/name).read_bytes();ast.parse(data.decode())
  temp=(CODE/name).with_suffix('.v4_partial');temp.write_bytes(data);temp.replace(CODE/name)
  freeze['sha256']['isaac/mod4/'+name]=h
 freeze.setdefault('controller_repairs',[]).append(dict(id='INTERMEDIATE5_FROM_MATURE4_20261003',files=prepared['candidate_hashes'],physics_reward_PPO_DR_hardware_unchanged=True,rate6_rejection_retained=True))
 atomic(REPORTS/'SPIN_SOURCE_FREEZE.json',freeze)
 state.update(chosen_checkpoint=str(checkpoint),consecutive=0,failed_blocks=0,active_training=None)
 state['pending_intermediate5']=dict(id='INTERMEDIATE5_FROM_MATURE4_20261003',phase='prepared',source_sha256=info['sha256'],target_cap=5.,fixed_profile='white_v2',authority='User delegated targeted spin improvement after questioning repeated mature4 training')
 atomic(REPORTS/'AUTONOMY_STATE.json',state)
 for name,h in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else PROD/name)==h,name
 assert read(LEDGER)['charged_training_seconds']==record['charged_before'] and read(LEDGER)['authorized_training_seconds']==252000
 # SIGTERM is queued while the exact parent is stopped; SIGCONT permits termination.
 os.kill(PARENT,signal.SIGTERM);os.kill(PARENT,signal.SIGCONT)
 for _ in range(100):
  if not identity(PARENT) or identity(PARENT)['state']=='Z':break
  time.sleep(.1)
 assert not identity(PARENT) or identity(PARENT)['state']=='Z','Old parent has not exited'
 if owned(GUARD,GTICKS):os.kill(GUARD,signal.SIGTERM)
 assert not active() and not read(LEDGER).get('active_segment')
 record.update(stage='handover_completed',source=info,old_parent_exited=True,charged_after=read(LEDGER)['charged_training_seconds'],authorized_seconds=252000,source_count=len(freeze['sha256']),new_source_hashes=prepared['candidate_hashes'],CPU_checks=cpu.stdout,only_controller_and_rate_schedule_changed=True,rate6_rejection_retained=True,physics_reward_PPO_DR_hardware_unchanged=True,end_epoch=time.time())
 atomic(RECEIPT,record);committed=True
 log=PROD/'supervisor_intermediate5_20261003.log';assert not log.exists()
 env=os.environ.copy();env['PYTHONUNBUFFERED']='1'
 with log.open('x') as stream:
  parent=subprocess.Popen([sys.executable,'-u',str(CODE/'supervise_autonomy.py'),'--resume'],cwd=PROD,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=env)
 record.update(new_parent_pid=parent.pid,log=str(log));atomic(RECEIPT,record)
 print(json.dumps(record))
except BaseException as error:
 record.update(stage='migration_error',error=repr(error),end_epoch=time.time());atomic(progress,record)
 if not committed:
  backup=REPORTS/'intermediate5_controller_before_20261003'
  if backup.exists():
   for name in prepared['candidate_hashes']:
    if (backup/name).exists():(CODE/name).write_bytes((backup/name).read_bytes())
   for name in ['SPIN_SOURCE_FREEZE.json','AUTONOMY_STATE.json']:
    if (backup/name).exists():(REPORTS/name).write_bytes((backup/name).read_bytes())
  resume()
 raise
finally:resume()
