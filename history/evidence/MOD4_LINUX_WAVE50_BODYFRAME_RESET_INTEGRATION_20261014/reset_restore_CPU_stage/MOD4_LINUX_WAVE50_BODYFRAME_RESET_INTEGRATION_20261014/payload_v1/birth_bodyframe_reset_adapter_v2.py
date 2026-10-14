"""Independent post-birth reset/command adapter. CPU fixtures are never GPU admission.

First transition attaches only after the original complete predecessor restore
and its one new physical episode. Later calls invoke the original reset once.
This file does not install a simulator, launch a worker, or grant a GPU lease.
"""
import copy
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from birth_bodyframe_state_v1 import (N, PROFILE, SOURCE, clone, validate,
    next_birth, mapped_command, audit_command, histogram_increment)


def tensor(v):
    return v.torch if hasattr(v, 'torch') else v


def pi_xyzw(q):
    assert q.ndim == 2 and q.shape[1] == 4 and torch.isfinite(q).all()
    assert torch.allclose(q.square().sum(-1), torch.ones(len(q), device=q.device), atol=1e-6, rtol=0)
    return torch.stack((-q[:, 1], q[:, 0], q[:, 3], -q[:, 2]), -1)


def assert_backend(env, proof, fixture):
    assert env.num_envs == N and env.physics_dt == .0025 and env.step_dt == .01
    if fixture:
        assert str(env.device) == 'cpu' and proof == {'CPU_fixture_only': True}
        return
    assert str(env.device).startswith('cuda') and torch.cuda.is_initialized()
    assert proof['actual_own_native_quaternion_ABI_verified'] is True
    assert proof['quaternion_convention'] == 'xyzw'
    assert proof['own_source_SHA'] == SOURCE and proof['scope_profile'] == PROFILE
    assert proof['extra_physics_steps_for_ABI_check'] == 0
    assert proof['data_vs_native_root_getter_exact'] is True
    assert proof['native_setter_readback_required'] is True
    assert proof['independent_xyzw_heading_witness_verified'] is True
    assert proof['sourcefreeze_verified'] is True
    assert isinstance(proof['sourcefreeze_SHA'], str) and len(proof['sourcefreeze_SHA']) == 64
    assert tensor(env.scene['robot'].data.root_state_w).is_cuda


def place_selected_flipped_births(env, ids, state, ray, backend_proof, fixture=False):
    assert_backend(env, backend_proof, fixture)
    validate(state)
    assert torch.equal(env._e1_episode[ids], state['bound_episode'][ids])
    flipped = ids[state['flip_pi'][ids]]
    robot = env.scene['robot']; bank = env._rough_probe_bank
    assert bank['points'].shape == (25200, 3)
    assert torch.isfinite(bank['points']).all()
    # Only rows requiring the declared pi change are sent to the native setter.
    before = tensor(robot.data.root_state_w)[flipped].clone()
    q30 = tensor(robot.data.joint_pos)[flipped].clone()
    qd30 = tensor(robot.data.joint_vel)[flipped].clone()
    assert q30.shape == (len(flipped), 30)
    assert torch.equal(q30, env._rough_probe_expected_q[flipped])
    assert torch.equal(before[:, 7:], torch.zeros_like(before[:, 7:]))
    assert torch.equal(qd30, torch.zeros_like(qd30))
    after = before.clone()
    if len(flipped):
        after[:, 3:7] = pi_xyzw(before[:, 3:7])
        frames = Rotation.from_quat(after[:, 3:7].cpu().numpy()).as_matrix()
        rotation = torch.as_tensor(frames, device=env.device, dtype=torch.float32)
        ceiling = float(ray.geometry.vertices[:, 2].max()) + 2.
        minimum = float('inf')
        for first in range(0, len(flipped), 64):
            last = min(first + 64, len(flipped))
            offsets = torch.einsum('nij,pj->npi', rotation[first:last], bank['points'])
            starts = offsets.clone()
            starts[:, :, :2] += before[first:last, None, :2]
            starts[:, :, 2] = ceiling
            surface = ray.cast(starts.contiguous(), 10.)
            assert surface['hit'].all() and torch.isfinite(surface['height']).all()
            assert torch.isfinite(surface['normal']).all() and (surface['normal'][..., 2] > 0).all()
            placed = (surface['height'] + .002 - offsets[:, :, 2]).amax(1)
            clear = placed[:, None] + offsets[:, :, 2] - surface['height']
            assert torch.isfinite(clear).all() and float(clear.min()) >= .002 - 1e-5
            after[first:last, 2] = placed
            minimum = min(minimum, float(clear.min()))
        assert torch.equal(after[:, :2], before[:, :2]) and torch.equal(after[:, 7:], before[:, 7:])
        robot.write_root_state_to_sim(after, env_ids=flipped)
        assert torch.equal(tensor(robot.data.root_state_w)[flipped], after), 'Actual setter readback differs'
    else:
        minimum = None
    assert torch.equal(tensor(robot.data.joint_pos)[flipped], q30)
    assert torch.equal(tensor(robot.data.joint_vel)[flipped], qd30)
    env._rough_query_tick = None
    return dict(profile=PROFILE, CPU_fixture_only=fixture,
                actual_GPU_native_passed=not fixture,
                selected_ids=ids.cpu().tolist(), pi_ids=flipped.cpu().tolist(),
                original_root_xyzw=before.cpu(), changed_root_xyzw=after.cpu(),
                q30_unchanged=True, qd30_unchanged=True, XY_and_velocities_exact=True,
                full_collision_points=25200, original_clearance_m=.002,
                original_placement_tolerance_m=1e-5, minimum_clearance_m=minimum,
                extra_reset_step_forward_render_RNG_calls=0,
                no_cached_ground_fallback=True,
                sampled_footprint_not_continuous_nonpenetration_certificate=True)


