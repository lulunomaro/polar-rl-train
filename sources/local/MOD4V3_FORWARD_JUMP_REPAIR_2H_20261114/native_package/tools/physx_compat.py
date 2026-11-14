"""OmniPhysics finite-angle encoding; the semantic USD remains the sublayer.

The current project runtime cannot use infinite revolute mimic bounds. Only
open ends are encoded as 1e20 degree sentinels in this optional target wrapper.
Finite CAD stops and all physical prims remain inherited from robot.usd.
"""
from pathlib import Path
import math
from pxr import Usd,UsdPhysics,UsdGeom

from build import write_json,sha


def build_wrapper(package):
    package=Path(package)
    path=package/'assets/robot_physx.usda'
    stage=Usd.Stage.CreateNew(str(path))
    stage.GetRootLayer().subLayerPaths=['robot.usd']
    stage.SetDefaultPrim(stage.GetPrimAtPath('/Robot'))
    UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
    rows=[]
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.RevoluteJoint):
            for key in ['physics:lowerLimit','physics:upperLimit']:
                a=prim.GetAttribute(key);value=a.Get()
                if value is not None and not math.isfinite(float(value)):
                    replacement=math.copysign(1e20,float(value));a.Set(replacement)
                    rows.append(dict(joint=prim.GetName(),attribute=key,
                        old='-inf'if value<0 else'inf',new_degrees=replacement))
    root=stage.GetDefaultPrim()
    root.SetCustomDataByKey('mod4v3:PhysXFiniteAngleEncoding',True)
    root.SetCustomDataByKey('mod4v3:PhysXNativeDynamicsVerified',False)
    stage.GetRootLayer().Save()
    report=dict(schema='mod4v3.physx_encoding.v1',source='assets/robot.usd',target='assets/robot_physx.usda',
        source_sha256=sha(package/'assets/robot.usd'),wrapper_sha256=sha(path),
        open_end_numeric_encoding_only=True,sentinel_degrees=1e20,changed_ends=rows,
        actual_finite_CAD_stops_changed=False,mass_geometry_or_passive_forces_changed=False,
        native_PhysX_dynamics_verified=False,
        semantic_adapter_and_runtime_config_still_required=True)
    write_json(package/'PHYSX_COMPATIBILITY.json',report)
    return report
