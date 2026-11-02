"""2k noisy-sample discrete COM functional. No true pose/DR/contact/physics."""
from dataclasses import replace
from pathlib import Path
import math,sys
import numpy as np
TASK=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(TASK))
from INTEGRATED_COM_WINDOW_V1.window_math import exp_rotation,integrated_rotation,EndpointModel,BudgetAssumptions
from DYNAMIC_COM_MOTION_V1.com_motion import Geometry

TOP={'kind','sequence','source_epoch_us','window_begin_us','window_end_us','aperture_us','mean_mode','count','sample_weight_us','dropped_count','correlated_postmean_noise','extra_information_branch','hardware_binding','actuation_used','mean','endpoint_joint_pos4','samples','payload_SHA','arrival_us','duplicate_source'}
SAMPLE={'gyro_body','accel_proper_body','joint_pos4','joint_vel4','wheel_vel2','sampled_us','encoder_pos_sampled_us','encoder_rate_sampled_us','weight_us','valid'}
MEAN={'accel_proper_body','joint_vel4','wheel_vel2','gyro_body'}
DIMS={'gyro_body':3,'accel_proper_body':3,'joint_pos4':4,'joint_vel4':4,'wheel_vel2':2}

def vec(x,n):
    v=np.asarray(x,float)
    if v.shape!=(n,) or not np.isfinite(v).all():raise ValueError('finite vector shape')
    return v

def validate(frame):
    if set(frame)!=TOP or set(frame['mean'])!=MEAN:raise ValueError('strict frame/mean allowlist')
    if frame['kind']!='RAW2K_CORRELATED_SHADOW_NOT_OLD_BENCHMARK' or frame['hardware_binding'] is not False or frame['actuation_used'] is not False or frame['correlated_postmean_noise'] is not True or frame['extra_information_branch'] is not True:raise ValueError('branch declaration')
    for k in ('sequence','source_epoch_us','window_begin_us','window_end_us','aperture_us','mean_mode','count','sample_weight_us','dropped_count','arrival_us'):
        if isinstance(frame[k],bool) or not isinstance(frame[k],int) or frame[k]<0:raise ValueError('integer clock/count')
    if frame['arrival_us']<frame['source_epoch_us'] or len(frame['samples'])!=frame['count']:raise ValueError('time/count')
    for k in MEAN:vec(frame['mean'][k],DIMS[k])
    vec(frame['endpoint_joint_pos4'],4)
    for s in frame['samples']:
        if set(s)!=SAMPLE or s['valid'] is not True:raise ValueError('strict sample allowlist/validity')
        for k,n in DIMS.items():vec(s[k],n)
        if s['sampled_us']!=s['encoder_pos_sampled_us'] or s['sampled_us']!=s['encoder_rate_sampled_us']:raise ValueError('raw q/qd/IMU time not aligned')
    if frame['mean_mode']==0:
        if frame['count']!=1 or frame['aperture_us']!=0 or frame['sample_weight_us']!=0:raise ValueError('boot mode')
    elif frame['mean_mode']==1:
        if frame['count']!=20 or frame['aperture_us']!=10000 or frame['sample_weight_us']!=500 or frame['dropped_count']!=0 or frame['window_begin_us']!=frame['source_epoch_us']-10000 or frame['window_end_us']!=frame['source_epoch_us']:raise ValueError('steady20 metadata')
        if [s['sampled_us'] for s in frame['samples']]!=list(range(frame['window_begin_us'],frame['source_epoch_us'],500)) or any(s['weight_us']!=500 for s in frame['samples']):raise ValueError('rawtime/weights')
    else:raise ValueError('meanmode')

class Stitch:
    def __init__(self):self.points=[];self.ends=[];self.last_key=None;self.last_payload=None;self.duplicates=0;self.boots=0;self.total_samples=0;self.unique_source_samples=0;self.mean_max_error=0.;self.endpoint_q_time_difference=[]
    def add(self,frame):
        validate(frame);self.total_samples+=frame['count'];key=(frame['sequence'],frame['source_epoch_us']);payload={k:v for k,v in frame.items() if k not in ('arrival_us','duplicate_source')}
        if key==self.last_key:
            if payload!=self.last_payload:raise ValueError('duplicate source payload differs')
            self.duplicates+=1;return
        if self.last_key is not None and (key[0]<=self.last_key[0] or key[1]<=self.last_key[1]):raise ValueError('sequence/epoch rollback')
        self.last_key=key;self.last_payload=payload;self.unique_source_samples+=frame['count']
        if frame['mean_mode']==0:self.boots+=1;return
        for k in MEAN:
            m=np.mean([s[k] for s in frame['samples']],axis=0);self.mean_max_error=max(self.mean_max_error,float(np.max(abs(m-np.array(frame['mean'][k])))))
        for s in frame['samples']:
            if self.points and s['sampled_us']<=self.points[-1]['sampled_us']:raise ValueError('nonmonotonic or duplicate joined rawsample')
            self.points.append({**s,'mean':frame['mean'],'source_sequence':frame['sequence'],'source_epoch_us':frame['source_epoch_us']})
        self.ends.append({'index':len(self.points)-1,'arrival_us':frame['arrival_us'],'source_epoch_us':frame['source_epoch_us'],'sequence':frame['sequence']})
        self.endpoint_q_time_difference.append(float(np.max(abs(np.array(frame['endpoint_joint_pos4'])-np.array(frame['samples'][-1]['joint_pos4'])))))

