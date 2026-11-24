"""Deterministic, batched operator/proprioception-only finite state machine.

All times are counted in 20 ms control ticks. No engine object is accepted.
"""
from dataclasses import dataclass, asdict
from enum import IntEnum
import math
import torch

class Phase(IntEnum):
    CRUISE_E0 = 0
    STAIR_ARMED_APPROACH = 1
    STAIR_CLIMB_ACTIVE = 2
    TREAD_BRIDGE = 3
    DECK_SETTLE = 4
    JUMP_380MM = 5

LABELS = ('巡航 E0', '上阶预备(未触阶直立)', '触阶攀爬 E_stair',
          '阶面过渡', '台顶稳态', '大跳')

@dataclass
class DetectorConfig:
    pitch_impulse: float = .10
    pitch_rate_impulse: float = .32
    wheel_deceleration: float = .35
    leg_impulse: float = .35
    impact_pitch_min: float = -1.
    sensor_ema_alpha: float = 1.
    sensor_noise_norm_threshold: float = .003
    noisy_pitch_impulse: float = .05
    noisy_pitch_rate_impulse: float = .12
    noisy_wheel_deceleration: float = .15
    noisy_leg_impulse: float = .15
    noisy_impact_pitch_min: float = -.1
    noisy_fast_pitch_impulse: float = .01
    noisy_fast_rate_impulse: float = .5
    blocked_pitch: float = .11
    blocked_wheel_m_s: float = .15
    blocked_ticks: int = 6
    confirmation_ticks: int = 1
    arm_height: float = .390
    deck_height: float = .350
    min_climb_ticks: int = 15
    stable_ticks: int = 10
    bridge_ticks: int = 8
    deck_wait_ticks: int = 20

    def to_dict(self):
        return asdict(self)

