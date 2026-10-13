"""Prepare new isolated repairroot. CPUonly; no dispatcher/AppLauncher/PPO/ledger."""
from pathlib import Path
import hashlib,json,shutil,time,torch,psutil,traceback
D=Path(__file__).resolve().parent;W=D.parents[1]
L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
N=W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013'
FA=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/policy_reward'
P=L/'attempts/same128_continue_second7200_v1/output/model_32396.pt'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def copy(p,q):
 assert p.is_file() and not q.exists();q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert H(p)==H(q);return dict(source=str(p),destination=str(q),bytes=p.stat().st_size,sha256=H(p),byteexact=True)
def walk(x):
 if torch.is_tensor(x):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,(tuple,list)):
  for v in x:yield from walk(v)
def main():
 assert not N.exists(),'New isolated root already exists; do not reprepare'
 assert H(P)=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 torch.set_num_threads(1);ck=torch.load(P,map_location='cpu',weights_only=False)
 floats=[v for v in walk(ck) if v.is_floating_point()];assert len(floats)==107 and all(torch.isfinite(v).all() for v in floats)
 assert ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==128 and ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
 assert tuple(ck['actor_state_dict']['mlp.0.weight'].shape)==(256,35) and tuple(ck['critic_state_dict']['mlp.0.weight'].shape)==(256,38)
 N.mkdir();(N/'reports').mkdir();rows=[]
 for p in (L/'runtime').rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:rows.append(copy(p,N/'runtime'/p.relative_to(L/'runtime')))
 for name in ('local_scope_worker.py','local_state_projection.py','local_training_runtime.py','run_local_attempt.py','local_physx_api.py','request_stop_after_save.ps1'):
  rows.append(copy(L/name,N/'immutable_local_continue_reference'/name))
 rows.append(copy(L/'local_physx_api.py',N/'local_physx_api.py'))
 rows.append(copy(L/'reports/SOURCE_FULL_STATE_CPU_ACTUAL.json',N/'reports/SOURCE_FULL_STATE_CPU_ACTUAL.json'))
 for name in ('left_head_exploration_migration_cpu_v1.py','LEFT_HEAD_EFFECTIVE_EXPLORATION_CPU_ACTUAL_PROOF.json'):
  assert (FA/name).exists(),name;rows.append(copy(FA/name,N/'immutable_repair_operator'/name))
 write(N/'reports/REFERENCE_ALL_SOURCE_BYTE_SHA_EXACT.json',dict(epoch=time.time(),passed_reference_copy_only=True,files=rows,original_runtime_assets_all_byteexact=True,installed_package_files_not_modified=True,no_GPU_SDK_PPO_started=True))
 source=dict(epoch=time.time(),passed=True,checkpoint=dict(path=str(P),bytes=P.stat().st_size,sha256=H(P)),original_source_SHA=ck['LOCAL_TEMPORARY_BRANCH']['source_SHA'],num_envs=128,finite_floating_tensors=107,old_source_complete_CPU_schema_only=True,same_backend_geometry_entry_direction_route_lifetime=True,CPU_not_GPU_admission=True,independent_repair_axis_not_applied=True,not_PhysX_exact_resume=True)
 write(N/'reports/ACTION_EFFECTIVE_SOURCE_FULLSTATE_CPU_VERIFIED.json',source)
 write(N/'reports/LOCAL_REPAIR_PREPARATION_STATUS.json',dict(epoch=time.time(),stage='immutable_reference_and_CPU_source_prepared',new_root=str(N),source=source['checkpoint'],operator_source=rows[-2],operator_CPU_report=rows[-1],active_worker_runtime_controller_not_yet_completed=True,no_GPU_SDK_PPO_or_formal_pass_claimed=True,resource_snapshot=dict(RAM_available_bytes=psutil.virtual_memory().available,durable_free_bytes=shutil.disk_usage(N).free),remote_training_and_evaluation_pause_preserved=True,shared_GPU_lock=str(W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock'),no_budget_transaction=True))
 print(json.dumps(dict(root=str(N),source=source['checkpoint'],copied_files=len(rows),CPU_source_finite107=True,GPU_launched=False),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  write(D/('ACTION_EFFECTIVE_PREPARE_CPU_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),source=dict(path=str(Path(__file__)),sha256=H(__file__)),no_GPU=True));raise
