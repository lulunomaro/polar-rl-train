"""One frozen public upper-deck footprint question; no dynamics/controller score search.
Source parser/convex LP semantics reused from R26. Coplanar face UNION avoids
assuming one source triangle alone must contain the whole robot rectangle.
"""
from pathlib import Path
import json,warnings,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog,OptimizeWarning
R=Path(__file__).resolve().parent;D=R/'PUBLIC_UPPERDECK_CORRIDOR_V1'
L=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player')

def area(poly):
 if len(poly)<3:return 0.
 p=np.asarray(poly);return .5*abs(float(p[:,0]@np.roll(p[:,1],-1)-p[:,1]@np.roll(p[:,0],-1)))
def clip(poly,n,d,inside):
 if len(poly)<3:return []
 out=[];sgn=1. if inside else-1.
 for p,q in zip(poly,poly[1:]+poly[:1]):
  p=np.asarray(p);q=np.asarray(q);fp=sgn*(float(n@p)+d);fq=sgn*(float(n@q)+d);ip=fp<=0.;iq=fq<=0.
  if ip:out.append(p)
  if ip!=iq:out.append(p+(q-p)*(fp/(fp-fq)))
 return out if area(out)>1e-14 else[]
def subtract(poly,cover):
 remaining=poly;pieces=[]
 for p,q in zip(cover,cover[1:]+cover[:1]):
  p=np.asarray(p);q=np.asarray(q);edge=q-p;n=np.array([edge[1],-edge[0]]);d=-float(n@p)
  outside=clip(remaining,n,d,False)
  if outside:pieces.append(outside)
  remaining=clip(remaining,n,d,True)
  if not remaining:break
 return pieces

