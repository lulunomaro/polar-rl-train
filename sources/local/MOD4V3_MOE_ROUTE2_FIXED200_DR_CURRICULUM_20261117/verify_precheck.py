"""Verify the final zeroDR curriculum probe and keep all prior failed evidence intact."""
from pathlib import Path
import json,hashlib,datetime,torch
T=Path(__file__).resolve().parent;E=T/'evidence'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
old=T.parent/'MOD4V3_MOE_ROUTE2_FIXED200_STARTUP_REPAIR_20261117'
a=load(old/'evidence/control/ROUTE2_NATIVE_PREFLIGHT.json');path=E/'zeroDR_curriculum_probe_r3_cache/ROUTE2_NATIVE_PREFLIGHT.json';b=load(path);x=a['startup_diagnostics'];y=b['startup_diagnostics']
ck=torch.load(T/'weights/model_step000.pt',map_location='cpu',weights_only=False);ref=torch.load(T/'c874_reference.pt',map_location='cpu',weights_only=False)
isolation={}
for stream in ['actor','critic']:
 isolation[stream]=max(float((v-ck[stream+'_state_dict']['mlp.e0.'+k.removeprefix('mlp.')]).abs().max())for k,v in ref[stream+'_state_dict'].items()if k.startswith('mlp.'))
isolation['STD']=float((ref['actor_state_dict']['distribution.std_param']-ck['actor_state_dict']['distribution.e0_std']).abs().max())
checks=dict(
 native600_zero_updates=b['policy_steps']==600 and b['PPO_updates']==0 and b['optimizer_updates']==0,
 native_architecture_passed=b['passed'],scene_safely_closed=load(E/'zeroDR_curriculum_probe_r3_cache/SAFE_CLOSED.json')['scene_closed'],
 all819_fixed20cm=b['stair_envs']==819 and b['height_population']==[819] and all(abs(v-.2)<1e-5 for v in b['actual_cooked_heights_minmax_m']),
 true_zeroDR_seed=b['E1_DR_level']==0 and b['E1_DR_curriculum']['actual_fullDR_population']==0 and b['E1_DR_curriculum']['zeroDR_population']==819,
 center_seed_is_honestly_labelled=all(v==0 for v in b['actual_physical_seed_offsets_mm']),
 planned_five_offset_coverage_balanced=all(min(r)>0 and max(r)-min(r)<=1 for r in b['offset_population_DR_then_nominal']),
 true_c874_E0_actor_STD_critic_exact=all(v==0 for v in isolation.values()),
 E0_gradient_and_parameter_zero=b['normal_gradient_norm']==0 and b['normal_parameter_max_change']==0,
 entire_network_no_optimizer_update=b['all_actor_parameter_max_change']==0 and b['all_critic_parameter_max_change']==0,
 history_and_previous_action_exact=b['history_queue_max_error']==0 and b['shared_previous_raw_executed_action_max_error']==0,
 startup_collapse_rates_more_than_halved=all(y[g]['collapse_rate']<x[g]['collapse_rate']*.5 for g in ['DR','nominal']),
 startup_median_height_recovered=all(y[g]['median_minimum_height_m']>.36 for g in ['DR','nominal']),
 height_aux_no_explosion=y['height_aux_max_per_step']<=.005001 and y['height_aux_mean_per_E1_step']<x['height_aux_mean_per_E1_step']/20,
 stall_negative_normal_reward_exact=b['maximum_stall_net_reward']<0 and b['normal_reward_max_error']==0,
 reset_cache_nonreset_rows_exact_zero=b['reset_sensor_cache']['nonreset_rows_max_change']==0,
 finite_trainable_E1_gradients=not b['E1_missing_gradients'] and all(v['finite']for v in b['E1_gradient_parameters'].values()),
 local_DR_gate_test_passed=load(E/'DR_MIXTURE_LOCAL_CHECKS.json')['passed'])
protected=load(E/'PROTECTED_INPUTS.json');checks['protected_inputs_unchanged']=all(hashlib.sha256(Path(v['path']).read_bytes()).hexdigest()==v['sha256']for v in protected.values())
result=dict(generated_at=datetime.datetime.now().astimezone().isoformat(),passed=all(checks.values()),checks=checks,PPO_updates=0,optimizer_updates=0,candidate_preflight_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),E0_reference_parameter_errors=isolation,control_summary={k:v for k,v in x.items()if k!='rows'},candidate_summary={k:v for k,v in y.items()if k!='rows'},E1_DR_curriculum=b['E1_DR_curriculum'],reset_sensor_cache=b['reset_sensor_cache'],formal_200mm_limit_unchanged=.6,skill_graduated=False,zeroDR_success_is_not_fullDR_graduation=True,training_not_started=True)
(E/'COMBINED_PRECHECK_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if not result['passed']:raise SystemExit(1)
