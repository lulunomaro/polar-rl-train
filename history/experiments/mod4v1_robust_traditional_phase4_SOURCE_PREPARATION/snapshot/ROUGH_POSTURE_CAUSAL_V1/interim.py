"""Urgent offline R22 TRAIN event table, public FK at sparse selected rows.
No physics/mesh rebuild/Git; rawtrace read ONLY for new causal analysis, not SHA.
"""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent;sys.path.insert(0,str(TASK))
from CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel
CASES=[f'r22_height{d}bar{h}' for d in (0,20,40) for h in (40,60)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cv(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:cv(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [cv(v) for v in x]
    return x

def main():
    assert not (R/'INTERIM.json').exists();model=NominalModel();source=[];cases=[];nominal=[]
    index=json.loads((TASK/'TALL_ROUGH_BANK_V1/INDEX.json').read_text(encoding='utf-8'))
    for n in index['rows']:
        q=np.array([n['q'][3],n['q'][3]+n['q'][4],n['q'][5],n['q'][5]+n['q'][6]]);p=model.fk(q);w=p['wheel_B'];nominal.append({'delta':n['delta'],'q4':q.tolist(),'wheel_center_B2':w.tolist(),'planar_leg_length2_m':np.linalg.norm(w[:,[0,2]],axis=1).tolist(),'vertical_drop2_m':(-w[:,2]).tolist(),'upright_root_height_wheel_on_level_m':float(np.mean(-w[:,2])+.06369999796152115)})
    for case in CASES:
        base=TASK/'results'/case;cfg=json.loads((base/'config.json').read_text(encoding='utf-8'));result=json.loads((base/'result.json').read_text(encoding='utf-8'));gain=json.loads((TASK/cfg['gain_file']).read_text(encoding='utf-8'))['gain'];tq=np.array([gain['q'][3],gain['q'][3]+gain['q'][4],gain['q'][5],gain['q'][5]+gain['q'][6]])
        source += [{'path':str(p),'SHA':sha(p),'bytes':p.stat().st_size} for p in (base/'config.json',base/'result.json',TASK/cfg['gain_file'])]
        rows=[]
        with (base/'trace.jsonl').open('r',encoding='utf-8') as f:
            for line in f:rows.append(json.loads(line))
        assert len(rows)==result['controls']
        nw=[i for i,x in enumerate(rows) if x['physics_nonwheel_contact_ticks']>0];first=nw[0] if nw else None
        rail=[i for i,x in enumerate(rows) if np.any(np.abs(np.asarray(x['actual_tau'])[[2,5]])>=5.775909774436091-1e-6)]
        legrail=[i for i,x in enumerate(rows) if np.any(np.abs(np.asarray(x['actual_tau'])[[0,1,3,4]])>=40.-1e-6)]
        track=[i for i,x in enumerate(rows) if max(abs(np.asarray(x['encoder4'])-tq))>.05]
        pitch=[i for i,x in enumerate(rows) if abs(x['ground_truth']['pitch_true'])>math.radians(10)]
        def snap(i):
            if i is None:return None
            x=rows[i];gt=x['ground_truth'];before=x['ground_truth_before'];enc=np.asarray(x['encoder4']);est=np.asarray(x['estimated14']);p=model.fk(enc,check_limits=False);sym=np.asarray(before['state']);symq=np.array([sym[2],sym[2]+sym[3],sym[2],sym[2]+sym[3]]);sp=model.fk(symq,check_limits=False)
            return {'row':i,'sensor_time_s':x['sensor_timestamp_s'],'pre_grade_time_s':x['estimate_time'],'post_grade_time_s':x['time'],'nonwheel_bin_interval_s':[x['estimate_time'],x['time']],'root_height_before_after_m':[before['xyz'][2],gt['xyz'][2]],'pitch_before_after_deg':np.rad2deg([before['pitch_true'],gt['pitch_true']]).tolist(),'roll_post_deg':math.degrees(gt['roll_true']),'xyz_post_m':gt['xyz'],'true_forward_velocity_m_s':gt['body_velocity'][0],'request_shaped':{'request':x['request'],'shaped':x['shaped']},'target_q4':tq.tolist(),'encoder_q4':enc.tolist(),'encoder_target_error4_rad':(enc-tq).tolist(),'est_q4':[est[3],est[3]+est[4],est[5],est[5]+est[6]],'stored_truth_symmetric_hip_delta_before_rad':sym[2:4].tolist(),'truth_sym_FK_vertical_drop2_m':(-sp['wheel_B'][:,2]).tolist(),'encoder_FK_leg_length2_m':np.linalg.norm(p['wheel_B'][:,[0,2]],axis=1).tolist(),'encoder_FK_vertical_drop2_m':(-p['wheel_B'][:,2]).tolist(),'wheel_rate2_mean_rad_s':x['wheel_rate2'],'actual_tau_endstep6_Nm':x['actual_tau'],'requested_tau6_Nm':x['raw_requested_tau'],'physics_nonwheel_pair_point_ticks_in_control':x['physics_nonwheel_contact_ticks'],'cache_time_s':gt.get('collision_site_cache_time_s'),'2k_peak_or_named_identity':'not_saved_here_unknown'}
        pre=None if first is None else max(0,first-1);steady=None if first is None else max(0,first-25)
        cases.append({'case':case,'delta_target':gain['q'][4],'bar_height_m':result['scene']['original_parameters']['bar_height_range'][0]+.04*cfg['terrain_difficulty'],'source_trace_producer_reference':result['trace_artifact'],'trace_not_rehashed':True,'nominal_target':next(n for n in nominal if abs(n['delta']-gain['q'][4])<1e-9),'original_result':{'complete':result['complete'],'stop':result['stop_reason'],'duration_actual_s':result['duration_actual_s'],'rough_progress_m':result['rough_progress_m'],'max_pitch_abs_rad':result['max_pitch_abs'],'max_roll_abs_rad':result['max_roll_abs'],'max_actual_tau6':result['max_actual_tau6']},'first_nonwheel_control_bin':snap(first),'last_contactfree_preceding_bin':snap(pre),'quarter_second_before_nonwheel':snap(steady),'final':snap(len(rows)-1),'event_times_s':{'first_nonwheel_bin_end':None if first is None else rows[first]['time'],'first_endstep_wheel_torque_rail':None if not rail else rows[rail[0]]['time'],'first_endstep_leg_torque_rail':None if not legrail else rows[legrail[0]]['time'],'first_encoder_target_error_gt_0p05rad_ANALYSIS_ONLY':None if not track else rows[track[0]]['time'],'first_pitch_gt10deg_ANALYSIS_ONLY':None if not pitch else rows[pitch[0]]['time']},'all_raw_diagnostic_not_new_acceptance':True})
    obj={'status':'INTERIM_EXISTING_R22_TRAIN_CAUSAL_EVENTS_NOT_FINAL_SEAL','nominal_geometry':nominal,'cases':cases,'source_small_files':source,'physics_steps':0,'truth_used_only_offline_grading':True,'time_resolution':'100Hz rows; interval20physicalsteps, no2kidentity reconstruction; sensor/pregrade at t and postgrade at t+.01 separated','no_new_Git_or_assets_hash':True}
    (R/'INTERIM.json').write_text(json.dumps(cv(obj),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=[]
    for c in cases:
        pre=c['last_contactfree_preceding_bin'];n=c['first_nonwheel_control_bin'];f=c['final']
        def text(x):return '-' if x is None else f"{x['post_grade_time_s']:.3f}:z{x['root_height_before_after_m'][1]:.3f},p{x['pitch_before_after_deg'][1]:.1f},err{max(abs(a) for a in x['encoder_target_error4_rad']):.3f},w{max(abs(a) for a in x['wheel_rate2_mean_rad_s']):.1f},tw{max(abs(x['actual_tau_endstep6_Nm'][i]) for i in (2,5)):.2f}"
        lines.append({'case':c['case'],'target_root_height_m':c['nominal_target']['upright_root_height_wheel_on_level_m'],'pre_contact':text(pre),'first_nonwheel':text(n),'final':text(f),'stop':c['original_result']['stop'],'events':c['event_times_s']})
    print(json.dumps({'nominal_geometry':nominal,'minimum_event_table':lines},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
