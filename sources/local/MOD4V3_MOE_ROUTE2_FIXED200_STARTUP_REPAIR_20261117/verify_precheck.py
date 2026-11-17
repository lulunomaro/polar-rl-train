"""Verify the measured zero-update control/candidate comparison before authorizing PPO."""
from pathlib import Path
import json,hashlib,datetime
T=Path(__file__).resolve().parent;E=T/'evidence'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
a=load(E/'control/ROUTE2_NATIVE_PREFLIGHT.json');b=load(E/'candidate/ROUTE2_NATIVE_PREFLIGHT.json')
x=a['startup_diagnostics'];y=b['startup_diagnostics']
pop=b['offset_population_DR_then_nominal']
checks={
 'both600step_zero_update_controls':all(d['policy_steps']==600 and d['PPO_updates']==0 and d['optimizer_updates']==0 for d in [a,b]),
 'candidate_native_architecture_passed':b['passed'],
 'both_scenes_safely_closed':all(load(E/f'{q}/SAFE_CLOSED.json')['scene_closed']for q in ['control','candidate']),
 'all819_fixed20cm':b['stair_envs']==819 and b['height_population']==[819] and all(abs(v-.20)<1e-5 for v in b['actual_cooked_heights_minmax_m']),
 'all10_offset_cells_balanced':all(min(row)>0 and max(row)-min(row)<=1 for row in pop),
 'E0_action_STD_gradient_parameter_exact_zero':all(b[k]==0 for k in ['normal_action_max_error','normal_STD_max_error','normal_gradient_norm','normal_parameter_max_change']),
 'all_actor_and_critic_unchanged':b['all_actor_parameter_max_change']==0 and b['all_critic_parameter_max_change']==0,
 'history_and_previous_action_exact':b['history_queue_max_error']==0 and b['shared_previous_raw_executed_action_max_error']==0,
 'DR_startup_collapse_reduced':y['DR']['collapse_rate']<x['DR']['collapse_rate']*.5 and y['DR']['collapse_rate']<=.10,
 'nominal_startup_collapse_reduced':y['nominal']['collapse_rate']<x['nominal']['collapse_rate']*.5 and y['nominal']['collapse_rate']<=.05,
 'height_aux_capped_and_cold':y['height_aux_max_per_step']<=.005001 and y['height_aux_mean_per_E1_step']<x['height_aux_mean_per_E1_step']/20,
 'stall_negative_and_normal_reward_exact':b['maximum_stall_net_reward']<0 and b['normal_reward_max_error']==0,
 'anchor_response_increased_without_update':b['anchor_gradient_response']['parameter_updates']==0 and b['anchor_gradient_response']['gradient_multiplier']>33,
 'E1_gradients_all_finite':not b['E1_missing_gradients'] and all(v['finite']for v in b['E1_gradient_parameters'].values()),
 'formal_v1_five_startup_height_above36cm':all(r['min_height_first1s_m']>.36 for r in load(E/'V1_INITIAL_STARTUP_SUMMARY.json')['rows']),
}
protected=load(E/'PROTECTED_INPUTS.json');checks['protected_inputs_unchanged']=all(hashlib.sha256(Path(v['path']).read_bytes()).hexdigest()==v['sha256']for v in protected.values())
result=dict(generated_at=datetime.datetime.now().astimezone().isoformat(),passed=all(checks.values()),checks=checks,PPO_updates=0,optimizer_updates=0,candidate_preflight_sha256=hashlib.sha256((E/'candidate/ROUTE2_NATIVE_PREFLIGHT.json').read_bytes()).hexdigest(),control_summary={k:v for k,v in x.items()if k!='rows'},candidate_summary={k:v for k,v in y.items()if k!='rows'},offset_population_DR_then_nominal=pop,skill_graduated=False,formal_200mm_limit_unchanged=.6,original_deadline_unchanged='2026-11-17T22:30:31.928145+08:00')
(E/'COMBINED_PRECHECK_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
if not result['passed']:raise SystemExit(1)
