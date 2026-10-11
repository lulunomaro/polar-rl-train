from wave50_io import *
def main():
 n,w=io.connect_both()
 try:
  rows=run(n,r'''from pathlib import Path
import hashlib,json,time
D=Path(ROOT_TOKEN);roots=[D/'reports',D/'discard_logs',D/'learning_logs',D/'fresh_process_resume'];files=[]
for root in roots:
 if root.exists():files.extend(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(p for p in D.glob('WAVE50_*') if p.is_file());files.extend(D.glob('*.log'));rows=[]
for p in files:
 try:raw=p.read_bytes()
 except FileNotFoundError:continue
 rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),capture_saved_report=p.suffix.lower() in ('.json','.txt','.log','.error') and len(raw)<=8000000,large_original_index_only=p.suffix.lower() in ('.pt','.npz','.npy','.zip','.usd') or len(raw)>8000000,source_snapshot_index=p.suffix.lower()=='.py'))
print(json.dumps(dict(epoch=time.time(),actual_saved_file_indices=rows,source_freeze_and_snapshot_SHA_indices_original_bytes_retained=True,no_GPU_PPO_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  out=D/('preflight_actual_'+str(time.time_ns()));out.mkdir()
  with n.open_sftp() as f:
   for row in rows['actual_saved_file_indices']:
    if not row['capture_saved_report']:continue
    raw=f.open(row['path'],'rb').read()
    if H(raw)!=row['sha256']:row.update(snapshot_changed_during_read=True,bytes=len(raw),sha256=H(raw))
    p=out/Path(row['path']).relative_to(Path(ROOT));p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_actual_snapshot']=str(p)
  p=save('PREFLIGHT_ACTUAL_SAVED_COLLECTION_'+str(time.time_ns())+'.json',rows);print(json.dumps(dict(report=str(p),actual_saved_files=len(rows['actual_saved_file_indices']),copied_reports=sum(x['capture_saved_report'] for x in rows['actual_saved_file_indices']))))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
