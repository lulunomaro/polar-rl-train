"""Actual reference + AST-extracted REAL H1 MDP CPU algebra/shape/loss proof.

No model/checkpoint, learner import, actor forward, optimizer, RNG, GPU or plant.
Offline named order remains explicitly SDK-readback false throughout.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
import numpy as np
import torch
import torch.nn.functional as F

from supermimic_reference_adapter_v1 import NativeReference,PartialReferenceImitationMdp

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
D=HERE/"ACTUAL_PARTIAL_STEP270_PHASE_V3_1793006590678125700"
REFERENCE=D/"H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json"
H=T/"MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026/candidate_source_v5"


def canonical_json(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf8")


def put(path,value):
    with Path(path).open("x",encoding="utf8") as stream:json.dump(value,stream,ensure_ascii=False,indent=2)


def main():
    trial="ACTUAL_PARTIAL_H1_OBJECTIVE_CPU_PROOF_V3_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False)
    try:
        source=[];snapshot=out/"source_snapshot";snapshot.mkdir()
        for path in (Path(__file__),HERE/"supermimic_reference_adapter_v1.py",H/"h1_supermimic_bridge_v1.py",H/"supermimic_vendor_v2/geometry.py"):
            data=path.read_bytes();target=snapshot/path.name;target.write_bytes(data)
            source.append(dict(path=str(path),snapshot_path=str(target),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
        # Import only four pure tensor geometry functions from source AST; no
        # package __init__, learner, policy class or training globals execute.
        geo=ast.parse((H/"supermimic_vendor_v2/geometry.py").read_text(encoding="utf8"))
        names={"quat_to_mat","yaw_mat","mat_to_6d","invariant_features"}
        funcs=[n for n in geo.body if isinstance(n,ast.FunctionDef) and n.name in names]
        assert {n.name for n in funcs}==names
        future=ast.ImportFrom(module="__future__",names=[ast.alias(name="annotations")],level=0)
        module=ast.fix_missing_locations(ast.Module(body=[future]+funcs,type_ignores=[]));namespace=dict(torch=torch,F=F)
        exec(compile(module,"REAL_NATIVE_GEOMETRY_SOURCE_AST_PURE_FUNCTIONS","exec"),namespace)
        bridge=ast.parse((H/"h1_supermimic_bridge_v1.py").read_text(encoding="utf8"))
        cls=next(n for n in bridge.body if isinstance(n,ast.ClassDef) and n.name=="H1GoalMdp")
        module=ast.fix_missing_locations(ast.Module(body=[cls],type_ignores=[]))
        exec(compile(module,"REAL_NATIVE_H1_GOAL_MDP_SOURCE_AST_ONLY","exec"),namespace)
        ref=NativeReference.from_dict(json.loads(REFERENCE.read_text(encoding="utf8")))
        offline=ref.for_offline_joint_order(ref.joint_names)
        assert offline.metadata["sdk_joint_order_verified"] is False
        provider=offline.torch_provider("cpu",offline_cpu_only=True)
        base=namespace["H1GoalMdp"](torch.tensor(ref.states[0,13:43],dtype=torch.float32),ref.metadata["own_geometry"]["nominal_spawn_height_m"])
        mdp=PartialReferenceImitationMdp(base,provider)
        frames=torch.arange(50,311,dtype=torch.int32);assert len(frames)==len(ref.times_s)
        target=provider.raw_reference_at_frames(frames);own_task=base.goal(frames,1)
        position=target[:,:3].clone();position[:,0]=own_task[:,0];position[:,1]=0.
        cutoff=ref.metadata["partial_phase_contract"]["demo_height_vz_active_through_reference_time_s"]
        query=frames.float()*.01+ref.metadata["native_frame_zero_reference_time_s"]
        post=query>cutoff
        landing_z=float(ref.metadata["partial_phase_contract"]["own_task_nominal_chassis_height_m"])+.27
        position[post,2]=landing_z
        velocity=target[:,7:10].clone();velocity[:,:2]=0;velocity[post,2]=0
        state=(position,namespace["quat_to_mat"](target[:,3:7]),velocity,target[:,10:13],target[:,13:43],target[:,43:73])
        action=torch.zeros((len(frames),6));context=torch.zeros((len(frames),49))
        obs=mdp.obs(state,action,context,frames);goal=mdp.goal(frames,1);critic=mdp.critic_features(state,frames,context)
        assert tuple(obs.shape)==(261,128) and tuple(goal.shape)==(261,73) and tuple(critic.shape)==(261,123)
        assert bool(torch.isfinite(obs).all() and torch.isfinite(goal).all())
        np.testing.assert_allclose(goal.numpy(),offline.goal_frames_numpy(frames.numpy(),1,.01),atol=3e-5)
        terms=mdp.objective_terms(state,frames,action,action)
        assert all(bool(torch.isfinite(value).all()) for value in terms.values())
        assert bool((goal[post,2]==0).all() and (goal[post,9]==0).all())
        assert bool((terms["demo_height_cost"][post]==0).all() and (terms["demo_vertical_velocity_cost"][post]==0).all())
        assert float(terms["own_task_landing_height_cost"][post].max())<1e-9
        altered=ref.states.copy();altered[ref.times_s>cutoff,2]-=10;altered[ref.times_s>cutoff,9]+=100
        altered[:,0]+=200;altered[:,7]+=200
        changed=NativeReference(ref.times_s,altered,ref.joint_names,ref.metadata).for_offline_joint_order(ref.joint_names)
        changed_mdp=PartialReferenceImitationMdp(base,changed.torch_provider("cpu",offline_cpu_only=True))
        # Evaluate safely after the masking boundary (reference time >=1s), so
        # no interpolation spans its deliberately modified adjacent source row.
        later=query>=1.
        later_state=tuple(v[later] for v in state)
        torch.testing.assert_close(mdp.reward(later_state,frames[later],action[later],action[later]),
                                   changed_mdp.reward(later_state,frames[later],action[later],action[later]))
        ground=list(later_state);ground[0]=ground[0].clone();ground[0][:,2]-=.27
        correct=mdp.reward(later_state,frames[later],action[later],action[later])
        ground_reward=mdp.reward(tuple(ground),frames[later],action[later],action[later])
        assert bool((correct>ground_reward).all())
        np.testing.assert_allclose(provider.raw_reference_at_frames(torch.tensor([100]))[0].numpy(),ref.at_time(.5),atol=3e-6)
        np.testing.assert_allclose(provider.raw_reference_at_frames(torch.tensor([0]))[0].numpy(),ref.states[0],atol=3e-6)
        manifest=mdp.contract_manifest();assert manifest["reference_metadata"]["sdk_joint_order_verified"] is False
        manifest_path=out/"PARTIAL_REFERENCE_OBJECTIVE_OFFLINE_CPU_CONTRACT_V3.json"
        with manifest_path.open("xb") as stream:stream.write(canonical_json(manifest))
        config_sha=hashlib.sha256(canonical_json(manifest["config"])).hexdigest()
        report=dict(trial_id=trial,status="PASS_ACTUAL_REFERENCE_REAL_H1_MDP_OFFLINE_CPU_OBJECTIVE_PROOF",
            native_reference=dict(path=str(REFERENCE),bytes=REFERENCE.stat().st_size,SHA256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),schema="mod4.supermimic.native_reference.v1"),
            source=source,actual_original_source_NPZ_SHA256=ref.metadata["source"]["artifact_sha256"],
            frames_proved=261,obs_dim=128,goal_dim=73,critic_base_feature_dim=123,history10_unchanged=True,
            source_ascent_apex_reference_s=cutoff,post_ascent_masked_frames=int(post.sum()),
            correct_own_platform_landing_height_m=landing_z,
            source_flat_return_Z_Vz_and_horizontal_mutations_do_not_change_postascent_loss=True,
            correct_platform_landing_scores_above_own_ground_landing_in_task_region=True,
            source_onset1_5s_maps_own_age100_and_initial_hold=True,
            offline_named_order_proved=True,actual_runtime_SDK_readback=False,
            offline_objective_contract=dict(path=str(manifest_path),bytes=manifest_path.stat().st_size,
                SHA256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),schema=manifest["schema"],
                serialization="UTF8_sorted_keys_compact_separators_plus_single_newline"),
            objective_config_SHA256=config_sha,
            actual_native_actor_forward_optimizer_GPU_plant_or_WM_training_executed=False,
            pending=["runtime_actual_robot_joint_names_hard_check_before_first_step_Pi",
                     "runtime_loss_and_fullsave_protocol_admission","own_motor_torque_speed_and_collision_dynamics",
                     "own_H1_dualwheel270mm_cross_topcontact_200callbacks_0.5s_stable_recovery","frozen_skill_evaluation"],
            physical_V8_reward_commands_success_and_WM_actual_transition_sources="unchanged",
            git_archive_state="pending_root_stage_archive")
        path=out/"ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json";put(path,report)
        print(json.dumps(dict(out=str(out),report=str(path),report_SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              status=report["status"],contract=report["offline_objective_contract"],objective_config_SHA256=config_sha)))
    except BaseException:
        put(out/"ACTUAL_REFERENCE_H1_MDP_CPU_ORIGINAL_ERROR.json",dict(error=traceback.format_exc(),
            git_archive_state="pending_root_stage_archive",all_partial_outputs_preserved=True));raise


if __name__=="__main__":main()
