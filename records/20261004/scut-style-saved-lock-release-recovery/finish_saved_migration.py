"""Explicit recovery from already saved/exited trainer; no second handover.

Use the recorded exit epoch, never current time, to avoid charging this frozen
repair window. Preserve both failed migration attempts and their exact sources.
"""
import json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import fcntl,json,os,signal,subprocess,sys,time
from pathlib import Path
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');S=Path('/home/egde/rl_candidates/MOD4_SCUT_STYLE_RATE_CONTINUE_20261004');R=C/'reports'
sys.path.insert(0,str(C));import supervise_contact_gate_continue as old
ctl=old.ctl;repair=old.repair;base=old.base;helpers=old.helpers;read=old.read
__import__('torch').set_num_threads(1);base.STATE.update(read(P/'status.json'))
j=read(R/'SCUT_STYLE_MIGRATION_RETRY1.json')
assert j['stage']=='attention_required' and j['old_parent_retired'] and 'tail_charged_s' not in j
assert not (R/'SCUT_STYLE_SAVED_RECOVERY_BEGIN.json').exists() and not (R/'SCUT_STYLE_HANDOVER.json').exists()
for pid in (4145334,4145375,4158388,4177891):
 ident=helpers.identity(pid);assert not ident or ident['state']=='Z',ident
assert not base.trainers() and not helpers.active_processes(ctl.PROBES)
watch=helpers.identity(j['watchdog']['pid'])
if watch and watch['state']!='Z':
 assert watch['start_ticks']==j['watchdog']['start_ticks'] and str(S/'migrate_scut_style_retry1.py') in watch['argv'] and '--watchdog' in watch['argv']
 os.kill(watch['pid'],signal.SIGTERM)
 for _ in range(100):
  now=helpers.identity(watch['pid'])
  if not now or now['state']=='Z':break
  time.sleep(.025)
 assert not now or now['state']=='Z'
