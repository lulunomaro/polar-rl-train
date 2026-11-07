"""MOD4v3 SCUT flat walking + variable-height reward profile.

The reward equations are the pinned SCUT flat recipe.  This file only adapts the
MOD4v3 names and height signal; it does not change the 35-D observation or the
6-D action contract.
"""
import ast
import inspect
import textwrap
from copy import deepcopy

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



def configuration_v1(meta=None,bank=None,n=None,seed=None,terrain_selection='flat'):
    """Flat-v1: the V30 flat base plus SCUT airborne/pre-contact/landing terms.

    This is the task-level Flat-v1 overlay. It keeps the V30 flat reward weights
    and the same action/observation contract, while enabling the pinned SCUT
    airborne state machine and the reviewed landing/pre-contact additions.
    """
    cfg = configuration()
    cfg.enable_state_machines = True
    cfg.ctrl_mode_obs_enabled = True
    cfg.ctrl_mode_obs_dim = 7
    cfg.ctrl_mode_obs_layout = (
        'normal', 'stair', 'slope', 'recover', 'jump',
        'height_target', 'state_time',
    )
    cfg.height_obs_clip_enabled = True
    cfg.height_obs_clip_range = [0.05, 0.45]
    cfg.termination_duration_steps = 10

    air = deepcopy(cfg.airborne_state_machine_cfg)
    air['enabled'] = True
    air.setdefault('enter', {})['wheel_radius'] = 0.0625
    air.setdefault('reward_scales', {}).update(
        undesired_contact=25.0,
        flat_orientation_y_v=0.0,
        termination=6.0,
        track_height_square=0.0,
        foot_bound_square=0.0,
    )
    air.setdefault('landing_trajectory', {}).update(
        enabled=False,
        start_wheel_contact_duration_s=0.02,
        target_height=0.24,
        end_vel_z=0.0,
        min_height_margin=0.02,
        min_down_vel=0.2,
        duration_s=0.3,
        max_abs_acc=30.0,
    )
    air.setdefault('reward_additions', {}).update({
        'airborne_wheel_contact_force_over': {
            'type': 'wheel_contact_force_over', 'force_threshold': 300.0,
            'mode': 'l1', 'reduce': 'sum',
        },
        'airborne_landing_wheel_body_x_positive': {
            'type': 'landing_wheel_body_x_positive', 'target_x': 0.03,
            'sigma': 0.03, 'command_x_min': 1.0,
            'start_wheel_contact_duration_s': 0.02,
            'contact_force_threshold': 1.0, 'contact_mode': 'any_wheel',
            'use_entry_command': True,
        },
        'airborne_air_wheel_zero_torque_exp': {
            'type': 'wheel_zero_torque_exp', 'sigma': 1.5,
            'before_wheel_contact_duration_s': 0.02,
            'contact_mode': 'any_wheel',
        },
        'airborne_precontact_wheel_directional_speed': {
            'type': 'wheel_directional_speed', 'start': 0.0, 'full': 10.0,
            'command_x_threshold': 1.0, 'root_x_threshold': 1.0,
            'reduce': 'min', 'before_wheel_contact_duration_s': 0.02,
            'contact_mode': 'any_wheel',
        },
        'airborne_precontact_wheel_directional_speed_shortfall': {
            'type': 'wheel_directional_speed_shortfall', 'start': 0.0,
            'full': 10.0, 'command_x_threshold': 1.0,
            'root_x_threshold': 1.0, 'reduce': 'min',
            'require_wheel_contact_timer_started': True,
            'before_wheel_contact_duration_s': 0.05,
            'contact_mode': 'any_wheel',
        },
        'airborne_landing_wheel_max_contact_force': {
            'type': 'landing_wheel_max_contact_force', 'force_start': 200.0,
            'force_full': 400.0, 'start_wheel_contact_duration_s': 0.02,
            'contact_force_threshold': 1.0, 'contact_mode': 'any_wheel',
        },
        'airborne_landing_traj_height': {
            'type': 'landing_traj_height_exp', 'sigma': 0.01,
        },
        'airborne_landing_traj_vel_z': {
            'type': 'landing_traj_vel_z_exp', 'sigma': 0.25,
        },
    })
    cfg.airborne_state_machine_cfg = air

    cfg.rewards.update(
        airborne_joint_pos_limits=-10.0,
        airborne_wheel_heading_x_centering=10.0,
        airborne_air_wheel_zero_torque_exp=20.0,
        airborne_precontact_wheel_directional_speed=10.0,
        airborne_precontact_wheel_directional_speed_shortfall=-10.0,
        action_rate=-0.002,
        action_smoothness_leg=-0.005,
        action_smoothness_wheel=-0.001,
        leg_joint_acc=-1.0e-7,
        leg_joint_vel=-1.0e-3,
        wheel_acc=-2.0e-9,
        wheel_vel=-2.0e-6,
    )
    cfg.predefined_reset_air = {
        'enabled': True,
        'modes': ({
            'name': 'air_1',
            'prob': 0.30,
            'iteration_start': 0,
            'iteration_end': -1,
            'pose_range': {
                'z': (0.12, 0.42), 'roll': (-0.10, 0.10),
                'pitch': (-0.20, 0.20), 'yaw': (-3.141592653589793, 3.141592653589793),
            },
            'velocity_range': {
                'x': (-2.5, 2.5), 'y': (-0.5, 0.5), 'z': (0.0, 0.0),
                'roll': (-0.05, 0.05), 'pitch': (-0.10, 0.10), 'yaw': (-0.5, 0.5),
            },
            'command_limits': {
                'duration_s': 3.0, 'lin_vel_x': (-2.5, 2.5),
                'lin_vel_y': (0.0, 0.0), 'ang_vel_z': (-1.5707963267948966, 1.5707963267948966),
                'height': (0.18, 0.43),
            },
            'leg_length_range': (0.15, 0.35),
            'leg_angle_range': (-0.7853981633974483, 0.7853981633974483),
        },),
    }
    return cfg



