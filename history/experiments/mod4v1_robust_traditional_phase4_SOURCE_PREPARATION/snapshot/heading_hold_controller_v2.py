"""R36: only native-bool log serialization repair; same control equations."""
"""NewTRAINstraight-headingcascade, sensor-only, notfrozenH1/H4/H2.
InnerPIratealonehasdisturbance-dependentheadingoffset. OuterP ofrelativeheading
letsitsrateintegralholdtorquebiaswithoutrequiringangleoffset. No worldXYinput.
"""
import numpy as np
from sensor_core_v4 import wrap
from ground_controller_v4 import GroundController as Base


class GroundController(Base):
    def __init__(self, gain, config=None):
        config = config or {}
        super().__init__(gain, config)
        self.heading_k = float(config.get('heading_hold_k', 2.))
        self.heading_correction_cap = float(config.get('heading_correction_cap', .8))
        if not np.isfinite([self.heading_k, self.heading_correction_cap]).all() or not 0 <= self.heading_k <= 10. or not 0 <= self.heading_correction_cap <= 2.:
            raise ValueError('finite bounded heading settings required')
        self.heading_target = None
        self.heading_log = {}

    def command(self, estimate, forward, yaw_rate):
        x = estimate.state14
        if not np.isfinite(x).all() or not np.isfinite(estimate.sensor_age_s) or estimate.sensor_age_s < 0 or estimate.sensor_age_s > .05:
            self.heading_log = dict(active=False, reason='invalid_estimate')
            self.valid_command = False
            return np.zeros(6)
        if self.heading_target is None:
            self.heading_target = float(x[1])
        # Operator turning/highspin is not qualified by thisstraight-lineprototype.
        active = bool(abs(yaw_rate) < 1e-6 and abs(x[8]) < 2.)
        if not active:
            self.heading_target = float(x[1])
        error = wrap(self.heading_target - float(x[1]))
        correction = float(np.clip(self.heading_k * error, -self.heading_correction_cap,
                                   self.heading_correction_cap)) if active else 0.
        tau = super().command(estimate, forward, yaw_rate + correction)
        self.heading_log = dict(target_relative_yaw=self.heading_target, yaw_error=error,
                                correction_rad_s=correction, active=active,
                                world_position_used=False)
        return tau
