"""Independent correction of the old reader's principal-inertia-frame telemetry."""
from pathlib import Path
import hashlib,json,math,time
import numpy as np,mujoco
from series_sim import SeriesSim,SERIES

D=Path(__file__).resolve().parent
def run():
    dest=D/'CHASSIS_FRAME_SERIES_REVIEW.json'
    if dest.exists():raise RuntimeError('Completed checks are reusable.')
    out=dict(epoch=time.time(),id='local-xbody-reader-repair',original_report_path=str(D/'LOCAL_SMOKE_REVIEW.json'),original_report_sha256=hashlib.sha256((D/'LOCAL_SMOKE_REVIEW.json').read_bytes()).hexdigest(),original_inertial_frame_measurements_retained=True,physics_or_policy_changes=False,trials=[])
    cases=[(f'spin_{label}_{sign:+d}','flat',0.,speed*sign,500) for label,speed in zip(SERIES['spin_labels'],SERIES['spin_rad_s']) for sign in (1,-1)]
    cases += [('straight_positive','flat',1.5,0.,500),('straight_negative','flat',-1.5,0.,500)]
    for id,scene,tv,tw,n in cases:
        s=SeriesSim(scene,'e0');rows=[];v=w=0.;failure=None
        for i in range(n):
            v+=float(np.clip(tv-v,-.008,.008));w+=float(np.clip(tw-w,-.04,.04));s.command.vx=v;s.command.wz=w;s.step_control();h=s.health();vel=s.body_velocity();gyro=s.data.sensor('base_gyro').data
            # Independently measured site gyro must match actual chassis angular velocity.
            assert np.max(np.abs(gyro-vel[:3]))<1e-8
            R=s.data.xmat[s.chassis_id].reshape(3,3);yaw=math.atan2(R[1,0],R[0,0])
            rows.append([s.data.time,*s.base_position,vel[3],vel[2],*gyro,yaw,v,w,h['closure_error_m'],h['mimic_error_rad']])
            if h['upright_cos']<.60 or s.base_position[2]<.12:failure='local fall prefix';break
        raw=np.array(rows);np.savez_compressed(D/(id+'.npz'),trajectory=raw,columns=np.array(['t','x','y','z','body_vx','body_wz','gyro_x','gyro_y','gyro_z','yaw','command_vx','command_wz','closure_m','mimic_rad']))
        tail=raw[-100:];ty=float(tail[:,5].mean());tx=float(tail[:,4].mean())
        r=dict(id=id,model='e0',checkpoint_sha256=s.policy.sha256,target_vx=tv,target_wz=tw,controls=len(raw),tail_mean_body_vx=tx,tail_mean_signed_yaw=ty,correct_signed_direction=bool((tw*ty>0) if tw else (tv*tx>0)),gyro_chassis_frame_exact=True,failure=failure,health=s.health(),raw_path=str(D/(id+'.npz')))
        out['trials'].append(r);(D/(id+'_REVIEW.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
        print(id,round(tx,4),round(ty,4),failure,flush=True)
    out['all_signed_directions_correct']=all(r['correct_signed_direction'] for r in out['trials']);out['all_trials_finite']=all(r['health']['finite'] for r in out['trials']);out['local_falls']=[r['id'] for r in out['trials'] if r['failure']]
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':run()
