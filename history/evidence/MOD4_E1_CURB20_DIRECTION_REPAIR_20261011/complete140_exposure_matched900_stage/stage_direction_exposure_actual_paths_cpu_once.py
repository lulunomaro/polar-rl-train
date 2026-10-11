"""New isolated root and CPU admission only; no trainer launch in this file."""
from direction_io import *
import traceback
from prepare_direction140_decision_and_exposure_continuation_once import OLDROOT,ROOT

def main():
 decision=json.loads((R/'CURB140_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['allow_one_exposure_duration_only_continuation']
 n,w=io.connect_both()
 try:
  # Number is selected only after both actual queues/results/jobs show it unused.
  num=141
  folders=[('linux',io.E+'/eval_queue'),('linux',io.E+'/eval_results'),('windows','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')]
  checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for host,path in folders:
    names=(f if host=='linux' else g).listdir(path);matches=[x for x in names if 'episode-d3-'+str(num)+'-' in x]
    checks.append(dict(host=host,path=path,number=num,matches=matches));assert not matches,(host,path,matches)
  unused=dict(epoch=time.time(),number=num,both_hosts_actual_queue_results_jobs_unused=checks)
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,shutil,fcntl
old=Path(PREVIOUS_ROOT_TOKEN);D=Path(NEW_ROOT_TOKEN);B=Path(BUDGET_PATH_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not D.exists();st=j(old/'reports/E1_STATE.json');receipt=j(old/'reports/e1_CURB20_direction_repair_observation_PASSED.json')
assert st['phase']=='E1_CURB20_direction_repair_saved_review_ready' and st['child'] is None
assert receipt['checkpoint']['sha256']=='e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16'
exits=[]
for loc in (st['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),receipt['own_PID_bound_receipt']):
 p=Path('/proc')/str(loc['pid']);actual=None
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();actual=dict(state=z[0],start_ticks=int(z[19]));assert actual['state']=='Z' or actual['start_ticks']!=loc.get('start_ticks')
 exits.append(dict(locator=loc,actual=actual))
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
b=j(B);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
segments=[x for x in b['completed_segments'] if x['pid']==receipt['own_PID_bound_receipt']['pid']];assert segments==receipt['unique_completed_segment']
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==423
D.mkdir();(D/'reports').mkdir()
for name,sha in freeze['sha256'].items():
 p=old/name;assert h(p)==sha;q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json','DIRECTION_TARGET_CPU_PASSED.json','ENTRY_ORIGIN_BOUND_SDK10_PASSED.json','DIRECTION_NATIVE20K_PASSED.json','DIRECTION_REUSED_PHYSICAL_SCOPE_VERIFIED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','ENTRY_FRESH_SAME_SCOPE_PASSED.json'):
 shutil.copy2(old/'reports'/name,D/'reports'/name)
reuse=[]
for name in ('ENTRY_ORIGIN_BOUND_SDK10_PASSED.json','DIRECTION_NATIVE20K_PASSED.json'):
 row=j(old/'reports'/name);assert row['passed'] and h(Path(row['path']))==row['sha256'];reuse.append(row)
pre=j(old/'reports/E1_COMPLETE_PPO_PREFLIGHT_PASSED.json')
for k in ('small','big'):
 row=pre[k];assert row['discarded_preflight'] and h(Path(row['checkpoint']['path']))==row['checkpoint']['sha256']
 assert [x for x in b['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']]==row['unique_completed_segment']
fresh=j(old/'reports/ENTRY_FRESH_SAME_SCOPE_PASSED.json');assert fresh['passed'] and fresh['actual_control_steps']==fresh['actual_additional_PPO_updates']==0
print(json.dumps(dict(root=str(D),previous=str(old),source_freeze=freeze,selected_checkpoint=receipt['checkpoint'],actual_previous_exits=exits,old_unique_formal_segment=segments,reused_physical= reuse,reused_complete_preflight=pre,reused_fresh=fresh,canonical_bytes_SHA=h(B),no_GPU_or_budget_write=True)))
'''.replace('PREVIOUS_ROOT_TOKEN',repr(OLDROOT)).replace('NEW_ROOT_TOKEN',repr(ROOT)).replace('BUDGET_PATH_TOKEN',repr(io.B)))
  save('EXPOSURE_MATCHED_SOURCE423_COPIED.json',v);hashes=dict(v['source_freeze']['sha256'])
  p=D/'exposure_matched_payload/supervise_curb20_direction_exposure_matched_once.py';raw=p.read_bytes();hashes[p.name]=H(raw)
  with n.open_sftp() as f:
   io.put(f,ROOT+'/'+p.name,raw)
   values={'SOURCE_FREEZE.json':dict(candidate_root=ROOT,sha256=hashes,old423_allbytes_exact=True,only_new_independent_controller=True),
    'MATCHED_SOURCE_SELECTED.json':v['selected_checkpoint'],
    'MATCHED_ADMISSION_REUSE_ACTUAL.json':v,
    'CANDIDATE_JOB_UNUSED_ACTUAL.json':unused,
    'CURB140_COMPLETE_SCOPE_DECISION.json':decision}
   for name,value in values.items():io.put(f,ROOT+'/reports/'+name,json.dumps(value,ensure_ascii=False,indent=2).encode())
   for name,src in [('CURB140_COMPLETE_ACTUAL_REVIEW.json',sorted(R.glob('CURB140_SCHEMA_REVIEW_[0-9]*.json'))[-1]),('CURB140_PREFIX_EXPOSURE_DIAGNOSIS.json',R/'CURB140_COMPLETE_PREFIX_EXPOSURE_DIAGNOSIS.json')]:io.put(f,ROOT+'/reports/'+name,src.read_bytes())
  cpu=run(n,r'''from pathlib import Path
import sys,json,torch,ast,time,hashlib
D=Path(NEW_ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_direction_exposure_matched_once as own
own.prior.verify();assert own.prior.D==D and own.prior.CODE==D/'isaac/mod4'
row=own.read(D/'reports/MATCHED_SOURCE_SELECTED.json');p=Path(row['path']);info=own.source();assert info==p
ck=torch.load(p,map_location='cpu',weights_only=False)
assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
assert own.prior.fullsave(p)['finite_tensors']==104
a=torch.load(p,map_location='cpu',weights_only=False);z=torch.load(p,map_location='cpu',weights_only=False)
for key in ('actor_state_dict','critic_state_dict'):
 for name,x in a[key].items():assert torch.equal(x,z[key][name]) and x.untyped_storage().data_ptr()!=z[key][name].untyped_storage().data_ptr()
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_only=True,root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),selected_checkpoint=row,finite_tensors=104,all_actorcritic_optimizer_std_DR_named_private_command_geometry_entry_direction_source_contract_verified=True,independent_actorcritic_storage_verified=True,
 same_scope_startup_contract_requires_terrain_entry_direction_exact_and_no_new_scope=True,original_423_all_bytes_preserved=True,old_scope_CPU_SDK_native_small_big_fresh_clock_reused=True,no_GPU_or_PPO_preflight_replay=True,target_seconds=900,candidate_number=141)
(D/'reports/MATCHED_REUSE_CPU_PASSED.json').write_text(json.dumps(v,indent=2));own.boundary();print(json.dumps(v))
'''.replace('NEW_ROOT_TOKEN',repr(ROOT)))
  save('EXPOSURE_MATCHED_TARGET_CPU_PASSED.json',cpu);save('EXPOSURE_MATCHED_SOURCE_FREEZE.json',values['SOURCE_FREEZE.json']);save('EXPOSURE_MATCHED_ACTIVE_ROOT.json',dict(root=ROOT,source_count=len(hashes),dispatch_pending=True));save('EXPOSURE_MATCHED_JOB_UNUSED_ACTUAL.json',unused)
  print(json.dumps(dict(root=ROOT,source_count=len(hashes),CPU_passed=True,seconds=900,number=num,dispatch_pending=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('EXPOSURE_MATCHED_STAGE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_stage_or_GPU_replay=True));raise
