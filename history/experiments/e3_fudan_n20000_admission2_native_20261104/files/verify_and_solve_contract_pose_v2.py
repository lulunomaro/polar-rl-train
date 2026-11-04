"""Qualify normalized physical inertia and solve a flat, body-and-wheel-supported legal pose."""
from pathlib import Path
import json,sys,math
import numpy as np,mujoco
from pxr import Usd,UsdGeom,UsdPhysics
D=Path(__file__).resolve().parent;O=D/'CONTRACT_PARITY_AND_POSE_V2.json';assert not O.exists();S=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4');sys.path.insert(0,str(S));from kinematics import leg_configuration
A=D.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets';c=json.loads((A/'import_contract.json').read_bytes());path=D/'contract_parity_mujoco_v1/scene.xml';m=mujoco.MjModel.from_xml_path(str(path));data=mujoco.MjData(m);data.qpos[:7]=[0,0,0,1,0,0,0];mujoco.mj_forward(m,data)
def R(q):q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q);a=np.empty(9);mujoco.mju_quat2Mat(a,q);return a.reshape(3,3)
e=[]
for n,v in c['bodies'].items():
 i=m.body(n).id;Ia=R(m.body_iquat[i])@np.diag(m.body_inertia[i])@R(m.body_iquat[i]).T;Ib=R(v['principal_axes_wxyz'])@np.diag(v['diagonal_inertia_kg_m2'])@R(v['principal_axes_wxyz']).T;e.append(dict(name=n,mass_error=abs(float(m.body_mass[i])-v['mass_kg']),COM_error=float(np.max(abs(m.body_ipos[i]-v['com_m']))),inertia_error=float(np.max(abs(Ia-Ib))),neutral_position_error=float(np.max(abs(data.xpos[i]-v['neutral_position_m'])))))
maxerr=max(max(v[k]for k in('mass_error','COM_error','inertia_error','neutral_position_error'))for v in e);assert maxerr<1e-10,maxerr;assert m.nbody-1==31 and m.njnt-1==30 and m.neq==10
for n,v in dict(c['joints'],**c['roller_joints']).items():
 try:i=m.joint(n).id
 except KeyError:continue
 assert bool(m.jnt_limited[i])==(v['limits_si']is not None),n
 if v['limits_si']is not None:assert np.max(abs(m.jnt_range[i]-v['limits_si']))<1e-10,n
# Verify the source USD's guide cylinder world centre rather than double-counting the old contract position.
stage=Usd.Stage.Open(str(A/'robot.usd'));cache=UsdGeom.XformCache();source_guide=[]
for p in stage.Traverse():
 if p.GetName()=='guide_wheel_00'and p.HasAPI(UsdPhysics.CollisionAPI):source_guide.append(dict(path=str(p.GetPath()),world_position=list(cache.GetLocalToWorldTransform(p).ExtractTranslation())))
assert len(source_guide)==1,source_guide;ours=data.geom_xpos[m.geom('guide_wheel_00').id].copy();assert np.max(abs(ours-source_guide[0]['world_position']))<1e-7,(ours,source_guide)
col=[i for i in range(m.ngeom)if m.geom_contype[i]and m.geom_type[i]!=mujoco.mjtGeom.mjGEOM_PLANE]
def bottom(i):
 z=data.geom_xpos[i,2];r=data.geom_xmat[i].reshape(3,3);s=m.geom_size[i];t=m.geom_type[i]
 if t==6:return float(z-abs(r[2]).dot(s))
 if t==2:return float(z-s[0])
 if t==3:return float(z-abs(r[2,2])*s[1]-s[0])
 if t==5:return float(z-abs(r[2,2])*s[1]-s[0]*math.sqrt(max(0,1-r[2,2]**2)))
 return float(z-m.geom_rbound[i])
