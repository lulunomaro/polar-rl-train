"""Own already-loaded stage collision points only; no stage open or PhysX view.

This measures authored mesh support, not cooked contact shape/depth. Missing,
ambiguous, non-mesh or bounded-query cases return UNKNOWN without a task gate.
"""
import hashlib
import numpy as np
MAX_PRIMS=10000
MAX_MESHES=64
MAX_POINTS=65536


def unknown(name,reason,**details):
 return dict(name=name,status='UNKNOWN',reason=reason,**details),None


def loaded_stage_wheel(stage,robot_path,name):
 """Exactly one bounded metadata query per wheel; each mesh.points Get once."""
 from pxr import Usd,UsdGeom,UsdPhysics,Gf
 root=stage.GetPrimAtPath(robot_path)
 if not root or not root.IsValid():return unknown(name,'OWN_ROBOT_ROOT_ABSENT',robot_path=robot_path)
 candidates=[];visited=0
 for prim in Usd.PrimRange(root,Usd.TraverseInstanceProxies()):
  visited+=1
  if visited>MAX_PRIMS:return unknown(name,'OWN_PRIM_QUERY_BOUND',visited=visited)
  if prim.GetName()==name and prim.HasAPI(UsdPhysics.RigidBodyAPI):candidates.append(prim)
 if len(candidates)!=1:return unknown(name,'RIGID_BODY_PATH_MISSING_OR_AMBIGUOUS',matches=[str(p.GetPath()) for p in candidates])
 body=candidates[0];cache=UsdGeom.XformCache(Usd.TimeCode.Default())
 to_body=cache.GetLocalToWorldTransform(body).GetInverse();points=[];meshes=[];count=0;nonmesh=[]
 for prim in Usd.PrimRange(body,Usd.TraverseInstanceProxies()):
  if not prim.HasAPI(UsdPhysics.CollisionAPI):continue
  enabled=prim.GetAttribute('physics:collisionEnabled')
  if enabled and enabled.Get() is False:continue
  if not prim.IsA(UsdGeom.Mesh):nonmesh.append(str(prim.GetPath()));continue
  if len(meshes)>=MAX_MESHES:return unknown(name,'COLLISION_MESH_QUERY_BOUND',meshes=len(meshes))
  value=UsdGeom.Mesh(prim).GetPointsAttr().Get()  #ONE metadata attribute read.
  if value is None or len(value)==0:return unknown(name,'EMPTY_COLLISION_MESH_POINTS',mesh=str(prim.GetPath()))
  count+=len(value)
  if count>MAX_POINTS:return unknown(name,'COLLISION_POINTS_QUERY_BOUND',points=count)
  to_world=cache.GetLocalToWorldTransform(prim)
  local=np.asarray([tuple(to_body.Transform(to_world.Transform(Gf.Vec3d(*p)))) for p in value],dtype=np.float32)
  if not np.isfinite(local).all():return unknown(name,'NONFINITE_AUTHORED_METADATA',mesh=str(prim.GetPath()))
  points.append(local);meshes.append(dict(path=str(prim.GetPath()),point_count=len(value),points_attribute_reads=1,
    mesh_local_to_stage=repr(to_world),body_stage_to_local=repr(to_body)))
 if nonmesh:return unknown(name,'NON_MESH_COLLIDER_NOT_RECONSTRUCTED',paths=nonmesh,mesh_count=len(meshes))
 if not points:return unknown(name,'NO_ENABLED_COLLISION_MESH',body_path=str(body.GetPath()))
 support=np.concatenate(points,axis=0).astype(np.float32,copy=False)
 return dict(name=name,status='AUTHORED_COLLISION_MESH_POINTS',body_path=str(body.GetPath()),
  robot_path=robot_path,mesh_count=len(meshes),point_count=len(support),meshes=meshes,
  body_local_F32_point_SHA=hashlib.sha256(support.tobytes()).hexdigest(),
  source='Current already-loaded own stage;relative authored mesh transforms',
  cooked_shape_or_contact_depth=False,stage_open_calls=0,PhysX_getter_calls=0),support


def load_own_wheels(stage,robot_path):
 rows=[];support=[]
 for name in ('left_wheel','right_wheel'):
  try:row,points=loaded_stage_wheel(stage,robot_path,name)
  except Exception as exc:row,points=unknown(name,'STAGE_METADATA_QUERY_EXCEPTION',error=type(exc).__name__+': '+str(exc))
  rows.append(row);support.append(points)
 return rows,support


def authored_bottom(points,position,quat_xyzw,plane_z):
 if points is None:return None
 q=np.asarray(quat_xyzw,dtype=np.float32);p=np.asarray(position,dtype=np.float32)
 norm=float(np.linalg.norm(q))
 if not np.isfinite(q).all() or not np.isfinite(p).all() or norm<=0:return None
 q=q/np.float32(norm);v=np.asarray(points,dtype=np.float32)
 t=2*np.cross(np.broadcast_to(q[:3],v.shape),v)
 rotated=v+q[3]*t+np.cross(np.broadcast_to(q[:3],v.shape),t)
 return float(np.min(rotated[:,2])+p[2]-np.float32(plane_z))
