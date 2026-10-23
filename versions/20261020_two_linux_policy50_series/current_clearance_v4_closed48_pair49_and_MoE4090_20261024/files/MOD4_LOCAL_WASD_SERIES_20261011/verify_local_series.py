"""Local nominal physics checks only; no trained-expert graduation is inferred."""
from pathlib import Path
import json,math,time,traceback
import numpy as np,mujoco
from series_sim import SeriesSim,SERIES
from io_runtime import write_json

D=Path(__file__).resolve().parent
def run():
    if (D/'LOCAL_SMOKE_REVIEW.json').exists():raise RuntimeError('Use completed checks; do not repeat.')
    result=dict(epoch=time.time(),protocol='local MuJoCo nominal 0.5ms /100Hz direct frozen Torch actor',production_mutations=0,training_mutations=0,budget_mutations=0,expert_qualification=False,scene_checks=[],trials=[])
    for sc in SERIES['scenes']:
        s=SeriesSim(sc['id'],'terrain' if sc['id']!='flat' else 'e0');r=s.parameter_readback()
        for _ in range(20):s.step_control()
        h=s.health();assert h['finite']
        result['scene_checks'].append(dict(scene=sc['id'],initial_parameter_readback=r,controls=20,health=h))
    cases=[('e0_stand','flat','e0',False,0,0,300),('e0_spin_pos4pi','flat','e0',False,0,4*math.pi,800),('e0_spin_neg4pi','flat','e0',False,0,-4*math.pi,800),('e0_forward','flat','e0',False,1.5,0,500),('e0_reverse','flat','e0',False,-1.5,0,500),('terrain_wave35_forward','wave35','terrain',False,.3,0,1500),('terrain_wave35_reverse','wave35','terrain',True,.3,0,1500),('terrain_curb20_up','curb20','terrain',False,.3,0,800),('terrain_curb20_down','curb20','terrain',True,.3,0,800),('wave_candidate_stand','flat','wave_candidate',False,0,0,300)]
    for id,scene,model,reverse,tv,tw,n in cases:
        s=SeriesSim(scene,model,reverse);v=w=0.;rows=[];failure=None;start=s.base_position.copy()
        for i in range(n):
            v+=float(np.clip(tv-v,-.008,.008));w+=float(np.clip(tw-w,-.04,.04));s.command.vx=v;s.command.wz=w;s.step_control()
            vel=np.zeros(6);mujoco.mj_objectVelocity(s.model,s.data,mujoco.mjtObj.mjOBJ_BODY,s.chassis_id,vel,1);h=s.health()
            rows.append([s.data.time,*s.base_position,v,w,vel[3],vel[2],h['upright_cos'],h['closure_error_m'],h['mimic_error_rad']])
            if h['upright_cos']<.60 or s.base_position[2]<.12:failure='local fall prefix';break
        raw=np.array(rows);path=D/(id+'.npz');np.savez_compressed(path,trajectory=raw,columns=np.array(['time','x','y','z','command_vx','command_wz','actual_body_vx','actual_body_wz','upright_cos','closure_m','mimic_rad']))
        tail=raw[-min(200,len(raw)):]
        trial=dict(id=id,scene=scene,model=model,checkpoint_sha256=s.policy.sha256,reverse=reverse,requested_controls=n,actual_controls=len(raw),target_vx=tv,target_wz=tw,failure=failure,valid_prefix_preserved=True,start_xyz=start.tolist(),end_xyz=s.base_position.tolist(),tail_mean_body_vx=float(tail[:,6].mean()),tail_mean_signed_yaw=float(tail[:,7].mean()),health=s.health(),raw_path=str(path))
        result['trials'].append(trial);(D/(id+'_REVIEW.json')).write_text(json.dumps(trial,ensure_ascii=False,indent=2),encoding='utf8')
        print(id,len(raw),'vx',round(trial['tail_mean_body_vx'],4),'yaw',round(trial['tail_mean_signed_yaw'],4),'failure',failure,flush=True)
    # Render the actual new robot and full wave road as an inspectable artifact.
    from PIL import Image
    s=SeriesSim('wave35','terrain');renderer=mujoco.Renderer(s.model,height=720,width=1080)
    cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=(0,0,.1);cam.distance=7.;cam.azimuth=100;cam.elevation=-38
    renderer.update_scene(s.data,camera=cam);Image.fromarray(renderer.render()).save(D/'LOCAL_WAVE_PREVIEW.png');renderer.close()
    result['all_scene_loads_finite']=all(x['health']['finite'] for x in result['scene_checks'])
    result['all_trials_finite']=all(x['health']['finite'] for x in result['trials'])
    result['local_failures']=[t['id'] for t in result['trials'] if t['failure']]
    write_json(D/'LOCAL_SMOKE_REVIEW.json',result,required=True)
    print('Checks complete. Local falls:',result['local_failures'],flush=True)

if __name__=='__main__':
    try:run()
    except Exception:
        (D/'LOCAL_SMOKE_ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise
