from second_io import *
def main():
 n,w=io.connect_both();dest=D/('own_saved_actual_'+str(time.time_ns()));dest.mkdir();rows=[]
 try:
  with n.open_sftp() as f:
   paths=[ROOT+'/controller.log',ROOT+'/guardian.log']
   paths.extend(ROOT+'/reports/'+x for x in f.listdir(ROOT+'/reports') if x.endswith(('.json','.md')))
   runs=f.listdir(ROOT+'/learning_logs') if f.listdir(ROOT+'/learning_logs') else []
   for name in runs:
    paths.extend(ROOT+'/learning_logs/'+name+'/'+x for x in f.listdir(ROOT+'/learning_logs/'+name) if x.endswith('.json'))
   for remote in paths:
    raw=f.open(remote,'rb').read();rel=Path(remote[len(ROOT)+1:]);p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    rows.append(dict(remote_path=remote,local_snapshot_path=str(p),bytes=len(raw),sha256=H(raw),actual_snapshot_bytes=True))
  artifacts=run(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT_TOKEN);rows=[]
for p in (D/'learning_logs').rglob('*'):
 if not p.is_file() or p.suffix.lower() not in ('.pt','.npz'):continue
 before=p.stat();h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 after=p.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
 rows.append(dict(path=str(p),bytes=after.st_size,sha256=h.hexdigest(),large_original_index_only=True,original_retained=True))
print(json.dumps(dict(epoch=time.time(),artifacts=rows,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('SECOND_OWN_SAVED_SOURCE_COLLECTION_'+str(time.time_ns())+'.json',dict(epoch=time.time(),rows=rows,artifact_indices=artifacts,actual_sources_and_reports_captured=True,no_old_GPU_or_once_replay=True));print(json.dumps(dict(report=str(p),saved_reports=len(rows),large_indices=len(artifacts['artifacts']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_SOURCE_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
