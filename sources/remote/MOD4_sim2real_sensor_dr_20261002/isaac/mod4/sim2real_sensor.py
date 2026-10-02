"""Independent sensor whitelist alongside white_v1; legacy DR stays disabled."""
import os
import torch
from isaaclab.managers import ManagerTermBase, EventTermCfg
from sensor_core import SensorCore


class SensorEvent(ManagerTermBase):
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self.profile = os.environ.get('RM_SIM2REAL_SENSOR_PROFILE', 'off')
        self.core = SensorCore(env.num_envs, env.device, env.cfg.seed or 0, profile=self.profile)
        env._sim2real_sensor = self
        # Preserve the original physical audit and correct its old global label.
        # Otherwise "noise/delay unchanged" would contradict this separate profile.
        original_audit = env._mild_dr.audit
        def scoped_audit():
            result = original_audit()
            result['other_randomization'] = 'spring/PD/COM/armature/joint-friction/push unchanged; actor sensing uses separate ' + self.profile
            result['audit_scope'] = 'white_v1 physical parameters; sensor perturbations reported separately'
            return result
        env._mild_dr.audit = scoped_audit

    def __call__(self, env, env_ids):
        ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids.to(env.device)
        # This event is appended after white_v1: physical nominal samples stay clean.
        assert hasattr(env, '_mild_dr'), 'white_v1 parameter event must precede sensor reset'
        self.core.reset(ids, env._mild_dr.nominal[ids])

    def transform(self, env, key, value):
        return self.core.sample(key, value, env.common_step_counter)

    def audit(self):
        return self.core.audit()


def configure(cfg):
    profile = os.environ.get('RM_SIM2REAL_SENSOR_PROFILE', 'off')
    assert profile in ('off', 'sensor_v1', 'sensor_noise_v1', 'sensor_delay_v1'), profile
    if profile == 'off' or os.environ.get('RM_MILD_DR_PROFILE') == 'nominal':
        return
    assert os.environ.get('RM_MILD_DR_PROFILE') == 'white_v1'
    assert os.environ.get('RM_DR_OFF') == '1'
    for name in ('base_ang_vel', 'projected_gravity', 'leg_pos', 'leg_vel', 'wheel_vel'):
        assert getattr(cfg.observations.policy, name).noise is None, 'No double noise injection'
    cfg.events.sim2real_sensor = EventTermCfg(func=SensorEvent, mode='reset')


def audit(env):
    term = getattr(env, '_sim2real_sensor', None)
    return term.audit() if term else {'profile': 'off', 'critic_reward_and_plant_unchanged': True}
