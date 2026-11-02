"""Public nominal moving-COM specific-force prototype. No SDK/runtime truth.
All bounds/confidences are declared/proposed, not contact identity or probability.
Wheel eccentricity is computed from public MCI; absent spin states stay uncertain.
"""
from dataclasses import dataclass
from enum import IntEnum,IntFlag
import math
import numpy as np
try:
    from ..CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel,ModelDomainError,vec,axis_R,wrap,XML_SHA
except ImportError:
    from CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel,ModelDomainError,vec,axis_R,wrap,XML_SHA

ROLE='proposed_engineering_public_nominal_not_contact_or_measured_calibration'
class Valid(IntFlag):Q4=1;QD4=2;PROPER_ORIGIN=4;OMEGA=8;ALPHA=16;QDD4=32
CORE=Valid.Q4|Valid.QD4|Valid.PROPER_ORIGIN|Valid.OMEGA
class Cue(IntEnum):UNCERTAIN=0;COM_FREEFALL_LIKE=1;COM_NONFREEFALL_LIKE=2

@dataclass(frozen=True,slots=True)
class Sample:
    timestamp_s: float
    valid_bits: Valid
    q4: tuple
    qd4: tuple
    proper_origin_B3: tuple
    omega_B3: tuple
    proper_reference: str='unbound'
    alpha_B3: object=None
    qdd4: object=None
    q_error_rad4: object=None
    qd_error_rad_s4: object=None
    qdd_error_rad_s24: object=None
    proper_error_m_s23: object=None
    omega_error_rad_s3: object=None
    alpha_error_rad_s23: object=None
    encoder_calibration_confidence: float=0.
    imu_frame_calibration_confidence: float=0.
    derivative_confidence: float=0.
    wheel_angle2: object=None       # Relative joint-output angle about authored axis
    wheel_rate2: object=None
    wheel_acc2: object=None
    wheel_angle_error_rad2: object=None
    wheel_rate_error_rad_s2: object=None
    wheel_acc_error_rad_s22: object=None
    wheel_rate_abs_bound_rad_s2: object=None
    wheel_acc_abs_bound_rad_s22: object=None
    wheel_binding_id: str=''

@dataclass(frozen=True,slots=True)
class Config:
    max_age_s: float=.03
    min_dt_s: float=.001
    max_dt_s: float=.04
    motion_difference_dt_s: float=1e-4
    q_difference_rad: float=1e-5
    allow_sensor_difference: bool=True
    qdd_jerk_abs_bound_rad_s34: object=None
    angular_jerk_abs_bound_rad_s33: object=None
    model_confidence_cap: float=.60
    min_cue_confidence: float=.60
    gravity_reference_m_s2: float=9.81
    freefall_max_g: float=.25
    nonfreefall_min_g: float=.60
    nominal_COM_position_error_m: float=.005
    nominal_COM_velocity_error_m_s: float=.02
    nominal_COM_acceleration_error_m_s2: float=.2
    def __post_init__(self):
        if not 0<self.min_dt_s<self.max_dt_s or not 0<self.max_age_s or not 0<self.motion_difference_dt_s<.01 or not 0<self.q_difference_rad<.01:raise ValueError('time/difference settings')
        if not 0<self.min_cue_confidence<=1 or not 0<self.model_confidence_cap<=1 or not 0<self.freefall_max_g<self.nonfreefall_min_g:raise ValueError('cue settings')
        for n in self.__dataclass_fields__:
            v=getattr(self,n)
            if isinstance(v,float) and (not math.isfinite(v) or v<0):raise ValueError(n)
        for value,size in ((self.qdd_jerk_abs_bound_rad_s34,4),(self.angular_jerk_abs_bound_rad_s33,3)):
            if value is not None and bound(value,size) is None:raise ValueError('declared jerk bound')

def finite(x):return isinstance(x,(int,float,np.integer,np.floating)) and not isinstance(x,bool) and math.isfinite(x)
def bound(x,n):
    if x is None:return None
    try:a=vec(x,n,'declared error bound')
    except ModelDomainError:return None
    return a if np.all(a>=0) else None

def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list,np.ndarray)):return [clean(v) for v in x]
    if isinstance(x,(float,np.floating)) and not math.isfinite(x):return None
    if isinstance(x,np.generic):return x.item()
    return x

