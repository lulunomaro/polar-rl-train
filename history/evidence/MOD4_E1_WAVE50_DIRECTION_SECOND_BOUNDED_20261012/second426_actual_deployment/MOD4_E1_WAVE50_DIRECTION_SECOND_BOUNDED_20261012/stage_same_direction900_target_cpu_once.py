"""Actual426 CPU admission; resource reference is not a geometry/state admission."""
from wave_direction_second_io import *
def main():
 save('STAGE_STARTED.json',dict(epoch=time.time(),same_direction_second900_scope=True,no_old_once_replay=True))
 files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==2
 for name,raw in files.items():compile(raw,name,'exec')
 decision=json.loads((R/'COMPLETE150_SCOPE_DECISION.json').read_bytes());resource=json.loads((PRIOR/'reports/NEXT_DIRECTION_900S_RESOURCE_REFERENCE_ACTUAL.json').read_bytes());assert resource['resource900_reference_guard_passed']
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
  number=151
  while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listings]);save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  v=run(n,r'''from pathlib import Path
import json,sys,torch,hashlib,time,shutil,fcntl,numpy as np
OLD=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);sys.path[:0]=[str(OLD),str(OLD/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as previous
from wave50_direction_source_guard import verify_original_records
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();verify_original_records(previous.s.q,OLD)
st=j(OLD/'reports/E1_STATE.json');passed=j(OLD/'reports/e1_WAVE50_direction_observation_PASSED.json');assert st['phase']=='E1_WAVE50_direction_saved_review_ready' and st['child'] is None and passed['checkpoint']['sha256']==SHA_TOKEN and len(passed['unique_completed_segment'])==1
for loc in (st['owner'],j(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=91780234)):
 a=previous.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
assert not previous.trainers();B=previous.s.q.ctl.CANONICAL;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and not j(previous.s.q.ctl.STATE_PATH).get('active_training') and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1020
locks=[]
for path in (B.parent/'native_floor_supervisor.lock',previous.s.q.P/'autonomy_controller.lock'):
 with path.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_fcntl_free=True))
source=Path(SOURCE_TOKEN);info=previous.fullsave(source);assert h(source)==SHA_TOKEN and info['finite_tensors']==104
freeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==424
for name,sha in freeze.items():assert h(OLD/name)==sha
reference=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011');ref_freeze=j(reference/'reports/SOURCE_FREEZE.json')['sha256'];reference_source_bytes=sum((reference/k).stat().st_size for k in ref_freeze);current_source_bytes=sum((OLD/k).stat().st_size for k in freeze)
refwhole=sum(p.stat().st_size for p in reference.rglob('*') if p.is_file());required=2*refwhole+2*1024**3+2*max(0,current_source_bytes-reference_source_bytes)
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;free=shutil.disk_usage(OLD).free;assert free>required and mem>8*1024**3 and not D.exists(),dict(free=free,required=required,actual900_refwhole=refwhole,source_asset_size_delta=current_source_bytes-reference_source_bytes)
reuse=[]
for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','WAVE50_NATIVE_SCOPE_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json','WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'):
 p=OLD/'reports'/name;a=j(p);reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
 if 'checkpoint' in a:
  p=Path(a['checkpoint']['path']);assert h(p)==a['checkpoint']['sha256'];reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),discarded_preflight=True,large_index_only=True))
 if 'path' in a and 'sha256' in a:
  p=Path(a['path']);assert h(p)==a['sha256'];reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),large_index_only=True))
reuse.extend(j(OLD/'reports/REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices'])
D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json','COMPLETE149_DIRECTION_AXIS_DECISION.json'):shutil.copy2(OLD/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,oldfreeze=freeze,selected=info,old_own_passed=passed,actual_old_parent_guardian_child_exit=True,two_fcntl_free=locks,canonical_SHA=h(B),no_budget_write=True,resources=dict(actual_free_bytes=free,required_bytes=required,actual900_ref_wholeoutput_bytes=refwhole,actual_source_bytes=current_source_bytes,reference_source_bytes=reference_source_bytes,extra_asset_delta_double_budgeted=True,RAM_available_bytes=mem,matching_reference_only_no_geometry_admission=True,original1800_guard_failure_retained_no_evidence_deleted=True),reused=dict(passed=True,same50_entry_direction_geometry_command_reset_reward_LR_DR=True,actual_original_file_indices=reuse,no_SDK_native_small_big_fresh_clock_replay=True))))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(SOURCE_SHA)).replace('SOURCE_TOKEN',repr(SOURCE)))
  save('OLD424_BOUNDARY_AND_SECOND900_RESOURCES_ACTUAL.json',v);freeze=dict(v['oldfreeze'])
  values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,all424_oldbytes_exact=True,new_files=list(files),only_same_scope_manifest_and_unique900_controller=True),'MATCHED_SOURCE_SELECTED.json':v['selected'],'COMPLETE150_SCOPE_DECISION.json':decision,'REUSED_ACTUAL_CONTRACTS.json':v['reused'],'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused,'OLD424_SOURCE_BOUNDARY.json':v}
  with n.open_sftp() as f:
   for name,raw in files.items():assert name not in freeze;io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  for name,value in values.items():
   if name!='CANDIDATE_JOB_UNUSED_ACTUAL.json' and name!='COMPLETE150_SCOPE_DECISION.json':save(name,value)
  result=run(n,r'''from pathlib import Path
import sys,json,torch,time,copy,ast,tempfile,hashlib
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_second_bounded_once as own
from wave50_direction_state import KEY,validate
from retention_command_state import validate as validate_command,same
own.boundary();source=own.source();info=own.prior.fullsave(source);ck=torch.load(source,map_location='cpu',weights_only=False);assert info['sha256']==SHA_TOKEN and info['finite_tensors']==104 and ck['E1_WAVE50_initial_source_sha256']==own.ORIGINAL35_SHA
validate(ck[KEY],20000);state=ck['E1_retained_flat_command_state'];validate_command(state,20000);rejects=[]
with tempfile.TemporaryDirectory() as tmp:
 path=Path(tmp)/'same_direction_CPU_fixture.pt';torch.save(ck,path);assert own.prior.fullsave(path)['finite_tensors']==104
 for field in ('assignment_sha256','entry_map_sha256','entry_origin_sha256','profile','bound_episode'):
  bad=copy.deepcopy(ck)
  if field=='bound_episode':bad[KEY][field]+=1
  else:bad[KEY][field]='wrong' if field=='profile' else '0'*64
  torch.save(bad,path)
  try:own.prior.fullsave(path)
  except AssertionError:rejects.append(field)
  else:raise AssertionError('Wrong direction accepted '+field)
 p=Path(tmp)/'command.pt';torch.save(state,p);assert same(state,torch.load(p,map_location='cpu',weights_only=False))
clone=copy.deepcopy(ck);tensor_count=0
def tensors(v):
 if torch.is_tensor(v):yield v
 elif isinstance(v,dict):
  for x in v.values():yield from tensors(x)
 elif isinstance(v,(list,tuple)):
  for x in v:yield from tensors(x)
for group in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
 for a,b in zip(tensors(ck[group]),tensors(clone[group])):assert a.data_ptr()!=b.data_ptr() and torch.equal(a,b);tensor_count+=1
assert own.prior.D==own.D==D and own.prior.CODE==D/'isaac/mod4' and own.prior.s.D==D and own.prior.s.R==D/'reports'
constants=str(own.prior.train.__code__.co_consts);assert own.ENTRY in constants and '--seed' in constants and '20260928' in constants and 'predecessor_direction_state_restored_exact' in constants
assert own.ENTRY in str(own.prior.guardian.__code__.co_consts)
assert not any(k.endswith('INITIAL_ADMISSION') for k in own.runtime()) and own.runtime()['RM_KEEP_STD']=='1'
worker=(own.prior.CODE/own.ENTRY).read_text();assert "manifest['new_episode_direction_axis']=False" in worker and "manifest['explicit_G3_to_WAVE50_geometry_transition']=False" in worker and "manifest['same50_entry_direction_fullstate_continuation']=True" in worker
assert "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in worker;ast.parse(worker)
for node in ast.walk(ast.parse(worker)):
 if isinstance(node,ast.For) and isinstance(node.iter,ast.Tuple) and 'shutil.copy2(Path(__file__).parent' in ast.unparse(node):
  for item in node.iter.elts:
   if isinstance(item,ast.Constant) and isinstance(item.value,str):assert (own.prior.CODE/item.value).is_file(),item.value
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,root=str(D),source_count=426,source_checkpoint=info,full_source_same50_entry_direction_D0D7_oldnamed_private_CPU_schema_verified=True,independent_actor_critic_optimizer_storage_tensors=tensor_count,strict_rejected_direction_identities=rejects,private_command_CPU_disk_fixture_exact=True,actual_CUDA_fullresume_reserved_for_new_startup=True,source35_b026_ancestor129_identity_preserved=True,old424_allbytes_exact=True,import_main_Popen_guardian_worker_root_exact=True,truthful_same_scope_manifest_only_worker_change=True,explicit_seed20260928=True,no_CUDA_initialized=True)
(D/'reports/DIRECTION_SECOND_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.verify();print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(SOURCE_SHA)))
  save('DIRECTION_SECOND_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(root=ROOT,source_count=426,target_CPU_passed=True,chosen_seconds=900,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True,original_sources_and_resource_refusal_preserved=True));raise
