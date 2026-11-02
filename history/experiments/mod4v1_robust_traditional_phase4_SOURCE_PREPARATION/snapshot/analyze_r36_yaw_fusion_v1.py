"""Zero-physics feasibility diagnostic on R36 TRAIN, never old holdout.
Wheel-differential yaw is conditional rolling kinematics, not independent slip truth.
This offline computation does not change any already-run controller or score.
"""
from pathlib import Path
import json
import math
import statistics
import numpy as np
from physics_bridge import geometry

R = Path(__file__).resolve().parent
D = R/'DATA_DIAGNOSTIC/R36_YAW_FUSION_V1'
D.mkdir(parents=True,exist_ok=False)
chart=geometry()
chart.radius=.0625
weights=(0.,.25,.5,.75,1.)
reports=[]
for seed in range(201,209):
    case=f'r36b_heading_k2_{seed}'
    pred={w:dict(yaw=0.,y=0.,last_vy=0.,last_w=0.)for w in weights}
    integrated_gyro=0.
    last_stamp=None
    errors={w:[]for w in weights}
    rate_errors=[]
    view_errors=[]
    max_rate_delta=0.
    true0=None
    samples=[]
    unique=0
    with (R/'results'/case/'trace.jsonl').open('r',encoding='utf-8')as f:
        for line in f:
            row=json.loads(line)
            stamp=row['sensor_timestamp_s']
            truth=row['ground_truth_before']
            if true0 is None:
                true0=truth['yaw_true']
            if last_stamp is not None and stamp<=last_stamp+1e-10:
                continue
            dt=0. if last_stamp is None else stamp-last_stamp
            last_stamp=stamp
            unique+=1
            omega=np.asarray(row['raw_gyro'],float)
            omega_no_z=omega.copy()
            omega_no_z[2]=0.
            q=row['encoder4']
            qd=row['encoder_rate4']
            spin=row['wheel_rate2']
            data=[chart.wheel_kinematics(q[2*j],q[2*j+1],qd[2*j],qd[2*j+1],spin[j],omega_no_z,side)for j,side in enumerate(('left','right'))]
            track=data[0][1][1]-data[1][1][1]
            assert track>0.
            encoder_wz=(data[1][0]-data[0][0])/track
            roll=row['estimated_roll']
            pitch=row['estimated14'][2]
            conversion=max(math.cos(pitch),.15)
            wg=(omega[1]*math.sin(roll)+omega[2]*math.cos(roll))/conversion
            we=(omega[1]*math.sin(roll)+encoder_wz*math.cos(roll))/conversion
            max_rate_delta=max(max_rate_delta,abs(we-wg))
            true_heading=truth['yaw_true']-true0
            true_rate=(truth['gyro_true'][1]*math.sin(truth['roll_true'])+truth['gyro_true'][2]*math.cos(truth['roll_true']))/max(math.cos(truth['pitch_true']),.15)
            rate_errors.append((wg-true_rate,we-true_rate))
            view_errors.append(row['estimated14'][1]-true_heading)
            for w,p in pred.items():
                rate=(1.-w)*wg+w*we
                p['yaw']+=rate*dt
                vy=row['estimated14'][7]*math.sin(p['yaw'])
                p['y']+=.5*dt*(p['last_vy']+vy)
                p['last_vy']=vy
                errors[w].append(p['yaw']-true_heading)
            if abs(row['time']-12.)<.0001:
                samples.append(dict(true_y_m=row['root_xy_current_m'][1],true_relative_yaw_rad=true_heading,V4_estimated_yaw_rad=row['estimated14'][1]))
    arr=np.asarray(rate_errors)
    rp=json.loads((R/'results'/case/'result.json').read_bytes())
    reports.append(dict(case=case,unique_packets=unique,rate_RMS_gyro_rad_s=float(np.sqrt(np.mean(arr[:,0]**2))),rate_RMS_encoder_rad_s=float(np.sqrt(np.mean(arr[:,1]**2))),max_abs_wheel_minus_gyro_rad_s=max_rate_delta,V4_final_yaw_error_rad=view_errors[-1],V4_yaw_error_RMS_rad=float(np.sqrt(np.mean(np.square(view_errors)))),weight_results={str(w):dict(final_yaw_error_rad=errors[w][-1],yaw_error_RMS_rad=float(np.sqrt(np.mean(np.square(errors[w])))),deadreckoned_y_m=pred[w]['y'])for w in weights},last=samples,source_trace_producer_SHA=rp['trace_artifact']['SHA']))
summary={str(w):dict(median_yaw_RMS_rad=statistics.median(r['weight_results'][str(w)]['yaw_error_RMS_rad']for r in reports),worst_abs_final_yaw_error_rad=max(abs(r['weight_results'][str(w)]['final_yaw_error_rad'])for r in reports))for w in weights}
sigma=.125/math.sqrt(3.)
output=dict(kind='R36_TRAIN_OFFLINE_YAW_FUSION_FEASIBILITY_NOT_CONTROLLER_OR_HOLDOUT',physics_steps=0,weights_predeclared=list(weights),rolling_radius_m=.0625,support_rolling_assumption_not_validated=True,no_true_state_in_predictors=True,truth_only_for_residual_grading=True,simple_gyro_noise_scaling=dict(gyro_uniform_half_rad_s=.125,sigma_rad_s=sigma,post_mean_noise=True,dt_s=.01,constant_speed_m_s=2.,duration_s=10.,small_angle_sigma_y_m=2.*sigma*math.sqrt(.01*10.**3/3.),interpretation='Illustrative gyro-only white-noise integration, not a universal bound or measured reliability'),summary=summary,cases=reports)
with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(output,f,indent=2,allow_nan=False)
print(json.dumps(dict(summary=summary,cases=[dict(case=r['case'],V4_final_yaw_error_rad=r['V4_final_yaw_error_rad'],rate_RMS_gyro_rad_s=r['rate_RMS_gyro_rad_s'],rate_RMS_encoder_rad_s=r['rate_RMS_encoder_rad_s'],last=r['last'],weight_results=r['weight_results'])for r in reports],simple_gyro_scaling=output['simple_gyro_noise_scaling']),indent=2))
