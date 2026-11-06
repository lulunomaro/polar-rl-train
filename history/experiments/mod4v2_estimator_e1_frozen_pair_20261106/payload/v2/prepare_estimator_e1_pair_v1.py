"""Freeze ONE newly seeded same-condition baseline/E1 pair, not old-case replay.
Observer E1 changes feedback; torque policy/K/PD/actuation and old torque3of3 frozen.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;SRC=R/'T01_OBSERVER_AUDIT_V1';D=R/'T01_ESTIMATOR_E1_PAIR_V1'
def main():
 if D.exists():raise RuntimeError('E1 pair already frozen')
 check=json.loads((R/'ESTIMATOR_CAUCHY_E1_V1/check001/RESULT.json').read_text(encoding='utf-8'))
 if not check['passed']or check['same_E1_witness_maxdiff']!=0.:raise RuntimeError('E1 new software check failed')
 proto=json.loads((SRC/'PROTOCOL.json').read_text(encoding='utf-8'));gates=proto['gates'].copy();windows=proto['windows'].copy()
 baseproto=json.loads((R/'T01_NOMINAL_BAND_TRAIN_V1/PROTOCOL.json').read_text(encoding='utf-8'))
 proto.update(id='MOD4V2_HW300N60_OBSERVER_E1_FROZEN_PAIRED_TRAIN_001',status='frozen_before_two_new_same_seed_episodes',
  scope='First observer-module repair E1: one Cauchy innovation multiplier. Old torqueM1..M3 remain frozen;not a 4th torque/K candidate. E1 changes system feedback,baseline does not.',
  formal_cases=[dict(id='new_pair_baseline',seed=520200,nominal=False,profile='slow',observer_variant='baseline'),
   dict(id='new_pair_e1',seed=520200,nominal=False,profile='slow',observer_variant='E1')],
  diagnostic_only=False,training_only=True,controller_unchanged_from_M0=False,controller_torque_policy_unchanged=True,
  observer_candidate_index=1,observer_candidate_limit=3,old_torque_mechanisms_frozen_count=3,
  execution_policy=dict(exactly_one_new_pair=True,max_parallel_physics_workers=2,threads_per_worker=1,
   no_retry_or_seed_selection_or_parameter_grid=True,old_paused_seeds_stay_paused=[520184,520185,520112,520113,520114,520115],
   pair_has_one_independent_episode_parameter_draw_replicated_for_comparison=True,
   both_results_retained_regardless_of_pass=True,not_T36_or_reliability=True))
 proto['notes']=baseproto['notes']+[
  'Same new520200 seed in two fresh models/FullDR constructors;paired comparison is not two independent random samples,oldcases never replayed.',
  'E1 is actor feedback change. Same-variant witness0 is not baseline-E1 equivalence. Controller torque policy/K/shaper/PD/D4/DC/scene/gates fixed.',
  'Existing innovation_limit reused,only hard linear innovation multiplier replaced by bounded Cauchy. Norm gate and accel_correction1.5 retained.',
  'No residual mean subtraction/root teacher/episode parameter inversion/forced D3/draw selection/score-window changes.',
  'A paired result may worsen or still fail and does not prove gravity gate was unique cause;all outcomes retained.']
 pins={p['path']:p for p in proto['frozen_small_sources']}
 path=R/'estimator_cauchy_e1.py';pins[str(path)]=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 proto['frozen_small_sources']=list(pins.values());text=(SRC/'run_observer_audit_case.py').read_text(encoding='utf-8')
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise RuntimeError('E1 pair source anchor not unique:'+a)
  text=text.replace(a,b,1)
 one("    dump(out/'config.json', cfg)","    cfg.update(observer_variant=spec['observer_variant'],system_changed=spec['observer_variant']!='baseline',paired_seed=520200)\n    dump(out/'config.json', cfg)")
 one("        import runtime_v2 as runtime","        import runtime_v2 as runtime\n        from estimator_cauchy_e1 import CauchyEstimatorE1,MatchingE1Sidecar\n        variant=spec['observer_variant']\n        if variant not in('baseline','E1'):raise ValueError('Unknown observer variant')\n        original_estimator=runtime.StateEstimator")
 one("                 meta['original_default_M0_controller_unchanged']=True","                 meta['original_default_M0_controller_unchanged']=variant=='baseline'\n                 meta.update(observer_variant=variant,observer_changed=variant!='baseline',system_changed=variant!='baseline',controller_torque_policy_unchanged=True)")
 one("        t = time.perf_counter()\n        print('T01_FORMAL_BUILD '","        runtime.StateEstimator=CauchyEstimatorE1 if variant=='E1'else original_estimator\n        t = time.perf_counter()\n        print('T01_FORMAL_BUILD '")
 one("            timing['engine_setup_wall_s'] = time.perf_counter()-t","            runtime.StateEstimator=original_estimator\n            timing['engine_setup_wall_s'] = time.perf_counter()-t")
 one('        sidecar=ObserverSidecar(engine.estimator);sidecar.attach(engine.estimator)',
  "        sidecar=(MatchingE1Sidecar if variant=='E1'else ObserverSidecar)(engine.estimator);sidecar.attach(engine.estimator)")
 one("status='ONE_NEW_OBSERVER_ONLY_DR_DIAGNOSTIC_UNCHANGED_M0_NOT_WAVE2_OR_T36'",
  "status='FROZEN_NEW_OBSERVER_E1_PAIRED_CASE_SYSTEM_CHANGE_EXPLICIT_NOT_T36'")
 one('controller_changed=False,previous_three_mechanisms_frozen=True,robust_corridor_certified=False,',
  "controller_changed=variant!='baseline',observer_changed=variant!='baseline',system_changed=variant!='baseline',\n            controller_torque_policy_unchanged=True,observer_variant=variant,same_variant_witness_is_not_baseline_equivalence=True,\n            previous_three_mechanisms_frozen=True,robust_corridor_certified=False,")
 assert proto['gates']==gates and proto['windows']==windows
 compile(text,str(D/'run_estimator_pair_case.py'),'exec')
 D.mkdir(exist_ok=False);(D/'run_estimator_pair_case.py').write_text(text,encoding='utf-8')
 (D/'PROTOCOL.json').write_text(json.dumps(proto,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(models=0,forward=0,physics=0,old_QA_or_raw=0,
  proposed_case_ids=['v2_t01_e1_pair_baseline_520200_001','v2_t01_e1_pair_candidate_520200_001'],
  observer_changes_system=True,old_torque3of3_unchanged=True,old_gates_unchanged=True,new_seed_not_yet_sampled=True),indent=2),encoding='utf-8')
 print('E1_PAIR_FROZEN baseline/E1 sameNEW520200; twofreshmodels,onepairedrandomsetting;feedbackchangeexplicit;no model/physics')
if __name__=='__main__':main()
