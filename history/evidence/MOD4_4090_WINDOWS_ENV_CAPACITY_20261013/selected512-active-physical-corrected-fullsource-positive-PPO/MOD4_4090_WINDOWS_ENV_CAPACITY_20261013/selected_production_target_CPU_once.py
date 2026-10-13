from pathlib import Path;import json,hashlib,psutil,msvcrt,shutil,time,ast
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v8_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_selected_ownstate_production_v1_20261013');N=512
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
rel=json.loads((old/'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json').read_bytes());assert rel['OSlock_released'] and rel['all_own_descendants_actual_absent']
parent=rel['parent']
try:p=psutil.Process(parent['pid']);assert p.create_time()!=parent['created']
except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
source=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v8_20261013/attempts/temporary2048_fullrestore_v1/output/WINDOWS4090_REPAIRED_FULLRESTORE_COMPLETE.pt');assert H(source)=='21213e0f1ce6ee716b7f4ff44cb214b0a4809dce129cd756c599cd8c497b9bee'
independent=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/SELECTED_INDEPENDENT_PHYSICS_CPU_REVIEW_ed3b75fc2e3af9ffee03e36ea29285bbb3926b3033ee3d8fcdc3a83790a0c634.json');assert H(independent)=='ed3b75fc2e3af9ffee03e36ea29285bbb3926b3033ee3d8fcdc3a83790a0c634';physics=json.loads(independent.read_bytes());assert physics['passed'] and physics['actual_whole_stdout_no_overflow'] and physics['complete_native_restore_physical_contracts_passed'] and physics['num_envs']==N and physics['actual_scope'].replace(chr(92),'/')==str(old).replace(chr(92),'/') and physics['prePPO_production_source']['sha256']==H(source) and physics['discarded_benchmark_weights']['sha256']!=H(source)
assert not new.exists();new.mkdir();(new/'reports').mkdir();(new/'attempts').mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload',ignore=shutil.ignore_patterns('__pycache__'))
p=new/'payload/temporary_parent.py';s=p.read_text(encoding='utf8');needle="for phase in ('native', 'fullrestore', 'train'):";assert s.count(needle)==1;s=s.replace(needle,"for phase in ('train',):")
needle='            resource_reject = False';assert s.count(needle)==1;s=s.replace(needle,needle+'\n            capacity_error_seen = False')
needle='                if time.time() - lastwrite >= 15 or child.poll() is not None:';assert s.count(needle)==1
guard='''                if phase == 'train' and (time.time() - lastwrite >= 15 or child.poll() is not None):
                    lp=A/'worker_stdout.log'
                    if lp.exists():
                        with lp.open('rb') as f:
                            f.seek(max(0,lp.stat().st_size-1048576));tail=f.read()
                        if b'buffer overflow detected' in tail or b'Contacts have been dropped' in tail or b'PhysX scene is corrupted' in tail or b'PhysX error:' in tail:
                            capacity_error_seen=True
                            atomic(O/'ACTUAL_PHYSX_CAPACITY_FAILURE.json',dict(epoch=time.time(),passed=False,original_log_path=str(lp),no_invalid_physics_scope_pass=True,request_own_save_stop_no_kill=True))
                            if not stop.exists():atomic(stop,dict(epoch=time.time(),reason='actual_PhysX_capacity_error',no_kill=True))
'''
s=s.replace(needle,guard+needle)
needle='passed = child.returncode == 0 and final is not None';assert s.count(needle)==1;s=s.replace(needle,'passed = not capacity_error_seen and child.returncode == 0 and final is not None')
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),source=ref(source),max_formal_updates=256,capacity_benchmark_only=False,production_weights_discarded=False,chosen_num_envs_by_actual_throughput_and_resource=True,strict_same_expanded_source=True,new_native_fullrestore_not_replayed=True,concrete_future_training_trace_upper_bound_bytes=N*256*24*16*4)
import sys;sys.path.insert(0,str(new/'payload'));import torch,temporary_state_binding as b
assert not torch.cuda.is_initialized() and b.N==N;ck=torch.load(source,map_location='cpu',weights_only=False);b.validate(ck,H(source));assert b.floating_count(ck)==107 and len(b.perenv_inventory(ck))==99 and ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['actual_current_GPU_restore_verified'] and not ck['WINDOWS4090_EXPANDED_ENV_BRANCH']['all12_own_CPUCUDA_restore_disk_roundtrip_and_API_offsets_pending']
cpu=dict(epoch=time.time(),passed=True,source=ref(source),chosen_num_envs=N,float107=True,perenv99=True,source_is_own_prePPO_not_discard_benchmark=True,actual_native_fullrestore_proofs_reused_byteSHA=True,independent_actual_whole_stdout_physics_admission=physics,independent_physics_proof_ref=ref(independent),old_parent_release_actual=rel)
q=new/'reports/SELECTED_SAME_EXPANDED_TARGET_CPU_ACTUAL.json';q.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(q)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
q=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';q.write_text(json.dumps(mf,indent=2),encoding='utf8');lease=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';lease.write_text(json.dumps(dict(epoch=time.time(),case_id='capacity512_selected_ownstate_production_v1_20261013',approved_GPU_scope=True,mode='train',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(q),human20GB_environment_search_and_training_authorized=True),indent=2),encoding='utf8');print(json.dumps(dict(epoch=time.time(),scope=str(new),targetCPU=ref(new/'reports/SELECTED_SAME_EXPANDED_TARGET_CPU_ACTUAL.json'),num_envs=N,source=ref(source),no_future_PPO_pass_inferred=True)))
