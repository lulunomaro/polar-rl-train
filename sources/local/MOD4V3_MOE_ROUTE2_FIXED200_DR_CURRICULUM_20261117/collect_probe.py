"""Read-only collection of one native zero-update probe; never starts PPO."""
from pathlib import Path
import sys,json,shlex
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T))
from remote_run import connect,execute,P,REMOTE
job=sys.argv[1];out=T/'evidence'/sys.argv[2];out.mkdir(parents=True,exist_ok=True)
c=connect()
try:
 code="from pathlib import Path;import json;p=Path("+repr(REMOTE)+")/"+repr(job)+";print(json.dumps(dict(files=[f.name for f in p.glob('*.json')],pid_alive=Path('/proc/'+str(json.loads((p.parent/(p.name+'_LAUNCH.json')).read_text())['pid'])).exists())))"
 state=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))
 with c.open_sftp() as sf:
  for name in state['files']:sf.get(REMOTE+'/'+job+'/'+name,str(out/name))
  if 'SAFE_CLOSED.json'in state['files']:sf.get(REMOTE+'/'+job+'.log',str(out/'stdout.log'))
 summary={'pid_alive':state['pid_alive']}
 for name in ['PROBE_PROGRESS.json','STARTUP_DIAGNOSTICS.json','ERROR.json','SAFE_CLOSED.json','OFFSET_COVERAGE.json']:
  if(out/name).exists():
   d=json.loads((out/name).read_text(encoding='utf-8'));summary[name]={k:v for k,v in d.items()if k not in ['rows']}
 print(json.dumps(summary,ensure_ascii=False))
finally:c.close()
