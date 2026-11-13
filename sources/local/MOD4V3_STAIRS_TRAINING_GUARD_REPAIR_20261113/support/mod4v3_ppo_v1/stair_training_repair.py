"""Continuous-stair height and ordinary termination repair on the pinned native body."""
import ast
import inspect
import textwrap
import types
import torch
from mod4v1_scut.math_ops import euler_xyz_from_quat, wrap_to_pi
from .scut_flat_env import tensor


def wheel_center_ground(hits, wheel_xy, fallback):
    """Use the vertical ray at the wheel projection, rather than averaging across a riser."""
    valid = torch.isfinite(hits).all(-1)
    distance = (hits[..., :2] - wheel_xy[:, None, :]).square().sum(-1)
    closest = distance.masked_fill(~valid, float('inf')).argmin(-1)
    z = hits[..., 2].gather(1, closest[:, None]).squeeze(1)
    return torch.where(valid.any(-1), z, fallback)


def _contact_termination(self, force):
    hit = force > 1.0  # Pinned native threshold, unchanged.
    guides = self._stair_guide_columns[None, :]
    allowed = self._stair_guide_allowed[:, None]
    self._stair_contact_raw = (hit & ~(guides & allowed)).any(-1)
    self._stair_suppressed_guide_raw = (hit & guides & allowed).any(-1)
    return self._stair_contact_raw.clone()


def _duration(self, terminate):
    # Preserve the original combined timer outside the continuous stair course.
    legacy = self._stair_original_duration(terminate)
    rpy = euler_xyz_from_quat(self.robot.data.root_quat_w)
    roll = wrap_to_pi(rpy[0]).abs() > float(self.cfg.termination_roll_deg) * torch.pi / 180.
    pitch = wrap_to_pi(rpy[1]).abs() > float(self.cfg.termination_pitch_deg) * torch.pi / 180.
    contact = self._stair_contact_raw & terminate
    orientation = (roll | pitch) & terminate
    other = terminate & ~contact & ~orientation
    results = []
    for cause, mask in [('contact', contact), ('orientation', orientation), ('other', other)]:
        results.append(self._stair_original_duration(
            mask & self._stair_course_mask,
            counter_attr='_stair_' + cause + '_counter',
            raw_attr='_stair_' + cause + '_raw_buf'))
    return torch.where(self._stair_course_mask, results[0] | results[1] | results[2], legacy)


def install_native_done_repair(reward):
    """Change only contact selection and ordinary dwell; retain native safety and state overrides."""
    original = reward._get_dones.__func__
    tree = ast.parse(textwrap.dedent(inspect.getsource(original)))
    contacts = dwell = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'terminate' for t in node.targets):
            if isinstance(node.value, ast.Call) and ast.unparse(node.value).startswith('torch.any(reset_contact_force > 1.0'):
                node.value = ast.parse('self._stair_contact_termination(reset_contact_force)', mode='eval').body
                contacts += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == '_apply_termination_duration':
            node.func.attr = '_stair_apply_duration'
            dwell += 1
    assert (contacts, dwell) == (1, 1), 'Pinned done body no longer matches the two repair sites'
    ast.fix_missing_locations(tree)
    namespace = dict(original.__globals__)
    exec(compile(tree, '<continuous-stair-native-done-repair>', 'exec'), namespace)
    reward._get_dones = types.MethodType(namespace[tree.body[0].name], reward)
    reward._stair_original_duration = reward._apply_termination_duration
    reward._stair_contact_termination = types.MethodType(_contact_termination, reward)
    reward._stair_apply_duration = types.MethodType(_duration, reward)
    reward._stair_guide_columns = torch.tensor(
        [i in reward._guide_link_idx for i in reward._reset_contact_link_idx],
        device=reward.device, dtype=torch.bool)
    zeros = torch.zeros(reward.num_envs, device=reward.device, dtype=torch.bool)
    reward._stair_guide_allowed = zeros.clone()
    reward._stair_course_mask = zeros.clone()
    reward._stair_contact_raw = zeros.clone()
    reward._stair_suppressed_guide_raw = zeros.clone()


class ContinuousStairRepairMixin:
    def _make_reward(self, meta):
        reward = super()._make_reward(meta)
        install_native_done_repair(reward)
        return reward

    def prepare_endpoint(self):
        super().prepare_endpoint()
        if not getattr(self, '_continuous_ready', False):
            return
        r = self.reward
        stairs = self.continuous_stair_mask
        wheels = self.view.data.body_pos_w[:, r._wheel_link_idx]
        grounds = []
        for side, name in enumerate(('ground_left', 'ground_right')):
            hits = tensor(self.scene[name].data.ray_hits_w)
            grounds.append(wheel_center_ground(hits, wheels[:, side, :2], r.ground_wheels[:, side]))
        wheel_ground = torch.stack(grounds, dim=1)
        self.stair_original_root_ground = r.ground_z_est.clone()
        self.stair_wheel_ground = wheel_ground
        support_ground = wheel_ground.amin(1)
        r.ground_z_est = torch.where(stairs, support_ground, r.ground_z_est)
        r.ground_wheels = torch.where(stairs[:, None], wheel_ground, r.ground_wheels)
        r._invalidate_step_caches()
        center = self._center()
        x = (wheels[:, :, 0] - center[:, None, 0]) * self.stair_side[:, None]
        edge = torch.where(self.stair_stage == 0, 2.9, 1.4)
        # Reuse the existing reward's 0.45 m approach window. Chassis contact is never exempted.
        near = (x - edge[:, None]).abs().amin(1) < .45
        r._stair_course_mask = stairs
        r._stair_guide_allowed = stairs & self.stair_up & (self.stair_stage < 2) & near

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        reward = getattr(self, 'reward', None)
        if reward is None:
            return
        for cause in ('contact', 'orientation', 'other'):
            for suffix in ('_counter', '_raw_buf'):
                value = getattr(reward, '_stair_' + cause + suffix, None)
                if value is not None:
                    value[ids] = 0
        for name in ('_stair_guide_allowed', '_stair_contact_raw', '_stair_suppressed_guide_raw'):
            value = getattr(reward, name, None)
            if value is not None:
                value[ids] = False

    def terrain_summary(self):
        result = super().terrain_summary()
        result['stair_training_repair'] = dict(
            height_reference='min vertical terrain ray at the two drive-wheel centers; continuous stairs only',
            guide_contact_exemption='ascending continuous stairs, stage<2, existing0.45m edge approach window',
            ordinary_dwell='contact/orientation/other separately; native40deg and10x20ms retained',
            contact_threshold_N=1., closure_reset_m=.002,
            retained_flat_rough_semantics='unchanged', optimizer_updates_in_validation=0)
        return result
