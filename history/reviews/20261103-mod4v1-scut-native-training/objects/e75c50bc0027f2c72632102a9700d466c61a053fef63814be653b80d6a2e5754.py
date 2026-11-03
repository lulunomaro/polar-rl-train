from pathlib import Path
import fcntl,json,os,runpy,sys,time,traceback,importlib.util,subprocess,hashlib
r=Path(__file__).resolve().parent;plan=json.loads((r/'PLAN_NATIVE_REV3.json').read_bytes());j=Path(plan['closed_root'])
spec=importlib.util.spec_from_file_location('original_closed_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
locks=[];worker=None;error=None
try:
 for p in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+plan['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 peer=json.loads((Path(plan['peer_root'])/'OWNER_EXIT.json').read_bytes())
 assert peer['all_own_waited']and peer['original_cost_settled']and peer['original_leases_released']
 o.resource(plan['GPU_UUID'])
 manifest=json.loads((r/'INSTALL_MANIFEST03.json').read_bytes())
 for row in manifest:
  p=r/row['relative'];assert len(p.read_bytes())==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 task=json.loads((j/'TASK.json').read_bytes())
 source_registry=plan['source_paths'];source_raw=Path(source_registry['path']).read_bytes()
 assert len(source_raw)==source_registry['bytes']and hashlib.sha256(source_raw).hexdigest()==source_registry['SHA']
 o.put(r/'SOURCE_REGISTRY_RESOLVED03.json',dict(**source_registry,passed=True,checkpoint_reads=0,physics_steps=0))
 env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=source_registry['path']
 code="import sys,runpy;sys.path.insert(0,"+repr(task['package_root'])+");import mod4v1_scut;mod4v1_scut.__path__[:0]="+repr([str(r/'overlay03'),task['module_overlay']])+";runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')"
 c=plan['checkpoint'];args=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile','jump270','--job-root',str(r/'evaluation03'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA'],'--e0-source-diagnostic']
 for path in task['support']:args+=['--support',path]
 with (r/'WORKER03.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B','-c',code,*args],env=env,cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks))
 o.put(r/'WORKER_IDENTITY03.json',o.b.ident(worker.pid));rc=worker.wait()
 o.put(r/'WORKER_WAITED03.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 if rc or (r/'evaluation03/ERROR.json').exists()or not(r/'evaluation03/RESULT.json').exists():
  raise RuntimeError('Actual diagnostic worker failed or omitted complete result: '+str(rc))
except BaseException:
 error=traceback.format_exc();o.put(r/'ORIGINAL_ERROR03.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 o.put(r/'RELEASE03.json',dict(epoch=time.time(),error=error,all_own_waited=worker is None or worker.poll()is not None,locks_released=True,optimizer_operations=0,ledger_writes=0))
