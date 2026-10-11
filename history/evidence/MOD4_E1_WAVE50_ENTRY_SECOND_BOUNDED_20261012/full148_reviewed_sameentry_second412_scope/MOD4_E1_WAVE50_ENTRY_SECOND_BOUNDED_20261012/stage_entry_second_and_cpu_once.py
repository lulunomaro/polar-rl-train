"""Admit a new same50+entry root. Reuse every completed GPU contract by exactSHA."""
from entry_second_io import *

def main():
 assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),new_same_entry_second_scope=True,no_old_once_replay=True))
 decision=json.loads((ENTRY_LOCAL/'reports/ENTRY148_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['full_four_cases_complete_errorfree_and_raw_reviewed'] and decision['allow_one_second_bounded_same50_entry_scope_exposure_block_under005']
 files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file()};assert len(files)==2
 for name,raw in files.items():compile(raw,name,'exec')
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
  number=149
  while any(any('episode-d3-'+str(number)+'-' in name for name in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listings]);save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)
  boundary=run(n,r'''from pathlib import Path
import sys,json,hashlib,torch,time,shutil,fcntl
old=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);B=Path(B_TOKEN);sys.path[:0]=[str(old),str(old/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once_v2 as previous
from wave50_entry_source_guard import verify_original_records
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();verify_original_records(previous.s.q,old)
st=j(old/'reports/E1_STATE.json');passed=j(old/'reports/e1_WAVE50_entry_observation_PASSED.json');assert st['phase']=='E1_WAVE50_entry_saved_review_ready' and st['child'] is None and passed['checkpoint']['sha256']==SHA_TOKEN and len(passed['unique_completed_segment'])==1
for loc in (st['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=90749332)):
 a=previous.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
source=Path(SOURCE_TOKEN);info=previous.fullsave(source);assert h(source)==SHA_TOKEN and info['finite_tensors']==102
assert not previous.trainers();b=j(B);assert b['active_segment'] is None and not j(previous.s.q.ctl.STATE_PATH).get('active_training') and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>1920
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',previous.s.q.P/'autonomy_controller.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
freeze=j(old/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==410
for name,sha in freeze.items():assert h(old/name)==sha
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;disk=shutil.disk_usage(old)
prior1800=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012');priorbytes=sum(p.stat().st_size for p in prior1800.rglob('*') if p.is_file());required=2*priorbytes+2*1024**3
assert mem>8*1024**3 and disk.free>required and not D.exists(),dict(free=disk.free,required=required,prior_actual_completed_1800s_wholeoutput=priorbytes)
reuse=[]
for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','WAVE50_NATIVE_SCOPE_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json','WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'):
 p=old/'reports'/name;a=j(p);reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
 if 'checkpoint' in a:
  ck=Path(a['checkpoint']['path']);assert h(ck)==a['checkpoint']['sha256'];reuse.append(dict(path=str(ck),bytes=ck.stat().st_size,sha256=h(ck),discarded_preflight=True,large_index_only=True))
 if 'path' in a and 'sha256' in a:
  p=Path(a['path']);assert h(p)==a['sha256'];reuse.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),large_index_only=p.stat().st_size>8000000))
fresh=old/'fresh_process_resume/FRESH_PROCESS_SAME_WAVE50_FULL_RESUME_PASSED.json';a=j(fresh);assert a['passed'] and a['actual_same_WAVE50_terrain_command_private_CPUCUDA_disk_roundtrip_exact'] and a['actual_control_steps']==a['actual_additional_PPO_updates']==0
reuse.append(dict(path=str(fresh),bytes=fresh.stat().st_size,sha256=h(fresh)));reuse.extend(j(old/'reports/REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices'])
before=B.read_bytes();D.mkdir();(D/'reports').mkdir()
for name,sha in freeze.items():p=D/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,p);assert h(p)==sha
for name in ('REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','WAVE50_FOUR_CASE_TEMPLATES.json','SOURCE_SELECTED.json','OWN369_ACTUAL_SOURCE_BOUNDARY.json','COMPLETE147_ENTRY_AXIS_DECISION.json'):shutil.copy2(old/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),selected=info,oldfreeze=freeze,old_own_PASSED=passed,actual_old_parent_guardian_child_exit=True,two_fcntl_free=locks,canonical_SHA=h(B),remaining_seconds=b['remaining_training_seconds'],reused=dict(passed=True,same50_entry_geometry_command_reset_reward_LR_DR=True,actual_original_file_indices=reuse,no_SDK_native_small_big_fresh_clock_replay=True),resources=dict(RAM_available_bytes=mem,disk_free_bytes=disk.free,prior_completed1800s_wholeoutput_bytes=priorbytes,required_bytes=required),no_GPU_or_budget_write=True)))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(SOURCE_SHA)).replace('SOURCE_TOKEN',repr(SOURCE)))
  save('OLD410_ACTUAL_SOURCE_BOUNDARY.json',boundary);freeze=dict(boundary['oldfreeze'])
  with n.open_sftp() as f:
   for name,raw in files.items():assert name not in freeze;io.put(f,ROOT+'/'+name,raw);freeze[name]=H(raw)
   assert len(freeze)==412
   values={'SOURCE_FREEZE.json':dict(epoch=time.time(),sha256=freeze,all410_old_bytes_exact=True,new_files=list(files),only_truthful_manifest_and_second_sameentry_controller_changed=True),'MATCHED_SOURCE_SELECTED.json':boundary['selected'],'COMPLETE148_SCOPE_DECISION.json':decision,'REUSED_ACTUAL_CONTRACTS.json':boundary['reused'],'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode());save(name,value)
  result=run(n,r'''from pathlib import Path
import sys,json,torch,time,hashlib,ast,copy
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_second_bounded_once as own
from retention_command_state import validate,same
from wave50_entry_current_state_v2 import validate_complete_entry,KEY
own.boundary();source=own.source();info=own.prior.fullsave(source);ck=torch.load(source,map_location='cpu',weights_only=False);assert info['sha256']==SHA_TOKEN and info['finite_tensors']==102 and ck['E1_terrain_state']['profile']=='mod4_G4_CAD_derived_50mm_entry_v1' and ck['E1_WAVE50_initial_source_sha256']==own.ORIGINAL35_SHA
validate_complete_entry(ck,20000)
state=ck['E1_retained_flat_command_state'];validate(state,20000);p=D/'reports/SAME_ENTRY_PRIVATE_COMMAND_CPU_FIXTURE.pt';torch.save(state,p);loaded=torch.load(p,map_location='cpu',weights_only=False);validate(loaded,20000);assert same(state,loaded)
rejected=[]
for kind in ('entry_map_sha256','entry_origin_sha256','entry_assignment_sha256'):
 wrong=copy.deepcopy(ck);wrong['E1_terrain_state'][kind]='0'*64
 try:validate_complete_entry(wrong,20000)
 except AssertionError:rejected.append(kind)
 else:raise AssertionError('Wrong entry identity accepted:'+kind)
assert len(rejected)==3 and own.INIT_SHA!=own.ORIGINAL35_SHA and own.prior.SOURCE_SHA==own.ORIGINAL35_SHA
assert own.prior.D==own.D==D and own.prior.CODE==D/'isaac/mod4' and own.prior.s.D==D and own.prior.s.R==D/'reports'
constants=str(own.prior.train.__code__.co_consts);assert 'train_wave50_entry_same_scope_resume_ppo.py' in constants and 'same_entry_identity_restored_exact' in constants and '--seed' in constants and '20260928' in constants
runtime=own.prior.runtime();assert not any(n.endswith('INITIAL_ADMISSION') for n in runtime) and runtime['RM_KEEP_STD']=='1'
old=D/'isaac/mod4/train_wave50_entry_resume_ppo_v2.py';new=D/'isaac/mod4/train_wave50_entry_same_scope_resume_ppo.py';a=old.read_text();b=new.read_text()
expected=a.replace("manifest['explicit_G3_to_WAVE50_geometry_transition']=True","manifest['explicit_G3_to_WAVE50_geometry_transition']=False").replace("manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=True","manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=False").replace("    manifest['active_expert']='E1_WAVE50'","    manifest['same_WAVE50_entry_geometry_command_fullrestore_continuation']=True\n    manifest['active_expert']='E1_WAVE50'")
assert b==expected and "_write_dynamic(torch.arange(env.num_envs,device=env.device))" in b
assert 'train_wave50_entry_same_scope_resume_ppo.py' in str(own.prior.guardian.__code__.co_consts)
assert len(own.read(own.R/'SOURCE_FREEZE.json')['sha256'])==412 and not torch.cuda.is_initialized()
result=dict(epoch=time.time(),passed=True,root=str(D),source_count=412,source_checkpoint=info,same50_entry_full_D0D7_actorcriticstdoptimizer_private_command_CPU_schema_verified=True,original35_and129_lineage_preserved=True,all410_bytes_exact=True,worker_only_truthful_same_scope_manifest_disclosure=True,import_main_Popen_same_worker_root_exact=True,guardian_own_worker_name_exact=True,source_snapshot_old_required_paths_reused=True,CPU_private_command_disk_roundtrip_exact=True,strict_wrong_entry_identity_rejected=rejected,CPU_fixture=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()),no_CUDA_initialized=True,new_SDK_native_small_big_fresh_not_required_same_scope_exact_reuse=True)
(D/'reports/ENTRY_SECOND_TARGET_CPU_PASSED.json').write_text(json.dumps(result,indent=2));own.verify();print(json.dumps(result))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('SHA_TOKEN',repr(SOURCE_SHA)))
  save('ENTRY_SECOND_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(root=ROOT,CPU_passed=True,source_count=412,candidate_number=number,no_GPU_or_dispatch_yet=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_SECOND_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_step_may_continue=True,no_GPU_or_old_once_replay=True));raise
