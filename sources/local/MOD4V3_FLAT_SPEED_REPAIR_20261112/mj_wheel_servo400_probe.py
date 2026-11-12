"""Matching400Hz wheel/100Hz leg servo in MuJoCo; frozen actors and plant."""
from pathlib import Path
import sys,json,numpy as np,torch,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'));import kinematics_audit as audit
E=T/'evidence/mj_wheel_servo400_r1';E.mkdir(exist_ok=False);audit.E=E

def physics(self,action):
 e=self.sim.env;action=action.clamp(-e.action_clip,e.action_clip);self.action_history.append((float(e.d.time),action.detach().clone()));self.sent_trace.append(action.detach().numpy().reshape(-1).tolist());applied=action
 for j in range(e.decim):
  applied=self.lookup(self.action_history,float(e.d.time)-self.action_s);tau=e._torque(applied).detach().numpy().reshape(-1)
  if j%4==0:e.d.ctrl[e.act_ids]=tau
  else:e.d.ctrl[e.act_ids[4:]]=tau[4:]
  audit.replay.mujoco.mj_step(e.m,e.d);self.sensor_history.append((float(e.d.time),self.sensor()))
 e.a_prev=applied.detach().clone();self.last_applied=applied[:,self.sim.ppo_to_env].detach().cpu().clone();self.applied_trace.append(applied.detach().numpy().reshape(-1).tolist());return e.state()
audit.replay.DelayReplay.physics=physics
for name in ('parent','010m'):
 for h in (.28,.38):audit.run(name+'__servo400',audit.actors[name],0,(-1.5,0.,2.2),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays);(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),no_optimizer=True,wheel_PD_s=.0025,leg_PD_s=.01,canonical_plant_unchanged=True)))
