"""ONE fresh native component check, no old trajectory/physics/holdout reads."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
import json,math,subprocess,sys,time
from types import SimpleNamespace
import numpy as np
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import physics_bridge as bridge
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController as C2
from RM_ROBUSTNESS_V1.controller_roll_follow_v1 import GroundController as C1
OUT=HERE/'validation001'
TOL=dict(reference_state4_rad=5e-4,delta_rad=5e-4,raw_height_m=2e-6,filtered_height_m=2e-6,
         heading_error_rad=2e-6,corrected_yaw_rad_s=2e-6,common_absolute_q_rad=2e-7,
         delta_slew_rad_per_call=.0080001)

def main():
    OUT.mkdir(exist_ok=False)
    protocol=dict(id='C2REF_NATIVE_COMPONENT_MATH_001',physics_steps=0,old_cases_read=0,
        scope='Reference-generation slice only; no full torque controller/estimator/BSP/HIL qualification',
        fixed_dt=.01,ctk_fd_epsilon=.001,python_fd_epsilon='existing public geometry default',
        sequences=[['center',1,100],['changing',1,600],['height_clip',1,180],['fps_no_outer_loop',0,200]],
        acceptance=TOL,require_same_inverse_acceptance=True,require_common_q_and_slew=True,
        fault_checks_expected=16,full_T01_acceptance=False)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    result=dict(protocol_id=protocol['id'],passed=False,physics_steps=0,old_cases_read=0)
    try:
        gain=bridge.load_gain(ROOT/'nominal_gain_v1.json')
        pack=json.loads((ROOT/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_bytes())
        geometry=bridge.geometry();q0=np.asarray([gain['q'][3],gain['q'][3]+gain['q'][4]],np.float32).astype(float)
        rows=[];expected=[];previous_delta=None
        for name,mode,count in protocol['sequences']:
            cls=C2 if mode else C1
            py=cls(gain,pack['controller'],geometry=geometry);py.K=np.asarray(pack['K_6x14'])
            py.q0=q0.copy();previous_delta=None
            for i in range(count):
                t=i*.01;x=np.zeros(14);x[1]=3.+.8*t;x[0]=.1*t;x[7]=.2*math.sin(t);x[8]=.8
                motion=name in ('changing','fps_no_outer_loop')
                hip=.06*math.sin(2*t) if motion else 0.;crank=.04*math.cos(2*t) if motion else 0.
                qL=q0+np.array([hip,crank]);qR=q0-np.array([hip,crank])
                x[3],x[4],x[5],x[6]=qL[0],qL[1]-qL[0],qR[0],qR[1]-qR[0]
                if motion:
                    dh=.12*math.cos(2*t);dc=-.08*math.sin(2*t)
                    x[10],x[11],x[12],x[13]=dh,dc-dh,-dh,dh-dc
                pitch=.1*math.sin(.7*t) if motion else 0.
                roll=.2*math.sin(1.3*t) if motion else 0.
                if name=='height_clip':roll=.6*min(1.,i/30.,(count-i)/30.)
                x[2]=pitch
                yaw=(.8 if t<2. else (0. if t<4. else -.8)) if mode else 1.8*math.sin(2*t)
                if name=='center':x[1]=0.;yaw=0.
                omega=np.array([.1*math.cos(t),.1*math.sin(t),.2])
                values=np.asarray([*x,roll,*omega,yaw,.01,0.],np.float32).astype(float)
                e=SimpleNamespace(state14=np.asarray(values[:14]),roll=values[14],
                                  omega_body=np.asarray(values[15:18]),sensor_age_s=0.)
                py.command(e,.3,values[18])
                raw=py.follow_diag['max_abs_raw_wheel_center_height_difference_m']
                # Latest raw value is recomputed from original public FK, not its running maximum.
                left,_=py._fk(np.array([e.state14[3],e.state14[3]+e.state14[4]]),'left')
                right,_=py._fk(np.array([e.state14[5],e.state14[5]+e.state14[6]]),'right')
                n=np.array([-math.sin(e.state14[2]),math.sin(e.roll)*math.cos(e.state14[2]),math.cos(e.roll)*math.cos(e.state14[2])])
                error=math.atan2(math.sin(py.intent_heading-e.state14[1]),math.cos(py.intent_heading-e.state14[1])) if mode else 0.
                corrected=float(np.clip(values[18]+3.*error,-1.5,1.5)) if mode else values[18]
                expected.append(dict(ref4=py.ref[[3,4,5,6]].copy(),delta2=py.delta.copy(),raw=float(n@(left-right)),
                    height=py.height_difference,heading_error=error,yaw=corrected,
                    accepted=int(py.follow_diag['inverse_holds']==0 if i==0 else py.follow_diag['inverse_holds']==last_holds),
                    q0=q0.copy(),reset=i==0,mode=mode))
                last_holds=py.follow_diag['inverse_holds']
                rows.append(f'{int(i==0)} {mode} '+' '.join(format(v,'.9g') for v in values)+' 1\n')
        data=OUT/'new_synthetic_input.txt';data.write_text(' '.join(format(v,'.9g') for v in q0)+'\n'+''.join(rows),encoding='ascii')
        gcc='C:/MinGW/bin/gcc.exe';exe=OUT/'pc2_native_check.exe'
        command=[gcc,'-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math',str(HERE/'pc2_reference.c'),
                 str(HERE/'host_check.c'),str(ROOT/'SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c'),'-lm','-o',str(exe)]
        result['compile_command']=command
        compiled=subprocess.run(command,capture_output=True,text=True)
        (OUT/'compile.stdout.log').write_text(compiled.stdout,encoding='utf8');(OUT/'compile.stderr.log').write_text(compiled.stderr,encoding='utf8')
        result['compile_exit']=compiled.returncode
        if compiled.returncode:raise RuntimeError('Native compile failed; preserve this attempt')
        output=OUT/'native_output.jsonl';started=time.perf_counter()
        native=subprocess.run([str(exe),str(data),str(output)],capture_output=True,text=True)
        result['native_wall_seconds']=time.perf_counter()-started;result['native_exit']=native.returncode
        (OUT/'native.stdout.log').write_text(native.stdout,encoding='utf8');(OUT/'native.stderr.log').write_text(native.stderr,encoding='utf8')
        if native.returncode:raise RuntimeError('Native run failed; preserve this attempt')
        native_rows=[json.loads(line) for line in output.read_text(encoding='utf8').splitlines()]
        if len(native_rows)!=len(expected):raise AssertionError('Row count mismatch')
        maxima=dict(reference_state4_rad=0.,delta_rad=0.,raw_height_m=0.,filtered_height_m=0.,heading_error_rad=0.,corrected_yaw_rad_s=0.,common_absolute_q_rad=0.,delta_slew_rad_per_call=0.)
        mismatches=[];last_delta=np.zeros(2)
        for a,b in zip(native_rows,expected):
            if b['reset']:last_delta=np.zeros(2)
            if a['status']!=0 or a['valid']!=1 or a['accepted']!=b['accepted']:mismatches.append(a['i'])
            for key,left,right in [('reference_state4_rad',a['ref4'],b['ref4']),('delta_rad',a['delta2'],b['delta2']),
                ('raw_height_m',a['raw'],b['raw']),('filtered_height_m',a['height'],b['height']),
                ('heading_error_rad',a['heading_error'],b['heading_error']),('corrected_yaw_rad_s',a['yaw'],b['yaw'])]:
                maxima[key]=max(maxima[key],float(np.max(np.abs(np.asarray(left)-right))))
            r=a['ref4'];common=np.array([.5*(r[0]+r[2]),.5*(r[0]+r[1]+r[2]+r[3])])
            maxima['common_absolute_q_rad']=max(maxima['common_absolute_q_rad'],float(np.max(np.abs(common-b['q0']))))
            maxima['delta_slew_rad_per_call']=max(maxima['delta_slew_rad_per_call'],float(np.max(np.abs(np.asarray(a['delta2'])-last_delta))))
            last_delta=np.asarray(a['delta2'])
        result.update(rows=len(expected),max_error_or_rate=maxima,status_or_inverse_mismatch_rows=mismatches,
            thresholds=TOL,native_summary=native.stdout.strip(),component_only=True,full_T01_acceptance=False)
        result['passed']=not mismatches and all(maxima[k]<=TOL[k] for k in TOL)
        if not result['passed']:raise AssertionError('Predeclared component tolerance/contract failed')
    except BaseException as exc:
        result['error']=repr(exc)
        (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');raise
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
