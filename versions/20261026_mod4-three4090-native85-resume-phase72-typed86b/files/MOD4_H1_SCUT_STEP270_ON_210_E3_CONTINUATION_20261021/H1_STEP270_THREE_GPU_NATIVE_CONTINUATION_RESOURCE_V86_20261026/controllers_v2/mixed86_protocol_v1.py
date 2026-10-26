"""Typed normal/native three-slot contract. Pure metadata, no I/O on import."""
import hashlib,json
NAMESPACE='H1step270_three_gpu_native_cont_2610v86'
SOURCES={
 'h1':('8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',829700),
 'e2':('94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af',829700),
 'recovery':('7f8f270c84b7e3d9e7efd0b1bd29d10d430a51bb976e1689222859f24e714d59',862540)}
GPUS=dict(h1='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',e2='GPU-16828f91-2b45-b646-8dc0-9481138e2842',recovery='GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
BOOTSTRAP_SHA=SOURCES['h1'][0]
REFERENCE_SHA='0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94'
AUTHORITY_GENERATION='MOD4_SINGLE_WRITER72_20261026'

def digest(value):return hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest()

def validate_schedule(cfg):
 specs=cfg['experts'];assert set(specs)==set(SOURCES) and cfg['deferred_experts']==[]
 assert cfg['scheduling_authority']=='human_requested_available_experts' and cfg['authority_generation']==AUTHORITY_GENERATION
 for key,(sha,adam) in SOURCES.items():
  spec=specs[key];assert spec['key']==key and spec['source_SHA']==sha and spec['source_Adamstep']==adam
  assert spec['GPU_UUID']==GPUS[key] and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
  assert spec['execution_backend']==('source210' if key=='h1' else 'target72')
  assert spec['owner_authority_generation']==AUTHORITY_GENERATION
 if not (specs['e2'].get('finite_method_test') and specs['e2'].get('native_continuation') and specs['e2'].get('h1_step270_method_test')):raise AssertionError('Native continuation role missing')
 assert specs['e2']['bootstrap_source_SHA']==BOOTSTRAP_SHA and specs['e2']['source_native_iteration']==68 and specs['e2']['window_start_world_updates']==680 and specs['e2']['window_start_policy_updates']==58
 assert specs['h1'].get('closed_production_continuation') and not specs['h1'].get('finite_method_test')
 assert specs['recovery']['policy_hz']==50 and not specs['recovery'].get('finite_method_test')
 return True

def native_valid_ready(row,spec):
 envelope=row.get('closed_source_CPU') or {};value=envelope.get('value') or {}
 flags=('actual_installed_CPU_passed','actual_H1_source_SDK_CPU_passed','native85_fullstate_source_CPU_passed','source_original85_cost_allout_passed','native_continuation_restore_required','not_production_E2_source_or_skill_qualification','original_H1_270_physics_source_exact','reference_and_adapter_actual_CPU_validated')
 pins=spec.get('candidate_pins')
 return bool(spec.get('finite_method_test') and spec.get('native_continuation') and spec.get('h1_step270_method_test')
  and spec.get('key')=='e2' and spec.get('source_SHA')==SOURCES['e2'][0] and spec.get('source_Adamstep')==829700 and spec.get('bootstrap_source_SHA')==BOOTSTRAP_SHA
  and spec.get('GPU_UUID')==GPUS['e2'] and spec.get('execution_backend')=='target72'
  and isinstance(pins,dict) and pins and value.get('candidate_pins')==pins
  and row.get('key')=='e2' and row.get('phase')=='ready' and not row.get('original_error') and row.get('manifest_SHA')==spec.get('manifest_SHA')
  and envelope.get('actual_CPU_waited_EXIT0') is True and envelope.get('SHA')==digest(value)
  and value.get('passed') is True and value.get('kind')=='UNISUPERMIMIC_FUDAN_NATIVE85_CONTINUATION_SOURCE_SDK_CPU_V86'
  and value.get('source_SHA')==spec['source_SHA'] and value.get('bootstrap_SHA')==BOOTSTRAP_SHA and value.get('bootstrap_Adam')==829700
  and value.get('GPU_UUID')==spec['GPU_UUID'] and value.get('execution_backend')==spec['execution_backend']
  and all(value.get(flag) is True for flag in flags)
  and value.get('reference_artifact_SHA')==REFERENCE_SHA==spec.get('reference_artifact_SHA')
  and value.get('adapter_CPU_report_SHA')==spec.get('adapter_CPU_report_SHA')
  and value.get('objective_contract_SHA')==spec.get('objective_contract_SHA')
  and value.get('source_native_iteration')==68 and value.get('source_world_updates')==680 and value.get('source_policy_updates')==58
  and value.get('metadata_helper_bytes')==2536 and value.get('metadata_helper_SHA')=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
  and value.get('actual_runtime_order_readback') is False)
