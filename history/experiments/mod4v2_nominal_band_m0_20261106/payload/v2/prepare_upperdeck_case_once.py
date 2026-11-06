"""Derive ONE new deck-interior M0 case from existing unexecuted R26 preparer.
Literal/AST substitutions only; original score gates/control/PD/DR/physics kept.
"""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent
D=R/'T01_UPPERDECK_M0_V1'
def main():
 proof=json.loads((R/'PUBLIC_UPPERDECK_CORRIDOR_V1/PLAN.json').read_text(encoding='utf-8'))
 if proof['controller_changed']or not proof['M1_M2_M3_frozen']:raise ValueError('Not originalM0/new public scenario')
 if D.exists():raise RuntimeError('Deck case preparation prefix consumed')
 src=R/'prepare_uniform_corridor_case_once.py';tree=ast.parse(src.read_text(encoding='utf-8'))
 mapping={
  'T01_UNIFORM_CORRIDOR_V1':'T01_UPPERDECK_M0_V1',
  'PUBLIC_UNIFORM_CORRIDOR_V1/PLAN.json':'PUBLIC_UPPERDECK_CORRIDOR_V1/PLAN.json',
  'PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json':'PUBLIC_UPPERDECK_CORRIDOR_V1/RESULT.json',
  'run_uniform_corridor.py':'run_upperdeck_m0.py',
  'MOD4V2_HW300N60_T01_AUDITED_CORRIDOR_M0_001':'MOD4V2_HW300N60_T01_PUBLIC_UPPERDECK_M0_001',
  't01_uniform_corridor':'t01_upperdeck_m0',
  'nominal_uniform_corridor_m0':'nominal_upperdeck_m0',
  'v2_t01_uniform_corridor_m0_nominal_520160_001':'v2_t01_upperdeck_m0_nominal_520170_001',
  'planned_endpoint_x_bounds=[-9.,-5.5],reverse_progress_projection=False,':'planned_endpoint_x_bounds=[-.8,.8],reverse_progress_projection=False,',
  "status='NEW_UNIFORM_CORRIDOR_M0_SCENARIO_NOT_OLD_ROUTE_IMPROVEMENT_OR_T01_GRADUATION'":"status='NEW_PUBLIC_UPPERDECK_M0_NOT_DESCENT_OR_OLD_ROUTE_COMPARISON_OR_T01_GRADUATION'",
  'Publicsource floor has transverse tilt;uniform-plane corridor is not horizontal z0 proxy.':'Actual authored upper-deck surface/coplanar source-face union,not a z0 proxy;not a descent/jump task.',
 }
 counts={k:0 for k in mapping};seed_changes=0
 class Sub(ast.NodeTransformer):
  def visit_Constant(self,n):
   nonlocal seed_changes
   if isinstance(n.value,str)and n.value in mapping:
    counts[n.value]+=1;return ast.copy_location(ast.Constant(mapping[n.value]),n)
   if type(n.value)is int and n.value==520160:seed_changes+=1;return ast.copy_location(ast.Constant(520170),n)
   return n
 tree=Sub().visit(tree)
 if not all(v>0 for v in counts.values())or seed_changes!=1:raise ValueError('Changed original preparer literals/schema')
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
 pos=next(i for i,n in enumerate(fn.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='proto'for t in n.targets))
 extra=ast.parse("one('center_within_endpoints_plus_025m=bool(xs and min(xs)>=-9.25 and max(xs)<=-5.25))','center_within_endpoints_plus_025m=bool(xs and min(xs)>=-1.05 and max(xs)<=1.05))')").body
 fn.body[pos:pos]=extra
 ns={'__name__':'_deck_m0_one_case_derivation','__file__':str(src)}
 exec(compile(ast.fix_missing_locations(tree),str(src)+'[public-deck-new-case-literals]','exec'),ns);ns['main']()
 (D/'DERIVATION.json').write_text(json.dumps(dict(original_preparer=src.name,literal_substitution_counts=counts,seed_substitutions=seed_changes,
  original_unexecuted_520160_stays_unused=True,case_id='v2_t01_upperdeck_m0_nominal_520170_001',control_unchanged=True,old_gates_unchanged=True,
  public_surface_anchor='central_upper_down',new_fixed_interior_plan_not_authored_descent=True,source_geometry_only_not_runtime_score_search=True,
  model_builds=0,forward=0,physics_steps=0,extra_source_queries=0),indent=2),encoding='utf-8')
if __name__=='__main__':main()