bodycols=[i for i in col if m.body(m.geom_bodyid[i]).name=='chassis'or m.body(m.geom_bodyid[i]).name.startswith('guide_roller_')];rootz=-min(bottom(i)for i in bodycols)+.0001;target=.0625+.0001-rootz;rows=[];limit_rejected=0;collision_rejected=0;hi=float(json.loads((S/'model_parameters.json').read_bytes())['limits']['left']['input_difference_rad'][1])
for diff in np.linspace(c['training_window']['input_difference_min_rad'],hi,1801):
 try:_,p0=leg_configuration(0,float(diff))
 except ValueError:continue
 wx,wz=p0['W'];radius=math.hypot(wx,wz)
 if abs(target)>radius:continue
 phi=math.atan2(wx,wz);a=math.acos(target/radius)
 for h0 in(-phi+a,-phi-a):
  hip=(h0+math.pi)%(2*math.pi)-math.pi
  if not-.5<=hip<=.5:continue
  vals={s:leg_configuration(hip,float(diff),s)[0]for s in('left','right')};valid=True
  for side,v in vals.items():
   for n,q in v.items():
    lim=c['joints'][side+'_'+n]['limits_si']
    if lim is not None and not lim[0]-1e-10<=q<=lim[1]+1e-10:valid=False
  if not valid:limit_rejected+=1;continue
  mujoco.mj_resetData(m,data);data.qpos[:7]=[0,0,rootz,1,0,0,0]
  for side,v in vals.items():
   for n,q in v.items():data.qpos[m.joint(side+'_'+n).qposadr[0]]=q
  mujoco.mj_forward(m,data);minimum=min(bottom(i)for i in col)
  if minimum<-.00001:collision_rejected+=1;continue
  W=data.xpos[m.body('left_wheel').id].copy();K=data.xpos[m.body('left_shin').id].copy();same=bool(W[0]*K[0]>0);rows.append(dict(hip_rad=hip,input_difference_rad=float(diff),root_xyz=data.qpos[:3].tolist(),joint_values=vals,qpos=data.qpos.tolist(),wheel_xyz=W.tolist(),knee_xyz=K.tolist(),minimum_collision_height_m=minimum,body_and_wheel_ground_margin_m=.0001,same_end_knee_and_wheel=same,original_ranges_preserved=True))
rows.sort(key=lambda v:(not v['same_end_knee_and_wheel'],-abs(v['wheel_xyz'][0])));r=dict(kind='NOMINAL_CONTRACT_PARITY_PLUS_KINEMATIC_POSE_SEARCH_NOT_SKILL',body_count=m.nbody-1,coordinates=m.njnt-1,equalities=m.neq,total_mass_kg=float(m.body_mass.sum()),max_normalized_physical_parameter_error=maxerr,source_guide_geometry=source_guide,all_authored_joint_limits_and_enable_flags_match=True,prior_build_verifier_error='V1 used unnormalized float32 contract principal quaternion in the comparison matrix; failed threshold1e-8 at1.6431959959373188e-8. V2 normalizes both physical rotations; scene unchanged.',source_principal_quaternion_norm_max_deviation=max(abs(np.linalg.norm(v['principal_axes_wxyz'])-1)for v in c['bodies'].values()),root_level_ground_height=rootz,search_diff_samples=1801,feasible_ground_supported_poses=len(rows),same_end_poses=sum(v['same_end_knee_and_wheel']for v in rows),native_joint_limit_rejected=limit_rejected,collision_rejected=collision_rejected,best_candidates=rows[:5],not_claimed=['video exact rear-leg silhouette','measured hardware range','new native training','original E3 skill pass','PhysX/MuJoCo contact equivalence']);O.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items()if k!='best_candidates'},indent=2));print(json.dumps([{k:v for k,v in p.items()if k not in('qpos','joint_values')}for p in rows[:3]],indent=2))
if rows:
 p=rows[0];data.qpos[:]=p['qpos'];mujoco.mj_forward(m,data);m.vis.headlight.active=1;m.vis.headlight.ambient[:]=.6;m.vis.headlight.diffuse[:]=.8
 with mujoco.Renderer(m,height=600,width=1000)as rr:
  cam=mujoco.MjvCamera();cam.lookat[:]=[0,0,.15];cam.distance=1.3;cam.azimuth=90;cam.elevation=-12;rr.update_scene(data,camera=cam);from PIL import Image;Image.fromarray(rr.render()).save(D/'LEGAL_BODY_AND_WHEELS_GROUND_POSE_V2.png')
