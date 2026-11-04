"""One read-only diagnosis of original pre-GO contention; no locks/signals/SDK/models or writes remote."""
from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;out=D/'FDN_W2_ORIGINAL_RESOURCE_WAIT_DIAGNOSIS_ONCE.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
root=json.loads((D/'FDN_W2_STAGE_RESULT.json').read_bytes())['root'];code='''from pathlib import Path
import json,time,subprocess
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());keep=('generation','active','active_owner','active_run','active_run_id','current_owner','remaining_seconds','authorized_seconds','used_expert_seconds','total_seconds');view={k:c[k] for k in keep if k in c};p=subprocess.run(['nvidia-smi','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True);print(json.dumps(dict(epoch=time.time(),canonical_read_only_current_metadata=view,GPU_query_returncode=p.returncode,GPU_query=p.stdout,stderr=p.stderr,foreign_process_or_lock_modifications=0,source_models_SDK_or_optimizer_calls=0)))
'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();v=dict(root=root,returncode=rc,stdout=a,stderr=b,epoch=time.time());out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert rc==0,b
finally:c.close()
