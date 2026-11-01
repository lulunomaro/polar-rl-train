from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,traceback
P=Path(__file__).resolve().parent;T=json.loads((P/'TASK274.json').read_bytes())
def put(n,x):
 with(P/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
locks=[];worker=None;error=None;result=None;wait=None
try:
 canonical=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
 for path in(canonical.parent.parent/('three_expert_v2_'+T['GPU_UUID']+'.lock'),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
  f=path.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 c=json.loads(canonical.read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 line=subprocess.check_output(['nvidia-smi','-i',T['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();fields=[x.strip()for x in line.split(',')]
 assert fields[0]==T['GPU_UUID']and fields[1]=='NVIDIA GeForce RTX 4090'and int(fields[2])>15669 and int(fields[3])<=30 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(P).free>25*1024**3
 put('ACTUAL274_PRIVATE_SHARED_CNONE_AND_RESOURCE.json',dict(passed=True,epoch=time.time(),GPU=line,current_CNone=True,private_shared_EX=True,account_writes=0))
 put('TASK274_ADMITTED.json',dict(T,private_shared_EX_and_current_authority_admitted=True))
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=T['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',PYTHONNOUSERSITE='1')
 for k in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
 args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(P/'worker274_new272_H32_CUDA_no_optimizer_once.py')]
 with(P/'ACTUAL274_WORKER_STDOUT_STDERR.log').open('xb')as log:
  worker=subprocess.Popen(args,cwd=P,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,close_fds=True);p=psutil.Process(worker.pid);identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd());put('ACTUAL274_WORKER_IDENTITY_BEFORE_WAIT.json',identity)
  rc=worker.wait(timeout=900);wait=dict(epoch=time.time(),returncode=rc,identity=identity,original_waited=True);put('ACTUAL274_WORKER_WAITED.json',wait)
 q=P/'ACTUAL274_NEW272_H32_CUDA_ADMISSION_RESULT.json';result=json.loads(q.read_bytes())if q.is_file()else None
 assert rc==0 and result and result['passed']and result['optimizer_steps']==0 and result['actual_WM_updates']==0 and result['scratch_params_and_norms_restored_exact']and not(P/'ORIGINAL274_WORKER_ERROR.json').exists()
except BaseException:
 error=traceback.format_exc();put('ORIGINAL274_PARENT_ERROR.json',dict(epoch=time.time(),error=error,no_retry=True))
finally:
 if worker is not None:worker.wait()
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 put('ACTUAL274_ALL_OWN_WAITED_PRIVATE_SHARED_RELEASED.json',dict(epoch=time.time(),all_own_children_waited=worker is None or worker.poll()is not None,private_shared_EX_acquired=len(locks)==2,all_owned_locks_released=True,wait=wait))
print(json.dumps(dict(passed=error is None and bool(result and result['passed']),error=error,result=result,wait=wait,account_writes=0)))
