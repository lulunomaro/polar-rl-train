from pathlib import Path
import sys,json,shlex
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R.parent/'tmp'))
from step7_remote_access import connect
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));REMOTE=P['root']
def execute(c,cmd,timeout=50):
 i,o,e=c.exec_command(cmd,timeout=timeout);out=o.read().decode('utf8',errors='replace');err=e.read().decode('utf8',errors='replace');status=o.channel.recv_exit_status()
 if status:raise RuntimeError('Remote exit '+str(status)+'\n'+out[-4000:]+'\n'+err[-4000:])
 return out
