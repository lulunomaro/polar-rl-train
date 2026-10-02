"""Positive and deliberately corrupted imports, plus runtime guard faults."""
from pathlib import Path
import sys, json, hashlib
from types import SimpleNamespace
import numpy as np
import torch
import mujoco
from pxr import Usd, Sdf, UsdGeom
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'isaac'))
from audit_import import audit_stage,RuntimeGuard,audit_runtime_parameters,CONTRACT
ASSET=ROOT/'isaac/robot.usd'
def fresh():
    s=Usd.Stage.Open(str(ASSET));s.SetEditTarget(s.GetSessionLayer());return s
valid=audit_stage(fresh());cases=[]
# Verify reference composition retargets all closure, mimic and filter relationships.
cloned=Usd.Stage.CreateInMemory();UsdGeom.SetStageMetersPerUnit(cloned,1.);UsdGeom.SetStageUpAxis(cloned,'Z')
clone_results=[]
for i in range(2):
    parent=UsdGeom.Xform.Define(cloned,f'/World/envs/env_{i}')
    parent.AddTranslateOp().Set((float(i)*2.,0.,0.))
    path=f'/World/envs/env_{i}/Robot'
    cloned.DefinePrim(path).GetReferences().AddReference(str(ASSET),'/Robot')
    clone_results.append(audit_stage(cloned,path))
def rejects(name,mutation,expected):
    s=fresh();mutation(s)
    try:audit_stage(s)
    except RuntimeError as e:
        assert expected in str(e),(name,str(e));cases.append(name)
    else:raise AssertionError('Missed corrupted import: '+name)
rejects('deleted_closure',lambda s:s.GetPrimAtPath('/Robot/closures/left_proximal_closure').SetActive(False),'MISSING CLOSURE')
rejects('closure_in_articulation',lambda s:s.GetPrimAtPath('/Robot/closures/left_distal_closure').GetAttribute('physics:excludeFromArticulation').Set(False),'outside articulation')
rejects('wrong_mimic_sign',lambda s:s.GetPrimAtPath('/Robot/joints/left_drive_hip_spin').GetAttribute('physxMimicJoint:rotX:gearing').Set(1.),'mimic gearing')
rejects('deleted_mimic',lambda s:s.GetPrimAtPath('/Robot/joints/left_drive_input_spin').RemoveAppliedSchema('PhysxMimicJointAPI:rotX'),'MISSING MIMIC')
rejects('wrong_joint_parent',lambda s:s.GetPrimAtPath('/Robot/joints/right_knee').GetRelationship('physics:body0').SetTargets(['/Robot/links/chassis']),'body0 topology')
rejects('wrong_wheel_mass',lambda s:s.GetPrimAtPath('/Robot/links/left_wheel').GetAttribute('physics:mass').Set(.1188),'mass')
rejects('missing_filter',lambda s:s.GetPrimAtPath('/Robot/links/left_thigh').GetRelationship('physics:filteredPairs').SetTargets([]),'collision filter missing')
rejects('gas_preload_zeroed',lambda s:s.GetPrimAtPath('/Robot/joints/left_gas_slide').GetAttribute('drive:linear:physics:targetPosition').Set(0.),'gas spring target_position_m')
rejects('armature_zeroed',lambda s:s.GetPrimAtPath('/Robot/joints/left_hip').GetAttribute('physxJoint:armature').Set(0.),'armature')
rejects('default_body_drag',lambda s:s.GetPrimAtPath('/Robot/links/left_wheel').GetAttribute('physxRigidBody:angularDamping').Set(.05),'body damping')
rejects('wrong_collision_axis',lambda s:s.GetPrimAtPath('/Robot/links/left_wheel/left_tire').GetAttribute('xformOp:orient').Set(__import__('pxr.Gf',fromlist=['Quatf']).Quatf(1.)),'geometry orientation')
rejects('wrong_drive_units',lambda s:s.GetPrimAtPath('/Robot/joints/left_hip').GetAttribute('drive:angular:physics:damping').Set(.2),'drive damping')
rejects('tree_joint_excluded',lambda s:s.GetPrimAtPath('/Robot/joints/left_hip').CreateAttribute('physics:excludeFromArticulation',Sdf.ValueTypeNames.Bool).Set(True),'tree joint excluded')
rejects('missing_hifi',lambda s:s.GetPrimAtPath('/Robot/links/left_wheel/visual_276').SetActive(False),'HiFi visual')

m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
robot=SimpleNamespace(device='cpu',joint_names=[m.joint(j).name for j in range(1,m.njnt)],body_names=[m.body(b).name for b in range(1,m.nbody)])
robot.data=SimpleNamespace(body_pos_w=torch.tensor(d.xpos[None,1:].copy(),dtype=torch.float32),body_quat_w=torch.tensor(d.xquat[None,1:].copy(),dtype=torch.float32),
    joint_pos=torch.tensor(d.qpos[None,m.jnt_qposadr[1:]].copy(),dtype=torch.float32),joint_vel=torch.tensor(d.qvel[None,m.jnt_dofadr[1:]].copy(),dtype=torch.float32))
guard=RuntimeGuard(robot);guard.check()
robot.data.body_pos_w[0,robot.body_names.index('left_coupler'),0]+=.02
try:guard.check()
except RuntimeError as e:assert 'separated' in str(e);cases.append('runtime_detached_link')
else:raise AssertionError('Runtime guard missed separation')
robot.data.body_pos_w=torch.tensor(d.xpos[None,1:].copy(),dtype=torch.float32)
robot.data.joint_pos[0,robot.joint_names.index('left_drive_hip_spin')]+=.1
try:guard.check()
except RuntimeError as e:assert 'coupling failed' in str(e);cases.append('runtime_chain_slip')
else:raise AssertionError('Runtime guard missed chain slip')
properties={
    'get_masses':torch.tensor(m.body_mass[None,1:].copy()),
    'get_dof_armatures':torch.tensor(m.dof_armature[None,6:].copy()),
    'get_dof_dampings':torch.tensor(m.dof_damping[None,6:].copy()),
    'get_dof_stiffnesses':torch.tensor(m.jnt_stiffness[None,1:].copy()),
    'get_dof_max_forces':torch.tensor([[dict(zip(CONTRACT['actuated_joint_names'],CONTRACT['effort_limits_nm'])).get(n,1e6) for n in robot.joint_names]]),
    'get_dof_limits':torch.tensor([[CONTRACT['joints'][n]['limits_si'] or [-1e9,1e9] for n in robot.joint_names]])}
robot.root_physx_view=SimpleNamespace(**{name:(lambda v=v:v) for name,v in properties.items()})
audit_runtime_parameters(robot)
for label,key,name,bad in [('runtime_armature_lost','get_dof_armatures','left_hip',0.),
                         ('runtime_gas_stiffness_lost','get_dof_stiffnesses','left_gas_slide',0.),
                         ('runtime_effort_overridden','get_dof_max_forces','left_hip',400.)]:
    i=robot.joint_names.index(name);old=properties[key][0,i].item();properties[key][0,i]=bad
    try:audit_runtime_parameters(robot)
    except RuntimeError:cases.append(label)
    else:raise AssertionError('Missed PhysX parameter override: '+label)
    properties[key][0,i]=old
result={'status':'PASS','valid_usd':valid,'independent_references':clone_results,'injected_faults_rejected':cases,
    'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['isaac/robot.usd','isaac/import_contract.json','isaac/audit_import.py']},
    'scope':'USD static tests including two independently referenced environments, plus mocked runtime telemetry; not a PhysX execution test'}
(ROOT/'reports/import_guard_tests.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
