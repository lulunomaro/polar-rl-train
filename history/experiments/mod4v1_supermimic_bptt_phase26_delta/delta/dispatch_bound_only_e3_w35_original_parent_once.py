"""Dispatch one original-gated reference parent via a source-only actual-wait recorder.
Neither controller acquires resources nor opens a model; original parent does so.
"""
from pathlib import Path
import json,sys,time,shlex,hashlib,ast
R=Path(__file__).resolve().parent;marker=R/'BOUND_ONLY_E3_W35_V1_PARENT_DISPATCH_ONCE.json';out=R/'reports/BOUND_ONLY_E3_W35_V1_ACTUAL_PARENT_DISPATCH_V1.json';assert not marker.exists()and not out.exists();stage=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_ACTUAL_SOURCE_STAGE_V1.json').read_bytes());assert stage['returncode']==0 and stage['stage']['staged']and stage['stage']['parent_launches']==0;quality=json.loads((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes());assert quality['qualified_reference_execution']and quality['qualified_candidate_execution'];root=stage['root'];gid=stage['group_id'];expected=stage['stage_complete_SHA'];controller=(R/'bound_probe_parent_actual_wait_controller_v1.py').read_bytes();ast.parse(controller);controller_SHA=hashlib.sha256(controller).hexdigest();controlpath=root+'/bound_probe_parent_actual_wait_controller_v1.py'
code=r'''
from pathlib import Path
import os,json,time,hashlib,subprocess
root=Path(ROOT);assert root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks')and root.name==GROUP_ID;raw=(root/'STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==STAGE_SHA and json.loads(raw)['staged'];parent=root/'single_gpu_e3_w35_bound_only_parent_v1.py';raw=parent.read_bytes();assert len(raw)==9348 and hashlib.sha256(raw).hexdigest()=='63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80';control=root/'bound_probe_parent_actual_wait_controller_v1.py';raw=control.read_bytes();assert len(raw)==CONTROL_BYTES and hashlib.sha256(raw).hexdigest()==CONTROL_SHA
for name in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','BOUND_PROBE_PARENT_CONTROLLER_STARTED_V1.json','BOUND_PROBE_PARENT_DISPATCH_REQUEST_V1.json','BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'):assert not(root/name).exists(),name
request=dict(kind='ONE_BOUND_PROBE_CONTROLLER_AND_ONE_ORIGINAL_NATIVE_PARENT_NOT_RESOURCE_ADMISSION',epoch=time.time(),root=str(root),group_id=root.name,requested_roles=['E3','W35'],policy_variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1',stage_complete_SHA=STAGE_SHA,parent_source_SHA='63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80',actual_wait_controller_source_SHA=CONTROL_SHA,prior_qualified_quality_screen_SHA=PRIOR_SCREEN_SHA,actual_original_parent_resource_gates_unchanged=True,dispatcher_C_models_SDK_locks_signals=0)
with(root/'BOUND_PROBE_PARENT_DISPATCH_REQUEST_V1.json').open('x')as f:json.dump(request,f,indent=2);f.flush();os.fsync(f.fileno())
log=(root/'BOUND_PROBE_PARENT_CONTROLLER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(control),'--root',str(root),'--stage-sha',STAGE_SHA],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();text=(Path('/proc')/str(p.pid)/'stat').read_text();v=text[text.rfind(')')+2:].split();request['controller']=dict(pid=p.pid,linux_start_ticks=v[19],state=v[0]);until=time.monotonic()+15
while time.monotonic()<until:
 path=root/'BOUND_PROBE_PARENT_DISPATCH_RECEIPT_V1.json'
 if path.exists():
  receipt=json.loads(path.read_bytes());assert receipt['controller']['pid']==p.pid and receipt['group_id']==root.name and receipt['actual_native_parent_Popen_calls']==1;request['parent']=receipt['parent'];request['actual_native_parent_Popen_calls']=1;print(json.dumps(request));break
 if p.poll()is not None:raise RuntimeError('Source lifecycle controller ended before native parent receipt; inspect own log, do not replay')
 time.sleep(.05)
else:raise TimeoutError('Native parent PID receipt not yet published; preserve single controller, do not replay')
'''.replace('ROOT',repr(root)).replace('GROUP_ID',repr(gid)).replace('STAGE_SHA',repr(expected)).replace('CONTROL_BYTES',repr(len(controller))).replace('CONTROL_SHA',repr(controller_SHA)).replace('PRIOR_SCREEN_SHA',repr(hashlib.sha256((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes()).hexdigest()));ast.parse(code);marker.write_text(json.dumps(dict(root=root,group_id=gid,epoch=time.time(),purpose='New embedded zero-update bound-only probe, original resource gates, actual external parent wait',controller_SHA=controller_SHA),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(controlpath)
 except FileNotFoundError:pass
 else:raise AssertionError('Controller source already exists in unused reference root')
 with s.open(controlpath,'wb')as f:f.write(controller)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(root=root,group_id=gid,epoch=time.time(),returncode=rc,stdout=text,stderr=err,controller_source_bytes=len(controller),controller_source_SHA=controller_SHA);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,err;v['receipt']=json.loads(text);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
finally:s.close();c.close()
