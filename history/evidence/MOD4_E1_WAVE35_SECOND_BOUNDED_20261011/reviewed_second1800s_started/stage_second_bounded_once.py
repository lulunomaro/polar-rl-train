from second_io import *
def main():
 assert not (R/'SECOND_STAGE_STARTED.json').exists()
 save('SECOND_STAGE_STARTED.json',dict(epoch=time.time(),CPU_only=True,new_block_under_reviewed142_and005=True))
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    listings.append((host,path,fs.listdir(path)))
  number=143
  while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
  unused=dict(epoch=time.time(),number=number,actual_both_hosts_queue_results_jobs_unused=[dict(host=host,path=path,matches=[x for x in names if 'episode-d3-'+str(number)+'-' in x]) for host,path,names in listings])
  save('SECOND_CANDIDATE_UNUSED_ACTUAL.json',unused)
  decision=json.loads((PRIOR/'reports/WAVE142_COMPLETE_SCOPE_DECISION.json').read_bytes())
  assert decision['allow_one_additional_bounded_same_scope_block_under005'] and decision['own_checkpoint_SHA']==SOURCE_SHA
  own=json.loads(sorted((PRIOR/'reports').glob('WAVE_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());assert own['passed'] and own['closeout_ready'] and own['own_checkpoint']['sha256']==SOURCE_SHA
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,shutil,fcntl
old=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);B=Path(BUDGET_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path[:0]=[str(old),str(old/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave35_exposure_005_once as previous
m=previous.m;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
previous.verify_original_records(m.s.q,old)
previous.exited(old,'E1_WAVE35_exposure_005_saved_review_ready','e1_WAVE35_exposure_005_observation_PASSED.json',SHA_TOKEN)
assert not j(m.s.q.ctl.STATE_PATH).get('active_training') and not m.trainers()
row=j(old/'reports/e1_WAVE35_exposure_005_observation_PASSED.json');p=Path(row['checkpoint']['path']);assert str(p)==SOURCE_TOKEN and h(p)==SHA_TOKEN and m.fullsave(p)['finite_tensors']==102
run=Path(row['run']);manifest=j(run/'run_manifest.json');freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==368 and manifest['source_map']==freeze['sha256']
assert j(run/'latest_complete.json')['pid']==row['own_PID_bound_receipt']['pid'] and row['actual_updates']==98
for name,sha in manifest['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
for name,sha in freeze['sha256'].items():assert h(old/name)==sha
startup={};proof=j(old/'reports/REUSED_ACTUAL_CONTRACTS.json');assert proof['passed']
for item in proof['actual_original_file_indices']:assert h(Path(item['path']))==item['sha256']
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
 q=run/name;startup[name]=dict(path=str(q),bytes=q.stat().st_size,sha256=h(q));assert j(q)['source_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
t=j(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');c=j(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')
assert t['terrain_state_restored_exact'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact']
assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=True))
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024;disk=shutil.disk_usage(old)
assert mem>8*1024**3 and disk.free>8*1024**3 and not D.exists()
D.mkdir();(D/'reports').mkdir()
for name,sha in freeze['sha256'].items():q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,q);assert h(q)==sha
for name in ('E1_PLANNED_BEHAVIOR_PUBLISHED.json','G3_BEHAVIOR_PACKAGE_READY.json','REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md','REUSED_ACTUAL_CONTRACTS.json'):
 shutil.copy2(old/'reports'/name,D/'reports'/name)
assert before==B.read_bytes() and not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,oldfreeze=freeze,selected=previous.fullsave(p),own_source_run_manifest=manifest,old_parent_guardian_child_exited=True,unique_completed_segment=row['unique_completed_segment'],original_actual_same_scope_startup_indices=startup,resources=dict(RAM_bytes=mem,disk_free_bytes=disk.free),locks=locks,canonical_SHA=h(B),remaining_seconds=b['remaining_training_seconds'],no_GPU_or_budget_write=True)))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(SOURCE_SHA)).replace('SOURCE_TOKEN',repr(SOURCE)))
  save('SECOND_OLD_ACTUAL_BOUNDARY_AND_REUSE.json',v)
  freeze=dict(v['oldfreeze']['sha256']);wrapper=D/'payload/supervise_wave35_second_bounded_once.py';raw=wrapper.read_bytes();compile(raw,wrapper.name,'exec');assert wrapper.name not in freeze;freeze[wrapper.name]=H(raw)
  bound=dict(epoch=time.time(),seconds=1800,reviewed_same_scope_continuation_source=SOURCE_SHA,second_of_maximum_two_same_repair_blocks=True,no_third_or_geometry_increase=True,no_preflight_clock_replay=True,new_budget_seconds=0)
  values={'SOURCE_FREEZE.json':dict(candidate_root=ROOT,sha256=freeze,old368_allbytes_exact=True,new_files=1,independent_expert='E1_WAVE'),'SOURCE_SELECTED.json':v['selected'],'COMPLETE142_SCOPE_DECISION.json':decision,'SECOND_BOUNDING_DECISION.json':bound,'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused,'OWN368_FINAL_CPU_VERIFIED.json':own,'OWN368_ACTUAL_BOUNDARY_AND_REUSE.json':v}
  with n.open_sftp() as f:
   io.put(f,ROOT+'/'+wrapper.name,raw)
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  save('SECOND_SOURCE_FREEZE.json',values['SOURCE_FREEZE.json']);save('SECOND_BOUNDING_DECISION.json',bound)
  cpu=run(n,r'''from pathlib import Path
import sys,json,time,torch,ast,inspect
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave35_second_bounded_once as own
own.verify();own.boundary();p=own.source();a=torch.load(p,map_location='cpu',weights_only=False);z=torch.load(p,map_location='cpu',weights_only=False);checked=0
for group in ('actor_state_dict','critic_state_dict'):
 for key,v in a[group].items():assert torch.equal(v,z[group][key]) and v.data_ptr()!=z[group][key].data_ptr();checked+=1
x=next(iter(a['actor_state_dict'].values()));other=next(iter(z['actor_state_dict'].values()));keep=other.clone();x.add_(1);assert torch.equal(other,keep)
assert own.m.s.q.base.sha(p)==own.SOURCE_SHA and own.m.D==D and own.m.R==D/'reports' and own.m.CODE==D/'isaac/mod4' and own.m.s.D==D and own.m.s.R==D/'reports'
runtime=own.m.runtime();assert float(runtime.get('RM_EPISODE_S','20'))==20 and runtime['RM_KEEP_STD']=='1' and all(k not in runtime for k in ('RM_E1_INITIAL_ADMISSION','RM_E1_G3_INITIAL_ADMISSION','RM_E1_COMMAND_RETENTION_INITIAL_ADMISSION'))
assert own.m.train.__globals__ is own.m.__dict__
matched=(D/'supervise_e1_command_retention_matched_once.py').read_text();assert "assert terrain['terrain_state_restored_exact']" in matched and "v['predecessor_command_state_restored_exact']" in matched
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_only=True,root=str(D),source_count=369,finite_tensors=102,source=own.fullsave(p),independent_actorcritic_tensors_checked=checked,CPU_copy_mutation_not_other_copy_or_source=True,actual_import_worker_Popen_root_same=True,same_G3_samecommand_complete_CUDA_restore_required_on_own_startup=True,reuse_actual_SDK_native_small_big_fresh_clock_DR_exact=True,no_preflight_replay=True,seconds=1800,candidate_number=own.read(D/'reports/CANDIDATE_JOB_UNUSED_ACTUAL.json')['number'],no_new_budget_seconds=0)
(D/'reports/SECOND_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('SECOND_TARGET_CPU_PASSED.json',cpu);print(json.dumps(dict(root=ROOT,CPU_passed=True,seconds=1800,source_count=369,candidate_number=number,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_STAGE_REJECTED_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_step_may_continue=True,no_old_GPU_or_once_replay=True));raise
