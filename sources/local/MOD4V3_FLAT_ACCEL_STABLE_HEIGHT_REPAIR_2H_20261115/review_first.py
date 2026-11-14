"""Compare the first fixed checkpoint evaluation with the retained parent."""
import json
from pathlib import Path
import statistics
import time

T = Path(__file__).resolve().parent
E = T / 'evidence/remote'
plan = json.loads((T / 'PLAN.json').read_bytes())
job = 'eval_' + plan['training_job'] + '_model_005m'


def read(path):
    return json.loads(path.read_bytes())


def score(result):
    return statistics.mean(r['rim_peak_m'] * r['flight_quality']
                           if r['sequence_complete'] and not r['failed'] else 0. for r in result['episodes'])


parent = read(E / plan['baseline_job'] / 'RESULT.json')
child = read(E / job / 'RESULT.json')
progress = read(E / plan['training_job'] / 'LATEST_PROGRESS.json')
groups = {}
for nominal in (False, True):
    rows = [r for r in child['episodes'] if r['nominal'] == nominal]
    group = 'nominal' if nominal else 'fullDR'
    recovered = [r for r in rows if r['sequence_complete'] and not r['failed']]
    groups[group] = dict(cases=len(rows),
        takeoff=sum(r['takeoff'] for r in rows), landed=sum(r['landed'] for r in rows),
        recovered=len(recovered), high_jump=sum(r['success'] for r in rows),
        median_rim_m=statistics.median(r['rim_peak_m'] for r in rows),
        recovered_median_rim_m=statistics.median(r['rim_peak_m'] for r in recovered) if recovered else None,
        recovered_median_pitch_deg=statistics.median(r['air_pitch_rad'] * 180 / 3.141592653589793 for r in recovered) if recovered else None,
        recovered_median_roll_deg=statistics.median(r['air_roll_rad'] * 180 / 3.141592653589793 for r in recovered) if recovered else None,
        failed=sum(r['failed'] for r in rows),
        terminal_gate_counts=dict(no_request=sum(not r['requested'] for r in rows),
            motion_invalid=sum(r['takeoff'] and not r['motion_valid'] for r in rows),
            flight_pitch_over10deg=sum(r['air_pitch_rad'] > .1745329252 for r in rows),
            flight_roll_over5deg=sum(r['air_roll_rad'] > .0872664626 for r in rows),
            overspeed=sum(r['overspeed'] for r in rows), boundary=sum(r['boundary'] for r in rows),
            push_timeout=sum(r['push_timeout'] for r in rows)))
result = dict(attempt_id='stable-height-repair-first5min-review-01', epoch=time.time(),
    checkpoint_sha256=child['checkpoint_sha256'], checkpoint_job=job,
    parent_sha256=parent['checkpoint_sha256'], parent_summary=parent['summary'],
    candidate_groups=groups, parent_score_m=score(parent), candidate_score_m=score(child),
    score_ratio_to_parent=score(child) / max(score(parent), 1e-9),
    training_updates=progress['new_updates'], training_recovered_counts=progress['task']['counts']['sequence_complete'],
    exploration_STD=progress['exploration_STD'],
    recovered_events_exist=all(v > 0 for v in progress['task']['counts']['sequence_complete']),
    policy_promoted_to_player=False,
    interpretation='Fixed independent first5min comparison, not a claim of the final two-hour result; gate counts overlap')
(T / 'evidence/FIRST_EVAL_REVIEW.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
print(json.dumps(result, indent=2))
