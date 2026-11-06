"""Read two NEW small results/meta only. No raw/replay/FK/physics; one paired draw."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
def main():
 out=D/'COLLECTION001'
 if out.exists():raise RuntimeError('E1 pair collection already consumed')
 out.mkdir(exist_ok=False);(out/'PREEXEC.json').write_text(json.dumps(dict(small_results=2,small_meta=2,raw_reads=0,models=0,physics=0,
  pair_is_one_independent_random_setting=True,no_default_adoption_from_one_pair=True),indent=2),encoding='utf-8')
 names=['v2_t01_e1_pair_baseline_520200_001','v2_t01_e1_pair_candidate_520200_001']
 results=[json.loads((D/'runs'/name/'result.json').read_text(encoding='utf-8'))for name in names]
 metas=[json.loads((D/'runs'/name/'meta.json').read_text(encoding='utf-8'))for name in names]
 a,b=results;ma,mb=metas
 maxdiff=lambda x,y:max(abs(float(u)-float(v))for u,v in zip(x,y))
 qdiff=maxdiff(ma['initial_qpos37_grading'],mb['initial_qpos37_grading'])
 kdiff=maxdiff(sum(ma['actual_controller_K_6x14'],[]),sum(mb['actual_controller_K_6x14'],[]))
 checks=dict(both_complete=all(r['complete']and r['controls']==1200 and r['physics_steps']==24000 for r in results),
  both_one_model_DR=all(r['counts']==dict(model_builds=1,FullDR_constructors=1)for r in results),
  episode_DR_receipts_exactly_equal=ma['dr_meta']==mb['dr_meta'],initial_qpos_equal=qdiff==0.,torque_LQR_K_equal=kdiff==0.,
  original_gates_equal=a['config']['protocol_id']==b['config']['protocol_id'],
  baseline_system_unchanged=a['system_changed']is False,E1_system_change_explicit=b['system_changed']is True and b['observer_changed']is True,
  torque_policy_unchanged=all(r['controller_torque_policy_unchanged']for r in results),
  same_variant_witness_valid=all(r['observer_diagnostic_valid']and r['observer_sidecar_summary']['maximum_estimate_output_difference']==0. for r in results))
 selected_keys=('pitch_abs_peak_rad','roll_abs_peak_rad','pitch_rms_rad','roll_rms_rad','slow_vx_rmse_m_s','slow_progress_m','slow_max_lateral_m','final_stop_body_vx_rms_m_s')
 rows=[]
 for name,r in zip(names,results):
  s=r['observer_sidecar_summary'];motor=r['private_motor_observation']['sections']['all']
  rows.append(dict(case=name,variant=r['observer_variant'],complete=r['complete'],case_screen_pass=r['case_screen_pass'],
   original_false_checks=[k for k,v in r['checks'].items()if v is False],scope_observed=r['new_scenario_scope_valid'],
   system_changed=r['system_changed'],controller_torque_policy_unchanged=r['controller_torque_policy_unchanged'],
   metrics={k:r['metrics'][k]for k in selected_keys},contacts=r['contact_metrics'],
   matching_variant_output_maxdiff=s['maximum_estimate_output_difference'],matching_variant_witness_not_baseline_equivalence=True,
   correction_weight=s['gravity_correction_weight'],weight_exact_zero_count=s['gravity_weight_exact_zero_count'],
   gravity_innovation=s['gravity_innovation_m_s2'],final_observer_region=r['observer_regions']['final'],
   original_DC_changed_ticks=motor['any_dc_changed_ticks'],wall_s=r['total_case_wall_s'],producer_receipts=r['producer_raw_receipts']))
 change={k:b['metrics'][k]-a['metrics'][k]for k in selected_keys}
 change.update(whole_unsupported_points=b['contact_metrics']['whole_body_unsupported_ticks']-a['contact_metrics']['whole_body_unsupported_ticks'],
  weight_mean=b['observer_sidecar_summary']['gravity_correction_weight']['mean']-a['observer_sidecar_summary']['gravity_correction_weight']['mean'])
 result=dict(status='E1_NEW_SAME_SEED_PAIR_COLLECTED_NOT_RELEASE_OR_T36',pair_checks=checks,pair_valid=all(checks.values()),
  same_initial_qpos_maxdiff=qdiff,same_torque_LQR_K_maxdiff=kdiff,independent_DR_parameter_settings=1,simulation_episodes=2,
  models=2,controls=2400,physics_steps=48000,raw_reads_or_replays_or_new_FK_or_physics_in_collection=0,
  rows=rows,E1_minus_baseline=change,episode_dr=ma['dr_meta'],
  default_runtime_modified=False,default_E1_adoption=False,old_torque_mechanisms_frozen=3,observer_candidate_count=1,observer_candidate_cap=3,
  conclusion='Only one paired setting. Retain both outcomes;E1 not selected for default just from partial improvements or witness parity.')
 (out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
