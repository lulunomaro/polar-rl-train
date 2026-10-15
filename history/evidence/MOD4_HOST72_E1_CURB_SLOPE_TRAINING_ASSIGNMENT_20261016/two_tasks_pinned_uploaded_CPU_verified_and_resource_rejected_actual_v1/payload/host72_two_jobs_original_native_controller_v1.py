from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,os,subprocess,tarfile,time,traceback
ROOT=Path('/home/lc01/Zonglin Li/zonglin2');BASE=ROOT/'tasks/MOD4_HOST72_E1_CURB_SLOPE_TRAINING_ASSIGNMENT_20261016'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2)
def main():
 assert ROOT.resolve()==ROOT and BASE.resolve().is_relative_to(ROOT)
 archive=ROOT/'downloads/two_E1_assigned_jobs_original_native_v1.tar.gz';spec=json.loads((ROOT/'audit/two_E1_assigned_jobs_original_native_v1_manifest.json').read_bytes())
 assert sha(archive)==spec['sha256'] and archive.stat().st_size==spec['bytes'];BASE.mkdir(parents=True)
 with tarfile.open(archive,'r:gz') as t:
  for m in t:
   q=PurePosixPath(m.name);assert m.isfile() and not q.is_absolute() and '..' not in q.parts
   p=BASE.joinpath(*q.parts);assert p.resolve().is_relative_to(BASE);p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('xb') as f:f.write(t.extractfile(m).read())
 put(BASE/'TARGET_PAYLOAD_SHA_ACTUAL.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in BASE.rglob('*') if p.is_file()],no_PPO=True))
 compute=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True)
 assert not compute.stdout.strip(),compute.stdout
 rows=[]
 for i in (0,1):
  j=BASE/('job'+str(i));lock=j/'own_original_backend_native.lock'
  with lock.open('xb+') as f:
   fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   log=j/'ORIGINAL_BACKEND_NATIVE_STDOUT_STDERR.log'
   with log.open('xb') as s:
    p=subprocess.Popen([str(ROOT/'run-python.sh'),'-B',str(BASE/'host72_original_backend_native_worker_v1.py'),'--job',str(i)],cwd=str(j),stdout=s,stderr=subprocess.STDOUT,close_fds=True)
    put(j/'OWN_NATIVE_PARENT_STARTED_ACTUAL.json',dict(epoch=time.time(),parent_pid=os.getpid(),worker_pid=p.pid,argv=[str(ROOT/'run-python.sh'),str(BASE/'host72_original_backend_native_worker_v1.py'),'--job',str(i)],native_only_0PPO=True))
    code=p.wait(timeout=900)
   fcntl.flock(f,fcntl.LOCK_UN)
  row=dict(job=i,returncode=code,worker_pid=p.pid,actual_proc_absent=not Path('/proc',str(p.pid)).exists(),data_complete=(j/'original_backend_native120_v1/NATIVE120_DATA_COMPLETE_ACTUAL.json').exists(),own_fcntl_released=True)
  put(j/'OWN_NATIVE_PARENT_EXIT_ACTUAL.json',row);rows.append(row)
  put(BASE/('CURRENT_AFTER_JOB'+str(i)+'.json'),dict(epoch=time.time(),rows=rows))
 put(BASE/'TWO_ORIGINAL_BACKEND_NATIVE_FINITE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),rows=rows,all_pass=all(x['returncode']==0 and x['actual_proc_absent'] and x['data_complete'] for x in rows),no_optimizer_step_budget_or_source_host_mutation=True))
 print(json.dumps(rows),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  p=ROOT/'audit'/('TWO_ORIGINAL_NATIVE_CONTROLLER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');put(p,dict(error=traceback.format_exc(),no_signal_delete_retry_or_PPO=True));raise
