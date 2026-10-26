"""Unused83B same-asset USD kinematics from newly saved selected arrays; no dynamics/policy."""
from pathlib import Path
import hashlib,json,math,time,traceback
import numpy as np
from pxr import Usd,UsdPhysics
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026';A=P/'payloads/h1/job0/assets/robot.usd'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def Q(q):
 q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q);x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def U(p,q):
 out=np.eye(4);out[:3,:3]=Q([*q.GetImaginary(),q.GetReal()]);out[:3,3]=p;return out
def main():
 z=np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False);geo=json.loads((T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json').read_bytes());names=geo['body_names'];stage=Usd.Stage.Open(str(A));joints={};closures=[]
 for prim in stage.Traverse():
  if not prim.IsA(UsdPhysics.Joint):continue
  joint=UsdPhysics.Joint(prim);a=joint.GetBody0Rel().GetTargets();b=joint.GetBody1Rel().GetTargets()
  if not a or not b:continue
  row=dict(name=prim.GetName(),parent=str(a[0]).split('/')[-1],child=str(b[0]).split('/')[-1],T0=U(joint.GetLocalPos0Attr().Get(),joint.GetLocalRot0Attr().Get()),T1=U(joint.GetLocalPos1Attr().Get(),joint.GetLocalRot1Attr().Get()),kind=prim.GetTypeName())
  if 'Spherical' in row['kind']:closures.append(row)
  else:
   row['axis']=str(prim.GetAttribute('physics:axis').Get());joints[row['child']]=row
 order=[joints[b]['name'] for b in names[1:]];assert len(order)==30 and len(set(order))==30
 root=z['root13'];q=z['q30'];origins=z['env_origins'];frames,count=root.shape[:2];poses=np.empty((frames,count,len(names),4,4));closure=np.empty((frames,count,len(closures)))
 for f in range(frames):
  for e in range(count):
   by={};base=np.eye(4);base[:3,:3]=Q(root[f,e,3:7]);base[:3,3]=root[f,e,:3]-origins[e];by[names[0]]=base
   for k,name in enumerate(names[1:]):
    row=joints[name];axis='XYZ'.index(row['axis']);motion=np.eye(4);v=float(q[f,e,k])
    if 'Prismatic' in row['kind']:motion[axis,3]=v
    else:
     qq=np.zeros(4);qq[axis]=math.sin(v/2);qq[3]=math.cos(v/2);motion[:3,:3]=Q(qq)
    by[name]=by[row['parent']]@row['T0']@motion@np.linalg.inv(row['T1'])
   poses[f,e]=np.stack([by[n] for n in names])
   for k,row in enumerate(closures):closure[f,e,k]=np.linalg.norm((by[row['parent']]@row['T0'])[:3,3]-(by[row['child']]@row['T1'])[:3,3])
 wheel=[]
 for name in ('left_wheel','right_wheel'):
  shapes=[s for s in geo['shapes'] if s['body']==name];assert len(shapes)==1 and shapes[0]['type']=='Mesh';s=shapes[0];points=np.array(s['points'])@np.array(s['linear_body_from_shape']).T+np.array(s['origin_body_m']);mat=poses[:,:,names.index(name)];world=np.einsum('feij,pj->fepi',mat[:,:,:3,:3],points)+mat[:,:,:3,3,None].transpose(0,1,3,2);wheel.append(world)
 lo=np.stack([x.min(2) for x in wheel],2);hi=np.stack([x.max(2) for x in wheel],2)
 summaries=[]
 for e,env_id in enumerate(z['env_ids']):
  apex=int(np.argmax(lo[:,e,:,2].min(-1)));frontgap=.35-hi[:,e,:,0].min(-1);clear=lo[:,e,:,2].min(-1)>=.27
  summaries.append(dict(env_id=int(env_id),column=e,root_x_start=float(z['root_local'][0,e,0]),root_x_end=float(z['root_local'][-1,e,0]),root_dx=float(z['root_local'][-1,e,0]-z['root_local'][0,e,0]),both_wheel_bottom_max_m=float(lo[:,e,:,2].min(-1).max()),min_two_wheel_leading_edge_gap_to_step_m=float(frontgap.min()),apex_row=apex,front_gap_at_apex_m=float(frontgap[apex]),clearance_ge270_rows=int(clear.sum()),min_gap_while_clear_m=float(frontgap[clear].min()) if clear.any() else None,root_vx_mean=float(root[:,e,7].mean()),recorded_crossed_any=bool(z['step_wheel_crossed'][:,e].any()),recorded_takeoff_count=int(z['takeoff_count'][:,e].max()),recorded_done_any=bool(z['done'][:,e].any()),reconstructed_closure_max_m=float(closure[:,e].max())))
 out=D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz';np.savez_compressed(out,body_pose=poses,wheel_min=lo,wheel_max=hi,closure=closure,env_ids=z['env_ids'])
 put('RECORDED_USD_KINEMATICS_CPU_ACTUAL.json',dict(epoch=time.time(),scope='Kinematic visualization from actual 100Hz root13/q30 and same-source USD; no dynamic integration or new policy action',actual_body_order_source=str(T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json'),joint_order_derived_from_actual_31link_order_each_one_DOF_incoming_joint=order,not_fresh_PhysX_joint_name_readback=True,closure_max_m=float(closure.max()),recorded_closure_max_m=float(z['closure'].max()) if 'closure' in z else None,kinematic_closure_is_visual_consistency_only_not_new_training_gate=True,asset_path=str(A),shapes=geo['shapes'],body_names=names,case_summaries=summaries,artifact=dict(path=str(out),bytes=out.stat().st_size,SHA=hashlib.sha256(out.read_bytes()).hexdigest()),original_trace_control_rate_not_callback_replay=True,no_model_optimizer_GPU_plant_or_account_write=True))
 print(json.dumps(dict(closure_max_m=float(closure.max()),cases=sorted(summaries,key=lambda x:x['both_wheel_bottom_max_m'],reverse=True)[:4])))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('KINEMATIC_RECONSTRUCTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_same_once=True));raise
