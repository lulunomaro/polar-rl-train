"""Read-only MuJoCo platform contacts at every2.5ms physics step."""
import json
import numpy as np
import mujoco as mj
class GuideDiagnostics:
 def __init__(self,m,platform,height):
  self.m=m;self.platform=platform;self.height=height;self.events=[];self.frames=[]
  self.guides=[i for i in range(m.ngeom)if 'guide' in m.geom(i).name.lower()]
 def tick(self,d,frame,command):
  for i in range(d.ncon):
   c=d.contact[i];g1,g2=int(c.geom1),int(c.geom2)
   if self.platform not in (g1,g2):continue
   gid=g2 if g1==self.platform else g1;bid=int(self.m.geom_bodyid[gid]);name=self.m.body(bid).name;low=name.lower()
   force=np.zeros(6);mj.mj_contactForce(self.m,d,i,force)
   if force[0]<=1.:continue
   normal=np.asarray(c.frame).reshape(3,3)[0]*(1. if g1==self.platform else -1.)
   category='guide'if 'guide'in low else('main_wheel'if 'wheel'in low else('base_or_nose'if ('base'in low or 'head'in low or'nose'in low)else'other_link'))
   self.events.append(dict(t=float(d.time),frame=frame,category=category,body=name,geom=self.m.geom(gid).name,normal_force_N=float(force[0]),contact_xyz=np.asarray(c.pos).tolist(),body_center_xyz=d.xpos[bid].tolist(),geom_center_xyz=d.geom_xpos[gid].tolist(),normal_xyz=normal.tolist(),world_vx=float(d.qvel[0]),command_vx=float(command),wall_contact=bool(abs(normal[0])>.5 and c.pos[2]<self.height+.02)))
 def policy_frame(self,d,frame,command):
  centers={self.m.geom(i).name:d.geom_xpos[i].tolist()for i in self.guides}
  self.frames.append(dict(frame=frame,t=float(d.time),root_xyz=d.qpos[:3].tolist(),guide_centers=centers,command_vx=float(command),world_vx=float(d.qvel[0])))
 def finish(self,dest,trace):
  guides=[e for e in self.events if e['category']=='guide'];walls=[e for e in guides if e['wall_contact']and e['normal_force_N']>5.];stalled={e['frame']for e in walls if abs(e['world_vx'])<.05 and e['command_vx']>.1}
  row=dict(any_platform_contact=bool(self.events),first_any_platform_contact=self.events[0]if self.events else None,first_guide_platform_contact=guides[0]if guides else None,first_guide_wall_contact=walls[0]if walls else None,guide_wall_contact_policy_frames=len({e['frame']for e in walls}),guide_wall_stall_seconds=len(stalled)*.02,maximum_guide_wall_force_N=max((e['normal_force_N']for e in walls),default=0.),front_base_contact_samples=sum(e['category']=='base_or_nose'for e in self.events),contact_diagnostic_physics_dt_s=.0025)
  if self.frames:row['last_guide_centers_xyz']=self.frames[-1]['guide_centers']
  with (dest/'platform_contacts.jsonl').open('w',encoding='utf8')as f:
   for e in self.events:f.write(json.dumps(e)+'\n')
  (dest/'GUIDE_DIAGNOSTICS.json').write_text(json.dumps(dict(summary=row,policy_frames=self.frames),indent=2)+'\n')
  return row
