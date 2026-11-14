"""Report this fresh repair window from collected evidence only."""
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


def score(result):
    return statistics.mean(r['rim_peak_m'] * r['flight_quality'] if r['sequence_complete'] and not r['failed'] else 0.
                           for r in result['episodes'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['launch', 'final'], required=True)
    args = parser.parse_args()
    plan = read(T / 'PLAN.json')
    train = E / plan['training_job']
    start = read(train / 'TRAINING_STARTED.json')
    first = read(train / 'FIRST_UPDATE.json')
    assert all(first['changes'][k] for k in ('actor', 'critic', 'Adam', 'STD_in_bounds'))
    admission = read(E / plan['admission_job'] / 'ADMISSION.json')
    baseline = read(E / plan['baseline_job'] / 'RESULT.json')
    assert admission['passed'] and admission['stochastic_rollout']
    evaluations = []
    for folder in sorted(p for p in E.glob('eval_' + plan['training_job'] + '_*') if p.is_dir()):
        row = dict(job=folder.name)
        if (folder / 'RESULT.json').exists():
            result = read(folder / 'RESULT.json')
            row.update(status='complete', summary=result['summary'], checkpoint_sha256=result['checkpoint_sha256'],
                       recovered_level_height_score_m=score(result))
        elif (folder / 'ERROR.json').exists():
            row.update(status='failed', error=read(folder / 'ERROR.json'))
        else:
            row.update(status='pending')
        evaluations.append(row)
    done = [r for r in evaluations if r['status'] == 'complete']
    best = max(done, key=lambda r: r['recovered_level_height_score_m']) if done else None
    result = dict(phase=args.phase, collected_at=stamp(datetime.now().timestamp()),
        start=stamp(start['canonical_start_epoch']), deadline=stamp(start['deadline_epoch']),
        fresh_authorized_seconds=7200, training_job=plan['training_job'], parent=plan['parent'],
        parent_sha256=plan['parent_sha256'], source_archive_sha256=plan['source_archive_sha256'],
        admission=admission, baseline=baseline['summary'], baseline_score_m=score(baseline),
        first_update=first['changes'], evaluations=evaluations, best_evaluated_candidate=best,
        candidate_beats_parent=bool(best and best['recovered_level_height_score_m'] > score(baseline)),
        automatic_training_extension=False, old_player_preserved=True, policy_promoted_to_player=False)
    if args.phase == 'final':
        result.update(final=read(train / 'FINAL.json') if (train / 'FINAL.json').exists() else None,
                      closed=read(train / 'SAFE_CLOSED.json'),
                      error=read(train / 'ERROR.json') if (train / 'ERROR.json').exists() else None,
                      progress=read(train / 'LATEST_PROGRESS.json'))
    target = T / ('LAUNCH_REPORT.md' if args.phase == 'launch' else 'FINAL_REPORT.md')
    summary = T / ('evidence/LAUNCH_SUMMARY.json' if args.phase == 'launch' else 'evidence/FINAL_SUMMARY.json')
    summary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    target.write_text(f'''# Stable chassis and jump height: bounded-exploration repair

Phase:{args.phase}. Start:{result['start']}. Absolute deadline:{result['deadline']}.
This is a fresh authorized7200s window after the previous failed run closed.
Host72 only; GPU0 training2048 environments, GPU1 independent fixed256-case evaluations.
Every300s the owner atomically saves full actor/critic/STD/Adam/RNG state. No automatic extension.

## Evidence for repair

Previous task: MOD4V3_FLAT_ACCEL_HEIGHT_2H_20261115_R1.
Final SHA:3d25b60c9925e4bdf19d4863a6c370eed715d9c224db22074e405d5e4e433204.
Final nominal evaluation:2/51 takeoffs,0 landings,0 recovered jumps; all51 failed.
Training had zero settled height events throughout645 updates. Exploration STD grew
from legs.159-.210/wheels.466-.529 to legs.823-.878/wheels1.182-1.256 by110min.
The old positive entropy bonus and unconstrained STD accompanied this growth.
All23 completed checkpoint evaluations scored below the unchanged H40 parent.
The old source, weights and failures were retained and its final trial was archived.
See evidence/DIAGNOSIS.json for exact checkpoint measurements and indexed prior reports.

## Exact repair

Restore the original H40 parent:{plan['parent']}
SHA256:{plan['parent_sha256']}; iteration27382.
Verify full PPO restore first, then retain the actor MLP exactly. Set exploration STD
to legs.035/wheels.08; bound it after every update to legs[.015,.06], wheels[.03,.15].
Clear Adam state for the changed STD and reset value output head only; retain critic
hidden layers and all remaining optimizer state. Remove entropy reward, use learning
rate3e-5, PPO clip.1 and3 learning epochs. Plant, motors and spring mechanics unchanged.

Unlike the preceding deterministic-only admission, this admission samples the same
bounded stochastic policy used for training. It must produce nominal recovered jumps
in at least25pct of cases and fullDR recoveries in at least1pct before any optimization.
Measured admission:{json.dumps(admission)}
First update:{json.dumps(first['changes'])}
CPU checks:{read(T / 'evidence/OBJECTIVE_CHECK.json')['tests_run']} passed.

## Retained task and comparison

Level chassis and height remain the main objectives. Lower wheel-rim clearance and
chassis rise are recorded separately. Only the first flight earns height;20pct is
incremental,80pct is settled after0.5s stable recovery and multiplied by mean flight
attitude/angular-rate quality. Flight maxima must be pitch<=10deg, roll<=5deg;
airborne>=.16s, both-wheel support duty>=80pct. High-jump reporting:rim>=.35m and
chassis rise>=.25m; continuous height reward is uncapped.

Already-low chassis(<=.275m) or both springs compressed>=30mm skips extra crouching.
Otherwise preparation ends on readiness or after.32s. Compression itself has no reward.
Actual spring stroke is upper travel stop minus slide coordinate. A<=2-point spring
potential-release bonus is paid only on stable completion; it is not exact net work.
All six motor actions are learned. No added jump impulse or scripted leg-angle target.
Physics2.5ms/TGS32/4; legs100Hz, wheels400Hz, policy50Hz; actor35/critic78/action6;
closure10mm and mimic.01rad per-episode reset. FullDR ranges and20pct nominal mixture retained.

Fixed deterministic parent baseline:{json.dumps(baseline['summary'])}
Parent recovered-level-height score:{score(baseline):.8f}m.
Evaluation score averages recovered first-flight rim height times flight quality over
all256 cases; unsuccessful cases contribute zero. Training reward alone is not height.
The supervisor records every evaluation; two consecutive severe regressions trigger
a full-state save/close request without changing the original deadline.

Existing MuJoCo WASD and one-shot Space player with one visible tile is preserved.
New weights are not promoted before a compatible state-aware producer and MuJoCo replay.
End-of-run reports are collected and appended by the local finalizer.
''' + ('\n## First checkpoint review\n\n' + json.dumps(read(T / 'evidence/FIRST_EVAL_REVIEW.json'), indent=2) + '\n'
       if (T / 'evidence/FIRST_EVAL_REVIEW.json').exists() else '')
       + ('\n## Final evidence\n\n' + json.dumps(result, indent=2) + '\n' if args.phase == 'final' else ''), encoding='utf8')
    print(json.dumps(dict(report=str(target), phase=args.phase, completed_evaluations=len(done))))


if __name__ == '__main__':
    main()