locks=[]
try:
 for path in (P/'autonomy_controller.lock',ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
  f=path.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 prep=read(S/'PREPARED.json')
 for name,h in prep['files'].items():assert base.sha(S/name)==h,name
 repair.verify();source=base.checkpoint(Path(j['complete_checkpoint']['path']))
 assert source==j['complete_checkpoint'] and source['finite_tensors']==68
 run=Path(j['run']);saved=read(run/'latest_complete.json')
 assert saved==j['latest_complete'] and saved['pid']==4158388 and saved['checkpoint']==source['path']
 assert saved['saved_at']<=j['ended_epoch'] and (run/'STOP_AFTER_SAVE').exists()
 log=Path(j['old_trainer']['argv'][0]) # no execution; exact log comes from ledger
 b=base.budget_state();segment=b['active_segment']
 assert segment['pid']==4158388 and segment['accounted_through_epoch']<=j['ended_epoch']
 text=Path(segment['log']).read_text(errors='replace')
 assert 'Full checkpoint saved; authorized budget or stop-file reached' in text and 'Traceback (most recent call last)' not in text
 ctl.S=read(ctl.STATE_PATH);assert ctl.S['active_training']['pid']==4158388 and ctl.S['mature']==j['last_paired_mature']
 base.atomic_json(R/'SCUT_STYLE_SAVED_RECOVERY_BEGIN.json',dict(epoch=time.time(),prior_failure=str(R/'SCUT_STYLE_MIGRATION_RETRY1.json'),actual_exit_epoch=j['ended_epoch'],before_budget=b,source=source,locks_obtained_after_all_old_processes_exit=True,repair_window_no_PPO=True))
 from autonomy_policy import settle_segment
 tail=settle_segment(b,4158388,j['ended_epoch'])
 b['completed_segments'][-1].update(end_reason='scut_style_complete_saved_recovery',end_evidence='Recorded actual exit after atomic saved source and graceful log',observation_uncertainty_upper_s=.25)
 base.atomic_json(ctl.CANONICAL,b)
 ctl.S['active_training']=None;ctl.S['chosen_checkpoint']=source['path'];ctl.persist()
 freeze=read(R/'SOURCE_FREEZE.json');original=dict(freeze['sha256'])
 base.atomic_json(R/'SOURCE_FREEZE_BEFORE_SCUT_STYLE.json',freeze)
 targets={'scut_style_gate.py':C/'isaac/mod4/scut_style_gate.py','supervise_scut_style_continue.py':C/'supervise_scut_style_continue.py'}
 for name,path in targets.items():
  assert not path.exists();path.write_bytes((S/name).read_bytes());freeze['sha256'][path.relative_to(C).as_posix()]=base.sha(path)
 freeze.update(scut_style_acceptance_version=prep['acceptance_version'],slip_numeric_veto_removed=True,all_prior_sources_unchanged=True)
 base.atomic_json(R/'SOURCE_FREEZE.json',freeze)
 assert all(base.sha(C/name)==h for name,h in original.items());repair.verify()
 settled_bytes=ctl.CANONICAL.read_bytes()
 base.atomic_json(R/'SCUT_STYLE_PREPARED.json',prep)
 hand=dict(stage='completed',epoch=time.time(),complete_checkpoint=source,latest_complete=saved,
  last_paired_mature=ctl.S['mature'],old_parent=j['old_parent'],old_trainer=j['old_trainer'],old_guardian=j['old_guardian'],
  old_parent_future_launches_disabled=True,tail_charged_s=tail,actual_exit_epoch=j['ended_epoch'],
  observation_uncertainty_upper_s=.25,acceptance_version=prep['acceptance_version'],budget=base.budget_state(),
  new_reward_physics_PPO_DR_hardware_changes=False,source_count_before=len(original),source_count_after=len(freeze['sha256']),
  prior_migration_errors_preserved=[str(R/'SCUT_STYLE_MIGRATION.json'),str(R/'SCUT_STYLE_MIGRATION_RETRY1.json')],
  recovery_does_not_charge_frozen_downtime=True)
 base.atomic_json(R/'SCUT_STYLE_HANDOVER.json',hand)
 oldstate=read(old.J);oldstate.update(superseded_by=str(R/'SCUT_STYLE_STATE.json'),superseded_epoch=time.time());base.atomic_json(old.J,oldstate)
 base.status(stage='scut_style_saved_pending_assessment',supervisor_pid=None,training_pid=None,evaluation_pid=None,validation_pid=None,
             latest_checkpoint=source['path'],acceptance_version=prep['acceptance_version'],error=None)
 assert ctl.CANONICAL.read_bytes()==settled_bytes
 base.atomic_json(R/'SCUT_STYLE_SAVED_RECOVERY_COMPLETED.json',dict(stage='completed',tail_settled_once_s=tail,source=source,authorized_seconds=b['authorized_training_seconds'],charged_seconds=b['charged_training_seconds'],actual_exit_epoch=j['ended_epoch'],freeze_repair_seconds_not_charged=time.time()-j['ended_epoch'],budget_bytes_exact_during_install=True))
 for f in locks:f.close()
 locks=[]
 with (C/'supervisor_scut_style_continue.log').open('x') as stream:
  worker=subprocess.Popen([base.PY,str(C/'supervise_scut_style_continue.py')],cwd=C,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 launch=helpers.identity(worker.pid);assert launch and launch['cwd']==str(C)
 launch.update(epoch=time.time(),acceptance_version=prep['acceptance_version'],source=source)
 base.atomic_json(R/'SCUT_STYLE_LAUNCHED.json',launch);print(json.dumps(dict(launch=launch,tail_s=tail,source=source,remaining=b['remaining_training_seconds'])))
finally:
 for f in locks:f.close()
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=50)
 raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
 print(raw.strip())
 with c.open_sftp() as s:
  for name in ('SCUT_STYLE_HANDOVER.json','SCUT_STYLE_LAUNCHED.json','SCUT_STYLE_SAVED_RECOVERY_BEGIN.json','SCUT_STYLE_SAVED_RECOVERY_COMPLETED.json'):
   s.get('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004/reports/'+name,str(D/name))
finally:c.close()
