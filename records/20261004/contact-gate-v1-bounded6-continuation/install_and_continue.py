"""One explicit, evidence-bound controller installation and bounded6 launch."""
import json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
CAL='/home/egde/rl_candidates/MOD4_SPIN_CONTACT_GATE_CALIBRATION_20261004'
STAGE='/home/egde/rl_candidates/MOD4_CONTACT_GATE_CONTINUATION_20261004/source_role_review_v2'
code=r'''import fcntl,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');S=Path('/home/egde/rl_candidates/MOD4_CONTACT_GATE_CONTINUATION_20261004/source_role_review_v2');CAL=Path('/home/egde/rl_candidates/MOD4_SPIN_CONTACT_GATE_CALIBRATION_20261004');R=C/'reports'
L=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'CONTACT_CONTINUATION_INSTALL_BEGIN.json').exists() and not (R/'CONTACT_CONTINUATION_STATE.json').exists(),'One-shot continuation already began; inspect actual state'
locks=[]
try:
 for path in (P/'autonomy_controller.lock',L.parent/'native_floor_supervisor.lock'):
  f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 sys.path.insert(0,str(C));import supervise_rolling_repair as repair
 ctl=repair.ctl;ctl.idle();repair.verify()
 assert not ctl.helpers.active_processes(ctl.PROBES+('/contact_calibration_probe.py','/supervise_contact_gate_continue.py'))
 assert read(P/'status.json')['stage']=='targeted_repair_hold' and read(R/'REPAIR_STATE.json')['phase']=='repair_hold'
 assert read(ctl.STATE_PATH)['active_training'] is None and read(L)['active_segment'] is None
 before=L.read_bytes();old_freeze=(R/'SOURCE_FREEZE.json').read_bytes();old_hashes=read(R/'SOURCE_FREEZE.json')['sha256']
 for name,h in read(S/'PREPARED.json')['source_sha256'].items():assert sha(S/name)==h,name
 sys.path.insert(0,str(S));from contact_gate import VERSION;from continuation_contract import validate
 evidence=read(CAL/'reports/CONTACT_CALIBRATION_REVIEW.json');flat=read(CAL/'reports/retained_flat/RETAINED_FLAT_COMPLETED.json');ad=read(CAL/'reports/CONTACT_GATE_ADJUDICATION.json')
 assert ad['review_sha256']==sha(CAL/'reports/CONTACT_CALIBRATION_REVIEW.json')
 source=ctl.base.checkpoint(Path(evidence['source_selection']['latest6']['path']))
 validate(evidence,flat,source,read(ctl.STATE_PATH)['mature'],VERSION,sha(S/'contact_gate.py'),ad)
 assert (read(CAL/'reports/CALIBRATION_COMPLETED.json')['stage']=='completed')
 assert read(L)['charged_training_seconds']==210011.31948041916 and read(L)['authorized_training_seconds']==252000
 ctl.base.atomic_json(R/'CONTACT_CONTINUATION_INSTALL_BEGIN.json',dict(epoch=time.time(),source=source,gate_version=VERSION,ledger_sha256=sha(L),state_before=read(R/'REPAIR_STATE.json'),staged_source=str(S),draft_all_nine_hypothesis_retained=False if evidence['eligible_for_versioned_gate_review'] else True))
 (R/'ROLLING_SOURCE_FREEZE_BEFORE_CONTACT_GATE.json').write_bytes(old_freeze)
 destinations={name:(C/name if name=='supervise_contact_gate_continue.py' else C/'isaac/mod4'/name) for name in read(S/'PREPARED.json')['source_sha256']}
 for name,p in destinations.items():
  assert not p.exists(),'Never overwrite a production source or old entry: '+str(p)
  shutil.copy2(S/name,p)
 f=read(R/'SOURCE_FREEZE.json')
 for name,p in destinations.items():f['sha256'][p.relative_to(C).as_posix()]=sha(p)
 f.update(contact_acceptance_version=VERSION,original_mesh015_shadows_retained=True,reward_physics_hardware_DR_PPO_unchanged_from_rolling_v1=True)
 ctl.base.atomic_json(R/'SOURCE_FREEZE.json',f)
 assert all(sha(C/name)==h for name,h in old_hashes.items()),'Old123 source changed'
 repair.verify();assert L.read_bytes()==before
 manifest=dict(stage='installed_pending_preflight',epoch=time.time(),source=source,gate_version=VERSION,original_candidate_files_unchanged=len(old_hashes),candidate_frozen_files=len(f['sha256']),staged_tests=read(S/'PREPARED.json')['CPU_contract_tests'],source_sha256={p.relative_to(C).as_posix():sha(p) for p in destinations.values()},calibration_review_sha=sha(CAL/'reports/CONTACT_CALIBRATION_REVIEW.json'),adjudication_sha=sha(CAL/'reports/CONTACT_GATE_ADJUDICATION.json'),flat_receipt_sha=sha(CAL/'reports/retained_flat/RETAINED_FLAT_COMPLETED.json'),budget_bytes_exact_during_install=True,PPO_not_yet_started=True)
 ctl.base.atomic_json(R/'CONTACT_CONTINUATION_INSTALLED.json',manifest)
 with (C/'supervisor_contact_gate_continue.log').open('x') as log:
  worker=subprocess.Popen([ctl.base.PY,str(C/'supervise_contact_gate_continue.py')],cwd=C,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 owner=ctl.helpers.identity(worker.pid);owner.update(epoch=time.time(),independent_session=True,source=source,gate_version=VERSION)
 ctl.base.atomic_json(R/'CONTACT_CONTINUATION_LAUNCHED.json',owner);print(json.dumps(owner))
finally:
 for f in locks:f.close()
'''
c=connect()
try:
 with c.open_sftp() as s:
  for name in ('CONTACT_CALIBRATION_REVIEW.json','CONTACT_GATE_INDIVIDUAL_REVIEW.json','CONTACT_CALIBRATION_REPORT.md','CONTACT_GATE_ADJUDICATION.json','SOURCE_ROLE_ADJUDICATION.md'):
   s.put(str(D/name),CAL+'/reports/'+name)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
 print(raw.strip())
 with c.open_sftp() as s:
  for name in ('CONTACT_CONTINUATION_INSTALL_BEGIN.json','CONTACT_CONTINUATION_INSTALLED.json','CONTACT_CONTINUATION_LAUNCHED.json'):s.get('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004/reports/'+name,str(D/name))
finally:c.close()
