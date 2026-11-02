"""Sensor-only NOMINAL contact-force proxy, NOT force sensing/full RNE.
Fixed public parameters only. No episode model, DR values, contacts/rootGT API.
The published normal is chassis-Z compression, not an observed terrain normal.
"""
from dataclasses import dataclass
from enum import IntEnum,IntFlag
import math
import numpy as np
try:
    from .nominal_model import NominalModel,ModelDomainError,vec,wrap,XML_SHA
except ImportError:
    from nominal_model import NominalModel,ModelDomainError,vec,wrap,XML_SHA

ROLE='proposed_engineering_nominal_model_not_measured_calibration'
class Valid(IntFlag):
    Q4=1; QD4=2; TAU4=4; PROPER_ROOT=8; OMEGA=16; ALPHA=32
ALL_VALID=Valid.Q4|Valid.QD4|Valid.TAU4|Valid.PROPER_ROOT|Valid.OMEGA|Valid.ALPHA
class TorqueDomain(IntEnum):
    UNKNOWN=0; MEASURED_JOINT_OUTPUT_NM=1; CURRENT_CONVERTED_JOINT_OUTPUT_NM=2
    NOMINAL_DESIGN_OUTPUT_FIXTURE=3

@dataclass(frozen=True,slots=True)
class SensorInput:
    timestamp_s: float
    imu_timestamp_s: float
    torque_timestamp_s: float
    valid_bits: Valid
    encoder_q4: tuple
    encoder_qd4: tuple
    output_motor_tau4: tuple
    proper_root_B_m_s2: tuple
    omega_B_rad_s: tuple
    alpha_B_rad_s2: tuple
    torque_domain: TorqueDomain
    torque_binding_id: str
    torque_sign_verified: bool=False
    measured_torque_calibration_confirmed: bool=False
    proper_reference: str='unbound' # Exactly 'chassis_origin' required.
    torque_confidence4: tuple=(0.,0.,0.,0.)
    torque_sigma_Nm4: tuple=(None,None,None,None)
    encoder_calibration_confidence: float=0.
    proper_confidence: float=0.
    omega_confidence: float=0.
    alpha_confidence: float=0.
    encoder_qd_sigma4: tuple=(None,None,None,None)

@dataclass(frozen=True,slots=True)
class Config:
    execution_context: str='unbound_prototype'
    allow_nominal_design_fixture: bool=False
    max_age_s: float=.03
    max_channel_skew_s: float=.003
    min_dt_s: float=.001
    max_dt_s: float=.04
    history_samples_required: int=3
    q_consistency_tol_rad: float=.03
    min_input_confidence: float=.5
    nominal_model_confidence_cap: float=.55
    min_publish_confidence: float=.20
    qdd_soft_rad_s2: float=10.
    qdd_hard_rad_s2: float=80.
    qdd_noise_hard_rad_s2: float=50.
    omega_soft_rad_s: float=4.
    omega_hard_rad_s: float=20.
    alpha_soft_rad_s2: float=20.
    alpha_hard_rad_s2: float=100.
    proper_soft_m_s2: float=20.
    proper_hard_m_s2: float=80.
    condition_soft: float=10.
    condition_hard: float=100.
    mass_uncertainty_fraction: float=.15
    spring_uncertainty_fraction: float=.15
    unmodeled_generalized_sigma_Nm: float=1.
    normal_relative_uncertainty_floor_N: float=10.
    roundoff_negative_normal_N: float=1e-6
    def __post_init__(self):
        if self.allow_nominal_design_fixture and self.execution_context not in ('synthetic_fixture','simulation'):raise ValueError('design effort is not measured hardware torque; explicit fixture/simulation context required')
        if not 0<self.min_dt_s<self.max_dt_s or not 0<self.max_channel_skew_s<self.max_age_s or self.history_samples_required<2:raise ValueError('time/history settings')
        if not 0<self.min_input_confidence<=1 or not 0<self.min_publish_confidence<=self.nominal_model_confidence_cap<=1:raise ValueError('confidence settings')
        for a,b in [(self.qdd_soft_rad_s2,self.qdd_hard_rad_s2),(self.omega_soft_rad_s,self.omega_hard_rad_s),(self.alpha_soft_rad_s2,self.alpha_hard_rad_s2),(self.proper_soft_m_s2,self.proper_hard_m_s2),(self.condition_soft,self.condition_hard)]:
            if not 0<a<b:raise ValueError('proposed dynamic/condition tiers')
        for name in self.__dataclass_fields__:
            value=getattr(self,name)
            if isinstance(value,float) and (not math.isfinite(value) or value<0):raise ValueError(name+' finite nonnegative proposed setting')
        if self.normal_relative_uncertainty_floor_N<=0 or self.qdd_noise_hard_rad_s2<=0:raise ValueError('uncertainty scale')

