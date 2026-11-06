"""One declared numeric-boundary refinement, not score/route/clearance tuning.
Original complete NO_CORRIDOR and bounded source diagnosis stay immutable.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001'
def main():
 prior=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json').read_text(encoding='utf-8'))
 diagnosis=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001/RESULT.json').read_text(encoding='utf-8'))
 if prior['status']!='NO_CONSERVATIVE_CORRIDOR'or len(diagnosis['blockers'])!=1:raise ValueError('Unexpected original diagnosis')
 blocker=diagnosis['blockers'][0]
 if blocker['source_geom']!='rm_col_43671'or not(0<blocker['height_above_reference_plane_vertex_range_m'][1]-.001<1e-8):raise ValueError('Not the documented 1mm numeric boundary')
 if D.exists():raise RuntimeError('Numeric-boundary prefix consumed;no rerun')
 text=(R/'plan_public_uniform_corridor_once.py').read_text(encoding='utf-8')
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise ValueError('Nonunique exact source anchor:'+a)
  text=text.replace(a,b,1)
 one('clearance=.04;htol=.001','clearance=.04;htol=.001;numeric_compare_tol=1e-8')
 one('geometric_above_floor_threshold_m=htol,x_full_corridor_m=[xlo,xhi],',
  "geometric_above_floor_threshold_m=htol,numeric_height_compare_tolerance_m=numeric_compare_tol,numeric_tolerance_is_not_certified_native_contact_bound=True,x_full_corridor_m=[xlo,xhi],")
 one('obstacles=[];lp_calls=0;hulls=1;candidates=0;skipped_below=0;skipped_xy=0',
  'obstacles=[];lp_calls=0;hulls=1;candidates=0;skipped_below=0;skipped_xy=0;numeric_boundary_cases=[]')
 one('   if float(np.max(v[:,2]-a*v[:,0]-b*v[:,1]-c))<=htol:skipped_below+=1;continue',
  "   hmax=float(np.max(v[:,2]-a*v[:,0]-b*v[:,1]-c))\n   if hmax<=htol+numeric_compare_tol:\n    if hmax>htol:numeric_boundary_cases.append(dict(source_geom=name,max_height_m=hmax,delta_above_literal_threshold_m=hmax-htol,resolution='within declared source numeric comparison tolerance,not certified physical-clearance proof'))\n    skipped_below+=1;continue")
 one('chosen_plan=plan,physics_steps=0,raw_reads=0,',
  'chosen_plan=plan,numeric_boundary_cases=numeric_boundary_cases,original_literal_NO_CORRIDOR_retained=True,source_plan_is_numeric_candidate_not_native_sweep_proof=True,physics_steps=0,raw_reads=0,')
 compile(text,str(D/'derived_planner.py'),'exec')
 ns={'__name__':'_uniform_corridor_boundary_refinement','__file__':str(R/'plan_public_uniform_corridor_once.py')}
 exec(compile(text,str(D/'derived_planner.py'),'exec'),ns);ns['D']=D;ns['main']()
 (D/'DERIVATION.json').write_text(json.dumps(dict(original_source='plan_public_uniform_corridor_once.py',
  original_result='../RESULT.json',diagnosis='../HEIGHT_INSPECT001/RESULT.json',documented_height_delta_m=blocker['height_above_reference_plane_vertex_range_m'][1]-.001,
  numeric_compare_tol_m=1e-8,original_geometry_threshold_m=.001,original_contact_gates_unchanged=True,original_clearances_pose_margins_lateral_allowances_unchanged=True,
  no_new_controller_mechanism=True,no_physics_or_score_route_search=True,not_a_certified_native_source_roundoff_bound=True),indent=2),encoding='utf-8')
if __name__=='__main__':main()
