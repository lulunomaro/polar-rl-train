"""Freeze this source-only directory. Never reads actual model/asset/raw files."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
lineage=[
 N/'payloads_r5/h1/native87_source_guard_v1.py',N/'payloads_r5/h1/target_native87_source_sdk_cpu_v1.py',
 N/'payloads_r5/h1/native87_role_metadata_closure_v1.py',N/'payloads_r5/h1/same_optimized_source_contract_metadata_candidate_v1.py',
 L/'native87R5_closing_typed_source/review_H1_native87R5_finals_CPU_unused_once.py',
 L/'native88_two_available_H1_runtime_protocol_source_v1/native88_protocol_v1.py',
 L/'native88_two_available_H1_runtime_protocol_source_v1/native88_closed_source_CPU_v1.py',
 L/'native88_two_available_H1_runtime_protocol_source_v1/h1_native88_changed_plant_worker_v1.py',
 L/'native88_two_available_H1_runtime_protocol_source_v1/native88_resource_guard_v1.py',
 L/'native88_own_step_differentiable_objective_source_v1/SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json',
 L/'native88_gas400_actual_asset_CPU_admission_20261027/ASSET_COMPOSITION_CPU_ACTUAL.json',
 N/'reports/H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',
 N/'reports/H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json']
assert all(p.suffix in ('.py','.json','.md','.txt') for p in lineage)
put('LINEAGED_SOURCE_INVENTORY_ACTUAL.json',dict(scope='source/metadata only, no actual model/asset hashes',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in lineage]))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
put('FROZEN_SOURCE_ONLY_STATUS_ACTUAL.json',dict(frozen_UTC=now,status='SOURCE_ONLY_FROZEN_NOT_INSTALLED_NOT_ADMITTED_NOT_GO',passed_source_CPU_checks=39,
 payload_modules=['native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py'],actual_target_CPU_executed=False,
 actual_models_read=0,actual_GPU_scene_PhysX=False,actual_400N_hardware_curve_measured=False,remote=False,Git=False,
 pending=['root exact final payload/contract/manifest binding','one fresh actual installed-source CPU admission per role','immutable actual waited CPU proof','actual new4096/PhysX/gas/D0-D7/order before first control/newPi'],
 no_existing_frozen_directory_modified=True,all_errors_and_rejections_retained=True))
files=[]
for p in sorted(D.rglob('*')):
    if p.is_file():
        assert p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip')
        files.append(dict(relative=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
put('INDEX_SHA256_ACTUAL.json',dict(frozen_UTC=now,scope='complete own directory inventory except this self-index',files=files,Git_archive_pending_root=True))
print(json.dumps(dict(frozen_UTC=now,index_SHA=H(D/'INDEX_SHA256_ACTUAL.json'),files=len(files),payload=[r for r in files if r['relative'] in ('native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py')]),indent=2))
