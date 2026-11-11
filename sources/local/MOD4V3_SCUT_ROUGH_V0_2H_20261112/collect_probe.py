from pathlib import Path
import sys,json,hashlib
ROOT=Path(r'D:\claude2\fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112';P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'));B=P['support'].rsplit('/support',1)[0]
c=connect();s=c.open_sftp();files=[]
for job in ('smoke4096_unified_r1','smoke4096_unified_r2'):
 d=T/'evidence'/job;d.mkdir(exist_ok=True)
 for name in s.listdir(B+'/'+job):
  if name.endswith(('.json','.pt')):
   target=d/name;s.get(B+'/'+job+'/'+name,str(target));files.append(dict(path=target.relative_to(T).as_posix(),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
 for name in (job+'.log',job+'_LAUNCH.json'):
  target=d/name;s.get(B+'/'+name,str(target));files.append(dict(path=target.relative_to(T).as_posix(),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
s.close();c.close()
(T/'evidence/PROBE_COLLECTION.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(files),full_probe_PT_files=sum(x['path'].endswith('.pt') for x in files),source='both actual probe jobs, including failed first startup')))
