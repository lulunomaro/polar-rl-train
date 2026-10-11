"""Index only immutable completed saves/NPZ and freeze their small receipts."""
from wave_direction_io import *
def main():
 stamp=str(time.time_ns());n,w=io.connect_both();dest=D/'completed_training_receipts'/stamp;dest.mkdir(parents=True)
 try:
  v=run(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT_TOKEN);out=[];small=[]
def h(p):
 a=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):a.update(b)
 return a.hexdigest()
for receipt in D.joinpath('reports').glob('*_PASSED.json'):
 row=json.loads(receipt.read_bytes())
 if 'checkpoint' not in row or 'run' not in row:continue
 root=Path(row['run']);checkpoint=Path(row['checkpoint']['path']);assert checkpoint.is_relative_to(root) and h(checkpoint)==row['checkpoint']['sha256']
 for p in sorted(root.rglob('*')):
  if not p.is_file():continue
  if p.suffix.lower() in ('.pt','.npz','.npy'):out.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),completed_own_run_receipt=str(receipt),discarded_preflight=bool(row['discarded_preflight']),original_retained=True,large_index_only=True))
  elif p.parent==root and p.suffix in ('.json','.txt'):small.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
print(json.dumps(dict(epoch=time.time(),files=out,small_complete_receipts=small,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  with n.open_sftp() as f:
   for i,row in enumerate(v['small_complete_receipts']):
    raw=f.open(row['path'],'rb').read();assert H(raw)==row['sha256'] and len(raw)==row['bytes'];p=dest/(str(i)+'_'+Path(row['path']).name);p.write_bytes(raw);row['local_actual_saved_receipt']=str(p.resolve())
  report=save('DIRECTION_COMPLETE_TRAINING_ARTIFACTS_'+stamp+'.json',v);print(json.dumps(dict(report=str(report),completed_own_large_artifacts=len(v['files']),small_saved_receipts=len(v['small_complete_receipts']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE_ARTIFACT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_replay=True));raise
