"""Small selected sources only, no raw contents or project imports."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=load(D/'METHOD.json')
source=['run_manual_capture_v3.py','MINIHOP_V1/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_LANDING_V3/controller.py',
 'ground_controller_v4.py','sensor_core_jump_v1.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MINIHOP_AUDIT_V2/schema_v2.py',
 'MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py','physics_bridge_rm_buffer_v1.py','physics_bridge_rm_grade_v1.py',
 'MANUAL_FIRST_BAR_V1/grade_rows.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py']
paths=source+['batches/r55_first_bar_DR8/PROTOCOL.json']
checks=[];cases=[]
for name in m['cases']:
    p=R/'results'/name;cfg=load(p/'config.json');res=load(p/'result.json');man=load(p/'SOURCE_MANIFEST.json')
    assert cfg==res['config'] and not cfg['nominal'] and cfg['case_id']==name
    assert res['complete'] and res['controls']==800 and res['physics_steps']==16000
    assert res['guide_contact_physics_ticks']==m['recorded_guide_ticks_preserved'][name]
    assert res['proposed_manual_first_bar_clear_stop_v1'] is False
    index={str(Path(x['path']).resolve()).lower():x for x in man['files']}
    for f in source:
        q=(R/f).resolve();r=index[str(q).lower()]
        assert sha(q)==r['SHA'] and q.stat().st_size==r['bytes'],('manifest mismatch',name,f)
        checks.append(dict(case=name,path=f,SHA=r['SHA']))
    raw=[]
    for kind in ('trace','physics'):
        q=p/(kind+'.jsonl');k='trace_artifact' if kind=='trace' else 'physical_artifact';a=res[k]
        assert q.resolve()==Path(a['path']).resolve() and q.stat().st_size==a['bytes'] and a['producer_streamed_once']
        st=q.stat();raw.append(dict(path=q.relative_to(R).as_posix(),bytes=st.st_size,mtime_ns=st.st_mtime_ns,
            producer_SHA_not_recomputed=a['SHA'],kind=kind))
    cases.append(dict(case=name,raw=raw,original_guide_ticks=res['guide_contact_physics_ticks'],original_pass=res['proposed_manual_first_bar_clear_stop_v1'],
        first_bar=res['first_transverse_bar'],first_air_s=res['first_all_world_air_s'],first_landing_stage_s=res['first_landing']['stage_time_s']))
    paths += [f'results/{name}/{f}.json' for f in ('config','result','SOURCE_MANIFEST')]
small=[]
for f in paths:
    p=R/f;assert p.stat().st_size<262144
    small.append(dict(path=f,bytes=p.stat().st_size,SHA=sha(p)))
v=dict(kind='SMALL_INPUT_LOCK_BEFORE_SINGLE_RAW_PASS',method_SHA=sha(D/'METHOD.json'),small=small,cases=cases,
    actual_manifest_matches=checks,raw_contents_opened=0,raw_archival_hashes=0,mesh_assets_read_or_hashed=0)
with (D/'SOURCE_LOCK.json').open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps(dict(small_sources=len(small),manifest_matches=len(checks),method_SHA=v['method_SHA'],lock_SHA=sha(D/'SOURCE_LOCK.json'),
    raw_contents_opened=0,mesh_assets=0,original_guides=[c['original_guide_ticks'] for c in cases]),indent=2))
