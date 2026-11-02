"""Zero-step real-model boot admission for the NEW shadow publisher.
No old episode replay; mj_step is forbidden during this admission.
"""
from pathlib import Path
import hashlib
import json
import sys
import traceback
import numpy as np
import mujoco
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R))
from physics_bridge_raw2k_grade_v1 import BufferedImuPlant
from physics_bridge import FullDR,load_gain,geometry
from sensor_core_v4 import StateEstimator
from heading_hold_controller_v2 import GroundController
from RAW2K_SHADOW_V1.publisher import validate_projection
D=Path(__file__).resolve().parent/'admission001'
D.mkdir(parents=True,exist_ok=False)
original=mujoco.mj_step
calls=0
def forbid(*a,**k):
    global calls
    calls+=1
    raise AssertionError('physics stepping forbidden during raw2k admission')
mujoco.mj_step=forbid
try:
    g=load_gain(R/'nominal_gain_v1.json')
    plant=BufferedImuPlant(False)
    plant.attach_dr(FullDR(0,nominal=True))
    plant.reset(g['symmetric'],0.)
    packet=plant.sensor_packet()
    frame=plant.raw2k_shadow_frame
    assert validate_projection(frame)
    assert frame['source_epoch_us']==0 and frame['count']==1 and frame['mean_mode']==0
    for k in ('gyro_body','accel_proper_body','joint_vel4','wheel_vel2'):
        assert np.array_equal(np.asarray(frame['mean'][k]),getattr(packet,k))
    chart=geometry();chart.radius=.0625
    observer=StateEstimator(chart,plant.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.)
    controller=GroundController(g,dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052,heading_hold_k=2.,heading_correction_cap=.8))
    estimate=observer.update(packet)
    tau=controller.command(estimate,0.,0.)
    assert np.isfinite(tau).all()and tau.shape==(6,)
    json.dumps(dict(frame=frame,controller_log=controller.heading_log,tau=tau.tolist()),allow_nan=False)
    assert plant.tick_phys==0 and calls==0
    sources=[]
    for p in (Path(__file__),R/'physics_bridge_raw2k_v1.py',R/'physics_bridge_raw2k_grade_v1.py',R/'RAW2K_SHADOW_V1/publisher.py',R/'run_raw2k_shadow_case_v1.py'):
        raw=p.read_bytes();sources.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    result=dict(kind='REAL_MODEL_BOOT_ADMISSION_ONLY_NO_PHYSICS',physics_steps=0,mj_step_attempts=0,boot_packet_mean_exact=True,sensor_projection_allowlist=True,controller_consumes_original_100Hz_packet_only=True,raw2k_actuation_used=False,finite_nominal_P25_heading2_command=True,sources=sources)
    with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
except BaseException:
    with(D/'ERROR.txt').open('x',encoding='utf-8')as f:f.write(traceback.format_exc())
    raise
finally:mujoco.mj_step=original
