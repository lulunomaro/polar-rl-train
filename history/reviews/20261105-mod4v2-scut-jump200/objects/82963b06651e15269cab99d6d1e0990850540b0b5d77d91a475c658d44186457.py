"""Freeze only changed MOD4 source and references for the authorized repair hour."""
from pathlib import Path
import json,hashlib,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
P=N/'supermimic_final3786_sampling_1h'
A=N/'supermimic_final5936_semantic_repair_1h'
read=lambda p:json.loads(Path(p).read_bytes())
assert read(N/'supermimic_repair_cpu01/RESULT.json')['passed']
assert read(N/'supermimic_repair_native01/RESULT.json')['passed']
assert read(P/'reports/POSTROUND_COMPLETED.json')['complete']
boundary=read(P/'reports/FINAL5936_BOUNDARY_REVIEW.json')
assert boundary['all3_formal_transfers_SHAverified'] and boundary['sole78196_completed_and_exited']
assert read(P/'reports/ACTUAL_NATIVE_REVIEW.json')['all_actual_images_reviewed']
plan=read(P/'PLAN.json')
plan.update(remote_root=plan['remote_root'].rsplit('/',1)[0]+'/'+A.name,
    run_id='newton_supermimic_semantic_repair_'+str(time.time_ns()),
    source_checkpoint=boundary['checkpoint'],source_iteration=5936,
    source_BPTT_counts=boundary['checkpoint']['counts'],
    previous_overlay_paths=[read(P/'PLAN.json')['remote_root']+'/overlay',*plan['previous_overlay_paths']],
    cumulative_authorized_seconds_before_this_segment=boundary['cumulative_upper_after'],
    previous_native_review=str(P/'reports/ACTUAL_NATIVE_REVIEW.json'),
    semantic_repair=True,checkpoint_interval_seconds=300.,policy_residual_scale=.25,
    specific_repair='Explicit context139to176, held commands/DR/duplicate observations/physical sensors100Hz midpoint, terrain; jointH32 fit, real replay critic/PopArt+finite ending, transaction and cleanup; no sharedvendor changes.',
    human_latest='修复完就开始训啊',old_source_unchanged=True,
    extension_contract_migration='explicit named v1to176; fourAdam retained; original replay at source;64freshcontrols before any update')
plan.pop('GPU_UUID',None)
assert plan['cumulative_authorized_seconds_before_this_segment']+3900<=plan['cumulative_limit_seconds']
A.mkdir(exist_ok=False);(A/'reports').mkdir();files=[]
def add(path,relative):
 raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for name in ('supermimic_train.py','supermimic_newton.py','supermimic_evaluate.py','supermimic_semantics.py','supermimic_repaired.py'):
 add(CODE/name,'overlay/'+name)
binding=A/'SUPERMIMIC_BINDINGS.json';binding.write_bytes((P/binding.name).read_bytes());add(binding,binding.name)
entry=A/'entry.py'
text=(N/'newton_entry.py').read_text(encoding='utf8')
text=text.replace("if p.get('sampling_optimization',False):sys.argv+=['--sampling-optimization']",
    "if p.get('sampling_optimization',False):sys.argv+=['--sampling-optimization']\n  if p.get('semantic_repair',False):sys.argv+=['--semantic-repair']")
entry.write_text(text,encoding='utf8');add(entry,entry.name)
for name,relative in [('newton_owner.py','owner.py'),('newton_fudan_final620_1h/run-newton.sh','run-newton.sh')]:add(N/name,relative)
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],
    whole_tree_copies=0,asset_copies=0,checkpoint_copies=0,pinned_vendor_unchanged=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(A),files=len(files),source=boundary['checkpoint'],
    cumulative_upper_before=boundary['cumulative_upper_after'])))
