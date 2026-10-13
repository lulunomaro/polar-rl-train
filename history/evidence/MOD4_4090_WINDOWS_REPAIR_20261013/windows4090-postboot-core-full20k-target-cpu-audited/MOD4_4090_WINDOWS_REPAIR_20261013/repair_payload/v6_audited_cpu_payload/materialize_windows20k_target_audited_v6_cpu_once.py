"""New independent V6 target directory; original V5 materializer bytes retained."""
import materialize_windows20k_target_cpu_once as original
SCOPE_NAME='training_scope_full20k_left_repair_audited_v6_20261013'
ENVIRONMENT_ROOT=original.ENVIRONMENT_ROOT
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
original.SCOPE_NAME=SCOPE_NAME
original.EXECUTABLES=original.EXECUTABLES+NEW_FILES
if __name__=='__main__':original.main()
