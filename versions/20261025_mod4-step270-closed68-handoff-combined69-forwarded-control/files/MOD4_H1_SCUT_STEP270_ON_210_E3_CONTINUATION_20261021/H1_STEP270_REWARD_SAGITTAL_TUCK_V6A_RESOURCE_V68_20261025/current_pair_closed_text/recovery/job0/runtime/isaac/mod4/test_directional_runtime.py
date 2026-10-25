"""CPU lifecycle checks with a minimal SDK double; NOT Isaac acceptance."""
from pathlib import Path
from types import SimpleNamespace as NS
import importlib.util
import json
import math
import os
import sys
import types

import torch


class SDKDouble:
    def __init__(self, cfg, env):
        self.cfg, self.num_envs, self.device = cfg, env.num_envs, 'cpu'
        self.robot = env.robot
        self.vel_command_b = torch.zeros(env.num_envs, 3)
        self.is_heading_env = torch.zeros(env.num_envs, dtype=torch.bool)
        self.is_standing_env = torch.zeros_like(self.is_heading_env)

    @property
    def command(self): return self.vel_command_b

    def _resample_command(self, ids):
        self.vel_command_b[ids, 0] = 3 * torch.rand(len(ids)) - 1.5
        self.vel_command_b[ids, 1] = 0
        self.is_standing_env[ids] = torch.rand(len(ids)) < self.cfg.rel_standing_envs

    def _update_command(self):
        self.vel_command_b[self.is_standing_env] = 0


def main():
    fake = types.ModuleType('isaaclab.envs.mdp.commands.velocity_command')
    fake.UniformVelocityCommand = SDKDouble
    sys.modules[fake.__name__] = fake
    from directional_spin_runtime import DirectionalSpinCommand, transition_yaw, audit
    cfg = NS(heading_command=False, rel_heading_envs=0, rel_standing_envs=.1,
             resampling_time_range=(12, 16))
    heading = torch.zeros(6000)
    env = NS(num_envs=6000, robot=NS(data=NS(heading_w=NS(torch=heading))),
             cfg=NS(seed=20261002), step_dt=.01)
    torch.manual_seed(20261002)
    cmd = DirectionalSpinCommand(cfg, env); ids = torch.arange(env.num_envs)
    cmd._resample_command(ids);cmd._update_command()
    env.command_manager = NS(get_term=lambda _:cmd)
    first = audit(env)
    for key, expected in [('stand_fraction_actual',.1),('pure_fraction_actual',.3),
                          ('moving_fraction_actual',.2),('transition_fraction_actual',.1)]:
        assert abs(first[key] - expected) < .025, (key, first[key])
    assert cmd.command.shape == (6000, 3) and cmd.command[:,1].abs().max() == 0
    moving = cmd.is_moving_spin.clone()
    assert moving.any() and cmd.command[moving,2].abs().min() >= 1
    assert cmd.command[moving,2].abs().max() <= 2
    before = cmd.command.clone()
    heading[:] = math.pi / 2;cmd._update_command();audit(env)
    assert not torch.allclose(before[moving,0],cmd.command[moving,0])
    heading[:] = math.pi;cmd._update_command();audit(env)
    assert torch.allclose(cmd.command[moving,0],-before[moving,0],atol=1e-6)
    untouched = cmd.command[20:].clone()
    cmd._resample_command(torch.arange(20))
    assert torch.equal(cmd.command[20:],untouched)
    cmd._resample_command(ids);cmd._update_command();audit(env)
    assert not (cmd.is_pure_spin & cmd.is_moving_spin).any()
    assert not (cmd.is_moving_spin & cmd.is_standing_env).any()
    t = torch.tensor([0.,.5,1.,4.,4.5,5.,6.,6.5,7.,10.,10.5,11.,12.])
    expected = torch.tensor([0.,.5,1.,1.,.5,0.,0.,-.5,-1.,-1.,-.5,0.,0.])
    assert torch.equal(transition_yaw(t,torch.ones_like(t)),expected)
    transition = cmd.is_transition_spin
    cmd.phase_elapsed[transition] = 6.5;cmd._update_command()
    assert torch.allclose(cmd.command[transition,2],-.5*cmd.signed_yaw[transition])
    cmd.phase_elapsed[transition] = 11.5;cmd._update_command()
    assert cmd.command[transition,2].abs().max() == 0
    cmd.set_manual_evaluation_mode();cmd.is_standing_env[:] = False
    cmd.command[:,:] = torch.tensor([.3,0.,1.]);old=cmd.command.clone()
    heading[:] = -1.;cmd._update_command();assert torch.equal(cmd.command,old)
    cmd.is_standing_env[:10] = True;cmd._update_command();assert cmd.command[:10].abs().max() == 0
    try:
        bad = NS(**vars(cfg));bad.heading_command=True;DirectionalSpinCommand(bad,env)
        raise AssertionError('Invalid heading was accepted')
    except ValueError:pass
    evidence = {'cpu_only_sdk_double': True, 'actual_isaac_runtime_verified': False,
                'mode_fractions': first, 'heading_projection_refresh':True,
                'subset_reset_preserves_other_commands':True, 'standing_and_modes_do_not_overlap':True,
                'train_time_start_stop_reverse_profile':True, 'manual_frozen_evaluation_not_overridden':True,
                'command_width_3':True,'reward_ppo_physics_not_exercised':True}
    Path(__file__).with_name('CPU_RUNTIME_LIFECYCLE.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence))


if __name__ == '__main__': main()
