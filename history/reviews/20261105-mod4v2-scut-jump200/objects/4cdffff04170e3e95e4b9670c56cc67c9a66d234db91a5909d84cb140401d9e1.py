"""Explicit MOD4 context v2; the physical sensor/DR implementations stay intact.

The first139 channels retain the old layout. New privileged channels contain
episode parameters, encoder bias, the real clean100Hz midpoint and terrain.
Only genuinely unknown dynamic channels are learned. Imagined sensor samples
use the same uniform bounds, bias and0/10ms endpoint delay as the real task;
the midpoint itself is learned from the recorded100Hz physical midpoint.
"""
import math
import torch

from .supermimic_newton import FudanJumpMdp, NewtonSuperMimicBridge

SCHEMA = 'mod4v2.context176.closed_loop_real_value.v2'
OLD_DIM, CONTEXT_DIM = 139, 176
DR = slice(139, 152)        # pressure2, damping2, COM3, motor gains6
BIAS = slice(152, 156)      # episode leg encoder bias
MID = slice(156, 172)       # clean100Hz sensor sample at t+10ms
TERRAIN = slice(172, 176)   # .8-x, y, heading cosine/sine
SENSOR_SLICES = (slice(4, 7), slice(7, 10), slice(10, 14), slice(16, 20), slice(20, 22))


def terrain(state):
    position, rotation = state[:2]
    return torch.cat((.8-position[..., :1], position[..., 1:2], rotation[..., :2, 0]), -1)


class ClosedLoopMdp(FudanJumpMdp):
    def __init__(self, env):
        super().__init__(CONTEXT_DIM)
        self.legs, self.wheels = tuple(env.legs), tuple(env.wheels)
        from .config import reward_config
        self.observation_cfg = reward_config()
        from .hardware import adapter
        geometry=adapter()._geometry()
        self.mechanical_bounds=[geometry.mechanical_delta_bounds(side) for side in ('left','right')]
        self.noise_bounds = torch.tensor([.125]*3+[.025]*3+[.005]*4+[.25]*4+[.5]*2,
                                          device=env.device)

    def clean_sensors(self, state):
        _, rotation, _, omega, q, qd = state
        local_omega = (rotation.transpose(-1, -2)@omega.unsqueeze(-1)).squeeze(-1)
        gravity = -rotation[..., 2, :]
        return torch.cat((local_omega, gravity, q[..., self.legs], qd[..., self.legs],
                          qd[..., self.wheels]), -1)

    def encode_sensors(self, raw):
        from .config import observation_component
        return torch.cat([observation_component(self.observation_cfg, key, part)
                          for key, part in zip(('root_ang_vel_b', 'projected_gravity_b',
                                                'joint_pos', 'joint_vel_leg', 'joint_vel_wheel'),
                                               raw.split((3, 3, 4, 4, 2), -1))], -1)

    def predict_mask(self, device):
        mask = torch.zeros(CONTEXT_DIM, device=device)
        # Task state machine/ray height, torque, wheel kinematics/contact and
        # original Fudan memory still need learned dynamics. Midpoint is clean.
        for part in (slice(3,4), slice(28,35), slice(66,67), slice(86,92),
                     slice(98,106), slice(113,123), slice(124,133), slice(134,139), MID):
            mask[part] = 1
        return mask

    def valid_imagination_start(self, frames, horizon):
        return (frames >= 0) & (frames < 399)

    def project(self, previous, delta, state1, action, frames, *, noisy=True, state0=None):
        value = previous + self.predict_mask(previous.device)*delta
        clean = self.clean_sensors(state1)
        # Midpoint target is actually recorded at100Hz, not a linearized pose.
        delayed = previous[..., 92:93] >= .5
        sensed = torch.where(delayed, value[..., MID], clean)
        if noisy:
            sensed = sensed + (2*torch.rand_like(sensed)-1)*self.noise_bounds
        sensed = torch.cat((sensed[..., :6], sensed[..., 6:10]+previous[..., BIAS], sensed[..., 10:]), -1)
        encoded, clean_encoded = self.encode_sensors(sensed), self.encode_sensors(clean)
        value = value.clone()
        cursor = 0
        for block in SENSOR_SLICES:
            width = block.stop-block.start
            value[..., block] = encoded[..., cursor:cursor+width]
            value[..., slice(block.start+35, block.stop+35)] = clean_encoded[..., cursor:cursor+width]
            cursor += width
        value[..., :3] = previous[..., :3]
        value[..., 35:38] = previous[..., :3]
        value[..., 38] = value[..., 3]
        value[..., 14:16] = 0
        value[..., 49:51] = 0
        value[..., 22:28] = action
        value[..., 57:63] = action
        rotation, lin_vel = state1[1], state1[2]
        from .config import observation_component
        value[..., 63:66] = observation_component(self.observation_cfg, 'root_lin_vel_b',
            (rotation.transpose(-1,-2)@lin_vel.unsqueeze(-1)).squeeze(-1), 'critic')
        value[..., 67:74] = value[..., 28:35]
        # All queued actions have applied by the50Hz endpoint: configured lag
        # is at most2physics ticks, versus8ticks per control. Reproduce the
        # original target processor instead of predicting contradictory queues.
        current=(state0[4][...,self.legs] if state0 is not None else previous[...,45:49])
        targets=action[...,:4]*.5
        targets=targets.clone()
        for k,(c,h) in enumerate(((0,1),(2,3))):
            raw=targets[...,c]-targets[...,h]
            lo,hi=self.mechanical_bounds[k]
            gap=(raw+torch.round((current[...,c]-current[...,h]-raw)/(2*math.pi))*2*math.pi).clamp(lo,hi)
            hip=targets[...,h]+torch.round((current[...,h]-targets[...,h])/(2*math.pi))*2*math.pi
            targets[...,h]=hip;targets[...,c]=hip+gap
        value[...,124:128]=targets;value[...,128:132]=targets;value[...,132]=0
        value[...,134:136]=action[...,4:]*10;value[...,136:138]=action[...,4:]*10;value[...,138]=0
        value[..., TERRAIN] = terrain(state1)
        return value

    def project_predicted_context(self, context, state1, action, frames):
        raise RuntimeError('Context v2 requires previous context plus explicit delta')


class ClosedLoopBridge(NewtonSuperMimicBridge):
    def __init__(self, env):
        self.midpoint = None
        super().__init__(env)
        self.supermimic_mdp = ClosedLoopMdp(env)

    def clean(self):
        d, e = self.real.data, self.real
        return torch.cat((d.root_ang_vel_b, d.projected_gravity_b, d.joint_pos[:,e.legs],
                          d.joint_vel[:,e.legs], d.joint_vel[:,e.wheels]), -1).detach().clone()

    def observe(self, env):
        super().observe(env)
        if env.physics_ticks % 8 == 4:
            self.midpoint = self.clean()

    def context(self, obs):
        from supermimic_vendor_v2.geometry import unflatten_state
        e = self.real
        old = super().context(obs)
        constants = torch.cat((e._spring_pressure.component.factor, e._gas_damping.component.factor,
                               e._chassis_com.component.delta_m, e.motor_gain,
                               e._sensor_mild.bias), -1)
        # At reset the real delay queue also initializes with the new sample.
        fresh = e.episode_length_buf == 0
        clean = self.clean()
        mid = clean if self.midpoint is None else torch.where(fresh[:,None], clean, self.midpoint)
        return torch.cat((old, constants, mid, terrain(unflatten_state(self.pack()))), -1).detach().clone()
