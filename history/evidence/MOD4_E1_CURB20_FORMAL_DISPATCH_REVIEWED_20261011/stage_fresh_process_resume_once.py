"""New386 fresh-process-only repair; no SDK/native or completed PPO replay."""
from stage_environment_view_log_receipt_once import D,R,E,B,PY,connect_both,cleanup,linux_json,H,save,put
from pathlib import Path
import json,time,shlex,traceback
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FRESH_PROCESS_REVIEWED_20261011'
def main():
 save('FRESH_PROCESS_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='CURB386-FRESH-PROCESS-RESUME-STAGE-01',no_GPU_or_budget_action=True))
 n,w=connect_both()
 try:
  v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,shutil,fcntl
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());assert not new.exists()
st=j(old/'reports/E1_STATE.json');att=j(old/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
for loc in [st['owner'],st['child'],j(old/'reports/E1_GUARDIAN_STARTED.json')]:
 p=Path('/proc')/str(loc['pid'])
 if p.exists():a=(p/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc['start_ticks']
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
segs=[x for x in l['completed_segments'] if x['pid']==st['child']['pid']];assert len(segs)==1
errors=list(old.glob('curb_envview_discard20k_*.error.txt'));assert len(errors)==1 and 'assert int(env._sim_step_counter)==0' in errors[0].read_text()
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
run=Path(j(old/'reports/E1_CURRENT_SAVE.json')['own_run']);m=j(run/'run_manifest.json');health=j(run/'CLOCK_TRAINING_HEALTH.json');rec=j(run/'latest_complete.json')
assert rec['pid']==st['child']['pid'] and health['control_steps']==96 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==384
assert health['ordinary_episode_reset_events']==health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and not health['nonfinite_observed'] and health['stop_reason'] is None and health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact']
for name,h in m['src_sha256'].items():assert hashlib.sha256((run/'src_snapshot'/name).read_bytes()).hexdigest()==h
for name in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):assert j(run/name)['source_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
cp=Path(rec['checkpoint']);big=dict(epoch=time.time(),checkpoint=dict(path=str(cp),bytes=cp.stat().st_size,sha256=hashlib.sha256(cp.read_bytes()).hexdigest()),run=str(run),own_PID_bound_receipt=rec,actual_completed_updates=4,actual_environment_steps=1920000,health=health,unique_completed_segment=segs,discarded_preflight=True,original_postlearn_fullresume_failure_retained=True,whole_big_admission_pending_new_fresh_resume=True,learning_core_not_repeated=True)
f=j(old/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==384;new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_REUSED_NATIVE.json','CURB_FOUR_CASE_TEMPLATES.json','CURB_TARGET_FULLSTATE_CPU_PASSED.json','CURB_ENVIRONMENT_VIEW_CPU_PASSED.json','REUSED_SMALL128.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
(new/'reports/FRESH_PROCESS_BIG_CORE_VERIFIED.json').write_text(json.dumps(big,indent=2))
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),source_freeze=f,actual_old384_exit_two_OS_locks_free=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),big_completed_core=big,actual_old_error=dict(path=str(errors[0]),bytes=errors[0].stat().st_size,sha256=hashlib.sha256(errors[0].read_bytes()).hexdigest(),text=errors[0].read_text()))))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('FRESH_PROCESS_384_COPIED.json',v)
  with n.open_sftp() as f:
   freeze=v['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'fresh_process_payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'fresh_process_payload').as_posix();raw=p.read_bytes();compile(raw,name,'exec');assert name not in hashes;put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   assert len(hashes)==386;freeze=dict(freeze,candidate_root=NEW,sha256=hashes,all384_bytes_preserved=True,new_fresh_process_resume_only=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('FRESH_PROCESS_SOURCE_FREEZE.json',freeze)
  code=r'''from pathlib import Path
import sys,json,time,ast,torch,hashlib
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_fresh_process_resume_once as own
own.verify();own.wait_existing();big=own.read(D/'reports/FRESH_PROCESS_BIG_CORE_VERIFIED.json');cp=Path(big['checkpoint']['path']);assert hashlib.sha256(cp.read_bytes()).hexdigest()==big['checkpoint']['sha256']
info=own.fullsave(cp);assert info['finite_tensors']==102
text=(D/'isaac/mod4/probe_curb20_fresh_process_full_resume.py').read_text();tree=ast.parse(text);main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
calls=[x.func.attr for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)];assert 'learn' not in calls and 'step' not in calls and 'update' not in calls
original=(D/'isaac/mod4/action_delay_checkpoint.py').read_text();assert 'assert int(env._sim_step_counter)==0' in original
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_only=True,no_CUDA_initialized=True,source_count=386,big_checkpoint_CPU102=info,completed_big4_updates_not_repeated=True,SDK_native_small_exact_reused=True,actual_zero_step_startup_guard_unchanged=True,new_probe_main_has_no_learn_step_or_optimizer_update=True,new_fresh_process_actual_sameCURB_CUDA_restore_pending=True,formal_source_still_original129_3c97_not_discarded_big=True)
(D/'reports/CURB_FRESH_PROCESS_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('FRESH_PROCESS_CPU_REJECTED.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_budget_action=True));raise RuntimeError('CPU fresh-process source admission rejected')
  cpu=json.loads(raw);save('FRESH_PROCESS_TARGET_CPU_PASSED.json',cpu);print(json.dumps(dict(root=NEW,source_count=386,CPU_passed=True,big_checkpoint=cpu['big_checkpoint_CPU102'],no_GPU_started=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FRESH_PROCESS_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_stage_replay=True));raise
