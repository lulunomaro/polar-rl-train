"""Unique leased Windows parent, same nativeGPU OSlock,15s save-stop guardian.

No kill, automatic extra stages, SSH, canonical write or previous-once replay.
"""
from pathlib import Path
import argparse,json,hashlib,os,sys,time,shutil,subprocess,traceback,msvcrt
import psutil
P=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,value):
 p=Path(p);temp=p.with_suffix(p.suffix+'.partial')
 with temp.open('wb') as f:f.write(json.dumps(value,indent=2).encode());f.flush();os.fsync(f.fileno())
 os.replace(temp,p)
def identity(pid):
 try:
  x=psutil.Process(pid);return dict(pid=pid,created=x.create_time(),argv=x.cmdline(),cwd=x.cwd(),name=x.name())
 except psutil.Error:return None
def still(row):
 now=identity(row['pid']);return now is not None and now['created']==row['created']
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease',required=True);parser.add_argument('--manifest',required=True);parser.add_argument('--attempt',required=True);parser.add_argument('--python',required=True);parser.add_argument('--runtime-root',required=True);parser.add_argument('--mode',required=True,choices=['sdk','native','fullrestore','train']);parser.add_argument('--train-seconds',type=int,default=3600);a=parser.parse_args()
 assert os.name=='nt' and 0<a.train_seconds<=7200
 lease=json.loads(Path(a.lease).read_bytes());manifest=json.loads(Path(a.manifest).read_bytes());A=Path(a.attempt).resolve();scope=Path(lease['scope_root']).resolve();R=Path(a.runtime_root).resolve()
 environment_root=Path(lease['environment_root']).resolve();guard=Path(lease['shared_gpu_lock']).resolve()
 assert scope.is_relative_to(environment_root) and scope!=environment_root and R==scope/'runtime20k'
 assert guard==environment_root/'WINDOWS4090_GPU_EXCLUSIVE.lock','single environment-wide native GPU lock'
 assert manifest['environment_root']==str(environment_root) and manifest['scope_root']==str(scope) and manifest['shared_gpu_lock']==str(guard)
 assert A.is_relative_to(scope/'attempts') and not A.exists(),'one new independent attempt only'
 assert lease['approved_GPU_scope'] and lease['mode']==a.mode and Path(lease['attempt_path']).resolve()==A and lease['manifest_sha256']==H(a.manifest)
 assert lease['worker_sha256']==H(P/'windows4090_repair_worker.py') and lease['source_sha256']==manifest['source']['sha256']
 assert manifest['approved_for_new_Windows4090_scope'] and manifest['root_review_actual']['GPU_lease_explicitly_granted'] and manifest['num_envs']==20000 and manifest['seed']==20260928
 reference=manifest['original005_budget_reference']
 assert reference['authorized_seconds']==1188000 and reference['base_seconds']==36000
 conservative=reference.get('planning_mode')=='conservative_all_walltime_since_actual_saved_snapshot_lower_bound'
 if conservative:
  applied=json.loads(Path(reference['actual_original_saved_reference']['path']).read_bytes())
  assert applied['authorized_after']==1188000 and applied['extension_records']==reference['extension_records_count']==7 and applied['old_six_extensions_unchanged'] and applied['applied_once']
  assert reference['aggregate_extension_seconds']+reference['base_seconds']==1188000 and reference['individual_extension_record_values_not_reconstructed']
  assert reference['snapshot_epoch']==applied['epoch'] and reference['remaining_snapshot_seconds']==applied['remaining_seconds']
  assert reference['pending_cost_interval_already_covered_by_elapsed_walltime'] and reference['no_second_subtraction_of_covered_localcost']
  sixth=reference['sixth_budget_applied_reference'];assert H(sixth['path'])==sixth['sha256'];six=json.loads(Path(sixth['path']).read_bytes())
  assert six['authorized_before']==468000 and six['authorized_after']==applied['authorized_before']==828000 and six['added_seconds']==applied['added_seconds']==360000 and six['applied_once']
 else:
  assert len(reference['extension_seconds'])==7 and sum(reference['extension_seconds'])+reference['base_seconds']==1188000
 assert reference['canonical_reconciliation_pending'] and not reference['new_budget_authority']
 assert reference['actual_original_saved_reference']['sha256']==H(reference['actual_original_saved_reference']['path'])
 assert reference['pending_parent_cost_index']['sha256']==H(reference['pending_parent_cost_index']['path'])
 assert manifest['resource_guard_reference']['sha256']==H(manifest['resource_guard_reference']['path'])
 assert H(manifest['target_CPU_receipt']['path'])==manifest['target_CPU_receipt']['sha256']
 cpu=json.loads(Path(manifest['target_CPU_receipt']['path']).read_bytes());assert cpu['passed'] and cpu['actual_target_environment_root']==str(environment_root) and cpu['no_GPU_or_PPO']
 if a.mode=='train':
  remaining=max(0.,reference['remaining_snapshot_seconds']-(time.time()-reference['snapshot_epoch'])) if conservative else reference['remaining_snapshot_seconds']-reference['pending_unique_actual_parent_cost_seconds']
  assert remaining>=a.train_seconds+min(64800.,.13*remaining),'otherexpert/gate repair planning protection; no reserve or ledgerwrite'
 assert Path(a.python).resolve()==Path(lease['python']).resolve() and R==Path(lease['runtime_root']).resolve()
 assert H(manifest['source']['path'])==manifest['source']['sha256']
 for row in manifest['sourcefreeze_files']:
  assert H(row['path'])==row['sha256'],row['path']
 if a.mode in ('fullrestore','train'):
  required=manifest['required_stage_receipts'][a.mode]
  assert {row['kind'] for row in required}==({'sdk','native','fullrestore'} if a.mode=='train' else {'sdk','native'})
  for row in required:
   assert H(row['path'])==row['sha256'];r=json.loads(Path(row['path']).read_bytes());assert r['passed']
   assert H(row['owner_EXIT_path'])==row['owner_EXIT_sha256'];exitrow=json.loads(Path(row['owner_EXIT_path']).read_bytes());assert exitrow['passed'] and exitrow['worker_exitcode']==0 and exitrow['own_processes_actual_absent']
   assert r['pid']==exitrow['child']['pid'] and not still(exitrow['child']) and not still(exitrow['parent']),'own stage PID/start not closed'
   contract=r['complete_physical_command_DR_contract'];assert contract['passed'] and contract['all_static_D0D7_recipes_exact_to_complete_source'] and contract['actual_ground_query_error_m']<=1e-6 and contract['actual_height_reward_formula_error']<=1e-6
   if row['kind'] in ('sdk','native'):
    expected=300 if row['kind']=='sdk' else 144;assert r['mode']==row['kind'] and r['no_PPO'] and r['actual_controls']==expected and r['actual_callbacks']==expected*4
   else:
    assert r['no_PPO'] and r['actual_controls']==120 and r['actual_callbacks']==480
    assert r['latest']['sha256']==manifest['source']['sha256'] and Path(r['latest']['path']).resolve()==Path(manifest['source']['path']).resolve()
  if a.mode=='train':
   assert manifest['source']['sha256']!='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a','formal uses actual own fullrestore-save; do not reinitialize fromCPU candidate'
   assert a.train_seconds==3600,'first new formal approved3600s'
 A.mkdir(parents=True);O=A/'output';O.mkdir();snap=A/'src_snapshot';snap.mkdir();started=time.time();process=None;rows=[];lock=None;lock_held=False;known={}
 atomic(A/'LEASE_CONSUMED_ACTUAL.json',dict(epoch=started,lease=str(Path(a.lease).resolve()),lease_sha256=H(a.lease),case_id=lease['case_id'],mode=a.mode,one_unique_attempt=True,no_GPU_started_yet=True))
 try:
  # Sourcefreeze before any GPU process. Each filename mapping and SHA is retained.
  freezes=[]
  for i,row in enumerate(manifest['sourcefreeze_files']):
   source=Path(row['path']);target=snap/(str(i)+'_'+source.name);shutil.copy2(source,target);assert H(target)==row['sha256'];freezes.append(dict(source=str(source),snapshot=str(target),sha256=H(target)))
  atomic(A/'ACTUAL_PRELAUNCH_SOURCEFREEZE.json',dict(epoch=time.time(),files=freezes,manifest_sha256=H(a.manifest),source_SHA=manifest['source']['sha256']))
  need=manifest['resource_guards'];free=shutil.disk_usage(scope).free;RAM=psutil.virtual_memory().available
  result=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits','-i','0'],capture_output=True,text=True,check=True);GPU=int(result.stdout.strip())*1024*1024
  admission=dict(epoch=time.time(),durable_free_bytes=free,RAM_available_bytes=RAM,GPU_free_bytes=GPU,requirements=need,no_guard_reduction_or_evidence_deletion=True)
  admission['passed']=free>=need['durable_free_bytes'] and RAM>=need['RAM_available_bytes'] and GPU>=need['GPU_free_bytes'];atomic(A/'RESOURCE_ADMISSION_ACTUAL.json',admission);assert admission['passed'],'actual resource guard rejected beforeGPU'
  # Persistent file existence is not lock ownership. Parent keeps this native OS
  # lock until child and observed descendants are actually absent.
  lock=guard.open('a+b');lock.seek(0)
  if guard.stat().st_size==0:lock.write(b'0');lock.flush();os.fsync(lock.fileno())
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
  lock_held=True
  env=os.environ.copy();env['MOD4_WINDOWS_GPU_LOCK_PARENT_PID']=str(os.getpid());env['MOD4_WINDOWS_PARENT_START_EPOCH']=str(started)
  stop=A/'STOP_AFTER_SAVE';cmd=[a.python,str(P/'windows4090_repair_worker.py'),'--runtime-root',str(R),'--manifest',str(Path(a.manifest).resolve()),'--source-checkpoint',manifest['source']['path'],'--source-sha',manifest['source']['sha256'],'--output',str(O),'--stop-after-save',str(stop),'--mode',a.mode,'--train-seconds',str(a.train_seconds),'--probe-controls','120','--headless','--device','cuda:0']
  log=(A/'worker_stdout.log').open('wb');process=subprocess.Popen(cmd,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  child=identity(process.pid);assert child is not None
  atomic(A/'DISPATCH_RECEIPT.json',dict(epoch=time.time(),parent=identity(os.getpid()),child=child,argv=cmd,source_SHA=manifest['source']['sha256'],mode=a.mode,target_seconds=a.train_seconds,shared_native_OSlock=str(guard),OSlock_held=True,source_full20k_no_projection=True))
  known={child['pid']:child}
  while True:
   if process.poll() is None:
    try:
     for x in psutil.Process(process.pid).children(recursive=True):
      row=identity(x.pid)
      if row:known[row['pid']]=row
    except psutil.Error:pass
   alive=[x for x in known.values() if still(x)]
   progress=json.loads((O/'WINDOWS4090_PPO_PROGRESS.json').read_bytes()) if (O/'WINDOWS4090_PPO_PROGRESS.json').exists() else None
   if a.mode=='train' and time.time()-started>=a.train_seconds and not stop.exists():
    atomic(stop,dict(epoch=time.time(),reason='bounded3600s_request_save_after_current_update',no_kill=True))
   row=dict(epoch=time.time(),parent=identity(os.getpid()),child=identity(process.pid),own_alive_processes=alive,mode=a.mode,actual_progress=progress,OSlock_held=True,STOP_AFTER_SAVE=stop.exists(),no_kill_hotpatch_or_budgetwrite=True)
   atomic(A/'GUARDIAN_CURRENT.json',row)
   with (A/'guardian_history.ndjson').open('ab') as f:f.write(json.dumps(row).encode()+b'\n');f.flush();os.fsync(f.fileno())
   if process.poll() is not None and not alive:break
   time.sleep(15)
  log.close();code=process.returncode;expected='WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json' if a.mode=='train' else 'FULLRESTORE_PHYSICAL_PROBE_PASSED.json' if a.mode=='fullrestore' else 'PROBE_COMPLETE.json'
  receipt=json.loads((O/expected).read_bytes()) if (O/expected).exists() else None
  passed=code==0 and receipt is not None and receipt.get('passed',False) and not (O/'ORIGINAL_ERROR.json').exists()
  atomic(A/'EXIT_RECEIPT.json',dict(epoch=time.time(),parent=identity(os.getpid()),child=child,worker_exitcode=code,own_processes_actual_absent=True,expected_complete_receipt=expected,passed=passed,actual_parent_load_learn_save_exit_seconds=time.time()-started,mode=a.mode,no_PPO=a.mode!='train',failed_learning_startup_cost_retained=a.mode=='train' and progress is None,canonical_reconciliation_pending=a.mode=='train',canonical_not_written_or_copied=True,worker_returned_receipt_present=(O/'WORKER_RETURNED_NATURALLY.json').exists(),worker_returned_absence_not_fabricated=True,OSlock_release_follows_parent_boundary=True))
  if not passed:raise AssertionError('own stage originalfailure preserved; no automatic rerun')
 except BaseException:
  atomic(A/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),process=identity(process.pid) if process else None,mode=a.mode,canonical_not_written=True,no_automatic_rerun_kill_or_source_hotpatch=True));raise
 finally:
  if lock is not None:
   if not lock_held:lock.close()
   elif (process is None or process.poll() is not None) and not any(still(x) for x in known.values()):
    lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
    finally:lock.close()
    atomic(A/'PARENT_OSLOCK_RELEASED_ACTUAL.json',dict(epoch=time.time(),parent_pid=os.getpid(),child_actual_exit=process is None or process.poll() is not None,shared_lock=str(guard),native_OSlock_released=True,persistent_file_not_deleted=True))
   else:
    # Do not terminate an active trainer because parent inspection failed. Keep
    # protection while it saves/exits; original failure remains retained.
    while process.poll() is None or any(still(x) for x in known.values()):
     if process.poll() is None:
      try:
       for x in psutil.Process(process.pid).children(recursive=True):
        row=identity(x.pid)
        if row:known[row['pid']]=row
      except psutil.Error:pass
     time.sleep(15)
    lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
  if not (A/'EXIT_RECEIPT.json').exists():
   # An original parent observer/guard rejection is retained as failed.  Even
   # when it must wait for its own child to save naturally, its unique actual
   # load-to-exit tail still needs a receipt, never an invented successful pass.
   original_progress=json.loads((O/'WINDOWS4090_PPO_PROGRESS.json').read_bytes()) if (O/'WINDOWS4090_PPO_PROGRESS.json').exists() else None
   atomic(A/'EXIT_RECEIPT.json',dict(epoch=time.time(),parent=identity(os.getpid()),child=known.get(process.pid) if process else None,worker_exitcode=process.returncode if process else None,own_processes_actual_absent=(process is None or process.poll() is not None) and not any(still(x) for x in known.values()),passed=False,original_parent_failure_preserved=True,actual_parent_load_learn_save_exit_seconds=time.time()-started,mode=a.mode,no_PPO=a.mode!='train',failed_learning_startup_cost_retained=a.mode=='train' and original_progress is None,actual_PPO_progress_if_saved=original_progress,canonical_reconciliation_pending=a.mode=='train',canonical_not_written_or_copied=True,OSlock_released_after_actual_own_exit=True,no_worker_for_prelaunch_resource_rejection=process is None))
if __name__=='__main__':main()
