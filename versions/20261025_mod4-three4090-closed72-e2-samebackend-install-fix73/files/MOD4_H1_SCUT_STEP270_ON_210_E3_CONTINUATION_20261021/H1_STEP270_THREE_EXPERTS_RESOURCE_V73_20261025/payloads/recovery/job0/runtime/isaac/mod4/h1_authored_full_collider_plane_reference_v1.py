"""Exact authored primitive/mesh support against Plane; actual poses, no physics mutation."""
import torch
def body_world_z_row(q):
 x,y,z,w=q.unbind(-1);return torch.stack((2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1)
def evaluate(pos,quat,shapes):
 device=pos.device;ids=torch.as_tensor([s['body_index'] for s in shapes],device=device);rz=body_world_z_row(quat[:,ids]);L=torch.as_tensor([s['linear_body_from_shape'] for s in shapes],device=device,dtype=pos.dtype);t=torch.as_tensor([s['origin_body_m'] for s in shapes],device=device,dtype=pos.dtype);axis=torch.as_tensor([s.get('axis',2) for s in shapes],device=device);row=torch.einsum('nsi,sij->nsj',rz,L);center=pos[:,ids,2]+torch.einsum('nsi,si->ns',rz,t);result=[]
 for i,s in enumerate(shapes):
  r=row[:,i];kind=s['type']
  if kind=='Cube':extent=r.abs().sum(-1)*s['size']*.5
  elif kind in ('Cylinder','Capsule'):
   axial=r[:,s['axis']].abs();norm2=(r*r).sum(-1);radial=(norm2-axial*axial).clamp_min(0).sqrt();extent=axial*s['height']*.5+s['radius']*(norm2.sqrt() if kind=='Capsule' else radial)
  elif kind=='Sphere':extent=(r*r).sum(-1).sqrt()*s['radius']
  elif kind=='Mesh':
   points=torch.as_tensor(s['points'],device=device,dtype=pos.dtype);result.append(center[:,i]+(r@points.T).amin(-1));continue
  else:raise ValueError('Unsupported collider, UNKNOWN rather than a proxy')
  result.append(center[:,i]-extent)
 return torch.stack(result,-1)
def extract(stage,robot_path,body_names):
 from pxr import Usd,UsdGeom,UsdPhysics
 import numpy as np
 root=stage.GetPrimAtPath(robot_path);cache=UsdGeom.XformCache();rows=[]
 for prim in Usd.PrimRange(root,Usd.TraverseInstanceProxies()):
  if not prim.HasAPI(UsdPhysics.CollisionAPI):continue
  body=prim
  while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
  if not body or body.GetName() not in body_names:raise ValueError('Unmapped collision rigid body')
  relative=cache.GetLocalToWorldTransform(prim)*cache.GetLocalToWorldTransform(body).GetInverse();col=np.asarray(relative,dtype=np.float64).T;row=dict(path=str(prim.GetPath()),body=body.GetName(),body_index=body_names.index(body.GetName()),type=prim.GetTypeName(),linear_body_from_shape=col[:3,:3].tolist(),origin_body_m=col[:3,3].tolist())
  kind=row['type']
  if kind=='Cube':row['size']=float(UsdGeom.Cube(prim).GetSizeAttr().Get())
  elif kind in ('Cylinder','Capsule'):
   shape=UsdGeom.Cylinder(prim) if kind=='Cylinder' else UsdGeom.Capsule(prim);row.update(radius=float(shape.GetRadiusAttr().Get()),height=float(shape.GetHeightAttr().Get()),axis={'X':0,'Y':1,'Z':2}[str(shape.GetAxisAttr().Get())])
  elif kind=='Sphere':row['radius']=float(UsdGeom.Sphere(prim).GetRadiusAttr().Get())
  elif kind=='Mesh':row['points']=np.asarray(UsdGeom.Mesh(prim).GetPointsAttr().Get(),dtype=np.float64).tolist();assert row['points']
  else:raise ValueError('Unsupported actual authored collider '+kind)
  rows.append(row)
 if not rows:raise ValueError('No collision source shapes')
 return rows
