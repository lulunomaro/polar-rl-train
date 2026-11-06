"""New explicit NOMINAL experiment, NOT acceptance of R26 robust corridor.
Geometry-only choice made before physics, no source payload parse/score search.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'PUBLIC_NOMINAL_BAND_EXPERIMENT_V1'
def main():
 old=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001/RESULT.json').read_text(encoding='utf-8'))
 h=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001/RESULT.json').read_text(encoding='utf-8'))
 env=json.loads((R/'NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json').read_text(encoding='utf-8'))
 if old['status']!='NO_CONSERVATIVE_CORRIDOR'or old['chosen_plan']is not None or len(old['free_ground_y_intervals_m'])!=1:raise ValueError('Keep original failed corridor result')
 lo,hi=old['free_ground_y_intervals_m'][0];yy=.5*(lo+hi);a,b,c=h['source_floor_plane_z_ax_by_c'];clearance=.04
 nominal_lo=yy+env['bbox_all_root3_min_m'][1];nominal_hi=yy+env['bbox_all_root3_max_m'][1]
 if nominal_lo<lo+clearance or nominal_hi>hi-clearance:raise ValueError('Even nominal source envelope does not fit;no experiment')
 plan=dict(plan_id='nominal_m0_center_of_existing_source_band_v1',root_y_m=yy,full_corridor_y_m=[lo+clearance,hi-clearance],
  waypoints_m=[[-9.,yy,a*(-9.)+b*yy+c],[-5.5,yy,a*(-5.5)+b*yy+c]],yaw_rad=0.,
  source_floor_plane_z_ax_by_c=[a,b,c],source_free_y_band_m=[lo,hi],nominal_ROOT_box_world_y_m=[nominal_lo,nominal_hi],
  nominal_source_clearance_m=clearance,scenario_changed=True,controller_changed=False,default_runtime_changed=False,M1_M2_M3_frozen=True,
  comparison_with_old_path_is_not_matched=True,robust_corridor_certified=False,original_R26_pose_lateral_margin_test_stays_failed=True,
  declaration='Nominal experiment only;not passing old geometric certificate by shrinking margins;unchanged physical/old score gates;actual cached footprint observed separately',
  source_numeric_comparison_tolerance_m=1e-8,source_is_not_certified_native_clearance=True,geometry_choice_does_not_use_controller_results=True)
 proof=dict(status='PUBLIC_NOMINAL_BAND_EXPERIMENT_NOT_ROBUST_CORRIDOR',protocol=dict(x_full_corridor_m=old['protocol']['x_full_corridor_m'],
  old_R26_required_full_width_m=old['protocol']['relative_y_full_envelope_m'][1]-old['protocol']['relative_y_full_envelope_m'][0],
  old_R26_pose_bound_rad=[.1,.1,.1],old_R26_lateral_allowance_m=.2,these_robust_margins_not_certified=True),
  robust_corridor_certified=False,old_R26_result_unchanged=True,nominal_geometry_only=True,models=0,forward=0,physics_steps=0,source_parse=0,raw_reads=0,
  chosen_plan=plan,source_results=['PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001/RESULT.json','PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001/RESULT.json','NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json'])
 D.mkdir(exist_ok=False)
 (D/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(D/'RESULT.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
 print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
