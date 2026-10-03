"""One settled recovery after the old parent exited during the migration check.

Never settles a segment, resumes an old parent, or repeats a previous handover.
"""
import ast,fcntl,hashlib,json,os,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE=ROOT/'isaac/mod4';REPORTS=ROOT/'reports'
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
RECEIPT=REPORTS/'INTERMEDIATE5_CONTROLLER_HANDOVER_20261003.json'
RECOVERY=REPORTS/'INTERMEDIATE5_EXIT_RACE_RECOVERY_20261003.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,x):
 t=p.with_suffix('.partial');t.write_text(json.dumps(x,indent=2));t.replace(p)
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
def active():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  x=identity(int(p.name))
  if not x or x['state']=='Z' or '-c' in x['argv']:continue
  suffixes=('/train_mod4_ppo.py','/validate_speed.py','/spin_rate_probe.py','/spin_rate_fullscale_probe.py','/spin_substep_probe.py','/spin_contact_probe.py','/autonomy_turn_probe.py','/supervise_autonomy.py')
  if any(a.endswith(suffixes) for a in x['argv']):out.append(x)
 return out
assert not RECEIPT.exists() and not RECOVERY.exists(),'Recovery already recorded; inspect instead'
failed=read(REPORTS/'INTERMEDIATE5_CONTROLLER_PROGRESS_20261003.json')
assert failed['stage']=='migration_error' and "NoneType" in failed['error']
for label in ['old_parent','old_guardian']:
 old=failed[label];now=identity(old['pid'])
 assert not now or now['state']=='Z' or now['start_ticks']!=old['start_ticks'],label+' still active'
assert not active(),active()
budget=read(LEDGER);state=read(REPORTS/'AUTONOMY_STATE.json')
assert not budget.get('active_segment') and not state.get('active_training')
assert budget['charged_training_seconds']==failed['charged_before']
assert budget['authorized_training_seconds']==252000 and budget['owner_root']==str(ROOT)
for p in [ROOT/'autonomy_controller.lock',LEDGER.parent/'native_floor_supervisor.lock']:
 with p.open('a+') as stream:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
prepared=read(FILES/'INTERMEDIATE5_CONTROLLER_PREPARED.json')
freeze=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
for name,digest in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else ROOT/name)==digest,name
for name,digest in prepared['source_hashes'].items():assert sha(CODE/name)==digest,name
for name,digest in prepared['candidate_hashes'].items():assert sha(FILES/'intermediate5_controller'/name)==digest,name
cpu=subprocess.run([sys.executable,str(FILES/'test_intermediate5_controller.py')],capture_output=True,text=True,cwd=FILES)
assert cpu.returncode==0,cpu.stderr
save=read(Path('/home/egde/rl_candidates/MOD4_rate6_substep_diagnostic_20261003/reports/SUBSTEP_FROZEN_READBACK.json'))
latest=save['saved_checkpoint_receipt'];checkpoint=Path(latest['checkpoint'])
assert latest['pid']==save['trainer']['pid'] and checkpoint.parent==Path(save['run'])
assert state['chosen_checkpoint']==str(checkpoint)
sys.path.insert(0,str(CODE));import supervise_native_floor as base
info=base.checkpoint(checkpoint);assert info['finite_tensors']==68
assert info['sha256']=='0904737799adc6e3f71545fb03bfd70730abf04e3aae42ede38e56233d48c9bb'
cfg=read(CODE/'env.json');assert float(cfg['RM_SPIN_MAX_RAD_S'])==4. and cfg['RM_MILD_DR_PROFILE']=='white_v2' and 6. in state['rate_rejected']
record=dict(stage='recovery_validated_no_live_children',error_source=failed,source=info,charged_before=budget['charged_training_seconds'],authorized_seconds=252000,begin_epoch=time.time(),no_segment_settlement=True,old_parent_already_exited=True,CPU_checks=cpu.stdout)
atomic(RECOVERY,record)
for name,digest in prepared['candidate_hashes'].items():
 data=(FILES/'intermediate5_controller'/name).read_bytes();ast.parse(data.decode())
 t=(CODE/name).with_suffix('.v4_partial');t.write_bytes(data);t.replace(CODE/name)
 freeze['sha256']['isaac/mod4/'+name]=digest
freeze.setdefault('controller_repairs',[]).append(dict(id='INTERMEDIATE5_FROM_MATURE4_20261003',files=prepared['candidate_hashes'],physics_reward_PPO_DR_hardware_unchanged=True,rate6_rejection_retained=True))
atomic(REPORTS/'SPIN_SOURCE_FREEZE.json',freeze)
state.update(chosen_checkpoint=str(checkpoint),consecutive=0,failed_blocks=0,active_training=None)
state['pending_intermediate5']=dict(id='INTERMEDIATE5_FROM_MATURE4_20261003',phase='prepared',source_sha256=info['sha256'],target_cap=5.,fixed_profile='white_v2',authority='User delegated targeted spin improvement after questioning repeated mature4 training')
atomic(REPORTS/'AUTONOMY_STATE.json',state)
for name,digest in freeze['sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else ROOT/name)==digest,name
assert read(LEDGER)==budget and not active()
record.update(stage='handover_completed',charged_after=read(LEDGER)['charged_training_seconds'],source_count=len(freeze['sha256']),new_source_hashes=prepared['candidate_hashes'],rate6_rejection_retained=True,physics_reward_PPO_DR_hardware_unchanged=True,end_epoch=time.time())
atomic(RECEIPT,record)
log=ROOT/'supervisor_intermediate5_recovery1_20261003.log';assert not log.exists()
with log.open('x') as stream:
 parent=subprocess.Popen([sys.executable,'-u',str(CODE/'supervise_autonomy.py'),'--resume'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONUNBUFFERED':'1'})
record.update(stage='new_controller_launched',new_parent_pid=parent.pid,log=str(log));atomic(RECEIPT,record);atomic(RECOVERY,record)
print(json.dumps({'stage':record['stage'],'new_parent_pid':parent.pid,'source':info,'charged_after':record['charged_after']}))
