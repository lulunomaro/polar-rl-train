"""Frozen E1, no new mechanism: one fresh nominal regression then one new DR pair.
Copy tested R30 runner; only bookkeeping label/seed metadata change, no whitespace patch.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;SRC=R/'T01_ESTIMATOR_E1_PAIR_V1';D=R/'T01_ESTIMATOR_E1_VALIDATION_V1'
def main():
 if D.exists():raise RuntimeError('E1 validation prefix exists,do not regenerate')
 p=json.loads((SRC/'PROTOCOL.json').read_text(encoding='utf-8'))
 gates=dict(p['gates']);windows=dict(p['windows']);pins=list(p['frozen_small_sources'])
 text=(SRC/'run_estimator_pair_case.py').read_text(encoding='utf-8')
 for a,b in [('paired_seed=520200',"paired_seed=None if spec['nominal']else protocol['paired_DR_seed']"),
  ("status='FROZEN_NEW_OBSERVER_E1_PAIRED_CASE_SYSTEM_CHANGE_EXPLICIT_NOT_T36'", "status='FROZEN_E1_NOMINAL_REGRESSION_AND_NEW_PAIRED_TRAIN_NOT_T36'")]:
  if text.count(a)!=1:raise RuntimeError('Known bookkeeping anchor not unique:'+a)
  text=text.replace(a,b,1)
 compile(text,str(D/'run_e1_validation_case.py'),'exec')
 p.update(id='MOD4V2_HW300N60_E1_FROZEN_NOMINAL_REGRESSION_NEW_PAIRED_TRAIN_001',status='frozen_before_any_new_regression_or_DR_draw',
  scope='Unchanged E1 formula,not E2/new torque/K mechanism. New nominal E1 stand regression;new same-seed baseline/E1 TRAIN pair only if nominal passes all original gates AND observed scope.',
  paired_DR_seed=520211,formal_cases=[dict(id='e1_nominal_stand',seed=520210,nominal=True,profile='stand',observer_variant='E1'),
   dict(id='fresh_dr_baseline',seed=520211,nominal=False,profile='slow',observer_variant='baseline'),
   dict(id='fresh_dr_e1',seed=520211,nominal=False,profile='slow',observer_variant='E1')],
  execution_policy=dict(first='e1_nominal_stand',pair_only_if_nominal_original_screen_and_observed_scope_pass=True,
   on_nominal_failure='NOT_EXECUTED both DR cases;do not redraw or change formula',max_parallel_physics_workers=2,threads_per_worker=1,
   no_native_retry_or_seed_selection_or_grid=True,formula_frozen_to_original_E1=True,
   paired_DR_has_one_independent_parameter_setting=True,retain_both_results_regardless_of_pass=True,
   previous_paused_seeds_remain_unexecuted=[520184,520185,520112,520113,520114,520115],
   no_default_adoption_or_T01_T36_qualification=True))
 p['notes']=[s for s in p['notes']if '520200'not in s and 'Four DR TRAIN'not in s]+[
  'R31 adds one new nominal stand regression and one new520211 paired setting,not replay of any completedcase/check/raw.',
  'E1 formula and original innovation_limit/normgate/K/PD/gates/route unchanged;no E2 coefficient tuning or source-band widening.',
  'If nominal E1 fails originalscreen OR actual100Hzscope,do not start pairedDR. Both failing scopes remain failures.',
  'Same seed paired episodes are one independent DR setting,not N2 independent coverage;actual D3/D4 are not forced or preselected.']
 assert p['gates']==gates and p['windows']==windows and p['frozen_small_sources']==pins
 D.mkdir(exist_ok=False);runner=D/'run_e1_validation_case.py';runner.write_text(text,encoding='utf-8')
 p['frozen_small_sources'].append(dict(path=str(runner),bytes=runner.stat().st_size,sha256=hashlib.sha256(runner.read_bytes()).hexdigest()))
 (D/'PROTOCOL.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(models=0,forward=0,physics=0,old_QA_or_raw=0,E1_formula_changed=False,
  original_shared_sources_changed=False,old_gates_or_scope_widened=False,new_cases_not_yet_run=True,
  case_ids=['v2_t01_e1_regression_nominal_stand_520210_001','v2_t01_e1_validation_baseline_520211_001','v2_t01_e1_validation_candidate_520211_001']),indent=2),encoding='utf-8')
 print('FROZEN_E1_VALIDATION_READY;nominal first/conditional DRpair;0models/physics;E1unchanged')
if __name__=='__main__':main()
