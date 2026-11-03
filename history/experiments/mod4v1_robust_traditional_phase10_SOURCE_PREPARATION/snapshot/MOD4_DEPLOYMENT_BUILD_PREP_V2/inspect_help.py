"""Read command-line help only from the same exact three trusted ARMCC tools."""
from pathlib import Path
import subprocess,json,hashlib
O=Path(__file__).resolve().parent
rows=[]
for name in ('armar','fromelf','armcc'):
 a=['C:/Keil_v5/ARM/ARMCC/bin/'+name+'.exe','--help']
 c=subprocess.run(a,cwd=O,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=15)
 r=dict(argv=a,exit=c.returncode)
 for k,b in [('stdout',c.stdout),('stderr',c.stderr)]:
  p=O/(name+'_help_'+k+'.log');p.write_bytes(b);r[k]=dict(path=p.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
 rows.append(r)
with(O/'TOOL_HELP.json').open('x',encoding='utf-8')as f:json.dump(rows,f,indent=2);f.write('\n')
print(json.dumps(rows,indent=2))
