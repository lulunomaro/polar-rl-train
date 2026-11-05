"""Prepare only the tested residual-scale repair after completed actual80."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
read=lambda p:json.loads(Path(p).read_bytes())
P=N/'supermimic_final881_host_replay02_1h'
A=N/'supermimic_final1940_residual025_1h'
f=read(P/'reports/POSTROUND_FULL_RETURNED.json')['files'];owner=f['OWNER_EXIT.json']
assert read(P/'reports/POSTROUND_COMPLETED.json')['complete']
assert not owner['error']and owner['all_own_waited']and owner['original_leases_released']
assert read(P/'reports/ACTUAL_NATIVE_REVIEW.json')['all_actual_images_reviewed']
assert read(N/'reports/RESIDUAL025_FULL_RESUME_TEST.json')['passed']
assert read(N/'residual025_final1940_eval80/ACTUAL_NATIVE_REVIEW.json')['all_actual_images_reviewed']
old=read(P/'PLAN.json');ck=f['production/FINAL.json']['checkpoint']
plan=dict(old)
plan.update(remote_root=old['remote_root'].rsplit('/',1)[0]+'/'+A.name,
    run_id='newton_supermimic_residual025_'+str(time.time_ns()),
    previous_overlay_paths=[old['remote_root']+'/overlay',*old['previous_overlay_paths']],
    source_checkpoint=ck,source_iteration=1940,policy_residual_scale=.25,
    source_BPTT_counts=ck['counts'],source_PPO_iteration=881,
    cumulative_authorized_seconds_before_this_segment=old['cumulative_authorized_seconds_before_this_segment']+owner['actual_elapsed_seconds'],
    specific_repair='Bound learned residual to.25 after actualall80guide06early-contact collapse; full1940learnedmodels/4Adam/replay/RNG retained; Fudan/physics/DR unchanged',
    previous_native_review=str(P/'reports/ACTUAL_NATIVE_REVIEW.json'),
    candidate_eval=str(N/'residual025_final1940_eval80/ACTUAL_NATIVE_REVIEW.json'),
    state_read_fusion_enabled=False)
plan.pop('GPU_UUID',None)
assert plan['cumulative_authorized_seconds_before_this_segment']+3900<=360000
A.mkdir(exist_ok=False);(A/'reports').mkdir();files=[]
def add(path,relative):
    raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,
        bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for name in ('supermimic_newton.py','supermimic_train.py','supermimic_evaluate.py'):add(CODE/name,'overlay/'+name)
binding=A/'SUPERMIMIC_BINDINGS.json';binding.write_bytes((P/'SUPERMIMIC_BINDINGS.json').read_bytes());add(binding,binding.name)
add(N/'newton_entry.py','entry.py');add(N/'newton_owner.py','owner.py')
add(N/'newton_fudan_final620_1h/run-newton.sh','run-newton.sh')
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,
    shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],whole_tree_copies=0,
    checkpoint_copies=0,asset_copies=0,all_pinned_learner_source_referenced=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(A),source=ck,files=len(files),cumulative_before=plan['cumulative_authorized_seconds_before_this_segment'])))
