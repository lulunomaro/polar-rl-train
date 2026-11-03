"""Saved-result metadata only: no model boot, forward, integration or asset reads."""
from pathlib import Path
from urllib.parse import unquote
import hashlib,json,re
D=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,separators=(',',':'),allow_nan=False);f.write('\n')
m=load(D/'METHOD.json');lock=load(D/'SOURCE_LOCK.json');v=load(D/'STATIC_GEOMETRY.json')
assert sha(D/'METHOD.json')==lock['method_SHA']==v['method_SHA']
assert sha(D/'SOURCE_LOCK.json')==v['source_lock_SHA'] and sha(D/'static_geometry.py')==v['script_SHA']
for s in lock['sources']:
    p=Path(s['path']);assert p.stat().st_size==s['bytes']and sha(p)==s['SHA'],('source changed',s['path'])
expected={(c['name'],w,p)for c in m['candidates']for w in m['reference_weights']for p in m['pitches_rad']}
observed={(r['candidate'],r['weight'],r['pitch_rad'])for r in v['rows']}
assert len(v['rows'])==len(expected)==30 and observed==expected
assert v['model_boots']==1 and v['calls']['mj_forward']==30 and v['time_s']==0.
assert all(v['calls'][x]==0 for x in m['blocked_integrators'])
assert all(r['two_tire_co_support_numerically_consistent']for r in v['rows'])
assert all(r['sign']=='POSITIVE' and r['clearance_over_6cm_plane_m']>0 for r in v['rows'])
text=(D/'REPORT.md').read_text(encoding='utf-8');line_count=len(text.splitlines());assert line_count<=m['report_max_lines']
links=re.findall(r'\]\(<([^>]+)>\)',text)
for target in links:
    name,_,fragment=unquote(target).partition('#');p=Path(name);assert p.is_absolute()
    if p==D/'RECEIPT.json':continue
    assert p.is_file(),('bad report link',name)
    if fragment:
        r=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment);assert r
        lo=int(r[1]);hi=int(r[2]or r[1]);assert 1<=lo<=hi<=len(p.read_text(encoding='utf-8').splitlines())
files=['METHOD.json','SOURCE_LOCK.json','STATIC_GEOMETRY.json','REPORT.md','freeze_sources.py','static_geometry.py',
       'finalize_report.py','freeze_01.log','static_01.log']
minimum=min(v['rows'],key=lambda r:r['clearance_over_6cm_plane_m'])
r=dict(status='SEALED_NOMINAL_STATIC_GUIDE05_VERTICAL_GEOMETRY_ONLY_NOT_ACTUAL4505_OR_OPERATING_LIMIT',
    report_lines=line_count,verified_report_links=len(links),small_source_SHA_unchanged=len(lock['sources']),
    model_boots=1,static_joint_pitch_queries=30,mj_forward_calls=30,integrator_entry_counts={k:v['calls'][k]for k in m['blocked_integrators']},
    simulated_time_s=0.,positive_points=30,zero_points=0,negative_points=0,minimum_conditional_margin_m=minimum['clearance_over_6cm_plane_m'],
    minimum_point={k:minimum[k]for k in ('candidate','weight','pitch_rad')},
    model=v['model'],primitive=v['primitive'],consistency=v['consistency'],
    wheel_phase_assumption='public nominal FK wheel_spin0, not all-phase certificate',
    asset_policy='original normal model boot only; no extra asset archival hashes; evaluate two tire caches plus guide05 only',
    raw_files_opened=0,DR_samples_read=0,asset_archival_hashes=0,compiled_C_sources=0,new_episodes=0,old_QA_runs=0,
    agents_started=0,Git_actions=0,R56_source_changes=False,controller_or_gain_changes=False,
    gain_selected=False,contact_confidence_increased=False,actual4505_clearance_claim=False,
    dynamic_stability_certificate=False,new_operating_limit=False,PH7_pending=True,
    files=[dict(path=f,bytes=(D/f).stat().st_size,SHA=sha(D/f))for f in files])
put(D/'RECEIPT.json',r)
print(json.dumps(dict(status=r['status'],report_lines=line_count,small_sources_unchanged=len(lock['sources']),
    queries=30,forwards=30,integrator_calls=0,positive=30,negative=0,minimum_conditional_margin_mm=minimum['clearance_over_6cm_plane_m']*1000,
    report_SHA=sha(D/'REPORT.md'),static_JSON_bytes=(D/'STATIC_GEOMETRY.json').stat().st_size,
    static_JSON_SHA=sha(D/'STATIC_GEOMETRY.json'),receipt_SHA=sha(D/'RECEIPT.json')),indent=2))
