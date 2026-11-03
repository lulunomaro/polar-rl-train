"""Only four exact ARMCC-path version commands; no compile/link or project load."""
from pathlib import Path
import json,subprocess,hashlib
O=Path(__file__).resolve().parent
out=[]
for name in ('armcc','armar','armlink','fromelf'):
 p=Path('C:/Keil_v5/ARM/ARMCC/bin')/(name+'.exe');r=dict(tool=name,path=str(p),exists=p.is_file(),argv=[str(p),'--vsn'])
 if r['exists']:
  st=p.stat();r.update(bytes=st.st_size,mtime_ns=st.st_mtime_ns)
  try:
   c=subprocess.run(r['argv'],cwd=O,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,check=False)
   r.update(exit=c.returncode,stdout=c.stdout.decode('utf-8',errors='replace'),stderr=c.stderr.decode('utf-8',errors='replace'))
   for stream,b in [('stdout',c.stdout),('stderr',c.stderr)]:
    f=O/(name+'_vsn_'+stream+'.log');f.write_bytes(b);r[stream+'_file']=dict(path=f.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
  except subprocess.TimeoutExpired as e:
   r.update(exit=None,error='VERSION_COMMAND_TIMEOUT_15S',stdout=(e.stdout or b'').decode('utf-8',errors='replace'),stderr=(e.stderr or b'').decode('utf-8',errors='replace'))
 out.append(r)
v=dict(scope='EXACT_4_ARMCC_PATH_VERSIONS_ONLY',project_declared='ARMCC 5.06 update 4 build 422',tools=out,compiler_or_link_actions=0,UV_hook_flash=0,archive_library_code_executed=False)
with(O/'TOOL_VERSIONS.json').open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(v,ensure_ascii=False,indent=2))
