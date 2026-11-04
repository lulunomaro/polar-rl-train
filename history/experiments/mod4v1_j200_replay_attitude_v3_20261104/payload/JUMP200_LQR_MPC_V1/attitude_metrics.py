"""Bounded current J200 control-trace attitude reduction; truth grading only, never control."""
from pathlib import Path
import math,json

def reduce_trace(path,maximum_frames=800):
    groups={k:[]for k in('all','jump','approach','push','air','landing')};count=0;previous=None
    with Path(path).open(encoding='utf-8')as f:
        for line in f:
            r=json.loads(line);count+=1
            if count>maximum_frames:raise ValueError('current J200 trace exceeds declared frame cap')
            t=r['truth'];p=float(t['pitch_true']);roll=float(t['roll_true']);w=[float(x)for x in t['gyro_true']]
            if not all(math.isfinite(x)for x in[p,roll,*w]):raise ValueError('nonfinite attitude diagnostic')
            cp=math.cos(p)
            rollrate=w[0]+math.tan(p)*(math.sin(roll)*w[1]+math.cos(roll)*w[2])if abs(cp)>1e-6 else None
            pitchrate=math.cos(roll)*w[1]-math.sin(roll)*w[2]
            x=dict(time_post_s=r['time'],command_time_s=r['time']-.01,phase=r['phase'],pitch_rad=p,roll_rad=roll,body_omega_rad_s=w,rollrate_rad_s=rollrate,pitchrate_rad_s=pitchrate,estimated14=r['estimated14'],requested6=r['requested_tau'],last_substep_ctrl6=r['actual_tau'],root_post_xyz=t['xyz'],body_velocity_post=t['body_velocity'],vref=r.get('sensor_vref'))
            x['matched_truth_at_command']=dict(time_post_s=previous['time_post_s'],body_velocity_post=previous['body_velocity_post'],root_post_xyz=previous['root_post_xyz'],pitch_rad=previous['pitch_rad'],roll_rad=previous['roll_rad'])if previous is not None and abs(previous['time_post_s']-x['command_time_s'])<1e-7 else None
            previous=x
            groups['all'].append(x);phase=r['phase']
            key='approach'if phase=='approach'else'push'if phase=='push_off'else'air'if phase.startswith('flight_')else'landing'
            groups[key].append(x)
            if key!='approach':groups['jump'].append(x)
    def stats(a):
        if not a:return dict(frames=0)
        z=dict(frames=len(a),duration_s=len(a)*.01,first_snapshot=a[0],last_snapshot=a[-1])
        for k in('pitch_rad','roll_rad','rollrate_rad_s','pitchrate_rad_s'):
            vals=[q[k]for q in a if q[k]is not None];peak=max(a,key=lambda q:abs(q[k])if q[k]is not None else-1)
            z[k]=dict(peak_abs=max(abs(v)for v in vals),rms=math.sqrt(math.fsum(v*v for v in vals)/len(vals)),undefined_frames=len(a)-len(vals),peak_time_post_s=peak['time_post_s'],peak_phase=peak['phase'])if vals else None
        for i,k in enumerate(('body_rollrate','body_pitchrate','body_yawrate')):
            vals=[q['body_omega_rad_s'][i]for q in a];z[k]=dict(peak_abs=max(abs(v)for v in vals),rms=math.sqrt(math.fsum(v*v for v in vals)/len(vals)))
        z['pitch_peak_snapshot']=max(a,key=lambda q:abs(q['pitch_rad']));z['roll_peak_snapshot']=max(a,key=lambda q:abs(q['roll_rad']))
        return z
    return dict(trace=str(path),control_frames=count,groups={k:stats(v)for k,v in groups.items()},root_pose_epoch='current qpos/qvel at POST control',estimated14_epoch='original control-start view; held-rate source semantics unchanged',phase_epoch='command held during the20physics samples producing this POST',raw_payload_rehashed=False)

if __name__=='__main__':
    D=Path(__file__).resolve().parent
    paths=[D/'runs/j200_nominal_baseline_200001_attempt002/trace.jsonl',D/'runs/j200_capture_v2_nominal_200002/trace.jsonl']
    out=[reduce_trace(p)for p in paths]
    with(D/'ATTITUDE_OLD_TWO_ONCE.json').open('x',encoding='utf-8')as f:json.dump(out,f,indent=2,allow_nan=False)
    for x in out:
        print(json.dumps(dict(case=x['trace'],groups={k:{s:v[s]for s in('frames','pitch_rad','roll_rad','body_rollrate','body_pitchrate')if s in v}for k,v in x['groups'].items()})))
