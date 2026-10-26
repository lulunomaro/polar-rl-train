"""Standalone H1 target-conditioned SuperMimic experiment on the original Isaac plant.



Actual physical success remains the existing callback state machine. The analytic

root reference is an experimental objective, not a successful motion demonstration.

"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'sm_deps'))
import hashlib
import json
import shutil
import time
import traceback
import torch
from native_finalization_v1 import NativeCheckpointPublisher, run_native_lifecycle, source_sha as finalization_source_sha, verify_native, atomic_json
from native_continuation_v1 import (read_pinned_metadata_bundle, admit_closed_source, construct_preserving_post_reset_global_rng, restore_legacy85_new_episode, continuation_manifest_writer, BOOTSTRAP_SHA)
from supermimic_vendor_v2.geometry import invariant_features, unflatten_state
from supermimic_vendor_v2.learner import SuperMimicConfig, SuperMimicLearner
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY

class OwnCompleteSavedStop(Exception):
    pass

def put(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(value, indent=2), 'utf8')
    tmp.replace(path)

class H1GoalMdp:
    num_joints = 30
    action_dim = 6
    context_dim = 49
    obs_dim = 128
    goal_frame_dim = 73
    max_step_reward = 1.0

    def __init__(self, nominal_joints, nominal_height):
        self.nominal_joints = nominal_joints.detach().clone()
        self.nominal_height = float(nominal_height)

    def to(self, device):
        return H1GoalMdp(self.nominal_joints.to(device), self.nominal_height)

    def normalize_context(self, context):
        return torch.tanh(context)

    def add_noise(self, obs):
        return obs

    def obs(self, state, previous_action, context, frames):
        return torch.cat((invariant_features(state), previous_action, self.normalize_context(context)), -1)

    def goal(self, frames, num_frames):
        goals = []
        for offset in range(num_frames):
            f = frames.float() + offset
            t = ((f - 100) / 45).clamp(0, 1)
            smooth = t * t * (3 - 2 * t)
            x = 0.65 * smooth
            z = self.nominal_height + 0.27 * smooth + 0.3 * torch.sin(torch.pi * t)
            result = torch.zeros((*frames.shape, 73), device=frames.device, dtype=torch.float32)
            result[..., 0] = x
            result[..., 2] = z
            result[..., 3] = 1.0
            result[..., 13:43] = self.nominal_joints
            goals.append(result)
        return torch.cat(goals, -1)

    def reward(self, state, frames, action, previous_action):
        position, rotation, vel, ang, joint, jointvel = state
        target = self.goal(frames, 1)
        tracking = torch.exp(-5 * (position[..., 0] - target[..., 0]).square() - 5 * position[..., 1].square() - 15 * (position[..., 2] - target[..., 2]).square())
        upright = ((rotation[..., 2, 2] + 1) * 0.5).clamp(0, 1)
        return tracking * upright - 0.001 * (action - previous_action).square().mean(-1) - 0.001 * vel.square().mean(-1) - 0.0001 * jointvel.square().mean(-1)

    def soft_termination(self, state, frames):
        return (torch.sigmoid((0.12 - state[0][..., 2]) * 20) + torch.sigmoid((0.3 - state[1][..., 2, 2]) * 10)).clamp(0, 1)

    def critic_features(self, state, frames, normalized_context):
        return torch.cat((invariant_features(state), normalized_context, (frames.float() / 200)[..., None]), -1)

    def valid_imagination_start(self, frames, horizon):
        return torch.ones_like(frames, dtype=torch.bool)

@dataclass
class BridgeState:
    info: dict
    reward: torch.Tensor
    terminated: torch.Tensor
    truncated: torch.Tensor
    obs: dict

class H1Bridge:

    def __init__(self, runner, out, go):
        self.runner = runner
        self.vec = runner.env
        self.real = self.vec.unwrapped
        self.num_envs = self.real.num_envs
        self.device = torch.device(self.real.device)
        self.out = Path(out)
        self.go = go
        self.state = None
        self.trace = None
        self.learner = None
        self.ep_step = torch.zeros(self.num_envs, device=self.device, dtype=torch.int32)
        self.pi_updates = 0
        self.wm_updates = 0
        self.last_wm = None
        self.last_pi = None
        self.last_curve = -1
        robot = self.real.scene['robot']
        height = float((robot.data.root_pos_w[:, 2] - self.real.scene.env_origins[:, 2]).median())
        self.mdp = H1GoalMdp(robot.data.default_joint_pos[0], height)

    @property
    def supermimic_mdp(self):
        return self.mdp

    @torch.inference_mode()
    def pack(self, root, joint, velocity):
        root = root.detach().clone()
        root[:, :3] -= self.real.scene.env_origins
        root[:, 3:7] = root[:, [6, 3, 4, 5]]
        return torch.cat((root, joint.detach(), velocity.detach()), -1)

    @torch.inference_mode()
    def current(self):
        r = self.real.scene['robot']
        s = self.pack(r.data.root_state_w, r.data.joint_pos, r.data.joint_vel)
        ctx = torch.cat((self.real._integrated_contact.history.flatten(1), r.data.applied_torque, self.real.h1_phase.public_request().float()[:, None]), -1).detach().clone()
        return (s, ctx)

    def init_state(self):
        s, ctx = self.current()
        zero = torch.zeros(self.num_envs, device=self.device)
        self.state = BridgeState(info={SUPERMIMIC_STATE_KEY: dict(s=s, xi=ctx, f=self.real.h1_phase.age_control.clone(), a_prev=torch.zeros(self.num_envs, 6, device=self.device), ep_step=self.ep_step.clone())}, reward=zero, terminated=zero.bool(), truncated=zero.bool(), obs={})
        return self.state

    @torch.inference_mode()
    def before_action(self):
        if time.time() >= self.go['save_deadline'] or (self.out / 'STOP_AFTER_SAVE.json').exists() or shutil.disk_usage(self.out).free < 8 * 1024 ** 3:
            raise OwnCompleteSavedStop()
        assert self.trace is not None
        self.runner.alg.act(self.vec.get_observations())
        if self.learner.iteration != self.last_curve:
            events = self.trace.lifetime_goal_counter.snapshot()
            row = dict(epoch=time.time(), GO_elapsed_s=time.time() - self.go['learning_started_epoch'], native_iteration=self.learner.iteration, world_updates=self.wm_updates, policy_updates=self.pi_updates, environment_transitions=self.trace.total * self.num_envs, completed_control_rows=self.trace.total, events=events, wm_last=self.last_wm, policy_last=self.last_pi, not_frozen_evaluation_or_causal_PPO_comparison=True)
            with (self.out / 'ACTUAL_H1_CONVERGENCE_CURVE.jsonl').open('a', encoding='utf8') as f:
                f.write(json.dumps(row) + '\n')
            self.last_curve = self.learner.iteration
            if self.pi_updates > self.window_start_pi_updates:
                checkpoint = self.trace.source_models[-1]
                positive = dict(checkpoint, updates=self.learner.iteration, world_updates=self.wm_updates, policy_updates=self.pi_updates, original_task_events=events, not_PPO_or_production_source=True)
                put(self.out / 'latest_complete.json', positive)
                if not (self.out / 'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').exists():
                    put(self.out / 'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json', positive)

    @torch.inference_mode()
    def step(self, actions):
        info = self.state.info[SUPERMIMIC_STATE_KEY]
        obs, reward, done, extras = self.vec.step(actions)
        frame = self.trace.frame
        next_before_reset = self.pack(frame['root13'], frame['q30'], frame['joint_velocity'])
        executed = frame['executed6'].detach().clone()
        transition = dict(s=info['s'], s1=next_before_reset, a=executed, a_prev=info['a_prev'], xi=info['xi'], r=reward.detach(), f=info['f'], ep_step=info['ep_step'], done=done.bool())
        s, ctx = self.current()
        self.ep_step = torch.where(done.bool(), 0, self.ep_step + 1).to(torch.int32)
        previous = executed.clone()
        previous[done.bool()] = 0
        stateinfo = dict(s=s, xi=ctx, f=self.real.h1_phase.age_control.clone(), a_prev=previous, ep_step=self.ep_step.clone())
        self.state = BridgeState(info={SUPERMIMIC_STATE_KEY: stateinfo, SUPERMIMIC_TRANSITION_KEY: transition}, reward=reward, terminated=done.bool(), truncated=torch.zeros_like(done, dtype=torch.bool), obs={})
        return self.state

def run(runner, n, log_dir, B, J, out, task, go, src, phase):
    B, J, out = (Path(B), Path(J), Path(out))
    runner.logger.writer = None
    env = runner.env.unwrapped
    assert env.num_envs == 20000 and env.physics_dt == 0.0025 and (env.step_dt == 0.01) and (env.cfg.decimation == 4)
    from spring_pressure_checkpoint import exact
    source = torch.load(src, map_location='cpu', weights_only=False)
    for key, value in [('actor_state_dict', runner.alg.actor.state_dict()), ('critic_state_dict', runner.alg.critic.state_dict()), ('optimizer_state_dict', runner.alg.optimizer.state_dict())]:
        assert exact(value, source[key]), key
    assert {int(v['step']) for v in source['optimizer_state_dict']['state'].values()} == {task['source_Adamstep']}
    assert not env.h1_phase.age_control.any()
    from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
    sdk = isolated_actual_SDK_dt_probe(env)
    bridge = H1Bridge(runner, out, go)
    # New reference is a measured foreign jump retargeted to our static geometry;
    # its phase masks/task support objective are distinct from physical rewards.
    from supermimic_reference_adapter_v1 import read_json_reference, PartialReferenceImitationMdp
    reference_bundle = json.loads((B / 'MIXED84_REFERENCE_BINDING_ACTUAL.json').read_bytes())
    reference_path = B / reference_bundle['reference']['artifact_relative']
    assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == reference_bundle['reference']['reference_artifact_SHA']
    reference = read_json_reference(reference_path)
    actual_joint_names = list(env.scene['robot'].joint_names)
    reference = reference.for_sdk_joint_order(actual_joint_names)
    assert reference.metadata['sdk_joint_order_verified'] is True
    bridge.mdp = PartialReferenceImitationMdp(bridge.mdp, reference.torch_provider(env.device))
    runtime_objective = bridge.mdp.contract_manifest()
    assert runtime_objective['provider_execution_scope'] == 'runtime_actual_SDK_named_mapping_required'
    assert runtime_objective['reference_metadata']['sdk_joint_order_verified'] is True
    assert runtime_objective['config'] == reference_bundle['objective_contract']['config']
    runtime_bytes = (json.dumps(runtime_objective, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf8')
    runtime_contract_SHA = hashlib.sha256(runtime_bytes).hexdigest()
    runtime_path = out / 'NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json'
    assert not runtime_path.exists()
    runtime_partial = runtime_path.with_suffix('.json.partial')
    with runtime_partial.open('xb') as stream:
        stream.write(runtime_bytes)
    runtime_partial.replace(runtime_path)
    assert bridge.pi_updates == 0 and bridge.wm_updates == 0 and bridge.trace is None
    runtime_order = dict(
        actual_runtime_order_readback=True, complete_named_permutation=True,
        before_first_physical_step_and_Pi=True,
        scope='before first native learning control/Pi; original environment construction/reset is separate',
        actual_robot_joint_names=actual_joint_names,
        reference_artifact_SHA=reference_bundle['reference']['reference_artifact_SHA'],
        runtime_objective_contract_SHA=runtime_contract_SHA,
        source_SHA=task['source_SHA'], original_run_id=go['run_id'],
        actual_own_task_physics_commands_and_success_unchanged=True)
    put(out / 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json', runtime_order)
    cfg = SuperMimicConfig(iterations=1000000, buffer_steps=64, utd=1 / 24, horizon=16, goal_frames=1, hist=10, z_dim=32, wm_hidden=(512, 512, 512), policy_hidden=(512, 256, 128), critic_hidden=(256, 128), wm_window=8, wm_batches=10, wm_batch=512, pi_batch=512, warmup_steps=48, wm_only_iters=10, critic_epochs=2, critic_minibatches=2, ckpt_every=1000000, log_every=1, amp='none', compile=False, log_backend='none', seed=20261026)
    # Mandatory closed native source admission; missing85M2 closure stays blocked.
    binding, metadata = read_pinned_metadata_bundle(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
    admission = admit_closed_source(binding, current_runtime_order=runtime_order,
        current_runtime_objective=runtime_objective, **metadata)
    assert task['source_SHA'] == go['source_SHA'] == admission['checkpoint_SHA'], 'Native source file/task/GO binding differs'
    new_episode_proof = json.loads((Path(log_dir) / 'STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json').read_bytes())
    def restore_post_reset_rng(state):
        torch.random.set_rng_state(state[0])
        torch.cuda.set_rng_state_all(state[1])
    learner = construct_preserving_post_reset_global_rng(
        lambda: SuperMimicLearner(bridge, cfg, out / 'native_supermimic', device=env.device, backend='original_Isaac_MOD4_H1_step270'),
        lambda: (torch.random.get_rng_state(), torch.cuda.get_rng_state_all()),
        restore_post_reset_rng)
    bridge.learner = learner
    restore_receipt = restore_legacy85_new_episode(source, learner, bridge, admission,
        new_episode_proof, verify_native)
    put(out / 'NATIVE_CONTINUATION_STARTUP_ACTUAL.json', restore_receipt)
    oldsave = runner.save

    publisher = NativeCheckpointPublisher(oldsave, learner, bridge, out, producer=dict(
        bridge_source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        finalization_source_SHA=finalization_source_sha(),
        bootstrap_task_source_SHA=BOOTSTRAP_SHA,
        native_continuation_source_checkpoint_SHA=admission['checkpoint_SHA'],
        native_continuation_source_run_id=admission['source_run_id'],
        continuation_source_SHA=hashlib.sha256((B / 'native_continuation_v1.py').read_bytes()).hexdigest(),
        reference_artifact_SHA=reference_bundle['reference']['reference_artifact_SHA'],
        adapter_CPU_report_SHA=reference_bundle['adapter_CPU']['report_SHA'],
        objective_contract_SHA=reference_bundle['adapter_CPU']['objective_contract_SHA'],
        runtime_objective_contract_SHA=runtime_contract_SHA,
        native_not_production_H1_or_E2_source=True))

    def save(path, *args, **kwargs):
        return publisher(path, *args, **kwargs)
    runner.save = save
    runner.alg.act = lambda *args, **kwargs: None
    from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace
    trace = H1ControlPrefixTrace(runner, out / 'control_prefix_raw')
    bridge.trace = trace
    trace.install()
    original_wm = learner.wm_update
    original_pi = learner.policy_update

    def wm_update():
        result = original_wm()
        assert all((torch.isfinite(x).all() for x in result))
        assert all((torch.isfinite(p).all() for p in learner.wm.parameters()))
        bridge.wm_updates += 1
        bridge.last_wm = [float(x) for x in result]
        return result

    def pi_update():
        result = original_pi()
        assert all((torch.isfinite(x).all() for x in result))
        assert all((torch.isfinite(p).all() for p in learner.pi.parameters()))
        bridge.pi_updates += 1
        bridge.last_pi = [float(x) for x in result]
        return result
    learner.wm_update = wm_update
    learner.policy_update = pi_update
    put(out / 'ACTUAL_H1_NEW_METHOD_STARTUP_CONTRACT.json', dict(epoch=time.time(), source_SHA=task['source_SHA'], source_Adam=task['source_Adamstep'], source_actor_critic_STD17Adam_literal_exact=True, actual_SDK_dt_probe=sdk, actual_envs=env.num_envs, physics_dt=env.physics_dt, control_dt=env.step_dt, actual_geometry=env.h1_phase.state_dict()['geometry'], new_actor128_history10_goal73_not_PPO35_matched_comparison=True, reference_is_partial_retarget_not_our_successful_step_or_forced_action=True, actual_original_goal_machine_unchanged=True, actual_original_trace_sampler_retention_unchanged=True, source_G1_motion_library_not_used=True))
    return run_native_lifecycle(
        train=learner.train, stop_types=(OwnCompleteSavedStop,),
        persist_trace=trace.persist, save=save, out=out,
        iteration=lambda: learner.iteration,
        world_updates=lambda: bridge.wm_updates,
        policy_updates=lambda: bridge.pi_updates,
        events=trace.lifetime_goal_counter.snapshot,
        write_manifest=continuation_manifest_writer(atomic_json, bridge, restore_receipt))
