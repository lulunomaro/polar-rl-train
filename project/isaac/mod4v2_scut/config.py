"""Published SCUT base rewards and its optional ballistic jump equations."""
from .shared import load, export
_source = load('config')
export(_source, globals())

USD_SHA = '97e845c8dcc2485d91081949a8531d67771893731e31d04316b4e67d7ec9dbaa'
CONTRACT_SHA = '00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e'
ACTION_INTERFACE = 'mod4v2_clip6_before_PD_reward_and_action_history'
TARGET_INTERFACE = 'mod4v2_HW300N60_continuous_common_turn_mechanical_delta_before_D4'


def reward_config(profile='jump200'):
    if profile != 'jump200':
        raise ValueError('This fresh MOD4v2 task selects only single200mm jumping')
    cfg = _source.reward_config('trained_stair')
    cfg.height_range = (.25, .25)
    cfg.episode_length_s = 8.
    cfg.enable_state_machines = True
    cfg.airborne_state_machine_cfg['enabled'] = True
    cfg.stair_state_machine_cfg['enabled'] = False
    cfg.wheel_forward_scan_cfg.update(enabled=True,
        detect=dict(step_height_min=.18, step_height_max=.22, wall_height=.23),
        height_cmd=dict(bias=0., hold_s=.2, max=.25))
    takeoff = cfg.jump_takeoff_state_machine_cfg
    takeoff['enabled'] = True
    takeoff['trajectory'].update(enabled=True, peak_height=(.55, .60))
    takeoff['trigger'].update(mode='flag', require_tracking=False,
                              min_episode_time_s=.2, cooldown_s=1.)
    takeoff['assist']['enabled'] = False
    takeoff['push']['reward_additions'] = {
        'scut_jump_push_height': dict(type='push_height_tracking_exp', sigma=.01),
        'scut_jump_push_velocity': dict(type='push_vel_z_tracking_exp', sigma=1.)}
    takeoff['tuck']['reward_additions'] = {
        'scut_jump_peak': dict(type='peak_height_tracking_exp', event='exit', sigma=.01)}
    takeoff['reward_scales'].update(lin_vel_z=0., track_height_square=0.,
                                   track_height_exp_tight=0.)
    cfg.rewards.update(scut_jump_push_height=2., scut_jump_push_velocity=1., scut_jump_peak=2.)
    # A current real step ray may request another unassisted source attempt.
    # This is task triggering, with no additional reward formula or reward gate.
    cfg.jump200_retry_visible_step = True
    return cfg


def model_contract(asset_dir):
    import hashlib
    folder = Path(asset_dir)
    for name, expected in [('robot.usd', USD_SHA), ('import_contract.json', CONTRACT_SHA)]:
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
            raise ValueError('MOD4v2 HW300N60 identity mismatch: ' + name)
    contract = json.loads((folder / 'import_contract.json').read_bytes())
    if len(contract['bodies']) != 31 or contract['articulation_joint_count'] != 30:
        raise ValueError('MOD4v2 structure differs')
    return contract
