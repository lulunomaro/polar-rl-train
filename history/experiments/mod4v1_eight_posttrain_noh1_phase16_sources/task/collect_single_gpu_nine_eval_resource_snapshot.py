"""Read actualauthorizedGPU0/1 status only. Snapshotnotadmission, no kills/locks/PPO/budgetreads."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;code="""import subprocess,json,time,psutil,shutil
UUIDS=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'];rows=[]
for u in UUIDS:
 text=subprocess.check_output(['/usr/bin/nvidia-smi','-i',u,'--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();x=[v.strip()for v in text.split(',')];rows.append({'GPU_UUID':x[0],'name':x[1],'memory_total_MiB':int(x[2]),'memory_free_MiB':int(x[3]),'utilization_percent':int(x[4])})
apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_memory','--format=csv,noheader,nounits'],text=True);selected=[]
for line in apps.splitlines():
 x=[v.strip()for v in line.split(',')]
 if x and x[0]in UUIDS:selected.append({'GPU_UUID':x[0],'pid':x[1],'memory_MiB':x[2]})
print(json.dumps({'kind':'ONECARD_NINE_N80_EVAL_ACTUAL_RESOURCE_SNAPSHOT_NOT_ADMISSION','epoch':time.time(),'GPUs':rows,'authorizedGPU_compute_apps':selected,'RAM_available_bytes':psutil.virtual_memory().available,'project_disk_free_bytes':shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2').free,'no_foreign_actions_or_canonical_access':True}))
""";c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('NINE_N80_SINGLE_GPU_RESOURCE_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,indent=2))
