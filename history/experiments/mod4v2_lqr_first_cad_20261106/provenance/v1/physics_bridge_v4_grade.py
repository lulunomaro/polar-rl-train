"""Gradecurrentfreejointpose/velocitywithoutstage-stalebodyxmat.
This module is simulator/grading ONLY. It is never an estimator input.
Collision/contact/cachedwheelxyz still refer to last dynamicsstage; labelthem.
"""
import math
import numpy as np
from physics_bridge_v3 import BufferedImuPlant as PreviousPlant
from sensor_core_v4 import rotation
class BufferedImuPlant(PreviousPlant):
 def grade(self):
  h=self.health();R=rotation(self.d.qpos[3:7]);omega=self.d.qvel[3:6].copy();vb=R.T@self.d.qvel[:3];h['upright_cos']=float(R[2,2]);return dict(**h,body_velocity=vb.tolist(),gyro_true=omega.tolist(),yaw_true=math.atan2(R[1,0],R[0,0]),pitch_true=math.atan2(-R[2,0],math.hypot(R[0,0],R[1,0])),roll_true=math.atan2(R[2,1],R[2,2]),root_pose_velocity_time_s=float(self.d.time),collision_site_cache_time_s=max(0.,float(self.d.time)-self.dt),grading_frame='currentfreejointqposqvel; collision/sitecacheexplicitlystaged')
