from pathlib import Path
import os,json,time,hashlib,traceback
import stage_lifetime_target_CPU_once as io
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
def main():
 stamp=str(time.time_ns());dest=io.D/'actual_remote_snapshots'/stamp;dest.mkdir(parents=True);n,w=io.connect_linux_only()
 try:
  indices=io.run(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT_TOKEN);paths=sorted([p for p in (D/'reports').iterdir() if p.is_file()]+[p for p in D.iterdir() if p.is_file() and (p.suffix in ('.json','.log','.error') or '.error' in p.name)])
out=[]
for p in paths:
 if p.stat().st_size>8000000:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1048576),b''):h.update(block)
  out.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),large_index_only=True,original_retained=True))
 else:out.append(dict(path=str(p),bytes=p.stat().st_size,mutable_snapshot_required=True))
print(json.dumps(dict(epoch=time.time(),indices=out)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  with n.open_sftp() as f:
   for row in indices['indices']:
    if row.get('large_index_only'):continue
    b=f.open(row['path'],'rb').read();p=dest/Path(row['path']).relative_to(ROOT);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);row.update(snapshot_path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),snapshot_read_epoch=time.time())
  p=io.save('LIFETIME_CURRENT_REPORT_COLLECTION_'+stamp+'.json',dict(passed=True,epoch=time.time(),indices=indices['indices'],mutable_current_packets_captured_as_actual_snapshots=True,all_large_originals_retained_index_only=True,no_GPU_or_training_replay=True));print(json.dumps(dict(passed=True,report=str(p),files=len(indices['indices']))))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('LIFETIME_REPORT_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
