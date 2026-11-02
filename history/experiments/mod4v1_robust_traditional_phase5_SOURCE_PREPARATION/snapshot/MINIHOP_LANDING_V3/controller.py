"""TRAIN-only capture reference/gain schedule; not a landing-contact detector.
Two independently nominal ground equilibria, with precomputed gains, are
interpolated during timed capture. No online DARE, plant truth, or DR access.
Convex interpolation of gains is a hypothesis, not a stability certificate.
"""
import math
import numpy as np
from ground_controller_v4 import GroundController
from MINIHOP_OBSERVER_V2.controller import MiniHop as V2

class MiniHop(V2):
    def __init__(self,start_gain,end_gain,geometry,config,landing_gain):
        super().__init__(start_gain,end_gain,geometry,config)
        self.landing_enable=self.c.get('landing_transition_enable',False)
        assert type(self.landing_enable)is bool
        self.landing_seconds=float(self.c.get('landing_transition_s',.20))
        assert math.isfinite(self.landing_seconds)and .10<=self.landing_seconds<=1.
        other=GroundController(landing_gain,dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,roll_kp=20.,roll_kd=2.))
        assert self.ctrl.predict==0. and other.predict==0.
        self.K0=self.ctrl.K.copy();self.K1=other.K.copy()
        self.ff0=self.ctrl.tau_eq.copy();self.ff1=other.tau_eq.copy()
        self.eq0=self.ctrl.eq.copy();self.eq1=other.eq.copy()
        self.capture_started_s=None;self.landing_weight=0.

    def command(self,e,packet,now,attitude_q,forward=0.):
        capture=bool(self.landing_enable and self.enabled and self.launched and not self.fault
                     and math.isfinite(float(now))and now-self.trigger>=self.push+self.air)
        if capture:
            if self.capture_started_s is None:self.capture_started_s=float(now)
            u=float(np.clip((now-self.capture_started_s)/self.landing_seconds,0.,1.))
            s=3*u*u-2*u*u*u;self.landing_weight=s
            if u>0.:
                if u>=1.:
                    self.ctrl.K=self.K1.copy();self.ctrl.tau_eq=self.ff1.copy();self.ctrl.eq=self.eq1.copy()
                else:
                    self.ctrl.K=(1-s)*self.K0+s*self.K1
                    self.ctrl.tau_eq=(1-s)*self.ff0+s*self.ff1
                    self.ctrl.eq=(1-s)*self.eq0+s*self.eq1
                self.ctrl.ref[3:7]=self.ctrl.eq[3:7]
                # Existing fixed-leg PD uses zero velocity reference; do not
                # pretend the trajectory derivative is a tracked feed-forward.
        tau=super().command(e,packet,now,attitude_q,forward)
        r=self.ctrl.ref
        self.log.update(landing_transition_enabled=bool(self.landing_enable),landing_transition_weight=float(self.landing_weight),
                        landing_position_ref4=[float(r[3]),float(r[3]+r[4]),float(r[5]),float(r[5]+r[6])],
                        landing_velocity_ref_used4=[0.,0.,0.,0.],landing_detector_used=False,
                        landing_gain_schedule_is_experimental=True,landing_capture_started_s=self.capture_started_s)
        return tau
