"""Human-directed finite GPU owner; no canonical access."""
from pathlib import Path
import fcntl,hashlib,json,os,shutil,subprocess,time,traceback
import psutil
J=Path(__file__).resolve().parent
STATE=Path('/home/lc01/Zonglin Li/zonglin2/state')
read=lambda p:json.loads(Path(p).read_bytes())
def put(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.partial')
 with tmp.open('w')as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def ident(pid):
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
def resource(uuid):
 line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
 apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
 row=[x.strip()for x in line.split(',')];assert row[0]==uuid and row[1]=='NVIDIA GeForce RTX 4090'and int(row[2])>15669 and uuid not in apps
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free;assert ram>64*1024**3 and disk>50*1024**3
 return dict(epoch=time.time(),line=line,apps=apps,ram=ram,disk=disk)
def environment(uuid):
 e=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for key in ['PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE']:e.pop(key,None)
 for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
  path=J/'private_runtime'/rel;path.mkdir(parents=True,exist_ok=True);e[key]=str(path)
 return e
def main():
 plan=read(J/'PLAN.json');uuid=plan['GPU_UUID'];process=evaluator=None;error=None;start=None
 assert plan['human_direct_no_ledger_admission']and plan['train_seconds']==3600 and plan['max_parent_seconds']==3900
 put(J/'OWNER_STARTED.json',dict(epoch=time.time(),run_id=plan['run_id'],identity=ident(os.getpid())))
 lock=(STATE/('three_expert_v2_'+uuid+'.lock')).open('rb+')
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);actual=resource(uuid);manifest=read(J/'INSTALL_MANIFEST.json')
  for row in manifest['files']:
   p=J/row['relative'];assert p.resolve().is_relative_to(J)and p.suffix not in ['.pt','.pth'];assert p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  for row in manifest['shared_text']:
   p=Path(row['path']);assert p.suffix not in ['.pt','.pth'];assert p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  start=time.time();task=dict(plan,owner_parent_pid=os.getpid(),kind='MOD4V2_FUDAN_DIRECT_FINITE',canonical_admission_bypassed_by_latest_human=True,canonical_reads=0,canonical_writes=0);put(J/'TASK.json',task)
  put(J/'ROOT_ADMISSION_ACTUAL.json',dict(epoch=start,resource=actual,private_GPU_EX=True,human_direct_no_ledger_admission=True,canonical_reads=0,canonical_writes=0,PT_reads=0))
  go=dict(kind=task['kind'],run_id=plan['run_id'],GPU_UUID=uuid,learning_started_epoch=start,save_deadline=start+3600,nominal_end_epoch=start+3900,max_parent_seconds=3900,exit_headroom_seconds=300);put(J/'GO_PRODUCTION.json',go)
  with(J/'WORKER.log').open('xb')as log:process=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'entry.py'),'train'],cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
  put(J/'WORKER_IDENTITY.json',ident(process.pid))
  while process.poll()is None:
   if time.time()>=go['save_deadline']and not(J/'STOP_AFTER_SAVE.json').exists():put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Original finite saveboundary',fullsave_required=True))
   put(J/'OWNER_CURRENT.json',dict(epoch=time.time(),worker=ident(process.pid),GO=go,direct_elapsed_seconds=time.time()-start,canonical_reads=0,canonical_writes=0));time.sleep(5)
  rc=process.wait();final=read(J/'production/FINAL.json')if(J/'production/FINAL.json').exists()else None;close=read(J/'production/APP_CLOSE_INTENT.json')if(J/'production/APP_CLOSE_INTENT.json').exists()else None
  okay=bool(rc==0 and final and final['passed_execution']and close and close['error']is None and close['env_closed'])
  put(J/'TRAIN_CLOSED.json',dict(epoch=time.time(),returncode=rc,all_own_waited=True,original_cost_settled=False,canonical_accounting_performed=False,human_direct_no_ledger_admission=True,passed_execution=okay,final=final,close=close))
  if okay and final['PPO_updates']>0:
   resource(uuid)
   with(J/'EVAL.log').open('xb')as log:evaluator=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'entry.py'),'evaluate'],cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
   put(J/'EVAL_IDENTITY.json',ident(evaluator.pid));erc=evaluator.wait();put(J/'EVAL_WAITED.json',dict(epoch=time.time(),returncode=erc,own_waited=True,result=read(J/'evaluation/RESULT.json')if(J/'evaluation/RESULT.json').exists()else None))
 except BaseException:
  error=traceback.format_exc();put(J/'OWNER_ERROR.json',dict(epoch=time.time(),error=error))
  if process is not None and process.poll()is None:
   put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own exception fullsaveclose',fullsave_required=True));process.wait()
 finally:
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();waited=(process is None or process.poll()is not None)and(evaluator is None or evaluator.poll()is not None)
  put(J/'OWNER_EXIT.json',dict(epoch=time.time(),run_id=plan['run_id'],error=error,all_own_waited=waited,original_cost_settled=False,original_leases_released=True,canonical_accounting_performed=False,human_direct_no_ledger_admission=True,no_new_budget_or_refund=True,canonical_reads=0,canonical_writes=0,actual_elapsed_seconds=None if start is None else time.time()-start))
 if error:raise RuntimeError(error)
if __name__=='__main__':main()
