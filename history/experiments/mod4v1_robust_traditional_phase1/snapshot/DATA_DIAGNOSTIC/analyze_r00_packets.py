"""Read-only R00 packet/trace diagnosis. Pure recorded-data arithmetic; no MuJoCo.
Replay frozen estimator math on existing packets is NOT a new physical experiment.
Truth aligned to sensor_timestamp_s, never same-row post-actuation grade.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, traceback
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
SNAP=ROOT/'source_snapshots/r00'
CASES=['r00_forward_nominal_sensors','r00_spin_nominal_sensors']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def stats(a):
    a=np.asarray(a,float)
    if not a.size:return None
    return {'mean':np.mean(a,axis=0).tolist(),'rms':np.sqrt(np.mean(a*a,axis=0)).tolist(),'min':np.min(a,axis=0).tolist(),'max':np.max(a,axis=0).tolist()}
def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def main():
    assert not (OUT/'PACKET_DIAGNOSTIC.json').exists(),'Preserve previous attempt'
    spec=importlib.util.spec_from_file_location('r00_sensor_frozen_readonly',SNAP/'sensor_core.py');sc=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=sc;spec.loader.exec_module(sc)
    pins=json.loads((ROOT.parent/'traditional_control_20261101/reports/model_manifest.json').read_text(encoding='utf-8'))['neutral_skeleton_xz_m']
    geom=sc.LinkageGeometry(pins,radius=.06369999796152115)
    gain=json.loads((ROOT/'nominal_gain_v1.json').read_text(encoding='utf-8'))['gain']
    initial_rpy=np.array([0.,float(gain['q'][2]),float(gain['q'][1])]);initial_R=Rotation.from_euler('xyz',initial_rpy).as_matrix()
    sources=[meta(SNAP/'sensor_core.py'),meta(SNAP/'physics_bridge.py'),meta(SNAP/'run_ground_case.py'),meta(SNAP/'ground_controller.py'),meta(ROOT/'nominal_gain_v1.json')]
    output={};summaries={}
    for case in CASES:
        folder=ROOT/'results'/case
        rows=[json.loads(x) for x in (folder/'trace.jsonl').read_text(encoding='utf-8').splitlines()]
        manifest=json.loads((folder/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'));result=json.loads((folder/'result.json').read_text(encoding='utf-8'))
        for n in ['sensor_core.py','physics_bridge.py','run_ground_case.py','ground_controller.py']:
            entry=next(a for a in manifest['files'] if Path(a['path']).name==n);assert sha(SNAP/n)==entry['SHA'],n+' snapshot differs from recorded source'
        assert sha(ROOT/'nominal_gain_v1.json')==next(a['SHA'] for a in manifest['files'] if Path(a['path']).name=='nominal_gain_v1.json')
        sources += [meta(folder/n) for n in ['trace.jsonl','result.json','config.json','SOURCE_MANIFEST.json']]
        t=np.array([x['sensor_timestamp_s'] for x in rows]);post=np.array([x['time'] for x in rows]);N=len(t)
        assert np.max(abs(post-t-.01))<1e-9 and np.max(abs(np.diff(t)-.01))<1e-9
        gyro=np.array([x['raw_gyro'] for x in rows]);acc=np.array([x['raw_accel'] for x in rows]);enc=np.array([x['encoder4'] for x in rows]);ed=np.array([x['encoder_rate4'] for x in rows]);wr=np.array([x['wheel_rate2'] for x in rows]);estlog=np.array([x['estimated14'] for x in rows])
        post_rpy=np.array([[x['ground_truth'][k] for k in ['roll_true','pitch_true','yaw_true']] for x in rows]);post_R=Rotation.from_euler('xyz',post_rpy).as_matrix()
        R=np.concatenate([initial_R[None],post_R[:-1]],axis=0);rpy=Rotation.from_matrix(R).as_euler('xyz');true_vb=np.vstack([np.zeros(3),np.array([x['ground_truth']['body_velocity'] for x in rows[:-1]])]);true_gyro=np.vstack([np.zeros(3),np.array([x['ground_truth']['gyro_true'] for x in rows[:-1]])])
        true_xyz=np.vstack([np.array([0.,0.,rows[0]['ground_truth']['xyz'][2]]),np.array([x['ground_truth']['xyz'] for x in rows[:-1]])]);wheelF=np.array([x['wheel_support_N2'] for x in rows]);nonwheel=np.array([x['nonwheel_ground_contact'] for x in rows]);tau=np.array([x['actual_tau'] for x in rows]);requested_tau=np.array([x['raw_requested_tau'] for x in rows])
        assert np.max(abs(gyro-true_gyro))<1e-12
        up=np.einsum('nji,j->ni',R,np.array([0.,0.,sc.G]))
        variants={}
        instrument=[]
        for variant in ['original','truth_init','gyro_only_truth_init','gyro_only_original_init']:
            estimator=sc.StateEstimator(geom,imu_offset=(.03,0,.04),accel_correction=0. if variant.startswith('gyro_only') else 1.5)
            if variant in ['truth_init','gyro_only_truth_init']:estimator.q=sc.quat_from_rpy(*initial_rpy)
            estimates=[];qseq=[]
            for i,row in enumerate(rows):
                pre_vb=estimator.vb.copy();qbefore=None if estimator.q is None else estimator.q.copy()
                packet=sc.SensorPacket(float(t[i]),float(t[i]),gyro[i],acc[i],enc[i],ed[i],wr[i])
                estimate=estimator.update(packet);estimates.append(estimate.state14);qseq.append(estimator.q.copy())
                if variant=='original':
                    proper=estimate.proper_acc_origin;expected=np.array([estimator.wheel_acc,gyro[i,2]*pre_vb[0],0.]);gc=proper-expected;norm=float(np.linalg.norm(gc));confidence=max(0.,1.-abs(norm-sc.G)/(sc.G*.35))
                    if qbefore is None:
                        unit=proper/max(np.linalg.norm(proper),1e-9);qbefore=sc.quat_from_rpy(math.atan2(unit[1],unit[2]),math.atan2(-unit[0],math.hypot(unit[1],unit[2])),0.)
                    cup=sc.rotation(qbefore).T[:,2];correction=1.5*confidence*np.clip(np.cross(gc/max(norm,1e-9),cup),-.3,.3)
                    instrument.append({'alpha':estimator.alpha.copy(),'proper':proper.copy(),'wheel_acc':estimator.wheel_acc,'wheel_mean':float(np.mean(estimate.measured_wheel_forward2)),
                                       'wheel_forward2':estimate.measured_wheel_forward2.copy(),'expected':expected,'gravity_candidate':gc,'gravity_candidate_norm':norm,'confidence':confidence,'correction_omega':correction,
                                       'residual_vs_true_up':gc-up[i],'linear_using_true_attitude':proper-up[i]})
            variants[variant]={'estimated':np.array(estimates),'q_wxyz':np.array(qseq)}
        replayerr=float(np.max(np.abs(variants['original']['estimated']-estlog)));assert replayerr<1e-10,replayerr
        # Actual SO(3) interval increments from time-aligned root R, compared to
        # endpoint gyro samples; original estimator is right-end rectangular.
        dt=np.diff(t);truth_delta=np.einsum('nji,njk->nik',R[:-1],R[1:]);truth_omega=Rotation.from_matrix(truth_delta).as_rotvec()/dt[:,None]
        gyro_schemes={'right_endpoint':gyro[1:],'left_endpoint':gyro[:-1],'trapezoid':(gyro[:-1]+gyro[1:])/2}
        gyro_integrations={};intervals={}
        for scheme,omega in gyro_schemes.items():
            RR=initial_R.copy();seq=[RR.copy()]
            for w,dd in zip(omega,dt):RR=RR@Rotation.from_rotvec(w*dd).as_matrix();seq.append(RR.copy())
            seq=np.array(seq);angles=Rotation.from_matrix(seq).as_euler('xyz');geodesic=Rotation.from_matrix(np.einsum('nji,njk->nik',R,seq)).magnitude()
            gyro_integrations[scheme]={'rpy':angles,'geodesic_error':geodesic};intervals[scheme]=omega-truth_omega
        proper=np.array([x['proper'] for x in instrument]);expected=np.array([x['expected'] for x in instrument]);candidate=np.array([x['gravity_candidate'] for x in instrument]);residual=np.array([x['residual_vs_true_up'] for x in instrument]);conf=np.array([x['confidence'] for x in instrument]);norm=np.linalg.norm(acc,axis=1);wheelmean=np.array([x['wheel_mean'] for x in instrument]);wheelpair=np.array([x['wheel_forward2'] for x in instrument]);corr=np.array([x['correction_omega'] for x in instrument]);alpha=np.array([x['alpha'] for x in instrument])
        # Source gyro-to-Euler pitch rate relation evaluated with TRUE roll, not
        # estimated roll, to isolate sampling/integration mismatch from attitude.
        sampled_pitchrate=gyro[:,1]*np.cos(rpy[:,0])-gyro[:,2]*np.sin(rpy[:,0]);pitchrate_true=np.gradient(rpy[:,1],t)
        v_world=np.einsum('nij,nj->ni',R,true_vb);a_world=np.gradient(v_world,t,axis=0);a_body_from_100Hz=np.einsum('nji,nj->ni',R,a_world)
        windows={}
        for label,mask in [('all',np.ones(N,bool)),('precommand',t<1),('ramp_1_3',(t>=1)&(t<3)),('middle_3_6',(t>=3)&(t<6)),('tail_post_ge_6',post>=6)]:
            if not mask.any():continue
            win={'n':int(mask.sum()),'sensor_time_minmax_s':[float(t[mask].min()),float(t[mask].max())],
              'aligned_est_pitch_error':stats(estlog[mask,2]-rpy[mask,1]),'aligned_est_roll_error':stats(np.array([x['estimated_roll'] for x in rows])[mask]-rpy[mask,0]),'aligned_est_vx_error':stats(estlog[mask,7]-true_vb[mask,0]),
              'true_body_vxyz':stats(true_vb[mask]),'true_rpy':stats(rpy[mask]),'raw_gyro':stats(gyro[mask]),'raw_accel':stats(acc[mask]),'raw_accel_norm':stats(norm[mask]),'proper_origin':stats(proper[mask]),'expected_dynamic_accel_source':stats(expected[mask]),'gravity_candidate':stats(candidate[mask]),'gravity_candidate_minus_true_up':stats(residual[mask]),
              'source_accel_correction_confidence':stats(conf[mask]),'source_confidence_positive_fraction':float(np.mean(conf[mask]>0)), 'correction_omega':stats(corr[mask]),'wheel_mean_vx':stats(wheelmean[mask]),'wheel_pair_disagreement_m_s':stats(wheelpair[mask,0]-wheelpair[mask,1]),'wheel_acc_source':stats(np.array([x['wheel_acc'] for x in instrument])[mask]),
              'true_origin_accel_from_100Hz_velocity_difference':stats(a_body_from_100Hz[mask]),'sampled_pitch_rate_using_true_roll':stats(sampled_pitchrate[mask]),'true_pitch_derivative_100Hz':stats(pitchrate_true[mask]),
              'post_both_wheel_support_fraction_gt1N':float(np.mean(np.all(wheelF[mask]>1.,axis=1))),'post_any_wheel_support_fraction_gt1N':float(np.mean(np.any(wheelF[mask]>1.,axis=1))),'post_nonwheel_contact_count':int(np.count_nonzero(nonwheel[mask])),
              'actual_tau':stats(tau[mask]),'requested_tau':stats(requested_tau[mask]),'actual_wheel_differential_tau':stats(tau[mask,5]-tau[mask,2]),'requested_wheel_differential_tau':stats(requested_tau[mask,5]-requested_tau[mask,2]),'actual_wheel_absolute_peak_fraction':np.mean(np.abs(tau[mask][:,[2,5]])>=5.775909774436091*(1-1e-10),axis=0).tolist(),
              'recorded_final_state_not_rerun':True,'offline_variants':{}}
            for variant,v in variants.items():
                E=v['estimated'];win['offline_variants'][variant]={'pitch_error':stats(E[mask,2]-rpy[mask,1]),'vx_error':stats(E[mask,7]-true_vb[mask,0])}
            win['gyro_only_integrations']={scheme:{'pitch_error':stats(v['rpy'][mask,1]-rpy[mask,1]),'geodesic_orientation_error':stats(v['geodesic_error'][mask])} for scheme,v in gyro_integrations.items()}
            imask=mask[1:]
            win['interval_gyro_minus_root_SO3_average']={scheme:stats(err[imask]) for scheme,err in intervals.items()}
            windows[label]=win
        qtrue0=sc.quat_from_rpy(*initial_rpy);initial={'true_reset_rpy':initial_rpy.tolist(),'raw_accel0':acc[0].tolist(),'raw_accel0_norm':float(norm[0]),'estimator_initial_rpy':sc.rpy(variants['original']['q_wxyz'][0]).tolist(),'source_first_update_dt':0.,'confidence0':float(conf[0]),'source_initializes_from_untrusted_raw_accel_despite_confidence0':True}
        # Packet-local tables, preserving all data-driven terms for independent review.
        arraydata={'sensor_time_s':t,'post_time_s':post,'true_rpy_aligned':rpy,'true_body_velocity_aligned':true_vb,'raw_gyro':gyro,'raw_accel':acc,'true_up_body':up,'proper_origin':proper,'alpha_est_filtered':alpha,'expected_dynamic_source':expected,'gravity_candidate':candidate,'candidate_minus_true_up':residual,'confidence':conf,'correction_omega':corr,'wheel_forward2':wheelpair,'replayed_estimated14':variants['original']['estimated'],'true_omega_SO3_interval':truth_omega,'root_R_aligned':R}
        np.savez_compressed(OUT/(case+'_derived_arrays.npz'),**arraydata)
        output[case]={'config':result['config'],'raw_result_summary':{k:result[k] for k in ['tail_velocity_mean_m_s','tail_yawrate_mean_rad_s','tail_pitch_RMS','estimator_velocity_RMSE','estimator_pitch_RMSE','xy_displacement_m','nonwheel_ground_contact_control_samples']},'time_alignment':{'raw_gyro_equals_previous_row_grade_gyro_max_abs_error':float(np.max(abs(gyro-true_gyro))),'max_post_minus_sample_minus_10ms_s':float(np.max(abs(post-t-.01))),'initial_true_pose_from_gain':True},'replay_max_est14_error':replayerr,'initial':initial,'windows':windows}
        tail=windows['tail_post_ge_6'];summaries[case]={'replay_max_error':replayerr,'initial':initial,'tail':{k:tail[k] for k in ['n','aligned_est_pitch_error','aligned_est_vx_error','raw_accel_norm','source_confidence_positive_fraction','gravity_candidate_minus_true_up','post_both_wheel_support_fraction_gt1N','post_any_wheel_support_fraction_gt1N','post_nonwheel_contact_count','offline_variants','gyro_only_integrations','interval_gyro_minus_root_SO3_average']}}
    result={'kind':'SOURCE_DATA_ONLY_R00_PACKET_DIAGNOSIS','physics_steps':0,'time_advanced_s':0,'sources':sources,'source_hashes_unchanged_after':all(sha(x['path'])==x['sha256'] for x in sources),'cases':output,'limits':['Recorded100Hz samples cannot uniquely reconstruct >50Hz content or prove exact high-rate anti-alias remedy.','Offline estimator replays use the same physical trace; they are not closed-loop performance tests.','Trace grades are post-control; estimator comparisons use prior grade at sensor timestamp.','A stored MuJoCo sensordata sample may be last-stage staggered within0.5ms; no fresh physics sampling experiment performed.']}
    (OUT/'PACKET_DIAGNOSTIC.json').write_text(json.dumps(plain(result),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'PACKET_QUICK_SUMMARY.json').write_text(json.dumps(plain(summaries),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(plain(summaries),ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        (OUT/'PACKET_ANALYSIS_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
