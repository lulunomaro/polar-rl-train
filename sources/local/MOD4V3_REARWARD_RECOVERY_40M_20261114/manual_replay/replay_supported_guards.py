"""Upper-tread support is allowed for the video-matched ascent task only."""
import numpy as np,mujoco
import replay_training_guards as original
old_contact=original.contact_state

def supported_contact(sim):
 state=old_contact(sim);e=sim.env;m,d=e.m,e.d
 if sim.direction!='up':return state
 chassis,guides,_=sim._repair_body_ids;bad=False;upward=0.
 for i in range(d.ncon):
  c=d.contact[i];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
  if (b1==0)==(b2==0):continue
  terrain,robot,sgn=(g1,b2,1.) if b1==0 else (g2,b1,-1.)
  if robot!=chassis and robot not in guides:continue
  force=np.zeros(6);mujoco.mj_contactForce(m,d,i,force)
  if force[0]<=1.:continue
  normal=sgn*np.asarray(c.frame).reshape(3,3)[0];name=m.geom(terrain).name or ''
  tread=name in ('step_1','step_2') and normal[2]>.7
  if tread:upward+=max(0.,force[0]*normal[2])
  elif not(robot in guides and state['guide_contact_allowed']):bad=True
 state.update(contact_bad=bad,upper_tread_body_guide_upward_N=upward,task='video_supported_rearward_ascent');return state

def replay_step(*args,**kwargs):
 original.contact_state=supported_contact
 return original.replay_step(*args,**kwargs)
