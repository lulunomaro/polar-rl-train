from direction_io import *
def main():
 root=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root'];n,w=io.connect_both()
 try:
  v=io.linux_json(n,'''from pathlib import Path
import json,time,hashlib
D=Path(ROOT);rows=[]
paths=list((D/'reports').rglob('*'))+[D/'controller.log',D/'guardian.log']
for p in D.glob('*'):
 if p.is_file() and p.suffix in ('.json','.log','.error'):paths.append(p)
for p in D.glob('*_trace/*'):paths.append(p)
for p in D.glob('fresh_same_scope/*'):paths.append(p)
for base in ('discard_logs','learning_logs'):
 for p in (D/base).glob('*/*'):
  if p.is_file():paths.append(p)
for p in sorted(set(paths)):
 if not p.is_file():continue
 raw=p.read_bytes();rows.append(dict(path=str(p),relative_path=p.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),large_index_only=p.suffix in ('.pt','.npz','.npy','.usd','.zip') or len(raw)>8000000))
print(json.dumps(dict(epoch=time.time(),root=str(D),files=rows,no_GPU_or_budget_write=True)))
'''.replace('ROOT',repr(root)))
  dest=D/'saved_actual'/str(time.time_ns());dest.mkdir(parents=True)
  with n.open_sftp() as f:
   for row in v['files']:
    if row['large_index_only']:continue
    with f.open(row['path'],'rb') as q:raw=q.read()
    if H(raw)!=row['sha256']:
     # Activity may legitimately advance a mutable latest_complete/health/state file.
     row['changed_during_read']=True;row['snapshot_original_index_retained']=True;continue
    p=dest/row['relative_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_exact_copy']=str(p)
  save('DIRECTION_SAVED_EVIDENCE_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(saved_reports=sum('local_exact_copy' in r for r in v['files']),large_indices=sum(r['large_index_only'] for r in v['files']),mutable_advances=sum(r.get('changed_during_read',False) for r in v['files']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
