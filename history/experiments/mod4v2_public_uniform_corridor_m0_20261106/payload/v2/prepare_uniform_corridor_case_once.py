"""New CAD SCENARIO with unchanged M0, not M4/relabel of old failed scores.
All original score thresholds/windows and actuation source preserved.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'T01_UNIFORM_CORRIDOR_V1';OLD=R/'T01_OBSERVABILITY_V1'

def main():
 plan=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/PLAN.json').read_text(encoding='utf-8'))
 proof=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json').read_text(encoding='utf-8'))
 if proof['status']!='NEW_PUBLIC_SOURCE_CORRIDOR_FOUND'or plan['controller_changed']or not plan['M1_M2_M3_frozen']:raise ValueError('No new valid public plan')
 text=(OLD/'run_reverse_observe.py').read_text(encoding='utf-8')
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise RuntimeError('Source anchor not unique: '+a)
  text=text.replace(a,b,1)
 one('# ONE new reverse route diagnostic; old thresholds retained,progress projects along public reverse direction.',
  '# NEW audited uniform-plane corridor SCENARIO with original M0; old route failures and 3/3 cap retained.')
 one("meta['zones'][0]['spawn']=copy.deepcopy(protocol['public_route']['start_ground_m'])",
  "meta['zones'][0]['key']=protocol['zone_key']\n                 meta['zones'][0]['spawn']=copy.deepcopy(protocol['public_route']['start_ground_m'])")
 one("meta['planned_reverse_route']=copy.deepcopy(protocol['public_route'])",
  "meta['new_public_uniform_corridor']=copy.deepcopy(protocol['public_route'])\n                 meta['original_default_M0_controller_unchanged']=True")
 one("        for k in range(n):",'''        plan_scope=dict(samples=0,all_geom_cached_xy_within_corridor=True,root_pose_design_bounds_observed=True,
            geom_cache_is_PRE_last_physics_tick=True,geometry_cache_age_s=.0005,extra_forward_or_step=0,
            all_robot_geom_count=0,maximum_xy_excess_m=0.,max_root_rpy_abs3_rad=[0.,0.,0.],truth_only_no_actor_connection=True)
        gids=np.flatnonzero(p.m.geom_bodyid>0)
        if len(gids)!=311:raise RuntimeError('Expected all311 original robot geoms')
        corners=np.array([[x,y,z]for x in(-1,1)for y in(-1,1)for z in(-1,1)],float)
        local=p.m.geom_aabb[gids,:3,None]+p.m.geom_aabb[gids,3:,None]*corners.T[None,:,:]
        local=np.transpose(local,(0,2,1));plan_scope['all_robot_geom_count']=len(gids)
        bounds=protocol['scenario_plan'];xb=bounds['x_full_corridor_m'];yb=bounds['full_corridor_y_m']
        def private_plan_scope(g):
            world=np.einsum('nij,nkj->nki',p.d.geom_xmat[gids].reshape(-1,3,3),local)+p.d.geom_xpos[gids,None,:]
            xymin=world[:,:,:2].min(axis=(0,1));xymax=world[:,:,:2].max(axis=(0,1))
            excess=max(0.,xb[0]-float(xymin[0]),float(xymax[0])-xb[1],yb[0]-float(xymin[1]),float(xymax[1])-yb[1])
            qw,qx,qy,qz=map(float,p.d.qpos[3:7]);yy=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
            rpy=[float(g['roll_true']),float(g['pitch_true']),yy]
            plan_scope['samples']+=1;plan_scope['maximum_xy_excess_m']=max(plan_scope['maximum_xy_excess_m'],excess)
            plan_scope['all_geom_cached_xy_within_corridor'] &= excess<=1e-8
            plan_scope['root_pose_design_bounds_observed'] &= max(abs(v)for v in rpy)<=.1+1e-8
            for j in range(3):plan_scope['max_root_rpy_abs3_rad'][j]=max(plan_scope['max_root_rpy_abs3_rad'][j],abs(rpy[j]))
            return dict(cache_time_s=float(p.d.time)-.0005,xy_min_m=xymin.tolist(),xy_max_m=xymax.tolist(),
                xy_excess_m=excess,root_POST_rpy_rad=rpy,private_only=True)
        for k in range(n):''')
 one("            xy = np.asarray(g['xyz'][:2])-origin",
  "            private_scope_row=private_plan_scope(g)\n            xy = np.asarray(g['xyz'][:2])-origin")
 one("                source_time_metadata=metadata,","                source_time_metadata=metadata,source_plan_private_scope=private_scope_row,")
 one('planned_endpoint_x_bounds=[-9.,-5.5],reverse_progress_projection=True,',
  'planned_endpoint_x_bounds=[-9.,-5.5],reverse_progress_projection=False,')
 one("status='NEW_REVERSE_OBSERVABILITY_CASE_NOT_T01_GRADUATION_OR_MATCHED_FORWARD_COMPARISON'",
  "status='NEW_UNIFORM_CORRIDOR_M0_SCENARIO_NOT_OLD_ROUTE_IMPROVEMENT_OR_T01_GRADUATION'")
 one('            observer_data_returned_to_engine_or_controller_or_proxy=False)',
  '            observer_data_returned_to_engine_or_controller_or_proxy=False,source_plan_private_scope=plan_scope,\n            new_scenario_scope_valid=bool(plan_scope[\'samples\']==n and plan_scope[\'all_geom_cached_xy_within_corridor\'] and plan_scope[\'root_pose_design_bounds_observed\']),\n            controller_changed=False,previous_three_mechanisms_frozen=True)')
 proto=json.loads((OLD/'PROTOCOL.json').read_text(encoding='utf-8'));original_gates=dict(proto['gates'])
 proto.update(id='MOD4V2_HW300N60_T01_AUDITED_CORRIDOR_M0_001',status='frozen_before_one_new_scenario_M0_case',
  scope='Source-geometric routing correction only,not M4/newgain or matched old-route improvement',zone_key='t01_uniform_corridor',
  formal_cases=[dict(id='nominal_uniform_corridor_m0',seed=520160,nominal=True,profile='slow')],direction_sign=1.,
  public_route=dict(source=str(R/'PUBLIC_UNIFORM_CORRIDOR_V1/PLAN.json'),id=plan['plan_id'],start_ground_m=plan['waypoints_m'][0],
    goal_ground_m=plan['waypoints_m'][1],yaw_rad=0.,change='New explicit source-audited path before physics;originalCAD/old failures/3of3 frozen unchanged'),
  scenario_plan=dict(x_full_corridor_m=proof['protocol']['x_full_corridor_m'],full_corridor_y_m=plan['full_corridor_y_m'],
    geometry_design_pose_bounds_rad=[.1,.1,.1],observed_all311_geometry_AABBs_private_100Hz=True,
    limits='PRE cache age.5ms,not continuous swept volume;scope diagnostics separate from unchanged old score gates'),
  old_failed_route_case_ids_retained=[520111,520121,520130,520141,520151],controller_unchanged_from_M0=True,M1_M2_M3_frozen=True)
 proto['slow_command']['forward_m_s']=.3
 proto['notes']+=['New plan and initial location,not performance retuning or a pass on original flat_run path.',
  'Same originalM0 controller/runtime;originalcase gates/windows remain,scope diagnostics separate;no additional control mechanism.',
  'Publicsource floor has transverse tilt;uniform-plane corridor is not horizontal z0 proxy.']
 assert proto['gates']==original_gates and proto['controller']=='coord_soft_MOD4v2_fresh_LQR_heading'
 if D.exists():raise RuntimeError('New scenario prefix exists,do not prepare twice')
 compile(text,str(D/'run_uniform_corridor.py'),'exec')
 D.mkdir(exist_ok=False)
 (D/'run_uniform_corridor.py').write_text(text,encoding='utf-8')
 (D/'PROTOCOL.json').write_text(json.dumps(proto,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(models=0,physics_steps=0,raw_reads=0,controller_changed=False,old_gates_unchanged=True,
  planned_case='v2_t01_uniform_corridor_m0_nominal_520160_001',single_new_scenario=True,case_not_yet_executed=True),indent=2),encoding='utf-8')
 print('NEW_SOURCE_AUDITED_CORRIDOR_M0_PREPARED; no M4/no modelorphysics;old gates and old route failures retained')
if __name__=='__main__':main()
