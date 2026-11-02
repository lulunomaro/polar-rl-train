"""2026-11-02 18:48 human request: low-load GPU sharing is permitted.
Only future unused owner windows. This changes compute-app exclusion, not
canonical/private/finite locks, resource thresholds, budget, or active workers.
"""
import subprocess,time,shutil

def evaluate_resource_snapshot(uuid,gpu_line,compute_csv,ram_available,disk_free):
    a=[x.strip()for x in gpu_line.strip().split(',')]
    if len(a)!=4 or a[0]!=uuid or a[1]!='NVIDIA GeForce RTX 4090':
        raise RuntimeError('Exact authorized4090 required')
    if not(int(a[2])>15669 and int(a[3])<=30 and ram_available>64*1024**3 and disk_free>50*1024**3):
        raise BlockingIOError('Original GPU/host resource headroom not ready')
    processes=[]
    for line in compute_csv.strip().splitlines():
        parts=[x.strip()for x in line.split(',')]
        if len(parts)==3 and parts[0]==uuid:
            processes.append(dict(GPU_UUID=parts[0],pid=parts[1],used_GPU_memory_MiB=parts[2]))
    return dict(GPU_UUID=uuid,GPU_line=gpu_line.strip(),free_MiB=int(a[2]),utilization_percent=int(a[3]),preexisting_compute_processes=processes,compute_empty=not processes,low_load_sharing_allowed_by_human=True,human_request_local_time='2026-11-02T18:48:07+08:00',RAM_available=ram_available,disk_free=disk_free,canonical_private_finite_locks_still_required=True)

def admit_shared_gpu(uuid,job_root):
    import psutil
    line=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)
    apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
    value=evaluate_resource_snapshot(uuid,line,apps,psutil.virtual_memory().available,shutil.disk_usage(job_root).free)
    value['epoch']=time.time()
    return value
