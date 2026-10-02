"""Positive and deliberately corrupted imports, plus runtime guard faults."""
from pathlib import Path
import sys, json
from types import SimpleNamespace
import numpy as np
import torch
import mujoco
from pxr import Usd, Sdf
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'isaac'))
from audit_import import audit_stage,RuntimeGuard
ASSET=ROOT/'isaac/robot_closed.usda'
def fresh():
    s=Usd.Stage.Open(str(ASSET));s.SetEditTarget(s.GetSessionLayer());return s
valid=audit_stage(fresh());cases=[]
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
rejects('armature_zeroed',lambda s:s.GetPrimAtPath('/Robot/joints/left_hip').GetAttribute('physxJointAxis:rotX:armature').Set(0.),'armature')
rejects('missing_hifi',lambda s:s.GetPrimAtPath('/Robot/links/left_wheel/cad_113').SetActive(False),'HiFi visual')

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
result={'status':'PASS','valid_usd':valid,'injected_faults_rejected':cases,'scope':'USD static tests plus mocked runtime telemetry; not a PhysX execution test'}
(ROOT/'reports/import_guard_tests.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
