"""New bounded physical-limit exercise: resolve a small deliberately penetrated stop; no policy/weights."""
from pathlib import Path
import sys,json,math,traceback
import numpy as np,mujoco
D=Path(__file__).resolve().parent;C=D/'candidates/HW300N60';P=C/'package';out=C/'MECHANICAL_STOP_ENGINE_VALIDATION.json';assert not out.exists();sys.path.insert(0,str(P));import kinematics_v2 as kin
r=dict(kind='MUJOCO_ACTUAL_EQUIVALENT_STOP_RECOVERY_NOT_HARDWARE_CONTACT_CERTIFICATE',gravity_zero_isolated_diagnostic=True,physics_steps=120,policy_training_GPU_or_SDK=False,errors=[])
try:
 m=mujoco.MjModel.from_xml_path(str(P/'mjcf/scene.xml'));d=mujoco.MjData(m);m.opt.gravity[:]=0.;d.qpos[:3]=[0,0,1];d.qpos[3:7]=[1,0,0,0];lo,hi=kin.mechanical_delta_bounds('left');kin.set_configuration(m,d,left=(0,lo-.01),right=(0,0),check_limits=False)
 def state():
  j=m.joint('left_rocker_pin');q=float(d.qpos[j.qposadr[0]]);return dict(rocker=q,rocker_lower=float(m.jnt_range[j.id,0]),rocker_penetration=max(0.,float(m.jnt_range[j.id,0])-q),delta=float(d.qpos[m.joint('left_crank').qposadr[0]]-d.qpos[m.joint('left_hip').qposadr[0]]))
 r['initial']=state();finite=True;leg_names=('left_hip','left_crank','right_hip','right_crank')
 for step in range(120):
  if step%4==0:
   for name in leg_names:
    j=m.joint(name);v=float(d.qvel[j.dofadr[0]]);d.ctrl[m.actuator(name+'_motor').id]=np.clip(-2.*v,-40,40)
  mujoco.mj_step(m,d);finite=finite and bool(np.isfinite(d.qpos).all()and np.isfinite(d.qvel).all())
 r['final']=state();r['finite']=finite;r['stop_was_exercised']=r['initial']['rocker_penetration']>1e-4;r['stop_resolved_inside_1mrad']=r['final']['rocker_penetration']<1e-3;r['passed']=finite and r['stop_was_exercised']and r['stop_resolved_inside_1mrad'];r['target_PhysX_verified']=False;r['real_stop_mesh_contact_tested']=False
except BaseException:r['errors'].append(traceback.format_exc());r['passed']=False
out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2));sys.exit(0 if r['passed']else 1)
