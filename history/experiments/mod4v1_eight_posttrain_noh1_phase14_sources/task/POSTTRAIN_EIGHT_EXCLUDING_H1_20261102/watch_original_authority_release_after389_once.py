"""Oneboundedread-onlyoriginalauthorityreleasewatch. No retry/locks/SDK/models/GO orwriter; GPUqueryonlyafteroriginalownerbecomesNone."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
marker=D/'AUTHORITY_RELEASE_WATCH_AFTER389_ONCE.json';out=D/'reports/ORIGINAL_AUTHORITY_RELEASE_AFTER389_WATCH_RESULT.json';assert not marker.exists()and not out.exists();marker.write_text(json.dumps({'baseline_owner_pid':1458549,'max_seconds':3600,'read_interval_seconds':60,'no_retry_or_parent_or_model_launch':True},indent=2),encoding='utf-8');code="""from pathlib import Path
import json,time,subprocess
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');start=time.time();end=time.monotonic()+3600;last=None;changes=[]
while True:
 c=json.loads(p.read_bytes());a=c['active_segment'];identity=None if a is None else(a.get('owner_parent_pid',a.get('pid')),a.get('kind'))
 if identity!=last:changes.append({'epoch':time.time(),'identity':identity});last=identity
 if a is None:
  gpu=subprocess.check_output(['/usr/bin/nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);v={'kind':'ORIGINAL_CANONICAL_OWNER_RELEASE_OBSERVED_NOT_ADMISSION','epoch':time.time(),'started_epoch':start,'canonical_generation':c['authority_generation'],'remaining':c['remaining_training_seconds'],'reserve':c['finite_minimum_remaining_seconds'],'owner':None,'GPU_snapshot':gpu,'owner_changes':changes,'no_locks_PTOpen_SDK_GO_or_writer':True};print(json.dumps(v));break
 if time.monotonic()>=end:print(json.dumps({'kind':'BOUNDED_AUTHORITY_WATCH3600_STILL_BUSY_NOT_BLOCKED_GOAL','epoch':time.time(),'owner_changes':changes,'owner':identity,'remaining':c['remaining_training_seconds'],'no_PTOpen_SDK_GO_or_writer':True}));break
 time.sleep(60)
""";c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=3700);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
finally:c.close()
