from pathlib import Path
import sys,json,hashlib
from pxr import Usd,UsdPhysics,UsdShade
from fixed_material_pool import pool_fixed_materials,signature,POOL
asset=Path('/home/egde/fangzhen_linux/incoming/_from_target_20260928/robot.usd')
assert hashlib.sha256(asset.read_bytes()).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
stage=Usd.Stage.CreateInMemory();roots=[]
for i in range(2):
 p='/World/envs/env_'+str(i)+'/Robot';stage.DefinePrim(p).GetReferences().AddReference(str(asset));roots.append(p)

def plant(root):
 result={}
 for prim in Usd.PrimRange(stage.GetPrimAtPath(root)):
  if '/PhysicsMaterials' in str(prim.GetPath()):continue
  result[str(prim.GetPath())]=dict(type=prim.GetTypeName(),schemas=list(prim.GetAppliedSchemas()),
   attrs={a.GetName():str(a.Get()) for a in prim.GetAttributes()},
   rels={r.GetName():[str(t) for t in r.GetTargets()] for r in prim.GetRelationships() if r.GetName()!='material:binding:physics'})
 return result

def materials(root):
 out={}
 for prim in Usd.PrimRange(stage.GetPrimAtPath(root)):
  if prim.HasAPI(UsdPhysics.CollisionAPI):
   mat,_=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial('physics')
   assert mat,prim.GetPath();out[str(prim.GetPath())]=signature(mat.GetPrim())
 return out

before=[plant(r) for r in roots];mbefore=[materials(r) for r in roots]
proofs=[pool_fixed_materials(stage,r) for r in roots]
assert before==[plant(r) for r in roots]
assert mbefore==[materials(r) for r in roots]
assert len(mbefore[0])==len(mbefore[1])==34
active=[str(p.GetPath()) for p in stage.Traverse() if p.HasAPI(UsdPhysics.MaterialAPI)]
assert len(active)==4,active
assert len([p for p in active if p.startswith(POOL)])==2
assert len([p for p in active if p.endswith('/drive_tire')])==2
print(json.dumps({'passed':True,'actual_USD_SHA256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'all34_collider_material_values_exact':True,'all_robot_nonmaterial_attrs_and_relationships_exact':True,
 'two_robot_active_material_count':len(active),'private_wheels_retained':True,'asset_bytes_unchanged':True,
 'active_materials':active,'GPU_or_Kit_started':False,'PPO_updates':0}))
