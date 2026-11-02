"""Condition existing R00 packets on source gating/support, no physical replay.
Also test the 0.5ms qpos-vs-kinematic-stage stagger hypothesis by pure FK.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,struct,sys,traceback
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent
SNAP=ROOT/'source_snapshots/r00'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stats(a):
    a=np.asarray(a,float)
    if not a.size:return None
    return {'n':len(a),'mean':np.mean(a,axis=0).tolist(),'rms':np.sqrt(np.mean(a*a,axis=0)).tolist(),'min':np.min(a,axis=0).tolist(),'max':np.max(a,axis=0).tolist()}
def weighted(a,w):
    a=np.asarray(a,float);w=np.asarray(w,float)
    if not np.sum(w)>0:return None
    ww=w.reshape((len(w),)+(1,)*(a.ndim-1))
    return {'mean':np.sum(ww*a,axis=0).tolist()/float(np.sum(w)) if a.ndim==1 else (np.sum(ww*a,axis=0)/np.sum(w)).tolist(),'rms':(np.sqrt(np.sum(ww*a*a,axis=0)/np.sum(w))).tolist()}
def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def main():
    assert not (OUT/'CONDITIONED_DYNAMICS.json').exists()
    spec=importlib.util.spec_from_file_location('frozen_sensor_for_conditioning',SNAP/'sensor_core.py');sc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sc;spec.loader.exec_module(sc)
    pins=json.loads((ROOT.parent/'traditional_control_20261101/reports/model_manifest.json').read_text(encoding='utf-8'))['neutral_skeleton_xz_m'];geom=sc.LinkageGeometry(pins,radius=.06369999796152115);hardware_geom=sc.LinkageGeometry(pins,radius=.0625)
    raw=(ROOT/'MODEL_AUDIT/usd_meshes/left_tire.stl').read_bytes();num=struct.unpack_from('<I',raw,80)[0];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);v=np.unique(np.frombuffer(raw,dtype=dt,count=num,offset=84)['v'].reshape(-1,3),axis=0);radial=np.unique(np.round(np.arctan2(v[:,2],v[:,0]),10));facets=len(radial)
    outputs={};summary={}
    for case in ['r00_forward_nominal_sensors','r00_spin_nominal_sensors']:
        folder=ROOT/'results'/case;rows=[json.loads(x) for x in (folder/'trace.jsonl').read_text(encoding='utf-8').splitlines()];arr=np.load(OUT/(case+'_derived_arrays.npz'))
        t=arr['sensor_time_s'];post=arr['post_time_s'];R=arr['root_R_aligned'];true_rpy=arr['true_rpy_aligned'];true_vb=arr['true_body_velocity_aligned'];gyro=arr['raw_gyro'];gc=arr['gravity_candidate'];confidence=arr['confidence'];wheelpair=arr['wheel_forward2'];resid=arr['candidate_minus_true_up'];corr=arr['correction_omega'];est=arr['replayed_estimated14'];N=len(rows)
        force=np.vstack([np.zeros(2),np.array([x['wheel_support_N2'] for x in rows[:-1]])]);both=np.all(force>1.,axis=1);anywheel=np.any(force>1.,axis=1);proxy=np.array([r['contact_proxy'] for r in rows]);variance=np.array([r['velocity_variance'] for r in rows]);wheelerr=wheelpair.mean(axis=1)-true_vb[:,0]
        tilt=np.arctan2(-gc[:,0],np.hypot(gc[:,1],gc[:,2]));tilterror=tilt-true_rpy[:,1]
        rw=[];relative=[];omegawheel=[];radii_change=[]
        for i,row in enumerate(rows):
            rrs=[];rel=[];ows=[];changed=[]
            for j,side in enumerate(['left','right']):
                h,c=row['encoder4'][2*j:2*j+2];hd,cd=row['encoder_rate4'][2*j:2*j+2];spin=row['wheel_rate2'][j]
                rootv,rr,J,knee=geom.wheel_kinematics(h,c,hd,cd,spin,gyro[i],side);vel=J@np.array([hd,cd]);rrs.append(rr);rel.append(vel)
                ow=(rootv+vel[0]+np.cross(gyro[i],rr)[0])/geom.radius;ows.append(ow)
                hwr=hardware_geom.wheel_kinematics(h,c,hd,cd,spin,gyro[i],side)[0];changed.append(hwr-rootv)
            rw.append(np.mean(rrs,axis=0));relative.append(np.mean(rel,axis=0));omegawheel.append(ows);radii_change.append(changed)
        rw=np.array(rw);relative=np.array(relative);omegawheel=np.array(omegawheel);radii_change=np.array(radii_change)
        trace_rw=np.full((N,3),np.nan)
        for i in range(1,N):
            g=rows[i-1]['ground_truth'];trace_rw[i]=R[i].T@(np.mean(g['wheel_xyz'],axis=0)-np.array(g['xyz']))
        stagger_before=rw-trace_rw;stagger_template=(true_vb+relative)*.0005;stagger_after=stagger_before-stagger_template
        # The actual spin did not stay around an assumed origin. This is a
        # conditional rigid yaws-only term using measured yaw, not commanded4pi.
        centripetal_O_about_W=np.column_stack([gyro[:,2]**2*rw[:,0],gyro[:,2]**2*rw[:,1],np.zeros(N)])
        windows={}
        for label,mask in [('all',np.ones(N,bool)),('precommand',t<1),('ramp_1_3',(t>=1)&(t<3)),('middle_3_6',(t>=3)&(t<6)),('tail_post_ge_6',post>=6)]:
            w=confidence[mask];good=mask&(confidence>0)
            conditioned={}
            for name,condition in [('both_supported',both),('one_supported',anywheel&~both),('neither_supported',~anywheel),('source_contact_proxy_zero',proxy<=0),('source_confidence_zero',confidence<=0)]:
                mm=mask&condition;conditioned[name]={'n':int(mm.sum()),'wheel_mean_vx_measurement_error':stats(wheelerr[mm]),'KF_vx_error':stats(est[mm,7]-true_vb[mm,0]),'source_confidence':stats(confidence[mm])}
            imask=mask.copy();imask[0]=False
            windows[label]={'n':int(mask.sum()),'candidate_pitch_minus_true_pitch_conf_positive':stats(tilterror[good]),'candidate_pitch_minus_true_pitch_conf_weighted':weighted(tilterror[mask],w),
                'gravity_candidate_minus_true_up_conf_weighted':weighted(resid[mask],w),'proper_candidate_direction_conf_positive':stats(gc[good]/np.maximum(np.linalg.norm(gc[good],axis=1)[:,None],1e-15)),
                'correction_body_omega_integral_rad':np.sum(corr[mask]*.01,axis=0).tolist(),'source_mean_contact_proxy':float(proxy[mask].mean()),'source_velocity_std_reported_m_s':stats(np.sqrt(variance[mask])),
                'actual_velocity_error_over_reported_std_RMS':float(np.sqrt(np.mean((est[mask,7]-true_vb[mask,0])**2/variance[mask]))),
                'actual_raw_omega':stats(gyro[mask]),'potential_tire_facets_per_s_from_absolute_wheel_y_rate':stats(np.abs(omegawheel[mask])*facets/(2*math.pi)),
                'hardware_radius_0625_minus_source_radius_vx_measurement_change_m_s':stats(np.mean(radii_change[mask],axis=1)),
                'wheelmid_B_m':stats(rw[mask]),'yaw_only_rigid_origin_about_W_centripetal_template_m_s2':stats(centripetal_O_about_W[mask]),
                'FK_vs_recorded_wheelmid_before_stagger_correction_m':stats(stagger_before[imask]),'FK_vs_recorded_wheelmid_after_first_order_stagger_correction_m':stats(stagger_after[imask]),
                'stagger_rms_norm_before_m':float(np.sqrt(np.mean(np.sum(stagger_before[imask]**2,axis=1)))),'stagger_rms_norm_after_m':float(np.sqrt(np.mean(np.sum(stagger_after[imask]**2,axis=1)))),'conditioned':conditioned}
        outputs[case]={'windows':windows,'point_samples':[{'sensor_t':float(t[i]),'estimated_pitch':float(est[i,2]),'true_pitch':float(true_rpy[i,1]),'candidate_pitch':float(tilt[i]),'confidence':float(confidence[i]),'raw_yaw':float(gyro[i,2]),'true_vx':float(true_vb[i,0]),'estimated_vx':float(est[i,7]),'wheel_mean':float(wheelpair[i].mean())} for i in [0,99,199,299,399,499,599,699,799]]}
        tail=windows['tail_post_ge_6'];summary[case]={'confidence_weighted_accel_pitch_error':tail['candidate_pitch_minus_true_pitch_conf_weighted'],'source_velocity_std':tail['source_velocity_std_reported_m_s'],'RMS_actual_v_error_in_reported_sigma':tail['actual_velocity_error_over_reported_std_RMS'],'facet_rate_Hz':tail['potential_tire_facets_per_s_from_absolute_wheel_y_rate'],'radius_change_vx_delta':tail['hardware_radius_0625_minus_source_radius_vx_measurement_change_m_s'],'stagger_norm_RMS_before_after_m':[tail['stagger_rms_norm_before_m'],tail['stagger_rms_norm_after_m']],'yaw_only_origin_centripetal_at_actual_omega':tail['yaw_only_rigid_origin_about_W_centripetal_template_m_s2'],'conditioned':tail['conditioned'],'total_correction_body_omega_integral':windows['all']['correction_body_omega_integral_rad']}
    result={'kind':'CONDITIONED_RECORDED_DATA_ONLY','physics_steps':0,'source_tire_radial_polygon_sides':facets,'source_tire_vertices':len(v),'cases':outputs,'caveats':['Support conditioning is offline truth diagnosis, not a deployable contact gate.','Potential facetpass rate is a geometric excitation rate inferred from wheel angular motion, not measured above-Nyquist spectrum.','First-order0.5ms stage correction is a timestamp diagnostic approximation; unrecorded substep states remain unavailable.','Changing radius/replay estimator on a fixed trace does not establish new closed-loop skill performance.']}
    (OUT/'CONDITIONED_DYNAMICS.json').write_text(json.dumps(plain(result),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'CONDITIONED_QUICK_SUMMARY.json').write_text(json.dumps(plain(summary),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(plain({'polygon_sides':facets,'summary':summary}),ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        (OUT/'CONDITIONING_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
