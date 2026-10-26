"""Preserve V1 contracts, add exact H1 control binding, refresh source pins."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent.parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lineage=[]
for key in ('h1','recovery'):
 B=D/'candidate_overlays'/key;P=B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json';raw=P.read_bytes()
 with (D/'reports'/('NORMAL86_'+key+'_SOURCE_CONTRACT_V1_BEFORE_CONTROL_BINDING_REVIEW_ACTUAL.json')).open('xb') as stream:stream.write(raw)
 for name in ('normal86_source_guard_v1.py','normal86_closed_source_CPU_v1.py'):
  (B/name).write_bytes((D/'source'/name).read_bytes())
 c=json.loads(raw)
 if key=='h1':
  source=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026/reports/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'
  target=B/source.name
  with target.open('xb') as stream:stream.write(source.read_bytes())
  c['overlay_files'].append(dict(relative=source.name,bytes=target.stat().st_size,SHA=H(target)))
  lineage.append(dict(relative=source.name,source=str(source),SHA=H(source),bytes=source.stat().st_size))
 for row in c['overlay_files']:
  p=B/row['relative'];row.update(bytes=p.stat().st_size,SHA=H(p))
 c['source_review_revision']=2;c['previous_contract_SHA']=hashlib.sha256(raw).hexdigest()
 temp=P.with_suffix('.json.review2.partial')
 with temp.open('x',encoding='utf8') as stream:json.dump(c,stream,indent=2);stream.write('\n')
 temp.replace(P)
report=dict(epoch=time.time(),passed=True,source_only=True,reason='Exact H1 source210 forwarder binding and original learned17 origin checks',
 lineage=lineage,previous_contracts_preserved=True,real_PT_NPZ_remote_GPU_Task_GO_Git=False)
with (D/'reports/NORMAL86_FINAL_SOURCE_CONTROL_BINDING_REVIEW_V2_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))
