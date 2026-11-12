"""Capture exact nominal MuJoCo controller and coordinates, frozen models."""
from pathlib import Path
import sys,json,numpy as np,time
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'))
import kinematics_audit as audit
E=T/'evidence/mj_control_trace_r1';E.mkdir(exist_ok=False);audit.E=E
factory=audit.replay.Simulation;traces={};layout={}
def instrument(args):
 s=factory(args);e=s.env;before=s.step;torque=e._torque;tr={k:[] for k in ('joint_pos','joint_vel','torque','root')};traces[label]=tr
 def step(keys):
  tr['joint_pos'].append(e.d.qpos[e.qadr_all].copy());tr['joint_vel'].append(e.d.qvel[e.dadr_all].copy());tr['root'].append(np.r_[e.d.qpos[:7],e.d.qvel[:6]])
  return before(keys)
 def tor(a):
  v=torque(a);tr['torque'].append(v.numpy().copy().reshape(-1));return v
 s.step=step;e._torque=tor
 layout.update(joint_names=e.spec.joint_names,active_names=s.active_names,actuator_order=[e.spec.joint_names[i] for i in e.spec.act_idx],default_active=s.default_active.tolist())
 return s
audit.replay.Simulation=instrument
for model in ('parent','010m'):
 for h in (.28,.38):
  label=f'{model}_h{h}';audit.run(model,audit.actors[model],0,(2.2,),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays,**{label+'_'+k:np.asarray(v) for label,tr in traces.items() for k,v in tr.items()})
(E/'LAYOUT.json').write_text(json.dumps(layout,indent=2));(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=4,no_optimizer=True)))
