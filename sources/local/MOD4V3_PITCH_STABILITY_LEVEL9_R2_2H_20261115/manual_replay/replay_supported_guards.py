"""Actual step contact points for the ordered ascent; original dwell and closure guard retained."""
import numpy as np,mujoco
import replay_training_guards as original
old_contact=original.contact_state

def supported_contact(sim):
 state=old_contact(sim);e=sim.env;m,d=e.m,e.d
 if sim.direction!='up':return state
 chassis,guides,_=sim._repair_body_ids;bad=False;upward=0.;leg_upward=0.
 for i in range(d.ncon):
  c=d.contact[i];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
  if (b1==0)==(b2==0):continue
  terrain,robot,sgn=(g1,b2,1.)if b1==0 else(g2,b1,-1.)
  body_name=m.body(robot).name or ''
  leg=body_name.startswith(('left_front','left_rear','right_front','right_rear'))and robot not in guides
  if robot!=chassis and robot not in guides and not leg:continue
  force=np.zeros(6);mujoco.mj_contactForce(m,d,i,force)
  if force[0]<=1.:continue
  normal=sgn*np.asarray(c.frame).reshape(3,3)[0];name=m.geom(terrain).name or ''
  level=1 if name=='step_1'else 2 if name=='step_2'else 0
  tread=bool(level and normal[2]>.7 and abs(c.pos[2]-.2*level)<.025)
  face=bool(level and abs(normal[0])>.7 and abs(abs(c.pos[0])-(2.9 if level==1 else 1.4))<.035 and .2*(level-1)-.01<=c.pos[2]<=.2*level+.03)
  if tread:
   fz=max(0.,force[0]*normal[2]);upward+=fz
   if leg:leg_upward+=fz
  elif not(face or(robot in guides and state['guide_contact_allowed'])):
   if robot==chassis or robot in guides:bad=True
 state.update(contact_bad=bad,upper_tread_body_guide_upward_N=upward,upper_tread_all_allowed_upward_N=upward,upper_tread_leg_upward_N=leg_upward,task='ordered_rearward_contact_ascent_actual_points')
 return state

def replay_step(*args,**kwargs):
 original.contact_state=supported_contact
 return original.replay_step(*args,**kwargs)
