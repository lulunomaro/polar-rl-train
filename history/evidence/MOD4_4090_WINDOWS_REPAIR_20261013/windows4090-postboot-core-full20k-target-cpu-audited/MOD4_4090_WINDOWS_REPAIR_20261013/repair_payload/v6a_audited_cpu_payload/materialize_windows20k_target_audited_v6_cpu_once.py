"""New independent V6 target directory; original V5 materializer bytes retained."""
import materialize_windows20k_target_cpu_once as original
SCOPE_NAME='training_scope_full20k_left_repair_audited_v6a_20261013'
ENVIRONMENT_ROOT=original.ENVIRONMENT_ROOT
H=original.H
ref=original.ref
fresh_json=original.fresh_json
NEW_FILES=(
 'windows4090_substep_readback_v6.py','windows4090_probe_contract_audited_v6.py',
 'v6_closed_source_wrapper.py','windows4090_repair_worker_audited_v6.py',
 'windows4090_training_runtime_audited_v6.py','run_windows4090_stage_audited_v6_once.py',
 'materialize_windows20k_target_audited_v6_cpu_once.py','prepare_windows20k_sdk_manifest_audited_v6_cpu_once.py',
 'windows4090_demand_task_wrapper_audited_v6.ps1','register_windows4090_demand_task_audited_v6_once.ps1',
 'reference_sources/factor_runtime_3060_native_v2.py','reference_sources/factor_runtime.py',
 'reference_sources/local_physx_api.py','reference_sources/scut_curriculum_gate_v4.py',
 'V6_READBACK_AND_RESOURCE_CONTRACT_CPU_PREPARED.md',
)
_old_full_cpu=original.full_cpu
def full_cpu_with_actual_experiences(scope,root,packages,assembly):
 result=_old_full_cpu(scope,root,packages,assembly)
 ready=root/'install_reports/APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json'
 apps=__import__('json').loads(ready.read_bytes())
 assert apps['passed'] and apps['all21_recursive_apps_rendering_config_exact']
 for row in apps['actual_files']:
  assert H(row['path'])==row['sha256']
  result['sourcefreeze_files'].append(ref(row['path']))
 result['sourcefreeze_files'].append(ref(apps['actual_manifest']['path']))
 result['sourcefreeze_files'].append(ref(ready))
 result['actual_SDK_experiences21_CPU_exact']=True
 result['actual_substep_API_contact_COM_hardware_V6_GPU_pending']=True
 result['max_formal_updates']=256
 result['max_periodic_plus_final_checkpoints']=129
 return result
original.full_cpu=full_cpu_with_actual_experiences
original.SCOPE_NAME=SCOPE_NAME
original.EXECUTABLES=original.EXECUTABLES+NEW_FILES
if __name__=='__main__':original.main()
