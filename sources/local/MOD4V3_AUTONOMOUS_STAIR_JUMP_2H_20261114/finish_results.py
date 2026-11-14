"""Summarize the completed frozen run without replaying physics or optimization."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import statistics

T = Path(__file__).resolve().parent
E = T / 'evidence/remote'
plan = json.loads((T / 'PLAN.json').read_bytes())
train = E / plan['training_job']
final = json.loads((train / 'FINAL.json').read_bytes())
progress = json.loads((train / 'LATEST_PROGRESS.json').read_bytes())
closed = json.loads((train / 'SAFE_CLOSED.json').read_bytes())
assert closed['outcome'] == 'complete'
assert not (train / 'ERROR.json').exists()
final_job = E / ('eval_' + plan['training_job'] + '_model_final')
evaluation = json.loads((final_job / 'RESULT.json').read_bytes())
assert json.loads((final_job / 'SAFE_CLOSED.json').read_bytes())['outcome'] == 'complete'
local_checkpoint = T / 'weights' / (plan['training_job'] + '__model_final.pt')
digest = hashlib.sha256(local_checkpoint.read_bytes()).hexdigest()
assert digest == final['checkpoint']['sha256'] == evaluation['checkpoint_sha256']


def grouped(rows):
    output = []
    for nominal in (False, True):
        for level in (4, 5):
            cases = [row for row in rows if row['nominal'] == nominal and row['level'] == level]
            if not cases:
                continue
            output.append(dict(nominal=nominal, height_m=cases[0]['height_m'], cases=len(cases),
                **{key: sum(bool(row[key]) for row in cases)
                   for key in ('takeoff', 'crossed', 'landed', 'success', 'failed')},
                rim_peak_median_m=statistics.median(row['rim_peak_m'] for row in cases),
                rim_peak_max_m=max(row['rim_peak_m'] for row in cases),
                continuous_air_median_s=statistics.median(row['max_air_s'] for row in cases),
                final_sensed_edge_distance_median_m=statistics.median(row['edge_distance_m'] for row in cases)))
    return output


checkpoints = []
for directory in sorted(path for path in E.glob('eval_train_remaining_r2_*') if path.is_dir()):
    row = dict(job=directory.name)
    result_path = directory / 'RESULT.json'
    error_path = directory / 'ERROR.json'
    if result_path.exists():
        result = json.loads(result_path.read_bytes())
        episodes = result['episodes']
        row.update(status='completed', cases=len(episodes), checkpoint_sha256=result['checkpoint_sha256'],
            **{key: sum(bool(case[key]) for case in episodes) for key in ('takeoff', 'crossed', 'landed', 'success')},
            groups=grouped(episodes))
    elif error_path.exists():
        row.update(status='failed_evaluation', error_path=str(error_path),
                   original_error=json.loads(error_path.read_bytes()))
    else:
        row.update(status='missing_result')
    checkpoints.append(row)
completed = [row for row in checkpoints if row['status'] == 'completed']
failed = [row for row in checkpoints if row['status'] != 'completed']
rows = evaluation['episodes']
nominal = [row for row in rows if row['nominal']]
totals = {key: sum(bool(row[key]) for row in rows) for key in ('takeoff', 'crossed', 'landed', 'success')}
task_passed = totals['success'] > 0
physics_log = (E / (plan['training_job'] + '.log')).read_text(errors='replace')
assert 'PhysX error:' not in physics_log
tz = timezone(timedelta(hours=8))
stamp = lambda value: datetime.fromtimestamp(value, tz).isoformat()
summary = dict(status='task_goal_passed' if task_passed else 'task_goal_failed',
    optimizer_completed=True, runtime_closed=True, final_checkpoint=str(local_checkpoint),
    final_checkpoint_sha256=digest, valid_updates=progress['new_updates'],
    valid_env_steps=progress['total_env_steps'], final_iteration=progress['iteration'],
    requested_window_s=7200, original_start=stamp(final['original_start_epoch']),
    valid_segment_start=stamp(json.loads((train / 'TRAINING_STARTED.json').read_bytes())['epoch']),
    absolute_deadline=stamp(final['original_deadline_epoch']), final_saved=stamp(final['epoch']),
    runtime_closed_at=stamp(closed['epoch']), final_evaluation_at=stamp(evaluation['epoch']),
    valid_segment_wall_seconds=final['elapsed_seconds'],
    window_wall_seconds=final['epoch'] - final['original_start_epoch'],
    deadline_to_final_save_seconds=final['epoch'] - final['original_deadline_epoch'],
    automatic_extension=final['automatic_extension'], final_cases=len(rows), final_totals=totals,
    final_groups=grouped(rows),
    final_nominal_rim_peak_median_m=statistics.median(row['rim_peak_m'] for row in nominal),
    final_nominal_sensed_edge_distance_median_m=statistics.median(row['edge_distance_m'] for row in nominal),
    completed_evaluations=len(completed), failed_or_missing_evaluations=len(failed),
    all_completed_target_crossings=sum(row['crossed'] for row in completed),
    all_completed_target_successes=sum(row['success'] for row in completed),
    evaluation_sampling='Same specified seed10066 cases across checkpoints; not independent pooled trials',
    initial_invalid_segment='train7200; PhysX capacity overflow; all weights rejected',
    training_counts=progress['task']['counts'], count_columns=progress['task']['columns'],
    training_count_caveat='Stochastic cumulative events; repeated takeoff rewards make takeoff events exceed episode counts',
    numerical_resets=progress['task']['done_totals'],
    promoted_step_policy=None if not task_passed else 'requires separate selection',
    repeated_takeoff_reward_bug_confirmed_in_source=True,
    reward_causality='Repeated small-hop incentive matches observations; no causal ablation run',
    original_failures_replayed=False, new_training_window_started=False,
    checkpoints=checkpoints)
(T / 'evidence/FINAL_SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
table = '\n'.join('| ' + ('nominal' if row['nominal'] else 'fullDR') +
    f" | {row['height_m'] * 100:.1f} | {row['cases']} | {row['takeoff']} | {row['crossed']} | {row['landed']} | {row['success']} |"
    for row in summary['final_groups'])
report = f'''# Autonomous Stair Jump Final Result

Task outcome: **{'PASSED' if task_passed else 'FAILED'}**. The finite optimizer run and final evaluation completed, but the final model achieved {totals['success']}/{len(rows)} stable target stair landings. No completed checkpoint had a target crossing or successful landing. The existing manual player is not promoted to a failed stair policy.

## Final Independent Evaluation

| Group | Height(cm) | Cases | Takeoff | Crossed in air | Both wheels top | Stable success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{table}

Nominal median wheel-lower-rim peak above the approach ground: {summary['final_nominal_rim_peak_median_m'] * 100:.2f}cm. This measures the lower of the two wheel rims during qualified flight, not chassis/root height. Nominal median sensed target-edge distance at episode end: {summary['final_nominal_sensed_edge_distance_median_m']:.3f}m. The outcome is consistent with small hops before the edge, not successful stair traversal.

There are {len(completed)} completed checkpoint evaluations and {len(failed)} failed/missing evaluation. Every completed evaluation used the same specified 256 cases(seed10066); do not pool checkpoints into an independent success-rate estimate. The 30-minute evaluation failed `Terrain height observation mismatch` and has no accepted RESULT. Its original ERROR and source are retained and it was not replayed.

## Timing And State

- Original window start: {summary['original_start']}.
- Valid repaired segment start: {summary['valid_segment_start']}.
- Original deadline: {summary['absolute_deadline']}.
- Final checkpoint saved: {summary['final_saved']}; runtime closed: {summary['runtime_closed_at']}.
- Final evaluation finished: {summary['final_evaluation_at']}.
- Valid segment wall time: {summary['valid_segment_wall_seconds']:.3f}s, updates: {summary['valid_updates']}, environment steps: {summary['valid_env_steps']}.
- The final rollout and complete save finished {summary['deadline_to_final_save_seconds']:.3f}s after the absolute deadline. No automatic new training window was started. Failed initial runtime and repair/admission consumed the same original 7200s window.
- Final checkpoint SHA256: `{digest}`; the downloaded checkpoint hash matches both training and independent evaluation.
- All rejected R1 source, reports and checkpoints are retained. R2 had no PhysX console error; closure resets: {summary['numerical_resets']['closure']}, mimic resets: {summary['numerical_resets']['mimic']}, numerical resets: {summary['numerical_resets']['numerical']}. These are per-environment events.

## Confirmed Reward Defect

`Outcome.update` clears `qualified` at contact and can emit `takeoff=start` again after the next qualifying flight, even though `took_off` is already true for the episode. `_get_rewards` grants 2.0 for every such event. This permits repeated small-hop rewards in one episode. Large raw takeoff event counts are therefore not independent successful jumps. The source defect and observed pre-edge hops are documented; no causal reward-ablation experiment is claimed.

Even the 4cm warmup only accumulated 19 crossing events and 17 first dual-wheel top contacts, with zero 0.5s stable successes. Other training heights had no crossings. Time-based difficulty promotion continued despite that lack of mastery. This run did not learn the requested skill.

The next version needs an episode-bounded or removed takeoff bonus, useful forward clearance/edge-progress signals and a curriculum tied to actual task mastery. Those changes are not applied to this frozen run, and this report does not launch a new budget. Original plant, motors, timing, DR contracts, one-tile player and one-shot Space interface remain as archived at launch.

Full per-case evaluations, failed evaluation, raw logs and artifact hashes accompany `evidence/FINAL_SUMMARY.json` and `evidence/ARTIFACTS_FINAL.json`. Training and evaluation are complete; both GPUs were free at the final read-only status check.
'''
(T / 'FINAL_REPORT.md').write_text(report, encoding='utf8')
print(json.dumps({key: summary[key] for key in ('status', 'final_saved', 'final_evaluation_at',
    'valid_updates', 'valid_env_steps', 'completed_evaluations', 'failed_or_missing_evaluations',
    'final_totals', 'final_nominal_rim_peak_median_m')}, indent=2))
