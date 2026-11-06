"""R26 public-CAD corridor planning ONLY, not a fourth controller mechanism.
Reuses R25 source transforms/ConvexHull; no old-query replay, SDK, physics or raw.
Single source pass. Obstacles above the authored floor are projected by LP, not
sampled until a controller score wins. Original source and old failures untouched.
"""
from pathlib import Path
import json,warnings,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog,OptimizeWarning
R=Path(__file__).resolve().parent;D=R/'PUBLIC_UNIFORM_CORRIDOR_V1'
L=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player')

def main():
 env=json.loads((R/'NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json').read_text(encoding='utf-8'))
 bmin=np.asarray(env['bbox_all_root3_min_m'],float);bmax=np.asarray(env['bbox_all_root3_max_m'],float);radius=float(env['max_corner_norm_m'])
 if bmin.shape!=(3,)or bmax.shape!=(3,)or not np.isfinite(np.r_[bmin,bmax,radius]).all()or np.any(bmin>=bmax)or radius<=0:raise ValueError('Envelope not usable')
 D.mkdir(exist_ok=False)
 angles=np.array([.1,.1,.1]);rot_margin=radius*float(np.sum(angles))
 longitudinal_guard=.25;original_lateral_gate=.2;clearance=.04;htol=.001
 xlo=-9.+bmin[0]-rot_margin-longitudinal_guard;xhi=-5.5+bmax[0]+rot_margin+longitudinal_guard
 ymin_rel=bmin[1]-rot_margin-original_lateral_gate-clearance;ymax_rel=bmax[1]+rot_margin+original_lateral_gate+clearance
 pre=dict(scope='New public plan only;M0 unchanged;M1-M3=3/3 frozen;not same-route performance comparison',
  source=str(L/'rm7v7_latest_moe.xml'),floor_source_geom='rm_col_3553',root_x_waypoints_m=[-9.,-5.5],original_root_y_m=-1.,
  source_envelope=str(R/'NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json'),bbox_min=bmin.tolist(),bbox_max=bmax.tolist(),
  max_corner_radius_m=radius,nominal_pose_angle_design_bound_rad=angles.tolist(),rotation_inflation_m=rot_margin,
  longitudinal_guard_m=longitudinal_guard,lateral_allowance_m=original_lateral_gate,source_clearance_m=clearance,
  geometric_above_floor_threshold_m=htol,x_full_corridor_m=[xlo,xhi],relative_y_full_envelope_m=[ymin_rel,ymax_rel],
  LP_threads=1,models=0,SDK_import=False,physics_steps=0,raw_reads=0,old_QA=0,source_payload_hash=False,
  limits='Nominal geometry plus explicit pose/lateral design envelope,not full joint-domain swept-body or dynamic/HW proof;source hulls not native contact qualification')
 (D/'PREEXEC.json').write_text(json.dumps(pre,indent=2),encoding='utf-8')
 tree=ET.parse(L/'rm7v7_latest_moe.xml');root=tree.getroot();assets={m.get('name'):m for m in root.find('asset').findall('mesh')};world=root.find('worldbody')
 assert all(b.get('name')=='chassis'for b in world.findall('body'))
 records=[]
 for g in world.findall('geom'):
  if not(int(g.get('contype','1'))|int(g.get('conaffinity','1'))):continue
  m=assets[g.get('mesh')]
  if g.get('type')!='mesh'or not m.get('vertex')or m.get('file')or any(k in m.attrib for k in('refpos','refquat'))or any(k in g.attrib for k in('euler','axisangle','xyaxes','zaxis','class')):raise ValueError('Unsupported public source')
  v=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3)*np.fromstring(m.get('scale','1 1 1'),sep=' ')
  q=np.fromstring(g.get('quat','1 0 0 0'),sep=' ')
  if len(v)<4 or len(q)!=4 or abs(np.linalg.norm(q)-1)>1e-8:raise ValueError('Invalid source convex')
  w,x,y,z=q;rot=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
  records.append((g.get('name'),v@rot.T+np.fromstring(g.get('pos','0 0 0'),sep=' ')))
 assert len(records)==47282
 byname=dict(records);floor=byname['rm_col_3553'];E0=ConvexHull(floor).equations
 above=E0[:,2]>1e-10;upper=E0[above];xy=np.array([-9.034202394678847,-1.2188]);face=upper[np.argmin(-(upper[:,:2]@xy+upper[:,3])/upper[:,2])]
 a,b,c=-face[0]/face[2],-face[1]/face[2],-face[3]/face[2]
 floor_ylo=-np.inf;floor_yhi=np.inf
 for xx in(xlo,xhi):
  for nx,ny,nz,d in E0:
   coef=ny+nz*b;rhs=-(nx+nz*a)*xx-nz*c-d
   if abs(coef)<1e-11:
    if rhs < -1e-8:raise ValueError('Authored floor does not cover planned x range')
   elif coef>0:floor_yhi=min(floor_yhi,rhs/coef)
   else:floor_ylo=max(floor_ylo,rhs/coef)
 if not np.isfinite([floor_ylo,floor_yhi]).all()or floor_ylo>=floor_yhi:raise ValueError('No authored floor interval')
 obstacles=[];lp_calls=0;hulls=1;candidates=0;skipped_below=0;skipped_xy=0
 def solve(E,cost):
  nonlocal lp_calls
  lp_calls+=1
  A=np.vstack((E[:,:3],[a,b,-1.]));B=np.r_[-E[:,3],-c-htol]
  with warnings.catch_warnings():
   warnings.filterwarnings('ignore',category=OptimizeWarning,message='Unrecognized options detected.*')
   return linprog(cost,A_ub=A,b_ub=B,bounds=[(xlo,xhi),(floor_ylo,floor_yhi),(None,None)],method='highs',
    options={'threads':1,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 for name,v in records:
  if name=='rm_col_3553':continue
  mn=v.min(axis=0);mx=v.max(axis=0)
  if mx[0]<xlo or mn[0]>xhi or mx[1]<floor_ylo or mn[1]>floor_yhi:skipped_xy+=1;continue
  if float(np.max(v[:,2]-a*v[:,0]-b*v[:,1]-c))<=htol:skipped_below+=1;continue
  candidates+=1;E=ConvexHull(v).equations;hulls+=1
  low=solve(E,[0.,1.,0.])
  if low.status==2:continue
  if not low.success:raise RuntimeError('Source LP status '+name+': '+low.message)
  high=solve(E,[0.,-1.,0.])
  if not high.success:raise RuntimeError('Source LP max status '+name+': '+high.message)
  obstacles.append(dict(source_geom=name,y_range_m=[float(low.x[1]),float(high.x[1])]))
 intervals=sorted(v['y_range_m']for v in obstacles);merged=[]
 for lo,hi in intervals:
  if merged and lo<=merged[-1][1]+1e-8:merged[-1][1]=max(merged[-1][1],hi)
  else:merged.append([lo,hi])
 free=[];at=float(floor_ylo)
 for lo,hi in merged:
  if lo>at:free.append([at,lo])
  at=max(at,hi)
 if at<floor_yhi:free.append([at,float(floor_yhi)])
 choices=[]
 for lo,hi in free:
  centerlo=lo-ymin_rel;centerhi=hi-ymax_rel
  if centerhi-centerlo<=2e-6:continue
  yy=float(np.clip(-1.,centerlo+1e-6,centerhi-1e-6))
  choices.append(dict(root_y_m=yy,root_y_interval_m=[centerlo,centerhi],distance_from_original_y_m=abs(yy+1),
   ground_free_y_interval_m=[lo,hi],full_corridor_y_m=[yy+ymin_rel,yy+ymax_rel]))
 choices.sort(key=lambda q:(q['distance_from_original_y_m'],q['root_y_m']))
 plan=None
 if choices:
  chosen=choices[0];yy=chosen['root_y_m'];z0=float(a*(-9.)+b*yy+c);z1=float(a*(-5.5)+b*yy+c)
  corners=np.array([[xx,y,a*xx+b*y+c]for xx in(xlo,xhi)for y in chosen['full_corridor_y_m']])
  residual=float(np.max(corners@E0[:,:3].T+E0[:,3]))
  if residual>1e-8:raise ValueError('Final floor rectangle not contained')
  plan=dict(chosen,plan_id='cad_uniform_plane_corridor_v1',waypoints_m=[[-9.,yy,z0],[-5.5,yy,z1]],spawn_ground_m=[-9.,yy,z0],
   yaw_rad=0.,source_floor_plane_z_ax_by_c=[float(a),float(b),float(c)],floor_normal=(-np.array([a,b,-1.])/np.linalg.norm([a,b,-1.])).tolist(),
   floor_rectangle_halfspace_max_residual_m=residual,scenario_changed=True,controller_changed=False,default_runtime_changed=False,
   M1_M2_M3_frozen=True,comparison_with_old_path_is_not_matched=True)
 result=dict(status='NEW_PUBLIC_SOURCE_CORRIDOR_FOUND'if plan else'NO_CONSERVATIVE_CORRIDOR',protocol=pre,
  actual_source_colliders=len(records),source_parse_passes=1,selected_hull_builds=hulls,obstacle_candidate_count=candidates,
  LP_calls=lp_calls,skipped_xy=skipped_xy,skipped_below_floor=skipped_below,source_floor_y_interval_m=[float(floor_ylo),float(floor_yhi)],
  obstacle_y_intervals=obstacles,merged_obstacle_y_intervals_m=merged,free_ground_y_intervals_m=free,admissible_plan_choices=choices,
  chosen_plan=plan,physics_steps=0,raw_reads=0,source_payload_hash=False,controller_feedback_from_source=False)
 (D/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
 if plan:(D/'PLAN.json').write_text(json.dumps(plan,indent=2,allow_nan=False),encoding='utf-8')
 print(json.dumps(dict(status=result['status'],LP_calls=lp_calls,hulls=hulls,chosen_plan=plan),indent=2))
if __name__=='__main__':main()
