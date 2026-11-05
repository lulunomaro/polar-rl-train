"""Private GPU owner for one complete Newton hour and immediate independent80."""
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,traceback
J=Path(__file__).resolve().parent
STATE=Path('/home/lc01/Zonglin Li/zonglin2/state')
read=lambda p:json.loads(Path(p).read_bytes())

def put(path,value):
 path=Path(path);tmp=path.with_name(path.name+'.partial')
 with tmp.open('w')as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)

def ident(pid):
 p=psutil.Process(pid)
 return dict(pid=pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())

def resources(uuid):
 gpu=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True)
 apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
 row=[x.strip()for x in gpu.split(',')]
 assert row[0]==uuid and int(row[2])>15669 and uuid not in apps
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
 assert ram>64*1024**3 and disk>50*1024**3
 return dict(epoch=time.time(),gpu=gpu,apps=apps,ram=ram,disk=disk)

def environment(uuid):
 e=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',PYTHONNOUSERSITE='1')
 for key in ['PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE']:e.pop(key,None)
 for key,relative in {'TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','WARP_CACHE_PATH':'cache/warp','CUDA_CACHE_PATH':'cache/cuda','TORCH_HOME':'cache/torch'}.items():
  root=Path('/tmp')/('mod4n_'+hashlib.sha256(str(J).encode()).hexdigest()[:12])
  path=root/relative;path.mkdir(parents=True,exist_ok=True);e[key]=str(path)
 reference=read(J/'PLAN.json').get('warp_cache_reference')
 if reference:e['WARP_CACHE_PATH']=reference
 return e

def main():
 plan=read(J/'PLAN.json');uuid=plan['GPU_UUID'];process=evaluator=None;error=None;start=None;lock=None
 try:
  assert plan['human_direct_no_ledger_admission'] and plan['train_seconds']==3600 and plan['max_parent_seconds']==3900
  put(J/'OWNER_STARTED.json',dict(epoch=time.time(),identity=ident(os.getpid())))
  lock=(STATE/('three_expert_v2_'+uuid+'.lock')).open('rb+')
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);resource=resources(uuid)
  for row in read(J/'INSTALL_MANIFEST.json')['files']:
   p=J/row['relative'];assert p.resolve().is_relative_to(J)
   assert p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  start=time.time()
  put(J/'ROOT_ADMISSION_ACTUAL.json',dict(epoch=start,resource=resource,private_GPU_EX=True,canonical_reads=0,canonical_writes=0))
  go=dict(kind='MOD4V2_FUDAN_NEWTON_FINITE',run_id=plan['run_id'],GPU_UUID=uuid,
          learning_started_epoch=start,save_deadline=start+3600,nominal_end_epoch=start+3900,
          max_parent_seconds=3900,exit_headroom_seconds=300)
  put(J/'GO_PRODUCTION.json',go)
  with(J/'WORKER.log').open('xb')as log:
   process=subprocess.Popen([str(J/'run-newton.sh'),'-u','-B',str(J/'entry.py'),'train'],
       cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,
       stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
  worker_identity=dict(pid=process.pid,creation=psutil.Process(process.pid).create_time(),
                       launcher=str(J/'run-newton.sh'),entry=str(J/'entry.py'))
  put(J/'WORKER_IDENTITY.json',worker_identity)
  while process.poll()is None:
   if time.time()>=go['save_deadline']and not(J/'STOP_AFTER_SAVE.json').exists():
    put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Original hourly fullsave boundary'))
   put(J/'OWNER_CURRENT.json',dict(epoch=time.time(),worker=worker_identity,GO=go,
       elapsed=time.time()-start,canonical_reads=0,canonical_writes=0))
   time.sleep(5)
  rc=process.wait()
  final=read(J/'production/FINAL.json')if(J/'production/FINAL.json').exists()else None
  close=read(J/'production/APP_CLOSE_INTENT.json')if(J/'production/APP_CLOSE_INTENT.json').exists()else None
  okay=bool(rc==0 and final and final['passed_execution']and close and close['error']is None and close['env_closed'])
  put(J/'TRAIN_CLOSED.json',dict(epoch=time.time(),returncode=rc,all_own_waited=True,passed_execution=okay,final=final,close=close))
  if not okay:raise RuntimeError('Training did not complete with fullsave and safeclose')
  if final.get('PPO_updates',0)>0 or final.get('verified_BPTT_steps',0)>0:
   resources(uuid)
   with(J/'EVAL.log').open('xb')as log:
    evaluator=subprocess.Popen([str(J/'run-newton.sh'),'-u','-B',str(J/'entry.py'),'evaluate'],
        cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
   put(J/'EVAL_IDENTITY.json',dict(pid=evaluator.pid,creation=psutil.Process(evaluator.pid).create_time()))
   erc=evaluator.wait();result=read(J/'evaluation/RESULT.json')if(J/'evaluation/RESULT.json').exists()else None
   put(J/'EVAL_WAITED.json',dict(epoch=time.time(),returncode=erc,own_waited=True,result=result))
   assert erc==0 and result and result['passed_execution'],'Independent80 failed'
 except BaseException:
  error=traceback.format_exc();put(J/'OWNER_ERROR.json',dict(epoch=time.time(),error=error))
  if process is not None and process.poll()is None:
   put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own exception requires fullsave/close'));process.wait()
 finally:
  if evaluator is not None and evaluator.poll()is None:evaluator.wait()
  if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  put(J/'OWNER_EXIT.json',dict(epoch=time.time(),error=error,
      all_own_waited=(process is None or process.poll()is not None)and(evaluator is None or evaluator.poll()is not None),
      original_leases_released=True,canonical_reads=0,canonical_writes=0,
      actual_elapsed_seconds=None if start is None else time.time()-start))
 if error:raise RuntimeError(error)

if __name__=='__main__':main()
