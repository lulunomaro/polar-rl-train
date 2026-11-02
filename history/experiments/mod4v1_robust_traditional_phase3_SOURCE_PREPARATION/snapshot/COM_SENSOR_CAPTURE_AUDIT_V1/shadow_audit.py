"""New sensor-only projection audit. No original trace/DR receipt/physics/Git.
Strict branch never invents calibration. Conditional branch keeps frozen cue
threshold .60 and caps assumed input confidence .50, not a threshold workaround.
"""
from pathlib import Path
from dataclasses import dataclass,asdict
import ast,hashlib,importlib.util,json,math,sys
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent;PROJ=TASK/'SENSOR_CAPTURE_CLOOP_V1'
sys.path.insert(0,str(TASK))
from DYNAMIC_COM_MOTION_V1.com_motion import MovingCOM,Config as COMConfig,Sample,CORE,Valid,Cue,Geometry

TOP={'capture_index','packet','command','drive_feedback','reference','provenance','channel_epoch_semantics','wheel_phase_bound'}
PK={'sampled_us','arrival_us','channel_epoch_us','sequence','flags','coherent','window_begin_us','mean_weight_sum_us','expected_count','valid_count','dropped_count','mean_mode','mean_valid','mean_weights_valid','gyro_body','proper_accel_body','joint_q4','joint_dq4','wheel_spin2'}
CMD={'issued_us','expires_us','sequence','flags','enable','forward_m_s','yaw_rad_s'}
DRIVE={'sampled_us','flags','velocity_row6'}
FORBIDDEN={'rootGT','truth','contact','DR','qpos','qvel','qacc','envelope','true_attitude'}
FROZEN=TASK/'SPIN_H2_K20_V1/sensor_core_v4.py'
PUBLIC_D1=TASK.parent/'traditional_control_20261101/dr_components.py'
READS=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_evidence(p,allowed):
    p=Path(p).resolve();assert p in allowed,'No evidence read outside declared projection/public/frozen allowlist: '+str(p)
    raw=p.read_bytes();READS.append({'path':str(p),'bytes':len(raw),'SHA':sha(raw)});return raw

def vector(x,n):
    a=np.asarray(x,float)
    if a.shape!=(n,) or not np.isfinite(a).all():raise ValueError('sensor vector shape/finite')
    return a

def int_us(x):
    if isinstance(x,bool) or not isinstance(x,int) or x<0:raise ValueError('nonnegative integer us/count required')
    return x

def validate(row,index=None):
    if not isinstance(row,dict) or set(row)!=TOP:raise ValueError('Top-level projection allowlist')
    for obj,keys in ((row['packet'],PK),(row['command'],CMD),(row['drive_feedback'],DRIVE)):
        if not isinstance(obj,dict) or set(obj)!=keys:raise ValueError('Nested projection allowlist')
    p=row['packet'];c=row['command'];d=row['drive_feedback']
    for key in PK-{'channel_epoch_us','gyro_body','proper_accel_body','joint_q4','joint_dq4','wheel_spin2'}:int_us(p[key])
    for x in p['channel_epoch_us']:int_us(x)
    if len(p['channel_epoch_us'])!=4:raise ValueError('channel epoch shape')
    for key,n in [('gyro_body',3),('proper_accel_body',3),('joint_q4',4),('joint_dq4',4),('wheel_spin2',2)]:vector(p[key],n)
    v=vector(d['velocity_row6'],6);dq=vector(p['joint_dq4'],4);spin=vector(p['wheel_spin2'],2)
    if not np.array_equal(v,np.array([dq[0],dq[1],spin[0],dq[2],dq[3],spin[1]])):raise ValueError('Drive is not identical encoder velocity domain')
    if d['sampled_us']!=p['sampled_us'] or p['arrival_us']<p['sampled_us']:raise ValueError('drive/sensor clock binding')
    if row['reference']!='canonicalchassisBODY/loadsideSI' or row['wheel_phase_bound'] is not False:raise ValueError('reference/wheel phase declaration')
    if index is not None and row['capture_index']!=index:raise ValueError('capture index')
    if c['expires_us']<c['issued_us'] or not all(math.isfinite(float(c[k])) for k in ('forward_m_s','yaw_rad_s')):raise ValueError('command metadata')
    return p

