"""Create compact review indexes from actual completed receipts and frozen cases."""
from pathlib import Path
import json, time, hashlib

D=Path(__file__).resolve().parent
R=D/'reports'
P=D.parent/'MOD4_D4_FULL_CONTRACT_20261008'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
v=read(P/'reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
b=v['complete_blocks']['1']
assert not v['attention'] and b['checkpoint']['finite_tensors']==88
h=b['health']
assert h['stop_reason'] is None and not h['nonfinite_observed']
assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==101664
assert h['control_steps']==25416 and b['actual_updates']==1059 and b['actual_environment_steps']==508320000
assert h['actual_task_reset_events']==h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==0
assert len(b['unique_completed_segment'])==1
segment=b['unique_completed_segment'][0]
charged=segment['ended_epoch']-segment['started_epoch']
current=v['current']
assert current and current['block']==2 and current['snapshot_count']==24
assert current['init_sha256']==b['checkpoint']['sha256']
startup=current['startup']
assert startup['predecessor_had_action_queue'] and startup['action_queue_targets_timestamps_both_RNG_restored_exact']
assert not startup['explicitly_new_D4_queue'] and startup['stale_targets_cleared']
scope=read(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json')
assert scope['decision']['limited_true_D4_baseline_functional_scope_accepted']
summary=dict(epoch=time.time(),block1=b,block1_charged_once_seconds=charged,
    own_production_source_count=243,own_snapshot_count=24,
    actual_block2=dict(epoch=v['epoch'],owner=v['actual_owner'],guardian=v['actual_guardian'],trainer=v['actual_child'],
        run=current['run'],checkpoint=current['checkpoint'],source_sha256=current['init_sha256'],
        startup=startup,live_health=current['live_health'],live_health_not_final=True,
        deadline_epoch=v['phase']['deadline_epoch']),
    original_world_dispatch_error=dict(only_D3_feedback_not_D4_physical_action=True,
        original_flags_and_results_preserved=True,production_training_correct_and_unmodified=True,
        remedy='Isolated immutable world dispatcher plus CPU-only publication of true action-delayed cases'),
    actual_D4_baseline_scope=scope['baseline27575'],actual_candidate_scope=scope['candidate28633'],
    pairs=scope['pairs'],decision=scope['decision'],
    GPU_PPO_preflight_or_budget_mutations_this_review=0,
    only_missing_frozen_world_scope_was_evaluated=True,
    old_valid_flat_spin_evidence_reused_without_repeat=True,
    canonical=v['budget'],actual_tail_adjusted_remaining_seconds=v['actual_tail_adjusted_remaining_seconds'],
    CPU_only_publisher=read(R/'WORLD_PUBLICATION_DEPLOYED.json'),
    immutable_package=read(R/'WORLD_DISPATCH_PACKAGE.json'))
(R/'D4_BLOCK1_WORLD_DISPATCH_REVIEW.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
world=scope['baseline27575']['world']['facts']
candidate=scope['candidate28633']
text=f'''# D4 first two-hour block and frozen-world dispatch review

The4090 D4 physical action-delay block naturally saved model28633 and automatically resumed block2 without waiting for3060. Its ownCPU88/243-source freeze/24 snapshots and boundPID receipt passed. It learned1059 updates/25416 controls/508320000 environment policy steps, with101664 physical callbacks exactly, zero ordinary or integrity task events, no nonfinite values and noSTOP. Closure peaked at{h['max_closure_error_m']*1000:.9f}mm. The original parent charged{charged:.9f}s exactly once; this review writes no budget.

The first actual D4-to-D4 continuation restored the saved action targets, queue timestamps and both privateCUDA RNG streams together with all earlier sensor/feedback, actor/critic/std/optimizer and global/named RNG state. It then explicitly reset a new physical episode, cleared stale targets and rebased the clock. This is not aPhysX exact resume. The block2 periodic checkpoint is only a save/health snapshot, not a skill result.

Audit found the old standalone world replay imported theD3-only DelaySensorMod4Env. Its original successful task/model/data result remains, but it is notD4 action-delay evidence. Production training and the validflat/spin replay paths correctly usedActionDelayMod4Env. The new immutable world module changes only this dispatcher and adds actual queue readback; every other source, asset and clock is byte-identical. No active training source, worker, reward or plant was changed.

The corrected3060 baseline actually completed88 environments/1500 controls/15s. Its two action groups each applied6000 physical callbacks with target error0, true0/2500/5000us assignment and exact initial/final assignment. Root/30q, parameters andD1-D3 recipe match the old baseline. Its signed world target passed{world['passed']}/{world['count']}, with worst absolute full-circle net cross{world['max_abs_cross']:.9f}m/s and along{world['along_range'][0]:.9f}–{world['along_range'][1]:.9f}m/s. The scope is same3060/seed20261002/white_v3/A0/D1D2+D3+D4, not crossGPU bit equality or dualseed/allprofile graduation.

Candidate28633 completed kinds: {', '.join(candidate)}. All completed candidate pairs preserve actual initialroot/q/parameters, recipes, delay assignments and same immutable probe source. Full three-kind candidate comparison completed={scope['decision']['candidate_all_three_complete']}. Original quality flags and all raw remain. Finite boundary residuals are diagnostics; no new mechanical success-percentage line is introduced.

The CPU-only helper supplies only the missing trueD4 world cases for each actualPASSED block. Existing validflat/spin jobs are reused. The original world jobs remainD3-only diagnostics. A subsequent controller must publish the corrected world module directly, without retaining duplicateD3-only world dispatch.4090 never waits for frozen evaluation.

D5 preparation separately reviewed the frozen nominal software spring law and an offline401-point SI curve. ActualSDK drive-force readback and hardware force-stroke measurements are still missing; noD5 executor or randomization is deployed, and nominalk/preload/damping/armature are unchanged. The software estimate is not physical calibration or300–700N certification.
'''
(R/'D4_BLOCK1_WORLD_DISPATCH_REPORT.md').write_text(text,encoding='utf8')
print(json.dumps(dict(charged_once_seconds=charged,block1_source=b['checkpoint']['sha256'],block2_resume_passed=True,scope=scope['decision'])))
