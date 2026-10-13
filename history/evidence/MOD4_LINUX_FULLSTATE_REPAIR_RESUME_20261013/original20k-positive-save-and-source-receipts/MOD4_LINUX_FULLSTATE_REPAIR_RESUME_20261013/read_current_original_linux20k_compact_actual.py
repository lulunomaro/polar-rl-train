"""Compact observer. Keep large per-environment proof arrays in original files."""
import json
from remote_session import execute
from deploy_original_linux20k_formal_once import S as BASE
S=BASE.replace('_v1','_runtime_assets_complete_v3')
src=r'''
from pathlib import Path
import json,subprocess,hashlib,time
R=Path(S);out=dict(epoch=time.time(),scope=S)
for n in ('PARENT_IDENTITY.json','formal/DISPATCH_RECEIPT.json','formal/GUARDIAN_CURRENT.json','formal/EXIT_RECEIPT.json','ORIGINAL_PARENT_ERROR.json','ORIGINAL_LINUX_SAVED_REVIEW_READY.json'):
 p=R/n;v=json.loads(p.read_bytes()) if p.exists() else None
 if n=='ORIGINAL_LINUX_SAVED_REVIEW_READY.json' and v:v=dict(exists=True,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 out[n]=v
out['own_logs']=[]
for p in (R/'formal/learning_logs').glob('*'):
 if not p.is_dir():continue
 markers=[]
 for q in p.glob('*STARTUP*VERIFIED.json'):
  raw=q.read_bytes();v=json.loads(raw);markers.append(dict(name=q.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),proof={k:x for k,x in v.items() if isinstance(x,(bool,int,float,str))}))
 q=p/'latest_complete.json';out['own_logs'].append(dict(path=str(p),markers=markers,latest=json.loads(q.read_bytes()) if q.exists() else None))
log=R/'formal/worker_stdout.log'
with log.open('rb') as f:f.seek(max(0,log.stat().st_size-16000));tail=f.read().decode(errors='replace')
out['stdout_tail']=tail
out['compute']=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader'],capture_output=True,text=True).stdout
print(json.dumps(out))
'''
if __name__=='__main__':
    row,p=execute('S='+repr(S)+'\n'+src,'ORIGINAL_LINUX20K_COMPACT_CURRENT_ACTUAL',40)
    print(json.dumps(dict(receipt=str(p),current=row['formal/GUARDIAN_CURRENT.json'],own=[dict(path=x['path'],marker_count=len(x['markers']),latest=x['latest']) for x in row['own_logs']],error=row['ORIGINAL_PARENT_ERROR.json'],tail=row['stdout_tail'][-1500:]),indent=2))
