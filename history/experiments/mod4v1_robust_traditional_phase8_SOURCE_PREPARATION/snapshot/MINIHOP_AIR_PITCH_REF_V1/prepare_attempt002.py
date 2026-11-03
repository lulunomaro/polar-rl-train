"""Write explicit parent-approved second precode lock, not a gain/limit retry."""
from pathlib import Path
import hashlib,json,datetime
T=Path(__file__).resolve().parent;D=T/'attempt002';R=T.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((T/'SOURCE_LOCK.json').read_bytes());bad=json.loads((T/'attempt001/LIMITS_RESULT.json').read_bytes())
assert bad['status']=='NOT_READY_DOMAIN'and bad['offsets']==51 and bad['violating_offset_count']==14 and bad['math_gate_pass']
for x in old['sources']:assert sha(Path(x['path']))==x['SHA']
for n in ['ARCHITECTURE.md','METHOD.json','SOURCE_LOCK.json','freeze_sources.py','freeze_001.log','fk_limits.py','run_limits_001.py']:
    assert sha(T/n)==sha(T/'attempt001'/n)
assert not(D/'controller.py').exists()and not(D/'run_manual_air_pitch_ref_v1.py').exists()
m=json.loads((T/'METHOD.json').read_bytes())
m['kind']='ATTEMPT002_EXPLICIT_PARENT_APPROVED_ASYMMETRIC_DOMAIN_PRECODE'
p=m['fixed_parameters'];del p['h_abs_limit_rad'];p.update(h_min_rad=-.10,h_max_rad=.03)
m['cohorts']['FK_offset_interval_rad']=[-.10,.03]
m['cohorts']['flight_and_capture_reference_FK']='every actual commanded flight and timed_capture reference from enabled synthetic 600 ticks'
m['limits_gate']='All 51 new offsets and all synthetic flight/capture actual references must satisfy original XML limited joints and public delta envelope with zero limit relaxation; any failure stops NOT_READY, no third hypothesis.'
m['parent_amendment']='Only h upper .10->.03 based on public crouch/limit; lower -.10 and kp/kd/rate/period/timings/observer/wheel equations unchanged. Nominal margin is not DR safety guarantee.'
with(D/'METHOD.json').open('x',encoding='utf-8')as f:json.dump(m,f,indent=2,allow_nan=False);f.write('\n')
v=dict(kind='ATTEMPT002_PRECODE_LOCK_ONE_EXPLICIT_PARENT_DOMAIN_AMENDMENT',at=datetime.datetime.now().astimezone().isoformat(),
    method_SHA=sha(D/'METHOD.json'),architecture_SHA=sha(D/'ARCHITECTURE.md'),sources=old['sources'],
    unchanged_shared_FK_SHA=sha(T/'fk_limits.py'),original_precode_source_lock_SHA=sha(T/'SOURCE_LOCK.json'),
    attempt001_failed_result_SHA=sha(T/'attempt001/LIMITS_RESULT.json'),attempt001_preexec_SHA=sha(T/'attempt001/PREEXEC.json'),
    original_symmetric_method_preserved=True,amendment=dict(h_min=-.10,h_max=.03,kp=.25,kd=.04,rate=1.,period=.01,no_gain_fit=True,no_model_limit_change=True,no_DR_bound_guarantee=True),
    no_controller_or_entry_yet=True,no_third_hypothesis_authorized=True,PH7_pending=True)
with(D/'SOURCE_LOCK.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(old_sources_unchanged=len(old['sources']),attempt001_status=bad['status'],attempt001_violating_offsets=14,attempt002_method_SHA=v['method_SHA'],attempt002_source_lock_SHA=sha(D/'SOURCE_LOCK.json'),prototype_code_exists=False,model_boots=0,raw_reads=0),indent=2))
