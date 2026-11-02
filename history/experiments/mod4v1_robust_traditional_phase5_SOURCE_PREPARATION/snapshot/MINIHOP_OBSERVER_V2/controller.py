"""New TRAIN: delay rolling-wheel observations without changing phase timing.
R44's timer could re-enable wheel odometry before observed landing. This is a
manual-timer quarantine hypothesis, NOT a new contact/air confidence signal.
"""
import math
from MINIHOP_V1.controller import MiniHop as V1

class MiniHop(V1):
    def __init__(self,start_gain,end_gain,geometry,config):
        super().__init__(start_gain,end_gain,geometry,config)
        self.quarantine=float(self.c.get('observer_quarantine_after_push_s',self.air))
        assert math.isfinite(self.quarantine)and self.air<=self.quarantine<=1.
        self.quarantine_active=False
    def prepare_estimator(self,estimator,now):
        super().prepare_estimator(estimator,now)
        self.quarantine_active=bool(self.enabled and self.trigger+self.push<=now<self.trigger+self.push+self.quarantine)
        if self.quarantine_active:
            estimator.wheel_measurement_enabled=False
            estimator.ground_kinematic_constraint_enabled=False
        # Keep the original gyro/gravity correction schedule unchanged.
    def command(self,e,packet,now,attitude_q,forward=0.):
        tau=super().command(e,packet,now,attitude_q,forward)
        self.log.update(wheel_measurement_disabled_predicted=bool(self.quarantine_active),
            observer_quarantine_until_s=self.trigger+self.push+self.quarantine,
            observer_quarantine_is_timer_not_contact=True,original_torque_phase_timing_unchanged=True)
        return tau
