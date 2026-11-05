"""SCUT task bridge with v2 reset-domain and native hardware readback."""
import hashlib
import json
from pathlib import Path
import torch
from . import BINDINGS
from .hardware import adapter
from .shared import load, export

_source = load('sdk')
export(_source, globals())


def consistent_reset_v2(env, env_ids):
    import mod4_task as task
    robot = env.scene['robot']
    ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids
    if not len(ids):
        return
    bank = getattr(env, '_mod4v2_reset_bank', None)
    if bank is None:
        path = Path(BINDINGS['reset_bank'])
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != BINDINGS['reset_bank_SHA']:
            raise ValueError('Referenced source reset bank changed')
        poses = [p for p in json.loads(raw)['poses'] if .24 <= p['root_height_m'] <= .272]
        geometry = adapter()._geometry()
        for pose in poses:
            for side in ('left', 'right'):
                values = {name[len(side)+1:]: value for name, value in pose['joint_pos'].items()
                          if name.startswith(side + '_')}
                geometry.check_joint_limits(values, side=side, tolerance=1e-7)
        if len(poses) != 74:
            raise ValueError('Expected the validated74 v2-feasible source reset poses')
        q = torch.tensor([[p['joint_pos'].get(n, 0.) for n in robot.joint_names] for p in poses],
                         device=env.device, dtype=torch.float32)
        h = torch.tensor([p['root_height_m'] for p in poses], device=env.device)
        bank = (q, h)
        env._mod4v2_reset_bank = bank
    qbank, hbank = bank
    pick = torch.randint(len(hbank), (len(ids),), device=env.device)
    q = qbank[pick]
    robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=ids)
    root = robot.data.root_state_w[ids].clone()
    root[:, 2] = env.scene.env_origins[ids, 2] + hbank[pick]
    root[:, 7:] = 0.
    robot.write_root_state_to_sim(root, env_ids=ids)
    task.height_cmd(env)[ids] = .25


def configure(cfg, n, profile='jump200', contract=None):
    global MESH
    _source.configure(cfg, n, profile, contract)
    # The shared configure selects the actual course mesh after this module's
    # initial export. Evaluation must read that selected path, not its default.
    MESH = _source.MESH
    cfg.events.consistent_start.func = consistent_reset_v2
    # Installed SDK names this field physics; the release template's physx is stale.
    cfg.sim.physics.solver_type = 1
    return cfg


def native_hardware_readback(env, tensor):
    import math
    robot = env.scene['robot']
    names = list(robot.joint_names)
    geometry = adapter()._geometry()
    native = tensor(robot.root_view.get_dof_limits())
    rows = []
    for side in ('left', 'right'):
        for key, bounds in geometry.JOINT_BOUNDS.items():
            name = side + '_' + key
            actual = native[0, names.index(name)]
            for endpoint, wanted in enumerate(bounds):
                value = float(actual[endpoint])
                if wanted is None:
                    if not (value < -1e7 if endpoint == 0 else value > 1e7):
                        raise ValueError('v2 continuous/one-sided limit was narrowed: ' + name)
                elif abs(value - wanted) > 1e-6:
                    raise ValueError('v2 native mechanical stop differs: ' + name)
            rows.append(dict(name=name, native_SI=[float(v) if math.isfinite(float(v))
                else str(float(v)) for v in actual], expected_SI=bounds))
    gas_ids = [names.index(side + '_gas_slide') for side in ('left', 'right')]
    target = env.cfg.events.gas_spring_preload.params['targets']
    if max(abs(value - .1706394410901294) for value in target) > 1e-10:
        raise ValueError('v2 preload event has an old400N target')
    stiffness = tensor(robot.root_view.get_dof_stiffnesses())[:, gas_ids]
    damping = tensor(robot.root_view.get_dof_dampings())[:, gas_ids]
    expected_k = env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal)
    expected_d = env._gas_damping.component.actual_damping_Ns_per_m()
    if not torch.equal(stiffness.to(expected_k.device), expected_k):
        raise ValueError('v2 actual gas stiffness differs from retained D5')
    if not torch.equal(damping.to(expected_d.device), expected_d):
        raise ValueError('v2 actual gas damping differs from retained D6')
    return dict(native_limit_rows=rows, gas_target_m=target,
                gas_stiffness_n_m=2000., gas_damping_ns_m=3.,
                fresh_constructor=True, nominal_extension_force_n=300.,
                force_curve_calibrated=False, active_joint_boxes_removed=True,
                action_class=env.action_manager.get_term('legs').__class__.__name__,
                physics_dt=env.physics_dt, policy_dt=env.step_dt,
                reset_bank_poses_validated=74)


class ScutBridge(_source.ScutBridge):
    def __init__(self, env, task, contract, tensor, profile='jump200'):
        self.hardware_readback = native_hardware_readback(env, tensor)
        super().__init__(env, task, contract, tensor, profile)
        import os
        from .train import put
        put(Path(os.environ['MOD4V1_E0_JOB_ROOT']) / 'MOD4V2_NATIVE_HARDWARE.json',
            self.hardware_readback)
        from .config import reward_config
        recipe = reward_config(profile)
        put(Path(os.environ['MOD4V1_E0_JOB_ROOT']) / 'FUDAN_REWARD_RECIPE.json', dict(
            family='FUDAN_JUMP', commit=recipe.fudan_reward_commit,
            weights=recipe.rewards, clip_single_weighted_rate=2.5, dt=.02,
            virtual_leg='Measured body-frame hip-to-wheel sagittal L0/theta',
            tuck_length_m=.16, extend_length_m=.31, flight_base_height_m=.65,
            original_contact_filter='vertical wheel force>1N OR previouscontrol contact',
            SCUT_reward_terms_active=False, physical_assists=False))
        if os.environ.get('MOD4_WARP_SAMPLING') == '1':
            from .warp_sampling import install
            receipt = install(self)
            put(Path(os.environ['MOD4V1_E0_JOB_ROOT']) / 'WARP_SAMPLING.json', receipt)

    def snapshot(self, terminated, timeout):
        value = super().snapshot(terminated, timeout)
        r = self.reward
        value.update(fudan_leg_length=r.fudan_leg_length.clone(),
                     fudan_leg_theta=r.fudan_leg_theta.clone(),
                     fudan_contact_filt=r.fudan_contact_filt.clone(),
                     fudan_was_in_flight=r.fudan_was_in_flight.clone(),
                     fudan_base_air_time=r.fudan_base_air_time.clone())
        return value
