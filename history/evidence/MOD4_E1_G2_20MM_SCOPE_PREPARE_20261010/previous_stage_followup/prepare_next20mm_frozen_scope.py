"""Advance only the approved20mm geometric axis in an independent frozen evidence scope."""
from pathlib import Path
import ast,json,hashlib,zipfile,time
W=Path(__file__).resolve().parent.parent;old=W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010';D=W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010';assert not D.exists();D.mkdir();R=D/'reports';R.mkdir();A=D/'artifacts';A.mkdir();H=lambda b:hashlib.sha256(b).hexdigest()
selector=json.loads((old/'reports/SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json').read_bytes());cpu=json.loads((old/'reports/NEXT20MM_GEOMETRY_CPU_PREPARED.json').read_bytes());assert selector['behavior_review_complete'] and cpu['passed_CPU_geometry_only']
v=json.loads(sorted((old/'reports').glob('PROXY_ROUTE_REVIEW_*.json'))[-1].read_bytes());assert v['review_complete'] and not v['pending']
base=old/'artifacts/e1-g1-complete-wave-route-v4-proxy-frozen.zip'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
entry='runtime/isaac/mod4/frozen_history_flat.py';s=payload[entry].decode().replace('from g1_cad_wave_geometry import configure_g1','from g2_cad_wave_geometry import configure_g2').replace('from g1_cad_wave_geometry import profile','from g2_cad_wave_geometry import profile').replace('CAD_derived10mm_wave','CAD_derived20mm_wave').replace('sampled.max()<=.010001','sampled.max()<=.020001').replace('approved_E1_G1_complete_wave_route_behavior_v4','approved_E1_G2_derived20mm_complete_wave_route_behavior_v1')
assert 'g1_cad_wave_geometry import' not in s;ast.parse(s);payload[entry]=s.encode()
for name in ('g2_cad_profile.json','g2_cad_wave_geometry.py'):payload['runtime/isaac/mod4/'+name]=(old/'next20mm_cpu'/name).read_bytes()
changed=[entry,'runtime/isaac/mod4/g2_cad_profile.json','runtime/isaac/mod4/g2_cad_wave_geometry.py']
with zipfile.ZipFile(base) as z:assert all(payload[n]==z.read(n) for n in m['files'] if n!=entry)
m.update(files={n:H(b) for n,b in payload.items()},protocol='approved_E1_G2_derived20mm_complete_wave_route_behavior_v1',original_G1_members_retained=True,only_next20mm_geometry_and_dispatcher_scope_changed=True)
p=A/'e1-g2-derived20mm-complete-route-frozen.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(m,indent=2))
for name in ('SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json','NEXT20MM_GEOMETRY_CPU_PREPARED.json'):(R/name).write_bytes((old/'reports'/name).read_bytes())
(D/'frozen20mm_route.py').write_text(s,encoding='utf8')
pub=json.loads((old/'reports/PROXY_ROUTE_PUBLISHED.json').read_bytes());template=next(x for x in pub['jobs'] if x['role']=='anchor32053');(R/'MANIFEST_TEMPLATE.json').write_text(json.dumps(template,indent=2),encoding='utf8')
report=dict(epoch=time.time(),trial_id='E1-G2-20MM-FROZEN-SCOPE-PREPARE-01',package=dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p.read_bytes())),protocol=m['protocol'],changed_or_added_members=changed,all_original_geometry_DR_assets_and_hardware_other_members_byteexact=True,source=selector['source'],full10mm_paired_actual_review_reused=True,CPU20mm_actual9m_geometry_proof=cpu,only_new_geometry_axis=True,no_SDK_native_PPO_executor_deployed=True,no_production_runtime_or_canonical_write=True,new_budget_seconds=0,actual20mm_frozen_result_pending=True)
(R/'PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(root=str(D),package=report['package'],no_learning=True)))
