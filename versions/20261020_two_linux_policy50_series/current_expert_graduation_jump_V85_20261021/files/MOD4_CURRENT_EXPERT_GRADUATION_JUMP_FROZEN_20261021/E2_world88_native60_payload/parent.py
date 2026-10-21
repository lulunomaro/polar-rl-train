from pathlib import Path
import hashlib,json,os,psutil,signal,subprocess,sys,time,traceback,fcntl
B=Path(__file__).resolve().parent;cfg=json.loads((B/'FROZEN_CONFIG.json').read_bytes())
def put(name,value):
 with (B/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
if len(sys.argv)>1 and sys.argv[1]=='--detach':
 p=subprocess.Popen([sys.executable,'-u','-B',str(Path(__file__).resolve())],cwd=B,env=dict(os.environ),stdout=(B/'PARENT_FULL.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 q=psutil.Process(p.pid);print(json.dumps(dict(pid=p.pid,creation=q.create_time(),argv=q.cmdline(),root=str(B))));sys.exit(0)
lock=None;child=None
try:
 p=psutil.Process();put('PARENT_IDENTITY.json',dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=str(B),epoch=time.time()))
 lock=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 uuid=cfg['GPU_UUID'];line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if uuid in x);assert int(line.split(',')[-1])>7000
 assert psutil.virtual_memory().available>8*1024**3 and __import__('shutil').disk_usage(B).free>25*1024**3
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,CUDA_DEVICE_ORDER='PCI_BUS_ID',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');start=time.time()
 child=subprocess.Popen([cfg['python'],'-u','-B',str(B/'worker.py')],cwd=B,env=env,stdout=(B/'WORKER_FULL.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);cp=psutil.Process(child.pid);ident=dict(pid=child.pid,creation=cp.create_time(),argv=cp.cmdline(),root=str(B));put('CHILD_STARTED_ACTUAL.json',dict(epoch=start,worker=ident,source_SHA=cfg['source_SHA'],GPU_line=line,max_parent_seconds=cfg['wall_seconds'],no_optimizer=True))
 timeout=False
 try:rc=child.wait(timeout=cfg['wall_seconds'])
 except subprocess.TimeoutExpired:
  timeout=True;assert psutil.Process(child.pid).create_time()==ident['creation'];child.send_signal(signal.SIGINT);rc=child.wait(timeout=90)
 final=B/'out/FINAL.json';result=json.loads(final.read_bytes()) if final.exists() else None;errors=[str(p) for p in (B/'out').glob('*ORIGINAL_ERROR*.json')]
 put('PARENT_COMPLETE_ACTUAL.json',dict(epoch=time.time(),started_epoch=start,actual_child_waited=True,returncode=rc,own_timeout=timeout,final=result,errors=errors,passed=bool(rc==0 and result and result['passed_execution_not_skill'] and not errors and not timeout),no_training_or_canonical_write=True))
except BaseException:put('PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True))
finally:
 if child is not None and child.poll() is None:
  child.send_signal(signal.SIGINT);child.wait(timeout=90)
 if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 put('PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),all_own_children_waited=child is None or child.poll() is not None,own_eval_lease_released=True,original_training_locks_and_peers_untouched=True))
