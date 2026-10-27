"""Local source/text-only freeze; deliberately no model/asset traversal."""
from pathlib import Path
import ast,datetime,hashlib,json
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1'
def row(path):
 path=Path(path);assert path.suffix.lower() in ('.py','.json','.txt','.md')
 raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
sources=[B/p for p in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','NATIVE87_SOURCE_CONTRACT_ACTUAL.json','job0/TASK.json','three_slot_common_v1.py','h1_native_own87_worker_v1.py','h1_step270_sdk_runtime_candidate.py','step270_goal_and_scut_rates_candidate.py','source/native_wheel_leg_bridge_v4.py','source/actual_DR_memory_getter_v1.py','source/native87_encoder_actual_sdk_adapter_v1.py','source/converted_MOD4_jump_mdp_v4.py','source/native_finalization_own_v3.py','source/supermimic_wheel_leg_v3/networks.py','source/supermimic_wheel_leg_v3/learner.py','source/supermimic_wheel_leg_v3/geometry.py','job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py','job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py','job0/runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py')]
sources += [N/'saved_actual_SDK_source'/p for p in ('termination_manager_actual_for_future_frozen_N1_87.py.txt','observation_manager_6_1_14_actual.py.txt','actual_base_articulation_data_for_R5_tensor_view.py.txt','actual_physx_articulation_data_for_R5_tensor_view.py.txt')]
for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
with (HERE/'SOURCE_INPUTS_FINAL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(source_only=True,no_model_asset_or_raw_read=True,inputs=[row(p) for p in sources]),f,indent=2)
files=[]
for p in sorted(HERE.iterdir()):
 if p.is_file() and p.name!='FREEZE_INDEX_ACTUAL.json':
  r=row(p);r['relative']=p.name;files.append(r)
reports=[json.loads((HERE/name).read_bytes()) for name in ('SOURCE_CPU_ACTUAL.json','SOURCE_CPU_CLOSURE_INCREMENT_V2_ACTUAL.json','SOURCE_CPU_ORIGINAL_ALLOUT_INCREMENT_V3_ACTUAL.json')]
assert all(r['passed'] is True for r in reports)
value=dict(frozen=True,freeze_local=datetime.datetime.now().astimezone().isoformat(),scope='source-only future R5 formal frozen three-seed N1 acceptance preparation',actual_evaluation_executed=False,actual_GPU_or_SDK_N1_admitted=False,real_checkpoint_or_raw_read_stat_copy_or_hash=False,CPU_metadata_source_checks=sum(r['checks'] for r in reports),all_cpu_checks_fixture_or_source_only=True,files=files,self_excluded='FREEZE_INDEX_ACTUAL.json',errors_retained=['SOURCE_READ_ERRORS_RETAINED.json'],archive='PENDING root ordinary supplemental archive; no helper Git')
with (HERE/'FREEZE_INDEX_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
print(json.dumps(dict(frozen=True,files=len(files),CPUchecks=value['CPU_metadata_source_checks'],index=row(HERE/'FREEZE_INDEX_ACTUAL.json')),indent=2))
