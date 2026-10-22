from pathlib import Path
import json,math,time,traceback
import numpy as np
from pxr import Usd,UsdPhysics
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';N=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def Q(q):
 q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q);x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def U(p,q):
 out=np.eye(4);out[:3,:3]=Q([*q.GetImaginary(),q.GetReal()]);out[:3,3]=p;return out
try:
 data=json.loads((R/'V110_ACTUAL_PRE_FAILURE_THREE_CONTROL_STATE_CPU_ACTUAL.json').read_bytes());s=data['selected_state'];root=np.array(s['root13']);angles=np.array(s['q30'])
 geo=json.loads((T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json').read_bytes());names=geo['body_names'];asset=N/'payloads/h1/job0/assets/robot.usd';stage=Usd.Stage.Open(str(asset));joints={};closures=[]
 for prim in stage.Traverse():
  if not prim.IsA(UsdPhysics.Joint):continue
  j=UsdPhysics.Joint(prim);a=j.GetBody0Rel().GetTargets();b=j.GetBody1Rel().GetTargets()
  if not a or not b:continue
  row=dict(name=prim.GetName(),parent=str(a[0]).split('/')[-1],child=str(b[0]).split('/')[-1],T0=U(j.GetLocalPos0Attr().Get(),j.GetLocalRot0Attr().Get()),T1=U(j.GetLocalPos1Attr().Get(),j.GetLocalRot1Attr().Get()),kind=prim.GetTypeName())
  if 'Spherical' in row['kind']:closures.append(row)
  else:row['axis']=str(prim.GetAttribute('physics:axis').Get());joints[row['child']]=row
 order=[joints[b]['name'] for b in names[1:]];assert len(order)==30 and len(set(order))==30
 rows=[]
 for f in range(3):
  base=np.eye(4);base[:3,:3]=Q(root[f,3:7]);base[:3,3]=root[f,:3];by={names[0]:base}
  for k,name in enumerate(names[1:]):
   j=joints[name];axis='XYZ'.index(j['axis']);motion=np.eye(4);a=float(angles[f,k])
   if 'Prismatic' in j['kind']:motion[axis,3]=a
   else:q=np.zeros(4);q[axis]=math.sin(a/2);q[3]=math.cos(a/2);motion[:3,:3]=Q(q)
   by[name]=by[j['parent']]@j['T0']@motion@np.linalg.inv(j['T1'])
  wheel=[]
  for name in ('left_wheel','right_wheel'):
   shapes=[x for x in geo['shapes'] if x['body']==name];assert len(shapes)==1 and shapes[0]['type']=='Mesh';shape=shapes[0];pts=np.array(shape['points'])@np.array(shape['linear_body_from_shape']).T+np.array(shape['origin_body_m']);mat=by[name];world=pts@mat[:3,:3].T+mat[:3,3];wheel.append(dict(name=name,body_center=mat[:3,3].tolist(),lo=world.min(0).tolist(),hi=world.max(0).tolist()))
  closure=max(np.linalg.norm((by[x['parent']]@x['T0'])[:3,3]-(by[x['child']]@x['T1'])[:3,3]) for x in closures)
  rows.append(dict(control=data['complete_control_numbers'][f],root_position=root[f,:3].tolist(),root_inside_original_floor=bool((-178.75<=root[f,0]<=178.75) and (-177.5<=root[f,1]<=177.5)),wheels=wheel,reconstructed_wheel_max_y=max(x['hi'][1] for x in wheel),wheel_footprint_outside_floor=bool(max(x['hi'][1] for x in wheel)>177.5),recorded_done=s['done'][f],recorded_episode=s['episode'][f],reconstructed_closure_max_m=float(closure),recorded_closure_m=s['closure'][f]))
 assert all(x['root_inside_original_floor'] and x['wheel_footprint_outside_floor'] for x in rows)
 put('V110_RECORDED_PRE_FAILURE_ROOT_INSIDE_WHEEL_FOOTPRINT_OUTSIDE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_recorded_kinematic_diagnosis=True,rows=rows,scope='Three actual 100Hz root/q records with same authored USD FK; not PhysX callback replay or actual future repaired run',joint_order_derived_from_actual_body_order_not_new_PhysX_readback=order,asset=str(asset),actual_bad_query_y=177.50027465820312,floor_y_max=177.5,root_only_boundary_blindspot_consistent_with_pre_failure_records=True,no_guarantee_for_all_future_boundary_crossings=True,no_new_actor_optimizer_RNG_GPU_physics_query_or_model_load=True))
 print(json.dumps(dict(root_inside_all=True,reconstructed_wheel_footprint_outside_all=True,rows=rows)))
except BaseException:put('V110_RECORDED_BOUNDARY_RECONSTRUCTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
