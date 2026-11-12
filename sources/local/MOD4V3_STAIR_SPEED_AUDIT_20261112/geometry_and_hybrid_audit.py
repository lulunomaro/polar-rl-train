"""Frozen control-output swaps plus geometric measurement, no optimization."""
from pathlib import Path
import json,torch,numpy as np,time
import kinematics_audit as audit
T=Path(__file__).resolve().parent;E=T/'evidence/hybrid_followup';E.mkdir(exist_ok=True);audit.E=E
factory=audit.replay.Simulation;geometry=[]
def measured(args):
 sim=factory(args);original=sim.step
 def step(keys):
  value=original(keys);d=sim.env.d;m=sim.env.m;R=np.asarray(d.xmat[sim.env.base_id]).reshape(3,3);f=np.r_[R[:2,0]/np.linalg.norm(R[:2,0]),0.];pos=np.asarray(d.xpos[sim.env.base_id]);wheel=np.stack([d.xpos[m.body(n).id] for n in ('left_wheel_link','right_wheel_link')]);com=(np.asarray(d.xipos)*np.asarray(m.body_mass)[:,None]).sum(0)/np.asarray(m.body_mass).sum();relative=(R.T@(wheel-pos).T).T;q,qd=sim._current_active()
  geometry.append(dict(COM_minus_wheel_center_forward_m=float((com-wheel.mean(0))@f),base_minus_wheel_center_forward_m=float((pos-wheel.mean(0))@f),wheel_relative_body_x_m=relative[:,0].tolist(),wheel_relative_body_z_m=relative[:,2].tolist(),virtual_leg_angle_rad=np.arctan2(relative[:,0],-relative[:,2]).tolist(),active_joint_position_rad=q.tolist(),body_COM_body_frame=(R.T@(com-pos)).tolist()))
  return value
 sim.step=step;return sim
audit.replay.Simulation=measured
pairs=[('parent',audit.actors['parent']),('010m',audit.actors['010m']),('parent_legs_child_wheels',lambda x:torch.cat((audit.actors['parent'](x)[:,:4],audit.actors['010m'](x)[:,4:]),-1)),('child_legs_parent_wheels',lambda x:torch.cat((audit.actors['010m'](x)[:,:4],audit.actors['parent'](x)[:,4:]),-1))]
rows=[]
for height,command in ((.28,1.5),(.28,2.),(.28,2.2),(.38,2.2)):
 for name,actor in pairs:
  geometry=[];audit.run(name,actor,5,(command,),height);tail=geometry[-200:];record=audit.results[-1]
  record['geometry_mean']={k:np.mean(np.asarray([r[k] for r in tail]),axis=0).tolist() for k in tail[0]};rows.append(record)
  (E/'GEOMETRY_AND_HYBRIDS.json').write_text(json.dumps(dict(protocol='Same seed0,12s, final4s; actors frozen; parent/new only6output channels mixed; diagnostic controller, not a deployable checkpoint',rows=rows),indent=2),encoding='utf8')
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays)
(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(rows),no_optimizer=True)),encoding='utf8')
