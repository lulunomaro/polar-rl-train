"""One read-only current-identity/producer-state/resource snapshot after host restart.
No signals, lock changes, source checkpoints, SDK, raw telemetry, or canonical writes.
"""
from pathlib import Path
import json,sys,shlex
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'))
from project_connector import connect72
out=R/'reports/REPAIRED_OWNER_ACTUAL_STATE_ROUND6_ONCE.json'
assert not out.exists()
m=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())
code=r'''from pathlib import Path
import json,time,psutil,subprocess
J=Path(%r);pid=%d;creation=%r;B=Path('/home/lc01/Zonglin Li/zonglin2')
v=dict(epoch=time.time(),root=str(J),exact_owner_live=False,identity=None,metadata={},roles={},source_PT_raw_SDK_signals_lock_mutation_Cwrites=0)
try:
 p=psutil.Process(pid);v['exact_owner_live']=abs(p.create_time()-creation)<.001 and p.status()!=psutil.STATUS_ZOMBIE;v['identity']=dict(pid=pid,creation=p.create_time(),status=p.status(),cmdline=p.cmdline())
except psutil.NoSuchProcess:pass
for n in ('OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','PREGO_RESOURCE_WAIT.json','COHORT_FINAL.json'):
 f=J/n;v['metadata'][n]=json.loads(f.read_bytes()) if f.exists() else None
for role in ('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'):
 d=J/'roles'/role;row={}
 for n in ('GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','WORKER_IDENTITY_ACTUAL.json','PARENT_WAITED_ACTUAL.json','production/STARTUP_ACTUAL_NATIVE_SUPERMIMIC.json','production/PROGRESS.json','production/FINAL.json','production/WORKER_ERROR.json'):
  f=d/n;row[n]=json.loads(f.read_bytes()) if f.exists() else None
 v['roles'][role]=row
if not v['exact_owner_live']:
 f=J/'OWNER_FULL_STDOUT_STDERR.log'
 if f.exists():
  with f.open('rb')as z:z.seek(max(0,f.stat().st_size-18000));v['own_closed_parent_log_tail']=z.read().decode('utf-8','replace')
C=B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';c=json.loads(C.read_bytes());a=c['active_segment'];v['original_canonical_readonly']=dict(path=str(C),remaining=c['remaining_training_seconds'],active_owner=None if a is None else{k:a.get(k)for k in ('owner_run_id','owner_parent_pid','kind','started_epoch')})
p=subprocess.run(['lslocks','--json','--notruncate','--output','PID,COMMAND,TYPE,MODE,PATH'],capture_output=True,text=True);v['project_kernel_lock_modes']=[x for x in json.loads(p.stdout).get('locks',[])if str(B/'state')in str(x.get('path',''))]if p.returncode==0 else dict(returncode=p.returncode,stderr=p.stderr)
for k,cmd in [('GPU',['/usr/bin/nvidia-smi','--query-gpu=index,uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits']),('compute',['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'])]:
 p=subprocess.run(cmd,capture_output=True,text=True);v[k]=dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
print(json.dumps(v))
'''%(m['root'],m['pid'],m['creation'])
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=40);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err)
 v=json.loads(txt);out.write_text(json.dumps(v,indent=2),encoding='utf-8')
 print(out);print(json.dumps(dict(epoch=v['epoch'],exact_owner_live=v['exact_owner_live'],identity=v['identity'],metadata=v['metadata'],canonical=v['original_canonical_readonly'],GPU=v['GPU'],compute=v['compute'],roles={r:{k:x for k,x in row.items() if x is not None}for r,row in v['roles'].items()}),indent=2))
finally:c.close()
