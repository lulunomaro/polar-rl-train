"""R38 NEW INFORMATION shadow capture, not a new control/holdout benchmark.
Six fresh TRAIN episodes, at most four physics workers. No C worker dependency.
Original D1-aftermean/D3 and 100Hz P25+heading2 control remain unchanged.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import time
R=Path(__file__).resolve().parent
D=R/'batches/r38_raw2k_shadow6'
D.mkdir(parents=True,exist_ok=False)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
with(D/'ADMISSION.log').open('xb')as f:
    rc=subprocess.run([sys.executable,'-B',str(R/'RAW2K_SHADOW_V1/admission.py')],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
if rc:raise RuntimeError('zero-physics raw2k admission failed; physical jobs not started')
jobs=[dict(case='r38_raw2k_nom_stand',seed=0,nominal=True,mode='stand',duration=2.),dict(case='r38_raw2k_nom_forward',seed=0,nominal=True,mode='forward',duration=6.)]+[dict(case=f'r38_raw2k_DR_{s}',seed=s,nominal=False,mode='forward',duration=6.)for s in range(4211,4215)]
protocol=dict(kind='R38_NEW_INFORMATION_CORRELATED_RAW2K_SHADOW_ONLY',cases=jobs,not_H1_H2_H4_or_hardware=True,no_new_control_inputs=True,consumer='future COM/window diagnostic, not online actuation',sensor_noise='original 100Hz post-mean draw shared across all noisy 2k samples of the selected source window',D3='whole window follows authoritative returned packet source epoch; repeated boot reuses payload',within_window_noise_differences_cancel_is_extra_information=True,mean_roundoff_not_bitidentity=True,physics_dt_s=.0005,control_dt_s=.01,kinematic_radius_m=.0625,actual_tire_mesh_unchanged=True,full_D0_D7=True,max_physics_workers=4,source=[])
for name in (Path(__file__).name,'run_raw2k_shadow_case_v1.py','physics_bridge_raw2k_v1.py','physics_bridge_raw2k_grade_v1.py','RAW2K_SHADOW_V1/publisher.py','RAW2K_SHADOW_V1/BRIDGE_PRECHECK.json','RAW2K_SHADOW_V1/admission001/RESULT.json'):
    raw=(R/name).read_bytes();protocol['source'].append(dict(path=str(R/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
controller=dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052,heading_hold_k=2.,heading_correction_cap=.8)
def run(job):
    case=job['case'];cfg=dict(case_id=case,seed=job['seed'],nominal=job['nominal'],mode=job['mode'],duration_s=job['duration'],command_at_s=1.,forward_m_s=2.,controller=controller,kinematic_radius_m=.0625,feedback='sensors',upright_arming_prior=True,accel_reference='wheel_midpoint')
    cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
    with(D/(case+'.log')).open('xb')as f:
        rc=subprocess.run([sys.executable,'-B',str(R/'run_raw2k_shadow_case_v1.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
    rp=R/'results'/case/'result.json';result=json.loads(rp.read_bytes())if rp.exists()else{}
    row=dict(case=case,seed=job['seed'],nominal=job['nominal'],returncode=rc,start=start,end=time.time(),complete=result.get('complete'),base_gate=result.get('proposed_gate_passed'),controls=result.get('controls'),physics_steps=result.get('physics_callbacks'),shadow=result.get('raw2k_shadow_artifact'),publisher=result.get('raw2k_private_validation'),original_trace=result.get('trace_artifact'),tail_v=result.get('tail_velocity_mean_m_s'),v_RMS=result.get('tail_v_tracking_RMSE'))
    print(json.dumps(row),flush=True);return row
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
    # Nominal software/mean checks before consuming any DR physical case.
    for chunk in (jobs[:2],jobs[2:]):
        found=list(pool.map(run,chunk));rows.extend(found)
        if any(r['returncode']for r in found):
            unstarted=[j for j in jobs if j['case']not in{r['case']for r in rows}]
            (D/'SOFTWARE_ABORT.json').write_text(json.dumps(dict(rows=rows,unstarted=unstarted),indent=2),encoding='utf-8')
            raise RuntimeError('raw2k fresh-case software abort; no same-purpose replay')
(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind=protocol['kind'],rows=rows,physics_steps=sum(r['physics_steps']for r in rows),shadow_frames=sum(r['shadow']['frames']for r in rows),not_new_control_qualification=True),indent=2),encoding='utf-8')
print('RAW2K_SHADOW_BATCH_COMPLETE',len(rows),flush=True)
