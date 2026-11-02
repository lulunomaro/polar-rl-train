"""NEW R16 TRAIN sensor-derived-rate diagnostic, not an archival reread.
Only regex-extract time/gyro/estimated14 arrays; never parse/use qpos_truth,
truth, contact/envelope/DR keys. No physics, grading or H1/H2 input.
Logged time is post-step ROW clock, not an acquisition timestamp: derivative
numbers are apparent arrival-grid variation, never a calibrated noise bound.
"""
from pathlib import Path
import hashlib,json,re
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent
ARRAYS={k:re.compile(r'"'+k+r'"\s*:\s*(\[[^\]]*\])') for k in ('gyro','estimated14')}
TIME=re.compile(r'"time"\s*:\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def percentiles(a):
    return {'absolute_axis_percentiles_50_90_95_99_max':np.percentile(abs(a),[50,90,95,99,100],axis=0).tolist(),'not_pure_measurement_noise_or_verified_bound':True}
def run_diagnostic(max_rows=2000):
    rows=[]
    for case in ['r16_roll_long_0','r16_roll_long_101','r16_roll_long_201']:
        p=TASK/'results'/case/'trace.jsonl'
        if not p.exists():rows.append({'case_id':case,'available':False,'not_reconstructed':True});continue
        t=[];gyro=[];qd=[];rejected=0
        with p.open('r',encoding='utf-8') as f:
            for i,line in enumerate(f):
                if i>=max_rows:break
                try:
                    mt=TIME.search(line);mg=ARRAYS['gyro'].search(line);mx=ARRAYS['estimated14'].search(line)
                    if not all((mt,mg,mx)):raise ValueError('selected fields absent')
                    stamp=float(mt.group(1));w=np.asarray(json.loads(mg.group(1)),float);x=np.asarray(json.loads(mx.group(1)),float)
                    if w.shape!=(3,) or x.shape!=(14,) or not np.isfinite(x).all() or not np.isfinite(w).all() or not np.isfinite(stamp):raise ValueError('shape/finite')
                    t.append(stamp);gyro.append(w);qd.append([x[10],x[10]+x[11],x[12],x[12]+x[13]])
                except (ValueError,TypeError,json.JSONDecodeError):rejected+=1
        t=np.asarray(t);gyro=np.asarray(gyro);qd=np.asarray(qd);dt=np.diff(t);valid=(dt>1e-6)&(dt<.05)
        if len(t)<2 or not valid.any():rows.append({'case_id':case,'usable':False,'reason':'sensor-derived fields insufficient','unknown_not_filled':True});continue
        qdd=np.diff(qd,axis=0)[valid]/dt[valid,None];alpha=np.diff(gyro,axis=0)[valid]/dt[valid,None]
        rows.append({'case_id':case,'source_path':str(p),'source_bytes_stat_only':p.stat().st_size,'rows_selected':len(t),'rejected_rows':rejected,'row_dt_min_median_max_s':[float(dt.min()),float(np.median(dt)),float(dt.max())],'qd4_source':'sensor-derived est14 rates [10,10+11,12,12+13], not raw encoder packet replay','gyro_source':'logged packet.gyro_body','acquisition_timestamp_logged':False,'raw_joint_vel4_logged':False,'qdd_arrival_grid_apparent':percentiles(qdd),'alpha_arrival_grid_apparent':percentiles(alpha),'classification':'UNCERTAIN_ACQUISITION_ALIGNMENT_NOISE_AND_TRUE_MOTION_SEPARATION_UNPROVEN','H1_H2_used':False,'truth_or_contact_fields_extracted':False,'raw_hash_recomputed':False})
    code=[TASK/'run_jump270_roll_v3.py',TASK/'sensor_core_jump_v1.py',TASK/'sensor_core_v4.py']
    return {'purpose':'NEW_SENSOR_DERIVATIVE_RELIABILITY_DIAGNOSTIC_NOT_ARCHIVAL_OR_PHYSICS_RERUN','cases':rows,'source_code_SHA':[{'path':str(p),'SHA':sha(p)} for p in code if p.exists()],'only_extracted_field_allowlist':['time','gyro','estimated14 rates10..13'],'sensor_state_schema':'Lhipdot=10,Lcrankdot=10+11,Rhipdot=12,Rcrankdot=12+13','critical_gap':'R16 logger saved post-control physics time but no packet.time_s or raw4encoder acquisition tuple. Do not replace with qpos_truth or assume acquisition dt=.01.', 'existing_estimator_alpha_lowpass_tau_s':.06,'lowpass_tau_is_existing_source_not_new_tuning':True,'verdict':'No reliable current qdd/alpha calibration is established. Differentiated values include motion/noise/held samples/time alias; missing bounds stay uncertain. Future explicitly timestamped sensor-only packet logging is needed.','No_reconstruction_of_missing_R15_prefix_rows':True,'new_physics_steps':0,'H1_H2_changed':False}
