"""Represent released continuous/one-sided hinges as equivalent one-axis D6 joints.

Only this task's new overlay is authored. No finite artificial angular box is added.
The other five axes are locked and original joint frames, mimic and gas are retained.
"""
from pathlib import Path
import hashlib,json,math,time
from pxr import Usd,UsdPhysics,Sdf

HERE=Path(__file__).resolve().parent
SOURCE=Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/assets/robot.usd')
DEST=HERE/'physx_representation.usda'

if __name__=='__main__':
    assert not DEST.exists()
    stage=Usd.Stage.CreateNew(str(DEST))
    stage.GetRootLayer().subLayerPaths=[str(SOURCE).replace('\\','/')]
    stage.SetDefaultPrim(stage.GetPrimAtPath('/Robot'))
    rows=[]
    for prim in list(stage.Traverse()):
        if prim.GetTypeName()!='PhysicsRevoluteJoint':continue
        hinge=UsdPhysics.RevoluteJoint(prim)
        low,high=float(hinge.GetLowerLimitAttr().Get()),float(hinge.GetUpperLimitAttr().Get())
        if math.isfinite(low)and math.isfinite(high):continue
        axis=str(hinge.GetAxisAttr().Get());rot='rot'+axis
        drive=UsdPhysics.DriveAPI(prim,'angular')
        attrs={k:Get() for k,Get in []}
        if drive:
            attrs={a.GetName().split(':')[-1]:a.Get()for a in prim.GetAttributes()
                   if a.GetName().startswith('drive:angular:physics:')}
        prim.SetTypeName('PhysicsJoint')
        for dof in ['transX','transY','transZ','rotX','rotY','rotZ']:
            if dof==rot:continue
            limit=UsdPhysics.LimitAPI.Apply(prim,dof)
            limit.CreateLowAttr(1.);limit.CreateHighAttr(-1.)
        if math.isfinite(low)or math.isfinite(high):
            limit=UsdPhysics.LimitAPI.Apply(prim,rot)
            limit.CreateLowAttr(low);limit.CreateHighAttr(high)
        if drive:
            prim.RemoveAPI(UsdPhysics.DriveAPI,'angular')
            UsdPhysics.DriveAPI.Apply(prim,rot)
            for name,value in attrs.items():
                source=prim.GetAttribute('drive:angular:physics:'+name)
                prim.CreateAttribute('drive:'+rot+':physics:'+name,source.GetTypeName()).Set(value)
        rows.append(dict(path=str(prim.GetPath()),original_type='PhysicsRevoluteJoint',
            new_type='PhysicsJoint',free_axis=rot,low=low if math.isfinite(low)else None,
            high=high if math.isfinite(high)else None,other_five_axes_locked=True))
    stage.GetRootLayer().Save()
    raw=DEST.read_bytes()
    (HERE/'reports/PHYSX_REPRESENTATION_BUILD.json').write_text(json.dumps(dict(epoch=time.time(),
        source=str(SOURCE),source_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        layer=str(DEST),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),rows=rows,
        source_asset_modified=False,artificial_finite_limits_added=False,
        validation='USD representation only; nativeSDK test required'),indent=2),encoding='utf8')
    print(json.dumps(dict(joints=len(rows),layer=str(DEST),SHA=hashlib.sha256(raw).hexdigest())))