class Geometry:
    def __init__(self,c=Config()):
        self.c=c;self.base=NominalModel();self.total_mass=float(self.base.mass.sum());self.weights=self.base.mass/self.total_mass
        self.wheels=[]
        for side,bid in zip(('left','right'),self.base.wheel_ids):
            j=self.base.joints[self.base.joint_index[side+'_wheel_spin']];axis=np.array(j['axis'],float);axis/=np.linalg.norm(axis);pivot=np.array(j['pos_m']);com=np.array(self.base.bodies[bid]['com_local_m']);v=com-pivot;rad=v-axis*np.dot(axis,v)
            assert not any(b['parent']==side+'_wheel' for b in self.base.bodies),'Only leaf wheel correction is valid for this pinned model'
            self.wheels.append({'side':side,'body_id':bid,'axis_local':axis,'pivot_local':pivot,'com_local':com,'radial_local':rad,'radial_radius_m':float(np.linalg.norm(rad)),'weight':float(self.weights[bid])})
    def com(self,q4,phi2):
        q=vec(q4,4,'q4');phi=vec(phi2,2,'wheel angle');p=self.base.fk(q);r=np.sum(self.weights[:,None]*p['com_B'],axis=0)
        for wheel,angle in zip(self.wheels,phi):
            delta=(axis_R(wheel['axis_local'],angle)-np.eye(3))@(wheel['com_local']-wheel['pivot_local']);r+=wheel['weight']*p['R_body_B'][wheel['body_id']]@delta
        return r
    def jacobians(self,q4,phi2):
        h=self.c.q_difference_rad;J=np.zeros((3,4))
        for i in range(4):
            d=np.zeros(4);d[i]=h;J[:,i]=(self.com(np.asarray(q4)+d,phi2)-self.com(np.asarray(q4)-d,phi2))/(2*h)
        p=self.base.fk(q4);W=np.zeros((3,2))
        for i,(wheel,angle) in enumerate(zip(self.wheels,phi2)):
            radial=axis_R(wheel['axis_local'],angle)@(wheel['com_local']-wheel['pivot_local']);W[:,i]=wheel['weight']*p['R_body_B'][wheel['body_id']]@np.cross(wheel['axis_local'],radial)
        return J,W
    def motion(self,q4,qd4,qdd4,phi2=(0.,0.),wheel_rate2=(0.,0.),wheel_acc2=(0.,0.)):
        q=vec(q4,4,'q4');v=vec(qd4,4,'qd4');a=vec(qdd4,4,'qdd4');p=vec(phi2,2,'wheel angle');w=vec(wheel_rate2,2,'wheel rate');b=vec(wheel_acc2,2,'wheel acceleration');dt=self.c.motion_difference_dt_s
        r=self.com(q,p);rp=self.com(q+dt*v+.5*dt*dt*a,p+dt*w+.5*dt*dt*b);rm=self.com(q-dt*v+.5*dt*dt*a,p-dt*w+.5*dt*dt*b)
        rd=(rp-rm)/(2*dt);rdd=(rp-2*r+rm)/(dt*dt);J,W=self.jacobians(q,p);accel=J@a+W@b
        if not all(np.isfinite(x).all() for x in (r,rd,rdd,J,W)):raise ModelDomainError('nonfinite COM motion computation')
        return {'r_B':r,'rDot_B':rd,'rDDot_B':rdd,'Jq':J,'Jwheel':W,'acceleration_linear_part_B':accel,'convective_part_B':rdd-accel}
    def leg_wheel_angular_motion(self,q,v,a):
        dt=self.c.motion_difference_dt_s;out=[]
        for i,side in enumerate(('left','right')):
            def theta(z):
                h,c=z[2*i:2*i+2];return h+self.base.leg_values(h,c,side)['knee']
            t=theta(q);tp=theta(q+dt*v+.5*dt*dt*a);tm=theta(q-dt*v+.5*dt*dt*a)
            out.append((float(wrap(tp-tm))/(2*dt),float(wrap(tp-t)+wrap(tm-t))/(dt*dt)))
        return out

