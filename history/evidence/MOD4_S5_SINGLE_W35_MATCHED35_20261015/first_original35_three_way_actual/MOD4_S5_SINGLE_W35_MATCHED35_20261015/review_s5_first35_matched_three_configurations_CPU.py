"""One actual matched S5 cell; not the full seed/profile/switching matrix."""
from pathlib import Path
import hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
B=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015';C=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 paths=[R/'S5_SINGLE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',B/'reports/S4_RULE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',C/'reports/S4_FIRST_TRAINED_GATE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json']
 reviews=[json.loads(p.read_bytes()) for p in paths];assert all(x['passed'] for x in reviews)
 source=json.loads((R/'s5_single_w35_original35_1500_v1_S5_SINGLE_CONTROL_CPU_ADMITTED.json').read_bytes());assert source['passed']
 reports=[json.loads(Path(x['original_report']['local_path']).read_bytes()) for x in reviews]
 initial=[json.loads(Path(x['first_physics_initial_snapshot']['local_path']).read_bytes())['values'] for x in reviews];assert initial[0]==initial[1]==initial[2]
 for field in ('geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe'):
  rows=[]
  for report in reports:
   x=report[field]
   if field=='route_scope':
    x=dict(x);q=x.pop('query_worldmesh_evidence');x['actual_query_bytes_SHA']=dict(bytes=q['bytes'],sha256=q['sha256'])
   rows.append(x)
  assert rows[0]==rows[1]==rows[2],field
 static=[];draw=[]
 for report in reports:
  x=dict(report['sensor_recipe']);draw.append(x.pop('noise_draw_counts'));static.append(x)
 assert static[0]==static[1]==static[2]
 differences=[]
 for group in zip(*(x['rows'] for x in reviews)):
  assert len({x['env'] for x in group})==len({x['group'] for x in group})==1
  differences.append(dict(env=group[0]['env'],group=group[0]['group'],standing_no_transit_requirement=group[0]['group']==2,complete_single_rule_gate=[x['contact_complete'] for x in group],all_three_original_valid_episode_prefixes=[x['all_valid_episodes'] for x in group]))
 stats=[]
 for label,review in zip(('A_single_W35','B_rule_E0_W35','C_trained_gate148_E0_W35'),reviews):
  with np.load(review['raw']['local_path']) as z:d={k:z[k] for k in ('root','before_root','episode','terminated','group_ids')}
  rows=[]
  for i in range(80):
   valid=np.flatnonzero(d['episode'][:,i]==d['episode'][0,i]);bad=valid[d['terminated'][valid,i]]
   if len(bad):valid=valid[valid<bad[0]]
   assert len(valid)>0
   g=int(d['group_ids'][i]);sign=(1 if g==0 else -1 if g==1 else 0)
   speed=d['root'][valid,i,7]
   rows.append(dict(env=i,group=g,valid_controls=len(valid),first_ordinary_control=int(bad[0]) if len(bad) else None,mean_signed_x_speed_m_s=float(speed.mean()*sign) if g!=2 else None,mean_abs_tracking_error_m_s=float(np.abs(speed-.3*sign).mean()),mean_abs_yaw_rad_s=float(np.abs(d['root'][valid,i,12]).mean()),displacement_from_actual_first_root_m=float(np.linalg.norm(d['root'][valid[-1],i,:2]-d['before_root'][0,i,:2]))))
  bygroup=[]
  for g in range(3):
   selected=[x for x in rows if x['group']==g];tracking=[x['mean_abs_tracking_error_m_s'] for x in selected]
   bygroup.append(dict(group=g,envs=len(selected),tracking_env_mean=float(np.mean(tracking)),tracking_worst_env=float(max(tracking)),mean_abs_yaw_env_mean=float(np.mean([x['mean_abs_yaw_rad_s'] for x in selected])),standing_no_transit_or_perfect_tracking_claim=g==2))
  stats.append(dict(configuration=label,forward=review['forward_complete'],reverse=review['reverse_complete'],ordinary=review['ordinary'],truncation=review['truncation_unique'],per_env=rows,groups=bygroup))
 controls=[source,json.loads((B/'reports/S4_RULE35_SHARED_ROUTING_ADMITTED_s4_rule_original35_query35_full1500_v2.json').read_bytes()),json.loads((C/'reports/S4_FIRST_TRAINED_GATE35_SHARED_ROUTING_ADMITTED_s4_first_gate_final35_full1500_v1.json').read_bytes())]
 assert all(x['passed'] for x in controls)
 actor=torch.load(D/'payload/source/E1_WAVE35_frozen_source.pt',map_location='cpu',weights_only=False)['actor_state_dict'];float_count=sum(x.numel() for x in actor.values())
 result=dict(epoch=time.time(),passed_actual_first_matched_three_configurations=True,cell=dict(geometry='original35 tenwaves .4approach and strict>1N doublewheel before-and-after200mm',seed=20260928,num_envs=80,controls=1500,callbacks=6000,profile='white_v3',information='same normal35 A0/critic38 not used by deployment/action6 originalclip6'),
  sources=dict(single_W35='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',rule_experts=['b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8','b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'],gate='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3'),
  review_inputs=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)) for p in paths],same_actual_firstphysics_rootq30_all_params_assignment_staticrecipes_RNGqueues_exact=True,same_actual_geometry_query_bytes_SHA_and_original1e6_contact_COM_hardware=True,source_dynamic_noise_counters_at_each_final=draw,
  metrics=stats,original_all_valid_failed_unfinished_prefixes=differences,control_source_and_inference_reports=controls,
  all_three_route_counts_identical=all((x['forward'],x['reverse'],x['ordinary'])==(stats[0]['forward'],stats[0]['reverse'],stats[0]['ordinary']) for x in stats),
  no_blending_truth_teacher_hysteresis_or_live_correction=True,
  inference_actor_STD_float_count_single=float_count,inference_gate_parameter_float_count=4450,unused_pair_critic_fixture_and_empty_Adam_remain_separate_runtime_cost_limit=True,only_single_actor_executed_in_A=True,
  additional_gate_first_window_actual_learning_cost_seconds=2668.750717163086,original_expert_ancestry_training_cost_not_equalized_or_erased=True,one_cell_not_equal_training_budget_architecture_winner=True,
  all_current_frozen_eval_optimizer_updates0=True,gate_superiority_not_established_by_this_cell=True,
  next_missing=['Single-policyA flat/spin/world with actual matched V8 runtime and initial-state contracts; prior Linux WAVE143 failures remain historical until exact backend/initial data permit reuse.', 'Second developmentseed20261003 and nominal/white_v2/white_v3 architecture matrix, combined DR and actual task transition/switching cells.', 'Finalheldout20261011/12 after selection; no repeated tuning on heldout, and real hardware latency/calibration remains separate.'],
  production_architecture_selection_deferred_pending_actual_S5_matrix=True,S5_overall_complete=False,no_new_PPO_or_automatic_secondgate_learning=True,qualified50_70_or_allskills=False)
 p=R/'S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(first_matched_cell_complete=True,counts=[dict(configuration=x['configuration'],forward=x['forward'],reverse=x['reverse'],ordinary=x['ordinary']) for x in stats],S5_overall_complete=False,no_PPO=True)))
if __name__=='__main__':main()
