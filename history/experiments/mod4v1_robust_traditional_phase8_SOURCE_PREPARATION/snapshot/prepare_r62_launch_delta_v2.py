"""Generate new launchers only; preserve every reviewed old source byte."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent

def save(name,text):
    p=R/name;assert not p.exists();ast.parse(text)
    with p.open('x',encoding='utf-8',newline='')as f:f.write(text)
    return dict(path=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest())

s=(R/'launch_manual_profile_train_v3.py').read_text(encoding='utf-8')
s=s.replace('from fresh_train_batch_v1 import launch,dump','from fresh_train_batch_v2 import launch,dump')
s=s.replace('V1/V2 immutable.','V1/V2/V3 immutable. V4 uses artifact-aware software-stop waves.')
old="f=launch(R,args.batch_prefix+'_flat',args.runner,flat,meta,keys,max_workers=workers)"
new="""try:
    f=launch(R,args.batch_prefix+'_flat',args.runner,flat,meta,keys,max_workers=workers)
except BaseException:
    # Do not infer a successful RM admission from a software-aborted flat wave.
    dump(D/'RM_ADMISSION_DECISION.json',dict(status='FLAT_SOFTWARE_ABORT_NO_RM_LAUNCH',
        unstarted_deferred_RM=[n for n,c in rm],flat_batch_evidence=str(R/'batches'/(args.batch_prefix+'_flat')/'BATCH_RESULT.json'),
        actual_counts_only_from_saved_artifacts_not_duration=True))
    raise"""
assert s.count(old)==1;s=s.replace(old,new)
a=save('launch_manual_profile_train_v4.py',s)
p=(R/'launch_r62_airref_paired_train_v1.py').read_text(encoding='utf-8')
p=p.replace('from fresh_train_batch_v1 import launch,dump','from fresh_train_batch_v2 import launch,dump\nfrom r62_nominal_evidence_v1 import validate_enabled_nominals')
p=p.replace("D=R/'R62_AIRREF_ADMISSION_V1';P=R/'R62_AIRREF_PAIRED_TRAIN_V1'","D=R/'R62_AIRREF_ADMISSION_V2';P=R/'R62_AIRREF_PAIRED_TRAIN_V2'")
start=p.index("flat=load(flatp);rm=load(rmp)")
end=p.index("runner='MINIHOP_AIR_PITCH_REF_V1",start)
p=p[:start]+"""flat=load(flatp);rm=load(rmp)
assert approval['flat_result_SHA']==sha(flatp) and approval['RM_result_SHA']==sha(rmp)
fm=flatp.parent/'SOURCE_MANIFEST.json';mm=rmp.parent/'SOURCE_MANIFEST.json'
assert approval['flat_manifest_SHA']==sha(fm) and approval['RM_manifest_SHA']==sha(mm)
nominal_binding=validate_enabled_nominals(R,load(D/'PROTOCOL.json'),sources,flat,rm,load(fm),load(mm))
"""+p[end:]
p=p.replace("no_old_raw_or_baseline_replay=True,PH8_pending=True)","no_old_raw_or_baseline_replay=True,actual_nominal_binding=nominal_binding,PH8_pending=True)")
b=save('launch_r62_airref_paired_train_v2.py',p)
print(json.dumps(dict(kind='NEW_LAUNCH_DELTA_ONLY_NO_PROJECT_OR_PHYSICS_EXECUTION',files=[a,b],new_physics_steps=0),indent=2))
