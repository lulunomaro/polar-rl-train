"""Read only the existing canonical budget/public schedule and current hardware.
Does not reserve, sign, launch, write a remote file or print credential fields.
"""
from pathlib import Path
import json,datetime,hashlib,re,stat
from project_connector import connect72
ROOT=Path(__file__).resolve().parent;BASE='/home/lc01/Zonglin Li/zonglin2';AUTH=BASE+'/state/mod4_single_canonical_authority_20261026'
SENSITIVE=re.compile(r'password|passwd|secret|token|credential|hmac|signature|private.?key',re.I)
def scrub(v):
 if isinstance(v,dict):return {k:('[REDACTED_FIELD]' if SENSITIVE.search(str(k)) else scrub(x)) for k,x in v.items()}
 if isinstance(v,list):return [scrub(x) for x in v]
 return v
r={'captured_local':datetime.datetime.now().astimezone().isoformat(),'authority_root':AUTH,'read_only':True,'commands':{},'files':{}}
c=connect72();s=c.open_sftp()
try:
 for label,cmd in {'gpus':'nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits','compute_apps':'nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory,name --format=csv,noheader,nounits'}.items():
  i,o,e=c.exec_command(cmd,timeout=30);i.close();r['commands'][label]={'stdout':o.read().decode(),'stderr':e.read().decode(),'exit':o.channel.recv_exit_status()}
 rows=s.listdir_attr(AUTH);r['authority_directory']=[{'name':v.filename,'bytes':v.st_size,'mtime':v.st_mtime,'dir':stat.S_ISDIR(v.st_mode)} for v in rows]
 chosen=[v for v in rows if v.filename=='TRAINING_BUDGET_10H.json' or ('PUBLIC' in v.filename.upper() and v.filename.endswith('.json')) or v.filename=='AUTHORITY_HANDOFF_ACTUAL.json']
 for v in chosen:
  if v.st_size>4000000:r['files'][v.filename]={'status':'size_bound','bytes':v.st_size};continue
  with s.open(AUTH+'/'+v.filename,'rb') as f:raw=f.read()
  try:r['files'][v.filename]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'data':scrub(json.loads(raw))}
  except json.JSONDecodeError:r['files'][v.filename]={'status':'non_json_or_moving','bytes':len(raw)}
 for rel in ('run-python.sh','README.md','README_DEPLOYING.md','AGENTS.md','src/fangzhen_linux/AGENTS.md'):
  try:
   with s.open(BASE+'/'+rel,'rb') as f:raw=f.read(64000)
   r.setdefault('documents',{})[rel]=raw.decode('utf-8','replace')
  except OSError:pass
finally:s.close();c.close()
p=ROOT/'reports'/('authority72_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(r,ensure_ascii=False,indent=2))
