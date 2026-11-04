"""Pinned SCUT trained-stair recipe, with explicit MOD4 model/task substitutions."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

from .upstream import source_path

USD_SHA = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
LEGS = ('left_crank', 'left_hip', 'right_crank', 'right_hip')
WHEELS = ('left_wheel_spin', 'right_wheel_spin')
WHEEL_BODIES = ('left_wheel', 'right_wheel')
GUIDE_BODIES = tuple(f'guide_roller_{i:02d}' for i in range(8))
# The selected MOD4 E0 policy was trained and evaluated through the original
# RslRlVecEnvWrapper clip_actions=6.0. This is its execution interface, separate
# from SCUT's published agent.yaml (clip_actions=None). Keep PPO samples raw.
ACTION_CLIP = 6.0
ACTION_INTERFACE = 'mod4_e0_clip6_before_PD_reward_and_action_history'
TARGET_INTERFACE = 'mod4_contract_position_limits_then_existing_CAD_difference_before_D4_v1'
# The V14 subclass (env.py:117-130) adds guides back to base harmful contacts.
# MOD4's additional drive/gas bodies belong to the non-rolling leg structure.
STRUCTURAL_BODIES = ('chassis',) + tuple(
    side+'_'+part for side in ('left', 'right') for part in
    ('coupler', 'distal', 'drive_hip', 'drive_input', 'gas_barrel', 'gas_inner',
     'input', 'rocker', 'shin', 'thigh'))


def read_yaml(key):
    import yaml
    class Loader(yaml.SafeLoader):
        pass
    Loader.add_constructor('tag:yaml.org,2002:python/tuple',
                           lambda loader, node: tuple(loader.construct_sequence(node)))
    Loader.add_constructor('tag:yaml.org,2002:python/object/apply:builtins.slice',
                           lambda loader, node: slice(*loader.construct_sequence(node)))
    return yaml.load(source_path(key).read_text(encoding='utf-8-sig'), Loader=Loader)


def reward_config(profile='trained_stair'):
    if profile not in ('trained_stair', 'jump270', 'scut_stairs', 'jump200'):
        raise ValueError('Unknown SCUT profile')
    raw = read_yaml('trained_env')
    # Only reward/helper fields. No imported SCUT asset, actuator, randomizer or physics.
    values = {k: deepcopy(v) for k, v in raw.items()
              if isinstance(v, (bool, float, int, str)) or v is None}
    for key in ('rewards', 'airborne_state_machine_cfg', 'jump_takeoff_state_machine_cfg',
                'stair_state_machine_cfg', 'wheel_forward_scan_cfg',
                'obs_input_clip_cfg', 'obs_input_scale_cfg', 'obs_input_scale_streams',
                'height_obs_clip_range', 'height_range', 'jump_takeoff_permission_cfg'):
        values[key] = deepcopy(raw.get(key, {}))
    values['sim'] = SimpleNamespace(gravity=(0., 0., -9.81))
    values['use_absolute_height'] = False
    values['use_leg_length_as_height'] = False
    values['front_rear_joint_limit_rewards_enabled'] = False
    values['leg_action_mode'] = 'joint_pos'
    values['leg_action_dim'] = 4
    values['use_gimbal'] = False  # MOD4v1 has no gimbal; V14 no-gimbal contact branch
    values['reward_groups_enabled'] = False
    for key in ('airborne_state_machine_cfg', 'jump_takeoff_state_machine_cfg'):
        values[key].setdefault('enter', {})['wheel_radius'] = .0625
    values['stair_state_machine_cfg']['wheel_radius'] = .0625
    # Both optional physical assists remain disabled. These are reward/state hooks only.
    values['jump_takeoff_state_machine_cfg'].setdefault('assist', {})['enabled'] = False
    if profile == 'scut_stairs':
        # Select the published stair branch only, without restoring its other
        # rough terrain tasks. V13 applies this branch's saved height override.
        override = raw['terrain_command_overrides'].get('inv_stair_slope_for_rm_mid', {})
        values['height_range'] = tuple(override.get('height_range', [raw['height_range']])[0])
    if profile == 'jump270':
        values['height_range'] = (.25, .25)
        values['episode_length_s'] = 8.
        values['enable_state_machines'] = True
        for key in ('airborne_state_machine_cfg', 'stair_state_machine_cfg', 'wheel_forward_scan_cfg'):
            values[key]['enabled'] = True
        # 120-140mm detection would label the requested 270mm platform a wall.
        values['wheel_forward_scan_cfg']['detect'] = dict(
            step_height_min=.25, step_height_max=.29, wall_height=.30)
        values['wheel_forward_scan_cfg']['height_cmd'] = dict(bias=.27, hold_s=2., max=.61)
        # Relative body clearance on the platform; never change physical platform height.
        values['stair_state_machine_cfg']['height_cmd'] = dict(range=(.25, .34))
        values['stair_state_machine_cfg'].setdefault('failure', {})['terminate'] = False
        values['stair_state_machine_cfg']['reward_additions'] = {
            'mod4_stair_wheel_clearance': dict(type='wheel_above_reference_height',
                                               use_wheel_bottom=True, margin=.01, sigma=.01),
            'mod4_stair_height': dict(type='height_track_exp', sigma=.01),
        }
        values['rewards'].update(mod4_stair_wheel_clearance=1., mod4_stair_height=1.)
    if profile == 'jump200':
        values['height_range'] = (.25, .25)
        values['episode_length_s'] = 8.
        values['enable_state_machines'] = True
        values['airborne_state_machine_cfg']['enabled'] = True
        values['stair_state_machine_cfg']['enabled'] = False
        # StepUp supplies the original real-ray step event. Keep its temporary
        # height command at the normal .25m; ballistic rewards own the push.
        values['wheel_forward_scan_cfg'].update(enabled=True,
            detect=dict(step_height_min=.18, step_height_max=.22, wall_height=.23),
            height_cmd=dict(bias=0., hold_s=.2, max=.25))
        takeoff = values['jump_takeoff_state_machine_cfg']
        takeoff['enabled'] = True
        takeoff['trajectory'].update(enabled=True, peak_height=(.55, .60))
        takeoff['trigger'].update(mode='flag', require_tracking=False,
                                  min_episode_time_s=.2, cooldown_s=1.)
        takeoff['assist']['enabled'] = False
        takeoff['push']['reward_additions'] = {
            'jump200_push_height': dict(type='push_height_tracking_exp', sigma=.01),
            'jump200_push_velocity': dict(type='push_vel_z_tracking_exp', sigma=1.),
            'jump200_upward_velocity': dict(type='takeoff_vel_z', max=3.)}
        takeoff['tuck']['reward_additions'] = {
            'jump200_peak': dict(type='peak_height_tracking_exp', event='exit', sigma=.01)}
        takeoff['reward_scales'].update(lin_vel_z=0., track_height_square=0.,
                                       track_height_exp_tight=0.)
        values['rewards'].update(jump200_push_height=2., jump200_push_velocity=1.,
                                jump200_peak=2., jump200_upward_velocity=2.)
        # Actual final150 remained stationary for most endpoints and earned
        # .0825/control while only41/80 episodes requested takeoff. Gate the
        # approach's positive tracking bonuses by forward progress so waiting
        # before the measured step event no longer earns their full return.
        # Active takeoff and verified landing retain their own reward shaping.
        values['jump200_approach_progress_gate'] = True
        # Final263 reached the step in80/80 episodes, but its one temporal
        # scan event gave only one failed push. Permit another unassisted
        # attempt while the current forward and chassis-ground rays still
        # straddle this step.
        values['jump200_retry_visible_step'] = True
        # The failed pushes still earned the full flat/velocity bonuses at
        # almost zero upward speed. Gate those bonuses by measured ascent.
        values['jump200_takeoff_progress_gate'] = True
        # Final376 repeatedly pushed without flight while both hip targets
        # stayed clamped. Charge requests outside the existing feasible target
        # set; retain the processor, motor limits and CAD/D4 execution path.
        values['rewards']['jump200_target_projection'] = -2.
    return SimpleNamespace(**values)


def command_recipe(profile):
    """Saved command distribution; the 270mm course override is explicit."""
    raw = deepcopy(read_yaml('trained_env')['commands'])
    if profile in ('jump270', 'jump200'):
        raw.update(heading_command=False, rel_standing_envs=0., rel_heading_envs=0.,
                   special_modes=())
        raw['ranges'].update(lin_vel_x=(.6, .6), lin_vel_y=(0., 0.), ang_vel_z=(0., 0.))
    elif profile not in ('trained_stair', 'scut_stairs'):
        raise ValueError('Unknown SCUT profile')
    return raw


def ground_scan_config():
    """Keep the saved SCUT height-estimation footprint, independent of robot size."""
    raw = read_yaml('trained_env')['height_scanner']
    return dict(offset=tuple(raw['offset']['pos']),
                resolution=raw['pattern_cfg']['resolution'],
                size=tuple(raw['pattern_cfg']['size']),
                direction=tuple(raw['pattern_cfg']['direction']),
                ordering=raw['pattern_cfg']['ordering'],
                ray_alignment=raw['ray_alignment'], max_distance=raw['max_distance'])


def observation_component(cfg, key, value, stream='policy'):
    """Pinned observation order is clip, then scale; shared with both streams."""
    limit = cfg.obs_input_clip_cfg.get(key)
    if limit is not None:
        if isinstance(limit, (list, tuple)):
            value = value.clamp(float(limit[0]), float(limit[1]))
        else:
            value = value.clamp(-abs(float(limit)), abs(float(limit)))
    if not cfg.obs_input_scale_enabled or stream not in cfg.obs_input_scale_streams:
        return value
    scale = cfg.obs_input_scale_cfg.get(key, 1.)
    if isinstance(scale, dict):
        scale = [scale[k] for k in ('lin_vel_x', 'lin_vel_y', 'ang_vel_z')]
    return value * value.new_tensor(scale)


def current_airborne_config():
    """Additional current V14 branch, deliberately separate from the saved model.

