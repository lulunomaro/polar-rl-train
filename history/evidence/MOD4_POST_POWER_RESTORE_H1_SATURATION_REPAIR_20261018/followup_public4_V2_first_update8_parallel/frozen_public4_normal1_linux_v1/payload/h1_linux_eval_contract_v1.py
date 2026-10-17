from pathlib import Path
import hashlib,json
GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
def validate(lease,manifest,case):
 assert lease['target_host']=='10.24.0.72' and lease['execution_backend']=='linux72_GPU1_frozen_only'
 assert lease['GPU_UUID']==GPU and lease['namespace']=='H1_PUBLIC4_NORMAL1_LINUX4090_V1_20261018'
 assert lease['GPU_lease_granted_by_root'] is True and lease['actual_selected_GPU_idle_private_lock_free'] is True
 assert lease['checkpoint_sha256']==manifest['source']['SHA']=='282a46879f2c30c679d365b4c73017f85bd6560f3159915fee1cd53efc927fc4'
 assert lease['case_parameters']==case and case['steps'] in (120,1500) and case['num_envs']==80 and case['seed']==20260928
 assert case['kind']=='jump' and case['router_mode']=='single_eval' and case['headless'] and case['device']=='cuda:0'
 assert lease['human_authorized_4090_eval_parallel_training_not_interrupted'] is True
 if case['steps']==1500:assert lease['actual_same_backend_source_native120_allrow_CPU_passed'] is True and lease['native120_actual_exit_childrenout_lockfree'] is True
 return True