def window(p):
    t=p['sampled_us'];n=p['expected_count']
    if p['mean_mode']==0:
        if n!=1 or p['valid_count']!=1 or p['dropped_count']!=0 or p['mean_weight_sum_us']!=0 or p['window_begin_us']!=t:raise ValueError('boot instant metadata')
        return {'kind':'instant','center_us':float(t),'begin_us':t,'last_us':t,'variance_time_s2':0.,'q_end_to_center_s':0.,'aperture_span_us':0}
    if p['mean_mode']!=1 or n!=20 or p['valid_count']!=20 or p['dropped_count']!=0 or p['mean_weight_sum_us']!=10000 or p['window_begin_us']!=t-10000 or p['mean_weights_valid']!=1 or p['mean_valid']!=1:raise ValueError('mean aperture metadata')
    times=np.arange(n,dtype=float)*500+p['window_begin_us'];center=float(np.mean(times));variance=float(np.mean(((times-center)/1e6)**2))
    return {'kind':'mean20','center_us':center,'begin_us':int(times[0]),'last_us':int(times[-1]),'variance_time_s2':variance,'q_end_to_center_s':(t-center)/1e6,'aperture_span_us':int(times[-1]-times[0]),'epoch_is_not_instant_sync':True}

def derivative_abs_lag_s(dt,win):
    """E|u-v| for20sample box aperture u and finite-diff v~U[0,dt].
    Bounds jerk propagation to CURRENT mean-center, not to epoch endpoint.
    """
    u=(np.arange(20)*500+win['begin_us']-win['center_us'])/1e6
    def average_abs(x):
        if x<=0:return dt/2-x
        if x>=dt:return x-dt/2
        return (x*x+(dt-x)**2)/(2*dt)
    return float(np.mean([average_abs(float(x)) for x in u]))

def public_noise():
    raw=read_evidence(PUBLIC_D1,{PUBLIC_D1.resolve()});src=raw.decode('utf-8');start=src.index('CHANNELS = {');end=src.index('\n}',start)+2;excerpt=src[start:end]
    node=ast.parse(excerpt).body[0];channels=ast.literal_eval(node.value)
    expected={'omega3':.125,'gravity3':.025,'legq4':.005,'legqd4':.25,'wheelqd2':.5}
    assert {k:v[1] for k,v in channels.items()}==expected
    return expected,{'path':str(PUBLIC_D1),'source_SHA':sha(raw),'D1_assignment_excerpt':excerpt,'D1_assignment_SHA':sha(excerpt.encode()),'scope':'one observe call per100Hz feedback packet; D1 before D3; NOT20 independent D1 draws averaged','proper_mapping':'BENCHMARK assumption dimensionless gravity3 halfwidth*9.81 gives proper m/s2; not hardware calibration','episode_receipt_or_random_parameter_read':False}

def load_v4():
    raw=read_evidence(FROZEN,{FROZEN.resolve()});name='frozen_v4_sensor_math_for_new_shadow';spec=importlib.util.spec_from_file_location(name,FROZEN);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module,{'path':str(FROZEN),'SHA':sha(raw),'source_unmodified':True,'uses_only_sensor_math':True}

@dataclass(frozen=True)
class Assumptions:
    name: str='conditional_public_D1_window_model_not_hardware_calibration'
    sample_quantum_us: int=500
    mean_count: int=20
    lever_origin_to_IMU_B3: tuple=(.03,0.,.04)
    lever_position_error_norm_m: float=.0005
    qdd_jerk_abs_bound_rad_s3: float=1000.
    angular_jerk_abs_bound_rad_s3: float=200.
    wheel_jerk_abs_bound_rad_s3: float=100000.
    IMU_specific_force_second_derivative_abs_bound_m_s4: float=2000.
    unverified_encoder_zero_allowance_rad: float=.01
    assumed_input_confidence_cap: float=.50
    no_D1_reduction_by_mean_count: bool=True
    assumptions_are_not_measured_or_episode_truth: bool=True

