"""T01 candidate 2: retain C1 leg leveling and restore an operator-heading outer loop.

The 3/s gain and +/-1.5 rad/s bound are reused from player.py:294, not new tuning.
Zero commanded yaw rate now holds the captured heading instead of allowing drift.
No simulator imports, truth/contact inputs, DR knowledge or motor-limit changes.
"""
import numpy as np
from sensor_core_v4 import wrap
from controller_roll_v2 import GroundController as C1

VARIANT = 'coord_soft_MOD4v2_fresh_LQR_heading'


class GroundController(C1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = VARIANT
        self.intent_heading = None
        self.control_diagnostic = {}

    def command(self, e, forward, yaw_rate):
        if self.intent_heading is None:
            self.intent_heading = float(e.state14[1])
        self.intent_heading += float(yaw_rate)*self.dt
        heading_error = wrap(self.intent_heading-float(e.state14[1]))
        corrected_w = float(np.clip(float(yaw_rate)+3.*heading_error, -1.5, 1.5))
        old_w, old_i = self.old_shaped_w, self.yaw_integral
        tau = super().command(e, forward, corrected_w)
        if not self.valid_command:
            return tau
        x = np.asarray(e.state14, float)
        error = x-self.ref
        error[1] = error[8] = 0.
        for a, b in ((3,5),(4,6),(10,12),(11,13)):
            error[a] = error[b] = .5*(error[a]+error[b])
        error[2] *= self.wheel_pitch_scale
        error[9] *= self.wheel_pitch_scale
        error[7] *= self.wheel_velocity_scale
        pieces = {}
        for name, indices in (('position',[0]), ('velocity',[7]), ('pitch_rate',[2,9]),
                              ('legs',[3,4,5,6,10,11,12,13])):
            z = np.zeros(14); z[indices] = error[indices]
            pieces[name] = float(np.mean((-self.K@z)[[2,5]]))
        self.control_diagnostic = dict(intent_heading_rad=self.intent_heading,
            heading_error_rad=heading_error, raw_command=[float(forward),float(yaw_rate)],
            corrected_yaw_rate_rad_s=corrected_w, active_ref14=self.ref.copy(),
            park_error_m=self.park_error, shaped_v_m_s=self.shaper.v,
            shaped_w_rad_s=self.shaper.w, shaped_a_m_s2=self.shaper.a,
            yaw_integral=self.yaw_integral,
            yaw_desired_torque_Nm=self.yaw_kp*(self.ref[8]-x[8])+self.yaw_ki*float(np.clip(
                old_i+(self.ref[8]-x[8])*self.dt,-self.yaw_integral_limit,self.yaw_integral_limit))
                +self.yaw_rate_ff*self.ref[8]+self.yaw_ff*(self.ref[8]-old_w)/self.dt,
            wheel_lqr_common_contributions_Nm=pieces,
            wheel_common_requested_Nm=float(np.mean(tau[[2,5]])),
            wheel_differential_requested_Nm=float(.5*(tau[5]-tau[2])),
            roll_follow=dict(self.follow_diag), control_truth_inputs=False)
        return tau
