from pathlib import Path
import sys,os,json,time,hashlib,subprocess,shutil,msvcrt
D=Path(__file__).resolve().parent
def main():
 assert not (D/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists(),'LocalGPU executionpaused by latesthuman; thisroot isCPUprepared only'
 name=sys.argv[1];folder=D/'attempts'/name;assert not folder.exists()
 assert '--lease' in sys.argv and '--source-proof' in sys.argv and '--local-init-checkpoint' in sys.argv
 lease_path=Path(sys.argv[sys.argv.index('--lease')+1]);lease=json.loads(lease_path.read_bytes())
 assert lease['GPU_lease_granted_by_root'] is True and lease['target_root']==str(D)
 assert lease['worker_sha256']==hashlib.sha256((D/'local_scope_worker.py').read_bytes()).hexdigest()
 assert lease['runtime_sha256']==hashlib.sha256((D/'local_training_runtime.py').read_bytes()).hexdigest()
 assert lease['integration_sha256']==hashlib.sha256((D/'action_effective_repair_integration.py').read_bytes()).hexdigest()
 mode=sys.argv[sys.argv.index('--mode')+1];repair_mode=sys.argv[sys.argv.index('--repair-mode')+1]
 from action_effective_source_admission import source_guard,resources
 source_guard(sys.argv[sys.argv.index('--source-proof')+1],sys.argv[sys.argv.index('--local-init-checkpoint')+1],repair_mode)
 guard=resources(3600 if mode=='train' else 0);assert guard['passed'],guard
 if mode=='train':
  assert '--train-seconds' in sys.argv and int(sys.argv[sys.argv.index('--train-seconds')+1])==3600
  admission=json.loads((D/'reports/GPU_INITIAL_NO_PPO_ADMISSION_ACTUAL.json').read_bytes());assert admission['passed'] and admission['source_sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 else:assert mode=='fullrestore' and '--probe-controls' in sys.argv and int(sys.argv[sys.argv.index('--probe-controls')+1])==120
 folder.mkdir(parents=True)
 (folder/'RESOURCE_PRELAUNCH_ACTUAL.json').write_text(json.dumps(guard,indent=2),encoding='utf-8')
 lock=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock').open('a+b');lock.seek(0)
 if not lock.read(1):lock.write(b'1');lock.flush()
 lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 mode=sys.argv[sys.argv.index('--mode')+1] if '--mode' in sys.argv else 'probe'
 sources=list(D.glob('*.py'))+list((D/'immutable_repair_operator').glob('*.py'))+list((D/'runtime').rglob('*.py'))
 index=[]
 for p in sources:
  if '__pycache__' in p.parts:continue
  q=folder/'source_snapshot'/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  index.append(dict(path=str(p),snapshot=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
 (folder/'SOURCE_SNAPSHOT.json').write_text(json.dumps(dict(epoch=time.time(),files=index),indent=2),encoding='utf8')
 li=sys.argv.index('--lease');child_args=sys.argv[2:li]+sys.argv[li+2:]
 argv=[sys.executable,str(D/'local_scope_worker.py'),'--headless','--device','cuda:0','--num_envs','128','--output',str(folder/'output'),*child_args]
 start=time.time()
 with (folder/'worker.log').open('xb') as log:
  child_env=os.environ.copy();child_env['MOD4_LOCAL_PARENT_START_EPOCH']=str(start);child_env['MOD4_LOCAL_PARENT_PID']=str(os.getpid())
  p=subprocess.Popen(argv,cwd=D,env=child_env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  import psutil
  receipt=dict(epoch=start,child_pid=p.pid,child_create_time=psutil.Process(p.pid).create_time(),argv=argv,cwd=str(D),original_source_preserved=True)
  (folder/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8');print(json.dumps(receipt),flush=True)
  while p.poll() is None:
   if mode=='train':
    latest=folder/'output/LOCAL_LATEST_COMPLETE.json';health=folder/'output/CLOCK_TRAINING_HEALTH.json'
    row=dict(epoch=time.time(),parent_pid=os.getpid(),child_pid=p.pid,mode=mode,actual_child_create_time=receipt['child_create_time'],child_running=True,latest=json.loads(latest.read_bytes()) if latest.exists() else None,health=json.loads(health.read_bytes()) if health.exists() else None,own_bounded_save_exit_not_forced_kill=True)
    (folder/'GUARDIAN_CURRENT.json').write_text(json.dumps(row,indent=2),encoding='utf8')
   time.sleep(15)
  rc=p.returncode
 (folder/'EXIT_RECEIPT.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,wall_seconds=time.time()-start,child_pid=p.pid,actual_mode=mode,source_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',PPO_cost_pending_actual_mode=mode=='train',canonical_reconciliation_pending=mode=='train',no_canonical_copy_or_write=True),indent=2),encoding='utf8')
 lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
 print(json.dumps(dict(exit_code=rc,folder=str(folder))),flush=True)
 sys.exit(rc)
if __name__=='__main__':main()
