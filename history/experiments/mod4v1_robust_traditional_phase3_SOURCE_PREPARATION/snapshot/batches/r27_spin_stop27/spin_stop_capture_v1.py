"""Newsensor-onlyTRAINprofile: originalH2spin pluslow-rateP25capture/blend.
Noenv/truth/CAN. CapturesanESTIMATEDreferenceonly, notphysicalpose/state reset.
"""
import numpy as np
from spin_center_torque_v2 import GroundController as Spin
from ground_controller_v4 import GroundController as Normal


class GroundController(Spin):
    def __init__(self, gain, config=None):
        config = config or {}
        super().__init__(gain, config)
        normal = dict(config, position_weight=25., position_leash=1.)
        self.capture = Normal(gain, normal)
        self.capture_enabled = bool(config.get('stop_capture', False))
        self.capture_state = False
        self.low_ticks = 0
        self.mix = 0.

    def command(self, estimate, forward, yaw_rate):
        spin_tau = super().command(estimate, forward, yaw_rate)
        x = estimate.state14
        low = abs(yaw_rate) < 1e-6 and abs(forward) < 1e-6 and abs(self.ref[8]) < 2. and abs(x[8]) < 2.
        self.low_ticks = self.low_ticks + 1 if low else 0
        enabled = self.capture_enabled and self.low_ticks >= 10
        if enabled and not self.capture_state:
            self.capture.ref[:] = self.ref
            self.capture.ref[0] = x[0]
            self.capture.shaper.v = self.shaper.v
            self.capture.shaper.w = self.shaper.w
            self.capture.shaper.a = self.shaper.a
            self.capture.yaw_integral = self.yaw_integral
            self.capture.old_shaped_w = self.old_shaped_w
            self.capture.previous[:] = self.previous
        self.capture_state = enabled
        self.mix = float(np.clip(self.mix + (.05 if enabled else -.05), 0., 1.))
        capture_tau = self.capture.command(estimate, forward, yaw_rate) if self.mix > 0. else spin_tau
        tau = (1. - self.mix) * spin_tau + self.mix * capture_tau
        self.center_log['stop_capture_mix'] = self.mix
        self.center_log['stop_capture_reference'] = float(self.capture.ref[0])
        self.center_log['root_pose_reset'] = False
        self.previous[:] = tau
        return tau
