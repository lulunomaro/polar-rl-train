from pathlib import Path
import hashlib,json
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
def validate(lease,manifest,case):
 assert lease['target_host']=='10.24.4.210' and lease['execution_backend']=='linux210_GPU0_frozen_only'
 assert lease['GPU_UUID']==GPU and lease['namespace']=='H1_HOUR1_FINAL_LINUX210_V1_20261018'
 assert lease['GPU_lease_granted_by_root'] is True and lease['actual_selected_GPU_idle_private_lock_free'] is True
 assert lease['checkpoint_sha256']==manifest['source']['SHA']=='fe7780a502743dc12c0826d82f4a5a5a5ee8917f095890c7bfb866c48b600309'
 assert lease['case_parameters']==case and case['steps'] in (120,1500) and case['num_envs']==80 and case['seed']==20260928
 assert case['kind']=='jump' and case['router_mode']=='single_eval' and case['headless'] and case['device']=='cuda:0'
 assert lease['human_authorized_4090_eval_parallel_training_not_interrupted'] is True
 if case['steps']==1500:assert lease['actual_same_backend_source_native120_allrow_CPU_passed'] is True and lease['native120_actual_exit_childrenout_lockfree'] is True
 return True
