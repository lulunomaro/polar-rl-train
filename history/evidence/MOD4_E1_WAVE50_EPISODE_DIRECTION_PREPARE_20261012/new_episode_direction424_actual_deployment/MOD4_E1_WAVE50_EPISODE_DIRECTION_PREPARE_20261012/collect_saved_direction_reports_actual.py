"""Freeze saved own receipts; large completed originals stay at actual paths."""
from wave_direction_io import *
def main():
 n,w=io.connect_both();stamp=str(time.time_ns());dest=D/'saved_actual'/stamp;dest.mkdir(parents=True);indices=[]
 try:
  with n.open_sftp() as f:
   for name in sorted(f.listdir(ROOT+'/reports')):
    path=ROOT+'/reports/'+name
    if not name.endswith(('.json','.txt','.md')):continue
    raw=f.open(path,'rb').read();local=dest/'reports'/name;local.parent.mkdir(exist_ok=True);local.write_bytes(raw)
    indices.append(dict(path=path,bytes=len(raw),sha256=H(raw),actual_saved_source_local=str(local.resolve()),capture_epoch=time.time()))
   for name in ('controller.log','guardian.log'):
    try:raw=f.open(ROOT+'/'+name,'rb').read()
    except FileNotFoundError:continue
    local=dest/name;local.write_bytes(raw);indices.append(dict(path=ROOT+'/'+name,bytes=len(raw),sha256=H(raw),actual_saved_source_local=str(local.resolve()),capture_epoch=time.time(),active_log_snapshot_not_final=True))
  large=run(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT_TOKEN);out=[]
def h(p):
 q=hashlib.sha256()
 with p.open('rb') as f:
  for a in iter(lambda:f.read(1048576),b''):q.update(a)
 return q.hexdigest()
for label in ('WAVE50_SDK10','WAVE50_NATIVE20K'):
 receipt=D/'reports'/(label+'_PASSED.json')
 if not receipt.exists():continue
 row=json.loads(receipt.read_bytes());p=Path(row['path']);assert h(p)==row['sha256'];paths=[p]+list(D.glob(label+'_trace/*.npz'))
 for p in paths:out.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),actual_completed_original=True,original_retained=True,large_index_only=True))
print(json.dumps(dict(epoch=time.time(),files=out,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  report=save('DIRECTION_SAVED_COLLECTION_'+stamp+'.json',dict(epoch=time.time(),saved_text_report_indices=indices,large_completed_originals=large['files'],no_GPU_or_budget_write=True));print(json.dumps(dict(report=str(report),saved_reports=len(indices),completed_large_originals=len(large['files']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SAVED_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_replay=True));raise
