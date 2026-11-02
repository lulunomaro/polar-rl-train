"""Own E1canonical GPU1 bounded fresh80/n20k, original EX+finiteSH only.
Resource waiting45s<=1800 holds ZERO partialleases/PT/SDK; oneSDKdispatch.
No GPU0/canonical/budget/PPO/foreignprocess action.
"""
from pathlib import Path
import fcntl,hashlib,json,os,shutil,signal,subprocess,time,traceback
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')
def put(n,v):
 p=B/n;t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(v,indent=2,allow_nan=False));t.replace(p)
def main():
 assert B.is_relative_to(OWN/'tasks') and B.name.startswith('MOD4V1_E1_') and not (B/'PARENT_STARTED.json').exists()
 plan=json.loads((B/'E1_ACTUAL_PLAN.json').read_bytes());assert plan['canonical'] in ('CURB141','SLOPE135') and plan['GPU_index']==0 and plan['controls']==24
 mode=plan['mode'];assert mode in ('fresh80','n20k');limit=720 if mode=='fresh80' else 1200;workerlimit=690 if mode=='fresh80' else 900
 put('PARENT_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),mode=mode,SDK_parent_limit_s=limit,SDK_worker_limit_s=workerlimit,resource_wait_interval_s=45,resource_wait_cap_s=1800,PT_reads_by_supervisor=0,canonical_access=False))
 private=shared=child=log=None;privateheld=sharedheld=False;errors=[];started=time.monotonic();active_started=None;checks=[]
 def release():
  nonlocal private,shared,privateheld,sharedheld
  if shared is not None:
   if sharedheld:fcntl.flock(shared,fcntl.LOCK_UN)
   shared.close();shared=None;sharedheld=False
  if private is not None:
   if privateheld:fcntl.flock(private,fcntl.LOCK_UN)
   private.close();private=None;privateheld=False
 try:
  for r in plan['files']:
   p=B/r['relative'];assert p.suffix.lower() not in ('.pt','.pth','.ckpt','.onnx','.safetensors');assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['relative']
  uuid=plan['GPU_UUID'];assert uuid=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
  import psutil
  while True:
   reason=None;resource=None;rows=[];memory=disk=0
   try:
    private=(OWN/'state'/('three_expert_v2_'+uuid+'.lock')).open('rb+');fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB);privateheld=True
    shared=(OWN/'state/finite_environment_validation.lock').open('rb+');fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB);sharedheld=True
    apps=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);rows=[s for s in apps.splitlines() if s.split(',')[0].strip()==uuid]
    if rows:reason='SelectedGPU1_compute_process_exists'
    memory=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
    resource=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();v=[s.strip() for s in resource.split(',')]
    if not(v[0]==uuid and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669 and int(v[3])<=30 and memory>32*1024**3 and disk>25*1024**3):reason='Original_GPU_hostmemory_disk_resource_bounds'
   except BlockingIOError:reason='Original_GPUprivateEX_or_finiteSH_busy_mode_unchanged'
   if reason is None:break
   release();elapsed=time.monotonic()-started;checks.append(dict(epoch=time.time(),elapsed_s=elapsed,reason=reason,resource_line=resource,compute_rows=rows,all_partialleases_released=True,SDK_started=False,PT_opens=0));put('RESOURCE_WAIT_CHECKS.json',checks)
   if elapsed>=1800:put('WAIT_RESOURCE_TIMEOUT.json',dict(status='WAIT_RESOURCE_TIMEOUT',elapsed_s=elapsed,SDK_started=False,locks_held=False,PT_reads=0));return
   time.sleep(min(45,1800-elapsed))
  active_started=time.monotonic();d=B/'gpu1';d.mkdir(exist_ok=False);task=dict(plan['task'],GPU_UUID=uuid,actual_original_private_EX_held=True,actual_original_finiteSH_held=True)
  (d/'TASK.json').write_text(json.dumps(task,indent=2));(d/'RESOURCE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),GPU_line=resource,GPU_compute_rows=rows,host_available_bytes=memory,disk_free_bytes=disk,private_EX=True,finiteSH=True,canonical_access=False),indent=2))
  with (B/'SDK_DISPATCH_ONCE.json').open('x',encoding='utf-8') as f:json.dump(dict(epoch=time.time(),mode=mode,scope='E1canonicalboundedNoPPO',no_production_GO=True),f,indent=2)
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  for k,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
   p=d/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
  log=(d/'SDK_FULL_STDOUT_STDERR.log').open('xb');child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/plan['worker']),'--job-root',str(B),'--task',str(d/'TASK.json'),'--out',str(d/'out')],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=(private.fileno(),shared.fileno()),start_new_session=True);log.close();log=None
  put('CHILDREN.json',[dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),GPU_UUID=uuid,root=str(d),mode=mode,canonical=plan['canonical'],own_processgroup=True)])
  rc=child.wait(timeout=min(workerlimit,max(1,limit-(time.monotonic()-active_started)-30)))
  actual=d/'out'/plan['complete_basename'];error=d/'out'/plan['error_basename'];data=json.loads(actual.read_bytes()) if actual.exists() else None
  passed=bool(rc==0 and data and data.get('passed') and (d/'out/ENV_CLOSE_RETURNED.json').exists() and (d/'out/APP_CLOSING.json').exists() and not error.exists())
  row=dict(pid=child.pid,returncode=rc,actual_waited=True,passed=passed,actual_complete=data,expected_complete_basename=plan['complete_basename'],error_json_exists=error.exists(),env_close_returned=(d/'out/ENV_CLOSE_RETURNED.json').exists(),App_close_bridge=(d/'out/APP_CLOSING.json').exists())
  put('TERMINAL_ROWS.json',[row]);put('FINAL.json',dict(status='E1_CANONICAL_BOUNDED_'+mode+'_FINISHED',passed=passed,canonical=plan['canonical'],rows=[row],source_PT_reads_by_supervisor=0,canonical_access=False,productionGO_or_PPO=False,skill_graduation=False,active_SDK_wall_s=time.monotonic()-active_started,resource_wait_s=active_started-started))
 except BaseException:errors.append(traceback.format_exc());put('PARENT_ORIGINAL_ERROR.json',dict(errors=errors,no_auto_replay=True,PT_reads_by_supervisor=0,canonical_access=False))
 finally:
  if log:log.close()
  if child is not None and child.poll() is None:
   child.terminate()
   try:child.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=15)
  waited=child is None or child.poll() is not None;hadprivate=privateheld;hadshared=sharedheld
  if waited:release()
  put('PARENT_EXIT_SCOPE.json',dict(epoch=time.time(),all_own_children_waited=waited,original_private_lock_released=bool(hadprivate and waited),original_shared_lock_released=bool(hadshared and waited),all_partialleases_released=not privateheld and not sharedheld,no_foreign_scope_touched=True,canonical_access=False,errors=errors,active_SDK_wall_s=(time.monotonic()-active_started) if active_started else None,total_wall_s=time.monotonic()-started))
if __name__=='__main__':main()
