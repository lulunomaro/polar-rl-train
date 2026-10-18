"""Collect only new frozen210 native evidence and one compact hour2 metadata capture."""
import dispatch_new_fe778_frozen210_native120_after_E2_full_out_once as d
from inventory_current_owned210_storage_readonly_once import *
import getpass,hashlib
sp=d.importlib.util.spec_from_file_location('old_native_collection_pure_CODE_only',d.oldpath.parent/'collect_8a7c_GPU1_native120_existing_finite_once.py');old=d.importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
CASE=old.CASE.replace('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')
def main():
 save('FE778_210_NATIVE_HOUR2_CURRENT_FINITE_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True,max_single_connection_metadata_wait180=True));pw=getpass.getpass('72 H1 hour2 compact metadata (hidden): ');c=None
 try:
  c=a.t.connect();begin=time.monotonic()
  while True:
   meta=a.code(c,a.t.PY,"from pathlib import Path;import sys,json,time;B=Path(sys.argv[1]);p=B/'native120/PARENT_EXIT_RECEIPT.json';print(json.dumps(dict(epoch=time.time(),parent_exit=json.loads(p.read_bytes()) if p.is_file() else None)))",d.TARGET,timeout=60)
   if meta['parent_exit'] or time.monotonic()-begin>=180:break
   time.sleep(5)
  frozen=a.code(c,a.t.PY,CASE,d.TARGET,timeout=120);dest=B/'actual_H1_fe778_Linux210_native120';assert not dest.exists();dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(180)
  try:
   for row in frozen['files']:
    p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.partial');sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==row['SHA'];q.replace(p);row.update(local_path=str(p),twohost_complete_SHA=True)
  finally:sf.close()
  save('H1_FE778_LINUX210_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json',frozen)
  owner=a.code(c,a.t.PY,"from pathlib import Path;import json,time;B=Path('/mnt/mod4_linux_durable_20261013/H1h2_1810p5/owner');rows={p.name:json.loads(p.read_bytes()) for p in B.glob('*.json') if p.name in ('OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_IDENTITY.json')};print(json.dumps(dict(epoch=time.time(),rows=rows,readonly=True)))",timeout=60);save('H1_HOUR2_ACTUAL_OWNER_CURRENT_READONLY_SNAPSHOT.json',owner);c.close();c=a.connect72(pw);pw=None
  current=a.code(c,a.PY,"from pathlib import Path;import json,time,subprocess;B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1h2_1810p5');rows={p.name:json.loads(p.read_bytes()) for p in B.glob('*.json') if p.name in ('NODE_CURRENT.json','GO_PRODUCTION.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','NODE_IDENTITY.json')};print(json.dumps(dict(epoch=time.time(),rows=rows,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),readonly=True,no_mid_hour_model_audit=True)))",timeout=60);save('H1_HOUR2_FE778_CURRENT_ACTUAL_AFTER_NATIVE_COLLECTION.json',current)
  print(json.dumps(dict(frozen_parent_out=frozen['parent_child_launcher_actual_absent'],frozen_errors=frozen['original_error'],frozen_files=len(frozen['files']),H1_current=current['rows'].get('NODE_CURRENT.json'),H1_error=current['rows'].get('NODE_ORIGINAL_ERROR.json'),compute=current['compute'])),flush=True)
 finally:
  pw=None
  if c:c.close()
 save('FE778_210_NATIVE_HOUR2_CURRENT_COLLECTION_ACTUAL_HANDBACK.json',dict(epoch=time.time(),actual_returned=True,no_new_GPU_task_or_model_account_mutation=True))
if __name__=='__main__':
 try:main()
 except BaseException:save('FE778_210_NATIVE_HOUR2_CURRENT_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
