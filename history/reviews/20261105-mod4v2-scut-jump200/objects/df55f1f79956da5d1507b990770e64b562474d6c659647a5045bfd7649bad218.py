from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,psutil,subprocess,time,traceback
r=Path(__file__).resolve().parent;j=r.parent
spec=importlib.util.spec_from_file_location('original_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
p=json.loads((r/'PLAN.json').read_bytes());lock=None;worker=None;error=None
try:
 for expected in p['original_identities']:
  if psutil.pid_exists(expected['pid']):
   proc=psutil.Process(expected['pid'])
   assert proc.create_time()!=expected['creation']or proc.status()==psutil.STATUS_ZOMBIE
 source=Path(p['checkpoint']['path'])
 with source.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==p['checkpoint']['SHA']
 assert source.stat().st_size==p['checkpoint']['bytes']
 lock=(o.STATE/('three_expert_v2_'+p['GPU_UUID']+'.lock')).open('rb+')
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 o.put(r/'RESOURCE.json',o.resources(p['GPU_UUID']))
 with(r/'EVAL.log').open('xb')as log:
  worker=subprocess.Popen([str(j/'run-newton.sh'),'-u','-B',str(r/'evaluate.py')],cwd=r,
   env=o.environment(p['GPU_UUID']),stdout=log,stderr=subprocess.STDOUT,
   stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
 o.put(r/'WORKER.json',dict(pid=worker.pid,creation=psutil.Process(worker.pid).create_time()))
 rc=worker.wait();o.put(r/'WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 result=json.loads((r/'evaluation/RESULT.json').read_bytes())if(r/'evaluation/RESULT.json').exists()else None
 assert rc==0 and result and result['passed_execution']
except BaseException:
 error=traceback.format_exc();o.put(r/'ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,own_waited=worker is None or worker.poll()is not None,
  GPU_lock_released=True,optimizer_operations=0,canonical_reads=0,canonical_writes=0,
  original_window_not_extended=True,source_kind='Surviving FIRST1941; not a final2842 checkpoint'))
if error:raise RuntimeError(error)
