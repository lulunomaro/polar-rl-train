"""Static own-USD task-space retarget solver. No dynamics, optimizer training or actor.

All poses are composed from authored joint frames. The 6 spherical loop anchors,
own joint limits and actual body-parallel transmission geometry are used together.
The PhysX gearing -1 is NOT misread as q_drive == -q_reference.
This is a kinematic reference fit, not torque/collision/270mm-skill certification.
"""
from __future__ import annotations

from dataclasses import dataclass,replace
from pathlib import Path
import json
import math

import numpy as np

from supermimic_reference_adapter_v1 import (
    ACTION_ORDER, NativeReference, PendingReferenceError, ReferenceContractError,
    angular_velocity_world, array, derivative, mat_to_quat, quat_to_mat, require,
)


def transform(position, rotation):
    result=np.eye(4); result[:3,:3]=rotation; result[:3,3]=position
    return result


def axis_rotation(axis,angle):
    c,s=math.cos(angle),math.sin(angle)
    if axis==0: return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if axis==1: return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


@dataclass(frozen=True)
class IKResult:
    joint_pos30: np.ndarray
    status: str
    iterations: int
    wheel_error_max_m: float
    closure_error_max_m: float
    joint_limit_violation: float
    body_parallel_error_frobenius: float
    input_difference_violation_rad: float
    note: str = "static_kinematic_fit_only_not_own_dynamics_or_skill_success"

    def summary(self):
        return {key:(value.tolist() if isinstance(value,np.ndarray) else value)
                for key,value in self.__dict__.items()}


