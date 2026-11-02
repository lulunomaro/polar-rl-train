"""Actual423 saved facts/manifold/replay only; zeroNN/SDK/network/newphysics."""
from pathlib import Path
import json
import statistics
import time

P = Path(__file__).resolve().parent
T = P.parent
E = T / 'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102'
read = lambda path: json.loads(path.read_bytes())
returned = read(E / 'reports/ROOT423_EVALUATION_FULL_RETURNED.json')
result = returned['result']
assert not returned['wrapper_error'] and result and result['passed']
assert result['RL_residual'] and not result['online_MPC'] and result['first_episodes'] == 80
assert result['model_SHA'] == '8365d243006ef5ed6818d01298003107808f918347ad929f4ea936544f96e01a'
rows = result['results']
assert len(rows) == 80
files = {Path(row['path']).name: row['UTF8'] for row in returned['full_UTF8']}
strict = [row for row in rows if row['strict270_stable']]
clear = [row for row in rows if row['first_flight_whole_footprint_clear']]
leading = [row for row in rows if row['first_flight_both_cross']]
manifold = json.loads(files['ACTUAL423_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json'])
audits = []
for row in strict:
    env = row['env']
    run = longest = points = 0
    end = None
    topmax = 0.
    for tick in manifold['rows']:
        run = run + 1 if tick['active'][env] and tick['steady'][env] else 0
        if run > longest:
            longest = run
            end = tick['tick']
        topmax = max(topmax, min(tick['top_force_N'][env]))
    for packet in manifold['selected_solver_contact_points']:
        points += sum(len(contact['position_relative']) for contact in packet['contacts'] if contact['env'] == env)
    assert row['first_flight_whole_footprint_clear'] and not row['ground_return_after_clear'] and not row['edge_return_after_clear']
    assert longest >= 200 and row['longest_stable_seconds'] >= .5
    audits.append(dict(env=env, strict_run_ticks=longest, seconds=longest*.0025,
        interval_seconds=[(end-longest+1)*.0025, end*.0025], max_doublewheel_top_support_N=topmax,
        selected_raw_contact_points=points, actual400Hzmanifold=True, wholefootprintclear=True,
        groundedge_return=False))
control = json.loads(files['ACTUAL423_CURRENT_STATE_MPC_CONTROL_TRACE.json'])
residual = [row['learned_residual_mean_abs'] for row in control['rows']]
prior = read(P / 'reports/ANALYSIS405_ACTUAL_FINAL389_EVAL404_FACTS_AND_MANIFOLD.json')
summary = dict(epoch=time.time(), passed=True,
    scope='First actualindependent finalPPO416 evaluation after417localselfindexrefusal',
    modelSHA=result['model_SHA'], controls=result['controls'], physics=result['physics_callbacks'],
    first_episodes=80, strict=len(strict), strict_envs=[row['env'] for row in strict],
    whole_footprint_clear=len(clear), whole_clear_envs=[row['env'] for row in clear],
    leading_cross=len(leading), airborne_cases=sum(row['airborne_ever'] for row in rows),
    full8s=sum(row['full_window'] for row in rows), mean_seconds=statistics.mean(row['seconds'] for row in rows),
    median_seconds=statistics.median(row['seconds'] for row in rows), terminations=result['terminations'],
    mean_tracking_cost=statistics.mean(row['tracking_cost_mean'] for row in rows),
    mean_tracking_components={key:statistics.mean(row['tracking_components'][key] for row in rows) for key in rows[0]['tracking_components']},
    mean_learned_residual_control=statistics.mean(residual), max_learned_residual_control=max(residual),
    strict_manifold_audits=audits,
    prior389_404={key:prior[key] for key in ('strict','whole_footprint_clear','leading_cross','full8s','mean_seconds','median_seconds','terminations','mean_tracking_cost')},
    comparison_caveat='Samefixed270/newDRseed9137protocol, not exactmatchedcontacttrajectory or checkpointpairedcausalclaim',
    RL=True, online_MPC=False, autonomous_depthonly=False, model_reads=0, SDK=0, physics_steps=0, network=0,
    next='Nativecurrentmodelviewactualposes and inspect savedmotor/residual/phase toselecttargetedRLrepairorcontinuation; no unchangedbadtraining')
path = P / 'reports/ANALYSIS424_FINALPPO416_ACTUAL423_FACTS_AND_MANIFOLD.json'
with path.open('x', encoding='utf8') as stream:
    json.dump(summary, stream, indent=2, ensure_ascii=False, allow_nan=False)
print(json.dumps(summary, ensure_ascii=False), flush=True)
