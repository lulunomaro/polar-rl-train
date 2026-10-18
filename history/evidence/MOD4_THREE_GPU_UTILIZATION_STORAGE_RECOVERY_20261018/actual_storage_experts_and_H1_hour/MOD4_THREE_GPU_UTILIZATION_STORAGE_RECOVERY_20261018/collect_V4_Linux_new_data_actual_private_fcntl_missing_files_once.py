"""Bounded collection of only the two newly dispatched cases; no task replay or H1 audit."""
from inventory_current_owned210_storage_readonly_once import *
from collect_two_expert_first_linux_current_actual_once import CODE as META
import getpass,hashlib
_MARK='print(json.dumps(dict(epoch=time.time(),root=str(B)'
_EXTRA="import fcntl\nlock_cfg=json.loads((B/'LINUX_EXPERT_OBSERVATION_CONFIG.json').read_bytes());private_free=False\nwith Path(lock_cfg['actual_existing_private_lock']).open('rb+') as probe:\n try:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB);private_free=True;fcntl.flock(probe,fcntl.LOCK_UN)\n except BlockingIOError:pass\n"
assert _MARK in META
META=META.replace(_MARK,_EXTRA+'print(json.dumps(dict(private_fcntl_current_free=private_free,epoch=time.time(),root=str(B)')
FILES=r'''
from pathlib import Path
import sys,json,hashlib,time
B=Path(sys.argv[1]);rows=[];partial=[]
for base in (B/'native120_observation',):
 if not base.is_dir():continue
 for p in base.rglob('*'):
  if not p.is_file():continue
  if p.suffix=='.partial':partial.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained not complete'));continue
  if p.suffix.lower() not in ('.json','.npz','.log','.txt'):continue
  before=p.stat();h=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns;rows.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=after.st_size,SHA=h))
for n in ('OBSERVATION_PARENT_CHILD_ACTUAL.json','OBSERVATION_PARENT_EXIT_ACTUAL.json','observation_parent.log','observation_worker.log'):
 p=B/n
 if p.is_file():rows.append(dict(path=str(p),relative=n,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(dict(epoch=time.time(),files=rows,partial=partial)))
'''
def main():
 save('V4_TWO_LINUX_ONLY_MISSING_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True,same_connection_metadata_wait_max180_each=True,no_H1_checkpoint_or_behavior_audit=True));pw=getpass.getpass('72 GPU1 new Linux diagnostic missing evidence (hidden): ');results=[]
 try:
  for kind,host,remote in [('E2','210','/mnt/mod4_linux_durable_20261013/E2rf_1810d4'),('E3','72','/home/lc01/Zonglin Li/zonglin2/tasks/E3rf_1810d4')]:
   c=None
   try:
    c=a.t.connect() if host=='210' else a.connect72(pw);py=a.t.PY if host=='210' else a.PY;start=time.monotonic()
    while True:
     meta=a.code(c,py,META,remote,timeout=60);terminal='OBSERVATION_PARENT_EXIT_ACTUAL.json' in meta['rows']
     if terminal or time.monotonic()-start>=180:break
     time.sleep(5)
    files=[];partial=[]
    if terminal:
     listing=a.code(c,py,FILES,remote,timeout=90);partial=listing['partial'];dest=B/('actual_'+kind+'_Linux_d4_native120');dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
     try:
      for row in listing['files']:
       p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();tmp=p.with_suffix(p.suffix+'.partial');sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and hashlib.sha256(tmp.read_bytes()).hexdigest()==row['SHA'];tmp.replace(p);files.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
     finally:sf.close()
    value=dict(epoch=time.time(),expert=kind,host=host,remote_root=remote,metadata=meta,files=files,partial=partial,terminal_at_snapshot=terminal,no_PPO_or_budget_or_H1_mutation=True);save(kind+'_LINUX_V4_NEW_NATIVE120_COMPLETE_OR_PENDING_COLLECTION_ACTUAL.json',value);results.append(value)
   finally:
    if c:c.close()
 finally:pw=None
 save('V4_TWO_LINUX_NEW_EVIDENCE_COLLECTION_HANDBACK_ACTUAL.json',dict(epoch=time.time(),experts=[r['expert'] for r in results],actual_transport_returned=True,no_H1_or_budget_mutation=True));print(json.dumps([dict(expert=r['expert'],terminal=r['terminal_at_snapshot'],files=len(r['files']),complete=r['metadata']['rows'].get('native120_observation/COMPLETE_ACTUAL.json'),error=r['metadata']['rows'].get('native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'),own_processes=r['metadata']['own_processes'],compute=r['metadata']['compute']) for r in results]),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('V4_TWO_LINUX_ONLY_MISSING_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),only_missing_files_no_GPU_replay=True));raise