def strict_result(reason):return {'cue':int(Cue.UNCERTAIN),'confidence':0.,'proper_COM_B3':None,'radius_m_s2':None,'availability':'unbound_not_fake_zero','reasons':[reason,'HARDWARE_AND_TIMING_MODEL_NOT_CALIBRATED','NO_WHEEL_PHASE_OR_MOTION_ERROR_BINDING']}
def percentiles(values):
    v=np.asarray([x for x in values if x is not None and math.isfinite(float(x))],float)
    return None if not len(v) else {'n':len(v),'min':float(v.min()),'p50':float(np.percentile(v,50)),'p95':float(np.percentile(v,95)),'max':float(v.max())}

class Shadow:
    def __init__(self,noise,a,v4):
        self.noise=noise;self.a=a;self.v4=v4;self.model=MovingCOM();self.geom=self.model.geometry
        k=v4.LinkageGeometry(self.geom.base.pins);self.frozen=v4.StateEstimator(k,imu_offset=a.lever_origin_to_IMU_B3,upright_prior=True)
        self.prev=None;self.last_key=None;self.last_payload=None;self.prior_alpha_weight=1.;self.mean_seen=False
    def row(self,row):
        p=validate(row);win=window(p);t=p['sampled_us'];now=p['arrival_us'];key=(t,p['sequence']);payload=json.dumps({k:v for k,v in p.items() if k!='arrival_us'},sort_keys=True)
        epochs=p['channel_epoch_us'];shared=all(x==t for x in epochs)
        if not shared or p['coherent']!=1 or p['flags']!=1:raise ValueError('Declared shared queue epoch not coherent')
        clock={'sampled_us':t,'arrival_us':now,'queue_age_us':now-t,'window':win,'mean_center_age_us':now-win['center_us'],'q_position_epoch_to_mean_center_us':t-win['center_us'],'shared_queue_epoch':True,'instant_sync_not_inferred_from_coherent':win['kind']=='mean20'}
        sp=self.v4.SensorPacket(t/1e6,now/1e6,np.array(p['gyro_body']),np.array(p['proper_accel_body']),np.array(p['joint_q4']),np.array(p['joint_dq4']),np.array(p['wheel_spin2']))
        e=self.frozen.update(sp)
        baseline={'omega_B3':e.omega_body.tolist(),'alpha_LP60ms_B3':self.frozen.alpha.tolist(),'proper_origin_B3':e.proper_acc_origin.tolist(),'alpha_LP_tau_s':.06,'not_current_instantaneous_or_COM_calibration':True}
        result={'capture_index':row['capture_index'],'sampled_us':t,'arrival_us':now,'clock':clock,'frozenV4_baseline':baseline,'strict_unbound':strict_result('STRICT_UNKNOWN_NO_APERTURE_JERK_OR_CALIBRATION_BOUND')}
        def no(reason):result['conditional']=strict_result(reason);return result
        if self.last_key is not None:
            if key==self.last_key:
                if payload!=self.last_payload:raise ValueError('Same sensor sequence/epoch changed payload')
                clock['duplicate_epoch_no_new_derivative']=True;return no('REPEATED_SENSOR_EPOCH_NOT_FRESH_DERIVATIVE')
            if key[0]<=self.last_key[0] or key[1]<=self.last_key[1]:raise ValueError('Sensor epoch/sequence rollback')
        self.last_key=key;self.last_payload=payload
        clock['fresh_sensor_epoch']=True
        if win['kind']=='instant':self.prev=None;clock['boot_instant']=True;return no('BOOT_INSTANT_NO_SENSOR_ACCELERATION_HISTORY')
        current={'p':p,'win':win};old=self.prev;self.prev=current
        if old is None:
            clock['instant_to_mean_boundary_reset']=True;self.mean_seen=True;return no('INSTANT_TO_MEAN_RESET_NO_CROSS_BOUNDARY_DIFFERENCE')
        dt=(win['center_us']-old['win']['center_us'])/1e6
        if not .001<=dt<=.04:return no('MEAN_CENTER_DT_UNSUITABLE')
        self.prior_alpha_weight*=.06/(.06+dt)
        clock.update(derivative_dt_us=dt*1e6,derivative_nominal_center_us=(win['center_us']+old['win']['center_us'])/2,derivative_center_age_us=now-(win['center_us']+old['win']['center_us'])/2,derivative_support_begin_us=old['win']['begin_us'],derivative_support_last_us=win['last_us'],baseline_LP_steady_effective_age_us=now-(win['center_us']+old['win']['center_us'])/2+60000,baseline_initial_alpha_weight_upper=self.prior_alpha_weight)
        a=self.a;n=self.noise;v=np.array(p['joint_dq4']);omega=np.array(p['gyro_body']);spin=np.array(p['wheel_spin2']);q=np.array(p['joint_q4']);proper=np.array(p['proper_accel_body']);prev=old['p']
        qdd=(v-np.array(prev['joint_dq4']))/dt;alpha=(omega-np.array(prev['gyro_body']))/dt;wheel_acc=(spin-np.array(prev['wheel_spin2']))/dt;lag=derivative_abs_lag_s(dt,win);variance=win['variance_time_s2'];delta=win['q_end_to_center_s']
        qde=n['legqd4']+.5*a.qdd_jerk_abs_bound_rad_s3*variance;we=n['omega3']+.5*a.angular_jerk_abs_bound_rad_s3*variance
        qdde=2*n['legqd4']/dt+a.qdd_jerk_abs_bound_rad_s3*lag;ae=2*n['omega3']/dt+a.angular_jerk_abs_bound_rad_s3*lag
        wheel_ve=n['wheelqd2']+.5*a.wheel_jerk_abs_bound_rad_s3*variance;wheel_ae=2*n['wheelqd2']/dt+a.wheel_jerk_abs_bound_rad_s3*lag
        qc=q-v*delta-.5*qdd*delta*delta
        qe=n['legq4']+a.unverified_encoder_zero_allowance_rad+qde*delta+.5*qdde*delta*delta+a.qdd_jerk_abs_bound_rad_s3*delta**3/6
        lever=np.array(a.lever_origin_to_IMU_B3);root_proper=proper-np.cross(alpha,lever)-np.cross(omega,np.cross(omega,lever))
        wn=float(np.linalg.norm(omega));an=float(np.linalg.norm(alpha));we_norm=math.sqrt(3)*we;ae_norm=math.sqrt(3)*ae;lever_norm=float(np.linalg.norm(lever))
        root_lever_error_norm=ae_norm*lever_norm+(2*wn*we_norm+we_norm**2)*lever_norm+(an+ae_norm+(wn+we_norm)**2)*a.lever_position_error_norm_m
        proper_axis_error=n['gravity3']*9.81+.5*a.IMU_specific_force_second_derivative_abs_bound_m_s4*variance+root_lever_error_norm
        s=Sample(win['center_us']/1e6,CORE|Valid.QDD4|Valid.ALPHA,tuple(qc),tuple(v),tuple(root_proper),tuple(omega),'chassis_origin',alpha_B3=tuple(alpha),qdd4=tuple(qdd),q_error_rad4=(qe,)*4,qd_error_rad_s4=(qde,)*4,qdd_error_rad_s24=(qdde,)*4,proper_error_m_s23=(proper_axis_error,)*3,omega_error_rad_s3=(we,)*3,alpha_error_rad_s23=(ae,)*3,encoder_calibration_confidence=a.assumed_input_confidence_cap,imu_frame_calibration_confidence=a.assumed_input_confidence_cap,derivative_confidence=a.assumed_input_confidence_cap,wheel_angle2=None,wheel_rate2=tuple(spin),wheel_acc2=tuple(wheel_acc),wheel_rate_error_rad_s2=(wheel_ve,)*2,wheel_acc_error_rad_s22=(wheel_ae,)*2,wheel_binding_id='projection_relative_output_encoder_mean_window_model_ASSUMPTION')
        out=self.model.update(s,now/1e6);interval=out.proposed_norm_interval_m_s2;interval_class='unavailable'
        if interval is not None:
            interval_class='overlap'
            if interval[1]<=self.model.c.freefall_max_g*9.81:interval_class='freefall_like_by_assumed_radius_only'
            elif interval[0]>=self.model.c.nonfreefall_min_g*9.81:interval_class='nonfreefall_like_by_assumed_radius_only'
        result['conditional']={'cue':int(out.cue),'confidence':out.confidence,'proper_COM_B3':out.proper_COM_B3,'nominal_corrected_estimate_B3':out.nominal_corrected_estimate_B3,'radius_m_s2':out.proposed_error_radius_m_s2,'norm_interval_m_s2':interval,'interval_diagnostic_NOT_trusted_cue':interval_class,'r_COM_B3':out.r_COM_B3,'rDot_COM_B3':out.rDot_COM_B3,'rDDot_COM_B3':out.rDDot_COM_B3,'nominal_corrected_norm_m_s2':None if out.nominal_corrected_estimate_B3 is None else float(np.linalg.norm(out.nominal_corrected_estimate_B3)),'reasons':out.reasons,'wheel_missing_bound':out.wheel_missing_bound,'alpha_FD_B3':alpha.tolist(),'qdd_FD4':qdd.tolist(),'proper_origin_window_center_model_B3':root_proper.tolist(),'q4_window_center_model':qc.tolist(),'error_assumptions':{'q_axis_rad':qe,'qd_axis_rad_s':qde,'qdd_axis_rad_s2':qdde,'omega_axis_rad_s':we,'alpha_axis_rad_s2':ae,'proper_axis_m_s2':proper_axis_error,'FD_jerk_mean_absolute_lag_s':lag,'D1_noise_not_divided_by20':True,'IMU_to_root_lever_error_norm_m_s2':root_lever_error_norm,'same_public_bounds_all_cases_no_episode_parameter_use':True,'conditional_not_hardware_calibration':True}}
        return result

