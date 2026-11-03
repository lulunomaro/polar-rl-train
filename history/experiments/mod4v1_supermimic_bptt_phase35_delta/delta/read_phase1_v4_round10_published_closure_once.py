"""NEW bounded own-root metadata recovery snapshot; no parent/watcher restart."""
from pathlib import Path
import json,sys,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_V4_ROUND10_PUBLISHED_CLOSURE_RECOVERY_SNAPSHOT_V1.json';assert not out.exists();d=json.loads((R/'reports/PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_ORIGINAL_PARENT_DISPATCH_ONCE.json').read_bytes());assert d['returncode']==0 and d['actual_native_parent_Popen_calls']==1;root=d['root']
code=('ROOT=%r;EXPECTED=%r\n'%(root,{x:d[x]for x in('parent','controller')}))+r'''
from pathlib import Path
import json,time,hashlib
root=Path(ROOT);assert root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks')and root.name.startswith('MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_')
names=['PARENT_STARTED.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json','PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json','cases/E3/WORKER_SCENE_READY.json','cases/E3/WORKER_EVAL_STARTED.json','cases/E3/WORKER_ERROR.json']
docs={};pins={}
for rel in names:
 p=root/rel
 if not p.exists():docs[rel]=None;continue
 with p.open('rb')as f:raw=f.read(262145)
 assert len(raw)<=262144;docs[rel]=json.loads(raw);pins[rel]=dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())
p=root/'BOUNDED_ORIGINAL_RESOURCE_WAIT.json'
if p.exists():
 with p.open('rb')as f:raw=f.read(1048577)
 assert len(raw)<=1048576;v=json.loads(raw);docs[p.name]=dict(count=len(v),first=v[0]if v else None,latest=v[-1]if v else None)
identities={}
for label,wanted in EXPECTED.items():
 p=Path('/proc')/str(wanted['pid'])/'stat'
 if not p.exists():identities[label]=dict(expected=wanted,observed=None,same_start_ticks=False);continue
 txt=p.read_text();parts=txt[txt.rfind(')')+2:].split();actual=dict(pid=wanted['pid'],linux_start_ticks=parts[19],state=parts[0]);identities[label]=dict(expected=wanted,observed=actual,same_start_ticks=str(wanted['linux_start_ticks'])==parts[19])
print(json.dumps(dict(epoch=time.time(),root=str(root),published_metadata=docs,metadata_identities=pins,known_own_process_identities=identities,model_raw_FINAL_trace_C_GPU_SDK_lock_signal_parent_or_watcher_operations=0)))
'''
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();v=dict(kind='ROUND10_NEW_OWN_PUBLISHED_CLOSURE_SNAPSHOT_NOT_RETRY',epoch=time.time(),returncode=rc,stdout=stdout,stderr=stderr,old_local_job='pwsh-04ffe22045de4981',old_job_current_result='unknown job; job_list empty',old_closed_pointer_exists=False,old_marker_preserved=True,source_child_gap_review_failed_without_artifact=True)
 if rc==0:v['actual']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 assert rc==0,stderr
 a=v['actual']['published_metadata'];print(json.dumps(dict(report=str(out),actual_admission=a['ACTUAL_GROUP_ADMISSION.json'],children=a['CHILDREN.json'],parent_error=a['PARENT_ORIGINAL_ERROR.json'],parent_exit=a['PARENT_EXIT_SCOPE.json'],outer_actual_wait=a['PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'],resource_wait=a.get('BOUNDED_ORIGINAL_RESOURCE_WAIT.json'),known_own_processes=v['actual']['known_own_process_identities']),indent=2))
finally:c.close()