Literal dictionaries/weights are extracted from the reviewed source; no task
constructor, gimbal, reset-assist or Isaac dependency is imported here.
"""
    import ast
    source = source_path('current_cfg').read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    base = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                and n.name == 'WheelbipeV14FlatEnvCfg')
    raw = next(ast.literal_eval(n.value) for n in base.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'airborne_state_machine_cfg' for t in n.targets))
    cfg = reward_config('trained_stair')
    cfg.airborne_state_machine_cfg = deepcopy(raw)
    cfg.airborne_state_machine_cfg['enabled'] = True
    cfg.airborne_state_machine_cfg['enter']['wheel_radius'] = .0625
    cfg.airborne_state_machine_cfg['reward_scales'].update(
        undesired_contact=25., flat_orientation_y_v=0., termination=6.,
        track_height_square=0., foot_bound_square=0.)
    cfg.airborne_state_machine_cfg['reward_additions'].update(
        airborne_joint_pos_limits=dict(type='rear2_rear1_joint_pos_limits'),
        airborne_wheel_heading_x_centering=dict(type='wheel_heading_x_centering',
            wheel_contact_duration_s=.02, base_contact_duration_s=.02,
            wheel_heading_z_max=-.1, sigma=.02))
    cfg.rewards.update(airborne_joint_pos_limits=-10., airborne_wheel_heading_x_centering=10.)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == '_apply_v14_airborne_landing_precontact_cfg')
    # This original source function operates only on dictionaries and copy.
    unit = ast.Module(body=[function], type_ignores=[])
    namespace = {'copy': __import__('copy')}
    exec(compile(unit, str(source_path('current_cfg')), 'exec'), namespace)
    namespace[function.name](cfg)
    return cfg


def runner_config():
    """Translate the pinned RSL ActorCritic schema into installed RSL 5 MLP schema."""
    raw = read_yaml('trained_agent')
    p = raw['policy']
    model = dict(class_name='MLPModel', activation=p['activation'], obs_normalization=False)
    return dict(num_steps_per_env=raw['num_steps_per_env'], save_interval=raw['save_interval'],
                obs_groups={'actor': ['policy'], 'critic': ['critic']},
                actor=dict(**model, hidden_dims=p['actor_hidden_dims'], distribution_cfg=dict(
                    class_name='GaussianDistribution', init_std=p['init_noise_std'], std_type='scalar')),
                critic=dict(**model, hidden_dims=p['critic_hidden_dims']), algorithm=deepcopy(raw['algorithm']),
                logger='tensorboard', check_for_nan=True, empirical_normalization=False)


def model_contract(asset_dir):
    import hashlib
    folder = Path(asset_dir)
    for name, expected in [('robot.usd', USD_SHA), ('import_contract.json', CONTRACT_SHA)]:
        if hashlib.sha256((folder/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Enhanced MOD4v1 identity mismatch: '+name)
    contract = json.loads((folder/'import_contract.json').read_text(encoding='utf-8-sig'))
    if len(contract['bodies']) != 31 or contract['articulation_joint_count'] != 30:
        raise ValueError('Unexpected MOD4v1 structure')
    return contract
