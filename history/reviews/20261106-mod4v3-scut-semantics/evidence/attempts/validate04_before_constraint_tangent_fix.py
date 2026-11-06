"""Actual MuJoCo/Usd reads and physical equivalence probes for MOD4v3.

The checks compare independent compiled geometry/tensors/forces, not only the
builder's metadata. No policy, GPU training or target-runtime approval is implied.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import traceback
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Gf, Usd, UsdGeom, UsdPhysics

from build import sha, write_json, ry, rotation, quat_array
from semantics import Semantics, ScutRobotView, weighted_rewards, termination_reward_term, kinematic_measures


def validate(package, report):
    package = package.resolve()
    if report.exists():
        raise FileExistsError("Preserve earlier validation; choose a new report name")
    checks, details, errors = {}, {}, []
    def ck(name, passed, detail=None):
        checks[name] = bool(passed)
        if detail is not None:
            details[name] = detail
        if not passed:
            raise AssertionError(name)
    try:
        api = Semantics(package)
        spec = api.spec
        provenance = json.loads((package/"PROVENANCE.json").read_bytes())
        source = Path(provenance["source_package"])
        for row in provenance["immutable_inputs"]:
            ck("immutable_source_"+Path(row["path"]).name, sha(row["path"]) == row["sha256"])
        contract = json.loads((package/"assets/import_contract.json").read_bytes())
        ck("MJCF_identity", sha(package/"mjcf/scene.xml") == contract["source_mjcf_sha256"])
        ck("USD_identity", sha(package/"assets/robot.usd") == contract["output_usd_sha256"])
        ck("semantic_identity", sha(package/"semantics.json") == contract["semantics_sha256"])
        m0 = mujoco.MjModel.from_xml_path(str(source/"mjcf/scene.xml"))
        m = mujoco.MjModel.from_xml_path(str(package/"mjcf/scene.xml"))
        d0, d = mujoco.MjData(m0), mujoco.MjData(m)
        ck("full_model_counts", (m.nbody,m.nq,m.nv,m.nu,m.neq) == (32,37,36,6,10),
            dict(bodies_including_world=m.nbody,nq=m.nq,nv=m.nv,actuators=m.nu,equalities=m.neq))
        ck("total_mass_preserved", abs(m0.body_mass.sum()-m.body_mass.sum())<1e-10,
            dict(total_mass_kg=float(m.body_mass.sum())))
        ck("controls_reference_order", [m.joint(int(x[0])).name for x in m.actuator_trnid] == spec["control"]["policy_action_order"])
        ck("all_v2_bodies_mapped_once", len(set(spec["source_to_v3"]["bodies"].values())) == m.nbody-1)
        ck("all_reference_bodies_accounted", len(spec["reference_coverage"]["bodies"]) == 37)
        ck("all_reference_joints_accounted", len(spec["reference_coverage"]["joints"]) == 42)
        ck("rear2_is_actual_knee", all(spec["source_to_v3"]["joints"][s+"_knee"] == s+"_rear2_joint" for s in ("left","right")))
        absent = [r["scut"] for r in spec["reference_coverage"]["joints"] if r["status"] == "absent_on_MOD4"]
        details["absent_reference_joints"] = absent
        for name in absent:
            rejected = False
            try:
                api.require_reference([name])
            except ValueError:
                rejected = True
            ck("absent_raises_"+name, rejected)
        ck("reference_no_MJCF_honest", spec["reference"]["reference_MJCF_available"] is False)
        helper_spec=importlib.util.spec_from_file_location("mod4v3_validation_source_kinematics", package/"legacy/kinematics_v2.py")
        kin=importlib.util.module_from_spec(helper_spec); helper_spec.loader.exec_module(kin)
        old_joints = [m0.joint(i).name for i in range(1,m0.njnt)]
        body_map = spec["source_to_v3"]["bodies"]
        old_xml = ET.parse(source/"mjcf/scene.xml").getroot()
        closures = [(e.get("site1"),e.get("site2")) for e in old_xml.find("equality").findall("connect")]
        def set_v3():
            mujoco.mj_resetData(m,d)
            d.qpos[:7] = d0.qpos[:7]
            old_q = np.array([d0.qpos[m0.joint(n).qposadr[0]] for n in old_joints])
            values = api.from_legacy_v2(old_q, old_joints)
            for i,n in enumerate(api.native_names):
                d.qpos[m.joint(n).qposadr[0]]=values[i]
                old=spec["coordinates"]["native_from_v2"][n]["source"]
                d.qvel[m.joint(n).dofadr[0]]=d0.qvel[m0.joint(old).dofadr[0]]
            d.qvel[:6]=d0.qvel[:6]
            mujoco.mj_forward(m,d)
            return values
        scenarios = [((0.,0.),(0.,0.)), ((.2,.4),(-.1,-.6)),
            ((0.,-1.08),(.1,.58)), ((2*math.pi,2*math.pi+.1),(-2*math.pi,-2*math.pi-.4))]
        max_geo=max_rot=max_com=max_inertia=max_closure=max_force=0.
        rows=[]
        random=np.random.default_rng(20261106)
        for left,right in scenarios:
            mujoco.mj_resetData(m0,d0)
            d0.qpos[:3] = [0.,0.,.8]
            kin.set_configuration(m0,d0,left=left,right=right,check_limits=True)
            d0.qvel[:]=random.normal(0,.2,m0.nv)
            mujoco.mj_forward(m0,d0)
            native=set_v3()
            for i in range(m0.ngeom):
                n=m0.geom(i).name;j=m.geom(n).id
                max_geo=max(max_geo,float(np.max(np.abs(d0.geom_xpos[i]-d.geom_xpos[j]))))
                max_rot=max(max_rot,float(np.max(np.abs(d0.geom_xmat[i]-d.geom_xmat[j]))))
                ck("geom_material_"+n, np.allclose(m0.geom_friction[i],m.geom_friction[j],rtol=0,atol=1e-12))
            for i in range(m0.nsite):
                n=m0.site(i).name;j=m.site(n).id
                max_geo=max(max_geo,float(np.max(np.abs(d0.site_xpos[i]-d.site_xpos[j]))))
            for old,new in body_map.items():
                i,j=m0.body(old).id,m.body(new).id
                max_com=max(max_com,float(np.max(np.abs(d0.xipos[i]-d.xipos[j]))))
                R0=d0.ximat[i].reshape(3,3);R=d.ximat[j].reshape(3,3)
                I0=R0@np.diag(m0.body_inertia[i])@R0.T
                I=R@np.diag(m.body_inertia[j])@R.T
                max_inertia=max(max_inertia,float(np.max(np.abs(I0-I))))
            for a,b in closures:
                max_closure=max(max_closure,float(np.linalg.norm(d.site_xpos[m.site(a).id]-d.site_xpos[m.site(b).id])))
            max_force=max(max_force,float(np.max(np.abs(d0.qfrc_passive-d.qfrc_passive))))
            semantic=api.positions(native)
            ck("semantic_roundtrip_"+str(len(rows)),np.allclose(api.native_positions(semantic),native,atol=1e-12,rtol=0))
            for side in ("left","right"):
                # Independently read body rotations, then measure the actual
                # front2-to-front3 relative angle across the native loop cut.
                b2=m.body(side+"_front2_link").id;b3=m.body(side+"_front3_link").id
                rel=d.xmat[b2].reshape(3,3).T@d.xmat[b3].reshape(3,3)
                actual=math.atan2(rel[0,2],rel[0,0]);value=semantic[api.names.index(side+"_front3_joint")]
                ck("front3_physical_relative_angle_"+side+"_"+str(len(rows)),abs(math.atan2(math.sin(actual-value),math.cos(actual-value)))<1e-10)
            rows.append(dict(left=left,right=right,closure_m=max_closure))
        ck("collision_and_visual_world_geometry_preserved", max_geo<1e-9 and max_rot<1e-9,
            dict(max_world_point_error_m=max_geo,max_rotation_matrix_error=max_rot))
        ck("mass_com_inertia_world_preserved",max_com<1e-9 and max_inertia<1e-9,
            dict(max_world_COM_error_m=max_com,max_world_inertia_tensor_error_kg_m2=max_inertia))
        ck("static_closed_chain_preserved",max_closure<1e-5,dict(max_closure_m=max_closure,poses=rows))
        ck("same_native_passive_forces",max_force<1e-6,dict(max_abs_difference_SI=max_force))
        velocity=random.normal(size=(8,len(api.native_names)))
        torque=random.normal(size=velocity.shape)
        semantic_v=api.velocities(velocity);semantic_tau=api.generalized_forces(torque)
        power=np.sum(torque*velocity,axis=-1)-np.sum(semantic_tau*semantic_v,axis=-1)
        ck("torque_transform_preserves_power",np.max(np.abs(power))<1e-12,dict(max_power_error_W=float(np.max(np.abs(power)))))
        # Full masses, all collision/mesh transforms and every relationship are
        # read from the final USD instead of trusting the MJCF import contract.
        stage=Usd.Stage.Open(str(package/"assets/robot.usd"))
        source_stage=Usd.Stage.Open(str(source/"assets/robot.usd"))
        ck("USD_opens",bool(stage))
        for row in spec['reference_coverage']['joints']:
            if row['status']!='absent_on_MOD4':
                ck('USD_homologous_pivot_exists_'+row['scut'],stage.GetPrimAtPath('/Robot/joints/'+row['mod4v3']).IsA(UsdPhysics.Joint))
        ck("USD_units",UsdGeom.GetStageMetersPerUnit(stage)==1. and str(UsdGeom.GetStageUpAxis(stage))=="Z")
        cache0,cache=UsdGeom.XformCache(),UsdGeom.XformCache()
        usd_point=usd_inertia=usd_joint_gap=0.
        for old,new in body_map.items():
            a=source_stage.GetPrimAtPath('/Robot/links/'+old);b=stage.GetPrimAtPath('/Robot/links/'+new)
            ck("USD_rigid_body_"+new,b.HasAPI(UsdPhysics.RigidBodyAPI))
            ma,mb=UsdPhysics.MassAPI(a),UsdPhysics.MassAPI(b)
            ck("USD_mass_"+new,abs(ma.GetMassAttr().Get()-mb.GetMassAttr().Get())<1e-10)
            wa,wb=cache0.GetLocalToWorldTransform(a),cache.GetLocalToWorldTransform(b)
            ca=wa.Transform(Gf.Vec3d(*ma.GetCenterOfMassAttr().Get()));cb=wb.Transform(Gf.Vec3d(*mb.GetCenterOfMassAttr().Get()))
            usd_point=max(usd_point,float(np.max(np.abs(np.array(ca)-np.array(cb)))))
            Ra=rotation(quat_array(wa.ExtractRotationQuat()))@rotation(quat_array(ma.GetPrincipalAxesAttr().Get()))
            Rb=rotation(quat_array(wb.ExtractRotationQuat()))@rotation(quat_array(mb.GetPrincipalAxesAttr().Get()))
            Ia=Ra@np.diag(ma.GetDiagonalInertiaAttr().Get())@Ra.T;Ib=Rb@np.diag(mb.GetDiagonalInertiaAttr().Get())@Rb.T
            usd_inertia=max(usd_inertia,float(np.max(np.abs(Ia-Ib))))
            for child in a.GetChildren():
                other=b.GetChild(child.GetName())
                ck("USD_child_type_"+old+"_"+child.GetName(),bool(other) and child.GetTypeName()==other.GetTypeName())
                if child.IsA(UsdGeom.Xformable):
                    before=np.array(cache0.GetLocalToWorldTransform(child))
                    after=np.array(cache.GetLocalToWorldTransform(other))
                    usd_point=max(usd_point,float(np.max(np.abs(before-after))))
                if child.IsA(UsdGeom.Mesh):
                    ck("USD_mesh_vertices_"+old+"_"+child.GetName(),np.array_equal(np.array(UsdGeom.Mesh(child).GetPointsAttr().Get()),np.array(UsdGeom.Mesh(other).GetPointsAttr().Get())))
                ck("USD_collision_state_"+old+"_"+child.GetName(),child.HasAPI(UsdPhysics.CollisionAPI)==other.HasAPI(UsdPhysics.CollisionAPI))
        for prim in stage.Traverse():
            for rel in prim.GetRelationships():
                for target in rel.GetTargets():
                    ck("USD_relationship_"+str(prim.GetPath())+"_"+rel.GetName()+"_"+str(target),bool(stage.GetObjectAtPath(target)))
            if prim.IsA(UsdPhysics.Joint):
                j=UsdPhysics.Joint(prim);world=[]
                for i in (0,1):
                    target=getattr(j,f'GetBody{i}Rel')().GetTargets()
                    if target:
                        point=getattr(j,f'GetLocalPos{i}Attr')().Get()
                        world.append(np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(target[0])).Transform(Gf.Vec3d(*point))))
                if len(world)==2:usd_joint_gap=max(usd_joint_gap,float(np.linalg.norm(world[0]-world[1])))
        ck("USD_physical_transforms_preserved",usd_point<2e-7 and usd_inertia<2e-7,
            dict(max_transform_or_COM_error=usd_point,max_world_inertia_error=usd_inertia))
        ck("USD_anchors_still_closed",usd_joint_gap<1e-5,dict(max_anchor_gap_m=usd_joint_gap))
        for n,row in contract["joints"].items():
            prim=stage.GetPrimAtPath('/Robot/joints/'+n)
            is_hinge=row["type"]=='hinge'
            if is_hinge:
                ck("USD_hinge_semantic_axis_"+n,prim.GetAttribute('physics:axis').Get()=='Y')
                ck("USD_hinge_zero_frame_"+n,all(np.allclose(quat_array(getattr(UsdPhysics.Joint(prim),f'GetLocalRot{i}Attr')().Get()),[1,0,0,0]) for i in (0,1)))
            raw=[prim.GetAttribute('physics:lowerLimit').Get(),prim.GetAttribute('physics:upperLimit').Get()]
            values=[math.radians(x) if is_hinge else x for x in raw]
            expected=row['limits_si']
            ck("USD_MJCF_physical_limits_"+n,all((not math.isfinite(a) and b is None) or (b is not None and abs(a-b)<3e-7) for a,b in zip(values,expected)))
        for side in ("left","right"):
            n=side+'_spring2_joint';j=m.joint(n);lo,hi=m.jnt_range[j.id]
            k=float(m.jnt_stiffness[j.id]);ref=float(m.qpos_spring[j.qposadr[0]])
            ck("gas300N60mm_"+side,abs(hi-lo-.06)<1e-10 and abs(k*(ref-hi)-300)<1e-7)
            drive=UsdPhysics.DriveAPI.Get(stage.GetPrimAtPath('/Robot/joints/'+n),'linear')
            ck("gas_USD_MJCF_law_"+side,abs(drive.GetStiffnessAttr().Get()-k)<1e-6 and abs(drive.GetTargetPositionAttr().Get()-ref)<1e-7)
        # A moving mechanism smoke retains source gravity/contact/constraints.
        # Compare v2 and v3 under the same named actuator torques for 0.2 sec.
        mujoco.mj_resetData(m0,d0);d0.qpos[:3]=[0,0,.8]
        kin.set_configuration(m0,d0,left=(0,0),right=(0,0),check_limits=True)
        set_v3();dyn_error=dynamic_closure=0.
        for step in range(80):
            for i in range(m.nu):
                name=m.joint(int(m.actuator_trnid[i,0])).name
                old=spec['coordinates']['native_from_v2'][name]['source'];a0=m0.actuator(old+'_motor').id
                tau=.2*math.sin(step*.03+i)
                d.ctrl[i]=tau;d0.ctrl[a0]=tau
            mujoco.mj_step(m0,d0);mujoco.mj_step(m,d)
            dyn_error=max(dyn_error,float(np.max(np.abs(d.qpos[:3]-d0.qpos[:3]))))
            for a,b in closures:
                dynamic_closure=max(dynamic_closure,float(np.linalg.norm(d.site_xpos[m.site(a).id]-d.site_xpos[m.site(b).id])))
        ck("bounded_CPU_dynamics_finite",np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all())
        ck("bounded_CPU_same_response",dyn_error<1e-5,dict(seconds=.2,gravity=m.opt.gravity.tolist(),max_root_difference_m=dyn_error,policy=False))
        ck("bounded_CPU_closure10mm",dynamic_closure<.01,dict(max_closure_m=dynamic_closure))
        # Reward lifecycle checks exercise the previously missed event and name.
        terminated=np.array([True,False,True]);truncated=np.array([False,True,True])
        term=termination_reward_term(terminated,truncated)
        total,parts=weighted_rewards(dict(termination=term),dict(termination=-200.),.02)
        ck("fall_actually_penalized_and_timeout_distinct",np.array_equal(total,[-4,0,-4]))
        missing=False
        try:weighted_rewards(dict(termination=term),dict(termination=-200.,misspelled_reward=1.),.02)
        except KeyError:missing=True
        ck("missing_nonzero_reward_fails",missing)
        q=np.array([math.cos(.15),0,math.sin(.15),0])
        wheels=np.array([[[.1,.22,-.3],[-.1,-.22,-.3]]])
        measures=kinematic_measures(np.zeros((1,3)),q[None],wheels,np.array([[0,.18,0],[0,-.18,0]]))
        ck("SCUT_and_MOD4_leg_measures_distinct",not np.allclose(measures['scut_leg_length_xz'],measures['hip_to_wheel_length_3d']))
        ck("semantic_leg_angle_sign",measures['scut_leg_angle'][0,0]<0 and measures['scut_leg_angle'][0,1]>0)
        # Exercise the actual reward-facing adapter, including strict selectors
        # and the endpoint state instead of a name-only mapping declaration.
        from types import SimpleNamespace
        native=np.array([d.qpos[m.joint(n).qposadr[0]]for n in api.native_names])
        vnative=np.array([d.qvel[m.joint(n).dofadr[0]]for n in api.native_names])
        raw=SimpleNamespace(joint_names=list(api.native_names),body_names=contract['body_names'],
            data=SimpleNamespace(joint_pos=native[None],joint_vel=vnative[None],
                joint_acc=np.zeros((1,30)),applied_torque=np.zeros((1,30)),
                root_quat_w=np.array([[0.,0.,0.,1.]])))
        view=ScutRobotView(raw,package,quaternion_order='xyzw')
        ids,names=view.find_joints('.*_rear2_joint')
        ck('SCUT_view_rear2_binds_real_knees',names==['left_rear2_joint','right_rear2_joint'])
        ck('SCUT_view_state_uses_semantic_coordinates',np.allclose(view.data.joint_pos[0],api.positions(native),atol=1e-12))
        ck('SCUT_view_quaternion_conversion',np.array_equal(view.data.root_quat_w,[[1,0,0,0]]))
        ids,names=view.find_joints(spec['control']['policy_action_order'],preserve_order=True)
        ck('SCUT_view_explicit_action_order',names==spec['control']['policy_action_order'])
        ck('SCUT_view_front3_is_derived',all(n in view.joint_names for n in ['left_front3_joint','right_front3_joint']) and 'left_f3r1_joint'not in view.joint_names)
        decoded=api.decode_actions(np.ones((1,6)),np.zeros((1,4)),leg_scale=.5,wheel_scale=10.,wheel_mode='velocity')
        ck('SCUT_raw_action_formula',[float(x[0])for x in decoded['leg_position_targets'].values()]==[.5]*4 and all(float(x[0])==10 for x in decoded['wheel_targets'].values()))
        ck('force_roundtrip',np.allclose(api.native_forces(semantic_tau),torque,rtol=0,atol=1e-12))
        # Same-tree MJCF puts front3 at its SCUT pivot. The removed native hinge
        # is a fixed-tendon coordinate with its original damping and armature.
        from scut_tree import coupled_passive_forces
        mt=mujoco.MjModel.from_xml_path(str(package/'mjcf/scene_scut_tree.xml'))
        dt=mujoco.MjData(mt)
        runtime=json.loads((package/'scut_tree_runtime.json').read_bytes())
        ck('SCUT_tree_counts',mt.nbody==32 and mt.nu==6 and mt.neq==10 and mt.ntendon==2)
        rng=np.random.default_rng(7153)
        for side in ('left','right'):
            pbody=mt.body(int(mt.body_parentid[mt.jnt_bodyid[mt.joint(side+'_front3_joint').id]])).name
            ck('SCUT_tree_front3_parent_'+side,pbody==side+'_front2_link')
            ck('SCUT_tree_front3_native_scalar_'+side,mt.jnt_type[mt.joint(side+'_front3_joint').id]==mujoco.mjtJoint.mjJNT_HINGE)
        tree_geo=tree_mass=tree_passive=0.
        for left,right in scenarios:
            mujoco.mj_resetData(m0,d0);d0.qpos[:3]=[0,0,.8]
            kin.set_configuration(m0,d0,left=left,right=right,check_limits=True)
            d0.qvel[:]=rng.normal(0,.3,m0.nv);mujoco.mj_forward(m0,d0)
            native=set_v3();semq=api.positions(native)
            native_v=np.array([d.qvel[m.joint(n).dofadr[0]]for n in api.native_names]);semv=api.velocities(native_v)
            mujoco.mj_resetData(mt,dt);dt.qpos[:7]=d.qpos[:7];dt.qvel[:6]=d.qvel[:6]
            for i,n in enumerate(api.names):
                dt.qpos[mt.joint(n).qposadr[0]]=semq[i];dt.qvel[mt.joint(n).dofadr[0]]=semv[i]
            mujoco.mj_forward(mt,dt)
            for i in range(m.ngeom):
                tree_geo=max(tree_geo,float(np.max(np.abs(d.geom_xpos[i]-dt.geom_xpos[mt.geom(m.geom(i).name).id]))))
            # Compare complete generalized mass tensors in identical semantic
            # coordinates, including both fixed tendons' off-diagonal armature.
            Mf=np.empty((m.nv,m.nv));Mt=np.empty((mt.nv,mt.nv))
            mujoco.mj_fullM(m,d,Mf);mujoco.mj_fullM(mt,dt,Mt)
            Tf=np.zeros((m.nv,36));Tt=np.zeros((mt.nv,36));Tf[:6,:6]=np.eye(6);Tt[:6,:6]=np.eye(6)
            basis=np.eye(30)
            for col in range(30):
                vv=api.native_positions(basis[col])
                for i,n in enumerate(api.native_names):Tf[m.joint(n).dofadr[0],6+col]=vv[i]
                Tt[mt.joint(api.names[col]).dofadr[0],6+col]=1.
            tree_mass=max(tree_mass,float(np.max(np.abs(Tf.T@Mf@Tf-Tt.T@Mt@Tt))))
            tree_passive=max(tree_passive,float(np.max(np.abs(Tf.T@d.qfrc_passive-Tt.T@dt.qfrc_passive))))
        ck('SCUT_tree_same_physical_geometry',tree_geo<1e-9,dict(max_geom_error_m=tree_geo))
        ck('SCUT_tree_same_full_mass_tensor',tree_mass<1e-8,dict(max_generalized_mass_difference=tree_mass))
        ck('SCUT_tree_same_passive_forces',tree_passive<1e-7,dict(max_generalized_passive_force_difference=tree_passive))
        old_J=api.spec['coordinates']['native_order'].index('left_f3r1_joint')
        native_zero=np.zeros(30);vel=api.velocities(np.eye(30)[old_J])
        damp,mass=coupled_passive_forces(api.positions(native_zero),vel,runtime['loops'],api.names)
        ck('SCUT_tree_coupled_runtime_dissipates',np.dot(damp,vel)<0 and float(vel@mass@vel)>0)
        tree_stage=Usd.Stage.Open(str(package/'assets/robot_scut_tree.usd'))
        for side in ('left','right'):
            ck('SCUT_tree_USD_front3_scalar_'+side,tree_stage.GetPrimAtPath('/Robot/joints/'+side+'_front3_joint').IsA(UsdPhysics.RevoluteJoint))
            ck('SCUT_tree_USD_f3r1_closure_'+side,tree_stage.GetPrimAtPath('/Robot/joints/'+side+'_f3r1_joint').IsA(UsdPhysics.SphericalJoint))
        ck('SCUT_tree_USD_runtime_requirement_explicit',tree_stage.GetDefaultPrim().GetCustomDataByKey('mod4v3:runtimePhysicsRequired')is True)
        # CPU wheel-floor contact is read with names instead of reused indices.
        mujoco.mj_resetData(m,d);mujoco.mj_forward(m,d)
        gid=m.geom('ground').id
        wheel_contacts=set()
        for contact in d.contact:
            if gid in (contact.geom1,contact.geom2):
                other=contact.geom2 if contact.geom1==gid else contact.geom1
                wheel_contacts.add(m.body(int(m.geom_bodyid[other])).name)
        details['initial_ground_contact_bodies']=sorted(wheel_contacts)
        details['verification_scope']=dict(actual_MuJoCo_version=mujoco.__version__,USD_version=list(Usd.GetVersion()),
            all_checks_run_on_CPU=True,PhysX_GPU_dynamics=False,Newton_Warp_GPU_dynamics=False,
            task_success_or_reward_convergence_tested=False,
            raw_front3_scalar_requires_semantic_adapter=True)
    except BaseException:
        errors.append(traceback.format_exc())
    result=dict(schema="mod4v3.validation.v1",passed=not errors and all(checks.values()),
        checks=checks,details=details,errors=errors,
        claim="SEMANTIC_MAPPING_AND_REPRESENTATION_EQUIVALENCE_ONLY",
        rl_ready=False,training_or_foreign_process_modified=False)
    write_json(report,result)
    print(json.dumps(dict(report=str(report),passed=result['passed'],checks=len(checks),
        failed=[k for k,v in checks.items() if not v],errors=errors),ensure_ascii=False))
    return result['passed']


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();sys.exit(0 if validate(args.package,args.report) else 1)