class ManualFSM:
    def __init__(self, count=1, device='cpu', config=None):
        self.n, self.device = count, device
        self.config = config or DetectorConfig()
        self.phase = torch.zeros(count, dtype=torch.long, device=device)
        self.mode = torch.zeros(count, dtype=torch.bool, device=device)
        self.age = torch.zeros_like(self.phase)
        self.forward_ticks = torch.zeros_like(self.phase)
        self.blocked_ticks = torch.zeros_like(self.phase)
        self.confirm_ticks = torch.zeros_like(self.phase)
        self.stable_ticks = torch.zeros_like(self.phase)
        self.since_contact = torch.full_like(self.phase, 100000)
        self.height = torch.full((count,), .35, device=device)
        self.climb_motion = torch.zeros_like(self.mode)
        self.initialized = torch.zeros_like(self.mode)
        self.previous = torch.zeros(count, 35, device=device)
        self.trigger_reason = torch.zeros_like(self.phase)
        self.transitions = torch.zeros_like(self.phase)
        self.settle_ema = torch.zeros(count, 3, device=device)
        self.sensor_ema = torch.zeros(count,35,device=device)
        self.sensor_noise_seen = torch.zeros(count,dtype=torch.bool,device=device)

    def reset(self, ids=None):
        if ids is None:
            ids = torch.arange(self.n, device=self.device)
        for name in ('phase', 'age', 'forward_ticks', 'blocked_ticks', 'confirm_ticks', 'stable_ticks',
                     'mode', 'climb_motion', 'initialized', 'previous', 'trigger_reason', 'transitions'):
            getattr(self, name)[ids] = 0
        self.since_contact[ids] = 100000
        self.settle_ema[ids] = 0.
        self.sensor_ema[ids] = 0.
        self.sensor_noise_seen[ids] = False

    @torch.no_grad()
    def update(self, obs, *, mode, forward, reverse=None, force=None, jump=None):
        c = self.config
        mode = torch.as_tensor(mode, device=self.device).bool().expand(self.n)
        forward = torch.as_tensor(forward, device=self.device).bool().expand(self.n)
        zero = torch.zeros_like(mode)
        reverse = zero if reverse is None else torch.as_tensor(reverse, device=self.device).bool().expand(self.n)
        force = zero if force is None else torch.as_tensor(force, device=self.device).bool().expand(self.n)
        jump = zero if jump is None else torch.as_tensor(jump, device=self.device).bool().expand(self.n)
        old = self.phase.clone()
        fresh = ~self.initialized
        self.sensor_ema[fresh]=obs[fresh]
        self.sensor_noise_seen |= (obs[:,7:10].norm(dim=1)-1.).abs()>c.sensor_noise_norm_threshold
        alpha=torch.where(self.sensor_noise_seen,c.sensor_ema_alpha,1.)[:,None]
        self.sensor_ema += alpha*(obs-self.sensor_ema)
        self.sensor_ema[:,:4]=obs[:,:4]
        self.sensor_ema[:,22:]=obs[:,22:]
        obs=self.sensor_ema
        self.previous[fresh] = obs[fresh]
        self.height[fresh] = obs[fresh, 3]*.2
        self.initialized.fill_(True)
        self.age += 1
        self.since_contact += 1
        intent = mode & forward & ~reverse & (obs[:, 0] > .15)
        self.forward_ticks.copy_(torch.where(intent, self.forward_ticks+1, 0))
        p = self.previous
        # obs[20:22] = wheel angular speed * .1, radius .0625 m.
        wheel = obs[:, 20:22].mean(1)*.625
        last_wheel = p[:, 20:22].mean(1)*.625
        dpitch = (obs[:, 7] - p[:, 7]).abs()
        rate = (obs[:, 5] - p[:, 5]).abs()
        leg = (obs[:, 16:20]-p[:, 16:20]).abs().amax(1)
        decel = last_wheel-wheel
        noise=self.sensor_noise_seen
        dp_limit=torch.where(noise,c.noisy_pitch_impulse,c.pitch_impulse)
        rate_limit=torch.where(noise,c.noisy_pitch_rate_impulse,c.pitch_rate_impulse)
        decel_limit=torch.where(noise,c.noisy_wheel_deceleration,c.wheel_deceleration)
        leg_limit=torch.where(noise,c.noisy_leg_impulse,c.leg_impulse)
        pitch_floor=torch.where(noise,c.noisy_impact_pitch_min,c.impact_pitch_min)
        impact = ((dpitch > dp_limit) & (rate > rate_limit))
        impact |= ((decel > decel_limit) & (rate > rate_limit) & (leg > leg_limit))
        impact |= noise & (dpitch>c.noisy_fast_pitch_impulse) & (rate>c.noisy_fast_rate_impulse)
        impact &= obs[:,7] > pitch_floor
        blocked = (self.forward_ticks >= c.blocked_ticks) & (wheel.abs() < c.blocked_wheel_m_s)
        # Forward acceleration pitches the body in the opposite direction.
        # Its initial wheel reversal must never be interpreted as a wall.
        blocked &= obs[:, 7] > c.blocked_pitch
        self.blocked_ticks.copy_(torch.where(blocked, self.blocked_ticks+1, 0))
        evidence = intent & (impact | (self.blocked_ticks >= 2))
        self.confirm_ticks.copy_(torch.where(evidence, self.confirm_ticks+1, 0))
        confirmed = (self.confirm_ticks >= c.confirmation_ticks) | (mode & force & ~reverse)
        eligible = (old == Phase.STAIR_ARMED_APPROACH) | (old == Phase.DECK_SETTLE) | (old == Phase.TREAD_BRIDGE)
        trigger = eligible & confirmed & (intent | force)
        start = (old == Phase.CRUISE_E0) & (intent | (mode & force & forward & ~reverse))
        self.phase[start] = Phase.STAIR_ARMED_APPROACH
        trigger |= start & confirmed
        self.phase[trigger] = Phase.STAIR_CLIMB_ACTIVE
        self.trigger_reason.zero_()
        self.trigger_reason[trigger & impact] = 1
        self.trigger_reason[trigger & blocked] = 2
        self.trigger_reason[trigger & force] = 3
        self.since_contact[trigger] = 0
        self.climb_motion[trigger] = False
        self.stable_ticks[trigger] = 0
        self.climb_motion |= (self.phase == Phase.STAIR_CLIMB_ACTIVE) & (
            (obs[:, 7].abs() > .12) | ((obs[:, [11, 13]]-p[:, [11, 13]]).abs().amax(1) > .07))
        measured = torch.stack((obs[:, 7], obs[:, 5], obs[:, 16:20].abs().mean(1)), 1)
        self.settle_ema[fresh] = measured[fresh]
        self.settle_ema += .25*(measured-self.settle_ema)
        stable = (self.settle_ema[:, 0].abs() < math.sin(math.radians(8))) & (obs[:, 8].abs() < .10)
        stable &= self.settle_ema[:, 1].abs() < .24
        stable &= self.settle_ema[:, 2] < .40
        # Hand E0 a restored leg posture. Handing back while both legs remain
        # deeply folded puts E0 outside its demonstrated recovery states.
        restored = (obs[:, [10, 12]]-obs[:, [11, 13]] > .02).all(1)
        stable &= restored
        counting=self.phase==Phase.STAIR_CLIMB_ACTIVE
        self.stable_ticks.copy_(torch.where(counting,torch.where(stable,self.stable_ticks+1,
            (self.stable_ticks-1).clamp_min(0)),0))
        climb = (old == Phase.STAIR_CLIMB_ACTIVE) & (self.age >= c.min_climb_ticks)
        finish = climb & self.climb_motion & (self.stable_ticks >= c.stable_ticks)
        self.phase[finish] = Phase.TREAD_BRIDGE
        bridge_done = (old == Phase.TREAD_BRIDGE) & (self.age >= c.bridge_ticks) & ~trigger
        self.phase[bridge_done] = Phase.STAIR_ARMED_APPROACH
        deck = (old == Phase.STAIR_ARMED_APPROACH) & (self.phase == Phase.STAIR_ARMED_APPROACH)
        deck &= (self.since_contact < 100000) & (self.age >= c.deck_wait_ticks)
        self.phase[deck & ~trigger] = Phase.DECK_SETTLE
        # The operator veto is applied last, on this very control tick.
        cancel = ~mode | ~forward | reverse
        self.phase[cancel & (old != Phase.JUMP_380MM)] = Phase.CRUISE_E0
        self.phase[jump] = Phase.JUMP_380MM
        self.mode.copy_(mode)
        changed = self.phase != old
        self.age[changed] = 0
        self.transitions += changed
        active = self.phase == Phase.STAIR_CLIMB_ACTIVE
        target = obs[:, 3]*.2
        prepare = (mode & ~reverse & (self.phase == Phase.CRUISE_E0))
        target = torch.where(prepare | (self.phase == Phase.STAIR_ARMED_APPROACH) | active | (self.phase == Phase.TREAD_BRIDGE),
                             c.arm_height, target)
        target = torch.where(self.phase == Phase.DECK_SETTLE, c.deck_height, target)
        self.height += (target-self.height).clamp(-.004, .004)
        self.previous.copy_(obs)
        self.features = torch.stack((dpitch, rate, decel, leg, wheel, obs[:, 7].abs()), 1)
        return self.phase

    @property
    def stair_weight(self):
        active = (self.phase == Phase.STAIR_CLIMB_ACTIVE).float()
        bridge = self.phase == Phase.TREAD_BRIDGE
        return torch.where(bridge, (1.-self.age.float()/self.config.bridge_ticks).clamp(0., 1.), active)
