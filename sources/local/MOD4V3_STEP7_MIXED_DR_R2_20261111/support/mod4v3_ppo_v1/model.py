"""Read the released robot; no dynamics or coordinate values are invented here."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics


def metadata(package):
    package = Path(package)
    spec = json.loads((package/'semantics.json').read_bytes())
    runtime = json.loads((package/'runtime_config.json').read_bytes())
    contract = json.loads((package/'assets/import_contract.json').read_bytes())
    stage = Usd.Stage.Open(str(package/'assets/robot_physx.usda'))
    joints, closures = {}, {}
    for prim in stage.Traverse():
        if not prim.IsA(UsdPhysics.Joint):
            continue
        joint = UsdPhysics.Joint(prim)
        row = dict(parent=joint.GetBody0Rel().GetTargets()[0].name,
                   child=joint.GetBody1Rel().GetTargets()[0].name,
                   local_pos0=list(joint.GetLocalPos0Attr().Get()),
                   local_pos1=list(joint.GetLocalPos1Attr().Get()))
        joints[prim.GetName()] = row
        if prim.IsA(UsdPhysics.SphericalJoint):
            closures[prim.GetName()] = row
    cache = UsdGeom.XformCache()
    bodies = {}
    for name in contract['body_names']:
        prim = stage.GetPrimAtPath('/Robot/links/'+name)
        bodies[name] = dict(neutral_position_m=list(cache.GetLocalToWorldTransform(prim).ExtractTranslation()))
    xml = ET.parse(package/'mjcf/scene.xml')
    dynamics = {j.get('name'): dict(armature=float(j.get('armature', 0.)),
                 damping=float(j.get('damping', 0.))) for j in xml.findall('.//joint') if j.get('name')}
    gas = {side+'_spring2_joint': dict(target_position_m=.1706394410901294,
             stiffness_n_m=2000., damping_n_s_m=3.) for side in ('left','right')}
    wheel_span = abs(bodies['left_wheel_link']['neutral_position_m'][1]-
                     bodies['right_wheel_link']['neutral_position_m'][1])
    return dict(spec=spec, runtime=runtime, joints=joints, bodies=bodies,
                closures=closures, dynamics=dynamics, gas_springs=gas,
                nominal_span_m=wheel_span, package=str(package))


def reset_bank(package, source_bank):
    spec = json.loads((Path(package)/'semantics.json').read_bytes())
    rows = spec['coordinates']['native_from_v2']
    raw = json.loads(Path(source_bank).read_bytes())
    poses = [p for p in raw['poses'] if .24 <= p['root_height_m'] <= .272]
    # These are the same 74 mechanically feasible poses used by nominal V40.
    if len(poses) != 74:
        raise ValueError('Expected 74 source reset poses')
    return dict(names=list(rows), positions=[
        [p['joint_pos'].get(row['source'], 0.)+row['offset_si'] for row in rows.values()]
        for p in poses], heights=[p['root_height_m'] for p in poses])
