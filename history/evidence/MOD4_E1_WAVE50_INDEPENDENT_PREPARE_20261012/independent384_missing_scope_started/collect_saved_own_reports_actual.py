"""Capture saved report bytes and actual large-original indices without GPU replay."""
from wave50_io import *
def main():
 n,w=io.connect_both()
 try:
  rows=run(n,r'''from pathlib import Path
import hashlib,json,time
D=Path(ROOT_TOKEN);files=list((D/'reports').rglob('*'))+list(D.glob('*.log'))+list(D.glob('WAVE50_*.json'))+list(D.glob('WAVE50_*.json.assignment.json'))+list(D.glob('WAVE50_*_trace/*'))
unique={str(p):p for p in files if p.is_file()};rows=[]
for p in unique.values():
 raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),large_original_index_only=p.suffix.lower() in ('.pt','.npz','.npy','.zip','.usd') or len(raw)>8000000))
print(json.dumps(dict(epoch=time.time(),root=str(D),actual_saved_files=rows,no_GPU_PPO_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  out=D/('own_saved_actual_'+str(time.time_ns()));out.mkdir()
  with n.open_sftp() as f:
   for row in rows['actual_saved_files']:
    if row['large_original_index_only']:continue
    raw=f.open(row['path'],'rb').read()
    if H(raw)!=row['sha256']:
     row['snapshot_changed_during_read']=True;row['bytes']=len(raw);row['sha256']=H(raw)
    dest=out/Path(row['path']).relative_to(Path(ROOT));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['local_actual_snapshot']=str(dest)
  p=save('OWN_SAVED_ACTUAL_COLLECTION_'+str(time.time_ns())+'.json',rows)
  print(json.dumps(dict(collection=str(p),actual_saved_files=len(rows['actual_saved_files']),large_indices=sum(x['large_original_index_only'] for x in rows['actual_saved_files']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
