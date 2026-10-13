from pathlib import Path
import sys,json,time,hashlib,shutil,traceback,torch,numpy as np,psutil,subprocess,msvcrt
W=Path(__file__).resolve().parent;OLD=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013';D=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert not D.exists()
 final=json.loads((OLD/'reports/LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json').read_bytes());assert final['passed']
 source=final['own_checkpoint'];p=Path(source['path']);assert H(p)==source['sha256']=='97361dff5410a325094f8219d6afabe443dabd30331108bd27d4d73969ecfc89'
 A=OLD/'attempts/temporary_train128_v10_sameidentity_saved_source';dispatch=json.loads((A/'DISPATCH_RECEIPT.json').read_bytes());end=json.loads((A/'EXIT_RECEIPT.json').read_bytes());guardian=json.loads((A/'GUARDIAN_CURRENT.json').read_bytes())
 assert end['exit_code']==0
 if psutil.pid_exists(dispatch['child_pid']):assert abs(psutil.Process(dispatch['child_pid']).create_time()-dispatch['child_create_time'])>.001
 if psutil.pid_exists(guardian['parent_pid']):assert psutil.Process(guardian['parent_pid']).create_time()>end['epoch']
 with (OLD/'LOCAL_GPU_EXCLUSIVE.lock').open('r+b') as f:
  f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 ck=torch.load(p,map_location='cpu',weights_only=False);assert ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==128 and ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
 floats=[]
 def walk(v):
  if isinstance(v,torch.Tensor) and v.is_floating_point():assert torch.isfinite(v).all();floats.append(v)
  elif isinstance(v,dict):
   for z in v.values():walk(z)
  elif isinstance(v,(list,tuple)):
   for z in v:walk(z)
 walk(ck);assert len(floats)==107
 whole=sum(z.stat().st_size for z in A.rglob('*') if z.is_file());guard=int(whole*4*2+2*1024**3);free=psutil.disk_usage(str(W)).free;ram=psutil.virtual_memory().available;gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip();assert free>=guard and ram>=8*1024**3 and int(gpu)>=8500
 D.mkdir();(D/'reports').mkdir()
 shutil.copytree(OLD/'runtime',D/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
 names=('local_scope_worker.py','local_physx_api.py','local_state_projection.py','local_training_runtime.py','run_local_attempt.py','request_stop_after_save.ps1')
 rows=[]
 for name in names:
  raw=(OLD/name).read_bytes();(D/name).write_bytes(raw);rows.append(dict(name=name,original_SHA=hashlib.sha256(raw).hexdigest(),original_path=str(OLD/name)))
 for name in ('SOURCE_FULL_STATE_CPU_ACTUAL.json','V8_SAVE_WRITABLE_HANDLE_INDEPENDENT_CPU_VERIFIED.json'):(D/'reports'/name).write_bytes((OLD/'reports'/name).read_bytes())
 projection=D/'local_state_projection.py';text=projection.read_text(encoding='utf8');needle="D/'reports/V8_SAVE_WRITABLE_HANDLE_INDEPENDENT_CPU_VERIFIED.json'";assert text.count(needle)==1;text=text.replace(needle,"D/'reports/LOCAL_CONTINUE_SOURCE_FULLSTATE_CPU_VERIFIED.json'")
 # Same local scope must preserve every terrain/entry/direction/route/lifetime
 # identity and tensor before the new episode; only checkpoint provenance changes.
 needle="assert same(ck['E1_terrain_state'],projected['E1_terrain_state']) and same(ck['E1_WAVE50_episode_lifetime_state'],projected['E1_WAVE50_episode_lifetime_state'])";assert text.count(needle)==1
 text=text.replace(needle,"\n  for key in ('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_retained_flat_command_state','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):assert same(ck[key],projected[key]),key")
 compile(text,str(projection),'exec');projection.write_text(text,encoding='utf8')
 parent=D/'run_local_attempt.py';text=parent.read_text(encoding='utf8');needle="(D/'LOCAL_GPU_EXCLUSIVE.lock').open('a+b')";assert text.count(needle)==1;text=text.replace(needle,"Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock').open('a+b')");text=text.replace("sources=[D/'local_scope_worker.py',D/'local_physx_api.py']","sources=[D/'local_scope_worker.py',D/'local_physx_api.py',D/'local_state_projection.py',D/'local_training_runtime.py']");compile(text,str(parent),'exec');parent.write_text(text,encoding='utf8')
 sys.path.insert(0,str(D));from local_state_projection import same
 cloned={k:v.clone() if isinstance(v,torch.Tensor) else __import__('copy').deepcopy(v) for k,v in ck.items()};assert same(ck,cloned)
 for part in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert all(v.data_ptr()!=cloned[part][k].data_ptr() for k,v in ck[part].items() if isinstance(v,torch.Tensor))
 fixture=D/'reports/SAME128_FULLSTATE_CPU_DISK_FIXTURE.pt';torch.save(cloned,fixture);assert same(torch.load(fixture,map_location='cpu',weights_only=False),ck)
 wrong=__import__('copy').deepcopy(ck);wrong['E1_WAVE50_route_lifecycle_state']['assignment_sha256']='wrong';assert not same(ck,wrong)
 proof=dict(epoch=time.time(),passed=True,checkpoint=dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)),original_source_SHA=ck['LOCAL_TEMPORARY_BRANCH']['source_SHA'],num_envs=128,finite_floating_tensors=107,complete_local_final_already_reviewed=True,same_backend_geometry_entry_direction_route_lifetime=True,strict_full_tree_disk_roundtrip=True,source_wrong_assignment_rejected=True,old_source_original_not_modified=True,not_PhysX_exact_resume=True)
 save(D/'reports/LOCAL_CONTINUE_SOURCE_FULLSTATE_CPU_VERIFIED.json',proof)
 save(D/'reports/LOCAL_CONTINUE_RESOURCE_ADMISSION_ACTUAL.json',dict(epoch=time.time(),passed=True,durable_free=free,required=guard,first_complete_whole_output_bytes=whole,new_window_seconds=7200,rule='2x(4xactualcompleted1800whole)+2GiB',RAM_available=ram,minimum_RAM=8*1024**3,GPU_free_MiB=int(gpu),minimum_GPU_free_MiB=8500,no_parallel_GPU_or_installed_package_change=True))
 for z in rows:z['new_SHA']=H(D/z['name']);z['exact_old_bytes']=z['original_SHA']==z['new_SHA']
 save(D/'reports/LOCAL_CONTINUE_SOURCE_PREPARED.json',dict(epoch=time.time(),passed=True,old_runtime_all_byteexact=True,source_components=rows,only_source_proof_binding_stricter_sameidentity_and_sharedlock_snapshot_changes=True,SDK_and_fullrestore_physical_prior_SHA_reused_no_repeat=True,human_continue_intent='为何不继续训练了；此前正常训练别停与本机临时训练授权',remote_training_evaluation_still_paused=True,first_local1800_complete_second_same_scope7200=True,same_scope_max2_then_fullaudit=True,canonical_reconciliation_pending=True,shared_local_GPU_lock=str(OLD/'LOCAL_GPU_EXCLUSIVE.lock')))
 print(json.dumps(dict(passed=True,root=str(D),source=source,window=7200,resource_passed=True,ownfullCPU107_passed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=OLD/'reports'/('LOCAL_CONTINUE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');save(p,dict(error=traceback.format_exc(),partial_newroot_retained_if_any=True,no_GPU_or_PPO_or_remote_budget_mutation=True));raise
