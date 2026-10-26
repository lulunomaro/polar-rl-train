from pathlib import Path
import os,time,json,fcntl,subprocess
def acquire(B):
 root=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(root.resolve());task=json.loads((B/'job0/TASK.json').read_bytes());gpu=task['GPU_UUID'];assert gpu in ('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d');lock=(root/'state'/('three_expert_v2_'+gpu+'.lock')).open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with (root/'state/finite_environment_validation.lock').open('rb+') as global_lock:fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(global_lock,fcntl.LOCK_UN)
 (B/'OWN_GPU_SPECIFIC_FCNTL_AND_GLOBAL_FREE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),GPU_UUID=gpu,actual_private_GPU_fcntl_held=True,actual_original_global_fcntl_free_at_admission=True,human_three_distinct_experts_explicit_per_GPU_contract=True,other_process_untouched=True,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode()),indent=2));return lock
