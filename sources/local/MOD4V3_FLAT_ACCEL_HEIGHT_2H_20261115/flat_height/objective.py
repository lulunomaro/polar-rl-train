"""One-flight height accounting; landing settles the main height reward."""
import torch

SCHEMA = 'MOD4V3_MOVING_JUMP_PHASE_OBS_V1'
SLOTS = ['base_mode', 'jump_request', 'measured_air', 'landing_preparation',
         'preparation_cue', 'push_cue', 'phase_progress']
RIM_WEIGHT = 200.
BODY_WEIGHT = 80.
DENSE_FRACTION = .2


def moving_takeoff(vx):
    return (vx >= .3) & (vx <= 2.)


def height_value(rim, body):
    return RIM_WEIGHT * rim.clamp_min(0.) + BODY_WEIGHT * body.clamp_min(0.)


class HeightAccount:
    def __init__(self, n, device):
        self.rim_peak = torch.zeros(n, device=device)
        self.body_peak = self.rim_peak.clone()
        self.dense_paid = self.rim_peak.clone()
        self.deferred_paid = self.rim_peak.clone()
        self.started = self.rim_peak.bool()
        self.closed = self.started.clone()
        self.settled = self.started.clone()
        self.failed = self.started.clone()
        self.moving = self.started.clone()
        self.takeoffs = torch.zeros(n, device=device, dtype=torch.long)
        self.level_sum = self.rim_peak.clone()
        self.level_samples = self.rim_peak.clone()

    @property
    def flight_quality(self):
        return self.level_sum / self.level_samples.clamp_min(1.)

    def reset(self, ids):
        for value in vars(self).values():
            value[ids] = 0

    def update(self, *, launch, airborne, landed, stable, failed, rim, body, balance, moving):
        first = launch & ~self.started & ~self.closed
        self.started |= first
        self.takeoffs += first.long()
        self.moving[first] = moving[first]
        self.failed |= failed
        collect = self.started & ~self.closed & airborne & ~self.failed
        self.level_sum += balance.clamp(0., 1.) * collect
        self.level_samples += collect
        old_rim, old_body = self.rim_peak.clone(), self.body_peak.clone()
        self.rim_peak.copy_(torch.where(collect, torch.maximum(self.rim_peak, rim.clamp_min(0.)), self.rim_peak))
        self.body_peak.copy_(torch.where(collect, torch.maximum(self.body_peak, body.clamp_min(0.)), self.body_peak))
        dense = DENSE_FRACTION * height_value(self.rim_peak - old_rim, self.body_peak - old_body)
        dense *= balance.clamp(0., 1.) * self.moving
        self.dense_paid += dense
        self.closed |= self.started & landed | self.failed
        complete = stable & self.started & self.closed & ~self.settled & ~self.failed & self.moving
        deferred = (1. - DENSE_FRACTION) * height_value(self.rim_peak, self.body_peak) * complete * self.flight_quality
        self.deferred_paid += deferred
        self.settled |= complete
        return dict(first_takeoff=first, complete=complete, dense=dense, deferred=deferred,
                    reward=dense + deferred + 4. * complete)
