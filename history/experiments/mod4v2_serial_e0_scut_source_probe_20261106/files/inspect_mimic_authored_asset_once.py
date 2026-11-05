"""Read actual authored joint/API metadata from the current USD; no SDK/simulation/weights."""
from pathlib import Path
import json
from pxr import Usd,UsdPhysics
D=Path(__file__).resolve().parent;out=D/'MIMIC_AUTHORED_USD_METADATA_V1.json';assert not out.exists();pkg=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60_PHYSX_REPR_V2/package';stage=Usd.Stage.Open(str(pkg/'assets/robot.usd'),load=Usd.Stage.LoadNone);assert stage
rows=[]
def value(v):
 if v is None or isinstance(v,(str,int,float,bool)):return v
 try:return[value(x)for x in v]
 except TypeError:return str(v)
for side in('left','right'):
 for suffix in('drive_hip_spin','drive_input_spin','hip','crank'):
  name=side+'_'+suffix;p=stage.GetPrimAtPath('/Robot/joints/'+name);assert p.IsValid();joint=UsdPhysics.RevoluteJoint(p);rows.append(dict(name=name,path=str(p.GetPath()),type=p.GetTypeName(),applied_schemas=p.GetAppliedSchemas(),axis=joint.GetAxisAttr().Get(),all_attributes={a.GetName():value(a.Get())for a in p.GetAttributes()},relationships={r.GetName():[str(x)for x in r.GetTargets()]for r in p.GetRelationships()}))
r=dict(kind='ACTUAL_SOURCE_USD_JOINT_SCHEMA_METADATA_NOT_COMPOSED_RUNTIME',asset=str(pkg/'assets/robot.usd'),large_asset_hash_operations=0,rows=rows,native_SDK_simulation_or_weights_opened=0,source_read_only=True);out.write_text(json.dumps(r,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(path=str(out),rows=[{k:x[k]for k in('name','applied_schemas','axis','relationships')}for x in rows]),indent=2))
