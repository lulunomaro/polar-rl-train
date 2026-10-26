"""Keep81N reports immutable and separate; never replay its failed deployer."""
from pathlib import Path
import ast
import json
import time

H=Path(__file__).resolve().parent;T=H.parent
N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026';O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
q=(O/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes()
rec=(O/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes()
target=O/'preparation_exact_history/81N_root_reports_original_bytes'
assert target.resolve().is_relative_to(O.resolve()) and (O/'reports').resolve().is_relative_to(O.resolve()) and not target.exists()
(O/'reports').rename(target);(O/'reports').mkdir()
(O/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').write_bytes(q)
(O/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').write_bytes(rec)
entry=O/'deploy_actual_mixed81o_H1_method_original_writer_unused_once.py';s=entry.read_text('utf8')
s=s.replace("captured=N/'DEPLOYER_REUSED_H1_HELPER_EXACT_SOURCE.py'","captured=N/'DEPLOYER_REUSED_H1_HELPER_81O_EXACT_SOURCE.py'",1)
needle="  c=d.connect72(secret);d.upload(c,d.PY72,'recovery',q)"
assert s.count(needle)==1
partial=r'''
from pathlib import Path
import base64,hashlib,json,os,psutil,time
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_mixed_supermimic_2610v81n');files=[]
for key in ('e2','recovery'):
 B=base/key;assert B.is_dir() and not (B/'NODE_IDENTITY.json').exists() and not (B/'job0/GO_PRODUCTION.json').exists() and not (B/'job0/production_STARTED_ACTUAL.json').exists()
 assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 prior={x['relative'] for x in json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
 for p in B.rglob('*'):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if rel in prior or rel=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or p.suffix not in ('.json','.txt','.log'):continue
  raw=p.read_bytes();assert len(raw)<16*1024**2;files.append(dict(relative=key+'/'+rel,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(dict(epoch=time.time(),all81N_partial_noNODE_noGO_actual_out=True,files=files)))
'''
source="  c=d.connect72(secret)\n  partial=d.code(c,d.PY72,"+repr(partial)+",{},timeout=90)\n  import base64,hashlib\n  returned=[]\n  for row in partial['files']:\n   raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];p=N/'partial81N_installed_CPU_outputs'/row['relative'];p.parent.mkdir(parents=True,exist_ok=True)\n   with p.open('xb') as f:f.write(raw)\n   returned.append(dict(row,local_path=str(p)))\n  partial['files']=returned;put('EXACT81N_PREGO_PARTIAL_SOURCE_CPU_OUTPUTS_RETURNED_ACTUAL.json',partial)\n  d.upload(c,d.PY72,'recovery',q)"
s=s.replace(needle,source,1)
needle=" def code(c,py,source,args,timeout=90):\n"
assert s.count(needle)==1
check="from pathlib import Path;import os,psutil;roots=[Path('/mnt/mod4_linux_durable_20261013/H1step270_mixed_supermimic_2610v81n')/x for x in ('owner','h1')];assert all(not (p/'OWNER_IDENTITY.json').exists() and not (p/'NODE_IDENTITY.json').exists() and not (p/'GO_PRODUCTION.json').exists() for p in roots);assert not any(p.pid!=os.getpid() and any(a.startswith(tuple(str(x)+'/' for x in roots)) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\n"
s=s.replace(needle,needle+"  if source==d.OWNER:source="+repr(check)+"+source\n",1)
ast.parse(s);entry.write_text(s,'utf8')
with (H/'reports/NEW81O_REPORT_NAMES_AND_ORIGINAL81N_MISSING_TEXT_CAPTURE_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original81N_root_reports_preserved_under=str(target),new81O_root_reports_unused=True,newcaptured_helper_name_avoids_FileExists_without_overwrite=True,old81N_CPU_outputs_will_be_missing_only_returned_once=True,old81N_no_NODE_GO_or_own_process_required=True,original_owner_and_other_production_runtime_unchanged=True),f,indent=2)
print(json.dumps(dict(new81O_reports_and_deployer_unused=True)))