def summarize(case,outputs,source):
    total=len(outputs);eligible=[x for x in outputs if 'qdd_FD4' in x['conditional']];bounded=[x for x in outputs if x['conditional']['proper_COM_B3'] is not None];numeric=[x for x in outputs if x['conditional'].get('nominal_corrected_estimate_B3') is not None]
    counts=lambda branch:{str(k):sum(x[branch]['cue']==k for x in outputs) for k in (0,1,2)}
    return {'case':case,'rows':total,'source_projection_SHA':source['SHA'],'original_case_sourceSHA_reference_only':source['source_trace_SHA'],'fresh_epochs':sum(bool(x['clock'].get('fresh_sensor_epoch')) for x in outputs),'duplicate_epochs':sum(bool(x['clock'].get('duplicate_epoch_no_new_derivative')) for x in outputs),'boot_instant_rows':sum(bool(x['clock'].get('boot_instant')) for x in outputs),'instant_mean_boundary_reset_rows':sum(bool(x['clock'].get('instant_to_mean_boundary_reset')) for x in outputs),'mean20_rows':sum(x['clock']['window']['kind']=='mean20' for x in outputs),'fresh_homogeneous_mean_derivative_rows':len(eligible),'clock_queue_age_us':percentiles(x['clock']['queue_age_us'] for x in outputs),'clock_mean_center_age_us':percentiles(x['clock']['mean_center_age_us'] for x in outputs if x['clock']['window']['kind']=='mean20'),'clock_derivative_center_age_us':percentiles(x['clock'].get('derivative_center_age_us') for x in outputs),'baseline_LP60ms_steady_age_us':percentiles(x['clock'].get('baseline_LP_steady_effective_age_us') for x in outputs),'q_epoch_to_mean_skew_us':percentiles(x['clock']['q_position_epoch_to_mean_center_us'] for x in outputs),'strict_unbound':{'usable_vectors':0,'usable_rate_allrows':0.,'cue_counts':counts('strict_unbound'),'confidence_never_invented':True},'conditional':{'numeric_shadow_rows':len(numeric),'bounded_under_declared_assumptions_rows':len(bounded),'numeric_rate_allrows':len(numeric)/total,'bounded_rate_allrows':len(bounded)/total,'bounded_rate_eligible_mean_rows':None if not eligible else len(bounded)/len(eligible),'cue_counts':counts('conditional'),'cue_usable_rate_allrows':sum(x['conditional']['cue']!=0 for x in outputs)/total,'radius_m_s2':percentiles(x['conditional']['radius_m_s2'] for x in outputs),'nominal_corrected_norm_m_s2':percentiles(x['conditional'].get('nominal_corrected_norm_m_s2') for x in outputs),'confidence':percentiles(x['conditional']['confidence'] for x in outputs),'qdd_axis_error_bound_rad_s2':percentiles(x['conditional'].get('error_assumptions',{}).get('qdd_axis_rad_s2') for x in outputs),'alpha_axis_error_bound_rad_s2':percentiles(x['conditional'].get('error_assumptions',{}).get('alpha_axis_rad_s2') for x in outputs),'interval_nonfreefall_only_diagnostic_rows':sum(x['conditional'].get('interval_diagnostic_NOT_trusted_cue')=='nonfreefall_like_by_assumed_radius_only' for x in outputs),'no_FSM_threshold_lowering_or_point8_forcing':True},'no_truth_grading':'No physical/pose/contact/DR originals were read; applicability not accuracy/hardware calibration'}

