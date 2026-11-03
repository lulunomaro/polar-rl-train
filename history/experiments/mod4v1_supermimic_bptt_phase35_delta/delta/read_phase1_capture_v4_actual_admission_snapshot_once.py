"""One own-root published metadata snapshot; not a watcher/admission/SDK/model read."""
from pathlib import Path
import sys,json,time,shlex
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ACTUAL_ADMISSION_SNAPSHOT.json';assert not out.exists()
d=json.loads((R/'reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json').read_bytes());assert d['returncode']==0 and d['actual_native_parent_Popen_calls']==1
root=d['root'];code=('ROOT=%r\n'%root)+r'''
from pathlib import Path
import json,time
root=Path(ROOT);assert root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks') and root.name.startswith('MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
names=['PARENT_STARTED.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json','PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json','cases/E3/WORKER_SCENE_READY.json','cases/E3/WORKER_EVAL_STARTED.json','cases/E3/WORKER_ERROR.json']
values={}
for rel in names:
 p=root/rel
 if not p.exists():values[rel]=None;continue
 with p.open('rb')as f:raw=f.read(262145)
 if len(raw)>262144:values[rel]={'projection_not_read_reason':'metadata_exceeds_bounded_snapshot_limit'}
 else:values[rel]=json.loads(raw)
wait=root/'BOUNDED_ORIGINAL_RESOURCE_WAIT.json'
if wait.exists():
 with wait.open('rb')as f:raw=f.read(1048577)
 assert len(raw)<=1048576;rows=json.loads(raw);values[wait.name]={'count':len(rows),'latest':rows[-1]if rows else None}
print(json.dumps({'epoch':time.time(),'root':str(root),'published_metadata':values,'model_raw_FINAL_trace_C_GPU_SDK_lock_signal_operations':0}))
'''
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();v=dict(kind='ONE_PUBLISHED_PHASE1_CAPTURE_ACTUAL_ADMISSION_SNAPSHOT_V4',returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:v['actual']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 assert rc==0,stderr
 a=v['actual']['published_metadata'];print(json.dumps(dict(report=str(out),actual_admission=a['ACTUAL_GROUP_ADMISSION.json'],children=a['CHILDREN.json'],barrier=a['GROUP_BARRIER_STATUS.json'],error=a['PARENT_ORIGINAL_ERROR.json'],exit_scope=a['PARENT_EXIT_SCOPE.json'],resource_wait=a.get('BOUNDED_ORIGINAL_RESOURCE_WAIT.json')),indent=2))
finally:c.close()
