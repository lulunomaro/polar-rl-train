"""Continue the durable1941 state after reboot, actual80 and native review."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
P=N/'supermimic_final1940_residual025_1h'
E=P/'recovery_first1941_eval80'
A=N/'supermimic_first1941_reboot_periodic_1h'
read=lambda p:json.loads(Path(p).read_bytes())
assert read(E/'COMPLETED.json')['complete']
assert read(E/'ACTUAL_NATIVE_REVIEW.json')['all_actual_images_reviewed']
assert read(E/'SURVIVING_FIRST1941_LEARNER_AND_ALL80.json')['passed']
assert read(N/'reports/PERIODIC_FULL_CHECKPOINT_RESTORE_TEST.json')['passed']
interrupted=read(P/'reports/HOST_REBOOT_INTERRUPTED_WINDOW_AND_RECOVERY.json')
assert interrupted['original_exact_owner_dead']and interrupted['original_exact_worker_dead']
old=read(P/'PLAN.json');ck=read(E/'PLAN.json')['checkpoint']
result=read(E/'FULL_RETURNED.json')['files']
assert result['RELEASE.json']['error']is None and result['RELEASE.json']['GPU_lock_released']
assert result['evaluation/RESULT.json']['source_SHA']==ck['SHA']
eval_elapsed=result['RELEASE.json']['epoch']-result['RESOURCE.json']['epoch']
budget_upper=interrupted['conservative_cumulative_upper_before_eval']+eval_elapsed
plan=dict(old)
plan.update(remote_root=old['remote_root'].rsplit('/',1)[0]+'/'+A.name,
 run_id='newton_supermimic_reboot_periodic_'+str(time.time_ns()),
 previous_overlay_paths=[old['remote_root']+'/overlay',*old['previous_overlay_paths']],
 source_checkpoint=ck,source_iteration=1941,source_BPTT_counts=ck['counts'],
 policy_residual_scale=.25,checkpoint_interval_seconds=300.,
 cumulative_authorized_seconds_before_this_segment=budget_upper,
 cumulative_accounting_kind='Conservative ceiling: old actual51875.415 + interruptedGOtoNextBoot upper + real recoveryeval elapsed; not invented actualGPUcost',
 interrupted_actual_elapsed_unknown=True,
 interrupted_elapsed_lower=interrupted['known_active_elapsed_lower_seconds'],
 interrupted_elapsed_upper=interrupted['interrupted_elapsed_upper_to_next_boot_seconds'],
 specific_repair='Hostreboot killed originalwindow before final; resume only surviving durableFIRST1941 all4Adam/replay/RNG. Atomic full checkpoint every300s after safe updates, original3600save+300exit unchanged.',
 previous_native_review=str(E/'ACTUAL_NATIVE_REVIEW.json'),
 previous_interruption_report=str(P/'reports/HOST_REBOOT_INTERRUPTED_WINDOW_AND_RECOVERY.json'),
 previous_recovery80=str(E/'COMPLETED.json'),state_read_fusion_enabled=False)
plan.pop('GPU_UUID',None)
assert budget_upper+3900<=plan['cumulative_limit_seconds']
A.mkdir(exist_ok=False);(A/'reports').mkdir();files=[]


def add(path,relative):
 raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))


add(CODE/'supermimic_train.py','overlay/supermimic_train.py')
binding=A/'SUPERMIMIC_BINDINGS.json';binding.write_bytes((P/'SUPERMIMIC_BINDINGS.json').read_bytes());add(binding,binding.name)
add(N/'newton_entry.py','entry.py');add(N/'newton_owner.py','owner.py')
add(N/'newton_fudan_final620_1h/run-newton.sh','run-newton.sh')
(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(A/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,shared_text=read(P/'SOURCE_PREPARED.json')['shared_text'],
 whole_tree_copies=0,checkpoint_copies=0,asset_copies=0,all_pinned_learner_source_referenced=True),indent=2),encoding='utf8')
print(json.dumps(dict(root=str(A),source=ck,files=len(files),cumulative_upper=budget_upper,recovery_eval_elapsed=eval_elapsed)))
