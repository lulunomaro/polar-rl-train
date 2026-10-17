"""A new bounded read of the existing run; prior empty collection is kept, no GPU replay."""
from pathlib import Path
import sys,os,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sys.path.insert(0,str(M))
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import SNAP
from deploy_human_requested_H1_new_finite_strict_native_reuse_once import a,SOURCE,TARGET
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
PROGRESS=SNAP[:SNAP.rfind('print(json.dumps(')]+r'''
import subprocess
log=B/'job0/production_WORKER.log'
tail=''
if log.is_file():
 with log.open('rb') as f:f.seek(max(0,log.stat().st_size-131072));tail=f.read().decode('utf8',errors='backslashreplace')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.used,memory.free','--format=csv,noheader,nounits']).decode()
print(json.dumps(dict(epoch=time.time(),root=str(B),files=files,errors=errors,actual_own_processes=procs,first_complete_file_present=(B/'job0/production/model_update1.pt').is_file(),production_log_bytes=log.stat().st_size if log.exists() else None,production_log_tail=tail[-20000:],actual_GPU_snapshot=gpu,only_existing_own_scope_read=True)))
'''
def main():
 old=json.loads((R/'HUMAN_REQUESTED_H1_IMMUTABLE_FIRST_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert old['downloaded_models']==[] and old['actual_return_hands_all_transport_back']
 save('H1_MISSING_FIRST_PROGRESS_V2_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_hosts=True,single_target_connection_max600s_then_one_source=True,no_Task_native_or_worker_replay=True))
 pw=getpass.getpass('Host72 existing H1 progress and missing first only (hidden): ');c=None;v={};models=[]
 try:
  c=a.connect72(pw);pw=None;start=time.monotonic()
  while True:
   row=a.code(c,a.PY,PROGRESS,TARGET,'metadata',timeout=90);v['h1_progress']=row
   p=R/'H1_EXISTING_WORKER_FIRST_PROGRESS_V2_CURRENT_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(dict(epoch=time.time(),target=row),indent=2));tmp.replace(p)
   if row['first_complete_file_present'] or row['errors'] or any(r['path'].endswith('/NODE_EXIT_ACTUAL.json') for r in row['files']) or time.monotonic()-start>=600:break
   time.sleep(min(15,max(0,600-(time.monotonic()-start))))
  v['h1']=a.code(c,a.PY,SNAP,TARGET,'collect',timeout=90);sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['h1']['models']:
    assert row['kind'] in ('immutable_first','immutable_startup0');p=B/'actual_new_native_first_models'/Path(row['path']).name;p.parent.mkdir(exist_ok=True);assert not p.exists();part=p.with_suffix('.pt.partial');assert not part.exists();sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();v['owner']=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=60)
 finally:a.t.close(c)
 v.update(epoch=time.time(),downloaded_models=models,actual_return_hands_all_transport_back=True,old_empty_collection_preserved=True,no_old_complete_PT_raw_or_native_replay=True)
 save('HUMAN_REQUESTED_H1_MISSING_FIRST_PROGRESS_V2_BOUND_COLLECTION_ACTUAL.json',v)
 print(json.dumps(dict(models=[dict(kind=r['kind'],SHA=r['SHA']) for r in models],errors=v['h1']['errors'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('H1_MISSING_FIRST_PROGRESS_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_no_replay=True));raise
