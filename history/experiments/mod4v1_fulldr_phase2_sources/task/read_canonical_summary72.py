"""Parse the large canonical in place; emit only bounded numeric/identity summaries.
No ledger copy, reservation, charge or remote write.
"""
from pathlib import Path
import datetime,json,shlex
from project_connector import connect72
ROOT=Path(__file__).resolve().parent;BASE='/home/lc01/Zonglin Li/zonglin2'
code=r'''
import json,pathlib,hashlib,time,re
p=pathlib.Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
raw=p.read_bytes();d=json.loads(raw)
sensitive=re.compile(r'password|passwd|secret|token|hmac|signature|credential|private.?key',re.I)
identity=re.compile(r'generation|status|kind|run.?id|account|role|host|phase|mode|authority|path|name|updated|epoch|reason',re.I)
def small(v,depth=0,key=''):
 if sensitive.search(key):return '[REDACTED_FIELD]'
 if v is None or isinstance(v,(bool,int,float)):return v
 if isinstance(v,str):return v if identity.search(key) and len(v)<1000 else {'string_length':len(v)}
 if isinstance(v,list):return {'count':len(v),'last2':[small(x,depth+1,key) for x in v[-2:]]} if len(v)>4 else [small(x,depth+1,key) for x in v]
 if isinstance(v,dict):
  if depth>5:return {'keys':list(v)[:100],'dict_count':len(v)}
  return {k:small(x,depth+1,k) for k,x in list(v.items())[:100]}
 return {'type':type(v).__name__}
print(json.dumps({'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'read_epoch':time.time(),'canonical_keys':list(d),'summary':small(d)},ensure_ascii=False))
'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();out=o.read().decode('utf-8','replace');err=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();result={'exit':rc,'stderr':err,'result':json.loads(out) if rc==0 else {'stdout_length':len(out)}}
finally:c.close()
p=ROOT/'reports'/('canonical_summary72_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(result,ensure_ascii=False,indent=2))
if rc:raise SystemExit(rc)