@dataclass(frozen=True,slots=True)
class Output:
    timestamp_s: float
    proper_COM_B3: object
    nominal_corrected_estimate_B3: object
    cue: Cue
    confidence: float
    proposed_error_radius_m_s2: object
    proposed_norm_interval_m_s2: object
    r_COM_B3: object
    rDot_COM_B3: object
    rDDot_COM_B3: object
    terms: dict
    reasons: tuple
    derivative_metadata: dict
    wheel_missing_bound: dict
    provenance: str='public_nominal_moving_COM_nottruth_not_contact_identity'
    threshold_role: str=ROLE

class MovingCOM:
    def __init__(self,c=Config()):self.c=c;self.geometry=Geometry(c);self.previous=None
    def _unknown(self,t,reason,details=None):return Output(t if finite(t) else 0.,None,None,Cue.UNCERTAIN,0.,None,None,None,None,None,{},(reason,),clean(details or {}),{})
    def _wheel(self,s,q,v,a):
        reasons=[];vals=[];errs=[];bound_ok=True
        supplied=(s.wheel_angle2,s.wheel_rate2,s.wheel_acc2);eb=(s.wheel_angle_error_rad2,s.wheel_rate_error_rad_s2,s.wheel_acc_error_rad_s22)
        if s.wheel_binding_id:
            for value,error in zip(supplied,eb):
                try:val=vec(value,2,'wheel sensor') if value is not None else np.zeros(2)
                except ModelDomainError:return None
                vals.append(val);errs.append(bound(error,2) if value is not None else None)
        else:vals=[np.zeros(2) for _ in range(3)];errs=[None]*3;reasons.append('WHEEL_STATE_BINDING_UNBOUND')
        rate_abs=bound(s.wheel_rate_abs_bound_rad_s2,2);acc_abs=bound(s.wheel_acc_abs_bound_rad_s22,2);angular=self.geometry.leg_wheel_angular_motion(q,v,a)
        dr=drd=drdd=0.;detail=[]
        for i,wheel in enumerate(self.geometry.wheels):
            mass_radius=wheel['weight']*wheel['radial_radius_m'];phase_error=2. if errs[0] is None else min(2.,float(errs[0][i]))
            ve=None if errs[1] is None else float(errs[1][i]);ae=None if errs[2] is None else float(errs[2][i])
            if ve is None and rate_abs is not None:ve=float(rate_abs[i]+abs(vals[1][i]))
            if ae is None and acc_abs is not None:ae=float(acc_abs[i]+abs(vals[2][i]))
            if ve is None or ae is None:bound_ok=False;reasons.append('WHEEL_RATE_OR_ACCELERATION_BOUND_UNAVAILABLE')
            dpos=mass_radius*phase_error;dr+=dpos;wl,al=map(abs,angular[i]);wv=abs(vals[1][i]);av=abs(vals[2][i])
            if ve is not None and ae is not None:
                dvel=dpos*(wl+wv+ve)+mass_radius*ve
                dacc=dpos*(al+av+ae+(wl+wv+ve)**2)+mass_radius*(ae+2*(wl+wv)*ve+ve*ve)
                drd+=dvel;drdd+=dacc
            else:dvel=dacc=None
            detail.append({'side':wheel['side'],'nominal_radial_COM_eccentricity_m':wheel['radial_radius_m'],'mass_fraction':wheel['weight'],'COM_position_error_radius_m':dpos,'COM_velocity_missing_radius_m_s':dvel,'COM_accel_missing_radius_m_s2':dacc,'declared_rate_error_bound_rad_s':ve,'declared_accel_error_bound_rad_s2':ae})
        if any(x is None for x in errs):reasons.append('WHEEL_NOT_ASSUMED_BALANCED_MISSING_STATE_BOUND_ONLY')
        return vals,(dr,drd if bound_ok else None,drdd if bound_ok else None),{'finite_declared_nominal_wheel_bound':bound_ok,'wheels':detail,'geometric_bound_not_actual_imbalance_calibration':True},reasons
    def update(self,s,now_s):
        c=self.c
        if not isinstance(s,Sample) or not finite(now_s):return self._unknown(now_s,'BAD_SCHEMA_OR_TIME')
        if not finite(s.timestamp_s) or s.timestamp_s>now_s+1e-9 or now_s-s.timestamp_s>c.max_age_s:return self._unknown(now_s,'STALE_FUTURE_OR_NONFINITE_TIMESTAMP')
        if s.proper_reference!='chassis_origin' or not isinstance(s.valid_bits,(int,Valid)) or isinstance(s.valid_bits,bool) or int(s.valid_bits)<0 or int(s.valid_bits)&~int(CORE|Valid.ALPHA|Valid.QDD4) or s.valid_bits&CORE!=CORE:return self._unknown(s.timestamp_s,'REFERENCE_OR_REQUIRED_VALID_BITS_UNBOUND')
        try:q=vec(s.q4,4,'q4');v=vec(s.qd4,4,'qd4');proper=vec(s.proper_origin_B3,3,'proper origin');omega=vec(s.omega_B3,3,'omega');self.geometry.base.joint_values(q)
        except ModelDomainError as exc:return self._unknown(s.timestamp_s,'INPUT_MODEL_DOMAIN:'+str(exc))
        t=s.timestamp_s;old=self.previous;reasons=[];deriv={};qde=bound(s.qd_error_rad_s4,4);we=bound(s.omega_error_rad_s3,3)
        if old is not None and t<=old[0]:return self._unknown(t,'DUPLICATE_OR_OUT_OF_ORDER_SENSOR_TIME')
        dt=None if old is None else t-old[0];self.previous=(t,v.copy(),omega.copy(),qde,we)
        explicit_qdd=s.qdd4 is not None and bool(s.valid_bits&Valid.QDD4);explicit_alpha=s.alpha_B3 is not None and bool(s.valid_bits&Valid.ALPHA)
        try:
            if explicit_qdd:qdd=vec(s.qdd4,4,'qdd');qdd_e=bound(s.qdd_error_rad_s24,4);deriv['qdd_source']='explicit_sensor_estimator'
            elif c.allow_sensor_difference and dt is not None and c.min_dt_s<=dt<=c.max_dt_s:
                qdd=(v-old[1])/dt;jerk=bound(c.qdd_jerk_abs_bound_rad_s34,4);qdd_e=None if qde is None or old[3] is None or jerk is None else (qde+old[3])/dt+jerk*dt/2;deriv.update(qdd_source='sensor_qdot_two_point_difference',qdd_midpoint_lag_s=dt/2)
            else:return self._unknown(t,'QDD_SENSOR_DERIVATIVE_UNAVAILABLE_OR_WARMUP')
            if explicit_alpha:alpha=vec(s.alpha_B3,3,'alpha');alpha_e=bound(s.alpha_error_rad_s23,3);deriv['alpha_source']='explicit_sensor_estimator'
            elif c.allow_sensor_difference and dt is not None and c.min_dt_s<=dt<=c.max_dt_s:
                alpha=(omega-old[2])/dt;jerk=bound(c.angular_jerk_abs_bound_rad_s33,3);alpha_e=None if we is None or old[4] is None or jerk is None else (we+old[4])/dt+jerk*dt/2;deriv.update(alpha_source='sensor_gyro_two_point_difference',alpha_midpoint_lag_s=dt/2)
            else:return self._unknown(t,'ALPHA_SENSOR_DERIVATIVE_UNAVAILABLE_OR_WARMUP')
            qdd=vec(qdd,4,'derived qdd');alpha=vec(alpha,3,'derived alpha')
        except ModelDomainError as exc:return self._unknown(t,'DERIVATIVE_NONFINITE:'+str(exc))
        if not explicit_qdd or not explicit_alpha:reasons.append('DIFFERENCED_DERIVATIVE_HAS_LAG_AND_NOISE_NOT_CURRENT_TRUTH')
        if qdd_e is None or alpha_e is None:reasons.append('DERIVATIVE_NOISE_OR_JERK_TIME_ALIGNMENT_BOUND_UNAVAILABLE')
        try:wheel=self._wheel(s,q,v,qdd)
        except (ModelDomainError,ValueError,FloatingPointError) as exc:return self._unknown(t,'WHEEL_BOUND_MODEL_DOMAIN:'+str(exc))
        if wheel is None:return self._unknown(t,'WHEEL_SENSOR_SHAPE_OR_NONFINITE')
        wvals,werr,wmeta,wreasons=wheel;reasons+=wreasons
        try:
            motion=self.geometry.motion(q,v,qdd,*wvals);r=motion['r_B'];rd=motion['rDot_B'];rdd=motion['rDDot_B'];tangential=np.cross(alpha,r);centripetal=np.cross(omega,np.cross(omega,r));coriolis=2*np.cross(omega,rd);corrected=proper+tangential+centripetal+coriolis+rdd
            if not np.isfinite(corrected).all():raise ModelDomainError('nonfinite corrected vector')
        except (ModelDomainError,ValueError,FloatingPointError) as exc:return self._unknown(t,'COM_DIFFERENTIATION_DOMAIN:'+str(exc))
        qe=bound(s.q_error_rad4,4);pe=bound(s.proper_error_m_s23,3);bound_complete=all(x is not None for x in (qe,qde,qdd_e,pe,we,alpha_e,werr[1],werr[2]))
        conf_values=(s.encoder_calibration_confidence,s.imu_frame_calibration_confidence,s.derivative_confidence)
        conf=min(c.model_confidence_cap,*conf_values) if all(finite(x) and 0<=x<=1 for x in conf_values) else 0.
        if not explicit_qdd or not explicit_alpha:conf*=.5
        radius=None;interval=None;cue=Cue.UNCERTAIN
        if bound_complete:
            J=motion['Jq'];column=np.linalg.norm(J,axis=0);rerr=float(column@qe)+c.nominal_COM_position_error_m+werr[0]
            rderr=float(column@qde)+c.nominal_COM_velocity_error_m_s+werr[1]
            # Local nominal linearization plus explicit model-motion radius; no
            # claim this is a calibrated global interval over D0/D2/nonrigidity.
            rdderr=float(column@qdd_e)+c.nominal_COM_acceleration_error_m_s2+werr[2]
            ome=math.hypot(*we);ale=math.hypot(*alpha_e);wn=math.hypot(*omega);an=math.hypot(*alpha)
            radius=math.hypot(*pe)+(an+ale)*rerr+ale*math.hypot(*r)+(wn+ome)**2*rerr+(2*wn*ome+ome*ome)*math.hypot(*r)+2*(wn+ome)*rderr+2*ome*math.hypot(*rd)+rdderr
            magnitude=math.hypot(*corrected);interval=(max(0.,magnitude-radius),magnitude+radius)
            if not math.isfinite(radius):radius=None;interval=None;conf=0.;reasons.append('ERROR_PROPAGATION_NONFINITE')
            elif conf>=c.min_cue_confidence:
                if interval[1]<=c.freefall_max_g*c.gravity_reference_m_s2:cue=Cue.COM_FREEFALL_LIKE
                elif interval[0]>=c.nonfreefall_min_g*c.gravity_reference_m_s2:cue=Cue.COM_NONFREEFALL_LIKE
                else:reasons.append('SPECIFIC_FORCE_INTERVAL_AMBIGUOUS')
        else:conf=min(conf,.49);reasons.append('COMPENSATION_ERROR_RADIUS_UNBOUND')
        if conf<c.min_cue_confidence:reasons.append('CONFIDENCE_BELOW_PROPOSED_CUE_THRESHOLD')
        reasons+=['PUBLIC_NOMINAL_MCI_NOT_EPISODE_DR','COM_FREEFALL_CUE_NOT_CONTACT_IDENTITY_OR_ALL_SURFACE_AIR','LOCAL_ENGINEERING_ERROR_SCALE_NOT_VALIDATED_PROBABILITY_OR_GLOBAL_BOUND']
        deriv.update(qdd4=qdd.tolist(),alpha_B3=alpha.tolist(),qdd_error_bound4=None if qdd_e is None else qdd_e.tolist(),alpha_error_bound3=None if alpha_e is None else alpha_e.tolist())
        terms={'proper_origin_B3':proper.tolist(),'alpha_cross_r_B3':tangential.tolist(),'omega_cross_omega_cross_r_B3':centripetal.tolist(),'two_omega_cross_rDot_B3':coriolis.tolist(),'rDDot_B3':rdd.tolist(),'rDDot_linear_acceleration_B3':motion['acceleration_linear_part_B'].tolist(),'rDDot_convective_B3':motion['convective_part_B'].tolist()}
        valid_vector=bound_complete and conf>0
        return Output(t,tuple(map(float,corrected)) if valid_vector else None,tuple(map(float,corrected)),cue,float(max(0.,min(1.,conf))),radius,interval,tuple(r),tuple(rd),tuple(rdd),clean(terms),tuple(dict.fromkeys(reasons)),clean(deriv),clean(wmeta))
