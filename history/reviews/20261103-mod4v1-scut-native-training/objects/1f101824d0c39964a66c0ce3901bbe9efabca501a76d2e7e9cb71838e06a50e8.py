from pathlib import Path
import fcntl,json,os,runpy,sys,time,traceback,importlib.util,subprocess,hashlib
r=Path(__file__).resolve().parent;plan=json.loads((r/'PLAN.json').read_bytes());j=Path(plan['closed_root'])
spec=importlib.util.spec_from_file_location('original_closed_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
locks=[];worker=None;error=None
try:
 for p in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+plan['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 peer=json.loads((Path(plan['peer_root'])/'OWNER_EXIT.json').read_bytes())
 assert peer['all_own_waited']and peer['original_cost_settled']and peer['original_leases_released']
 o.resource(plan['GPU_UUID'])
 manifest=json.loads((r/'INSTALL_MANIFEST.json').read_bytes())
 for row in manifest:
  p=r/row['relative'];assert len(p.read_bytes())==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 task=json.loads((j/'TASK.json').read_bytes())
 env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=str(j/'SOURCE_PATHS.json')
 code="import sys,runpy;sys.path.insert(0,"+repr(task['package_root'])+");import mod4v1_scut;mod4v1_scut.__path__[:0]="+repr([str(r/'overlay'),task['module_overlay']])+";runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')"
 c=plan['checkpoint'];args=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile','jump270','--job-root',str(r/'evaluation'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA'],'--e0-source-diagnostic']
 for path in task['support']:args+=['--support',path]
 with (r/'WORKER.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B','-c',code,*args],env=env,cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks))
 o.put(r/'WORKER_IDENTITY.json',o.b.ident(worker.pid));rc=worker.wait()
 o.put(r/'WORKER_WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 if rc:raise RuntimeError('Actual diagnostic worker failed: '+str(rc))
except BaseException:
 error=traceback.format_exc();o.put(r/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,all_own_waited=worker is None or worker.poll()is not None,locks_released=True,optimizer_operations=0,ledger_writes=0))
