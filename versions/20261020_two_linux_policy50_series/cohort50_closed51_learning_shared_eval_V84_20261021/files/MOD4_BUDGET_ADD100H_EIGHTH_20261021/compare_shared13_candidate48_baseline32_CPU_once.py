from pathlib import Path
import json,time
B=Path(__file__).resolve().parent;R=B/'reports'
a=json.loads((R/'SHARED_H1_FULL13_ALL_ROWS_AND_FIRST_EPISODE_CPU_ACTUAL.json').read_bytes());b=json.loads((R/'SHARED_H1_BASELINE32_FULL13_V6_ALL_ROWS_AND_FIRST_EPISODE_CPU_ACTUAL.json').read_bytes())
assert a['passed_diagnostic_execution_and_all_row_CPU'] and b['passed_diagnostic_execution_and_all_row_CPU'] and b['candidate_baseline_initial_state_bitwise_exact']
assert a['controls']==b['controls']==750 and a['callbacks']==b['callbacks']==6000 and a['source_SHA']!=b['source_SHA']
rows=[dict(recipe=x['recipe'],candidate_first_episode_stable_credit=x['source_stable_credit_in_first_episode'],baseline_first_episode_stable_credit=y['source_stable_credit_in_first_episode'],candidate_resets=x['total_resets'],baseline_resets=y['total_resets'],candidate_first_failure=x['first_failure_sim_seconds'],baseline_first_failure=y['first_failure_sim_seconds']) for x,y in zip(a['cases'],b['cases']) if x['public_request'] and x['recipe']==y['recipe']]
assert len(rows)==12
q=dict(epoch=time.time(),same_runtime_seed_and_initial_state=True,candidate_SHA=a['source_SHA'],baseline_SHA=b['source_SHA'],candidate_source_stable_credits=a['first_episode_source_stable_recoveries'],baseline_source_stable_credits=b['first_episode_source_stable_recoveries'],cases=rows,scope='Fresh13 original poses diagnostic only; not original104 graduation or general skill regression proof',no_jump_height_claim=True,no_reward_change_or_automatic_GPU_training_replay=True)
(R/'MATCHED_E3_CANDIDATE48_BASELINE32_DIAGNOSTIC_COMPARISON_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(q,indent=2));print(json.dumps(q))
