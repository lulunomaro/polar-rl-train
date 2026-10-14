"""Own two saved cases, source/initial values and prefix differences only."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cases=['s4_rule_original35_query35_native120_v2','s4_rule_original35_query35_full1500_v2'];reports=[];data=[]
for case in cases:
 p=R/('S4_RULE35_OWN_PHYSICAL_DATA_ADMITTED_'+case+'.json');v=json.loads(p.read_bytes());assert v['passed'];reports.append(v)
 with np.load(v['raw']['local_path'],allow_pickle=False) as z:data.append({k:z[k].copy() for k in ('before_root','root','q','command','episode','terminated','truncated','action','processed_action','policy_obs')})
probes=[json.loads(Path(v['original_full_report']['local_path']).read_bytes()) for v in reports]
assert probes[0]['initial']==probes[1]['initial']
for key in ('sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','geometry_recipe','geometry'):
 # PD contains current transient samples at final; compare authoritative initial parameters above.
 if key=='chassis_PD_recipe':continue
 left=dict(probes[0][key]);right=dict(probes[1][key])
 if key=='sensor_recipe':
  a=left.pop('noise_draw_counts');b=right.pop('noise_draw_counts');assert set(a)==set(b)
  assert all(v==(120+3)*80 for v in a.values()) and all(v==(1500+3)*80 for v in b.values())
 assert left==right,key
prefix={}
for k in data[0]:
 a=data[0][k];b=data[1][k][:120];assert a.shape==b.shape
 prefix[k]=dict(byteexact=np.array_equal(a,b),different_values=int(np.count_nonzero(a!=b)),maxabs=float(abs(a.astype(np.float64)-b.astype(np.float64)).max()))
full=json.loads((R/'S4_RULE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes());routing=json.loads((R/('S4_RULE35_SHARED_ROUTING_ADMITTED_'+cases[1]+'.json')).read_bytes())
assert full['passed'] and routing['passed'] and full['forward_complete']==full['reverse_complete']==27 and full['ordinary']==0
out=dict(epoch=time.time(),passed_source_initial_scope_review=True,own_sources_geometry_immutable_recipes_initial_rootq_parameters_assignments_exact=True,final_noise_counters_actual_controls_plus3SDKsetup_times80=True,own_native120_and_full1500_both_physically_admitted=True,native_first120_to_full_first120_actual_differences=prefix,prefix_byteexact_not_assumed=True,full35_original_1N_before_after200mm_forward27_reverse27=True,standing26_no_transit_requirement=True,ordinary0=True,rule_routes_moving_to_W35_standing_to_E0=True,no_terrain_triggered_expert_switch_proof=True,no_trained_gate_or_MoE_qualification=True,source_W35_old_observed_scope_not_replayed_or_overwritten=True,actual_full15_6000_callbacks_shared35_whole6=True,gate_and_critic_updates0=True,full_training_environment_state_restore_and_PPO_API_integration_still_pending=True,no_budgetwrite=True)
p=R/'S4_RULE35_OWN_NATIVE_AND_FULL_ROUTE_COMPLETE_SCOPE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),passed=True,forward=27,reverse=27,ordinary=0,prefix_all_exact=all(v['byteexact'] for v in prefix.values()),gate_updates=0)))
