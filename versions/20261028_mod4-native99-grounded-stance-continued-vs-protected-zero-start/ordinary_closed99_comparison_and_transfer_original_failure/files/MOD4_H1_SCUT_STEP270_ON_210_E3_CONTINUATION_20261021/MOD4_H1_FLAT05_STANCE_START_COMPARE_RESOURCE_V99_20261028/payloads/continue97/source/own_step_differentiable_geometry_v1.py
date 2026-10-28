"""Differentiable recorded own30-joint tree FK and exact wheel mesh supports.

Only source JSON constants; no USD, SDK, model, physics or IK queries.
Uses actual imported X axes/T0/T1 and every actual q; never imposes an ideal
drive==hip mimic relation. Closed-loop compliance is a measured limitation.
"""
import torch
from torch import nn
def require(v,msg):
 if not bool(v):raise ValueError(msg)
def qmat(q):
 q=q/q.norm(dim=-1,keepdim=True).clamp_min(1e-12);w,x,y,z=q.unbind(-1)
 return torch.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1).reshape(*q.shape[:-1],3,3)
def mv(R,x):return (R@x.unsqueeze(-1)).squeeze(-1)
class OwnStepWheelGeometry(nn.Module):
 def __init__(self,contract,geometry,joint_names):
  super().__init__();self.names=tuple(joint_names);self.body_names=tuple(geometry['body_names']);self.wheel_names=('left_wheel','right_wheel')
  require(len(self.names)==30 and len(set(self.names))==30 and set(self.names)==set(contract['joints']),'named physical30 required')
  require(self.body_names[0]=='chassis' and len(self.body_names)==31,'recorded own31body root/order')
  self.rows=[];seen={'chassis'};bychild={r['child']:(name,r) for name,r in contract['joints'].items()}
  for i,child in enumerate(self.body_names[1:]):
   name,row=bychild[child];require(row['parent'] in seen,'authored topological tree required');seen.add(child)
   require(row['type'] in ('hinge','slide'),'only pinned X hinge/slide')
   self.rows.append((name,row['parent'],child,row['type']))
   for key,values in [('p0',row['local_pos0']),('p1',row['local_pos1'])]:self.register_buffer(key+str(i),torch.tensor(values,dtype=torch.float32))
   for key,values in [('R0',row['local_rot0']),('R1T',row['local_rot1'])]:
    R=qmat(torch.tensor(values,dtype=torch.float32));self.register_buffer(key+str(i),R.T if key=='R1T' else R)
  for i,name in enumerate(self.wheel_names):
   shapes=[x for x in geometry['shapes'] if x['body']==name];require(len(shapes)==1 and shapes[0]['type']=='Mesh','one actual recorded wheel mesh each')
   shape=shapes[0];points=torch.tensor(shape['points'],dtype=torch.float32);linear=torch.tensor(shape['linear_body_from_shape'],dtype=torch.float32);origin=torch.tensor(shape['origin_body_m'],dtype=torch.float32)
   points=points@linear.T+origin;require(points.ndim==2 and points.shape[-1]==3 and torch.isfinite(points).all(),'finite recorded wheel support points')
   self.register_buffer('points'+str(i),points)
 def forward(self,state):
  require(len(state)==7,'native base7 state required');p,R,v,w,q,dq,aux=state
  require(q.shape[-1]==30 and dq.shape==q.shape and aux.shape[-1]==54,'physical30/dynamic54 state')
  poses={'chassis':(p,R,v,w)}
  for i,(name,parent,child,kind) in enumerate(self.rows):
   pp,PR,pv,pw=poses[parent];R0=getattr(self,'R0'+str(i));R1T=getattr(self,'R1T'+str(i));p0=getattr(self,'p0'+str(i));p1=getattr(self,'p1'+str(i))
   j=self.names.index(name);a=q[...,j];ad=dq[...,j];A=PR@R0;axis=A[...,0];anchor=mv(PR,p0.expand_as(pp))
   if kind=='hinge':
    c,s=a.cos(),a.sin();zero=torch.zeros_like(a);one=torch.ones_like(a)
    motion=torch.stack((one,zero,zero,zero,c,-s,zero,s,c),-1).reshape(*a.shape,3,3)
    CR=A@motion@R1T;cw=pw+axis*ad[...,None];offset=mv(CR,p1.expand_as(pp));cp=pp+anchor-offset;cv=pv+torch.cross(pw,anchor,dim=-1)-torch.cross(cw,offset,dim=-1)
   else:
    CR=A@R1T;cw=pw;offset=anchor+axis*a[...,None]-mv(CR,p1.expand_as(pp));cp=pp+offset;cv=pv+torch.cross(pw,offset,dim=-1)+axis*ad[...,None]
   poses[child]=(cp,CR,cv,cw)
  lows=[];highs=[];centres=[];velocities=[]
  for i,name in enumerate(self.wheel_names):
   bp,bR,bv,bw=poses[name];points=getattr(self,'points'+str(i));world=(bR@points.T).transpose(-1,-2)+bp[...,None,:]
   local_centre=points.mean(0);offset=mv(bR,local_centre.expand_as(bp));centres.append(bp+offset);velocities.append(bv+torch.cross(bw,offset,dim=-1));lows.append(world.amin(-2));highs.append(world.amax(-2))
  return dict(low=torch.stack(lows,-2),high=torch.stack(highs,-2),centre=torch.stack(centres,-2),centre_velocity=torch.stack(velocities,-2),root_velocity=v,root_angular_velocity=w,body_position=torch.stack([poses[n][0] for n in self.body_names],-2),body_rotation=torch.stack([poses[n][1] for n in self.body_names],-3))
