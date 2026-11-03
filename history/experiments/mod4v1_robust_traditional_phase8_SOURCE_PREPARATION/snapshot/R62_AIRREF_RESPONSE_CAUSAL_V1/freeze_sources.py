"""Small-source lock only. Does not open any raw trace/physics content."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
METHOD=json.loads((OUT/'METHOD.json').read_bytes())
def rec(p):
    p=p.resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
SOURCES=['MINIHOP_AIR_PITCH_REF_V1/attempt002/controller.py','MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py','run_manual_position_v4.py','MINIHOP_POSITION_TRIGGER_V1/controller.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_V1/controller.py','ground_controller_v4.py','sensor_core_jump_v1.py','physics_bridge_rm_grade_v1.py','physics_bridge_v4_grade.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MANUAL_FIRST_BAR_V1/grade_rows.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py','JUMP270_V1/GAIN_BANK.json','reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.json','reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.md']
cases=list(dict.fromkeys(a['case']for a in METHOD['raw_allowlist']))
refs={str((ROOT/s).resolve()):rec(ROOT/s)for s in SOURCES}
results={};manifests={};matches=[]
for c in cases:
    d=ROOT/'results'/c
    for name in ['result.json','SOURCE_MANIFEST.json']:
        p=d/name;refs[str(p.resolve())]=rec(p)
    r=load(d/'result.json');m=load(d/'SOURCE_MANIFEST.json');results[c]=r;manifests[c]=m
    assert r['config']['case_id']==c and r['complete']and r['controls']==800 and r['physics_steps']==16000
    records={}
    for z in m['files']:
        p=str(Path(z['path']).resolve())
        if p in records:assert records[p]==z['SHA']
        records[p]=z['SHA']
        if p in refs:
            assert refs[p]['SHA']==z['SHA'],(c,p,'source drift')
            matches.append(dict(case=c,path=p,SHA=z['SHA']))
    required=['MINIHOP_V1/controller.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_POSITION_TRIGGER_V1/controller.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py']
    required+=['MINIHOP_AIR_PITCH_REF_V1/attempt002/controller.py','MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py']if c.startswith('r62_')else['run_manual_position_v4.py']
    for p in required:assert str((ROOT/p).resolve())in records,(c,p,'missing producer provenance')
raw=[]
for a in METHOD['raw_allowlist']:
    p=(ROOT/'results'/a['case']/a['file']).resolve();r=results[a['case']]
    art=r['trace_artifact'if a['file']=='trace.jsonl'else'physical_artifact'];st=p.stat()
    assert p==Path(art['path']).resolve()and st.st_size==art['bytes']
    raw.append(dict(**a,path=str(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns,producer_SHA_not_recomputed=art['SHA']))
q=load(ROOT/'JUMP270_V1/GAIN_BANK.json')['gains']['crouch']['q']
pairs=[]
for s in [4606,4610]:
    a=results[f'r60_tall0_fresh_RM_DR_{s}'];b=results[f'r62_airref002_paired_RM_DR_{s}']
    pairs.append(dict(seed=s,DR_metadata_equal=a['DR']==b['DR'],old_original_gate=a['proposed_manual_first_bar_clear_stop_v1'],new_original_gate=b['proposed_manual_first_bar_clear_stop_v1']))
value=dict(kind='LOCKED_BEFORE_ANY_RAW_OPEN',method=rec(OUT/'METHOD.json'),sources=list(refs.values()),selected_manifest_matches=matches,raw=raw,raw_content_reads=0,raw_hashes_recomputed=0,paired_metadata=pairs,public_crouch_absolute_q4=[q[3],q[3]+q[4],q[5],q[5]+q[6]])
with(OUT/'SOURCE_LOCK.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=value['kind'],small_sources=len(refs),selected_manifest_matches=len(matches),raw_paths=len(raw),raw_content_reads=0,pairs=pairs),indent=2))
