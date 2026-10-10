"""Preserve380 failure; extend only source view manager properties in a new scope."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;P=D/'environment_view_payload';C=P/'isaac/mod4';R=D/'reports';C.mkdir(parents=True,exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,text):compile(text,str(p),'exec');assert not p.exists();p.write_bytes(text.encode())
text=(D/'payload/isaac/mod4/curb20_command_migration.py').read_text()
old='view._env=SimpleNamespace(scene=SimpleNamespace(terrain=SimpleNamespace(retention_assignment_sha=source_assignment_sha)))'
assert text.count(old)==1
text=text.replace(old,'view._env=SimpleNamespace(num_envs=term.num_envs,device=term.device,scene=SimpleNamespace(terrain=SimpleNamespace(retention_assignment_sha=source_assignment_sha)))')
put(C/'curb20_command_migration_environment_view.py',text)
text=(D/'payload/isaac/mod4/curb20_full_checkpoint.py').read_text().replace('from curb20_command_migration import','from curb20_command_migration_environment_view import')
put(C/'curb20_full_checkpoint_environment_view.py',text)
text=(D/'payload/isaac/mod4/train_curb20_full_resume_ppo.py').read_text().replace('from curb20_full_checkpoint import','from curb20_full_checkpoint_environment_view import')
needle='    manifest["src_sha256"] = snapshot';assert text.count(needle)==1
text=text.replace(needle,"    for name in ('curb20_command_migration_environment_view.py','curb20_full_checkpoint_environment_view.py'):\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n"+needle)
put(C/'train_curb20_environment_view_resume_ppo.py',text)
base=(D/'payload/supervise_curb20_fullstate_once.py').read_text();fn=next(x for x in ast.parse(base).body if isinstance(x,ast.FunctionDef) and x.name=='train');train=ast.get_source_segment(base,fn)
train=train.replace("'train_curb20_full_resume_ppo.py'","'train_curb20_environment_view_resume_ppo.py'")
header='''"""Unique new environment-view repair: reuse small/native, new big restore then300s."""
from pathlib import Path
import argparse,json,os,subprocess,shutil,time,traceback
import supervise_curb20_fullstate_reviewed_once as reviewed
from clock_training_health import learning_health_pass
prior=reviewed.prior;D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=prior.s
read=prior.read;write=prior.write;identity=prior.identity;fullsave=reviewed.fullsave;freeze_run=prior.freeze_run;verify=prior.verify;runtime=prior.runtime;phase=reviewed.phase
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_REVIEWED_20261011')
def trainers():
 result=prior.trainers()
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   if any(Path(v.decode(errors='replace')).name=='train_curb20_environment_view_resume_ppo.py' for v in p.read_bytes().split(b'\\0')):result.append(identity(int(p.parent.name)))
  except (OSError,ValueError):pass
 return result
def wait_existing():
 prior.wait_existing();att=read(OLD/'reports/E1_REVIEWED_CONTROLLER_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 st=read(OLD/'reports/E1_STATE.json');loc=[st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),st['child']]
 for v in loc:
  a=identity(v['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=v['start_ticks']
 segs=read(s.q.ctl.CANONICAL)['completed_segments'];assert len([x for x in segs if x['pid']==st['child']['pid']])==1
 assert not trainers()
'''
tail='''
def guardian(owner,ticks):
 while True:
  a=identity(owner);lost=not a or a['state']=='Z' or a['start_ticks']!=ticks
  segment=s.q.base.budget_state()['active_segment'];st=read(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else {};loc=st.get('child');child=identity(loc['pid']) if loc else None
  own=bool(child and child['start_ticks']==loc['start_ticks'] and st['owner']['pid']==owner and str(CODE/'train_curb20_environment_view_resume_ppo.py') in child['argv'])
  if segment and own and segment['pid']==child['pid'] and (lost or s.left()<=0):
   for root in (D/'discard_logs',D/'learning_logs'):
    try:run=s.q.w.rate.trainer_run(root,child['pid']);break
    except (AssertionError,FileNotFoundError):run=None
   if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own CURB environment-view complete save; guardian owner/budget\\n')
  if not own and (lost or (R/'E1_REVIEW_READY.json').exists() or (R/'E1_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source()
 assert read(R/'CURB_ENVIRONMENT_VIEW_CPU_PASSED.json')['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=prior.inherited.fullsave(init),old380_all_actual_exited_failed_before_PPO=True,two_original_OS_locks_held=True,no_new_budget=True))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_CURB',new_environment_view_manager_property_repair_only=True,small128_native_SDK_not_repeated=True,formal_seconds=300,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 small=read(R/'REUSED_SMALL128.json');assert small['discarded_preflight'] and small['actual_updates']==2 and small['actual_environment_steps']==6144
 _,big=train(init,20000,4,900,'curb_envview_discard20k',True)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=small,big=big,weights_discarded=True,SDK_native_small_exact_reused=True,new_environment_view_cuda_scope_passed=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_CURB20_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_CURB',all_courses_finished=False,requires_actual133_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_CURB20_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''
put(P/'supervise_curb20_environment_view_once.py',header+'\n'+train+'\n'+tail)
v=json.loads(sorted(R.glob('FULLSTATE_ACTUAL_[0-9]*.json'))[-1].read_bytes());failed=[s for s in v['canonical']['own_completed_segments'] if s['pid']==2429546];assert len(failed)==1
(R/'ENVIRONMENT_VIEW_FAILURE_AND_REPAIR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='CURB380-BIG-RESTORE-ENVIRONMENT-VIEW-REJECTED-01',actual_original_error=v['logs']['curb_discard20k_1791658232236459487.log']['tail'],failed_PID=2429546,source_SHA=prior_sha if False else '3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',failed_before_learning_no_new_own_checkpoint=True,no_learning_iterations_in_log=True,unique_original_parent_settled_segment=failed[0],seconds=failed[0]['ended_epoch']-failed[0]['started_epoch'],all_actual_parent_guardian_child_exited=True,active_segment=None,repair='Source identity view needs num_envs and device properties accessed by actual ManagerTermBase. Extend new isolated view, retain strict original loader, SDK/native/small exact reuse; genuinely new big restore admission only.',new_source_files={p.relative_to(P).as_posix():H(p.read_bytes()) for p in P.rglob('*') if p.is_file()},old380_source_not_patched=True,no_budget_extension_or_recharge=True),indent=2))
print(json.dumps(dict(new_files=4,failed_before_learning_seconds=failed[0]['ended_epoch']-failed[0]['started_epoch'],original380_retained=True)))
