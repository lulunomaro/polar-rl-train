"""One original-gated capture parent, using own actual-Popen.wait controller.
No resource acquisition, model read, SDK call, signal or canonical write here.
"""
from pathlib import Path
import sys,json,hashlib,time,shlex,ast
R=Path(__file__).resolve().parent

def verify_prior_closed_import_failure():
 p=json.loads((R/'PHASE1_E3_CAPTURE_V1_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(p['path']).read_bytes());w=v['outer_actual_parent_wait'];e=v['parent_exit_scope'];assert v['status']=='FAIL_CLOSED_CAPTURE_EXECUTION' and w['actual_parent_p_wait_returned'] and w['returncode']==1 and e['all_own_children_waited'] and e['original_single_GPU_private_EX_released'] and e['original_global_finite_EX_released'];assert "No module named 'launch_storage_contract'" in v['published_metadata']['cases/E3/WORKER_ERROR.json']['error']
 fix=json.loads((R/'reports/PHASE1_WORKER_V2_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert fix['tests_run']==96 and fix['failures']==fix['errors']==0 and fix['source13_unchanged_after_test'];return v['root']
prior_consumed_root=verify_prior_closed_import_failure()

out=R/'reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json'
marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_PARENT_DISPATCH_STARTED_ONCE.json'
assert not out.exists()and not marker.exists(),'Capture parent purpose already consumed'
stage=json.loads((R/'reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json').read_bytes());assert stage['returncode']==0 and stage['receipt']['materialized']is True and stage['receipt']['parent_launches']==0 and stage['receipt']['metadata_validation']['passed'] and stage['receipt']['metadata_validation']['source_derivation_version']==2 and len(stage['receipt']['metadata_validation']['original_helper_bootstrap']['sources'])==2
mi=json.loads((R/'reports/PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1.json').read_bytes());assert mi['returncode']==0 and mi['receipt']['status']=='PASS' and not mi['receipt']['forbidden_modules_loaded']
q=json.loads((R/'reports/PHASE1_ACTUATION_REAL_CPU_V1.json').read_bytes());assert q['returncode']==0 and q['receipt']['status']=='PASS'
root=stage['group_root'];gid=stage['group_id'];sha=stage['stage_receipt_SHA256'];name='phase1_capture_parent_actual_wait_controller_v1.py'
raw=(R/'source_phase1_capture_controller_v1'/name).read_bytes();ast.parse(raw);control_SHA=hashlib.sha256(raw).hexdigest();assert(len(raw),control_SHA)==(3824,'95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831')
code=('ROOT=%r; GROUP_ID=%r; STAGE_SHA=%r; CONTROL_SHA=%r\n'%(root,gid,sha,control_SHA))+r'''
from pathlib import Path
import os,json,time,hashlib,subprocess
B=Path('/home/lc01/Zonglin Li/zonglin2');root=Path(ROOT)
assert root.parent==B/'tasks'and root.name==GROUP_ID and root.name.startswith('MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_')
raw=(root/'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==STAGE_SHA
stage=json.loads(raw);assert stage['materialized']is True and stage['parent_launches']==0 and stage['purpose']=='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
parent=root/'single_gpu_passive_capture_parent_v1.py';raw=parent.read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41')
control=root/'phase1_capture_parent_actual_wait_controller_v1.py';raw=control.read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(3824,CONTROL_SHA)
for n in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json','PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json','PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'):assert not(root/n).exists(),n
request=dict(kind='ONE_PHASE1_CAPTURE_CONTROLLER_AND_ORIGINAL_PARENT_NOT_RESOURCE_ADMISSION_V1',epoch=time.time(),root=str(root),group_id=root.name,requested_roles=['E3'],purpose='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN',stage_receipt_SHA256=STAGE_SHA,parent_source_SHA='d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41',controller_source_SHA=CONTROL_SHA,actual_original_parent_resource_gates_unchanged=True,SDK_scene_or_skill_admission=False,dispatcher_model_SDK_C_lock_signal_operations=0)
with(root/'PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json').open('x')as f:json.dump(request,f,indent=2);f.flush();os.fsync(f.fileno())
log=(root/'PHASE1_CAPTURE_CONTROLLER_STDOUT_STDERR.log').open('xb')
p=subprocess.Popen([str(B/'run-python.sh'),'-u','-B',str(control),'--root',str(root),'--stage-sha',STAGE_SHA],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
text=(Path('/proc')/str(p.pid)/'stat').read_text();v=text[text.rfind(')')+2:].split();request['controller']=dict(pid=p.pid,linux_start_ticks=v[19],state=v[0]);until=time.monotonic()+15
while time.monotonic()<until:
 path=root/'PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json'
 if path.exists():
  receipt=json.loads(path.read_bytes());assert receipt['controller']['pid']==p.pid and receipt['group_id']==root.name and receipt['actual_native_parent_Popen_calls']==1;request['parent']=receipt['parent'];request['actual_native_parent_Popen_calls']=1;print(json.dumps(request));break
 if p.poll()is not None:raise RuntimeError('Controller ended before receipt; preserve root and inspect; do not replay')
 time.sleep(.05)
else:raise TimeoutError('Parent receipt unpublished; preserve existing single controller, never replay')
'''
ast.parse(code)
with marker.open('x',encoding='utf-8')as f:json.dump(dict(epoch=time.time(),root=root,group_id=gid,stage_receipt_SHA256=sha,controller_source_SHA=control_SHA,purpose='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'),f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(root+'/'+name,'wx')as f:f.write(raw)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status()
 result=dict(kind='PHASE1_CAPTURE_SINGLE_ORIGINAL_PARENT_DISPATCH_RESULT_V2',epoch=time.time(),root=root,group_id=gid,GPU_UUID=stage['GPU_UUID'],stage_receipt_SHA256=sha,returncode=rc,stdout=stdout,stderr=stderr,controller_source_bytes=len(raw),controller_source_SHA=control_SHA)
 if rc==0:result.update(json.loads(stdout))
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 assert rc==0,stderr
 print(json.dumps(result,indent=2))
finally:s.close();c.close()
