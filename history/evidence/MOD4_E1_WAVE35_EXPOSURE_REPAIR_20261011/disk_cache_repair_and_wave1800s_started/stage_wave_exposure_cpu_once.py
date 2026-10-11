"""New output root/005 controller and actual CPU admission, no GPU or budget write."""
from wave_io import *
def main():
 assert not (R/'WAVE_STAGE_STARTED.json').exists()
 save('WAVE_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='WAVE35-005-DURATION-1800-NEWROOT-01',CPU_only=True))
 n,w=io.connect_both()
 try:
  checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-142-' in x];assert not matches,(host,path,matches)
    checks.append(dict(host=host,path=path,matches=matches))
  unused=dict(epoch=time.time(),number=142,actual_both_hosts_queue_results_jobs_unused=checks)
  decision=dict(epoch=time.time(),approved_under_004005_human_bounded_retraining=True,expert='E1_WAVE',seconds=1800,only_learning_exposure_duration_axis=True,
   source_SHA=SOURCE_SHA,not_old_unqualified_Wave_or_CURB_warmstart=True,old_actual_controls=144,old_actual_simulated_seconds=1.44,
   full_wave_span_m=2.4064227271861265,old_maximum_gentle_distance_m=.432,unchanged_command_resample_s=[12,16],unchanged_episode_s=20,
   unchanged_geometry_commands_reset_reward_LR_DR_hardware=True,max_two_same_scope_blocks_then_full_review=True,
   first_existing_math_scope_already_fully_admitted_no_new_SDK_native_PPO_clock=True,source3c97_new_independent_output=True,
   exposure_is_testable_hypothesis_not_causal_proof_or_graduation=True,no_automatic_more_training_or_50mm=True,no_new_budget_seconds=0)
  save('WAVE_EXPOSURE_DURATION_DECISION.json',decision);save('WAVE_CANDIDATE142_UNUSED_ACTUAL.json',unused)
  v=run(n,r'''from pathlib import Path
import sys,json,time,hashlib,torch,shutil,fcntl
old=Path(OLD_TOKEN);D=Path(ROOT_TOKEN);B=Path(BUDGET_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(old));sys.path.insert(0,str(old/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_wave_isolated_revision004_once as inherited
m=inherited.m;before=B.read_bytes();b=j(B);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
assert not j(m.s.q.ctl.STATE_PATH).get('active_training') and not m.trainers()
CURB=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011')
exits=[]
for root,label,phase,sha in ((old,'e1_wave_G3_isolated_observation_PASSED.json','E1_WAVE_G3_isolated_saved_review_ready','2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284'),(CURB,'e1_CURB20_direction_exposure_matched_observation_PASSED.json','E1_CURB20_direction_exposure_matched_saved_review_ready','7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43')):
 st=j(root/'reports/E1_STATE.json');row=j(root/'reports'/label);assert st['phase']==phase and st['child'] is None and row['checkpoint']['sha256']==sha
 assert [x for x in b['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']]==row['unique_completed_segment']
 for loc in (st['owner'],j(root/'reports/E1_GUARDIAN_STARTED.json'),row['own_PID_bound_receipt']):
  a=m.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc.get('start_ticks',a['start_ticks']);exits.append(dict(locator=loc,actual=a))
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
base=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_EPISODE_REVIEWED_20261010');pre=j(base/'reports/E1_COMPLETE_PPO_PREFLIGHT_PASSED.json');indices=[]
for row in pre['native'].values():
 p=Path(row['path']);assert h(p)==row['sha256'] and row['actual_parameter_ground_callback_scope_passed'];indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
for key in ('small','big'):
 row=pre[key];p=Path(row['checkpoint']['path']);assert h(p)==row['checkpoint']['sha256'] and row['discarded_preflight']
 assert row['actual_updates']==(2 if key=='small' else 4) and row['health']['control_steps']==(48 if key=='small' else 96)
 assert [x for x in b['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']]==row['unique_completed_segment']
 assert m.learning_health_pass(row['health']);indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),large_original_index_only=True))
run=Path(j(old/'reports/e1_wave_G3_isolated_observation_PASSED.json')['run']);startup={}
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
 p=run/name;v=j(p);assert v['source_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e';startup[name]=v
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
t=startup['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert t['terrain_state_restored_exact'] and not t['explicit_G2_to_G3_geometry_transition'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact']
c=startup['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'];assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['saved_source_episode_plus_one_verified'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact']
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==366 and not D.exists()
mem={x.split(':')[0]:int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemAvailable:','SwapFree:'))}
disk=shutil.disk_usage(old);assert mem['MemAvailable']>8*1024**3 and disk.free>12*1024**3
D.mkdir();(D/'reports').mkdir()
for name,sha in freeze['sha256'].items():
 p=old/name;assert h(p)==sha;q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json','G3_BEHAVIOR_PACKAGE_READY.json','REVISION_APPROVED.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md'):
 shutil.copy2(old/'reports'/name,D/'reports'/name)
assert B.read_bytes()==before and not torch.cuda.is_initialized()
proof=dict(epoch=time.time(),passed=True,same35mm_same_commands_same_reset_and_all_learning_modules_exact=True,actual_original_file_indices=indices,
 actual_complete_small_big=pre,actual_old366_same_G3_same_command_fresh_environment_startup=startup,
 old366_and_current424_actual_exits_unique_closed=exits,old366_all_source_SHA_exact=True,new_output_root=str(D),
 resource_available_RAM_bytes=mem['MemAvailable'],disk_free_bytes=disk.free,canonical_SHA=h(B),no_GPU_or_budget_write=True)
print(json.dumps(dict(proof=proof,oldfreeze=freeze)))
'''.replace('OLD_TOKEN',repr(OLD)).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)))
  save('WAVE_ACTUAL_SCOPE_REUSE_VERIFIED.json',v['proof']);freeze=dict(v['oldfreeze']['sha256'])
  with n.open_sftp() as f:
   for p in sorted((D/'payload').glob('*.py')):
    raw=p.read_bytes();compile(raw,p.name,'exec');assert p.name not in freeze;io.put(f,ROOT+'/'+p.name,raw);freeze[p.name]=H(raw)
   values={'SOURCE_FREEZE.json':dict(candidate_root=ROOT,sha256=freeze,old366_allbytes_exact=True,new_files=2,independent_expert='E1_WAVE'),
    'REUSED_ACTUAL_CONTRACTS.json':v['proof'],'EXPOSURE_DURATION_DECISION.json':decision,'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
  save('WAVE_NEW_SOURCE_FREEZE.json',values['SOURCE_FREEZE.json'])
  cpu=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,inspect,ast
D=Path(ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_wave35_exposure_005_once as own
own.verify();own.boundary();p=own.source();a=torch.load(p,map_location='cpu',weights_only=False);z=torch.load(p,map_location='cpu',weights_only=False)
checked=0
for group in ('actor_state_dict','critic_state_dict'):
 for key,v in a[group].items():assert torch.equal(v,z[group][key]) and v.data_ptr()!=z[group][key].data_ptr();checked+=1
x=next(iter(a['actor_state_dict'].values()));other=next(iter(z['actor_state_dict'].values()));keep=other.clone();x.add_(1);assert torch.equal(other,keep)
assert own.m.s.q.base.sha(p)==own.SOURCE_SHA and own.m.D==D and own.m.R==D/'reports' and own.m.CODE==D/'isaac/mod4'
assert own.m.s.D==D and own.m.s.R==D/'reports'
runtime=own.m.runtime();assert float(runtime.get('RM_EPISODE_S','20'))==20 and runtime['RM_KEEP_STD']=='1'
assert all(k not in runtime for k in ('RM_E1_INITIAL_ADMISSION','RM_E1_G3_INITIAL_ADMISSION','RM_E1_COMMAND_RETENTION_INITIAL_ADMISSION'))
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_only=True,root=str(D),source_count=368,finite_tensors=102,source=own.fullsave(p),independent_actorcritic_tensors_checked=checked,
 CPU_copy_mutation_not_other_copy_or_source=True,actual_import_train_worker_root_Popen_schema_same=True,actual_same_G3_samecommand_CUDA_restore_required_on_own_startup=True,
 reuse_actual_SDK_native_small_big_and_old_same_scope_startup_exact=True,no_preflight_replay=True,seconds=1800,geometry_height_m=.035,fulltenwaves=True,
 original12to16s_command_resampling20s_episode_and_original_route_termination_unchanged=True,new_budget_seconds=0,candidate_number=142)
(D/'reports/WAVE_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('WAVE_TARGET_CPU_PASSED.json',cpu);print(json.dumps(dict(root=ROOT,CPU_passed=True,seconds=1800,candidate_number=142,dispatch_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_STAGE_CPU_REJECTED_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_or_GPU_replay=True));raise
