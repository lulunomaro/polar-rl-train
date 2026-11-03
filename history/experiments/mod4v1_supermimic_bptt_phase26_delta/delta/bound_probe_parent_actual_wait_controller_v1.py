"""Own bound-probe-parent lifecycle recorder: actual Popen.wait, no resource/SDK work.
Original sealed bound-probe parent remains solely responsible for all child waits,
EX leases, original deadlines, error handling and read-only canonical checks.
"""
from pathlib import Path
import argparse,json,hashlib,os,subprocess,time,traceback
B=Path('/home/lc01/Zonglin Li/zonglin2');PARENT=(9348,'63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80')
def identity(pid):
 text=(Path('/proc')/str(pid)/'stat').read_text();v=text[text.rfind(')')+2:].split();return dict(pid=pid,linux_start_ticks=v[19],state=v[0])
def put(root,name,value):
 path=root/name;part=path.with_suffix(path.suffix+'.partial')
 with part.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
 assert not path.exists();part.replace(path)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--stage-sha',required=True);a=parser.parse_args();root=a.root;assert root.is_absolute()and root.parent==B/'tasks'and root.name.startswith('MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_');raw=(root/'STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==a.stage_sha and json.loads(raw)['staged'];parent=root/'single_gpu_e3_w35_bound_only_parent_v1.py';raw=parent.read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==PARENT
 for name in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','BOUND_PROBE_PARENT_CONTROLLER_STARTED_V1.json','BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'):assert not(root/name).exists(),name
 own=identity(os.getpid());put(root,'BOUND_PROBE_PARENT_CONTROLLER_STARTED_V1.json',dict(kind='OWN_BOUND_PROBE_PARENT_ACTUAL_WAIT_CONTROLLER_V1',epoch=time.time(),controller=own,parent_source_SHA=PARENT[1],controller_resource_SDK_model_C_lock_or_signal_operations=0));child=None;child_identity=None;rc=None;errors=[];started=time.time()
 try:
  log=(root/'BOUND_PROBE_PARENT_FULL_STDOUT_STDERR.log').open('xb');child=subprocess.Popen([str(B/'run-python.sh'),'-u','-B',str(parent)],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();child_identity=identity(child.pid);put(root,'BOUND_PROBE_PARENT_DISPATCH_RECEIPT_V1.json',dict(kind='ONE_ORIGINAL_BOUND_PROBE_PARENT_POPEN_NOT_RESOURCE_ADMISSION',epoch=time.time(),root=str(root),group_id=root.name,controller=own,parent=child_identity,parent_source_SHA=PARENT[1],actual_native_parent_Popen_calls=1,SDK_scene_or_skill_admission=False));rc=child.wait()
 except BaseException:
  errors.append(traceback.format_exc());put(root,'BOUND_PROBE_PARENT_CONTROLLER_ERROR_V1.json',dict(errors=errors,epoch=time.time(),controller=own))
 finally:
  if child is not None:
   if rc is None:rc=child.wait()
   put(root,'BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json',dict(kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_BOUND_PROBE_V1',epoch=time.time(),group_id=root.name,controller=own,parent=child_identity or dict(pid=child.pid),parent_source_SHA=PARENT[1],actual_native_parent_Popen_calls=1,actual_parent_p_wait_returned=True,returncode=rc,controller_errors=errors,wall_seconds=time.time()-started,original_parent_resource_close_wait_not_replaced=True,controller_resource_SDK_model_C_lock_or_signal_operations=0))
 return rc if rc is not None and not errors else 1
if __name__=='__main__':raise SystemExit(main())
