"""Future one-seed thin outer actual-wait recorder. SOURCE definitions only.

No stage/dispatch is performed while authoring or testing this SOURCE package.
The complete original good-holdout parent alone owns resources, SDK children,
canonical read-only checks, deadlines, error handling and both EX releases.
"""
from pathlib import Path
import argparse,json,hashlib,os,subprocess,time,traceback
import good_holdout_contract as contract
B=Path(contract.BASE)
PARENT=contract.PARENT_PIN
STAGE_FILE=contract.STAGE_NAME
_BINDING={}


def identity(pid):
 text=(Path('/proc')/str(pid)/'stat').read_text();v=text[text.rfind(')')+2:].split();return dict(pid=pid,linux_start_ticks=v[19],state=v[0])


def put(root,name,value):
 for key,expected in _BINDING.items():contract.need(key not in value or value[key]==expected,'controller binding conflict: '+key)
 value=dict(_BINDING,**value)
 path=root/name;part=path.with_suffix(path.suffix+'.partial')
 with part.open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
 assert not path.exists();part.replace(path)


def bounded(path,maximum):
 contract.need(not path.is_symlink()and path.is_file(),'own materialized regular metadata/source required')
 with path.open('rb')as stream:raw=stream.read(maximum+1)
 contract.need(len(raw)<=maximum,'original bounded metadata/source exceeded')
 return raw


def validate_launch(root,group_id,seed,gpu_uuid,stage_sha):
 contract.require_final_pins()
 contract.root_identity(str(root),group_id,seed,gpu_uuid)
 contract.need(root.is_dir()and not root.is_symlink(),'actual materialized own root required')
 cursor=root
 while cursor!=B/'tasks':
  contract.need(not cursor.is_symlink(),'materialized root ancestor symlink')
  cursor=cursor.parent
 stage_raw=bounded(root/STAGE_FILE,contract.GROUP_MAX)
 plan_raw=bounded(root/'GROUP_PLAN.json',contract.PLAN_MAX)
 parent=root/contract.PARENT_NAME;raw=bounded(parent,PARENT[0])
 stage,plan=contract.validate_stage(stage_raw,plan_raw,raw,root=str(root),group_id=group_id,seed=seed,gpu_uuid=gpu_uuid,stage_sha=stage_sha)
 for relative,pin in contract.OVERLAY_PINS.items():
  path=root/relative
  contract.need(path.resolve().is_relative_to(root.resolve()),'materialized SOURCE alias escapes own root')
  source=bounded(path,pin[0]);contract.need((len(source),contract.H(source))==tuple(pin),'complete staged good20 bytes differ: '+relative)
 own_source=Path(__file__).read_bytes()
 contract.need((len(own_source),contract.H(own_source))==contract.CONTROLLER_SOURCE_PIN,'exact own controller SOURCE differs')
 for name in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json',contract.STARTED,contract.DISPATCH,contract.WAITED,contract.ERROR):contract.need(not(root/name).exists(),'one-use lifecycle root already consumed: '+name)
 return parent,dict(root=str(root),group_id=group_id,seed=seed,GPU_UUID=gpu_uuid,evaluation_purpose=contract.purpose(seed),stage_receipt_SHA256=contract.H(stage_raw),GROUP_PLAN_bytes=len(plan_raw),GROUP_PLAN_SHA256=contract.H(plan_raw),controller_source_SHA=contract.H(own_source))


def main():
 global _BINDING
 contract.require_final_pins()
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--group-id',required=True);parser.add_argument('--seed',type=int,choices=contract.SEEDS,required=True);parser.add_argument('--gpu-uuid',required=True);parser.add_argument('--stage-sha',required=True);a=parser.parse_args();root=a.root
 parent,_BINDING=validate_launch(root,a.group_id,a.seed,a.gpu_uuid,a.stage_sha)
 own=identity(os.getpid());put(root,contract.STARTED,dict(kind=contract.STARTED_KIND,epoch=time.time(),controller=own,parent_source_SHA=PARENT[1],controller_resource_SDK_model_C_lock_or_signal_operations=0));child=None;child_identity=None;rc=None;errors=[];started=time.time()
 try:
  log=(root/'GOOD_HOLDOUT_PARENT_FULL_STDOUT_STDERR.log').open('xb');child=subprocess.Popen([str(B/'run-python.sh'),'-u','-B',str(parent)],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();child_identity=identity(child.pid);put(root,contract.DISPATCH,dict(kind=contract.DISPATCH_KIND,epoch=time.time(),root=str(root),group_id=root.name,controller=own,parent=child_identity,parent_source_SHA=PARENT[1],actual_native_parent_Popen_calls=1,SDK_scene_or_skill_admission=False));rc=child.wait()
 except BaseException:
  errors.append(traceback.format_exc());put(root,contract.ERROR,dict(errors=errors,epoch=time.time(),controller=own))
 finally:
  if child is not None:
   if rc is None:rc=child.wait()
   put(root,contract.WAITED,dict(kind=contract.WAITED_KIND,epoch=time.time(),group_id=root.name,controller=own,parent=child_identity or dict(pid=child.pid),parent_source_SHA=PARENT[1],actual_native_parent_Popen_calls=1,actual_parent_p_wait_returned=True,returncode=rc,controller_errors=errors,wall_seconds=time.time()-started,original_parent_resource_close_wait_not_replaced=True,controller_resource_SDK_model_C_lock_or_signal_operations=0))
 return rc if rc is not None and not errors else 1


if __name__=='__main__':raise SystemExit(main())
