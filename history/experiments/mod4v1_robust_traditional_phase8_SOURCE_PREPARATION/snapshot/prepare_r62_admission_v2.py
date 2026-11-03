"""Metadata-only amendment after two concrete static launcher findings.
No replay of the passed79-source/controller QA or any model/physics execution.
"""
from pathlib import Path
import hashlib,json,copy
R=Path(__file__).resolve().parent;V1=R/'R62_AIRREF_ADMISSION_V1';D=R/'R62_AIRREF_ADMISSION_V2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
assert not D.exists();D.mkdir()
dump(D/'PREPARE_PREEXEC.json',dict(kind='ADMIN_SOURCE_DELTA_ONLY_NO_CONTROL_EXECUTION',preparer=str(Path(__file__)),SHA=sha(Path(__file__)),new_physics_steps=0))
a=load(R/'PARENT_R62_DELTA_PREFLIGHT_V1/RESULT.json')
assert a['status']=='PASS_16_NEW_SOFTWARE_DELTA_FIXTURES_NO_PHYSICS' and a['new_physics_steps']==0 and a['actual_subprocesses']==0
for z in a['source_hashes_after']:assert sha(z['path'])==z['SHA'],z['path']
s=load(V1/'SOURCE_PREEXEC.json');files=copy.deepcopy(s['files']);old={Path(z['path']).resolve():z['SHA']for z in files}
# Preserve inherited source records; actual launcher checks all before integration.
newpaths=[R/n for n in('fresh_train_batch_v2.py','r62_nominal_evidence_v1.py','launch_manual_profile_train_v4.py','launch_r62_airref_paired_train_v2.py','prepare_r62_launch_delta_v2.py','preflight_r62_launch_delta_v2.py')]
newpaths += [R/'PARENT_R62_DELTA_PREFLIGHT_V1/RESULT.json',R/'R62_AIRREF_PAIRED_LAUNCH_REVIEW.json',V1/'PARENT_REVIEW_HOLD.json',Path(__file__)]
for p in newpaths:
    p=p.resolve();assert p.is_relative_to(R) and p.stat().st_size<512000
    value=sha(p)
    if p in old:assert old[p]==value
    else:files.append(dict(path=str(p),SHA=value,bytes=p.stat().st_size));old[p]=value
p=load(V1/'PROTOCOL.json');p['kind']='R62_AIRREF002_NOMINAL_ARTIFACT_STOP_V2'
p['software_delta']='Newhelper_v2 stops software errors from artifacts as well as rc; newnom_v4 records allRM deferred on flat software abort. All controller/actuator/success gates unchanged.'
p['inheritance']='Old static core/entry/source evidence reused; oldreadytrue review kept with parentHOLD and correction history, not actual physics approval.'
p['same_unused_case_IDs_not_replayed']=True
for name,c in p['configs']:assert not(R/'results'/name).exists()
dump(D/'PROTOCOL.json',p)
files.append(dict(path=str(D/'PROTOCOL.json'),SHA=sha(D/'PROTOCOL.json'),bytes=(D/'PROTOCOL.json').stat().st_size))
dump(D/'SOURCE_PREEXEC.json',dict(kind='SOURCE_V2_SOFTWARE_ONLY_DELTA_WITH_INHERITED_CORE_EVIDENCE',files=files,preparer_SHA=sha(Path(__file__)),
    inherited_index_path=str(V1/'SOURCE_PREEXEC.json'),inherited_index_SHA=sha(V1/'SOURCE_PREEXEC.json'),inherited_actual_source_records=len(s['files']),
    new_controller_source_changes=0,no_old_QA_or79source_scan_replay=True,no_model_or_integrator_execution=True,post_PH7_cutoff_pending=True))
dump(D/'CORRECTION_FROM_V1.json',dict(kind='STATIC_GUARD_FIX_NOT_CHANGED_PHYSICS_GATE',
    old_nominal_review_path=str(V1/'PRE_EXEC_REVIEW.json'),old_nominal_review_SHA=sha(V1/'PRE_EXEC_REVIEW.json'),
    old_parent_HOLD=str(V1/'PARENT_REVIEW_HOLD.json'),narrow_negative_review=str(R/'R62_AIRREF_PAIRED_LAUNCH_REVIEW.json'),
    issues_fixed=['rc0 plus ERROR/missing/bad JSON stops future waves and persists deferredRM','paired actualconfig equals locked enabled nominal profiles plus runtime manifest candidateSHA binding'],
    actual_bad_nominal_observed=False,actual_R62_physics_so_far=0,old_sources_reports_not_rewritten=True))
v=dict(status='PASS_R62_V2_METADATA_ONLY_SOFTWARE_DELTA_TESTED',integrator_calls=0,new_physics_steps=0,source_count=len(files),
       inherited_core_entry_QA_reused=True,old_600_FK_entry_replays=0,delta_fixtures=16,controller_or_model_invocations=0,
       independent_delta_review_and_parent_approval_required=True,nominal_dynamic_qualification='UNKNOWN',post_PH7_cutoff_pending=True)
dump(D/'RESULT.json',v);print(json.dumps(v,indent=2))
