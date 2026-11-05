"""PhysX's documented unwrapped-coordinate encoding for continuous hinges.

Finite1e20-degree sentinels represent open endpoints; no reachable mechanical
hard angle is introduced. Original true one-sided stops and mimic are retained.
"""
from pathlib import Path
import hashlib,json,math,time
from pxr import Usd,UsdPhysics

ROOT=Path(__file__).resolve().parent
SOURCE=Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/assets/robot.usd')
DEST=ROOT/'physx_finite_representation.usda'
if __name__=='__main__':
    assert not DEST.exists()
    stage=Usd.Stage.CreateNew(str(DEST));stage.GetRootLayer().subLayerPaths=[str(SOURCE).replace('\\','/')]
    stage.SetDefaultPrim(stage.GetPrimAtPath('/Robot'));rows=[]
    for prim in stage.Traverse():
        if prim.GetTypeName()!='PhysicsRevoluteJoint':continue
        joint=UsdPhysics.RevoluteJoint(prim)
        lo,hi=float(joint.GetLowerLimitAttr().Get()),float(joint.GetUpperLimitAttr().Get())
        before=[lo if math.isfinite(lo)else None,hi if math.isfinite(hi)else None]
        if not math.isfinite(lo):joint.CreateLowerLimitAttr(-1e20)
        if not math.isfinite(hi):joint.CreateUpperLimitAttr(1e20)
        if None in before:rows.append(dict(path=str(prim.GetPath()),physical_degree_bounds=before,
            encoded_degree_bounds=[float(joint.GetLowerLimitAttr().Get()),float(joint.GetUpperLimitAttr().Get())]))
    stage.GetRootLayer().Save()
    raw=DEST.read_bytes();(ROOT/'reports/FINITE_REPRESENTATION_BUILD.json').write_text(json.dumps(dict(
        epoch=time.time(),source=str(SOURCE),source_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        path=str(DEST),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),rows=rows,
        reason='OmniPhysics110 mimic requires finite revolute limits; large finite sentinels select unwrapped coordinate',
        documentation='https://docs.omniverse.nvidia.com/kit/docs/omni_physics/110.0/dev_guide/rigid_bodies_articulations/articulations.html',
        hardware_angular_box=False,true_stops_changed=False,source_asset_modified=False,
        native_validation_pending=True),indent=2),encoding='utf8')
    print(json.dumps(dict(path=str(DEST),SHA=hashlib.sha256(raw).hexdigest())))
