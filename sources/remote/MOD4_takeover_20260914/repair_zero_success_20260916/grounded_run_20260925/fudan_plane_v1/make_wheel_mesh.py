"""Replace only the two tire COLLIDERS with 24-sided cylindrical convex meshes."""
from pathlib import Path
import math, shutil
from pxr import Gf, Usd, UsdGeom, UsdPhysics
here=Path(__file__).resolve().parent
src=Path('/home/egde/rl_candidates/MOD4_takeover_20260914/repair_1536_20260915/asset/robot_tireload12_mat3.usd')
dst=here/'asset'/'robot_wheel_convex24.usd'
shutil.copy2(src,dst)
stage=Usd.Stage.Open(str(dst))
N=24
r=0.0637
half_width=0.010
for side in ('left','right'):
 path='/Robot/links/'+side+'_wheel/'+side+'_tire'
 prim=stage.GetPrimAtPath(path)
 assert prim and prim.GetTypeName()=='Cylinder',path
 prim.SetTypeName('Mesh')
 for key in ('axis','radius','height'):
  prim.RemoveProperty(key)
 points=[]
 for y in (-half_width,half_width):
  for i in range(N):
   theta=2*math.pi*i/N
   points.append(Gf.Vec3f(r*math.cos(theta),y,r*math.sin(theta)))
 counts=[];indices=[]
 for i in range(N):
  j=(i+1)%N
  counts.append(4);indices += [i,j,N+j,N+i]
 counts += [N,N]
 indices += list(reversed(range(N))) + list(range(N,2*N))
 mesh=UsdGeom.Mesh(prim)
 mesh.CreatePointsAttr(points)
 mesh.CreateFaceVertexCountsAttr(counts)
 mesh.CreateFaceVertexIndicesAttr(indices)
 mesh.CreateSubdivisionSchemeAttr('none')
 mesh.CreateExtentAttr([Gf.Vec3f(-r,-half_width,-r),Gf.Vec3f(r,half_width,r)])
 prim.GetAttribute('xformOp:orient').Set(Gf.Quatf(1,Gf.Vec3f(0,0,0)))
 api=UsdPhysics.MeshCollisionAPI.Apply(prim)
 api.CreateApproximationAttr('convexHull')
stage.GetRootLayer().Save()
for side in ('left','right'):
 p=stage.GetPrimAtPath('/Robot/links/'+side+'_wheel/'+side+'_tire')
 assert 'PhysicsCollisionAPI' in p.GetAppliedSchemas()
 assert UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get()=='convexHull'
print(dst)
