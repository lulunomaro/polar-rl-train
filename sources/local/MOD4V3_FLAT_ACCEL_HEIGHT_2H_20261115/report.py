"""Describe collected evidence without executing policies or changing weights."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import statistics

T = Path(__file__).resolve().parent
E = T / 'evidence/remote'


def read(path):
    return json.loads(path.read_bytes())


def stamp(epoch):
    return datetime.fromtimestamp(epoch, timezone(timedelta(hours=8))).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['launch', 'final'], required=True)
    args = parser.parse_args()
    plan = read(T / 'PLAN.json')
    train = E / plan['training_job']
    start = read(train / 'TRAINING_STARTED.json')
    baseline = read(E / plan['baseline_job'] / 'RESULT.json')
    first = read(train / 'FIRST_UPDATE.json')
    admission = read(E / plan['admission_job'] / 'ADMISSION.json')
    assert all(first['changes'].values()) and admission['passed']
    snapshots = []
    for folder in sorted(E.glob('eval_' + plan['training_job'] + '_*')):
        row = dict(job=folder.name)
        if (folder / 'RESULT.json').exists():
            result = read(folder / 'RESULT.json')
            cases = result['episodes']
            score = statistics.mean(r['rim_peak_m'] * r['flight_quality'] if r['sequence_complete'] and not r['failed'] else 0. for r in cases)
            row.update(status='complete', checkpoint_sha256=result['checkpoint_sha256'],
                       summary=result['summary'], recovered_level_height_score_m=score)
        elif (folder / 'ERROR.json').exists():
            row.update(status='failed', error=read(folder / 'ERROR.json'))
        else:
            row.update(status='pending')
        snapshots.append(row)
    complete = [row for row in snapshots if row['status'] == 'complete']
    best = max(complete, key=lambda r: r['recovered_level_height_score_m']) if complete else None
    report = dict(phase=args.phase, collected_at=stamp(datetime.now().timestamp()),
        training_start=stamp(start['canonical_start_epoch']), segment_start=stamp(start['epoch']),
        deadline=stamp(start['deadline_epoch']),
        training_job=plan['training_job'], source_archive_sha256=plan['source_archive_sha256'],
        parent=plan['parent'], parent_sha256=plan['parent_sha256'], parent_iteration=plan['parent_iteration'],
        admission=admission, first_update=first['changes'], baseline=baseline['summary'],
        checkpoint_evaluations=snapshots, best_evaluated_candidate=best,
        candidate_selection='mean recovered first-flight rim height times mean flight level quality over all fixed cases; failed/unrecovered cases zero',
        old_player_preserved=True, new_policy_promoted_to_player=False,
        initial_failed_attempts=['flat-accel-height-admit-r1', 'flat-accel-height-baseline-r1'],
        initial_failure='CPU spring parameter query versus CUDA state; no optimizer updates; repaired in R2')
    report['CPU_checks'] = read(T / 'evidence/OBJECTIVE_CHECK.json')
    if plan.get('repair_continuation'):
        old = E / plan['previous_training_job']
        report['previous_segment'] = dict(job=plan['previous_training_job'],
            final=read(old / 'FINAL.json'), closed=read(old / 'SAFE_CLOSED.json'),
            reason=plan['repair_reason'], strong_parent_restored_instead_of_early_child=True)
    if args.phase == 'final':
        report['final_checkpoint'] = read(train / 'FINAL.json') if (train / 'FINAL.json').exists() else None
        report['safe_closed'] = read(train / 'SAFE_CLOSED.json')
        report['training_error'] = read(train / 'ERROR.json') if (train / 'ERROR.json').exists() else None
        report['last_progress'] = read(train / 'LATEST_PROGRESS.json')
    target = T / ('LAUNCH_REPORT.md' if args.phase == 'launch' else 'FINAL_REPORT.md')
    result_path = T / ('evidence/LAUNCH_SUMMARY.json' if args.phase == 'launch' else 'evidence/FINAL_SUMMARY.json')
    result_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    baseline_lines = '\n'.join('- ' + name + ': ' + json.dumps(value) for name, value in baseline['summary'].items())
    text = f'''# Flat acceleration, level chassis and spring-assisted jump height

Phase: {args.phase}. Start: {report['training_start']}. Absolute deadline: {report['deadline']}.
One original7200s window, Host72 GPU0,2048 environments, one PPO owner. GPU1 evaluates
fixed256-case checkpoints. Initial admission and baseline precede the window;
repair and repaired-profile admission/baseline count inside the original window.
No consumed training window is replayed. Full checkpoints every300 seconds.

## Parent and behavior

Parent: {plan['parent']}
SHA256: {plan['parent_sha256']}; iteration {plan['parent_iteration']}.
Old fixed evidence: H40 nominal51/51 recovered, median wheel rim30.93cm, body rise25.06cm;
fullDR117/205. Repaired85 is the robustness reference with172/205 fullDR recoveries.
These old numbers use the old profile. The following baseline uses the new profile.
Actor, critic, STD and Adam are restored without parameter transformations.

{baseline_lines}

## Objective and physical mechanism

Level chassis and height are the main objectives. Height is measured separately as
the lower wheel rim above the ground and chassis rise from the request height.
Only the first flight collects height.20pct is incremental;80pct is paid after
stable recovery and multiplied by mean flight attitude/angular-rate quality.
The recovery gate requires maximum flight pitch<=10deg, roll<=5deg, airborne>=.16s,
both-wheel support duty>=80pct, and0.5s stable moving landing.35cm rim/25cm chassis rise
is the high-jump reporting threshold, not a cap on the continuous height reward.

Spring compression is upper physical travel stop minus actual slide coordinate.
The out-of-travel drive reference is not interpreted as available stroke.
Requests skip preparation if chassis<=.275m or both springs are compressed>=30mm.
Otherwise preparation ends on measured readiness or after.32s. Three approach height
commands(.26,.30,.36m) exercise low/preloaded and ordinary approach states.
No reward is paid for crouching or repeated takeoff events. A bounded<=2-point
spring potential-release bonus is paid once after recovered flight; it is an
energy-release estimate, not a claim of exact net mechanical work.

Original plant, motors, spring stiffness/damping and limits remain the physical
source of takeoff. No jump impulse or external scripted lift is applied.
FullDR and20pct nominal mixture remain. Physics2.5ms/TGS32/4, legs100Hz,
wheels400Hz, policy50Hz,35/78/6 interface, closure10mm and mimic.01rad per-episode reset.

## Validation and retained failures

CPU:{report['CPU_checks']['tests_run']} accounting/preload regressions passed. Native admission:{admission['num_envs']} environments,
{admission['complete_episodes']} complete episodes, console/clock/motor checks passed.
Already-low/preloaded immediate-push cases:{admission['already_low_skip_cases']}.
First update changes:{json.dumps(first['changes'])}.
R1 admission and baseline failed at the first spring calculation due to a CPU/CUDA
parameter mismatch; neither performed optimization. Original source, ERROR and
SAFE_CLOSED evidence are retained. R2 moves only immutable spring query tensors
to the environment device. R2's command-relative upper speed gate incorrectly erased
height rewards for physically stable forward launches. It was replaced in R3 by a
soft command-speed penalty with the existing2m/s task limit. The R2 segment was
saved at an update boundary, and R3 retains the original absolute deadline.
Source revisions and individual attempt IDs are preserved.

## Player and remaining work

Existing MuJoCo WASD plus one-shot Space player and single visible terrain tile are
preserved. New weights require the spring-aware phase producer and a qualified
MuJoCo replay before promotion; no new model is silently deployed to the old player.
Ongoing results:{result_path.name}. Training reward is not treated as measured height.
Reports generated later are collected and appended by the task's finalizer.
'''
    if args.phase == 'final':
        text += '\n## Final evidence\n\n' + json.dumps({k: report[k] for k in
            ('final_checkpoint', 'safe_closed', 'training_error', 'best_evaluated_candidate')}, indent=2) + '\n'
    target.write_text(text, encoding='utf8')
    print(json.dumps(dict(report=str(target), phase=args.phase, completed_evaluations=len(complete))))


if __name__ == '__main__':
    main()
