from pathlib import Path
import argparse,fcntl,hashlib,json,os,psutil,shutil,subprocess,sys,time,traceback
from authority231 import fresh_authority,actual_authority_file,write,H
def read(p):return json.loads(Path(p).read_bytes())
def identity(p):return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--purpose-id',required=True);p.add_argument('--sdk-python',required=True);a=p.parse_args();J=a.job_root.resolve()
 plan=read(J/'PLAN231.json');expected=read(J/'EXPECTED227D_BINDING.json');assert a.purpose_id==plan['purpose_id']
 assert not (J/'PARENT231_ONCE_CONSUMED.json').exists();write(J/'PARENT231_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=a.purpose_id,metadata_probe=1,model_max_bytes_decode=1,num_envs=20000,controls_max=1200,physical_callbacks_max=9600,optimizer_steps=0,account_writes=0))
 authpath,auth=actual_authority_file(J,a.purpose_id,expected,'ACTUAL231_BEFORE_METADATA_AUTHORITY')
 source=J/'SOURCE_INSTALL231_ACTUAL.json';assert read(source)['actual_postcopy_fullSHA_verified']
 admission=dict(kind='ROOT_E2_FROM226_CPU_METADATA_ADMISSION_ACTUAL',passed=True,purpose_id=a.purpose_id,job_root=str(J),authority_report_SHA=H(authpath),original_global_serial_control_admitted=True,target_host='72',actual_SDK_python_launcher=a.sdk_python,model_asset_GPU_App_access=0,no_training_GO_or_budget_writer=True,actual_report_refs=[dict(path=str(source),bytes=source.stat().st_size,SHA=H(source))])
 ap=J/'ACTUAL231_CPU_METADATA_ADMISSION.json';write(ap,admission)
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
 cmd=[a.sdk_python,'-u','-B',str(J/'run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py'),'--job-root',str(J),'--actual-authority',str(authpath),'--metadata-admission',str(ap),'--sdk-python-launcher',a.sdk_python,'--purpose-id',a.purpose_id,'--timeout-seconds','360']
 with(J/'ACTUAL231_METADATA_ENTRY_STDOUT.log').open('xb')as log:
  q=subprocess.Popen(cmd,cwd=J,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);pid=identity(psutil.Process(q.pid));write(J/'ACTUAL231_METADATA_ENTRY_IDENTITY_BEFORE_WAIT.json',pid);rc=q.wait()
 write(J/'ACTUAL231_METADATA_ENTRY_WAIT.json',dict(returncode=rc,identity=pid,actual_waited=True));assert rc==0
 wait=read(J/'E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json');assert wait['passed'] and wait['returncode']==0 and wait['all_own_children_waited']
 locks=[];child=None;waited=None;error=None;runtime=None
 try:
  GPU=plan['GPU_UUID'];assert GPU=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and GPU!=expected['go']['w35_72']['GPU_UUID']
  fresh_authority(expected)
  private=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock');shared=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')
  for path in(private,shared):
   f=path.open('rb+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BaseException:f.close();raise
   locks.append(f)
  line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();v=[s.strip()for s in line.split(',')];ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
  assert v[0]==GPU and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669 and int(v[3])<=30 and ram>32*1024**3 and disk>25*1024**3
  lockreceipt=J/'ACTUAL231_HELD_PRIVATE_SHARED_RESOURCE.json';write(lockreceipt,dict(epoch=time.time(),passed=True,GPU_UUID=GPU,GPU_line=line,RAM_available=ram,disk_free=disk,private_EX_held=True,shared_EX_held=True,actual_holding_parent=identity(psutil.Process()),unknown_GPU_PID_scans=False,model_reads=0))
  target=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt');link=J/'source/E2_ADAPTED93_FINAL92.pt';link.parent.mkdir();assert not link.exists() and not link.is_symlink();link.symlink_to(target)
  assert link.is_symlink() and os.readlink(link)==str(target)
  materialization=dict(actual_completed=True,selected_formal_SHA=plan['model_SHA'],selected_formal_bytes=14615089,selected_target_path=str(target),job_relative='source/E2_ADAPTED93_FINAL92.pt',method='same_host_symlink',model_byte_reads_or_copies=0)
  write(J/'ACTUAL231_SELECTED_SOURCE_SYMLINK_ONLY.json',materialization)
  afterpath,after=actual_authority_file(J,a.purpose_id,expected,'ACTUAL231_AFTER_METADATA_BEFORE_GPU_AUTHORITY')
  runtime=dict(kind='ROOT_E2_FROM226_ACTUAL_RUNTIME_ADMISSION',passed=True,purpose_id=a.purpose_id,job_root=str(J),authority_report_SHA=H(afterpath),source_SHA=plan['model_SHA'],worker_SHA=plan['worker_SHA'],num_envs=20000,original_private_EX_held=True,original_shared_guard_passed=True,original_resources_passed=True,GPU_UUID=GPU,actual_holding_parent=identity(psutil.Process()),selected_private_lock_receipt_SHA=H(lockreceipt),no_new_training_GO_or_account_write=True,selected_source_materialization=materialization,actual_report_refs=[dict(path=str(lockreceipt),bytes=lockreceipt.stat().st_size,SHA=H(lockreceipt))])
  rp=J/'ACTUAL231_RUNTIME_ADMISSION.json';write(rp,runtime)
  args=[a.sdk_python,'-u','-B',str(J/'finalize_e2_from226_actual_evidence_ROOT_ONLY.py'),'--job-root',str(J),'--actual-wait',str(J/'E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json'),'--actual-authority',str(afterpath),'--purpose-id',a.purpose_id,'--actual-runtime-admission',str(rp)]
  with(J/'ACTUAL231_TYPED_TASK_STDOUT.log').open('xb')as log:q=subprocess.Popen(args,cwd=J,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=q.wait()
  assert rc==0 and read(J/'FROZEN_CASE_TASK.json')['actual_private_GPU_EX_held_by_parent']
  childenv=dict(env,CUDA_VISIBLE_DEVICES=GPU,PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for key in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):childenv.pop(key,None)
  for key,leaf in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
   p=J/'private'/leaf;p.mkdir(parents=True,exist_ok=True);childenv[key]=str(p)
  with(J/'ACTUAL231_E2_MEAN_STDOUT_STDERR.log').open('xb')as log:
   child=subprocess.Popen([a.sdk_python,'-u','-B',str(J/'evaluate_e2_world213.py'),'--job-root',str(J)],cwd=J,env=childenv,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
   ident=identity(psutil.Process(child.pid));write(J/'ACTUAL231_E2_WORKER_IDENTITY_BEFORE_WAIT.json',ident)
   rc=child.wait(timeout=1800);waited=dict(epoch=time.time(),returncode=rc,original_waited=True,identity=ident);write(J/'ACTUAL231_E2_ORIGINAL_WAIT.json',waited)
  O=J/'frozen_regression';result=read(O/'BOUNDED_FROZEN_E2_N20K_PROFILES_ACTUAL.json');counts=read(O/'SOURCE213_SELECTED_PT_READ_COUNTS.json')
  errors=[str(p)for p in O.rglob('*ERROR*.json')]+[str(p)for p in O.glob('*EXCEPTION*.json')]
  assert rc==0 and result['passed_execution'] and not errors and read(O/'APP_CLOSING.json')
 except BaseException:
  error=traceback.format_exc();write(J/'ACTUAL231_E2_ORIGINAL_PARENT_ERROR.json',dict(error=error,no_auto_retry=True))
 finally:
  if child is not None:
   rc=child.wait()
   if waited is None:waited=dict(epoch=time.time(),returncode=rc,actual_waited=True);write(J/'ACTUAL231_FINAL_ORIGINAL_CHILD_WAIT.json',waited)
  acquired=len(locks)==2
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  write(J/'ACTUAL231_ALL_WAITED_PRIVATE_SHARED_RELEASED.json',dict(epoch=time.time(),all_own_children_waited=child is None or child.poll()is not None,private_shared_EX_acquired=acquired,all_owned_locks_released=True,original_wait=waited,no_signal_calls=True))
 write(J/'ACTUAL231_PARENT_RETURNED.json',dict(epoch=time.time(),passed_execution=error is None,error=error,runtime=runtime,original_wait=waited,model_byte_decodes_max=1,optimizer_or_account_writes=0,APPclose_requested_marker_optional_return=True))
 print(json.dumps(dict(passed_execution=error is None,original_error=error)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  if '--job-root'in sys.argv:
   J=Path(sys.argv[sys.argv.index('--job-root')+1]);write(J/('ACTUAL231_METADATA_OR_PRE_GPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_auto_retry=True))
  raise
