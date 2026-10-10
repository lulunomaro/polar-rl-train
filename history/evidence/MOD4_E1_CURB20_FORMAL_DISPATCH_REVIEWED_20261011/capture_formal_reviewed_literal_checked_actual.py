"""Freeze existing text receipts and index actual binary weights; never launch."""
from stage_formal_dispatch_reviewed_once import D,R,E,B,NEW,OLD,connect_both,cleanup,linux_json,save,H
from pathlib import Path
import json,time
def main():
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import json,hashlib,time
out=[]
for root in ROOTS:
 D=Path(root)
 candidates=list((D/'reports').glob('*.json'))+list(D.glob('*.log'))+list(D.glob('*.error.txt'))+list((D/'reports').glob('*.txt'))
 candidates+=list((D/'fresh_process_resume').glob('*.json'))+list((D/'fresh_process_resume').glob('*.pt'))
 for name in ('discard_logs','learning_logs'):
  for run in (D/name).glob('*'):
   if run.is_dir():candidates+=list(run.glob('*.json'))+list(run.glob('*.pt'))+list(run.glob('OWN_SAME_CURB_FULL_RESUME/*.json'))
 for p in sorted(set(candidates)):
  if not p.is_file():continue
  raw=p.read_bytes();out.append(dict(path=str(p),relative=p.relative_to(D).as_posix(),root=root,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),binary=p.suffix=='.pt',large_raw_text=len(raw)>5000000))
print(json.dumps(dict(epoch=time.time(),files=out,read_only_no_signal_no_budget_action=True)))
'''.replace('ROOTS',repr(['/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_REVIEWED_20261011', '/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011', '/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FRESH_PROCESS_REVIEWED_20261011', '/home/egde/rl_candidates/MOD4_S3_E1_CURB20_SPLIT_STATE_ADMITTED_20261011', '/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011']))
  index=linux_json(n,code);folder=D/'captured_remote'/str(time.time_ns());folder.mkdir(parents=True)
  with n.open_sftp() as f:
   for row in index['files']:
    if row['binary'] or row['large_raw_text']:row['capture']='actual_path_size_SHA_index_only';continue
    raw=f.open(row['path']).read()
    if H(raw)!=row['sha256']:
     row['initial_read_sha256']=row['sha256'];row['sha256']=H(raw);row['bytes']=len(raw);row['dynamic_file_changed_between_reads']=True
    p=folder/Path(row['root']).name/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_exact_file']=str(p);row['capture']='full_text_exact_bytes'
  p=save('REMOTE_FORMAL_REVIEWED_EVIDENCE_'+str(time.time_ns())+'.json',index)
  print(json.dumps(dict(report=str(p),text_files=sum(x['capture']=='full_text_exact_bytes' for x in index['files']),binary_or_large_indices=sum(x['capture']=='actual_path_size_SHA_index_only' for x in index['files']))))
 finally:cleanup(n,w)
if __name__=='__main__':main()
