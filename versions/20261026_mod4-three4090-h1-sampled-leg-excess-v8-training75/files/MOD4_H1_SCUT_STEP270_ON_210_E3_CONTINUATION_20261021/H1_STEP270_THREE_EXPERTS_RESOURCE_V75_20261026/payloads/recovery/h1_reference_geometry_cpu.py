import numpy as np
def support(pos,quat,shapes):
 # Rotate each basis vector via independent cross-product XYZW quaternion application.
 q=quat.astype(np.float64);a=q[...,:3];w=q[...,3:4];basis=np.broadcast_to(np.eye(3),q.shape[:-1]+(3,3));aa=a[...,None,:];t=2*np.cross(aa,basis);rotation_basis=basis+w[...,None,:]*t+np.cross(aa,t);zrow=rotation_basis[...,2]
 out=[]
 for s in shapes:
  rz=zrow[...,s['body_index'],:];L=np.asarray(s['linear_body_from_shape']);origin=np.asarray(s['origin_body_m']);shape_z=rz@L;center=pos[...,s['body_index'],2]+(rz*origin).sum(-1);kind=s['type']
  if kind=='Cube':
   corners=np.array([[x,y,z] for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)])*s['size'];value=center+(shape_z@corners.T).min(-1)
  elif kind=='Mesh':value=center+(shape_z@np.asarray(s['points']).T).min(-1)
  elif kind in ('Capsule','Cylinder'):
   axis=shape_z[...,s['axis']];r=np.linalg.norm(shape_z,axis=-1) if kind=='Capsule' else np.sqrt(np.maximum(0,(shape_z*shape_z).sum(-1)-axis*axis));value=center-np.abs(axis)*s['height']*.5-r*s['radius']
  else:raise ValueError('Unknown source shape')
  out.append(value)
 return np.stack(out,-1)
