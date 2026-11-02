"""Speed-scheduled fore/aft reference, NEW TRAIN, not a changed gate.
R40 cleared4cm without nonwheel contact but failed tail pitch; nominal observer
pitch error was only .004rad. Restore original body-fixed stance as shaped
speed returns to zero instead of retaining terrain counter-rotation at rest.
"""
import math
import numpy as np
from ROUGH_WORLD_LEG_V1.controller import WorldLegController as V1

class WorldLegController(V1):
    def __init__(self,gain,config=None):
        super().__init__(gain,config)
        self.nominal_world_k=self.world_k
        self.capture_speed=float((config or{}).get('world_full_activation_m_s',.4))
        assert math.isfinite(self.capture_speed)and self.capture_speed>0
    def command(self,estimate,forward,yaw_rate):
        previous_shaped=float(self.shaper.v)
        activation=float(np.clip(abs(previous_shaped)/self.capture_speed,0.,1.))
        self.world_k=self.nominal_world_k*activation
        try:tau=super().command(estimate,forward,yaw_rate)
        finally:self.world_k=self.nominal_world_k
        self.world_log.update(speed_activation=activation,previous_shaped_v_m_s=previous_shaped,
                              nominal_world_k=self.nominal_world_k,effective_world_k=self.nominal_world_k*activation,
                              policy='return_to_original_body_fixed_stance_at_shaped_stop')
        return tau
