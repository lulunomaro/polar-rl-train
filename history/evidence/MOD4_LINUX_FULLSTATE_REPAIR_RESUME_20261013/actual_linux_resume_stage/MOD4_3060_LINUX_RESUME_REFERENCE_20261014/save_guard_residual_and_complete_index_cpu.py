"""Append exact CAD residual conclusion and all newly saved file index; no GPU."""
from pathlib import Path
import json,hashlib,time
P=Path(__file__).resolve().parent;R=P/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=R/'REFERENCE17B_PAIRED91D_ALL_FAILURE_PREFIX_CPU_ACTUAL_REVIEW.json'
j=json.loads(source.read_bytes());rows=j['per_env'][:7]
assert all(r['actor_clip6_fraction_old_new'][0][0]==1. for r in rows)
assert all(r['actor_clip6_fraction_old_new'][1][0]==0. for r in rows)
left=[r['leg_difference_guard_lower_fraction_old_new'][1][0] for r in rows]
right=[r['leg_difference_guard_lower_fraction_old_new'][1][1] for r in rows]
q=R/'REFERENCE17B_ACTUAL_CAD_GUARD_RESIDUAL_CPU_SUPPLEMENT.json';assert not q.exists()
report=dict(epoch=time.time(),actual_saved_raw_only=True,source_report=dict(path=str(source),sha256=H(source)),
            raw_actor_clip6_left_old_fraction=1.,raw_actor_clip6_left_new_fraction=0.,
            current_left_CAD_crank_minus_hip_lower_guard_fraction_per_moving_env=left,
            current_right_CAD_crank_minus_hip_lower_guard_fraction_per_moving_env=right,
            current_left_range=[min(left),max(left)],current_right_range=[min(right),max(right)],
            original_CAD_window_min_rad=-1.0843,original_CAD_window_max_rad=.85,
            exact_source_formula_evidence='mod4_task.DelayedJointPositionAction.process_actions clamps pa0 to pa1+diff_min..diff_max and pa2 to pa3+same bounds',
            conclusion='Raw6 saturation disappeared, but effective processed left leg difference remains at the lower mechanical guard for92.87–98.40% of these valid moving controls. This is a remaining observed action-domain asymmetry, not proof of the sole failure cause or an accepted repair.',
            passability_old2_of7_new0_of7=True,original_physical_thresholds_not_changed=True,
            no_new_GPU_or_model_modification=True,not_single_initializer_causal_ablation=True)
q.write_text(json.dumps(report,indent=2),encoding='utf8')
files=[]
for p in sorted(P.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    large=p.suffix.lower() in ('.pt','.npz','.usd','.zip') or p.stat().st_size>2_000_000
    files.append(dict(path=str(p.resolve()),relative=p.relative_to(P).as_posix(),bytes=p.stat().st_size,
                      sha256=H(p),archive_disposition='actual_large_original_path_size_SHA_only' if large else 'full_saved_source_or_report_for_Git'))
index=R/'REFERENCE17B_ALL_SAVED_SOURCE_REPORT_RAW_ACTUAL_INDEX.json';assert not index.exists()
index.write_text(json.dumps(dict(epoch=time.time(),stage='3060_latest17b_frozen_samefixture_complete_failure_preserved',
                                saved_files=files,all_failed_preconnection_and_guard_rejections_preserved=True,
                                original_case_and_tasks_unchanged=True,no_more_GPU_granted_or_launched=True,
                                completed_parent_child_actual_exit_and_shared_lockfree=True,
                                only249_no210_PPO_or_budgetwrite=True,Git_by_root_pending=True),indent=2),encoding='utf8')
print(json.dumps(dict(guard_report=str(q),guard_SHA=H(q),index=str(index),index_SHA=H(index),files=len(files),Git_claimed=False)))
