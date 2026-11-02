"""NEW TRAIN counterfactual: IMU pitch -> shared hip/crank fore-aft reference.
Keeps existing height gain, delta, plant, wheel control and all physical limits.
No world pose, terrain, DR or contact input; not a proven world-height controller.
"""
import math
import numpy as np
from ground_controller_v4 import GroundController as Previous

class WorldLegController(Previous):
    def __init__(self,gain,config=None):
        super().__init__(gain,config);c=config or{}
        self.world_k=float(c.get('world_pitch_gain',0.))
        self.world_limit=float(c.get('world_pitch_limit_rad',.30))
        self.world_rate=float(c.get('world_pitch_rate_rad_s',2.))
        assert 0.<=self.world_k<=1. and 0.<self.world_limit<=.35 and 0.<self.world_rate<=3.
        self.shift=0.;self.world_log={}
    def command(self,estimate,forward,yaw_rate):
        x=estimate.state14
        if not np.isfinite(x).all()or estimate.sensor_age_s>.05:
            self.world_log=dict(valid=False,reason='existing_input_gate')
            return super().command(estimate,forward,yaw_rate)
        desired=float(np.clip(-self.world_k*float(x[2]),-self.world_limit,self.world_limit))
        self.shift+=float(np.clip(desired-self.shift,-self.world_rate*self.dt,self.world_rate*self.dt))
        desired_hip=np.asarray(self.eq[[3,5]])+self.shift
        # Actual USD hip range is +/-0.5; use an explicit 20mrad reference margin.
        target_hip=np.clip(desired_hip,-.48,.48)
        self.ref[[3,5]]=target_hip
        self.ref[[4,6]]=self.eq[[4,6]] # crank-minus-hip delta is preserved
        # No target-speed feedforward addition or new force/torque cancellation.
        self.world_log=dict(valid=True,pitch_input_rad=float(x[2]),shift_desired_rad=desired,shift_applied_rad=float(self.shift),
                            target_hip2_rad=target_hip.tolist(),delta2_rad=self.ref[[4,6]].tolist(),
                            hip_reference_clipped=bool(np.any(target_hip!=desired_hip)),
                            claim='body reference counter-rotation, not observed world clearance')
        return super().command(estimate,forward,yaw_rate)
