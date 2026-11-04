from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,subprocess,time,traceback
r=Path(__file__).resolve().parent;plan=json.loads((r/'PLAN_FIRST_AXIS.json').read_bytes());j=Path(plan['closed_root'])
s=importlib.util.spec_from_file_location('closed_mod4_original_owner',j/'owner.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
locks=[];worker=None;error=None
try:
 for path in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+plan['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  stream=path.open('rb+');locks.append(stream);fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 release=json.loads((j/'OWNER_EXIT.json').read_bytes());assert release['all_own_waited']and release['original_cost_settled']and release['original_leases_released']
 resource=o.resource(plan['GPU_UUID']);o.put(r/'GPU_ADMISSION_FIRST_AXIS.json',resource)
 for row in json.loads((r/'INSTALL_MANIFEST_FIRST_AXIS.json').read_bytes()):
  value=(r/row['relative']).read_bytes();assert len(value)==row['bytes']and hashlib.sha256(value).hexdigest()==row['SHA']
 registry=plan['source_registry'];value=Path(registry['path']).read_bytes();assert len(value)==registry['bytes']and hashlib.sha256(value).hexdigest()==registry['SHA']
 o.put(r/'SOURCE_REGISTRY_FIRST_AXIS.json',dict(**registry,verified=True))
 task=json.loads((j/'TASK.json').read_bytes());env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=registry['path']
 overlays=[str(r/'overlay_first_axis')]+task.get('module_overlays',[task['module_overlay']])
 code="import sys,runpy;sys.path.insert(0,"+repr(task['package_root'])+");import mod4v1_scut;mod4v1_scut.__path__[:0]="+repr(overlays)+";runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')"
 c=plan['checkpoint'];args=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile',task['profile'],'--job-root',str(r/'evaluation_first_axis'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA'],'--repair-target-limits','--repair-first-axis']
 for path in task['support']:args+=['--support',path]
 with(r/'WORKER_FIRST_AXIS.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B','-c',code,*args],env=env,cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks))
 o.put(r/'WORKER_IDENTITY_FIRST_AXIS.json',o.b.ident(worker.pid));rc=worker.wait()
 o.put(r/'WORKER_WAITED_FIRST_AXIS.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 result=r/'evaluation_first_axis/RESULT.json'
 if rc or(r/'evaluation_first_axis/ERROR.json').exists()or not result.exists()or not json.loads(result.read_bytes())['passed_execution']:
  raise RuntimeError('Target-limit diagnostic failed or omitted complete result: '+str(rc))
except BaseException:
 error=traceback.format_exc();o.put(r/'ERROR_FIRST_AXIS.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 for stream in reversed(locks):fcntl.flock(stream,fcntl.LOCK_UN);stream.close()
 o.put(r/'RELEASE_FIRST_AXIS.json',dict(epoch=time.time(),error=error,all_own_waited=worker is None or worker.poll()is not None,locks_released=True,optimizer_operations=0,ledger_writes=0))