def run(out):
    READS.clear()
    out=Path(out);assert not (out/'SUMMARY.json').exists();out.mkdir(parents=True,exist_ok=True)
    manifest_path=PROJ/'MANIFEST.json';raw=read_evidence(manifest_path,{manifest_path.resolve()});manifest=json.loads(raw);assert set(manifest['allowed_keys'])==TOP and sum(x['rows'] for x in manifest['sources'])==4400
    noise,noise_source=public_noise();v4,v4_source=load_v4();a=Assumptions();all_summaries=[]
    for source in manifest['sources']:
        p=Path(source['path']).resolve();assert p.parent==PROJ.resolve() and p.name.endswith('_sensor_only.jsonl')
        raw=read_evidence(p,{p});assert sha(raw)==source['SHA'] and len(raw)==source['bytes'];rows=[json.loads(line) for line in raw.splitlines()];assert len(rows)==source['rows']
        shadow=Shadow(noise,a,v4);outputs=[]
        for i,row in enumerate(rows):validate(row,i);outputs.append(shadow.row(row))
        dest=out/(source['case']+'_shadow.jsonl');assert not dest.exists();dest.write_text(''.join(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n' for x in outputs),encoding='utf-8')
        all_summaries.append(summarize(source['case'],outputs,source))
    summary={'status':'SENSOR_ONLY_SHADOW_APPLICABILITY_NOT_TRUTH_ACCURACY_OR_HARDWARE_CALIBRATION','projection_manifest_SHA':sha((PROJ/'MANIFEST.json').read_bytes()),'total_rows':sum(s['rows'] for s in all_summaries),'cases':all_summaries,'public_D1_source':noise_source,'public_D1_halfwidths_same_allcases':noise,'assumptions':asdict(a),'frozen_V4_source':v4_source,'frozen_COM_config_unchanged':asdict(COMConfig()),'evidence_reads':READS,'original_case_trace_or_DR_receipt_reads':0,'new_physics_steps':0,'Git_or_new_agents_or_real_IO':False,'verdict':'Strict all uncertain. Conditional vectors only under explicit window/jerk/model/error assumptions, .50 confidence below frozen.60 cue threshold; not current instant calibration. Same epoch does not remove aperture or alpha60ms lag.'}
    (out/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');return summary
