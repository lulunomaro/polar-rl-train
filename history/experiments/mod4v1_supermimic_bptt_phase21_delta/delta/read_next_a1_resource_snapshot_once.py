"""Read-only next-A1 readiness, one snapshot after the prior owner is fully closed."""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;out=R/'reports/NEXT_A1_AFTER_PRIOR_CLOSED_RESOURCE_SNAPSHOT_V1.json';assert not out.exists();truth=json.loads((R/'reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json').read_bytes());sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code=r'''from pathlib import Path
import json,subprocess,time,psutil,shutil
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(p.read_bytes());a=c.get('active_segment');owner=None if a is None else{k:a.get(k)for k in('owner_parent_pid','owner_run_id','started_epoch','kind')}
def query(fields,kind):
 q=subprocess.run(['nvidia-smi','--query-'+kind+'='+fields,'--format=csv,noheader,nounits'],capture_output=True,text=True,check=True);return q.stdout.strip().splitlines()
print(json.dumps(dict(epoch=time.time(),canonical_owner=owner,canonical_generation=c.get('authority_generation'),remaining_seconds=c['remaining_training_seconds'],strict_reserve_seconds=86412.86069250107,gpu_metadata=query('uuid,name,memory.total,memory.free,utilization.gpu','gpu'),compute_metadata=query('pid,gpu_uuid,used_gpu_memory','compute-apps'),RAM_available_bytes=psutil.virtual_memory().available,disk_free_bytes=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2').free,read_only=True,lock_signal_PT_SDK_GO_Cwrite_operations=0)))'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);value=json.loads(txt);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:c.close()
