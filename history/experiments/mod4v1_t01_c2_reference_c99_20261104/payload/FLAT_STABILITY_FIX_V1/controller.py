"""Fresh flat-ground diagnostic variants, not changes to sealed H controllers.
Mechanism comparison: SPR uses near-stop x integration and wheel+leg balancing.
All numeric K, trim, actuator bounds and plant remain MOD4v1's own frozen P25.
"""
import time
import numpy as np
from ground_controller_v4 import GroundController as OriginalController


class GroundController(OriginalController):
    def __init__(self, gain, config=None, variant='park_body'):
        cfg = dict(config or {})
        self.variant = variant
        self.park_error = 0.0
        super().__init__(gain, cfg)

    def command(self, estimate, forward, yaw_rate):
        if self.variant == 'baseline':
            return super().command(estimate, forward, yaw_rate)
        started = time.perf_counter_ns()
        x = estimate.state14.copy()
        if estimate.sensor_age_s > .05 or not np.isfinite(x).all():
            self.valid_command = False
            return np.zeros(6)
        v, w = self.shaper.update(float(forward), float(yaw_rate), self.dt)
        maxwheel = .9*55.3557*.06369999796152115
        envelope = abs(v)+.4376/2*abs(w)
        if envelope > maxwheel:
            v *= maxwheel/envelope
            w *= maxwheel/envelope
            self.envelope_clips += 1
        self.ref[1] = float(np.clip(self.ref[1]+w*self.dt, x[1]-self.heading_leash, x[1]+self.heading_leash))
        self.ref[7], self.ref[8] = v, w
        # SPR near-stop position term: no accumulated travel debt while driving.
        if abs(forward) < .05 and abs(v) < .05 and abs(x[7]) <= .1 and abs(w) < .2:
            self.park_error = float(np.clip(self.park_error+x[7]*self.dt, -self.position_leash, self.position_leash))
        else:
            self.park_error = 0.0
        self.ref[0] = x[0]-self.park_error
        error = x-self.ref
        error[1] = error[8] = 0.0
        # Preserve left/right roll independence; only sagittal K gets symmetric
        # states. No direct transfer of the source robot's K or geometry.
        for a, b in ((3, 5), (4, 6), (10, 12), (11, 13)):
            error[a] = error[b] = .5*(error[a]+error[b])
        weighted = error.copy()
        weighted[2] *= self.wheel_pitch_scale
        weighted[9] *= self.wheel_pitch_scale
        weighted[7] *= self.wheel_velocity_scale
        tau = self.tau_eq-self.K@weighted
        q = np.array([x[3], x[3]+x[4], x[5], x[5]+x[6]])
        qr = np.array([self.ref[3], self.ref[3]+self.ref[4], self.ref[5], self.ref[5]+self.ref[6]])
        qd = np.array([x[10], x[10]+x[11], x[12], x[12]+x[13]])
        leg = [0, 1, 3, 4]
        if self.variant != 'park_fullsym':
            tau[leg] = self.tau_eq[leg]+self.leg_kp*(qr-q)-self.leg_kd*qd
            if self.variant == 'park_body':
                body_error = np.zeros(14)
                body_error[[0, 2, 7, 9]] = weighted[[0, 2, 7, 9]]
                balance = -self.K@body_error
                # Common sagittal leg feedback coexists with the old bounded
                # pose PID; do not introduce the full asymmetric yaw leg loop.
                tau[[0, 3]] += .5*(balance[0]+balance[3])
                tau[[1, 4]] += .5*(balance[1]+balance[4])
        yaw_error = w-x[8]
        candidate = float(np.clip(self.yaw_integral+yaw_error*self.dt,
                                  -self.yaw_integral_limit, self.yaw_integral_limit))
        common = float(np.mean(tau[[2, 5]]))
        available = max(0., 5.775909774436091-abs(common))
        desired = self.yaw_kp*yaw_error+self.yaw_ki*candidate+self.yaw_rate_ff*w+self.yaw_ff*(w-self.old_shaped_w)/self.dt
        diff = float(np.clip(desired, -available, available))
        if abs(desired) <= available:
            self.yaw_integral = candidate
        tau[2], tau[5] = common-diff, common+diff
        self.old_shaped_w = w
        roll = float(np.clip(-self.roll_kp*estimate.roll-self.roll_kd*estimate.omega_body[0], -8., 8.))
        tau[1] += roll
        tau[0] -= roll
        tau[4] -= roll
        tau[3] += roll
        tau = np.clip(tau, -self.effort, self.effort)
        self.previous = tau.copy()
        self.max_solve_ms = max(self.max_solve_ms, (time.perf_counter_ns()-started)*1e-6)
        return tau
