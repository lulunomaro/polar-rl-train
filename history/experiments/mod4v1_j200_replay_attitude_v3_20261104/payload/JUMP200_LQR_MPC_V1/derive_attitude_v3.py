"""One reference-continuity mechanism, reusing coord_soft accel/jerk; no gain tuning/grid."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;s=(D/'run_capture_v2.py').read_text(encoding='utf-8')
# Both existing ground controllers get the SAME already-existing coord_soft shaper.
a='dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,roll_kp=float(c.get(\'ground_roll_kp\',20.)),roll_kd=2.)'
b="dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,roll_kp=float(c.get('ground_roll_kp',20.)),roll_kd=2.,accel=float(c['reference_accel_m_s2']),jerk=float(c['reference_jerk_m_s3']))"
assert s.count(a)==2;s=s.replace(a,b)
a='if land_start is None:land_start=t;land.ref[0]=x[0]+.15*x[7];est.vb[0]=x[7];est.distance=x[0];landing_q0=np.asarray(actualq,float).copy()'
b=a+';land.shaper.v=float(x[7]);land.shaper.a=0.;land.ref[7]=float(x[7])'
assert s.count(a)==1;s=s.replace(a,b)
# Actual body velocity is private scoring only; record it, never consume it in control.
a='ground_MPC_phase=phase in('
b="body_velocity_truth_post=last['body_velocity'],sensor_vref=float((ctrl if phase=='approach'else land).ref[7]),ground_MPC_phase=phase in("
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace('JUMP200_CAPTURE_V2_EXISTING_MINIHOP_SCHEDULE_GROUND_ONLY_MPC_NOT_AERIAL_MPC','JUMP200_ATTITUDE_V3_CONTINUOUS_SPEED_REFERENCE_SAME_K_SPEED_TARGET_GROUND_ONLY_MPC')
with(D/'run_attitude_v3.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
c=json.loads((D/'capture_v2_001.json').read_bytes());c.update(kind='J200_ATTITUDE_V3_SINGLE_EXISTING_REFERENCE_CONTINUITY_MECHANISM',seed=200003,duration_s=10.,start_x=-2.5,launch_distance_m=2.0,reference_accel_m_s2=.6,reference_jerk_m_s3=2.,speed=1.4,planned_takeoff_world_x_m=-.5,mechanism='existing coord_soft accel.6/jerk2, landing shaper seeded measured incomingvx notzero; K/step/push/air/capture/limits unchanged; longer same-speed runup preserves takeofflocation',RMS_comparison='publish durations and phase-specific RMS;10s vs8s wholeRMS not equal-duration proof',takeoff_speed_must_not_be_hidden_lower=True)
with(D/'attitude_v3_001.json').open('x',encoding='utf-8')as f:json.dump(c,f,indent=2)
print('ATTITUDE_V3_NEW_SOURCE_AND_CONFIG_READY; no physics in derivation')
