from pathlib import Path
import json,sys,time
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=Path(__file__).resolve().parent;P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'))
f=P['support'].rsplit('/support',1)[0]+'/'+P['training_round']['job']+'.log'
c=connect();s=c.open_sftp()
with s.open(f,'rb') as stream:lines=stream.read().decode('utf-8',errors='replace').splitlines()
s.close();c.close()
patterns=('foundLostAggregatePairsCapacity','buffer overflow','missed interactions','dropped contacts','Traceback')
r=dict(epoch=time.time(),log_lines=len(lines),capacity_or_traceback_matches=[x for x in lines if any(k in x for k in patterns)])
(T/'evidence'/('LOG_CHECK_'+str(int(r['epoch']))+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False))
