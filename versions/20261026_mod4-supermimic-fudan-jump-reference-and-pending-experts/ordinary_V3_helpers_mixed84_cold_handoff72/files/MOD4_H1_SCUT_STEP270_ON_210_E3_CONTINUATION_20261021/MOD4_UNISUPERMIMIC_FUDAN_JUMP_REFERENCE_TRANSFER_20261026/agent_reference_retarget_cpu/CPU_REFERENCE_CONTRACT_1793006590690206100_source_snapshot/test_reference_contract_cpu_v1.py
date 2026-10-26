"""Meaningful CPU-only adapter contracts. Every invocation saves a new attempt report.

No ONNX/PT/model load, actor forward, optimizer, RNG, plant, GPU, network or Git.
--own-usd enables only the explicitly authorized own-USD static kinematic checks.
--torch enables tensor arithmetic parity and partial-reference reward binding tests.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import sys
import time
import traceback
import unittest

import numpy as np

from supermimic_reference_adapter_v1 import (
    SCHEMA, TASK_REGISTRY, NativeReference, PendingReferenceError,
    ReferenceConditioningMdp, PartialReferenceImitationMdp, ReferenceContractError, TaskspaceDemo,
    angular_velocity_world, import_new_fudan_capture, invariant_features_numpy,
    mat_to_quat, quat_to_mat, retarget_taskspace, slerp,
    with_partial_step270_phase_contract,
)

HERE=Path(__file__).resolve().parent
T=HERE.parents[1]
OWN_USD=False
TORCH=False


def demo_fixture(n=31,dt=.002,standing=True):
    t=np.arange(n)*dt; phase=np.linspace(0,1,n)
    q=np.tile([1.,0,0,0],(n,1))
    p=np.stack((np.zeros(n) if standing else .02*phase,np.zeros(n),.4+.02*np.sin(math.pi*phase)),-1)
    local=np.tile(np.array([[0.,.2,-.25],[0.,-.2,-.25]]),(n,1,1))
    wheels=p[:,None,:]+local
    contact=np.ones((n,2),dtype=bool);contact[n//3:2*n//3]=False
    source=dict(quaternion="wxyz",wheel_order=["left","right"],foreign_transitions_for_native_world_model=False,
                fixture=True,not_real_demonstration=True)
    clock=dict(time_basis="measured_simulation_time_s",original_timestep=.002,actual_timestep=.002,
               script_declared_sim_dt_s=.005)
    return TaskspaceDemo.from_dict(dict(schema=SCHEMA,source=source,clock=clock,time_s=t.tolist(),
        chassis_position_m=p.tolist(),chassis_quaternion_wxyz=q.tolist(),wheel_center_m=wheels.tolist(),
        wheel_bottom_world_z_m=(wheels[:,:,2]-.06).tolist(),wheel_contact=contact.tolist(),
        provenance_kind="synthetic_CPU_contract_fixture"))


def native_fixture():
    states=np.zeros((3,73));states[:,3]=1;states[:,2]=[.3,.4,.3]
    states[:,0]=[0,.1,.2];states[:,7]=10
    states[:,13:43]=np.arange(30)[None,:]+np.arange(3)[:,None]*.1
    states[:,43:73]=100+np.arange(30)[None,:]
    mask=np.ones(73,dtype=bool);mask[[0,1,7,8,13+1,43+1]]=False
    meta=dict(kinematic_pose_contract="passed_for_all_exported_frames",foreign_transitions_for_native_world_model=False,
              provenance_kind="synthetic_CPU_contract_fixture",conditioning_feature_mask73=mask.tolist(),
              target_control_dt_s=.01,reference_role="partial_jump_shape_conditioning_only",
              joint_position_range_scale30=(1+np.arange(30)/30).tolist())
    ref=NativeReference([0,.01,.02],states,[f"joint{i}" for i in range(30)],meta,allow_fixture=True)
    return with_partial_step270_phase_contract(ref,measured_ascent_end_reference_time_s=.015,
        own_nominal_chassis_height_m=.3)


class CanonicalContracts(unittest.TestCase):
    def test_01_reject_foreign_actions_nonfinite_and_repeated_time(self):
        source=demo_fixture().as_dict()
        bad=copy.deepcopy(source);bad["raw_action6"]=[[1]*6]*len(bad["time_s"])
        with self.assertRaisesRegex(ReferenceContractError,"unexpected"):TaskspaceDemo.from_dict(bad)
        bad=copy.deepcopy(source);bad["chassis_position_m"][0][0]=float("nan")
        with self.assertRaisesRegex(ReferenceContractError,"non-finite"):TaskspaceDemo.from_dict(bad)
        bad=copy.deepcopy(source);bad["time_s"][1]=bad["time_s"][0]
        with self.assertRaisesRegex(ReferenceContractError,"strictly increasing"):TaskspaceDemo.from_dict(bad)

    def test_02_wxyz_rotation_and_antipodal_interpolation(self):
        q=np.array([[math.cos(.35),0,0,math.sin(.35)],[-math.cos(.35),0,0,-math.sin(.35)]])
        np.testing.assert_allclose(quat_to_mat(slerp(q[0],q[1],.5)),quat_to_mat(q[0]),atol=1e-12)
        np.testing.assert_allclose(quat_to_mat(mat_to_quat(quat_to_mat(q))),quat_to_mat(q),atol=1e-12)
        t=np.linspace(0,.1,51);rotation=np.stack((np.cos(t),t*0,t*0,np.sin(t)),-1)
        np.testing.assert_allclose(angular_velocity_world(rotation,t)[:,2],2,atol=1e-5)

    def test_03_actual_clock_is_not_declared_clock(self):
        demo=demo_fixture();sampled=demo.resample(.01)
        np.testing.assert_allclose(np.diff(sampled.time_s),.01,atol=1e-12)
        self.assertEqual(sampled.clock["actual_timestep"],.002)
        self.assertEqual(sampled.clock["script_declared_sim_dt_s"],.005)
        self.assertEqual(len(sampled.time_s),7)
        with self.assertRaisesRegex(ReferenceContractError,"crop outside"):demo.resample(.01,-1,.05)

    def test_04_contact_resampling_is_causal_hold(self):
        demo=demo_fixture(n=5,dt=.01)
        contact=np.array([[True,True],[False,True],[False,False],[True,False],[True,True]])
        sampled=replace(demo,wheel_contact=contact).resample(.005)
        np.testing.assert_array_equal(sampled.wheel_contact[1],contact[0])
        np.testing.assert_array_equal(sampled.wheel_contact[3],contact[1])
        np.testing.assert_array_equal(sampled.wheel_contact[-1],contact[-1])

    def test_05_standing_jump_does_not_invent_step_or_forward_motion(self):
        own=np.array([[0,.22,-.27],[0,-.22,-.27]])
        retarget=retarget_taskspace(demo_fixture(),own,[.03,0,.34])
        np.testing.assert_allclose(retarget.root_position_m[:,0],.03)
        self.assertFalse(retarget.metadata["task_coverage"]["H1_step270"])
        self.assertFalse(retarget.metadata["task_coverage"]["H1_forward_arrival"])
        self.assertEqual(retarget.metadata["closed_chain_IK"],"pending")
        np.testing.assert_allclose(retarget.wheel_local_m[0],own)

    def test_06_retarget_is_world_translation_and_yaw_equivariant(self):
        demo=demo_fixture(standing=False);angle=.7;c,s=math.cos(angle),math.sin(angle)
        r=np.array([[c,-s,0],[s,c,0],[0,0,1]]);offset=np.array([4.,-8.,.6])
        transformed=replace(demo,chassis_position_m=demo.chassis_position_m@r.T+offset,
                            chassis_quaternion_wxyz=mat_to_quat(r@quat_to_mat(demo.chassis_quaternion_wxyz)),
                            wheel_center_m=demo.wheel_center_m@r.T+offset,
                            wheel_bottom_world_z_m=demo.wheel_bottom_world_z_m+offset[2])
        own=np.array([[0,.22,-.27],[0,-.22,-.27]])
        a=retarget_taskspace(demo,own,[0,0,.34],target_heading_rad=.4)
        b=retarget_taskspace(transformed,own,[0,0,.34],target_heading_rad=.4)
        np.testing.assert_allclose(a.root_position_m,b.root_position_m,atol=1e-12)
        np.testing.assert_allclose(a.wheel_local_m,b.wheel_local_m,atol=1e-12)
        np.testing.assert_allclose(quat_to_mat(a.root_quaternion_wxyz),quat_to_mat(b.root_quaternion_wxyz),atol=1e-12)

    def test_07_native_joint_name_permutation_reorders_q_dq_and_mask(self):
        ref=native_fixture();names=list(reversed(ref.joint_names));permuted=ref.for_sdk_joint_order(names)
        np.testing.assert_allclose(permuted.states[:,13:43],ref.states[:,13:43][:,::-1])
        np.testing.assert_allclose(permuted.states[:,43:73],ref.states[:,43:73][:,::-1])
        np.testing.assert_array_equal(permuted.conditioning_mask73[13:43],ref.conditioning_mask73[13:43][::-1])
        np.testing.assert_allclose(permuted.metadata["joint_position_range_scale30"],ref.metadata["joint_position_range_scale30"][::-1])
        self.assertTrue(permuted.metadata["sdk_joint_order_verified"])
        with self.assertRaisesRegex(ReferenceContractError,"SDK joint names mismatch"):
            ref.for_sdk_joint_order(["foreign"]*30)

    def test_08_masked_goals_hold_endpoints_and_have_no_forward_penalty_channel(self):
        ref=native_fixture();got=ref.goal_frames_numpy(np.array([[-5.,.5],[2.,1000.]]),2,.01)
        self.assertEqual(got.shape,(2,2,146))
        np.testing.assert_allclose(got[...,0],0);np.testing.assert_allclose(got[...,7],0)
        np.testing.assert_allclose(got[...,73],0)
        np.testing.assert_allclose(ref.at_time(-1),ref.states[0])
        np.testing.assert_allclose(ref.at_time(100),ref.states[-1])
        with self.assertRaisesRegex(ReferenceContractError,"kinematic reference pending"):
            NativeReference([0,.01],np.zeros((2,73)),list(ref.joint_names),{},allow_fixture=True)
        with self.assertRaisesRegex(ReferenceContractError,"synthetic fixture"):
            NativeReference(ref.times_s,ref.states,ref.joint_names,ref.metadata)

    def test_09_invariant_features_remove_world_xy_but_raw_goals_do_not(self):
        states=native_fixture().states.copy();shifted=states.copy();shifted[:,:2]+=[5,-7]
        self.assertEqual(invariant_features_numpy(states).shape,(3,73))
        np.testing.assert_allclose(invariant_features_numpy(states),invariant_features_numpy(shifted))
        self.assertNotEqual(states[0,0],shifted[0,0])
        # Raw packed goal layout and native invariant layout have the SAME size;
        # size alone never licenses applying one layout's feature mask to the other.
        self.assertAlmostEqual(float(invariant_features_numpy(states)[0,0]),states[0,2])

    def test_10_eight_skill_registry_is_queue_not_environment_admission(self):
        self.assertEqual(len(TASK_REGISTRY),8)
        for name in ("H1_step270","E2_world_moving","E3_recovery"):
            row=TASK_REGISTRY[name];self.assertAlmostEqual(row.control_dt_s,row.physics_dt_s*row.decimation)
            self.assertIn("not_Task_GO",row.admission)
        self.assertIsNone(TASK_REGISTRY["continuous_stairs"].control_dt_s)

    def test_11_unverified_capture_is_rejected_before_file_io(self):
        with self.assertRaisesRegex(ReferenceContractError,"authorization receipt"):
            import_new_fudan_capture("UNREAD_NPZ","UNREAD_XML",{}, {})

    def test_18_reference_clock_anchor_is_explicit_and_not_a_future_gate(self):
        ref=native_fixture();aligned=ref.align_control_clock(native_frame_anchor=100,reference_time_anchor_s=.01)
        np.testing.assert_allclose(aligned.goal_frames_numpy(np.array([100.]),1,.01),ref.goal_frames_numpy(np.array([1.]),1,.01))
        self.assertFalse(aligned.metadata["clock_alignment"]["uses_future_actions_or_gate_choices"])


class TorchContracts(unittest.TestCase):
    def setUp(self):
        if not TORCH:self.skipTest("explicit --torch not selected")

    def test_12_tensor_goal_matches_numpy_multiframe_mask_and_quaternion(self):
        import torch
        ref=native_fixture().for_sdk_joint_order(native_fixture().joint_names)
        provider=ref.torch_provider("cpu",allow_fixture=True)
        frames=torch.tensor([[0.,.5],[1.,2000.]],dtype=torch.float32)
        np.testing.assert_allclose(provider.goal(frames,3).numpy(),ref.goal_frames_numpy(frames.numpy(),3,.01),atol=2e-6)
        self.assertEqual(tuple(provider.goal(frames,3).shape),(2,2,219))
        self.assertEqual(provider.to("cpu").control_dt_s,.01)

    def test_13_partial_reference_keeps_original_bound_reward(self):
        import torch
        class Base:
            goal_frame_dim=73;obs_dim=128
            def goal(self,frames,num_frames):return frames+5
            def reward(self,state,frames,action,previous_action):return self.goal(frames,1)
            def to(self,device):return self
        ref=native_fixture().for_sdk_joint_order(native_fixture().joint_names)
        wrapper=ReferenceConditioningMdp(Base(),ref.torch_provider("cpu",allow_fixture=True))
        frames=torch.tensor([0.,1.,2.])
        np.testing.assert_allclose(wrapper.reward(None,frames,None,None).numpy(),[5,6,7])
        np.testing.assert_allclose(wrapper.goal(frames,1)[:,0].numpy(),0)
        self.assertEqual(wrapper.obs_dim,128)
        self.assertEqual(wrapper.to("cpu").obs_dim,128)

    def test_19_demo_objective_aligns_pose_without_stationary_forward_or_legacy_height(self):
        import torch
        class Base:
            goal_frame_dim=73;obs_dim=128;legacy_z=999.
            def goal(self,frames,num_frames):
                target=torch.zeros((*frames.shape,73),dtype=torch.float32);target[...,0]=.15;target[...,2]=self.legacy_z
                return target
            def reward(self,*args):raise AssertionError("legacy root-only reward must not score the new candidate")
            def to(self,device):return self
        ref=native_fixture().for_sdk_joint_order(native_fixture().joint_names)
        provider=ref.torch_provider("cpu",allow_fixture=True);base=Base();mdp=PartialReferenceImitationMdp(base,provider)
        frames=torch.tensor([0.,1.,2.]);target=provider.raw_reference_at_frames(frames)
        position=target[:,:3].clone();position[:,0]=.15;position[:,1]=0
        state=(position,torch.eye(3).expand(3,3,3).clone(),target[:,7:10].clone(),target[:,10:13].clone(),target[:,13:43].clone(),target[:,43:73].clone())
        zero=torch.zeros((3,6));terms=mdp.objective_terms(state,frames,zero,zero)
        np.testing.assert_allclose(terms["demo_alignment"].numpy(),1,atol=1e-6)
        np.testing.assert_allclose(terms["own_task_forward"].numpy(),1,atol=1e-6)
        initial=terms["total"].clone();base.legacy_z=-999.
        torch.testing.assert_close(mdp.reward(state,frames,zero,zero),initial)
        # These are excluded source channels, not own task progress objectives.
        changed=ref.states.copy();changed[:,0]+=500;changed[:,7]+=900;changed[:,14]+=100;changed[:,44]+=100
        other=NativeReference(ref.times_s,changed,ref.joint_names,ref.metadata,allow_fixture=True)
        other_mdp=PartialReferenceImitationMdp(base,other.torch_provider("cpu",allow_fixture=True))
        torch.testing.assert_close(other_mdp.reward(state,frames,zero,zero),initial)
        raised=list(state);raised[0]=position.clone();raised[0][:,2]+=.1
        phase_terms=mdp.objective_terms(tuple(raised),frames,zero,zero)
        self.assertTrue(bool((phase_terms["demo_alignment"][:2]<1).all()))
        self.assertEqual(float(phase_terms["demo_height_cost"][-1]),0.)
        leg=list(state);leg[4]=state[4].clone();leg[4][:,2]+=.2
        self.assertTrue(bool((mdp.objective_terms(tuple(leg),frames,zero,zero)["demo_joint_position_cost"]>0).all()))
        behind=list(state);behind[0]=position.clone();behind[0][:,0]-=.1
        self.assertTrue(bool((mdp.objective_terms(tuple(behind),frames,zero,zero)["own_task_forward"]<1).all()))

    def test_20_partial_imitation_is_differentiable_cpu_math_without_actor(self):
        import torch
        class Base:
            goal_frame_dim=73
            def goal(self,f,n):
                value=torch.zeros((*f.shape,73));value[...,0]=.15;return value
            def to(self,device):return self
        ref=native_fixture().for_sdk_joint_order(native_fixture().joint_names)
        provider=ref.torch_provider("cpu",allow_fixture=True);mdp=PartialReferenceImitationMdp(Base(),provider)
        frames=torch.tensor([1.]);target=provider.raw_reference_at_frames(frames)
        pos=target[:,:3].clone().requires_grad_();q=target[:,13:43].clone().requires_grad_()
        qshift=q+torch.nn.functional.one_hot(torch.tensor([2]),30)*.1
        state=(pos,torch.eye(3)[None],target[:,7:10],target[:,10:13],qshift,target[:,43:73])
        zero=torch.zeros((1,6));reward=mdp.reward(state,frames,zero,zero)
        gp,gq=torch.autograd.grad(reward.sum(),(pos,q))
        self.assertTrue(bool(torch.isfinite(gp).all() and torch.isfinite(gq).all()))
        self.assertGreater(float(abs(gp[:,0]).max()),0)
        self.assertGreater(float(abs(gq[:,2]).max()),0)
        # No optimizer, actor forward, random sampling or plant step occurs.

    def test_21_correct_270mm_task_landing_is_not_pulled_to_flat_source_floor(self):
        import torch
        class Base:
            goal_frame_dim=73
            def goal(self,f,n):
                v=torch.zeros((*f.shape,73));v[...,0]=.65;v[...,2]=123.;return v
            def to(self,device):return self
        ref=native_fixture().for_offline_joint_order(native_fixture().joint_names)
        provider=ref.torch_provider("cpu",allow_fixture=True,offline_cpu_only=True)
        mdp=PartialReferenceImitationMdp(Base(),provider);frames=torch.tensor([2.]);target=provider.raw_reference_at_frames(frames)
        position=torch.tensor([[.65,0.,.57]]) # own nominal .30 + own platform .27
        state=(position,torch.eye(3)[None],torch.zeros((1,3)),target[:,10:13],target[:,13:43],target[:,43:73])
        zero=torch.zeros((1,6));terms=mdp.objective_terms(state,frames,zero,zero)
        self.assertEqual(float(terms["demo_height_cost"]),0.);self.assertEqual(float(terms["demo_vertical_velocity_cost"]),0.)
        self.assertAlmostEqual(float(terms["own_task_landing_height_cost"]),0.,places=10)
        source_changed=ref.states.copy();source_changed[-1,2]=-99.;source_changed[-1,9]=999.
        other=NativeReference(ref.times_s,source_changed,ref.joint_names,ref.metadata,allow_fixture=True)
        other_provider=other.torch_provider("cpu",allow_fixture=True,offline_cpu_only=True)
        other_mdp=PartialReferenceImitationMdp(Base(),other_provider)
        torch.testing.assert_close(mdp.reward(state,frames,zero,zero),other_mdp.reward(state,frames,zero,zero))
        self.assertEqual(float(other_provider.goal(frames,1)[0,2]),0.)
        self.assertEqual(float(other_provider.goal(frames,1)[0,9]),0.)
        ground=list(state);ground[0]=position.clone();ground[0][:,2]=.3
        self.assertGreater(float(mdp.reward(state,frames,zero,zero)),float(mdp.reward(tuple(ground),frames,zero,zero)))
        self.assertFalse(provider.reference.metadata["sdk_joint_order_verified"])
        self.assertIn("offline_CPU",mdp.contract_manifest()["provider_execution_scope"])

    def test_22_offline_order_mapping_is_truthful_and_cannot_allocate_GPU(self):
        ref=native_fixture().for_offline_joint_order(list(reversed(native_fixture().joint_names)))
        self.assertFalse(ref.metadata["sdk_joint_order_verified"]);self.assertTrue(ref.metadata["offline_joint_order_verified"])
        provider=ref.torch_provider("cpu",allow_fixture=True,offline_cpu_only=True)
        self.assertFalse(provider.reference.metadata["sdk_joint_order_verified"])
        with self.assertRaisesRegex(ReferenceContractError,"CPU only"):
            provider.to("cuda")


class OwnUsdContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not OWN_USD:raise unittest.SkipTest("explicit --own-usd not selected")
        from own_usd_closed_chain_ik_v1 import OwnUsdKinematics
        assets=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets"
        cls.kin=OwnUsdKinematics.from_sources(assets/"robot.usd",T/"full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json",assets/"import_contract.json")

    def test_14_actual_own_zero_pose_and_closures_fit(self):
        kin=self.kin;target=kin.wheel_local(np.zeros(30));fit=kin.solve(target)
        self.assertEqual(len(kin.variables),16);self.assertEqual(len(kin.closures),6)
        self.assertEqual(fit.status,"STATIC_KINEMATIC_FIT")
        self.assertLess(fit.closure_error_max_m,.002)
        action_ids=[kin.ids[name] for name in ("left_crank","left_hip","right_crank","right_hip","left_wheel_spin","right_wheel_spin")]
        self.assertEqual(len(set(action_ids)),6)
        self.assertTrue(all(kin.joints[i]["kind"]=="PhysicsRevoluteJoint" for i in action_ids))

    def test_15_transmission_uses_physical_parallelism_not_negative_q(self):
        kin=self.kin;q=np.zeros(30);q[kin.ids["left_hip"]]=.1;q=kin.project(q)
        good=kin.diagnostics(q,kin.wheel_local(q));self.assertLess(good["body_parallel_error_frobenius"],1e-5)
        q[kin.ids["left_drive_hip_spin"]]=-.1
        bad=kin.diagnostics(q,kin.wheel_local(q));self.assertGreater(bad["body_parallel_error_frobenius"],.1)

    def test_16_small_retarget_fits_but_unreachable_target_stays_pending(self):
        kin=self.kin;target=kin.wheel_local(np.zeros(30));target[:,0]+=.005;target[:,2]+=.005
        fit=kin.solve(target,max_iterations=50)
        self.assertEqual(fit.status,"STATIC_KINEMATIC_FIT",fit.summary())
        self.assertLessEqual(fit.wheel_error_max_m,.001)
        distant=target.copy();distant[:,2]-=3
        bad=kin.solve(distant,max_iterations=4)
        self.assertEqual(bad.status,"PENDING_UNREACHABLE_OR_IK_NOT_CONVERGED")
        demo=demo_fixture();task=retarget_taskspace(demo,kin.wheel_local(np.zeros(30)),[0,0,.34])
        with self.assertRaisesRegex(PendingReferenceError,"full native reference pending"):
            kin.to_native_reference(task,np.zeros((len(task.time_s),30)),[bad]*len(task.time_s),allow_fixture=True)

    def test_17_full_static_fixture_native_export_retains_pending_dynamics(self):
        kin=self.kin;demo=demo_fixture(standing=False)
        task=retarget_taskspace(demo,kin.wheel_local(np.zeros(30)),[0,0,.34])
        q,results=kin.retarget_clip(task)
        ref=kin.to_native_reference(task,q,results,allow_fixture=True)
        self.assertEqual(ref.states.shape,(7,73))
        self.assertIn("pending",ref.metadata["motor_torque_speed_feasibility"])
        self.assertIn("pending",ref.metadata["collision_nonpenetration"])
        self.assertFalse(ref.metadata["task_coverage"]["H1_step270"])
        self.assertFalse(ref.conditioning_mask73[0]);self.assertFalse(ref.conditioning_mask73[1])
        self.assertFalse(ref.conditioning_mask73[13+kin.ids["left_wheel_spin"]])
        self.assertEqual(ref.metadata["provenance_kind"],"synthetic_CPU_contract_fixture")


class RecordingResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.records=[]
    def addSuccess(self,test):super().addSuccess(test);self.records.append(dict(test=test.id(),status="PASS"))
    def addFailure(self,test,err):super().addFailure(test,err);self.records.append(dict(test=test.id(),status="FAIL",error=self._exc_info_to_string(err,test)))
    def addError(self,test,err):super().addError(test,err);self.records.append(dict(test=test.id(),status="ERROR",error=self._exc_info_to_string(err,test)))
    def addSkip(self,test,reason):super().addSkip(test,reason);self.records.append(dict(test=test.id(),status="NOT_RUN",reason=reason))


def main():
    global OWN_USD,TORCH
    parser=argparse.ArgumentParser();parser.add_argument("--own-usd",action="store_true");parser.add_argument("--torch",action="store_true")
    args=parser.parse_args();OWN_USD=args.own_usd;TORCH=args.torch
    trial_id="CPU_REFERENCE_CONTRACT_"+str(time.time_ns());start=time.time()
    snapshot=HERE/(trial_id+"_source_snapshot");snapshot.mkdir(exist_ok=False)
    files=[p for p in HERE.iterdir() if p.is_file() and (p.suffix==".py" or "schema" in p.name)]
    source=[]
    for p in files:
        data=p.read_bytes();target=snapshot/p.name
        with target.open("xb") as stream:stream.write(data)
        source.append(dict(path=str(target),original_path=str(p),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    report=dict(trial_id=trial_id,status="PASS" if result.wasSuccessful() else "FAIL",epoch=start,
                wall_s=time.time()-start,protocol=dict(own_usd_static=args.own_usd,torch_tensor_math=args.torch,
                no_actor_model_policy_or_training=True,no_GPU_network_Git_or_plant=True,no_old_raw_PT_or_NPZ_read=True,
                tests_are_synthetic_contracts_not_actual_success_demonstration=True),
                python=sys.executable,source=source,
                tests=result.records,run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                actual_Fudan_capture_validation="not_executed_by_this_contract_suite",
                git_archive_state="pending_root_stage_archive_not_claimed_recorded")
    out=HERE/(trial_id+".json")
    with out.open("x",encoding="utf8") as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(out),status=report["status"],run=result.testsRun,failures=len(result.failures),errors=len(result.errors))))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":
    try:sys.exit(main())
    except Exception:
        path=HERE/("CPU_REFERENCE_RUNNER_ERROR_"+str(time.time_ns())+".json")
        with path.open("x",encoding="utf8") as out:json.dump(dict(error=traceback.format_exc(),git_archive_state="pending_root_stage_archive"),out,indent=2)
        raise
