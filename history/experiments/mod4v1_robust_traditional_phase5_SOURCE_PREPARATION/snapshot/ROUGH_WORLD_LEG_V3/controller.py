"""Latched stop capture: preserve V1 driving prefix, alter only after stop.
V2 fixed tail posture but changed startup, introducing contacts/lateral failure.
This isolates the stop intervention; no old gate/physics/profile is overwritten.
"""
import math
import numpy as np
from ROUGH_WORLD_LEG_V1.controller import WorldLegController as V1

class WorldLegController(V1):
    def __init__(self,gain,config=None):
        super().__init__(gain,config)
        self.nominal_world_k=self.world_k;self.seen_drive=False;self.stop_capture=False
        self.capture_speed=float((config or{}).get('world_full_activation_m_s',.4))
        assert math.isfinite(self.capture_speed)and self.capture_speed>0.
    def command(self,estimate,forward,yaw_rate):
        if abs(forward)>1e-9:self.seen_drive=True;self.stop_capture=False
        elif self.seen_drive:self.stop_capture=True
        shaped=float(self.shaper.v)
        activation=float(np.clip(abs(shaped)/self.capture_speed,0.,1.))if self.stop_capture else 1.
        self.world_k=self.nominal_world_k*activation
        try:tau=super().command(estimate,forward,yaw_rate)
        finally:self.world_k=self.nominal_world_k
        self.world_log.update(speed_activation=activation,previous_shaped_v_m_s=shaped,
                              stop_capture=bool(self.stop_capture),seen_drive=bool(self.seen_drive),
                              effective_world_k=self.nominal_world_k*activation,
                              policy='v1_prefix_unchanged_then_shaped_stop_capture')
        return tau
