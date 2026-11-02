"""ReadonlydiagnosisoforiginalpreGOlockwait; noforeignsignals/lockacquire/SDK/models/canonicalwrite."""
from pathlib import Path
import json,sys,shlex
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/ACTUAL_PREGO_PROJECT_LOCK_WAIT_DIAGNOSIS_ONCE.json';assert not out.exists();code=r'''from pathlib import Path
import json,time,subprocess
B=Path('/home/lc01/Zonglin Li/zonglin2');C=B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';c=json.loads(C.read_bytes());a=c['active_segment'];p=subprocess.run(['lslocks','--json','--notruncate','--output','PID,COMMAND,TYPE,MODE,PATH'],capture_output=True,text=True);locks=json.loads(p.stdout).get('locks',[])if p.returncode==0 else[];locks=[x for x in locks if str(B/'state')in str(x.get('path',''))];n=subprocess.run(['/usr/bin/nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True);x=subprocess.run(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],capture_output=True,text=True);print(json.dumps(dict(epoch=time.time(),canonical=dict(path=str(C),remaining=c['remaining_training_seconds'],active_owner=None if a is None else{k:a.get(k)for k in('owner_run_id','owner_parent_pid','kind','started_epoch')}),project_kernel_lock_modes=locks,GPU=n.stdout,compute=x.stdout,signals_lock_ops_models_SDK_Cwrites=0)))''';c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
finally:c.close()
