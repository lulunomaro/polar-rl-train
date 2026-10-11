"""New isolated reset-entry source and target CPU admission, without GPU launch."""
from entry_io import *
def main():
 assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),new_entry_axis_only=True,no_old_once_replay=True))
 files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==14
 decision=json.loads((PREV/'reports/WAVE50_147_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes())
 diagnostic=json.loads((PREV/'reports/WAVE50_ENTRY_NEXT_AXIS_ACTUAL_DIAGNOSIS.json').read_bytes())
 axis=dict(candidate_forward_complete=5,candidate_reverse_complete=25,not_qualified50=True,new_entry_axis_approved=True,default_source_SHA=SOURCE_SHA,actual_complete147_decision=decision,actual_entry_axis_diagnosis=diagnostic)
 jobs=json.loads((PRIOR/'reports/WAVE50_FOUR_CASE_TEMPLATES.json').read_bytes())['jobs']
 n,w=io.connect_both()
 try:
  checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/results')):
    checks.append(dict(host=host,path=path,names=fs.listdir(path)))
  number=148
  while any(any('episode-d3-'+str(number)+'-' in x for x in row['names']) for row in checks):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=row['host'],path=row['path'],matches=[x for x in row['names'] if 'episode-d3-'+str(number)+'-' in x]) for row in checks]);save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  code=r'''from pathlib import Path
import json,hashlib,sys,time,torch,shutil,fcntl
BASE=Path(BASE_TOKEN);OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);B=Path(B_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_second_bounded_once as previous
previous.prior.verify_original_records(previous.m.s.q,OLD)
st=j(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE50_second_bounded_saved_review_ready' and st['child'] is None
p=j(OLD/'reports/e1_WAVE50_second_bounded_observation_PASSED.json');assert p['checkpoint']['sha256']=='a67b955f680dd101cc4480f19c2e95dd86c34423148302fad1d8e925e206d4df' and len(p['unique_completed_segment'])==1
for loc in (st['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=89922117)):
 actual=previous.m.identity(loc['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
source=Path(SOURCE_TOKEN);assert h(source)==SHA_TOKEN
from g4_fullsave_cpu import fullsave
selected=fullsave(source);assert selected['finite_tensors']==102
assert not previous.m.trainers();b=j(B);assert b['active_segment'] is None and not j(previous.m.s.q.ctl.STATE_PATH).get('active_training')
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>4000
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
freeze=j(BASE/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==384
for name,sha in freeze.items():assert h(BASE/name)==sha
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;disk=shutil.disk_usage(BASE);assert mem>8*1024**3 and disk.free>8*1024**3 and not D.exists()
before=B.read_bytes();D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/name,q);assert h(q)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','REUSED_ACTUAL_CONTRACTS.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json'):
 shutil.copy2(BASE/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),oldfreeze=freeze,selected=selected,own_source_SHA=SHA_TOKEN,complete129_ancestor_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',old386_own_PASSED_unique_closed=True,old_actual_exits=True,two_fcntl_free=locks,canonical_SHA=h(B),remaining_seconds=b['remaining_training_seconds'],resources=dict(RAM_bytes=mem,disk_free_bytes=disk.free),no_GPU_or_budget_write=True)))
'''
  for k,v in {'BASE_TOKEN':BASE,'OLD_TOKEN':OLD,'ROOT_TOKEN':ROOT,'B_TOKEN':io.B,'SOURCE_TOKEN':SOURCE,'SHA_TOKEN':SOURCE_SHA}.items():code=code.replace(k,repr(v))
  boundary=run(n,code);save('OLD386_AND_SOURCE369_ACTUAL_BOUNDARY.json',boundary)
  freeze=dict(boundary['oldfreeze']);new=[]
  with n.open_sftp() as f:
   for name,raw in files.items():
    assert name not in freeze
    io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw);new.append(name)
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,old384_allbytes_exact=True,new_entry_axis_files=new),'SOURCE_SELECTED.json':boundary['selected'],'OLD386_AND_SOURCE369_ACTUAL_BOUNDARY.json':boundary,'COMPLETE147_ENTRY_AXIS_DECISION.json':axis,'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused,'WAVE50_FOUR_CASE_TEMPLATES.json':dict(jobs=jobs),'WAVE50_TARGET_CPU_PASSED.json':dict(passed=True,source_count=len(freeze),CPU_record_in_progress=True)}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  save('SOURCE_FREEZE.json',values['SOURCE_FREEZE.json'])
  code=r'''from pathlib import Path
import sys,json,time,torch,ast,contextlib,io,inspect
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once as own
own.verify();own.wait_existing();p=own.source();assert own.D==D and own.R==D/'reports' and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
import test_wave50_entry_target_cpu as test
capture=io.StringIO()
with contextlib.redirect_stdout(capture):test.main(str(p))
v=json.loads(capture.getvalue());assert v['passed'] and v['no_CUDA_initialized']
missing=[]
for name in ('train_wave50_entry_resume_ppo.py','train_wave50_entry_fresh_preflight_ppo.py'):
 text=(own.CODE/name).read_text();tree=ast.parse(text)
 for node in ast.walk(tree):
  if isinstance(node,ast.For) and isinstance(node.target,ast.Name) and node.target.id=='name' and isinstance(node.iter,ast.Tuple):
   for a in node.iter.elts:
    if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.endswith(('.py','.json')) and not (own.CODE/a.value).is_file():missing.append(a.value)
 assert "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in text
 assert 'wave50_entry_runtime' in text and 'wave50_entry_full_checkpoint' in text
assert not missing,missing
fresh=(own.CODE/'probe_wave50_entry_fresh_process_full_resume.py').read_text();assert 'no_optional_logger_save_requested=True' in fresh and 'same_entry_identity_restored_exact' in fresh
assert "'--seed','20260928'" in inspect.getsource(own.fresh_resume)
runtime=own.runtime();assert runtime['RM_WAVE50_INITIAL_ADMISSION']=='verified_G3_to_independent_WAVE50_entry' and runtime['RM_KEEP_STD']=='1'
assert not torch.cuda.is_initialized();result=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),source_checkpoint=own.s.q.base.checkpoint(p),proof=v,source_snapshot_lists_all_exist=True,actual_import_main_Popen_worker_roots_match=True,old384_source_immutable_preserved=True,explicit_seed_fresh_zero_steps_guards_preserved=True,actual_CUDA_SDK_native_PPO_fresh_formal_pending=True,no_GPU_or_budget_write=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('ROOT_TOKEN',repr(ROOT))
  result=run(n,code);save('ENTRY_TARGET_CPU_PASSED.json',result)
  print(json.dumps(dict(root=ROOT,source_count=len(freeze),target_CPU_passed=True,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True,only_unexecuted_step_can_continue=True));raise
