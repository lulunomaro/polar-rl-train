from route_repair_io import *

def main():
 assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),old426_allbytes_immutable_newroute_only=True))
 files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==13
 for name,raw in files.items():compile(raw,name,'exec')
 decision=json.loads((PRIOR/'reports/CANDIDATE151_COMPLETE_SCOPE_DECISION.json').read_bytes());decision.update(default_source_SHA=SOURCE_SHA,new_route_only_scope_authorized_by004005=True,Wave_inward_limit_m=4.,outward_lateral_nonWave_limit_m=2.)
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
  number=152
  while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listings]);save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  boundary=run(n,r'''from pathlib import Path
import json,sys,torch,hashlib,time,shutil,fcntl
OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_second_bounded_once as previous
from wave50_direction_source_guard import verify_original_records
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();verify_original_records(previous.prior.s.q,OLD)
state=j(OLD/'reports/E1_STATE.json');passed=j(OLD/'reports/e1_WAVE50_direction_second_bounded_observation_PASSED.json');assert state['phase']=='E1_WAVE50_direction_second_bounded_saved_review_ready' and state['child'] is None and passed['checkpoint']['sha256']=='830f46548d3206bded67f9f244f085b7dbbe8f2c35f90faa84c983c4ba3c94c8' and len(passed['unique_completed_segment'])==1
for loc in (state['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=92072342)):
 a=previous.prior.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not previous.prior.trainers();B=previous.prior.s.q.ctl.CANONICAL;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and not j(previous.prior.s.q.ctl.STATE_PATH).get('active_training') and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1020
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',previous.prior.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
source=Path(SOURCE_TOKEN);info=previous.prior.inherited.fullsave(source);assert h(source)==SHA_TOKEN and info['finite_tensors']==102
f=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==426
for name,sha in f.items():assert h(OLD/name)==sha
reference=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_EPISODE_DIRECTION_REVIEWED_20261012');ref_freeze=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];reference_bytes=sum((reference/k).stat().st_size for k in ref_freeze);current_bytes=sum((OLD/k).stat().st_size for k in f);whole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());extra_route_state_margin=2*660000*20;required=2*whole+2*1024**3+2*max(0,current_bytes-reference_bytes)+extra_route_state_margin
free=shutil.disk_usage(OLD).free;mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024
assert free>required and mem>8*1024**3 and not D.exists(),dict(free=free,required=required,reference300_whole=whole)
reuse=j(OLD/'reports/REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']
for row in reuse:assert h(Path(row['path']))==row['sha256']
D.mkdir();(D/'reports').mkdir()
for name,sha in f.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json'):shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=f,source=info,old426_own_PASSED=passed,actual_old_parent_guardian_child_exit=True,two_fcntl_free=locks,canonical_SHA=h(B),no_budget_write=True,resources=dict(durable_free_bytes=free,required_bytes=required,reference300_whole_bytes=whole,reference300_source_bytes=reference_bytes,current_source_bytes=current_bytes,route_state_double20_save_margin_bytes=extra_route_state_margin,RAM_available_bytes=mem),reused=dict(actual_original_file_indices=reuse,only_unchanged_geometry_clock_DR_hardware_reused=True,new_route_SDK_native_PPO_fresh_contracts_required_once=True))))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('SOURCE_TOKEN',repr(SOURCE)).replace('SHA_TOKEN',repr(SOURCE_SHA)))
  save('OLD426_BOUNDARY_SOURCE35_RESOURCE_ACTUAL.json',boundary);freeze=dict(boundary['oldfreeze'])
  values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,all426_oldbytes_exact=True,new_files=list(files),only_new_route_lifecycle_axis=True),'COMPLETE151_ROUTE_AXIS_DECISION.json':decision,'REUSED_ACTUAL_CONTRACTS.json':boundary['reused'],'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused}
  with n.open_sftp() as f:
   for name,raw in files.items():assert name not in freeze;io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  for name,value in values.items():
   if name!='CANDIDATE_JOB_UNUSED_ACTUAL.json':save(name,value)
  result=run(n,r'''from pathlib import Path
import sys,torch,json,time,ast
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_CPU_reviewed_once as own
from test_wave50_route_target_cpu import verify
own.wait_existing();source=own.source();proof=verify(D,str(source));assert proof['passed'] and proof['no_CUDA_initialized']
assert own.D==D and own.CODE==D/'isaac/mod4' and own.s.D==D and own.s.R==D/'reports'
const=str(own.prior.train.__code__.co_consts);assert 'train_wave50_route_resume_ppo.py' in const and 'train_wave50_route_fresh_preflight_ppo.py' in const and '20260928' in const
assert 'train_wave50_route_resume_ppo.py' in str(own.prior.guardian.__code__.co_consts)
for name in ('train_wave50_route_resume_ppo.py','train_wave50_route_fresh_preflight_ppo.py','probe_wave50_route_fresh_process_full_resume.py'):
 s=(own.CODE/name).read_text();tree=ast.parse(s)
 for node in ast.walk(tree):
  if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
   for item in node.iter.elts:
    if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (own.CODE/item.value).is_file(),item.value
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=len(own.prior.read(own.R/'SOURCE_FREEZE.json')['sha256']),initial_source_checkpoint=own.prior.inherited.fullsave(source),proof=proof,old426_allbytes_exact=True,new_Wave_inward4m_otheraxes_and_nonWave2m_exact=True,import_main_Popen_guardian_worker_roots_exact=True,SDK_native_CPUCUDA_PPO_fresh_formal_pending=True,no_GPU_or_budget_write=True)
(own.R/'WAVE50_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('ROUTE_LIFECYCLE_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(passed=True,root=ROOT,source_count=len(freeze),actual_target_CPU_passed=True,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_substeps_may_continue_no_GPU_replay=True));raise
