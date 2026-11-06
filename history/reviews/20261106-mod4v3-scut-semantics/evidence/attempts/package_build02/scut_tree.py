"""SCUT's native front1->front2->front3 tree cut, with preserved MOD4 mechanics.

This optional variant puts all six anatomical scalar hinges at the same physical
pivots as SCUT V14. The old f3r1 hinge's damping/armature/stop moves to a coupled
coordinate. MuJoCo represents it by a fixed tendon. PhysX requires an explicit
runtime contribution; its USD never pretends that a spherical cut has armature.
The faithful native-cut USD remains the default physically complete USD.
"""
from copy import deepcopy
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics

from build import vec, numbers, quaternion, rotation, quat_array, write_json, sha


def build_scut_tree(package):
    package=Path(package)
    api_spec=__import__('json').loads((package/'semantics.json').read_bytes())
    root=ET.parse(package/'mjcf/scene.xml').getroot()
    model=mujoco.MjModel.from_xml_path(str(package/'mjcf/scene.xml'))
    data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    tendon=ET.Element('tendon')
    rows=[]
    for side in ('left','right'):
        def body(short):return root.find(".//body[@name='"+side+'_'+short+"_link']")
        rear,front2,front3=body('rear1'),body('front2'),body('front3')
        old=front3.find('joint');old_name=old.get('name')
        scalar=deepcopy(old)
        name=side+'_front3_joint'
        scalar.set('name',name);scalar.set('pos','0 0 0');scalar.set('axis','0 1 0')
        scalar.set('limited','false');scalar.attrib.pop('range',None)
        scalar.set('damping','0');scalar.set('armature','0');scalar.set('stiffness','0')
        semexpr=api_spec['coordinates']['semantic_from_native'][name]
        ref=sum(float(model.qpos0[model.joint(n).qposadr[0]])*c for n,c in semexpr.items())
        scalar.set('ref',f'{ref:.16g}')
        front3.remove(old);front3.insert(0,scalar)
        id2=model.body(side+'_front2_link').id;id3=model.body(side+'_front3_link').id
        R2=data.xmat[id2].reshape(3,3);R3=data.xmat[id3].reshape(3,3)
        front3.set('pos',numbers(R2.T@(data.xpos[id3]-data.xpos[id2])))
        front3.set('quat',numbers(quaternion(R2.T@R3)))
        rear.remove(front3);front2.append(front3)
        # Old proximal connect at B becomes the real f3r1 closure at P.
        # Existing measured physical P coordinate is the old hinge world anchor.
        oldjoint=model.joint(old_name).id;P=data.xanchor[oldjoint]
        idrear=model.body(side+'_rear1_link').id;Rrear=data.xmat[idrear].reshape(3,3)
        pa=R3.T@(P-data.xpos[id3]);pb=Rrear.T@(P-data.xpos[idrear])
        ET.SubElement(front3,'site',name=side+'_f3r1_rocker',pos=numbers(pa),size='.002',group='3')
        ET.SubElement(rear,'site',name=side+'_f3r1_rear',pos=numbers(pb),size='.002',group='3')
        closure=root.find("equality/connect[@name='"+name+"']")
        closure.set('name',side+'_f3r1_joint');closure.set('site1',side+'_f3r1_rocker');closure.set('site2',side+'_f3r1_rear')
        # relative rocker/rear1 angle = front1+front2+front3-rear1.
        coeffs={side+'_front1_joint':1.,side+'_front2_joint':1.,name:1.,side+'_rear1_joint':-1.}
        oldref=float(model.qpos0[model.joint(old_name).qposadr[0]])
        attrs=dict(name=side+'_f3r1_physical_coordinate',limited=old.get('limited','false'),
            damping=old.get('damping','0'),armature=old.get('armature','0'),stiffness='0')
        if old.get('range'):attrs['range']=old.get('range')
        attrs['solreflimit']='.001 1';attrs['solimplimit']='.9999 .99999 .0001'
        fixed=ET.SubElement(tendon,'fixed',**attrs)
        for n,c in coeffs.items():ET.SubElement(fixed,'joint',joint=n,coef=str(c))
        rows.append(dict(side=side,coordinate=coeffs,reference_rad=oldref,
            damping_Nm_s_rad=float(old.get('damping','0')),armature_kg_m2=float(old.get('armature','0')),
            limited=old.get('limited','false')=='true',limits_si=[None if not math.isfinite(float(x))else float(x)for x in old.get('range','-inf inf').split()],
            original_stop_and_passive_physics_preserved_in_MJCF=True,
            USD_runtime_adapter_required=True,
            reason='PhysX spherical loop closure has no scalar armature; apply coupled contribution explicitly'))
    root.insert(list(root).index(root.find('actuator')),tendon)
    path=package/'mjcf/scene_scut_tree.xml';ET.indent(root,space='  ');ET.ElementTree(root).write(path,encoding='utf8',xml_declaration=True)
    stage=Usd.Stage.Open(str(package/'assets/robot.usd'))
    target=package/'assets/robot_scut_tree.usd';stage.Flatten().Export(str(target));stage=Usd.Stage.Open(str(target))
    for row in rows:
        side=row['side'];hinge_path='/Robot/joints/'+side+'_front3_joint';cut_path='/Robot/joints/'+side+'_f3r1_joint'
        old=stage.GetPrimAtPath(cut_path);joint=UsdPhysics.Joint(old)
        # Preserve P-anchor opinions from the original hinge before changing type.
        ends=[(getattr(joint,f'GetBody{i}Rel')().GetTargets(),getattr(joint,f'GetLocalPos{i}Attr')().Get())for i in (0,1)]
        Bjoint=UsdPhysics.Joint(stage.GetPrimAtPath(hinge_path));Bends=[(Bjoint.GetBody0Rel().GetTargets(),Bjoint.GetLocalPos0Attr().Get()),(Bjoint.GetBody1Rel().GetTargets(),Bjoint.GetLocalPos1Attr().Get())]
        # Original B closure is front2->front3; scalar hinge inherits that order.
        stage.RemovePrim(hinge_path);h=UsdPhysics.RevoluteJoint.Define(stage,hinge_path)
        for i,(targets,pos)in enumerate(Bends):
            getattr(h,f'CreateBody{i}Rel')().SetTargets(targets);getattr(h,f'CreateLocalPos{i}Attr')().Set(pos)
            getattr(h,f'CreateLocalRot{i}Attr')().Set(Gf.Quatf(1,Gf.Vec3f(0)))
        h.CreateAxisAttr().Set('Y');h.CreateLowerLimitAttr().Set(float('-inf'));h.CreateUpperLimitAttr().Set(float('inf'))
        h.CreateExcludeFromArticulationAttr().Set(False);h.CreateCollisionEnabledAttr().Set(False)
        h.GetPrim().CreateAttribute('physxJoint:armature',Sdf.ValueTypeNames.Float).Set(0.)
        h.GetPrim().CreateAttribute('physxJoint:jointFriction',Sdf.ValueTypeNames.Float).Set(0.)
        h.GetPrim().SetCustomDataByKey('mod4v3:semanticScalar',True)
        stage.RemovePrim(cut_path);c=UsdPhysics.SphericalJoint.Define(stage,cut_path)
        # SCUT endpoint order is front3->rear1, opposite the old tree hinge.
        for i,(targets,pos)in enumerate(reversed(ends)):
            getattr(c,f'CreateBody{i}Rel')().SetTargets(targets);getattr(c,f'CreateLocalPos{i}Attr')().Set(pos)
            getattr(c,f'CreateLocalRot{i}Attr')().Set(Gf.Quatf(1,Gf.Vec3f(0)))
        c.CreateExcludeFromArticulationAttr().Set(True);c.CreateCollisionEnabledAttr().Set(False)
        c.GetPrim().SetCustomDataByKey('mod4v3:coupledPhysicalCoordinate','../scut_tree_runtime.json')
    rootprim=stage.GetDefaultPrim();rootprim.SetCustomDataByKey('mod4v3:front3IsDerivedScalarAcrossLoopCut',False)
    rootprim.SetCustomDataByKey('mod4v3:representation','SCUT_tree_with_explicit_coupled_physics_runtime')
    rootprim.SetCustomDataByKey('mod4v3:runtimePhysicsRequired',True)
    stage.GetRootLayer().Save()
    report=dict(schema='mod4v3.scut_tree_runtime.v1',MJCF='mjcf/scene_scut_tree.xml',USD='assets/robot_scut_tree.usd',
        loops=rows,physical_default_USD='assets/robot.usd',
        all_SCUT_anatomical_scalar_joints_are_native=True,
        coordinate_basis='semantic_order in semantics.json',
        native_MJCF_coupled_force_and_inertia=True,
        USD_use_without_runtime_contribution_changes_physics=True,
        USD_runtime_PhysX_verified=False,
        no_dummy_gimbal_or_extra_rollers_added=True)
    write_json(package/'scut_tree_runtime.json',report)
    return report


def coupled_passive_forces(q, qd, rows, names):
    """Exact rate/armature contribution for SCUT-tree simulators without tendons.

    Return damping generalized force and rank-one generalized mass additions.
    Apply these at the physics solver level, not as an acceleration reward.
    Stops must additionally use the declared coupled coordinate/limits.
    """
    out=np.zeros_like(qd);mass=np.zeros((len(names),len(names)))
    for row in rows:
        a=np.array([row['coordinate'].get(n,0.)for n in names])
        speed=np.einsum('...i,i->...',qd,a)
        out-=row['damping_Nm_s_rad']*speed[...,None]*a
        mass+=row['armature_kg_m2']*np.outer(a,a)
    return out,mass


if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);a=parser.parse_args()
    result=build_scut_tree(a.package)
    print(json.dumps(dict(MJCF=str(a.package/result['MJCF']),USD=str(a.package/result['USD']))))
