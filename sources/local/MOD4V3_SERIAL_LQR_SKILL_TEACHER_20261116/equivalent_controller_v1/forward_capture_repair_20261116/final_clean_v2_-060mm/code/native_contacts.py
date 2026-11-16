"""Translation-invariant contact-frame geometry for the simulation teacher.
Privileged teacher contact positions/forces are explicit. No absolute stair position,
terrain geom name, policy input, or c874 observation is used for control decisions.
"""
import numpy as np,mujoco as mj
from native_contact_latch import WheelContactLatch
class NativeContacts:
 def __init__(self,m,d,base,wheels,guides,radius):
  self.m,self.d,self.base=m,d,base;self.wheels=set(wheels);self.guides=set(guides);self.radius=radius;self.edge=None;self.top=None;self.window=[]
  self.floor=float(min(d.xpos[list(wheels),2])-radius)
  self.contact_latch=WheelContactLatch(len(wheels))
  self.contact_hysteresis=False
  self.contact_surfaces={b:{} for b in self.wheels}
  self.previous_wheel_velocity={b:np.zeros(3) for b in self.wheels}
  self.wheel_geoms={b:next(i for i in range(m.ngeom) if m.geom_bodyid[i]==b and m.geom_contype[i]) for b in self.wheels}
 def instant_sample(self):
  m,d=self.m,self.d;pos=d.xpos[self.base];R=d.xmat[self.base].reshape(3,3);forward=R[:,0].copy();forward[2]=0.;forward/=max(np.linalg.norm(forward),1e-9)
  vertical=wall=moment=0.;top=None;events=[];wheel_up={b:False for b in self.wheels};wheel_wall={b:False for b in self.wheels};wheel_top={b:False for b in self.wheels};wheel_vertical={b:0. for b in self.wheels}
  wheel_environment={b:False for b in self.wheels}
  wheel_velocity={}
  for b in self.wheels:
   jp=np.zeros((3,m.nv));jr=jp.copy();mj.mj_jacGeom(m,d,jp,jr,self.wheel_geoms[b]);wheel_velocity[b]=jp@d.qvel
  for i,c in enumerate(d.contact):
   g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2]);body=b2 if b1==0 else b1 if b2==0 else -1
   if body<0:continue
   robot_geom=g2 if b1==0 else g1;normal=(1. if b1==0 else -1.)*np.asarray(c.frame).reshape(3,3)[0];force=np.zeros(6);mj.mj_contactForce(m,d,i,force);fz=max(0.,force[0]*normal[2]);guide=robot_geom in self.guides;tire=body in self.wheels
   if guide and c.pos[2]>self.floor+1e-4:
    vertical+=fz;wall+=force[0]*np.linalg.norm(normal[:2])
    world_force=(1. if b1==0 else -1.)*np.asarray(c.frame).reshape(3,3).T@force[:3]
    moment+=float(np.cross(np.asarray(c.pos)-d.subtree_com[self.base],world_force)@np.cross([0.,0.,1.],forward))
    if normal[2]>.7 and force[0]>0.:top=float(c.pos[2]);self.top=top
   if tire:
    wheel_environment[body]=True
    wheel_vertical[body]+=fz
    terrain_geom=g1 if b1==0 else g2
    approach=max(0.,-float(self.previous_wheel_velocity[body]@normal),-float(wheel_velocity[body]@normal))
    # Same physical settling interval MuJoCo enforces for positive solref.
    # This estimates geometric engagement after a micro-separation; it does
    # not add contact force or mark a wall as valid rolling odometry.
    settling=max(2.*float(m.opt.timestep),float(c.solref[0]))
    release=approach*settling
    self.contact_surfaces[body][terrain_geom]=max(self.contact_surfaces[body].get(terrain_geom,0.),release)
   if tire and normal[2]>.7 and force[0]>1.:
    wheel_up[body]=True
    wheel_top[body]=bool(self.top is not None and abs(c.pos[2]-self.top)<.005)
   if tire and abs(normal[2])<.5 and force[0]>1.:wheel_wall[body]=True
   if tire and abs(normal[2])<.2 and abs(normal@forward)>.8 and force[0]>1.:
    n=normal.copy();n[2]=0.;n/=np.linalg.norm(n);n*=np.sign(n@forward);self.edge=(np.asarray(c.pos).copy(),n)
   if guide and force[0]>1.:events.append(dict(geom=m.geom(robot_geom).name,normal=normal.tolist(),point=np.asarray(c.pos).tolist(),force=float(force[0])))
  # Natural pitch time about the current wheel support line. This uses
  # native mass/inertia and the measured posture, not a fitted delay.
  pivot=np.mean(d.xpos[sorted(self.wheels)],axis=0);axis=np.cross([0.,0.,1.],forward)
  arm=d.xipos-pivot;principal=np.einsum('bij,bj->bi',d.ximat.reshape(-1,3,3).transpose(0,2,1),np.broadcast_to(axis,(m.nbody,3)))
  inertia=float(np.sum(m.body_inertia*principal**2)+np.sum(m.body_mass*(np.sum(arm*arm,axis=1)-(arm@axis)**2)))
  center=np.average(d.xipos,axis=0,weights=m.body_mass);height=float(center[2]-pivot[2])
  pitch_time=None if height<=0. else float(np.sqrt(inertia/(m.body_mass.sum()*abs(m.opt.gravity[2])*height)))
  result=dict(guide_vertical_n=float(vertical),guide_pitch_moment_nm=float(moment),guide_horizontal_n=float(wall),top_z_relative=None if self.top is None else self.top-float(pos[2]),guide_events=events,edge_valid=self.edge is not None,wheel_odometry_valid=[wheel_up[b]and not wheel_wall[b]for b in sorted(self.wheels)],wheel_top_supported=[wheel_top[b]for b in sorted(self.wheels)],wheel_vertical_n=[float(wheel_vertical[b])for b in sorted(self.wheels)],wheel_wall=[wheel_wall[b]for b in sorted(self.wheels)],accel_world=(R@d.sensor('native_teacher_accel').data).tolist())
  proximity={};details={}
  for b in sorted(self.wheels):
   nearby=False;rows=[]
   for surface,release in self.contact_surfaces[b].items():
    distance=float(mj.mj_geomDistance(m,d,self.wheel_geoms[b],surface,1.,None))
    nearby |= distance<=release
    rows.append(dict(surface=int(surface),distance_m=distance,release_m=float(release)))
   proximity[b]=nearby
   details[b]=rows
  result['wheel_environment_contact']=[wheel_environment[b] for b in sorted(self.wheels)]
  result['wheel_geometric_engagement']=[bool(wheel_environment[b] or proximity[b]) for b in sorted(self.wheels)]
  result['wheel_contact_geometry']=[details[b] for b in sorted(self.wheels)]
  result['wheel_geom_velocity']=[wheel_velocity[b].tolist() for b in sorted(self.wheels)]
  result['capture_pitch_time_s']=pitch_time
  result['base_z']=float(pos[2])
  mj.mj_subtreeVel(m,d)
  result['com_forward_speed']=float(d.subtree_linvel[self.base]@forward)
  result['com_relative']=(center-pos).tolist()
  if self.edge is not None:
   point,n=self.edge;den=max(.1,float(n@forward));result['com_edge_distance']=float((point-center)@n)/den;result['base_edge_distance']=float((point-pos)@n)/den;result['wheel_edge_distance']=np.array([float((point-d.xpos[b])@n)/den for b in sorted(self.wheels)]).tolist();result['edge_point_relative']=(point-pos).tolist();result['edge_normal']=n.tolist()
  return result

 def observe_substep(self):
  sample=self.instant_sample()
  engaged=sample['wheel_geometric_engagement'] if self.contact_hysteresis else sample['wheel_environment_contact']
  sample.update(self.contact_latch.update(engaged,float(self.m.opt.timestep)))
  self.previous_wheel_velocity={b:np.asarray(v) for b,v in zip(sorted(self.wheels),sample['wheel_geom_velocity'])}
  self.window.append(sample)
 def sample(self):
  now=self.instant_sample()
  now.update(self.contact_latch.snapshot())
  if not self.window:return now
  window=self.window;self.window=[]
  now['wheel_contact_history']=[dict(raw=x['wheel_environment_contact'],engaged=x['wheel_geometric_engagement'],confirmed=x['wheel_contact_confirmed'],absent_s=x['wheel_contact_absent_s']) for x in window]
  for key in ['guide_vertical_n','guide_horizontal_n','guide_pitch_moment_nm','wheel_vertical_n','accel_world']:
   mean=np.mean([x[key]for x in window],axis=0);now[key]=mean.tolist()if isinstance(mean,np.ndarray)else float(mean)
  now['wheel_top_supported']=[any(x['wheel_top_supported'][i]for x in window)and now['wheel_vertical_n'][i]>1. for i in range(2)]
  now['wheel_odometry_valid']=[any(x['wheel_odometry_valid'][i]for x in window)and not any(x['wheel_wall'][i]for x in window)for i in range(2)]
  R=self.d.xmat[self.base].reshape(3,3);now['accel_interval_body']=(R.T@np.asarray(now['accel_world'])).tolist();now['integrated_substeps']=len(window)
  return now
