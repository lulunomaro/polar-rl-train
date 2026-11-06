"""One nominal-only M0 experiment. R26 robust corridor remains FAILED.
Reuses unexecuted R26 preparer via exact literals, adds explicit non-certificate.
"""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;D=R/'T01_NOMINAL_BAND_M0_V1'
def main():
 proof=json.loads((R/'PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/RESULT.json').read_text(encoding='utf-8'))
 if proof['status']!='PUBLIC_NOMINAL_BAND_EXPERIMENT_NOT_ROBUST_CORRIDOR'or proof['robust_corridor_certified']is not False:raise ValueError('No nominal-only contract')
 if D.exists():raise RuntimeError('Nominal experiment prefix consumed')
 src=R/'prepare_uniform_corridor_case_once.py';tree=ast.parse(src.read_text(encoding='utf-8'))
 mapping={
  'T01_UNIFORM_CORRIDOR_V1':'T01_NOMINAL_BAND_M0_V1',
  'PUBLIC_UNIFORM_CORRIDOR_V1/PLAN.json':'PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/PLAN.json',
  'PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json':'PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/RESULT.json',
  'NEW_PUBLIC_SOURCE_CORRIDOR_FOUND':'PUBLIC_NOMINAL_BAND_EXPERIMENT_NOT_ROBUST_CORRIDOR',
  'run_uniform_corridor.py':'run_nominal_band_m0.py',
  'MOD4V2_HW300N60_T01_AUDITED_CORRIDOR_M0_001':'MOD4V2_HW300N60_T01_NOMINAL_BAND_M0_EXPERIMENT_001',
  't01_uniform_corridor':'t01_nominal_band_m0','nominal_uniform_corridor_m0':'nominal_band_m0',
  'v2_t01_uniform_corridor_m0_nominal_520160_001':'v2_t01_nominal_band_m0_520180_001',
  'Source-geometric routing correction only,not M4/newgain or matched old-route improvement':'Explicit nominal-only source-band experiment;R26 robust pose/lateral corridor remains failed;not M4/newgain or matched old-route improvement',
  "status='NEW_UNIFORM_CORRIDOR_M0_SCENARIO_NOT_OLD_ROUTE_IMPROVEMENT_OR_T01_GRADUATION'":"status='NEW_NOMINAL_BAND_M0_NOT_ROBUST_CORRIDOR_OR_OLD_ROUTE_COMPARISON_OR_T01_GRADUATION'",
 }
 counts={k:0 for k in mapping};seed_changes=0;meta_changes=0;result_changes=0
 class Sub(ast.NodeTransformer):
  def visit_Constant(self,n):
   nonlocal seed_changes,meta_changes,result_changes
   if isinstance(n.value,str):
    value=n.value
    if value in mapping:counts[value]+=1;return ast.copy_location(ast.Constant(mapping[value]),n)
    if value.startswith("meta['new_public_uniform_corridor']"):
     value=value.replace("meta['new_public_uniform_corridor']","meta['new_nominal_band_experiment']",1)
     value+="\n                 meta['robust_corridor_certified']=False";meta_changes+=1;return ast.copy_location(ast.Constant(value),n)
    if 'source_plan_private_scope=plan_scope,'in value and 'previous_three_mechanisms_frozen=True)'in value:
     value=value.replace('previous_three_mechanisms_frozen=True)','previous_three_mechanisms_frozen=True,robust_corridor_certified=False,\n            old_R26_source_robust_margin_test_stays_failed=True,observed_scope_not_worst_case_prior_proof=True)',1)
     result_changes+=1;return ast.copy_location(ast.Constant(value),n)
   if type(n.value)is int and n.value==520160:seed_changes+=1;return ast.copy_location(ast.Constant(520180),n)
   return n
 tree=Sub().visit(tree)
 if not all(v>0 for v in counts.values())or(seed_changes,meta_changes,result_changes)!=(1,1,1):raise ValueError('Original preparer schema changed')
 ns={'__name__':'_nominal_band_new_case_derivation','__file__':str(src)}
 exec(compile(ast.fix_missing_locations(tree),str(src)+'[nominal-band-new-case]','exec'),ns);ns['main']()
 (D/'DERIVATION.json').write_text(json.dumps(dict(original_preparer=src.name,literal_counts=counts,seed_changes=seed_changes,
  case_id='v2_t01_nominal_band_m0_520180_001',original520160_unused=True,upperdeck520170_unused=True,
  controller_unchanged=True,old_gates_unchanged=True,M1_M2_M3_frozen=True,robust_corridor_certified=False,
  original_R26_geometric_margin_failure_unchanged=True,nominal_experiment_not_native_or_hardware_proof=True,
  model_builds=0,forward=0,physics_steps=0,source_queries=0,raw_reads=0),indent=2),encoding='utf-8')
if __name__=='__main__':main()
