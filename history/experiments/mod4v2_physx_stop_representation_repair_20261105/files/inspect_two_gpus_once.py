"""One real read-only resource snapshot on host72; host86 excluded, no leases claimed."""
from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;out=D/'RESOURCE_72_TWO_GPU_SNAPSHOT.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code='''import json,time,subprocess,shutil
from pathlib import Path
import psutil
B=Path('/home/lc01/Zonglin Li/zonglin2')
def cmd(a):
 p=subprocess.run(a,capture_output=True,text=True);return dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
c=json.loads((B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];owner=None if a is None else{k:a[k]for k in('owner_run_id','owner_parent_pid','started_epoch')if k in a}
r=dict(epoch=time.time(),host='72',excluded_host86_not_connected=True,gpus=cmd(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute=cmd(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']),RAM_available_bytes=psutil.virtual_memory().available,disk_free_bytes=shutil.disk_usage(B).free,original_authority=dict(generation=c['authority_generation'],remaining_training_seconds=c['remaining_training_seconds'],finite_minimum_remaining_seconds=c.get('finite_minimum_remaining_seconds'),active_owner=owner),snapshot_is_not_GPU_or_lock_lease=True,canonical_writes_or_copies=0,model_raw_or_SDK_reads=0,foreign_signal_or_flock_operations=0)
print(json.dumps(r))'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,err;r=json.loads(text);assert r['gpus']['returncode']==r['compute']['returncode']==0;out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
finally:c.close()