class BirthAdapter:
    def __init__(self, env, state, ray, backend_proof, fixture=False):
        assert_backend(env, backend_proof, fixture)
        validate(state)
        self.env = env; self.state = clone(state); self.ray = ray
        self.backend_proof = copy.deepcopy(backend_proof); self.fixture = fixture
        self.term = env.command_manager.get_term('twist')
        self.reset_in_progress = False; self.installed = False
        self.original_reset = env._reset_idx
        self.original_write = self.term._write_dynamic
        self.original_audit = self.term.audit_direction
        self.original_step = env.step
        self.latest_birth = None

    def after_existing_birth(self, ids):
        """Caller has performed exactly one original full reset, never reset here."""
        candidate = next_birth(self.state, ids, self.env._e1_episode)
        receipt = place_selected_flipped_births(self.env, ids, candidate, self.ray,
                                               self.backend_proof, self.fixture)
        self.state = candidate
        self.latest_birth = receipt
        # Bind legacy WORLD entry bookkeeping after the parent's increment.
        self.original_write(ids)
        self.apply_commands(ids)
        return receipt

    def apply_commands(self, ids):
        if self.reset_in_progress:
            return
        assert torch.equal(self.state['bound_episode'], self.env._e1_episode)
        term = self.term
        assert not term.manual_evaluation_mode
        original = term.vel_command_b.clone()
        mapped = mapped_command(original, term.family, term.is_standing_env, self.state, ids)
        term.vel_command_b[ids] = mapped[ids]

    def install(self):
        assert not self.installed and torch.equal(self.state['bound_episode'], self.env._e1_episode)
        audit_command(self.term.vel_command_b, self.term.family, self.term.is_standing_env,
                      self.env._e1_episode, self.state)

        def reset(ids):
            ids = torch.as_tensor(ids, device=self.env.device, dtype=torch.int64)
            before = self.env._e1_episode.clone()
            assert not self.reset_in_progress
            self.reset_in_progress = True
            try:
                result = self.original_reset(ids)
            finally:
                self.reset_in_progress = False
            expected = before.clone(); expected[ids] += 1
            assert torch.equal(self.env._e1_episode, expected)
            self.after_existing_birth(ids)
            return result

        def write(ids):
            ids = torch.as_tensor(ids, device=self.env.device, dtype=torch.int64)
            self.original_write(ids)
            self.apply_commands(ids)

        def audit():
            # Do not invoke the invalid legacy BODY x WORLD-entry predicate.
            legacy = self.term.state_dict_direction()
            assert torch.equal(legacy['wave_mask'], self.state['wave_mask'])
            assert torch.equal(legacy['entry_sign'], self.state['world_toward_sign'])
            result = audit_command(self.term.vel_command_b, self.term.family, self.term.is_standing_env,
                                   self.env._e1_episode, self.state)
            result.update(assignment_sha256=legacy['assignment_sha256'],
                          entry_map_sha256=legacy['entry_map_sha256'],
                          legacy_world_entry_bookkeeping_profile=legacy['profile'],
                          predecessor_audit_preserved_in_original_module=True)
            return result

        def step(action):
            assert not self.reset_in_progress
            self.term.audit_direction()
            # Count the command that produced the transition, before any reset.
            delta = histogram_increment(self.term.vel_command_b, self.term.family,
                                        self.term.is_standing_env, self.state)
            tick = int(self.env._sim_step_counter)
            result = self.original_step(action)
            assert int(self.env._sim_step_counter) == tick + 4
            self.state['completed_control_histogram'].add_(delta)
            self.state['completed_controls'] += 1
            return result

        self.env._reset_idx = reset
        self.term._write_dynamic = write
        self.term.audit_direction = audit
        self.env.step = step
        self.installed = True

    def state_dict(self):
        self.term.audit_direction()
        return {k: v.cpu().clone() if torch.is_tensor(v) else clone(v) for k, v in self.state.items()}

    def load_state_dict(self, state):
        """Only restore bookkeeping; never write a live pose or consume a birth."""
        validate(state, self.state['source_bindings'])
        assert torch.equal(state['bound_episode'].to(self.env.device), self.env._e1_episode)
        self.state = {k: v.to(self.env.device).clone() if torch.is_tensor(v) else clone(v) for k, v in state.items()}
