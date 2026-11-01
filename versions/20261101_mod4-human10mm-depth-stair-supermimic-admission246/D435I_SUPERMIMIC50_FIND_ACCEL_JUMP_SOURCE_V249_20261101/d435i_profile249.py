"""Front-chassis-fixed D435i calibration contract; no hardware/camera opened here."""
import numpy as np
MODEL='RealSense D435i'
MOUNT='fixed to front of ownMOD4 chassis, user confirmed'
NOMINAL_FAMILY_DEPTH_FOV_DEGREES=(87.,58.)
OFFICIAL_SOURCE='https://www.realsenseai.com/product-family/430-series/'
def calibrated_packet(z16,*,depth_scale_m,K,T_heading_optical,sensor_time_in_control_clock,control_time):
    a=np.asarray(z16);K=np.asarray(K,dtype=np.float32);T=np.asarray(T_heading_optical,dtype=np.float32)
    if a.ndim!=2 or a.dtype!=np.uint16 or not(0<float(depth_scale_m)<.1):raise ValueError('ActualZ16 and measured depth-scale required')
    if K.shape!=(3,3)or T.shape!=(4,4)or not np.isfinite(K).all()or not np.isfinite(T).all():raise ValueError('Actual active-stream intrinsics and fixed-mount plus IMU transform required')
    if sensor_time_in_control_clock>control_time:raise ValueError('Map hardware timestamps to control clock first')
    depth=a.astype(np.float32)*np.float32(depth_scale_m);depth[a==0]=np.nan
    return dict(depth_m=depth,K=K,T_heading_optical=T,sensor_time=sensor_time_in_control_clock,control_time=control_time,source='calibrated D435i Z-depth;no terrain map',nominal_FOV_is_not_device_calibration=True)
