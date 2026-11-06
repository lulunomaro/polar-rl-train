"""One new validation collection, small result/meta only; no raw/model/replay."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
NAMES=['v2_t01_e1_regression_nominal_stand_520210_001','v2_t01_e1_validation_baseline_520211_001','v2_t01_e1_validation_candidate_520211_001']
def main():
 out=D/'COLLECTION001'
 if out.exists():raise RuntimeError('Validation collection already consumed')
 out.mkdir(exist_ok=False);(out/'PREEXEC.json').write_text(json.dumps(dict(maximum_new_small_results=3,maximum_new_small_meta=3,raw_reads=0,models=0,physics=0,old_QA_or_replay=0),indent=2),encoding='utf-8')
 results=[];metas=[];rows=[]
 for name in NAMES:
  folder=D/'runs'/name
  if not(folder/'result.json').is_file():
   results.append(None);metas.append(None);rows.append(dict(case=name,status='NOT_EXECUTED'if not folder.exists()else'PREFIX_WITHOUT_RESULT',not_inferred_failure=True));continue
  r=json.loads((folder/'result.json').read_text(encoding='utf-8'));m=json.loads((folder/'meta.json').read_text(encoding='utf-8'));results.append(r);metas.append(m)
  s=r['observer_sidecar_summary']
  rows.append(dict(case=name,status='EXECUTED',config=r['config'],complete=r['complete'],counts=r['counts'],controls=r['controls'],physics_steps=r['physics_steps'],wall_s=r['total_case_wall_s'],
   screen_pass=r['case_screen_pass'],false_checks=[k for k,v in r['checks'].items()if v is False],scope=r['new_scenario_scope_valid'],
   metrics=r['metrics'],contacts=r['contact_metrics'],footprint_scope=r['source_plan_private_scope'],observer_variant=r['observer_variant'],
   observer_changed=r['observer_changed'],torque_policy_unchanged=r['controller_torque_policy_unchanged'],
   matching_variant_witness_maxdiff=s['maximum_estimate_output_difference'],matching_variant_witness_not_baseline_equivalence=True,
   gravity_weight=s['gravity_correction_weight'],weight_zero_count=s['gravity_weight_exact_zero_count'],final_observer=r['observer_regions']['final'],
   DC_changed_ticks=r['private_motor_observation']['sections']['all']['any_dc_changed_ticks'],episode_DR=r['dr_meta'],producer_receipts=r['producer_raw_receipts']))
 n=results[0];nominal_ok=bool(n and n['complete']and n['case_screen_pass']and n['new_scenario_scope_valid'])
 if not nominal_ok and any(r is not None for r in results[1:]):raise RuntimeError('Declared nominal-first stop rule violated')
 comparison=None
 if results[1]is not None and results[2]is not None:
  a,b=results[1:];ma,mb=metas[1:]
  diff=lambda x,y:max(abs(float(i)-float(j))for i,j in zip(x,y))
  qdiff=diff(ma['initial_qpos37_grading'],mb['initial_qpos37_grading']);kdiff=diff(sum(ma['actual_controller_K_6x14'],[]),sum(mb['actual_controller_K_6x14'],[]))
  pair_checks=dict(episode_DR_equal=ma['dr_meta']==mb['dr_meta'],initial_qpos_maxdiff_zero=qdiff==0.,K_maxdiff_zero=kdiff==0.,
   both_complete=all(r['complete']and r['controls']==1200 and r['physics_steps']==24000 for r in(a,b)),
   system_change_explicit=a['system_changed']is False and b['system_changed']is True,
   both_same_variant_witness_zero=all(r['observer_diagnostic_valid']and r['observer_sidecar_summary']['maximum_estimate_output_difference']==0. for r in(a,b)))
  metrics=('roll_rms_rad','pitch_rms_rad','slow_vx_rmse_m_s','slow_progress_m','slow_max_lateral_m','final_stop_body_vx_rms_m_s')
  comparison=dict(checks=pair_checks,pair_valid=all(pair_checks.values()),initial_qpos_maxdiff=qdiff,K_maxdiff=kdiff,
   independent_DR_settings=1,simulation_episodes=2,E1_minus_baseline={k:b['metrics'][k]-a['metrics'][k]for k in metrics},
   whole_points=[a['contact_metrics']['whole_body_unsupported_ticks'],b['contact_metrics']['whole_body_unsupported_ticks']],
   original_screen_pass=[a['case_screen_pass'],b['case_screen_pass']],observed_scope=[a['new_scenario_scope_valid'],b['new_scenario_scope_valid']])
 result=dict(status='FROZEN_E1_REGRESSION_NEW_PAIR_VALIDATION_COLLECTED_NOT_T36',nominal_E1_original_screen_and_scope_pass=nominal_ok,
  paired_wave_status='EXECUTED'if comparison is not None else'NOT_EXECUTED_FROZEN_NOMINAL_STOP',rows=rows,pair=comparison,
  total_new_controls=sum(r['controls']for r in results if r),total_new_physics_steps=sum(r['physics_steps']for r in results if r),
  new_episode_DR_settings=1 if comparison else 0,default_E1_adopted=False,E1_formula_changed=False,old_torque_mechanisms_frozen=3,observer_candidates_consumed=1,
  raw_reads=0,old_QA_or_replay_or_new_model_FK_physics_in_collection=0)
 (out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
