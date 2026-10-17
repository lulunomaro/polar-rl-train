"""One bounded transport owner observes both existing GPU scopes; never launches work."""
from pathlib import Path
import sys,os,time,json,getpass,traceback,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;P=W/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sys.path[:0]=[str(P),str(M)]
from deploy_human_requested_H1_new_finite_strict_native_reuse_once import a
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import SNAP
TRAIN='/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1810v4';EVAL='/home/lc01/Zonglin Li/zonglin2/tasks/H1fe_1810ev5';OWNER='/mnt/mod4_linux_durable_20261013/H1r_1810v4/owner'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
META=r'''
from pathlib import Path
import sys,json,time,psutil,subprocess
T=Path(sys.argv[1]);E=Path(sys.argv[2]);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
rows=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=__import__('os').getpid() and any(x.startswith(str(T)+'/') or x.startswith(str(E)+'/') for x in p.info['cmdline'] or []):rows.append(p.info)
 except psutil.Error:pass
out=E/'native120/output';errors={p.name:read(p) for p in out.glob('*ERROR*.json')}
print(json.dumps(dict(epoch=time.time(),training_current=read(T/'NODE_CURRENT.json'),training_GO=read(T/'GO_PRODUCTION.json'),training_error=read(T/'NODE_ORIGINAL_ERROR.json'),training_first_exists=(T/'job0/production/model_update1.pt').is_file(),eval_dispatch=read(E/'native120/DISPATCH_RECEIPT.json'),eval_parent_exit=read(E/'native120/PARENT_EXIT_RECEIPT.json'),eval_started=read(out/'STARTED.json'),eval_complete=read(out/'COMPLETE_ACTUAL.json'),eval_original_errors=errors,actual_scope_processes=rows,GPU_actual_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.used,memory.free','--format=csv,noheader,nounits']).decode(),compute_actual_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),no_PT_raw_hash=True)))
'''
CASE=r'''
from pathlib import Path
import sys,json,time,psutil,os,hashlib,fcntl
B=Path(sys.argv[1]);A=B/'native120';O=A/'output';read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while x:=f.read(4*1024*1024):h.update(x)
 return h.hexdigest()
exitrow=read(A/'PARENT_EXIT_RECEIPT.json');procs=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
lockpath=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock');free=False
with lockpath.open('rb+') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
 except BlockingIOError:pass
files=[]
if exitrow and not procs:
 for p in sorted([*O.glob('*'),A/'worker.log',A/'LEASE_ACTUAL.json',A/'DISPATCH_RECEIPT.json',A/'PARENT_EXIT_RECEIPT.json']):
  if p.is_file() and not p.name.endswith('.partial'):files.append(dict(relative=p.relative_to(B).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)))
print(json.dumps(dict(epoch=time.time(),files=files,parent_exit=exitrow,parent_child_launcher_actual_absent=bool(exitrow and not procs),actual_selected_private_fcntl_free=free,actual_own_processes=procs,actual_Linux_backend=read(B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json'),actual_natural_exit_marker_present=(O/'EXIT_NATURAL.json').exists(),original_error=any(O.glob('*ERROR*.json')),original_transport_error=False,pending_not_complete=not bool(exitrow and not procs))))
'''
def main():
 put('PARALLEL_V5_H1_TRAIN_GPU1_EVAL_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_created_argv_alive_only_exclusive_all21072_249_transport=True,max_single_target_metadata_wait300s_then_one_source=True,no_new_task_or_GPU_or_watcher=True));pw=getpass.getpass('Host72 existing parallel training/evaluation finite collection (hidden): ');c=None;models=[]
 try:
  c=a.connect72(pw);pw=None;start=time.monotonic()
  while True:
   v=a.code(c,a.PY,META,TRAIN,EVAL,timeout=90);p=R/'PARALLEL_V5_H1_TRAIN_GPU1_EVAL_CURRENT_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
   if (v['training_first_exists'] and v['eval_parent_exit']) or v['training_error'] or time.monotonic()-start>=300:break
   time.sleep(min(15,max(0,300-(time.monotonic()-start))))
  training=a.code(c,a.PY,SNAP,TRAIN,'collect',timeout=120);frozen=a.code(c,a.PY,CASE,EVAL,timeout=180);sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in training['models']:
    p=B/'paid_d723_v4/actual_new_native_first_models'/Path(row['path']).name;p.parent.mkdir(exist_ok=True);assert not p.exists();part=p.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
   for row in frozen['files']:
    p=B/'actual_Linux_GPU1_V5_native120'/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();part=p.with_suffix(p.suffix+'.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);row.update(local_path=str(p),twohost_complete_SHA=True)
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,SNAP,OWNER,'metadata',timeout=90)
 finally:a.t.close(c)
 put('PARALLEL_V5_H1_TRAINING_FIRST_AND_GPU1_NATIVE120_BOUND_COLLECTION_ACTUAL.json',dict(epoch=time.time(),h1=training,owner=owner,downloaded_models=models,frozen=frozen,actual_parallel_snapshot=v,actual_return_hands_all_transport_back=True,no_old_PT_native_raw_replay_or_training_interrupt=True))
 put('LINUX_GPU1_V5_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json',frozen)
 with (B/'paid_d723_v4/reports/PARALLEL_D723_H1_MISSING_FIRST_PROGRESS_V2_BOUND_COLLECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(downloaded_models=models,h1=training,owner=owner),f,indent=2)
 print(json.dumps(dict(training_models=len(models),training_errors=training['errors'],eval_complete_parent=frozen['parent_child_launcher_actual_absent'],eval_errors=frozen['original_error'],eval_files=len(frozen['files']),actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('PARALLEL_FINITE_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
