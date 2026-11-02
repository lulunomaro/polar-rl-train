"""New TRAIN hypothesis: smooth flight leg retraction, no contact/plant inputs.
Inherited V3 approach/push/capture and all guards are unchanged. Leg PD still
uses zero velocity reference; this is not trajectory-derivative feed-forward.
"""
import math
import numpy as np
from MINIHOP_LANDING_V3.controller import MiniHop as V3

class MiniHop(V3):
    def __init__(self,start_gain,end_gain,geometry,config,landing_gain):
        super().__init__(start_gain,end_gain,geometry,config,landing_gain)
        self.smooth_air=self.c.get('smooth_air_retraction_enable',False)
        assert type(self.smooth_air)is bool
        self.retract_time=float(self.c.get('air_retraction_s',.16))
        assert math.isfinite(self.retract_time)and .08<=self.retract_time<=.25 and self.retract_time<self.air
    def command(self,e,packet,now,attitude_q,forward=0.):
        t=float(now);since=t-self.trigger
        active=bool(self.smooth_air and self.enabled and self.launched and not self.fault and math.isfinite(t)
                    and self.push<=since<self.push+self.air)
        weight=None
        if active:
            u=float(np.clip((since-self.push)/self.retract_time,0.,1.))
            weight=10*u**3-15*u**4+6*u**5
            original=self.q_start
            target=self.q_end.copy()if u<=0. else(original.copy()if u>=1. else(1-weight)*self.q_end+weight*original)
            self.q_start=target
            try:tau=super().command(e,packet,now,attitude_q,forward)
            finally:self.q_start=original
        else:tau=super().command(e,packet,now,attitude_q,forward)
        self.log.update(smooth_air_retraction_enabled=bool(self.smooth_air),smooth_air_retraction_active=active,
                        air_retraction_weight=weight,air_retraction_time_s=self.retract_time,
                        air_velocity_ref_used4=[0.,0.,0.,0.],guards_unchanged=True)
        return tau
