from pathlib import Path
import getpass,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
READ=r'''
from pathlib import Path
import json,psutil,shutil,subprocess,time
raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);uuid='GPU-16828f91-2b45-b646-8dc0-9481138e2842';line=next(x for x in raw.splitlines() if uuid in x);f=[x.strip() for x in line.split(',')];busy=[x for x in compute.splitlines() if uuid in x];print(json.dumps(dict(epoch=time.time(),third_GPU_UUID=uuid,third_GPU_line=line,third_compute_rows=busy,third_has_compute=bool(busy),third_memory_free_MiB=int(f[4]),original_H1_min_free_MiB=15669,memory_threshold_passed=int(f[4])>=15669,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2').free,no_peer_identity_inspection=True,no_training_launch_or_lock_mutation=True,no_full_H1_admission_claim=True)))
'''
try:
 with (R/'THIRD4090_RESOURCE_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 pw=getpass.getpass('72 third4090 read-only resources (hidden): ');c=d.connect72(pw);pw=None
 try:v=d.code(c,d.PY72,READ,{},timeout=90)
 finally:c.close()
 with (R/'THIRD4090_RESOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'THIRD4090_RESOURCE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
