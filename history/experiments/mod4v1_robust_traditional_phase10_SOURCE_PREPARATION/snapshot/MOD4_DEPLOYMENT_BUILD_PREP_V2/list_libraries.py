"""Read-only armar -t for exactly the two authorized libraries. No symbol/code dump."""
from pathlib import Path
import json,subprocess,hashlib
O=Path(__file__).resolve().parent
P=json.loads((O/'PATHS_AND_PROJECT.json').read_bytes());rows=[]
for i,r in enumerate(P['libraries'],1):
 p=Path(r['path']);st=p.stat();assert (st.st_size,st.st_mtime_ns)==(r['bytes'],r['mtime_ns'])
 argv=['C:/Keil_v5/ARM/ARMCC/bin/armar.exe','-t',str(p)]
 c=subprocess.run(argv,cwd=O,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20,check=False)
 rr=dict(library=r,argv=argv,exit=c.returncode)
 for k,b in [('stdout',c.stdout),('stderr',c.stderr)]:
  f=O/('library_'+str(i)+'_list_'+k+'.log');f.write_bytes(b);rr[k]=dict(path=f.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
 assert len(c.stdout)<=1048576,'LISTING_CAP_NOT_EXPANDED'
 rr['members']=c.stdout.decode('utf-8',errors='strict').splitlines()if c.returncode==0 else None
 assert (p.stat().st_size,p.stat().st_mtime_ns)==(st.st_size,st.st_mtime_ns)
 rows.append(rr)
with(O/'LIBRARY_MEMBERS.json').open('x',encoding='utf-8')as f:json.dump(rows,f,indent=2);f.write('\n')
print(json.dumps([dict(library=r['library']['name'],exit=r['exit'],members=len(r['members'] or []),first=(r['members']or[])[:8],last=(r['members']or[])[-3:],stdout=r['stdout'])for r in rows],indent=2))
