"""Finite model-free SDK admission using the original per-GPU private lock contract.
No canonical write and no old once/launcher/worker is replayed.
"""
from pathlib import Path
import os,sys,json,time,hashlib,fcntl,subprocess,traceback,shutil
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')
def put(n,v):
 p=B/n;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2,allow_nan=False));q.replace(p)
def main():
 assert B.is_relative_to(OWN/'tasks');assert not(B/'PARENT_STARTED.json').exists()
 cfg=json.loads((B/'PLAN.json').read_bytes());put('PARENT_STARTED.json',{'pid':os.getpid(),'epoch':time.time(),'model_opens':0,'canonical_writes':0})
 locks=[];children=[];errors=[];shared=None
 try:
  for row in cfg['files']:
   p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
  canonical=OWN/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';budget=json.loads(canonical.read_bytes())
  put('PARALLEL_MODEL_FREE_SCOPE.json',{'canonical_writes':0,'other_owner_unchanged':True,'other_active_owner_pid':(budget['active_segment'] or {}).get('owner_parent_pid'),'native_property_probe_only':True})
  assert budget['remaining_training_seconds']>budget['finite_minimum_remaining_seconds']
  for spec in cfg['gpus']:
   fd=(OWN/'state'/('three_expert_v2_'+spec['uuid']+'.lock')).open('rb+');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(fd)
  shared=(OWN/'state/finite_environment_validation.lock').open('rb+');fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB)
  apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
  assert all(spec['uuid'] not in apps for spec in cfg['gpus']),'A planned GPU has a compute process'
  import psutil
  assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
  for spec,fd in zip(cfg['gpus'],locks):
   resource=subprocess.check_output(['/usr/bin/nvidia-smi','-i',spec['uuid'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[v.strip() for v in resource.split(',')]
   assert a[0]==spec['uuid'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30
   d=B/spec['label'];d.mkdir();task={'kind':'MOD4V1_NEW_NATIVE_NO_PT','GPU_UUID':spec['uuid'],'asset':str(B/'assets/robot.usd'),'asset_sha256':cfg['asset_sha256'],'contract_sha256':cfg['contract_sha256'],'worker_sha256':cfg['worker_sha256'],'actual_original_private_EX_held':True}
   (d/'TASK.json').write_text(json.dumps(task,indent=2));(d/'RESOURCE_ACTUAL.json').write_text(json.dumps({'epoch':time.time(),'line':resource,'private_EX':True,'canonical_before':None,'source_model_opens':0},indent=2))
   env=dict(os.environ,CUDA_VISIBLE_DEVICES=spec['uuid'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
   for name in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(name,None)
   for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
    p=d/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
   log=(d/'SDK_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'native_mod4v1_probe.py'),'--task',str(d/'TASK.json')],cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=(fd.fileno(),),start_new_session=True);log.close();children.append((spec,d,p));put('CHILDREN.json',[{'label':x['label'],'GPU_UUID':x['uuid'],'pid':p.pid,'root':str(d)} for x,d,p in children])
  terminal=[]
  for spec,d,p in children:
   rc=p.wait(timeout=720);data=json.loads((d/'NATIVE_DATA_COMPLETE.json').read_bytes()) if(d/'NATIVE_DATA_COMPLETE.json').exists() else None
   terminal.append({'label':spec['label'],'GPU_UUID':spec['uuid'],'pid':p.pid,'returncode':rc,'actual_waited':True,'data_complete':data,'App_close_bridge':(d/'APP_CLOSING.json').exists(),'passed':bool(rc==0 and data and data.get('passed') and (d/'APP_CLOSING.json').exists())});put('TERMINAL_ROWS.json',terminal)
  put('FINAL.json',{'passed':all(t['passed'] for t in terminal),'rows':terminal,'model_opens':0,'optimizer_updates':0,'canonical_writes':0,'epoch':time.time()})
 except BaseException:
  errors.append(traceback.format_exc());put('PARENT_ORIGINAL_ERROR.json',{'errors':errors,'no_old_once_replayed':True})
 finally:
  for spec,d,p in children:
   if p.poll() is None:
    p.terminate()
    try:p.wait(timeout=30)
    except subprocess.TimeoutExpired:pass
  waited=all(p.poll() is not None for _,_,p in children)
  if waited:
   for fd in locks:fcntl.flock(fd,fcntl.LOCK_UN)
  for fd in locks:fd.close()
  if shared is not None:
   if waited:fcntl.flock(shared,fcntl.LOCK_UN)
   shared.close()
  put('PARENT_EXIT_SCOPE.json',{'epoch':time.time(),'all_own_children_waited':waited,'private_locks_released':waited,'if_unwaited_child_inherits_lock':True,'errors':errors})
if __name__=='__main__':main()