class OwnUsdKinematics:
    def __init__(self,body_names,joints,closures,mimics,training_min_input_difference_rad,
                 wheel_points_body_m,source_metadata):
        self.body_names=tuple(body_names); self.joints=tuple(joints)
        self.closures=tuple(closures); self.mimics=tuple(mimics)
        self.joint_names=tuple(row["name"] for row in joints)
        require(len(self.joints)==30 and len(set(self.joint_names))==30,"own model must have 30 unique one-DOF joints")
        require(len(self.body_names)==31,"own model must have 31 bodies")
        self.ids={name:i for i,name in enumerate(self.joint_names)}
        self.by_child={row["child"]:row for row in self.joints}
        self.lo=np.array([r["lower"] for r in self.joints]);self.hi=np.array([r["upper"] for r in self.joints])
        self.min_input_difference_rad=float(training_min_input_difference_rad)
        self.wheel_points=tuple(np.asarray(x,dtype=float) for x in wheel_points_body_m)
        self.source_metadata=dict(source_metadata)
        self.wheel_names=("left_wheel","right_wheel")
        self.mimic_names={m["name"] for m in self.mimics}
        self.unidentified_spin_names={name for name in self.joint_names if name.startswith("guide_roller_") or name.endswith("wheel_spin")}
        self.variables=np.array([i for i,name in enumerate(self.joint_names)
                                 if name not in self.mimic_names|self.unidentified_spin_names])
        self.neutral_poses=self.forward(np.zeros(30),enforce_transmission=False)
        self.neutral_parallel={m["name"]:self.neutral_poses[m["reference_child"]][:3,:3].T @
                                self.neutral_poses[m["child"]][:3,:3] for m in self.mimics}
        # Current actual asset uses equal authored joint frames for drive/reference.
        # Check this geometrically before using the scalar equality in the solve.
        for m in self.mimics:
            require(abs(m["gearing"]+1)<1e-6 and abs(m["offset"])<1e-6,"unhandled actual mimic recipe")
            q=np.zeros(30);q[self.ids[m["name"]]]=.1;q[self.ids[m["reference"]]]=.1
            poses=self.forward(q,enforce_transmission=False)
            relative=poses[m["reference_child"]][:3,:3].T@poses[m["child"]][:3,:3]
            require(np.linalg.norm(relative-self.neutral_parallel[m["name"]])<1e-5,
                    "body-parallel transmission differs from current asset; explicit mapping needed")

    @classmethod
    def from_sources(cls,usd_path,geometry_json_path,import_contract_path):
        # Deferred import: pure contract/reference tests do not need pxr or Isaac Lab.
        from pxr import Usd,UsdPhysics
        geometry=json.loads(Path(geometry_json_path).read_text(encoding="utf8"))
        contract=json.loads(Path(import_contract_path).read_text(encoding="utf8"))
        stage=Usd.Stage.Open(str(usd_path));require(stage is not None,"own USD failed to open")
        names=geometry["body_names"]; by_child={};closures=[]; raw_by_name={}
        def local(joint,side):
            p=getattr(joint,f"GetLocalPos{side}Attr")().Get()
            q=getattr(joint,f"GetLocalRot{side}Attr")().Get()
            return transform(np.array(p),quat_to_mat([q.GetReal(),*q.GetImaginary()]))
        for prim in stage.Traverse():
            if not prim.IsA(UsdPhysics.Joint):continue
            joint=UsdPhysics.Joint(prim);a=joint.GetBody0Rel().GetTargets();b=joint.GetBody1Rel().GetTargets()
            if not a or not b:continue
            row=dict(name=prim.GetName(),parent=str(a[0]).split("/")[-1],child=str(b[0]).split("/")[-1],
                     T0=local(joint,0),T1inv=np.linalg.inv(local(joint,1)),kind=prim.GetTypeName())
            if "Spherical" in row["kind"]:
                row["T1"]=local(joint,1);closures.append(row);continue
            require("Revolute" in row["kind"] or "Prismatic" in row["kind"],"unexpected own tree joint kind")
            row["axis"]="XYZ".index(str(prim.GetAttribute("physics:axis").Get()))
            low=prim.GetAttribute("physics:lowerLimit").Get();high=prim.GetAttribute("physics:upperLimit").Get()
            factor=math.pi/180 if "Revolute" in row["kind"] else 1.
            row["lower"]=float(low)*factor;row["upper"]=float(high)*factor
            require(row["child"] not in by_child,"duplicate incoming own joint")
            by_child[row["child"]]=row;raw_by_name[row["name"]]=row
        joints=[by_child[n] for n in names[1:]]
        resolved={names[0]}
        for row in joints:
            require(row["parent"] in resolved,"geometry body order is not own joint topological order")
            resolved.add(row["child"])
        mimics=[]
        for name,m in contract["mimics"].items():
            # Validate the actual USD relationship, rather than trusting a stale contract.
            prim=stage.GetPrimAtPath("/Robot/joints/"+name)
            relation=prim.GetRelationship("physxMimicJoint:rotX:referenceJoint").GetTargets()
            require(len(relation)==1 and str(relation[0]).split("/")[-1]==m["reference_joint"],"own mimic source/contract mismatch")
            gearing=float(prim.GetAttribute("physxMimicJoint:rotX:gearing").Get())
            require(abs(gearing-float(m["gearing"]))<1e-6,"own mimic gearing mismatch")
            mimics.append(dict(name=name,reference=m["reference_joint"],gearing=gearing,offset=float(m["offset"]),
                               child=raw_by_name[name]["child"],reference_child=raw_by_name[m["reference_joint"]]["child"]))
        wheel_points=[]
        for wheel in ("left_wheel","right_wheel"):
            shapes=[s for s in geometry["shapes"] if s["body"]==wheel]
            require(len(shapes)==1 and shapes[0]["type"]=="Mesh","actual own wheel collision mesh missing")
            shape=shapes[0]
            wheel_points.append(np.array(shape["points"])@np.array(shape["linear_body_from_shape"]).T+np.array(shape["origin_body_m"]))
        return cls(names,joints,closures,mimics,contract["training_window"]["input_difference_min_rad"],wheel_points,
                   dict(usd_path=str(usd_path),geometry_json_path=str(geometry_json_path),import_contract_path=str(import_contract_path),
                        source_hashes="not_recomputed_large_USD_or_old_arrays_not_hashed",
                        joint_order="derived_from_actual_geometry_body_order_incoming_USD_joint_not_fresh_SDK_readback",
                        actual_own_wheel_collision_radius_m=float(max(abs(wheel_points[0][:,2]))),
                        nominal_spawn_height_m=float(contract["spawn_height_m"])))

    def project(self,q):
        out=np.clip(np.asarray(q,dtype=float),self.lo,self.hi).copy()
        for side in ("left","right"):
            hip=self.ids[side+"_hip"];crank=self.ids[side+"_crank"]
            out[crank]=max(out[crank],out[hip]+self.min_input_difference_rad)
        for m in self.mimics:
            out[self.ids[m["name"]]]=out[self.ids[m["reference"]]]
        return out

    def forward(self,q,enforce_transmission=True):
        q=array(q,(30,),"own joint position")
        if enforce_transmission:q=self.project(q)
        result={self.body_names[0]:np.eye(4)}
        for i,row in enumerate(self.joints):
            motion=np.eye(4)
            if "Prismatic" in row["kind"]:motion[row["axis"],3]=q[i]
            else:motion[:3,:3]=axis_rotation(row["axis"],q[i])
            result[row["child"]]=result[row["parent"]]@row["T0"]@motion@row["T1inv"]
        return result

    def wheel_local(self,q):
        poses=self.forward(q)
        return np.stack([poses[name][:3,3] for name in self.wheel_names])

    def closure_vectors(self,poses):
        return np.stack([(poses[r["parent"]]@r["T0"])[:3,3]-(poses[r["child"]]@r["T1"])[:3,3]
                         for r in self.closures])

    def diagnostics(self,q,target):
        poses=self.forward(q,enforce_transmission=False)
        errors=np.stack([poses[n][:3,3] for n in self.wheel_names])-target
        violation=float(np.maximum(self.lo-q,0).max()+np.maximum(q-self.hi,0).max())
        parallel=max(float(np.linalg.norm(poses[m["reference_child"]][:3,:3].T@poses[m["child"]][:3,:3]-
                                          self.neutral_parallel[m["name"]])) for m in self.mimics)
        difference=max(max(0.,self.min_input_difference_rad-(q[self.ids[s+"_crank"]]-q[self.ids[s+"_hip"]])) for s in ("left","right"))
        return dict(wheel_error_max_m=float(np.linalg.norm(errors,axis=-1).max()),
                    closure_error_max_m=float(np.linalg.norm(self.closure_vectors(poses),axis=-1).max()),
                    joint_limit_violation=violation,body_parallel_error_frobenius=parallel,input_difference_violation_rad=difference)

    def solve(self,target_wheel_local_m,seed30=None,*,max_iterations=60,wheel_fit_tolerance_m=.001,
              closure_tolerance_m=.002):
        """Deterministic bounded damped least squares over 16 own leg coordinates.

        The closure tolerance records the existing 2mm per-environment protection;
        it does not create a batch stop or change training physics. Wheel fit is
        a retarget approximation tolerance, not a new skill graduation threshold.
        No result is projected into a fake success when a target is unreachable.
        """
        target=array(target_wheel_local_m,(2,3),"target own wheel centers")
        require(max_iterations>=0 and wheel_fit_tolerance_m>0 and closure_tolerance_m>0,"invalid bounded IK configuration")
        q=self.project(np.zeros(30) if seed30 is None else array(seed30,(30,),"IK seed"))
        anchor=q.copy(); damping=1e-5
        def residual(value):
            poses=self.forward(value)
            wheel=np.stack([poses[n][:3,3] for n in self.wheel_names])-target
            return np.concatenate((wheel.ravel(),2*self.closure_vectors(poses).ravel(),.0001*(value[self.variables]-anchor[self.variables])))
        result=None
        for iteration in range(max_iterations+1):
            diag=self.diagnostics(q,target)
            passed=(diag["wheel_error_max_m"]<=wheel_fit_tolerance_m and diag["closure_error_max_m"]<=closure_tolerance_m and
                    diag["joint_limit_violation"]<=1e-8 and diag["body_parallel_error_frobenius"]<=1e-5 and
                    diag["input_difference_violation_rad"]<=1e-8)
            if passed or iteration==max_iterations:
                result=IKResult(q.copy(),"STATIC_KINEMATIC_FIT" if passed else "PENDING_UNREACHABLE_OR_IK_NOT_CONVERGED",iteration,**diag)
                break
            current=residual(q); columns=[]
            for index in self.variables:
                h=1e-5 if "Prismatic" not in self.joints[index]["kind"] else 1e-6
                plus=q.copy();plus[index]+=h;plus=self.project(plus)
                minus=q.copy();minus[index]-=h;minus=self.project(minus)
                delta=plus[index]-minus[index]
                columns.append((residual(plus)-residual(minus))/delta if abs(delta)>0 else np.zeros_like(current))
            jacobian=np.stack(columns,axis=-1)
            step=np.linalg.solve(jacobian.T@jacobian+damping*np.eye(len(self.variables)),-jacobian.T@current)
            step*=min(1.,.2/max(float(np.linalg.norm(step)),1e-12))
            accepted=False
            for scale in (1.,.5,.25,.125,.0625):
                proposal=q.copy();proposal[self.variables]+=scale*step;proposal=self.project(proposal)
                if np.linalg.norm(residual(proposal)) < np.linalg.norm(current):
                    q=proposal;damping=max(damping*.5,1e-8);accepted=True;break
            if not accepted:damping=min(damping*10,1e3)
        return result

    def retarget_clip(self,taskspace,seed30=None,**solver_kwargs):
        q=self.project(np.zeros(30) if seed30 is None else array(seed30,(30,),"own seed"))
        results=[]; poses=[]
        for target in taskspace.wheel_local_m:
            solved=self.solve(target,q,**solver_kwargs);results.append(solved);q=solved.joint_pos30.copy();poses.append(q)
        return np.stack(poses),results

    def derived_wheel_spin(self,taskspace,joint_pos30):
        """Own no-slip kinematic phase in measured support; hold in flight.

        This quadrature is of an explicitly assumed rolling reference, not foreign
        q copying, action inversion, or plant dynamics. Wheel spin in flight and
        the 8 free guide rollers are not identifiable from these demonstrations.
        """
        q=np.asarray(joint_pos30,dtype=float).copy();t=taskspace.time_s
        r=quat_to_mat(taskspace.root_quaternion_wxyz)
        center=taskspace.root_position_m[:,None,:]+np.einsum("tij,twj->twi",r,taskspace.wheel_local_m)
        center_velocity=derivative(center,t)
        for k,wheel in enumerate(self.wheel_names):
            row=self.by_child[wheel];idx=self.ids[row["name"]];axes=[];parent_q=[];rad=[]
            for frame in range(len(t)):
                pose=self.forward(q[frame]);parent=pose[row["parent"]]
                axis=r[frame]@parent[:3,:3]@row["T0"][:3,:3][:,row["axis"]]
                axes.append(axis);parent_q.append(mat_to_quat(r[frame]@parent[:3,:3]))
                localpoints=self.wheel_points[k]
                points=(r[frame]@pose[wheel][:3,:3]@localpoints.T).T
                # Radius is the authored collision mesh's vertical support extent.
                rad.append(max(float(-points[:,2].min()),1e-8))
            parent_w=angular_velocity_world(np.array(parent_q),t);rate=[]
            for frame in range(len(t)):
                axis=axes[frame];tangent=np.cross(axis,[0.,0.,1.]);length=np.linalg.norm(tangent)
                require(length>.1,"wheel axis vertical: rolling tangent undefined")
                tangent/=length;bottom=np.array([0.,0.,-rad[frame]])
                denominator=float(np.dot(np.cross(axis,bottom),tangent))
                speed=-float(np.dot(center_velocity[frame,k]+np.cross(parent_w[frame],bottom),tangent))/denominator
                rate.append(speed if taskspace.wheel_contact[frame,k] else 0.)
            q[:,idx]=q[0,idx]
            for frame in range(1,len(t)):
                # ZOH support: never introduce an airborne spin from future contact.
                q[frame,idx]=q[frame-1,idx]+rate[frame-1]*(t[frame]-t[frame-1])
        return q

    def reconstruct_root_height_from_recorded_wheel_path(self,demo,taskspace,joint_pos30,*,source_wheel_radius_m=.06):
        """Preserve recorded wheel-ground height motion after own limb-range retarget.

        Source baseline is removed; its original ~0.3m platform is not transferred
        as our task surface. The observed bottom-path displacement is scaled only
        by the two actual wheel radii. Own chassis Z is then reconstructed using
        own FK and collision points. Left/right disagreement is reported, never
        called contact/dynamics success or silently converted into a 270mm step.
        """
        require(np.isfinite(source_wheel_radius_m) and source_wheel_radius_m>0,"positive original cylinder radius required")
        clock=taskspace.metadata["source_clock"]
        observed=demo.resample(taskspace.metadata["target_control_dt_s"],clock["crop_start_source_s"],clock["crop_end_source_s"])
        require(len(observed.time_s)==len(taskspace.time_s),"source/retarget frame count mismatch")
        q=array(joint_pos30,(len(taskspace.time_s),30),"own retarget joint timeline")
        rotations=quat_to_mat(taskspace.root_quaternion_wxyz);offset=[]
        for frame in range(len(q)):
            poses=self.forward(q[frame]);row=[]
            for k,wheel in enumerate(self.wheel_names):
                pose=poses[wheel]
                points=(rotations[frame]@(pose[:3,:3]@self.wheel_points[k].T+pose[:3,3,None])).T
                row.append(float(points[:,2].min()))
            offset.append(row)
        offset=np.array(offset)
        own_radius=float(self.source_metadata["actual_own_wheel_collision_radius_m"])
        scale=own_radius/source_wheel_radius_m
        bottom_displacement=(observed.wheel_bottom_world_z_m-observed.wheel_bottom_world_z_m[0])*scale
        root_delta_each=bottom_displacement-(offset-offset[0])
        root=taskspace.root_position_m.copy();root[:,2]=root[0,2]+root_delta_each.mean(-1)
        disagreement=abs(root_delta_each[:,0]-root_delta_each[:,1])
        achieved=root[:,2,None]+offset
        desired=taskspace.root_position_m[0,2]+offset[0]+bottom_displacement
        meta=dict(taskspace.metadata,root_height_method="own_collision_FK_plus_recorded_wheel_bottom_displacement_mean_left_right_v2",
                  source_wheel_radius_m=float(source_wheel_radius_m),own_collision_wheel_radius_m=own_radius,
                  wheel_bottom_displacement_scale=scale,
                  source_initial_platform_world_height_removed=True,
                  root_Z_not_legacy_settled_leglength_amplified_curve=True,
                  left_right_root_height_disagreement_max_m=float(disagreement.max()),
                  actual_reference_contact_not_own_plant_contact=True)
        diagnostics=dict(time_s=taskspace.time_s.tolist(),desired_recorded_scaled_wheel_bottom_world_z_m=desired.tolist(),
                         own_kinematic_wheel_bottom_world_z_m=achieved.tolist(),
                         own_wheel_bottom_reference_error_m=(achieved-desired).tolist(),
                         left_right_root_height_disagreement_m=disagreement.tolist(),
                         maximum_abs_wheel_bottom_reference_error_m=float(abs(achieved-desired).max()),
                         metric="kinematic_motion_approximation_not_physical_contact_or_skill_acceptance")
        return replace(taskspace,root_position_m=root,metadata=meta),diagnostics

    def preserve_recorded_wheel_height_asymmetry(self,demo,taskspace,*,source_wheel_radius_m=.06):
        """Retain the recorded L/R bottom-height difference before own static IK.

        Common limb compression is range-attenuated by retarget_taskspace; the
        observed L/R support/flight geometry is kept separately. Thus attenuation
        cannot silently turn a one-wheel source touchdown into two airborne own
        wheels. Residual collision-mesh approximation is reported after own FK.
        """
        clock=taskspace.metadata["source_clock"]
        observed=demo.resample(taskspace.metadata["target_control_dt_s"],clock["crop_start_source_s"],clock["crop_end_source_s"])
        rotations=quat_to_mat(taskspace.root_quaternion_wxyz);own_radius=float(self.source_metadata["actual_own_wheel_collision_radius_m"])
        scale=own_radius/source_wheel_radius_m
        neutral=self.forward(np.zeros(30));support=[]
        for frame in range(len(taskspace.time_s)):
            row=[]
            for k,wheel in enumerate(self.wheel_names):
                points=(rotations[frame]@neutral[wheel][:3,:3]@self.wheel_points[k].T).T
                row.append(float(points[:,2].min()))
            support.append(row)
        support=np.array(support);wheels=taskspace.wheel_local_m.copy()
        base_center=np.einsum("ij,wj->wi",rotations[0],wheels[0])[:,2]
        initial_bottom_diff=(base_center+support[0])[0]-(base_center+support[0])[1]
        observed_diff=observed.wheel_bottom_world_z_m[:,0]-observed.wheel_bottom_world_z_m[:,1]
        desired_diff=initial_bottom_diff+(observed_diff-observed_diff[0])*scale
        for i,r in enumerate(rotations):
            require(abs(r[2,2])>.5,"source near inversion: upright wheel-height mapping is not applicable")
            xy=r[2,0]*(wheels[i,0,0]-wheels[i,1,0])+r[2,1]*(wheels[i,0,1]-wheels[i,1,1])
            dz=(desired_diff[i]-xy-(support[i,0]-support[i,1]))/r[2,2]
            mean=float(wheels[i,:,2].mean());wheels[i,0,2]=mean+dz*.5;wheels[i,1,2]=mean-dz*.5
        meta=dict(taskspace.metadata,limb_common_compression="explicit_range_attenuated_excursion",
                  left_right_wheel_height_difference="recorded_bottom_difference_scaled_by_wheel_radius_then_solved_through_own_R_and_IK",
                  source_wheel_radius_m=float(source_wheel_radius_m),own_collision_wheel_radius_m=own_radius)
        return replace(taskspace,wheel_local_m=wheels,metadata=meta)

    def to_native_reference(self,taskspace,joint_pos30,results,*,source_jump_validation="pending",allow_fixture=False):
        require(len(results)==len(taskspace.time_s),"missing per-frame IK results")
        if not all(r.status=="STATIC_KINEMATIC_FIT" for r in results):
            raise PendingReferenceError("full native reference pending: one or more task-space frames fail the own-geometry IK fit")
        q=self.derived_wheel_spin(taskspace,joint_pos30)
        # Recompute after own rolling spin derivation, do not trust mismatched external q.
        for row,target in zip(q,taskspace.wheel_local_m):
            diag=self.diagnostics(row,target)
            require(diag["closure_error_max_m"]<=.002 and diag["wheel_error_max_m"]<=.001 and
                    diag["joint_limit_violation"]<=1e-8 and diag["body_parallel_error_frobenius"]<=1e-5 and
                    diag["input_difference_violation_rad"]<=1e-8,"provided joint clip disagrees with validated IK")
        t=taskspace.time_s
        packed=np.concatenate((taskspace.root_position_m,taskspace.root_quaternion_wxyz,
                               derivative(taskspace.root_position_m,t),angular_velocity_world(taskspace.root_quaternion_wxyz,t),q,derivative(q,t)),-1)
        mask=np.ones(73,dtype=bool)
        # This source has not demonstrated our forward arrival or side motion.
        # Packed goals retain world XY; native invariant_features remove it.
        # Mask XY/XY velocity rather than inventing travel toward the step.
        mask[[0,1,7,8]]=False
        for name in self.unidentified_spin_names:
            index=self.ids[name];mask[13+index]=False;mask[43+index]=False
        meta=dict(taskspace.metadata,own_geometry=self.source_metadata,
                  kinematic_pose_contract="passed_for_all_exported_frames",
                  closed_chain_IK="static_all_exported_frames_fit_dynamic_feasibility_pending",
                  sdk_joint_order_verified=False,source_jump_validation=source_jump_validation,
                  foreign_transitions_for_native_world_model=False,
                  wheel_spin_source="own_center_path_rolling_reference_in_support_hold_in_flight",
                  unidentifiable_joint_reference=list(sorted(self.unidentified_spin_names)),
                  free_guide_roller_spin="own_seed_held_unobserved_not_foreign_copy",
                  source_contact_reference=dict(time_s=t.tolist(),left_right_contact=taskspace.wheel_contact.tolist(),
                                                phase=list(taskspace.contact_phase),
                                                used_for="phase_metadata_and_own_rolling_reference_only_not_applied_physical_gate"),
                  conditioning_feature_mask73=mask.tolist(),
                  conditioning_mask_layout="raw_packed_state_xyz_wxyz_world_v_world_w_q30_dq30",
                  conditioning_mask_excludes="world_XY_world_velocity_XY_unidentified_wheel_and_guide_roller_spin_q_dq",
                  joint_position_range_scale30=np.where(np.isfinite(self.hi-self.lo),np.maximum((self.hi-self.lo)*.5,.001),1.).tolist(),
                  reference_reward_integration="PartialReferenceImitationMdp_native_imagination_own_task_XY_plus_demo_alignment_runtime_loss_admission_pending",
                  physical_reward_integration="original_V8_RewardManager_unchanged",
                  motor_torque_speed_feasibility="pending_own_dynamics_not_evaluated",
                  collision_nonpenetration="pending_not_certified_by_wheel_center_IK",
                  native_physics_dt_s=.0025,native_H1_decimation=4,native_H1_control_dt_s=.01,
                  H1_success_machine_unchanged=True,not_frozen_skill_graduation=True)
        return NativeReference(t,packed,self.joint_names,meta,allow_fixture=allow_fixture)
