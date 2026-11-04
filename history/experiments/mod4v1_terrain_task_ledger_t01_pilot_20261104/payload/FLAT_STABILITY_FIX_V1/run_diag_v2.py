"""New TRAIN diagnostics only. Actual full MuJoCo; truth logged, never feedback."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse, csv, json, math, time, traceback
import numpy as np
from physics_bridge import ROOT, FullDR, load_gain, geometry
from physics_bridge_v3 import BufferedImuPlant
from sensor_core_v4 import StateEstimator, rpy, rotation
from FLAT_STABILITY_FIX_V1.controller_v2 import GroundController


def request(t):
    if 5 <= t < 12: return 1.,0.
    if 20 <= t < 27: return -1.,0.
    if 35 <= t < 42: return 1.,1.5
    if 47 <= t < 54: return 2.,0.
    return 0.,0.


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--variant',required=True,choices=['coord','coord_soft','body_soft','body_priority'])
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    out=args.out.resolve()
    assert out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter()
    rows=[]
    plant=None
    try:
        pack=json.loads((ROOT/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_bytes())
        gain=load_gain(ROOT/'nominal_gain_v1.json')
        plant=BufferedImuPlant(False,(.03,0.,.04))
        plant.attach_dr(FullDR(0,nominal=True))
        plant.reset(gain['symmetric'],0.)
        estimator=StateEstimator(geometry(),plant.imu_offset,accel_correction=1.5,
            wheel_std=.065,accel_reference='wheel_midpoint',innovation_limit=1.,upright_prior=True)
        controller=GroundController(gain,pack['controller'],variant=args.variant)
        controller.K=np.asarray(pack['K_6x14'],float)
        names=['pre_s','post_s','request_v','request_w','ref_v','ref_w','ref_x','est_x',
            'est_v','true_v','est_pitch','true_pitch','true_roll','root_z','gyro_y',
            'est_pitchdot','wheel_l','wheel_r','tau_req_lw','tau_req_rw',
            'tau_act_lw','tau_act_rw','q_lhip','q_lcrank','q_rhip','q_rcrank',
            'qd_lhip','qd_lcrank','qd_rhip','qd_rcrank','proper_x','proper_z',
            'slip_innovation','park_error','tau_act_lhip','tau_act_lcrank','tau_act_rhip','tau_act_rcrank']
        complete=True
        with (out/'signals.csv').open('x',newline='',encoding='utf-8') as f:
            writer=csv.writer(f);writer.writerow(names)
            for k in range(7000):
                t=float(plant.d.time)
                pkt=plant.sensor_packet();e=estimator.update(pkt)
                # PRE-step root values are diagnostic only, time-aligned to e.
                truth_rpy=rpy(plant.d.qpos[3:7])
                true_v=float((rotation(plant.d.qpos[3:7]).T@plant.d.qvel[:3])[0])
                true_z=float(plant.d.qpos[2])
                v,w=request(t)
                tau=controller.command(e,v,w)
                plant.apply_torque_request(tau,pkt)
                a=plant.d.ctrl.copy()
                row=[t,float(plant.d.time),v,w,*controller.ref[[7,8,0]],*e.state14[[0,7]],
                    true_v,e.state14[2],truth_rpy[1],truth_rpy[0],true_z,pkt.gyro_body[1],
                    e.state14[9],*pkt.wheel_vel2,*tau[[2,5]],*a[[2,5]],
                    *pkt.joint_pos4,*pkt.joint_vel4,pkt.accel_proper_body[0],
                    pkt.accel_proper_body[2],e.slip_innovation,controller.park_error,*a[[0,1,3,4]]]
                assert len(row)==len(names)
                rows.append(row);writer.writerow(row)
                if k%1000==999:
                    f.flush();print(f'{args.variant} sim_t={plant.d.time:.2f}',flush=True)
                if not np.isfinite(plant.d.qpos).all() or abs(truth_rpy[1])>1.1 or abs(truth_rpy[0])>.85:
                    complete=False;break
        arr=np.asarray(rows,float)
        col={n:i for i,n in enumerate(names)}
        def metrics(lo,hi):
            s=arr[(arr[:,0]>=lo-1e-8)&(arr[:,0]<hi-1e-8)]
            if len(s)==0:return {'samples':0}
            p=s[:,col['true_pitch']];ep=s[:,col['est_pitch']]-p
            vs=s[:,col['true_v']]; vr=s[:,col['ref_v']]
            h=s[:,col['root_z']]
            centered=p-p.mean()
            spectrum=np.abs(np.fft.rfft(centered))
            frequency=np.fft.rfftfreq(len(p),.01)
            fi=int(np.argmax(spectrum[1:])+1) if len(spectrum)>1 else 0
            return dict(samples=len(s),pitch_mean_deg=float(np.rad2deg(p.mean())),
                pitch_std_deg=float(np.rad2deg(p.std())),pitch_p2p_deg=float(np.rad2deg(np.ptp(p))),
                pitch_maxabs_deg=float(np.rad2deg(np.abs(p).max())),
                pitch_dominant_Hz=float(frequency[fi]),est_pitch_RMSE_deg=float(np.rad2deg(np.sqrt(np.mean(ep*ep)))),
                roll_maxabs_deg=float(np.rad2deg(np.abs(s[:,col['true_roll']]).max())),
                body_height_p2p_mm=float(1000*np.ptp(h)),velocity_mean=float(vs.mean()),
                velocity_tracking_RMSE=float(np.sqrt(np.mean((vs-vr)**2))),
                est_velocity_RMSE=float(np.sqrt(np.mean((s[:,col['est_v']]-vs)**2))),
                wheel_actual_torque_std_Nm=float(s[:,[col['tau_act_lw'],col['tau_act_rw']]].std(axis=0).mean()))
        result=dict(variant=args.variant,complete=complete,controls=len(rows),physics_steps=plant.tick_phys,
            actual_duration_s=float(plant.d.time),wall_s=time.perf_counter()-started,
            controller_feedback='sensor_estimate_only',truth_used_for_control=False,nominal=True,
            plant_dt_s=plant.dt,control_dt_s=.01,model_unchanged=True,original_PD_DC_path=True,
            initialization='supported upright diagnostic, NOT autonomous startup qualification',
            actuator_last_sample_epoch='post_s - 0.0005',
            all=metrics(0,70),initial_rest=metrics(2,5),forward1=metrics(8,12),
            reverse1=metrics(23,27),turn=metrics(39,42),forward2=metrics(50,54),
            final_rest=metrics(60,70))
        (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
        print(json.dumps(result,indent=2),flush=True)
    except BaseException:
        (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise


if __name__=='__main__':main()
