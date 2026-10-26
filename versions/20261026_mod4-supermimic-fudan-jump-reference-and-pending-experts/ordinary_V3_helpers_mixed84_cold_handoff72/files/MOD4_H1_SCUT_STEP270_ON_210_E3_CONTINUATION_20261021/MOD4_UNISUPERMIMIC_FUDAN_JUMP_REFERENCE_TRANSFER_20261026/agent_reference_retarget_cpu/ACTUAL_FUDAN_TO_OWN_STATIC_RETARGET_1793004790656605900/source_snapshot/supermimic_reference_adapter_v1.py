"""Task-space demonstration import and native SuperMimic goals; no plant/model IO.

This module consumes measured poses/contact observations, never foreign q/actions.
It has no random sampling, optimizer, policy inference, GPU, or dynamics integrator.
An unfinished retarget is explicit and cannot silently become a 73-value native goal.
The existing H1 plant, 6-action interface, reward coefficients and success machine are
outside this module. Source and target clocks are separate measured/configured fields.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json
import math
import xml.etree.ElementTree as ET

import numpy as np


SCHEMA = "mod4.supermimic.taskspace_demo.v1"
NATIVE_SCHEMA = "mod4.supermimic.native_reference.v1"
FUDAN_COMMIT = "8204e853dfd2ed06d85a322e1a998c3d20a3be2c"
ACTION_ORDER = ("left_crank", "left_hip", "right_crank", "right_hip",
                "left_wheel_spin", "right_wheel_spin")
FORBIDDEN_KEYS = {"full_qpos", "full_qvel", "raw_action6", "executed_action6",
                  "actuator_torque6", "obs25", "obs_history125", "a", "s1",
                  "applied_action", "gate_choice", "future_applied_action"}


class ReferenceContractError(ValueError):
    pass


class PendingReferenceError(ReferenceContractError):
    pass


def require(condition, message):
    if not condition:
        raise ReferenceContractError(message)


def array(value, shape, name):
    out = np.asarray(value, dtype=float)
    require(out.shape == tuple(shape), f"{name}: expected {shape}, got {out.shape}")
    require(bool(np.isfinite(out).all()), f"{name}: non-finite data")
    return out


def quat_normalize(q):
    q = np.asarray(q, dtype=float)
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    require(bool(np.isfinite(q).all() and (norm > 0).all()), "invalid quaternion")
    return q / norm


def quat_to_mat(q):
    q = quat_normalize(q)
    w, x, y, z = np.moveaxis(q, -1, 0)
    return np.stack((1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y),
                     2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x),
                     2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)), -1).reshape(q.shape[:-1]+(3, 3))


def mat_to_quat(matrix):
    """Stable scalar/batched conversion; output is wxyz with continuous signs later."""
    matrix = np.asarray(matrix, dtype=float)
    flat = matrix.reshape(-1, 3, 3)
    result = []
    for m in flat:
        vals = np.array([1+np.trace(m), 1+m[0,0]-m[1,1]-m[2,2],
                         1-m[0,0]+m[1,1]-m[2,2], 1-m[0,0]-m[1,1]+m[2,2]])
        k = int(np.argmax(vals)); s = 2 * math.sqrt(max(0., vals[k]))
        require(s > 0, "invalid rotation matrix")
        if k == 0:
            q = [s/4, (m[2,1]-m[1,2])/s, (m[0,2]-m[2,0])/s, (m[1,0]-m[0,1])/s]
        elif k == 1:
            q = [(m[2,1]-m[1,2])/s, s/4, (m[0,1]+m[1,0])/s, (m[0,2]+m[2,0])/s]
        elif k == 2:
            q = [(m[0,2]-m[2,0])/s, (m[0,1]+m[1,0])/s, s/4, (m[1,2]+m[2,1])/s]
        else:
            q = [(m[1,0]-m[0,1])/s, (m[0,2]+m[2,0])/s, (m[1,2]+m[2,1])/s, s/4]
        result.append(q)
    return quat_normalize(np.array(result)).reshape(matrix.shape[:-2]+(4,))


def continuous_quat(q):
    q = quat_normalize(q).copy()
    for i in range(1, len(q)):
        if np.dot(q[i-1], q[i]) < 0:
            q[i] *= -1
    return q


def slerp(q0, q1, fraction):
    q0, q1 = quat_normalize(q0), quat_normalize(q1)
    dot = np.sum(q0*q1, -1, keepdims=True)
    q1 = np.where(dot < 0, -q1, q1); dot = np.clip(abs(dot), 0, 1)
    t = np.asarray(fraction)[..., None]
    theta = np.arccos(dot); sine = np.sin(theta)
    a = np.divide(np.sin((1-t)*theta), sine, out=1-t+np.zeros_like(sine), where=sine > 1e-8)
    b = np.divide(np.sin(t*theta), sine, out=t+np.zeros_like(sine), where=sine > 1e-8)
    return quat_normalize(a*q0+b*q1)


def derivative(values, times):
    require(len(times) >= 2, "derivative needs at least two measured times")
    return np.gradient(np.asarray(values), np.asarray(times), axis=0, edge_order=1)


def angular_velocity_world(quaternions, times):
    """Finite differences of orientation, in world coordinates; no qvel copying."""
    q = continuous_quat(quaternions)
    qd = derivative(q, times)
    w, v = q[:, :1], q[:, 1:]
    wd, vd = qd[:, :1], qd[:, 1:]
    return 2 * (-wd*v + w*vd + np.cross(v, vd))


def invariant_features_numpy(packed73):
    """Same order as native invariant_features: z, heading-free6d, body v/w, q/dq."""
    state = np.asarray(packed73)
    require(state.shape[-1] == 73, "native packed reference requires 30 joints / 73 values")
    r = quat_to_mat(state[..., 3:7])
    xy = r[..., :2, 0]; norm = np.linalg.norm(xy, axis=-1, keepdims=True)
    require(bool((norm > 1e-8).all()), "heading undefined for vertical forward axis")
    xy = xy / norm
    heading = np.zeros_like(r)
    heading[..., 0, 0] = xy[..., 0]; heading[..., 1, 0] = xy[..., 1]
    heading[..., 0, 1] = -xy[..., 1]; heading[..., 1, 1] = xy[..., 0]
    heading[..., 2, 2] = 1
    local_rot = np.swapaxes(heading, -1, -2) @ r
    rt = np.swapaxes(r, -1, -2)
    return np.concatenate((state[..., 2:3], local_rot[..., :, :2].reshape(state.shape[:-1]+(6,)),
                           (rt @ state[..., 7:10, None])[..., 0],
                           (rt @ state[..., 10:13, None])[..., 0], state[..., 13:]), -1)


@dataclass(frozen=True)
class TaskReferenceSpec:
    name: str
    control_dt_s: float | None
    physics_dt_s: float | None
    decimation: int | None
    admission: str = "reference_contract_pending_not_Task_GO"


TASK_REGISTRY = {
    "H1_step270": TaskReferenceSpec("H1_step270", .01, .0025, 4),
    "E2_world_moving": TaskReferenceSpec("E2_world_moving", .02, .0025, 8),
    "E3_recovery": TaskReferenceSpec("E3_recovery", .02, .0025, 8),
    **{name: TaskReferenceSpec(name, None, None, None) for name in
       ("E1_CURB", "E1_SLOPE", "E4_low_tunnel", "continuous_stairs", "flyramp_gap_landing")},
}


@dataclass(frozen=True)
class TaskspaceDemo:
    source: dict
    clock: dict
    time_s: np.ndarray
    chassis_position_m: np.ndarray
    chassis_quaternion_wxyz: np.ndarray
    wheel_center_m: np.ndarray
    wheel_bottom_world_z_m: np.ndarray
    wheel_contact: np.ndarray
    provenance_kind: str = "measured_original_robot_reference"

    @classmethod
    def from_dict(cls, data):
        allowed = {"schema", "source", "clock", "time_s", "chassis_position_m",
                   "chassis_quaternion_wxyz", "wheel_center_m", "wheel_bottom_world_z_m",
                   "wheel_contact", "provenance_kind"}
        require(set(data) == allowed, f"unexpected/missing canonical fields: {set(data)^allowed}")
        require(data["schema"] == SCHEMA, "unknown demonstration schema")
        require(not FORBIDDEN_KEYS.intersection(data), "foreign action/state fields are prohibited")
        t = np.asarray(data["time_s"], dtype=float); n = len(t)
        require(t.shape == (n,) and n >= 2 and np.isfinite(t).all() and np.all(np.diff(t)>0),
                "sample times must be finite, strictly increasing, at least two")
        p = array(data["chassis_position_m"], (n,3), "chassis position")
        q = array(data["chassis_quaternion_wxyz"], (n,4), "chassis quaternion wxyz")
        require(bool(np.all(abs(np.linalg.norm(q,axis=-1)-1) < .001)), "non-unit source quaternion")
        wheels = array(data["wheel_center_m"], (n,2,3), "left/right wheel centers")
        bottom = array(data["wheel_bottom_world_z_m"], (n,2), "left/right wheel bottoms")
        contact_raw = np.asarray(data["wheel_contact"])
        require(contact_raw.shape == (n,2) and bool(np.isin(contact_raw,[False,True,0,1]).all()), "binary left/right contacts required")
        require(data["clock"].get("time_basis") == "measured_simulation_time_s", "measured source sim time required")
        require(data["source"].get("quaternion") == "wxyz", "canonical quaternion must be wxyz")
        require(data["source"].get("wheel_order") == ["left", "right"], "canonical wheel order must be left/right")
        require(data["source"].get("foreign_transitions_for_native_world_model") is False,
                "foreign dynamics cannot enter the native world model")
        require(data["provenance_kind"] in ("measured_original_robot_reference", "synthetic_CPU_contract_fixture"), "unknown provenance kind")
        return cls(dict(data["source"]), dict(data["clock"]), t, p, continuous_quat(q), wheels,
                   bottom, contact_raw.astype(bool), data["provenance_kind"])

    def as_dict(self):
        return dict(schema=SCHEMA, source=self.source, clock=self.clock, time_s=self.time_s.tolist(),
                    chassis_position_m=self.chassis_position_m.tolist(), chassis_quaternion_wxyz=self.chassis_quaternion_wxyz.tolist(),
                    wheel_center_m=self.wheel_center_m.tolist(), wheel_bottom_world_z_m=self.wheel_bottom_world_z_m.tolist(),
                    wheel_contact=self.wheel_contact.tolist(), provenance_kind=self.provenance_kind)

    def resample(self, target_dt_s, start_s=None, end_s=None):
        require(np.isfinite(target_dt_s) and target_dt_s > 0, "positive target clock required")
        start = float(self.time_s[0] if start_s is None else start_s)
        end = float(self.time_s[-1] if end_s is None else end_s)
        require(self.time_s[0] <= start < end <= self.time_s[-1], "crop outside measured source interval")
        t = start + np.arange(int(np.floor((end-start)/target_dt_s + 1e-9))+1)*target_dt_s
        require(len(t) >= 2, "crop has fewer than two target frames")
        lo = np.clip(np.searchsorted(self.time_s,t,side="right")-1,0,len(self.time_s)-2)
        a = (t-self.time_s[lo])/(self.time_s[lo+1]-self.time_s[lo])
        def lerp(v):
            f = a.reshape((-1,)+(1,)*(v.ndim-1))
            return (1-f)*v[lo]+f*v[lo+1]
        # Contacts are measured observations: hold the last sample, never interpolate.
        hold = np.clip(np.searchsorted(self.time_s,t,side="right")-1,0,len(self.time_s)-1)
        clock = dict(self.clock, target_control_dt_s=float(target_dt_s),
                     crop_start_source_s=start, crop_end_source_s=end,
                     source_times_retained=True, contact_resampling="left_continuous_zero_order_hold")
        return TaskspaceDemo(self.source,clock,t,lerp(self.chassis_position_m),
                             continuous_quat(slerp(self.chassis_quaternion_wxyz[lo],self.chassis_quaternion_wxyz[lo+1],a)),
                             lerp(self.wheel_center_m),lerp(self.wheel_bottom_world_z_m),self.wheel_contact[hold],self.provenance_kind)


def import_new_fudan_capture(npz_path, mjcf_xml_path, producer_receipt, case_summary, normal_contact_threshold_n=1.):
    """Read only allowlisted pose/contact arrays of the explicitly authorized NEW capture.

    Caller must supply root's verified producer/two-host artifact receipt. This function
    does not compute model/raw hashes or infer body indices from foreign joint vectors.
    The XML body preorder is valid only for this direct, include-free pinned MJCF.
    """
    require(producer_receipt.get("new_capture_explicitly_authorized") is True, "new capture authorization receipt required")
    require(producer_receipt.get("two_host_sha_verified") is True, "capture producer/two-host SHA verification pending")
    require(producer_receipt.get("source_commit") == FUDAN_COMMIT, "wrong Fudan pinned commit")
    require(Path(producer_receipt.get("artifact_path","")).resolve()==Path(npz_path).resolve(),
            "capture path differs from the explicitly authorized receipt")
    sha=producer_receipt.get("artifact_sha256","")
    require(isinstance(sha,str) and len(sha)==64 and all(c in "0123456789abcdef" for c in sha),"verified artifact SHA256 required in receipt")
    require(case_summary.get("status") == "COMPLETE_BOUNDED_ORIGINAL_ROBOT_CPU_ROLLOUT", "original capture incomplete/error")
    require(np.isfinite(normal_contact_threshold_n) and normal_contact_threshold_n >= 0, "invalid contact threshold")
    root = ET.parse(mjcf_xml_path).getroot()
    require(not root.findall(".//include"), "XML includes need producer model body-name metadata")
    names = ["world"]+[b.attrib["name"] for b in root.find("worldbody").iter("body")]
    ids = [names.index(n) for n in ("base_Link_del", "l_wheel_Link", "r_wheel_Link")]
    with np.load(npz_path, allow_pickle=False) as z:
        # Do not materialize obs/actions/full_qpos/full_qvel/torque members.
        t = np.asarray(z["time"]).copy()
        pos = np.asarray(z["body_position"]).copy()
        quat = np.asarray(z["body_quaternion_wxyz"]).copy()
        bottom = np.asarray(z["wheel_bottom_world_z"]).copy()
        contact = np.asarray(z["wheel_normal_contact_N"]).copy()
    require(t.ndim==1 and len(t)>=2 and np.isfinite(t).all() and (np.diff(t)>0).all(),"capture needs finite increasing measured sample times")
    require(pos.shape == (len(t),len(names),3) and quat.shape == (len(t),len(names),4), "XML/capture body order mismatch")
    source = dict(repository="https://github.com/yly-true/fudan_rl_wheel_leg", commit=FUDAN_COMMIT,
                  artifact_path=str(npz_path), artifact_sha256=producer_receipt.get("artifact_sha256"),
                  body_order_source="pinned_include_free_MJCF_preorder_plus_world",
                  quaternion="wxyz", wheel_order=["left","right"],
                  foreign_transitions_for_native_world_model=False,
                  original_case=case_summary["case"], capture_complete=True,
                  contact_threshold_n=float(normal_contact_threshold_n),
                  source_jump_validation=producer_receipt.get("source_jump_validation", "pending"),
                  not_our_step270_success=True)
    clock = dict(time_basis="measured_simulation_time_s", **case_summary["model_timestep"],
                 source_sample_dt_min_s=float(np.diff(t).min()), source_sample_dt_max_s=float(np.diff(t).max()))
    data = dict(schema=SCHEMA,source=source,clock=clock,time_s=t.tolist(),
                chassis_position_m=pos[:,ids[0]].tolist(),chassis_quaternion_wxyz=quat[:,ids[0]].tolist(),
                wheel_center_m=pos[:,ids[1:]].tolist(),wheel_bottom_world_z_m=bottom.tolist(),
                wheel_contact=(contact > normal_contact_threshold_n).tolist(),
                provenance_kind="measured_original_robot_reference")
    return TaskspaceDemo.from_dict(data)


@dataclass(frozen=True)
class RetargetTaskspace:
    time_s: np.ndarray
    root_position_m: np.ndarray
    root_quaternion_wxyz: np.ndarray
    wheel_local_m: np.ndarray
    wheel_contact: np.ndarray
    contact_phase: tuple[str,...]
    metadata: dict


def retarget_taskspace(demo, own_nominal_wheel_local_m, own_root_start_m,
                       target_heading_rad=0., target_control_dt_s=.01,
                       start_s=None, end_s=None):
    """Preserve observed motion; scale relative limb excursions using each robot's rest geometry.

    No added forward travel, step rise, root impulse, gate, action, or joint-angle copy.
    A flat standing jump therefore remains a flat standing jump reference, with explicit
    task-coverage pending; it is never relabeled a successful 270 mm step demonstration.
    """
    own_wheel = array(own_nominal_wheel_local_m,(2,3),"own wheel rest geometry")
    own_root = array(own_root_start_m,(3,),"own root start")
    d = demo.resample(target_control_dt_s,start_s,end_s)
    r = quat_to_mat(d.chassis_quaternion_wxyz)
    local = np.einsum("tji,twj->twi",r,d.wheel_center_m-d.chassis_position_m[:,None,:])
    source_leg = float(np.linalg.norm(local[0][:,[0,2]],axis=-1).mean())
    target_leg = float(np.linalg.norm(own_wheel[:,[0,2]],axis=-1).mean())
    require(source_leg > 0 and target_leg > 0, "zero baseline leg geometry")
    leg_scale = target_leg/source_leg
    source_span = abs(local[0,0,1]-local[0,1,1]); own_span = abs(own_wheel[0,1]-own_wheel[1,1])
    require(source_span > 0 and own_span > 0, "zero wheel track width")
    scale = np.array([leg_scale, own_span/source_span, leg_scale])
    wheels = own_wheel+(local-local[0])*scale
    source_yaw = math.atan2(r[0,1,0],r[0,0,0])
    angle = float(target_heading_rad)-source_yaw
    c,s = math.cos(angle),math.sin(angle)
    align = np.array([[c,-s,0],[s,c,0],[0,0,1]])
    # Scale in the source heading frame, then rotate into the target heading.
    # Scaling after world-frame rotation would break heading equivariance.
    sc,ss=math.cos(source_yaw),math.sin(source_yaw)
    source_heading=np.array([[sc,-ss,0],[ss,sc,0],[0,0,1]])
    tc,ts=math.cos(target_heading_rad),math.sin(target_heading_rad)
    target_heading=np.array([[tc,-ts,0],[ts,tc,0],[0,0,1]])
    root=own_root+((d.chassis_position_m-d.chassis_position_m[0])@source_heading*scale)@target_heading.T
    rotation = align@r
    phases = tuple("both_supported" if a and b else "flight" if not (a or b)
                   else "left_supported" if a else "right_supported" for a,b in d.wheel_contact)
    metadata = dict(schema="mod4.supermimic.taskspace_retarget.v1", source=d.source,
                    source_clock=d.clock,target_control_dt_s=float(target_control_dt_s),
                    source_baseline_leg_m=source_leg,target_baseline_leg_m=target_leg,
                    scale_xyz=scale.tolist(),body_angle_copy=False,foreign_action_copy=False,
                    source_motion_preserved_no_synthetic_step_or_forward_displacement=True,
                    closed_chain_IK="pending", dynamic_actuation_feasibility="pending",
                    H1_dualwheel270mm_cross_topcontact_200callback_recovery="not_demonstrated",
                    provenance_kind=d.provenance_kind,
                    reference_role="partial_jump_shape_reference",
                    task_coverage=dict(source_jump="pending_source_validation",H1_step270=False,
                                       H1_forward_arrival=False,H1_top_contact_and_recovery=False),
                    native_frame_zero_reference_time_s=0.)
    return RetargetTaskspace(d.time_s-d.time_s[0],root,continuous_quat(mat_to_quat(rotation)),
                            wheels,d.wheel_contact,phases,metadata)


class NativeReference:
    """Reference-only 73-state tensor/NumPy loader with explicit native joint-name mapping.

    The caller supplies a complete own-robot kinematic clip. A pending/failed solve,
    synthetic fixture, or unverified SDK order cannot be used for production goals.
    Target velocities are derivatives of retargeted states, not foreign qvel/actions.
    """
    def __init__(self, times_s, packed73, joint_names, metadata, *, allow_fixture=False):
        t=np.asarray(times_s,dtype=float); n=len(t)
        require(t.shape==(n,) and n>=2 and np.isfinite(t).all() and np.all(np.diff(t)>0), "bad native times")
        states=array(packed73,(n,73),"native packed73")
        require(len(joint_names)==30 and len(set(joint_names))==30, "30 unique native joint names required")
        require(metadata.get("kinematic_pose_contract") == "passed_for_all_exported_frames", "kinematic reference pending/failed")
        require(metadata.get("foreign_transitions_for_native_world_model") is False, "reference may not seed WM dynamics")
        if not allow_fixture:
            require(metadata.get("provenance_kind") == "measured_original_robot_reference", "synthetic fixture cannot become a training demonstration")
            require(metadata.get("source_jump_validation") == "observed_jump_validated", "original jump reference validation pending")
        require(bool(np.all(abs(np.linalg.norm(states[:,3:7],axis=-1)-1)<.001)), "native quaternion must be unit wxyz")
        self.times_s=t; self.states=states.copy(); self.states[:,3:7]=continuous_quat(states[:,3:7])
        self.joint_names=tuple(joint_names); self.metadata=dict(metadata); self.allow_fixture=allow_fixture
        mask=np.asarray(metadata.get("conditioning_feature_mask73"),dtype=bool)
        require(mask.shape==(73,),"explicit packed-state conditioning mask73 required")
        self.conditioning_mask73=mask
        dt=metadata.get("target_control_dt_s")
        require(isinstance(dt,(int,float)) and np.isfinite(dt) and dt>0,"explicit positive target control clock required")

    @classmethod
    def from_dict(cls,data,*,allow_fixture=False):
        require(data.get("schema")==NATIVE_SCHEMA,"wrong native reference schema")
        require(set(data)=={"schema","times_s","packed73","joint_names","metadata"},"unexpected native reference fields")
        return cls(data["times_s"],data["packed73"],data["joint_names"],data["metadata"],allow_fixture=allow_fixture)

    def as_dict(self):
        return dict(schema=NATIVE_SCHEMA,times_s=self.times_s.tolist(),packed73=self.states.tolist(),
                    joint_names=list(self.joint_names),metadata=self.metadata)

    def for_sdk_joint_order(self,sdk_joint_names):
        names=tuple(sdk_joint_names)
        require(len(names)==30 and len(set(names))==30 and set(names)==set(self.joint_names), "native SDK joint names mismatch")
        ids=np.array([self.joint_names.index(n) for n in names]); out=self.states.copy()
        out[:,13:43]=self.states[:,13+ids]; out[:,43:73]=self.states[:,43+ids]
        mask=self.conditioning_mask73.copy()
        mask[13:43]=self.conditioning_mask73[13+ids];mask[43:73]=self.conditioning_mask73[43+ids]
        meta=dict(self.metadata,sdk_joint_order_verified=True,conditioning_feature_mask73=mask.tolist())
        if "joint_position_range_scale30" in meta:
            meta["joint_position_range_scale30"]=array(meta["joint_position_range_scale30"],(30,),"joint range scales")[ids].tolist()
        return NativeReference(self.times_s,out,names,meta,allow_fixture=self.allow_fixture)

    def align_control_clock(self,*,native_frame_anchor,reference_time_anchor_s):
        """Explicit reviewed phase alignment; no reading of future plant gates/actions."""
        require(np.isfinite(native_frame_anchor) and np.isfinite(reference_time_anchor_s),"finite reference clock anchors required")
        require(self.times_s[0]<=reference_time_anchor_s<=self.times_s[-1],"reference clock anchor outside clip")
        offset=float(reference_time_anchor_s)-float(native_frame_anchor)*float(self.metadata["target_control_dt_s"])
        meta=dict(self.metadata,native_frame_zero_reference_time_s=offset,
                  clock_alignment=dict(native_frame_anchor=float(native_frame_anchor),reference_time_anchor_s=float(reference_time_anchor_s),
                                       uses_future_actions_or_gate_choices=False))
        return NativeReference(self.times_s,self.states,self.joint_names,meta,allow_fixture=self.allow_fixture)

    def at_time(self,query_times_s):
        """Explicit hold at both endpoints; interpolate only retargeted states."""
        q=np.asarray(query_times_s,dtype=float); require(bool(np.isfinite(q).all()),"non-finite query")
        clipped=np.clip(q,self.times_s[0],self.times_s[-1])
        lo=np.clip(np.searchsorted(self.times_s,clipped,side="right")-1,0,len(self.times_s)-2)
        alpha=(clipped-self.times_s[lo])/(self.times_s[lo+1]-self.times_s[lo])
        result=(1-alpha[...,None])*self.states[lo]+alpha[...,None]*self.states[lo+1]
        result[...,3:7]=slerp(self.states[lo,3:7],self.states[lo+1,3:7],alpha)
        return result

    def goal_frames_numpy(self,frames,num_frames,control_dt_s):
        require(num_frames>=1 and isinstance(num_frames,int),"positive integer goal window required")
        require(np.isfinite(control_dt_s) and control_dt_s>0,"positive native control clock required")
        f=np.asarray(frames,dtype=float)
        offset=float(self.metadata.get("native_frame_zero_reference_time_s",0.))
        return np.concatenate([self.at_time((f+i)*control_dt_s+offset)*self.conditioning_mask73
                               for i in range(num_frames)],-1)

    def torch_provider(self,device="cpu",*,allow_fixture=False):
        require(self.metadata.get("sdk_joint_order_verified") is True,"call for_sdk_joint_order(actual robot.joint_names) first")
        require(allow_fixture or not self.allow_fixture,"fixture torch provider requires explicit CPU test flag")
        return TorchReferenceGoalProvider(self,device,allow_fixture=allow_fixture)


class TorchReferenceGoalProvider:
    """Drop-in goal/reference source; imports torch only when explicitly instantiated.

    Add to an H1GoalMdp subclass and override goal() plus to(). Inherited native
    reward then calls the overridden goal, retaining the current reward coefficients.
    No WM replay write or hidden applied-action/gate inputs exist here.
    """
    goal_frame_dim=73

    def __init__(self,reference,device="cpu",*,allow_fixture=False):
        import torch
        self._torch=torch; self.reference=reference; self.allow_fixture=allow_fixture
        require(not allow_fixture or str(device)=="cpu","synthetic contract fixtures are CPU only")
        self.times=torch.as_tensor(reference.times_s,dtype=torch.float32,device=device)
        self.states=torch.as_tensor(reference.states,dtype=torch.float32,device=device)
        self.mask=torch.as_tensor(reference.conditioning_mask73,dtype=torch.float32,device=device)
        self.control_dt_s=float(reference.metadata["target_control_dt_s"])
        self.first_time_s=float(reference.times_s[0]);self.last_time_s=float(reference.times_s[-1])

    def to(self,device):
        return TorchReferenceGoalProvider(self.reference,device,allow_fixture=self.allow_fixture)

    def _evaluate(self,frames,num_frames,*,mask):
        torch=self._torch
        require(isinstance(num_frames,int) and num_frames>=1,"positive goal window required")
        require(frames.device==self.states.device,"reference and native frame device mismatch")
        if frames.is_floating_point():
            require(bool(torch.isfinite(frames).all()),"non-finite frame query")
        all_goals=[]
        for offset in range(num_frames):
            times=((frames.float()+offset)*self.control_dt_s+float(self.reference.metadata.get("native_frame_zero_reference_time_s",0.))).clamp(self.first_time_s,self.last_time_s)
            lo=(torch.searchsorted(self.times,times.contiguous(),right=True)-1).clamp(0,len(self.times)-2)
            a=((times-self.times[lo])/(self.times[lo+1]-self.times[lo]))[...,None]
            result=(1-a)*self.states[lo]+a*self.states[lo+1]
            first,second=self.states[lo,3:7],self.states[lo+1,3:7]
            dot=(first*second).sum(-1,keepdim=True)
            second=torch.where(dot<0,-second,second);dot=dot.abs().clamp(0,1)
            theta=torch.acos(dot);sine=torch.sin(theta)
            # Clamp only the inactive numerical denominator; no new physical gate.
            wa=torch.where(sine<1e-6,1-a,torch.sin((1-a)*theta)/sine.clamp_min(1e-12))
            wb=torch.where(sine<1e-6,a,torch.sin(a*theta)/sine.clamp_min(1e-12))
            result[...,3:7]=torch.nn.functional.normalize(wa*first+wb*second,dim=-1)
            all_goals.append(result*self.mask if mask else result)
        return torch.cat(all_goals,-1)

    def goal(self,frames,num_frames):
        return self._evaluate(frames,num_frames,mask=True)

    def raw_reference_at_frames(self,frames,num_frames=1):
        return self._evaluate(frames,num_frames,mask=False)

    def reference_at_frames(self,frames,num_frames=1):
        return self.goal(frames,num_frames)


class ReferenceConditioningMdp:
    """Composition wrapper for a PARTIAL demonstration and the unchanged task MDP.

    Native goal() is a packed state, not invariant_features(). In the current H1
    implementation inherited reward() would track self.goal's world X/Y. Calling
    base.reward explicitly keeps its existing task objective, and avoids scoring
    an unobserved standing-jump forward path. Reference values condition the native
    policy; they are not forced actions, a new reward, or foreign WM transitions.

    The static mask is applied to goal channels; it is not concatenated, so the
    actor observation128/history10 and goal73 dimensions remain unchanged. The
    metadata carries the mask semantics. Do not unflatten a masked goal as a full
    physical state or use it as a WM target. Unmasked states remain in reference.
    """
    def __init__(self,base_mdp,provider):
        require(base_mdp.goal_frame_dim==73,"native base goal dimension changed")
        require(provider.reference.metadata.get("reference_role") in ("partial_jump_shape_conditioning_only","partial_jump_shape_reference"),
                "this wrapper is explicitly reviewed only for partial jump conditioning")
        self.base=base_mdp;self.provider=provider

    def __getattr__(self,name):
        return getattr(self.base,name)

    def to(self,device):
        return ReferenceConditioningMdp(self.base.to(device),self.provider.to(device))

    def goal(self,frames,num_frames):
        return self.provider.goal(frames,num_frames)

    def reference_at_frames(self,frames,num_frames=1):
        return self.goal(frames,num_frames)

    def reward(self,state,frames,action,previous_action):
        # Keep the method bound to base: base.reward's self.goal remains the task
        # objective, never the stationary foreign reference's world XY.
        return self.base.reward(state,frames,action,previous_action)


@dataclass(frozen=True)
class PartialImitationObjectiveConfig:
    """Reviewed formula candidate; runtime/loss admission is explicitly pending.

    Costs below are dimensionless after the named SI/range normalizations. They
    do not change the real V8 RewardManager and are not claimed trained weights.
    """
    own_task_x_weight: float=5.
    own_task_y_weight: float=5.
    demo_height_weight_per_m2: float=15.
    demo_orientation_frobenius_weight: float=2.
    demo_vertical_velocity_weight_per_m2_s2: float=.1
    demo_angular_velocity_weight_per_rad2_s2: float=.02
    demo_joint_position_range_weight: float=2.
    demo_joint_velocity_range_weight: float=.01
    joint_velocity_reference_timescale_s: float=.1
    action_change_weight: float=.001
    speed_regularization_weight: float=.001
    joint_speed_regularization_weight: float=.0001
    admission: str="source_CPU_candidate_runtime_loss_admission_pending"


class PartialReferenceImitationMdp:
    """Actual partial-demo alignment in native imagination; physical V8 untouched.

    The old analytic root Z curve is NOT scored in this candidate. Own task X
    and Y progress remain separate task terms (the existing base.goal X and Y=0),
    never relabeled as Fudan motion. Demo alignment scores retargeted height,
    orientation, vertical/angular velocity and observed own leg q/dq only. World
    XY/XY velocity and unidentifiable wheel/roller spins are excluded from demo
    alignment. No future applied action or physical phase/gate is accepted.

    This replaces only native H1GoalMdp.reward's IMAGINATION SURROGATE when a caller
    deliberately installs it. It does not touch Bridge.step()/V8 RewardManager,
    real command/success, WM data source or architecture, policy inference, or
    physical sampling. The conditioning-only wrapper above is a preserved earlier
    alternative; it is not the proposed demonstration-transfer objective.
    """
    def __init__(self,base_mdp,provider,config=None):
        require(base_mdp.goal_frame_dim==73,"native goal73 required")
        require(provider.reference.metadata.get("reference_role") in ("partial_jump_shape_conditioning_only","partial_jump_shape_reference"),
                "partial jump objective requires an explicitly partial reference")
        self.base=base_mdp;self.provider=provider;self.config=config or PartialImitationObjectiveConfig()
        require(self.config.joint_velocity_reference_timescale_s>0,"positive joint velocity normalization timescale required")
        scales=array(provider.reference.metadata.get("joint_position_range_scale30"),(30,),"own joint position scale30")
        require(bool((scales>0).all()),"own joint range scales must be positive")
        self.joint_scale=provider._torch.as_tensor(scales,dtype=provider.states.dtype,device=provider.states.device)
        self.qmask=provider.mask[13:43]
        self.dqmask=provider.mask[43:73]
        require(bool((provider.mask[[0,1,7,8]]==0).all()),"partial demo cannot claim XY motion coverage")

    def __getattr__(self,name):return getattr(self.base,name)

    def to(self,device):
        return PartialReferenceImitationMdp(self.base.to(device),self.provider.to(device),self.config)

    def goal(self,frames,num_frames):return self.provider.goal(frames,num_frames)

    def reference_at_frames(self,frames,num_frames=1):return self.goal(frames,num_frames)

    def objective_terms(self,state,frames,action,previous_action):
        torch=self.provider._torch;c=self.config
        position,rotation,velocity,angular_velocity,joint_pos,joint_vel=state
        target=self.provider.raw_reference_at_frames(frames)
        task_target=self.base.goal(frames,1)
        own_task_forward=torch.exp(-c.own_task_x_weight*(position[...,0]-task_target[...,0]).square()
                                   -c.own_task_y_weight*position[...,1].square())
        w,x,y,z=target[...,3:7].unbind(-1)
        desired_rotation=torch.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),
                                      2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),
                                      2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1).reshape(rotation.shape)
        height_cost=c.demo_height_weight_per_m2*(position[...,2]-target[...,2]).square()
        rotation_cost=c.demo_orientation_frobenius_weight*(rotation-desired_rotation).square().mean((-1,-2))
        vertical_velocity_cost=c.demo_vertical_velocity_weight_per_m2_s2*(velocity[...,2]-target[...,9]).square()
        angular_velocity_cost=c.demo_angular_velocity_weight_per_rad2_s2*(angular_velocity-target[...,10:13]).square().mean(-1)
        qcost=((joint_pos-target[...,13:43])/self.joint_scale).square()*self.qmask
        vscale=self.joint_scale/c.joint_velocity_reference_timescale_s
        dqcost=((joint_vel-target[...,43:73])/vscale).square()*self.dqmask
        joint_position_cost=c.demo_joint_position_range_weight*qcost.sum(-1)/self.qmask.sum().clamp_min(1)
        joint_velocity_cost=c.demo_joint_velocity_range_weight*dqcost.sum(-1)/self.dqmask.sum().clamp_min(1)
        demo_cost=height_cost+rotation_cost+vertical_velocity_cost+angular_velocity_cost+joint_position_cost+joint_velocity_cost
        demo_alignment=torch.exp(-demo_cost)
        upright=((rotation[...,2,2]+1)*.5).clamp(0,1)
        regularization=c.action_change_weight*(action-previous_action).square().mean(-1)
        regularization=regularization+c.speed_regularization_weight*velocity.square().mean(-1)+c.joint_speed_regularization_weight*joint_vel.square().mean(-1)
        total=own_task_forward*upright*demo_alignment-regularization
        return dict(total=total,own_task_forward=own_task_forward,demo_alignment=demo_alignment,
                    demo_height_cost=height_cost,demo_orientation_cost=rotation_cost,
                    demo_vertical_velocity_cost=vertical_velocity_cost,demo_angular_velocity_cost=angular_velocity_cost,
                    demo_joint_position_cost=joint_position_cost,demo_joint_velocity_cost=joint_velocity_cost,
                    upright=upright,regularization=regularization)

    def reward(self,state,frames,action,previous_action):
        return self.objective_terms(state,frames,action,previous_action)["total"]

    def contract_manifest(self):
        """Metadata for root's save/admission protocol; does not write external state."""
        return dict(schema="mod4.supermimic.partial_reference_objective_contract.v1",
                    candidate_admission=self.config.admission,config=asdict(self.config),
                    reference_metadata=self.provider.reference.metadata,
                    native_goal_dim=73,native_obs_dim=128,native_history=10,native_actions=6,native_joints=30,
                    packed_goal_layout="XYZ_wxyz_world_v_world_w_q30_dq30",
                    invariant_feature_layout="Z_headingfree6D_body_v_body_w_q30_dq30",
                    raw_goals_include_world_XY=True,invariant_features_remove_world_XY=True,
                    own_task_forward="existing_native_base_goal_X_and_Y0_only_not_Fudan_coverage",
                    own_task_analytic_height_curve="excluded_from_this_imagination_surrogate",
                    demo_alignment="retargeted_Z_orientation_Vz_world_angular_velocity_leg_q_dq",
                    demo_XY_and_XY_velocity_and_unobserved_spins="excluded_by_explicit_mask",
                    source_contact="reference_only_not_an_applied_action_or_physical_gate",
                    native_world_model="only_actual_own_plant_executed_transitions",
                    physical_reward="existing_V8_RewardManager_unchanged",
                    physical_H1="2.5ms_TGS32_4_100Hz_decimation4_unchanged",
                    H1_success="actual_dualwheel270mm_cross_topcontact_200callbacks_0.5s_recovery_unchanged",
                    closed_chain_protection="existing_2mm_per_env_reset_not_batch_stop",
                    frozen_E0_W35_and_qualified_models="retained_no_model_loading_by_adapter",
                    does_not_admit_environment_training_or_skill_graduation=True)


def read_json_reference(path,*,allow_fixture=False):
    return NativeReference.from_dict(json.loads(Path(path).read_text(encoding="utf8")),allow_fixture=allow_fixture)
