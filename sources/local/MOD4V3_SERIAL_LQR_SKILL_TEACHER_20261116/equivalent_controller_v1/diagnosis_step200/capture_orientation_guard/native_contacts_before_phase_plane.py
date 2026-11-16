"""Translation-invariant contact-frame geometry for the simulation teacher.
Privileged teacher contact positions/forces are explicit. No absolute stair position,
terrain geom name, policy input, or c874 observation is used for control decisions.
"""
import numpy as np,mujoco as mj
class NativeContacts:
 def __init__(self,m,d,base,wheels,guides,radius):
  self.m,self.d,self.base=m,d,base;self.wheels=set(wheels);self.guides=set(guides);self.radius=radius;self.edge=None;self.top=None;self.window=[]
  self.floor=float(min(d.xpos[list(wheels),2])-radius)
 def instant_sample(self):
  m,d=self.m,self.d;pos=d.xpos[self.base];R=d.xmat[self.base].reshape(3,3);forward=R[:,0].copy();forward[2]=0.;forward/=max(np.linalg.norm(forward),1e-9)
  vertical=wall=moment=0.;top=None;events=[];wheel_up={b:False for b in self.wheels};wheel_wall={b:False for b in self.wheels};wheel_top={b:False for b in self.wheels};wheel_vertical={b:0. for b in self.wheels}
  for i,c in enumerate(d.contact):
   g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2]);body=b2 if b1==0 else b1 if b2==0 else -1
   if body<0:continue
   robot_geom=g2 if b1==0 else g1;normal=(1. if b1==0 else -1.)*np.asarray(c.frame).reshape(3,3)[0];force=np.zeros(6);mj.mj_contactForce(m,d,i,force);fz=max(0.,force[0]*normal[2]);guide=robot_geom in self.guides;tire=body in self.wheels
   if guide and c.pos[2]>self.floor+1e-4:
    vertical+=fz;wall+=force[0]*np.linalg.norm(normal[:2])
    world_force=(1. if b1==0 else -1.)*np.asarray(c.frame).reshape(3,3).T@force[:3]
    moment+=float(np.cross(np.asarray(c.pos)-d.subtree_com[self.base],world_force)@np.cross([0.,0.,1.],forward))
    if normal[2]>.7 and force[0]>0.:top=float(c.pos[2]);self.top=top
   if tire:wheel_vertical[body]+=fz
   if tire and normal[2]>.7 and force[0]>1.:
    wheel_up[body]=True
    wheel_top[body]=bool(self.top is not None and abs(c.pos[2]-self.top)<.005)
   if tire and abs(normal[2])<.5 and force[0]>1.:wheel_wall[body]=True
   if tire and abs(normal[2])<.2 and abs(normal@forward)>.8 and force[0]>1.:
    n=normal.copy();n[2]=0.;n/=np.linalg.norm(n);n*=np.sign(n@forward);self.edge=(np.asarray(c.pos).copy(),n)
   if guide and force[0]>1.:events.append(dict(geom=m.geom(robot_geom).name,normal=normal.tolist(),point=np.asarray(c.pos).tolist(),force=float(force[0])))
  result=dict(guide_vertical_n=float(vertical),guide_pitch_moment_nm=float(moment),guide_horizontal_n=float(wall),top_z_relative=None if self.top is None else self.top-float(pos[2]),guide_events=events,edge_valid=self.edge is not None,wheel_odometry_valid=[wheel_up[b]and not wheel_wall[b]for b in sorted(self.wheels)],wheel_top_supported=[wheel_top[b]for b in sorted(self.wheels)],wheel_vertical_n=[float(wheel_vertical[b])for b in sorted(self.wheels)],wheel_wall=[wheel_wall[b]for b in sorted(self.wheels)],accel_world=(R@d.sensor('native_teacher_accel').data).tolist())
  if self.edge is not None:
   point,n=self.edge;den=max(.1,float(n@forward));result['wheel_edge_distance']=np.array([float((point-d.xpos[b])@n)/den for b in sorted(self.wheels)]).tolist();result['edge_point_relative']=(point-pos).tolist();result['edge_normal']=n.tolist()
  return result

 def observe_substep(self):
  self.window.append(self.instant_sample())
 def sample(self):
  now=self.instant_sample()
  if not self.window:return now
  window=self.window;self.window=[]
  for key in ['guide_vertical_n','guide_horizontal_n','guide_pitch_moment_nm','wheel_vertical_n','accel_world']:
   mean=np.mean([x[key]for x in window],axis=0);now[key]=mean.tolist()if isinstance(mean,np.ndarray)else float(mean)
  now['wheel_top_supported']=[any(x['wheel_top_supported'][i]for x in window)and now['wheel_vertical_n'][i]>1. for i in range(2)]
  now['wheel_odometry_valid']=[any(x['wheel_odometry_valid'][i]for x in window)and not any(x['wheel_wall'][i]for x in window)for i in range(2)]
  R=self.d.xmat[self.base].reshape(3,3);now['accel_interval_body']=(R.T@np.asarray(now['accel_world'])).tolist();now['integrated_substeps']=len(window)
  return now