class Prefix:
    """Gyro-only gauge prefixes of exact per-sample constant-bin transports."""
    def __init__(self,points):
        n=len(points);self.points=points;self.R=np.zeros((n,3,3));self.M=np.zeros_like(self.R);self.I=np.zeros((n,3));self.J=np.zeros_like(self.I);self.norm_integral=np.zeros(n);self.time_norm_integral=np.zeros(n);self.segment=np.zeros(n,int)
        if not n:return
        self.R[0]=np.eye(3);self.M[0]=np.eye(3)
        for i in range(n-1):
            p=points[i];h=(points[i+1]['sampled_us']-p['sampled_us'])/1e6
            if h!=.0005:
                self.R[i+1]=np.eye(3);self.M[i+1]=np.eye(3);self.segment[i+1]=self.segment[i]+1;continue
            w=np.array(p['gyro_body']);f=np.array(p['accel_proper_body']);wm=np.array(p['mean']['gyro_body']);fm=np.array(p['mean']['accel_proper_body']);self.segment[i+1]=self.segment[i]
            self.I[i+1]=self.I[i]+self.R[i]@integrated_rotation(w,h)@f;self.R[i+1]=self.R[i]@exp_rotation(w,h)
            self.J[i+1]=self.J[i]+self.M[i]@integrated_rotation(wm,h)@fm;self.M[i+1]=self.M[i]@exp_rotation(wm,h)
            fn=float(np.linalg.norm(f));self.norm_integral[i+1]=self.norm_integral[i]+h*fn;self.time_norm_integral[i+1]=self.time_norm_integral[i]+h*(p['sampled_us']/1e6)*fn
    def evaluate(self,i,j,u0,u1):
        if i<0 or j<=i or self.segment[i]!=self.segment[j]:raise ValueError('windowcontiguity')
        T=(self.points[j]['sampled_us']-self.points[i]['sampled_us'])/1e6;A=self.R[i].T;B=self.M[i].T;rr=A@self.R[j];rm=B@self.M[j];fi=A@(self.I[j]-self.I[i])/T;fm=B@(self.J[j]-self.J[i])/T;bi=(rr@u1-u0)/T;bm=(rm@u1-u0)/T
        return {'T_s':T,'raw_discrete_average3':fi+bi,'mean_bin_same_raw_endpoint_average3':fm+bm,'raw_force3':fi,'raw_boundary3':bi,'mean_force3':fm,'mean_boundary3':bm,'raw_R_relative_end':rr,'mean_R_relative_end':rm,'paired_vector_difference_norm_m_s2':float(np.linalg.norm(fi+bi-fm-bm)),'paired_norm_difference_m_s2':float(np.linalg.norm(fi+bi)-np.linalg.norm(fm+bm)),'same_noisy_raw_u_endpoints_used':True,'not_continuous_true_COM_error':True}
    def discrete_budget(self,i,j,solution,e0,e1):
        T=solution['T_s'];noise_w=math.sqrt(3)*.125;noise_f=math.sqrt(3)*.025*9.81;t0=self.points[i]['sampled_us']/1e6;fn=self.norm_integral[j]-self.norm_integral[i];tn=self.time_norm_integral[j]-self.time_norm_integral[i];rot_error=noise_w/T*(tn-t0*fn+.0005*fn)
        boundary=(e0['u_error_norm_m_s']+e1['u_error_norm_m_s'])/T;orient_end=min(2.,noise_w*T)*float(np.linalg.norm(e1['u_B3']))/T;radius=noise_f+rot_error+boundary+orient_end;mag=float(np.linalg.norm(solution['raw_discrete_average3']));lo=max(0.,mag-radius);hi=mag+radius;interval_class='overlap'
        if hi<=.25*9.81:interval_class='freefall_like_under_discrete_model_assumptions_only'
        elif lo>=.60*9.81:interval_class='nonfreefall_like_under_discrete_model_assumptions_only'
        return {'proposed_discrete_functional_radius_m_s2':radius,'proposed_discrete_norm_interval_m_s2':[lo,hi],'noise_term_not_divided_by20_or_windowN':noise_f,'gyro_discrete_rotation_uncertainty_m_s2':rot_error,'endpoint_error_m_s2':boundary,'endpoint_orientation_error_m_s2':orient_end,'paired_mean_approximation_radius_to_same_discretefunctional_m_s2':radius+solution['paired_vector_difference_norm_m_s2'],'conditional_interval_NOT_trusted_cue':interval_class,'continuous_physical_quadrature_error_radius':None,'continuous_intrastep_motion_correlation_bound_unavailable':True,'trusted_cue':0,'confidence_cap':.50,'frozen_trusted_threshold':.60,'hardware_binding':False,'common_offset_not_assumed_IID':True,'model_errors_not_assumed_independent_or_canceled':True}

def endpoint_model():
    # Alignment is available in the rawpoint schema, not inferred from queueepoch.
    # Only endpoint aperture-age term is removed; all noise/model errors retained.
    a=replace(BudgetAssumptions(),mean_endpoint_age_s=0.)
    return EndpointModel(Geometry(),assumptions=a)