def make_reward_class(meta,cfg_factory=configuration):
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
                        cfg=cfg_factory(), quaternion_order='wxyz')
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
            # MOD4 active leg coordinates have no finite SCUT rear2/rear1
            # mechanical-stop pair. Do not fabricate one from the SCUT names;
            # the real closure/mechanical limits are checked by the plant guard.
            z = self.height_cmd.new_zeros(self.num_envs)
            return z, z.clone(), z.clone()

        def ctrl_mode_obs(self):
            if not bool(getattr(self.cfg, 'ctrl_mode_obs_enabled', False)):
                return self.height_cmd.new_zeros((self.num_envs, 0))
            phase = getattr(self, 'jump_takeoff_phase', self.height_cmd.new_zeros(self.num_envs, dtype=torch.long))
            jump_state = phase != 0
            stair_state = self.height_cmd.new_zeros(self.num_envs, dtype=torch.bool)
            slope_state = self.height_cmd.new_zeros(self.num_envs, dtype=torch.bool)
            recover_state = self.height_cmd.new_zeros(self.num_envs, dtype=torch.bool)
            normal_state = ~(jump_state | recover_state | stair_state | slope_state)
            one_hot = torch.zeros((self.num_envs, 5), dtype=torch.float, device=self.device)
            one_hot[:, 0] = normal_state.float()
            one_hot[:, 1] = stair_state.float()
            one_hot[:, 2] = slope_state.float()
            one_hot[:, 3] = recover_state.float()
            one_hot[:, 4] = jump_state.float()
            target = getattr(self, 'jump_takeoff_ref_target_height',
                             getattr(self, 'jump_takeoff_height_cmd', self.height_cmd))
            height_target = torch.where(jump_state, target, torch.zeros_like(self.height_cmd))
            duration = getattr(self, 'airborne_current_duration', torch.zeros_like(self.height_cmd))
            aux = getattr(self, 'jump_takeoff_ref_phase',
                          getattr(self, 'jump_takeoff_phase_time', torch.zeros_like(self.height_cmd)))
            phase_time = torch.where(phase != 0, aux, duration)
            phase_time = torch.where(jump_state, phase_time, torch.zeros_like(phase_time))
            return torch.cat((one_hot, height_target[:, None], phase_time[:, None]), dim=-1)

        def _get_ctrl_mode_obs_raw(self):
            return self.ctrl_mode_obs()

        def _get_wheel_motor_z_axis_align_error_sq(self):
            # V30 flat does not enable this standing-only reward term, but the
            # pinned base computes it unconditionally. Keep it finite and zero.
            return self.height_cmd.new_zeros(self.num_envs)

        def _postprocess_reward_terms(self, terms):
            values = super()._postprocess_reward_terms(terms)
            self.length, self.theta = self.virtual_legs()
            return values

    return ScutFlatRewards


def make_reward_class_v1(meta):
    return make_reward_class(meta,cfg_factory=configuration_v1)