@dataclass(frozen=True,slots=True)
class Result:
    timestamp_s: float
    normal_proxy_N2: tuple
    confidence2: tuple
    normal_sigma_N2: tuple
    model_force_body_xz_N2: tuple
    reasons2: tuple
    common_reasons: tuple
    debug: dict
    provenance: str='nominal_model_nottruth'
    normal_axis: str='chassis_Z_compression_proxy_not_observed_ground_normal'
    model_source_SHA: str=XML_SHA
    threshold_role: str=ROLE

def finite(x):return isinstance(x,(int,float,np.floating,np.integer)) and not isinstance(x,bool) and math.isfinite(x)
def confid(x):return finite(x) and 0<=x<=1

def clean_debug(x):
    if isinstance(x,dict):return {k:clean_debug(v) for k,v in x.items()}
    if isinstance(x,(tuple,list,np.ndarray)):return [clean_debug(v) for v in x]
    if isinstance(x,(float,np.floating)) and not math.isfinite(x):return None
    if isinstance(x,np.generic):return x.item()
    return x

def taper(value,soft,hard):
    if value>=hard:return 0.
    return 1. if value<=soft else soft/value

class ContactProxy:
    def __init__(self,c=Config()):
        self.c=c;self.model=NominalModel();self.previous=None;self.good_samples=0;self._history_updated_this_call=False
    def _unknown(self,t,reason,debug=None):
        if not self._history_updated_this_call:self.good_samples=0
        return Result(t if finite(t) else 0.,(None,None),(0.,0.),(None,None),(None,None),((reason,),(reason,)),(reason,),clean_debug(debug or {}))
    def step(self,s,now_s):
        self._history_updated_this_call=False
        c=self.c
        if not isinstance(s,SensorInput):return self._unknown(now_s,'BAD_SENSOR_SCHEMA')
        if not all(finite(x) for x in (now_s,s.timestamp_s,s.imu_timestamp_s,s.torque_timestamp_s)):return self._unknown(now_s,'NONFINITE_TIME')
        t=s.timestamp_s
        if not isinstance(s.valid_bits,(int,Valid)) or isinstance(s.valid_bits,bool) or int(s.valid_bits)!=int(ALL_VALID):return self._unknown(t,'REQUIRED_VALIDITY_UNAVAILABLE')
        stamps=(t,s.imu_timestamp_s,s.torque_timestamp_s)
        if any(x>now_s+1e-9 or now_s-x>c.max_age_s for x in stamps) or max(stamps)-min(stamps)>c.max_channel_skew_s:return self._unknown(t,'STALE_FUTURE_OR_UNALIGNED_CHANNELS')
        if s.proper_reference!='chassis_origin':return self._unknown(t,'PROPER_ROOT_REFERENCE_UNBOUND')
        try:
            q=vec(s.encoder_q4,4,'q4');v=vec(s.encoder_qd4,4,'qd4');proper=vec(s.proper_root_B_m_s2,3,'proper_root');w=vec(s.omega_B_rad_s,3,'omega');alpha=vec(s.alpha_B_rad_s2,3,'alpha')
            self.model.joint_values(q)  # Public geometry/ranges only, before any derivative history.
        except ModelDomainError as exc:return self._unknown(t,'NONFINITE_OR_SHAPE:'+str(exc))
        old=self.previous
        if old is not None:
            dt=t-old[0]
            if dt<c.min_dt_s:return self._unknown(t,'SAMPLE_TIME_REPLAY_OR_ROLLBACK')
            if dt>c.max_dt_s:
                self.previous=(t,q.copy(),v.copy());return self._unknown(t,'SAMPLE_GAP_RESTART_DERIVATIVE_WARMUP')
            mismatch=np.max(abs(wrap(q-old[1])-(v+old[2])*.5*dt))
            if mismatch>c.q_consistency_tol_rad:
                self.previous=(t,q.copy(),v.copy());return self._unknown(t,'ENCODER_TIMING_OR_ZERO_OFFSET_JUMP',{'consistency_error_rad':float(mismatch)})
            qdd=(v-old[2])/dt
        else:dt=None;qdd=None
        self.previous=(t,q.copy(),v.copy());self.good_samples+=1;self._history_updated_this_call=True
        if qdd is None or self.good_samples<c.history_samples_required:
            # Do not substitute zero acceleration as a measured contact estimate.
            return Result(t,(None,None),(0.,0.),(None,None),(None,None),(('DERIVATIVE_WARMUP',),)*2,('DERIVATIVE_WARMUP',),{'good_samples':self.good_samples})
        qualities=(s.encoder_calibration_confidence,s.proper_confidence,s.omega_confidence,s.alpha_confidence)
        if not all(confid(x) and x>=c.min_input_confidence for x in qualities):return self._unknown(t,'ENCODER_OR_IMU_CALIBRATION_ALPHA_UNTRUSTED')
        if not isinstance(s.output_motor_tau4,(tuple,list)) or len(s.output_motor_tau4)!=4 or not isinstance(s.torque_confidence4,(tuple,list)) or len(s.torque_confidence4)!=4 or not isinstance(s.torque_sigma_Nm4,(tuple,list)) or len(s.torque_sigma_Nm4)!=4:return self._unknown(t,'TORQUE_FEEDBACK_SHAPE')
        common=['PUBLIC_NOMINAL_PARAMETERS_NOT_EPISODE_DR','CHASSIS_Z_NOT_TRUE_TERRAIN_NORMAL','ONLY_WHEEL_CENTER_LOAD_PATH_ASSUMED_GUIDE_NONWHEEL_SUPPORT_UNOBSERVED','WHEEL_SPIN_DRIVE_REACTION_CONTACT_MOMENT_UNOBSERVED','NOT_COMPLETE_RNE_OR_MEASURED_FOOT_FORCE']
        if not isinstance(s.torque_binding_id,str) or not s.torque_binding_id or s.torque_sign_verified is not True:return self._unknown(t,'TORQUE_DOMAIN_SIGN_OR_BINDING_UNKNOWN')
        if s.torque_domain==TorqueDomain.NOMINAL_DESIGN_OUTPUT_FIXTURE:
            if not c.allow_nominal_design_fixture:return self._unknown(t,'DESIGN_EFFORT_NOT_MEASURED_CALIBRATION')
            common.append('DESIGN_TORQUE_FIXTURE_NOT_MEASURED_CALIBRATION')
        elif s.torque_domain not in (TorqueDomain.MEASURED_JOINT_OUTPUT_NM,TorqueDomain.CURRENT_CONVERTED_JOINT_OUTPUT_NM) or s.measured_torque_calibration_confirmed is not True:
            return self._unknown(t,'MEASURED_OUTPUT_TORQUE_CALIBRATION_UNBOUND')
        levels=[float(np.max(abs(qdd))),math.hypot(*w),math.hypot(*alpha),math.hypot(*proper)]
        factors=[taper(levels[0],c.qdd_soft_rad_s2,c.qdd_hard_rad_s2),taper(levels[1],c.omega_soft_rad_s,c.omega_hard_rad_s),taper(levels[2],c.alpha_soft_rad_s2,c.alpha_hard_rad_s2),taper(levels[3],c.proper_soft_m_s2,c.proper_hard_m_s2)]
        if min(factors)<=0:return self._unknown(t,'DYNAMIC_LEGDD_OMEGA_ALPHA_OR_PROPER_UNTRUSTED',{'levels':levels,'qdd_estimate4':qdd.tolist()})
        noise_factor=1.;qdd_noise=None
        if isinstance(s.encoder_qd_sigma4,(tuple,list)) and len(s.encoder_qd_sigma4)==4 and all(finite(x) and x>=0 for x in s.encoder_qd_sigma4):
            qdd_noise=math.sqrt(2)*max(s.encoder_qd_sigma4)/dt
            if qdd_noise>c.qdd_noise_hard_rad_s2:return self._unknown(t,'LEG_DD_NOISE_UNTRUSTED',{'qdd_noise_rad_s2':qdd_noise})
            noise_factor=1./(1.+qdd_noise/max(c.qdd_soft_rad_s2,1e-12))
        else:noise_factor=.5;common.append('QD_NOISE_UNBOUND_CONFIDENCE_REDUCED')
        if min(factors)<1:common.append('DYNAMIC_APPROXIMATION_CONFIDENCE_REDUCED')
        try:terms=self.model.terms(q,v,qdd,proper,w,alpha)
        except (ModelDomainError,ValueError,np.linalg.LinAlgError,FloatingPointError) as exc:return self._unknown(t,'MODEL_DOMAIN_OR_DIFFERENTIATION:'+str(exc))
        normals=[];confidence=[];sigmas=[];model_forces=[];why2=[];cond2=[]
        for i,J in enumerate(terms['Jwheel_xz2']):
            why=[];indices=(2*i,2*i+1);cond=float(np.linalg.cond(J.T));cond2.append(cond)
            tau=[s.output_motor_tau4[k] for k in indices];tc=[s.torque_confidence4[k] for k in indices];ts=[s.torque_sigma_Nm4[k] for k in indices]
            if not all(finite(x) for x in tau) or not all(confid(x) and x>=c.min_input_confidence for x in tc) or not all(finite(x) and x>=0 for x in ts):
                normals.append(None);confidence.append(0.);sigmas.append(None);model_forces.append(None);why2.append(('TORQUE_UNKNOWN_LOW_CONFIDENCE_OR_SIGMA_UNBOUND',));continue
            if not math.isfinite(cond) or cond>=c.condition_hard:
                normals.append(None);confidence.append(0.);sigmas.append(None);model_forces.append(None);why2.append(('SINGULAR_OR_ILL_CONDITIONED_FORCE_MAP',));continue
            k=slice(2*i,2*i+2);rhs=terms['load4'][k]-np.array(tau)-terms['tauGas4'][k]-terms['tauOtherPassive4'][k]
            try:
                with np.errstate(over='raise',invalid='raise',divide='raise'):
                    F=np.linalg.solve(J.T,rhs)
                if not np.isfinite(F).all():raise FloatingPointError('nonfinite force solve')
            except (FloatingPointError,np.linalg.LinAlgError):
                normals.append(None);confidence.append(0.);sigmas.append(None);model_forces.append(None);why2.append(('NUMERIC_FORCE_SOLVE_UNAVAILABLE',));continue
            model_forces.append(tuple(map(float,F)))
            # Explicit proposed uncertainty envelope. Does NOT alter nominal masses
            # or springs using hidden randomized parameters. Not calibrated probability.
            sigma_tau=np.hypot(np.hypot(np.array(ts),c.mass_uncertainty_fraction*np.abs(terms['load4'][k])),np.hypot(c.spring_uncertainty_fraction*np.abs(terms['tauGas4'][k]),c.unmodeled_generalized_sigma_Nm))
            inv=np.linalg.inv(J.T)
            with np.errstate(over='ignore',invalid='ignore'):sigma=math.hypot(*(inv[1]*sigma_tau))
            sigmas.append(sigma if math.isfinite(sigma) else None)
            conf=min(*qualities,*tc,c.nominal_model_confidence_cap)*min(factors)*noise_factor*taper(cond,c.condition_soft,c.condition_hard)
            conf/=1.+sigma/(max(0.,float(F[1]))+c.normal_relative_uncertainty_floor_N)
            if cond>c.condition_soft:why.append('JACOBIAN_CONDITION_CONFIDENCE_REDUCED')
            if not np.isfinite(F).all() or not math.isfinite(sigma) or not math.isfinite(conf):why.append('NONFINITE_FORCE_OR_UNCERTAINTY');conf=0.
            elif F[1]<-c.roundoff_negative_normal_N:why.append('NEGATIVE_COMPRESSION_NOT_SUPPORT');conf=0.
            if conf<c.min_publish_confidence:why.append('CONFIDENCE_BELOW_PUBLISH_NOT_ZERO_FORCE');normal=None
            else:normal=max(0.,float(F[1])) # Only tiny declared roundoff-negative tolerance.
            normals.append(normal);confidence.append(max(0.,min(1.,conf)));why2.append(tuple(why))
        debug={'qdd_estimate4':qdd.tolist(),'qdd_noise_rad_s2':qdd_noise,'dynamic_levels':levels,'dynamic_factors':factors,'load4':terms['load4'].tolist(),'tauGas4':terms['tauGas4'].tolist(),'tauOtherPassive4':terms['tauOtherPassive4'].tolist(),'gas_slide2':terms['gas_slide2'].tolist(),'gas_force_scalar_N2':terms['gas_scalar_force_N2'].tolist(),'condition2':cond2,'normal_uncertainty_is_proposed_not_empirical':True}
        return Result(t,tuple(normals),tuple(confidence),tuple(sigmas),tuple(model_forces),tuple(why2),tuple(common),debug)
