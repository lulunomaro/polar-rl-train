"""MOD4v3 SCUT flat walking + variable-height reward profile.

The reward equations are the pinned SCUT flat recipe.  This file only adapts the
MOD4v3 names and height signal; it does not change the 35-D observation or the
6-D action contract.
"""
import ast
import inspect
import textwrap

import torch

from mod4v1_scut.rewards import ScutRewards as Base
from mod4v1_scut.config import reward_config as original_config
from mod4v1_scut.math_ops import quat_apply_inverse

SCUT_LEG_ORDER = ('left_front1_joint', 'left_rear1_joint', 'right_front1_joint', 'right_rear1_joint')


def configuration():
    cfg = original_config('trained_stair')
    # Flat SCUT run: leg length is the commanded height.  The v3 standing task
    # uses the same L0 signal, but fixes it at 0.334 m.
    cfg.use_absolute_height = False
    cfg.use_leg_length_as_height = False
    cfg.vel_height_gate_enabled = False
    cfg.height_upright_gate_enabled = False
    cfg.enable_state_machines = False
    for name in ('airborne_state_machine_cfg', 'jump_takeoff_state_machine_cfg',
                 'stair_state_machine_cfg', 'wheel_forward_scan_cfg'):
        getattr(cfg, name)['enabled'] = False
    cfg.height_range = (0.20, 0.42)
    cfg.default_height_cmd = 0.25
    cfg.episode_length_s = 20.0
    cfg.reward_groups_enabled = False
    cfg.front_rear_joint_limit_rewards_enabled = False
    cfg.leg_action_mode = 'joint_pos'
    cfg.leg_action_dim = 4
    cfg.use_gimbal = False
    cfg.airborne_state_machine_cfg.setdefault('enter', {})['wheel_radius'] = 0.0625
    # Exact SCUT flat weights from the V30 flat recipe.  Keep every enabled key
    # explicit so a missing term is visible in STARTUP.json.
    cfg.rewards.update(
        termination=-200.0,
        leg_joint_acc=-5.0e-07,
        leg_joint_vel=-0.005,
        leg_joint_pair_pos_diff=0.0,
        joint_torque=-0.0001,
        wheel_acc=-1.0e-08,
        wheel_vel=-1.0e-05,
        wheel_power=-0.0001,
        wheel_air_spin=0.0,
        lin_vel_z=-0.5,
        ang_vel_xy=-0.05,
        action_smoothness_leg=-0.05,
        action_rate=-0.01,
        action_smoothness_wheel=-0.01,
        flat_orientation_y=0.0,
        flat_orientation_y_v=-2.0,
        flat_orientation_y_exp=1.0,
        flat_orientation_x=0.0,
        flat_orientation_x_v=-2.0,
        flat_orientation_x_exp=1.0,
        track_lin_vel_xy=1.0,
        track_lin_vel_xy_tight=0.0,
        track_lin_vel_xy_square=-0.1,
        track_ang_vel_z=1.0,
        track_ang_vel_z_square=-0.1,
        stand_still_lin_vel=-2.0,
        stand_still=0.0,
        track_height_exp=0.0,
        track_height_exp_soft=0.0,
        track_height_exp_tight=1.0,
        track_height_square=-1.0,
        track_height_exp_both_wheels_contact=0.0,
        no_fork=-1.0,
        no_fork_square=-1.0,
        no_fork_exp=0.0,
        no_fork_z_exp=0.0,
        undesired_contact=-2.0,
        # These standing-only extras are intentionally zero for the flat task.
        pen_theta_no0=0.0,
        stand32_heading=0.0,
        stand32_wheel_distance=0.0,
    )
    return cfg


def make_reward_class(meta):
    names = {**meta['spec']['source_to_v3']['joints'],
             **meta['spec']['source_to_v3']['bodies']}

    class Names(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in names:
                return ast.copy_location(ast.Constant(names[node.value]), node)
            return node

    node = ast.parse(textwrap.dedent(inspect.getsource(Base.__init__)))
    node = Names().visit(node)
    ast.fix_missing_locations(node)
    scope = dict(Base.__init__.__globals__)
    scope.update(
        LEGS=SCUT_LEG_ORDER,
        WHEELS=tuple(meta['runtime']['policy_action_order'][4:]),
        WHEEL_BODIES=tuple(meta['spec']['frames']['wheel_order']),
        GUIDE_BODIES=tuple(meta['spec']['contact_groups']['guides']),
        STRUCTURAL_BODIES=tuple(meta['spec']['contact_groups']['structural']),
    )
    exec(compile(node, __file__, 'exec'), scope)
    constructor = scope['__init__']

    class ScutFlatRewards(Base):
        def __init__(self, robot, n, device):
            constructor(self, robot, meta, n, device, profile='trained_stair',
                        cfg=configuration(), quaternion_order='wxyz')
            self._left_right_leg_joint_pair_idx = (
                [robot.joint_names.index(s) for s in ('left_front1_joint', 'left_rear1_joint')],
                [robot.joint_names.index(s) for s in ('right_front1_joint', 'right_rear1_joint')],
            )
            self._hip_anchors = torch.tensor(
                [meta['joints'][s + '_rear1_joint']['local_pos0'] for s in ('left', 'right')],
                device=device,
            )
            self.length = torch.zeros(n, 2, device=device)
            self.theta = torch.zeros_like(self.length)

        def virtual_legs(self):
            d = self.robot.data
            rel = d.body_pos_w[:, self._wheel_link_idx] - d.root_pos_w[:, None]
            v = quat_apply_inverse(
                d.root_quat_w[:, None].expand(-1, 2, -1), rel
            ) - self._hip_anchors[None]
            return v.norm(dim=-1), torch.atan2(v[..., 0], -v[..., 2])

        def motor_stop_terms(self, airborne=False):
            # The flat SCUT recipe does not enable motor-stop shaping.
            z = self.height_cmd.new_zeros(self.num_envs)
            return z, z.clone(), z.clone()

        def _get_wheel_motor_z_axis_align_error_sq(self):
            # V30 flat does not enable this standing-only reward term, but the
            # pinned base computes it unconditionally. Keep it finite and zero.
            return self.height_cmd.new_zeros(self.num_envs)

        def _postprocess_reward_terms(self, terms):
            values = super()._postprocess_reward_terms(terms)
            self.length, self.theta = self.virtual_legs()
            return values

    return ScutFlatRewards