def main():
 if D.exists():raise RuntimeError('Upper-deck question already attempted;no rerun')
 routes=json.loads((L/'routes.json').read_text(encoding='utf-8'));route=next(x for x in routes if x['id']=='central_upper_down')
 anchor=np.asarray(route['spawn_ground_m'],float)
 if not np.allclose(anchor,[-1.5,0.,.4000000059604645],rtol=0.,atol=1e-12):raise ValueError('Published deck anchor changed')
 env=json.loads((R/'NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json').read_text(encoding='utf-8'))
 if env['status']!='NOMINAL_SOURCE_GEOMETRY_FULL_ENVELOPE'or env['actual_robot_geom_count']!=311 or env['unknown_flags']:raise ValueError('No complete envelope')
 mn=np.asarray(env['bbox_all_root3_min_m']);mx=np.asarray(env['bbox_all_root3_max_m']);rot=.3*float(env['max_corner_norm_m'])
 xlo=-.8+mn[0]-rot-.25;xhi=.8+mx[0]+rot+.25;ylo=mn[1]-rot-.2-.04;yhi=mx[1]+rot+.2+.04
 pre=dict(id='PUBLIC_UPPER_DECK_FIXED_FOOTPRINT_001',public_route_anchor=route,root_x_waypoints_m=[-.8,.8],root_y_m=0.,yaw_rad=0.,
  x_full_corridor_m=[float(xlo),float(xhi)],full_corridor_y_m=[float(ylo),float(yhi)],pose_bound_rad=[.1,.1,.1],rotation_margin_m=rot,
  original_lateral_allowance_m=.2,clearance_m=.04,longitudinal_guard_m=.25,geometry_above_floor_threshold_m=.001,
  source_height_compare_tolerance_m=1e-8,coplanar_source_tolerance_m=1e-7,coverage_area_tolerance_m2=1e-10,
  scope='NEW public deck-interior M0 scenario,not old-route improvement/not M4/no reset of3of3;no descent/jump qualification',
  source_parse_passes_planned=1,models=0,physics_steps=0,old_raw_reads=0,SDK_import=False,LP_threads=1,
  limitations='Nominal geometry+declared rigid pose/lateral design margins,not full joint sweep/native contact/hardware proof;source numeric tolerances not certified total bounds')
 D.mkdir(exist_ok=False);(D/'PREEXEC.json').write_text(json.dumps(pre,indent=2),encoding='utf-8')
 xml=ET.parse(L/'rm7v7_latest_moe.xml').getroot();assets={m.get('name'):m for m in xml.find('asset').findall('mesh')};records=[]
 for g in xml.find('worldbody').findall('geom'):
  if not(int(g.get('contype','1'))|int(g.get('conaffinity','1'))):continue
  m=assets[g.get('mesh')]
  if g.get('type')!='mesh'or not m.get('vertex')or m.get('file')or any(k in m.attrib for k in('refpos','refquat'))or any(k in g.attrib for k in('euler','axisangle','xyaxes','zaxis','class')):raise ValueError('Unsupported source transform')
  v=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3)*np.fromstring(m.get('scale','1 1 1'),sep=' ');q=np.fromstring(g.get('quat','1 0 0 0'),sep=' ')
  if len(v)<4 or len(q)!=4 or abs(np.linalg.norm(q)-1)>1e-8:raise ValueError('Invalid convex source')
  w,x,y,z=q;T=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
  v=v@T.T+np.fromstring(g.get('pos','0 0 0'),sep=' ');records.append((g.get('name'),v,v.min(axis=0),v.max(axis=0)))
 if len(records)!=47282:raise ValueError('Unexpected source collider count')
 cache={};hulls=0
 def equations(name,v):
  nonlocal hulls
  if name not in cache:cache[name]=ConvexHull(v).equations;hulls+=1
  return cache[name]
 planes=[]
 for name,v,low,high in records:
  if np.any(anchor[:2]<low[:2]-1e-8)or np.any(anchor[:2]>high[:2]+1e-8)or high[2]<anchor[2]-1e-6 or low[2]>anchor[2]+1e-6:continue
  E=equations(name,v);up=E[E[:,2]>1e-10]
  if not len(up):continue
  zz=-(up[:,:2]@anchor[:2]+up[:,3])/up[:,2];j=int(np.argmin(zz));z=float(zz[j]);f=up[j]
  if abs(z-anchor[2])>1e-6 or np.max(E[:,:3]@np.r_[anchor[:2],z]+E[:,3])>1e-8:continue
  abc=-f[[0,1,3]]/f[2]
  if np.linalg.norm(abc[:2])>1e-5:continue
  planes.append((name,abc))
 base=dict(protocol=pre,actual_source_colliders=len(records),source_parse_passes=1,models=0,physics_steps=0,raw_reads=0,source_payload_hash=False,controller_feedback_from_source=False,
  selected_hull_builds=hulls,LP_calls=0,chosen_plan=None)
 def finish(status,**kw):
  result=dict(base,status=status,selected_hull_builds=hulls,**kw)
  (D/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
  print(json.dumps({k:result[k]for k in('status','selected_hull_builds','LP_calls','chosen_plan')},indent=2));return result
 if not planes:finish('NO_PUBLIC_ANCHOR_HORIZONTAL_SOURCE_FACE');return
 planes.sort(key=lambda p:p[0]);refname,abc=planes[0];a,b,c=abc
 rect=[np.array([x,y])for x,y in((xlo,ylo),(xhi,ylo),(xhi,yhi),(xlo,yhi))];uncovered=[rect];floor_faces=[]
 for name,v,low,high in records:
  if high[0]<xlo or low[0]>xhi or high[1]<ylo or low[1]>yhi:continue
  hv=v[:,2]-v[:,:2]@abc[:2]-c
  if float(hv.min())>1e-7 or float(hv.max())< -1e-7:continue
  E=equations(name,v)
  for f in E[E[:,2]>1e-10]:
   faceabc=-f[[0,1,3]]/f[2]
   if max(abs(float((faceabc[:2]-abc[:2])@p+faceabc[2]-c))for p in rect)>1e-7:continue
   facev=v[np.abs(v@f[:3]+f[3])<=1e-7]
   if len(facev)<3:continue
   xy=facev[:,:2];poly=[x for x in xy[ConvexHull(xy).vertices]];floor_faces.append(dict(source_geom=name,vertex_count=len(poly)))
   nxt=[]
   for piece in uncovered:nxt.extend(subtract(piece,poly))
   uncovered=nxt
   if len(uncovered)>20000:raise RuntimeError('Coverage fragmentation unknown;no truncation')
 uncovered_area=sum(area(p)for p in uncovered);covered=uncovered_area<=1e-10
 if not covered:
  finish('SOURCE_FLOOR_UNION_DOES_NOT_COVER_FIXED_FOOTPRINT',reference_floor_geom=refname,source_floor_plane_z_ax_by_c=abc.tolist(),floor_faces=floor_faces,uncovered_area_m2=uncovered_area,uncovered_piece_count=len(uncovered));return
 obstacles=[];boundary=[];lp_calls=0
 for name,v,low,high in records:
  if high[0]<xlo or low[0]>xhi or high[1]<ylo or low[1]>yhi:continue
  hmax=float(np.max(v[:,2]-v[:,:2]@abc[:2]-c))
  if hmax<=.001+1e-8:
   if hmax>.001:boundary.append(dict(source_geom=name,max_height_m=hmax))
   continue
  E=equations(name,v);A=np.vstack((E[:,:3],[a,b,-1.]));B=np.r_[-E[:,3],-c-.001];lp_calls+=1
  with warnings.catch_warnings():
   warnings.filterwarnings('ignore',category=OptimizeWarning,message='Unrecognized options detected.*')
   sol=linprog([0.,0.,0.],A_ub=A,b_ub=B,bounds=[(xlo,xhi),(ylo,yhi),(None,None)],method='highs',options={'threads':1,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  if sol.status==2:continue
  if not sol.success:raise RuntimeError('Source feasibility unknown:'+name+':'+sol.message)
  obstacles.append(dict(source_geom=name,witness_xyz_m=sol.x.tolist(),vertex_height_range_m=[float(np.min(v[:,2]-v[:,:2]@abc[:2]-c)),hmax]))
 plan=None
 if not obstacles:
  plan=dict(plan_id='public_upperdeck_interior_fixed_m0_v1',root_y_m=0.,full_corridor_y_m=[float(ylo),float(yhi)],waypoints_m=[[-.8,0.,float(a*(-.8)+c)],[.8,0.,float(a*.8+c)]],
   yaw_rad=0.,source_floor_plane_z_ax_by_c=abc.tolist(),reference_floor_geom=refname,public_anchor_route='central_upper_down',public_anchor_used_for_surface_not_descent=True,
   scenario_changed=True,controller_changed=False,default_runtime_changed=False,M1_M2_M3_frozen=True,comparison_with_old_path_is_not_matched=True,
   source_only_not_native_clearance_proof=True,numeric_height_compare_tolerance_m=1e-8)
 base['LP_calls']=lp_calls
 finish('NEW_PUBLIC_SOURCE_CORRIDOR_FOUND'if plan else'PUBLIC_UPPERDECK_FIXED_FOOTPRINT_OBSTRUCTED',reference_floor_geom=refname,source_floor_plane_z_ax_by_c=abc.tolist(),floor_faces=floor_faces,uncovered_area_m2=uncovered_area,
  obstacle_count=len(obstacles),obstacles=obstacles,numeric_boundary_cases=boundary,chosen_plan=plan)
 if plan:(D/'PLAN.json').write_text(json.dumps(plan,indent=2,allow_nan=False),encoding='utf-8')
if __name__=='__main__':main()
