"""Sensor-only FSM prototype. All defaults are PROPOSED ENGINEERING values.
No simulator/hardware imports, no contacts/root/world-position inputs, no CAN.
Profiles and q4 references are proposals, NOT an actuator authorization or skill.
"""
from dataclasses import dataclass
from enum import IntEnum, IntFlag
import math
from typing import Optional

ROLE = 'proposed_engineering_not_user_acceptance'

class Mode(IntEnum):
    DISARMED=0; ARMING=1; BALANCE=2; DEGRADED=3; RECOVERY=4
    STEP_APPROACH=5; PRELOAD=6; PUSH_OFF=7; FLIGHT=8; LANDING=9; FAULT_LATCH=10

class Profile(IntEnum):
    INHIBIT=0; ARM_VERIFY=1; BALANCE=2; BALANCE_LIMITED=3; RECOVERY=4
    STEP_SLOW=5; PRELOAD=6; PUSH_OFF=7; FLIGHT=8; LANDING=9

class Phase(IntEnum):
    NONE=0; RECOVERY_UPRIGHT=1; APPROACH_HOLD=2; PRELOAD_RAMP=3
    PUSH_EXTEND=4; FLIGHT_POSE=5; LANDING_COMPLY=6

class Valid(IntFlag):
    AHRS=1; GYRO=2; PROPER_ACC=4; ENCODER_Q=8; ENCODER_QD=16; COMMAND=32
    FORCE_PROXY=64; MOTOR_CURRENT=128; MOTOR_TEMP=256; POWER=512
    FRONT_RANGE=1024; TYPED_STEP=2048
    CLIPPED=1<<28; OVERRUN=1<<29; DRIVER_FAULT=1<<30
CORE = Valid.AHRS|Valid.GYRO|Valid.PROPER_ACC|Valid.ENCODER_Q|Valid.ENCODER_QD|Valid.COMMAND

class ProperReference(IntEnum):
    UNDECLARED=0; IMU_SITE=1; CHASSIS_ORIGIN=2; WHOLE_ROBOT_COM=3; DECLARED_OTHER_POINT=4

class PowerKind(IntEnum):
    UNDECLARED=0; ELECTRICAL_BUS=1; MECHANICAL_ESTIMATE=2

class ObstacleKind(IntEnum):
    UNKNOWN=0; TYPED_STEP=1; OTHER=2

class Support(IntEnum):
    UNCERTAIN=0; SUPPORTED=1; UNSUPPORTED=2; PARTIAL=3

@dataclass(frozen=True, slots=True)
class Command:
    timestamp_s: float
    arm: bool=False
    disarm: bool=False
    estop: bool=False
    jump_event: int=0
    recovery_event: int=0
    reset_event: int=0
    forward_m_s: float=0.
    yaw_rad_s: float=0.

@dataclass(frozen=True, slots=True)
class ForceProxy:
    timestamp_s: float
    normal_N2: tuple
    confidence2: tuple
    provenance: str  # Explicit caller model/proxy source, never a truth binding.

@dataclass(frozen=True, slots=True)
class MotorFeedback:
    timestamp_s: float
    current_A6: Optional[tuple]=None
    temperature_C6: Optional[tuple]=None
    power_W: Optional[float]=None
    power_kind: PowerKind=PowerKind.UNDECLARED

@dataclass(frozen=True, slots=True)
class FrontObservation:
    timestamp_s: float
    observation_id: int
    kind: ObstacleKind
    range_m: Optional[float]=None
    step_height_m: Optional[float]=None
    range_sigma_m: Optional[float]=None
    height_sigma_m: Optional[float]=None

@dataclass(frozen=True, slots=True)
class SensorFrame:
    timestamp_s: float
    valid_bits: Valid
    rpy_rad3: tuple                 # chassis x-forward/y-left/z-up AHRS convention
    omega_rad_s3: tuple             # angular velocity in that chassis frame
    proper_acc_m_s2: tuple
    proper_reference: ProperReference  # Mandatory explicit declaration
    encoder_q4: tuple              # Lhip,Lcrank,Rhip,Rcrank output-side radians
    encoder_qd4: tuple
    command: Command
    force_proxy: Optional[ForceProxy]=None
    motor: Optional[MotorFeedback]=None
    front: Optional[FrontObservation]=None
    lever_com_confidence: float=0.  # Includes moving COM/lever derivatives if claimed
    com_force_model_confidence: float=0.
    schema_version: int=1

@dataclass(frozen=True, slots=True)
class JumpBinding:
    preload_q4: tuple
    push_off_q4: tuple
    flight_q4: tuple
    landing_q4: tuple
    joint_min_q4: tuple
    joint_max_q4: tuple
    binding_id: str

@dataclass(frozen=True, slots=True)
class RecoveryBinding:
    target_q4: tuple
    joint_min_q4: tuple
    joint_max_q4: tuple
    binding_id: str

@dataclass(frozen=True, slots=True)
class Config:
    # Timings, tilt/rate, force and trajectory values are proposed, not acceptance.
    frame_warn_age_s: float=.03
    frame_fault_age_s: float=.12
    command_warn_age_s: float=.05
    command_fault_age_s: float=.2
    future_tolerance_s: float=.002
    missing_required_fault_s: float=.15
    tick_fault_gap_s: float=.2
    optional_age_s: float=.05
    arm_stable_s: float=.20
    arm_timeout_s: float=1.
    resume_stable_s: float=.10
    reset_stable_s: float=.20
    tilt_warn_rad: float=.35
    tilt_fault_rad: float=.90
    stable_tilt_rad: float=.20
    stable_omega_rad_s: float=2.
    omega_warn_rad_s: float=20.
    omega_fault_rad_s: float=40.
    force_on_N: float=25.
    force_off_N: float=8.
    force_min_confidence: float=.8
    force_on_hold_s: float=.05
    force_off_hold_s: float=.03
    contact_max_sample_gap_s: float=.04
    enable_com_freefall_evidence: bool=False
    com_model_min_confidence: float=.9
    com_freefall_max_g: float=.25
    gravity_m_s2: float=9.81
    require_both_support_for_arm: bool=True
    required_motor_bits: Valid=Valid(0)
    current_warn_A6: Optional[tuple]=None
    current_fault_A6: Optional[tuple]=None
    temperature_warn_C: Optional[float]=None
    temperature_fault_C: Optional[float]=None
    power_warn_W: Optional[float]=None
    power_fault_W: Optional[float]=None
    power_limit_kind: PowerKind=PowerKind.UNDECLARED
    electrical_warn_hold_s: float=.02
    allow_manual_jump: bool=False
    allow_auto_step_approach: bool=False
    allow_auto_step_launch: bool=False
    allow_manual_recovery: bool=False
    allow_auto_recovery: bool=False
    execution_context: str='unbound_prototype'
    jump: Optional[JumpBinding]=None
    recovery: Optional[RecoveryBinding]=None
    front_sensor_bound: bool=False
    approach_trigger_m: float=.60
    launch_range_m: float=.20
    max_range_sigma_m: float=.03
    max_height_sigma_m: float=.02
    eligible_step_min_m: Optional[float]=None
    eligible_step_max_m: Optional[float]=None
    max_launch_forward_command_m_s: float=.15
    max_launch_yaw_command_rad_s: float=.3
    approach_timeout_s: float=2.
    preload_duration_s: float=.20
    push_duration_s: float=.10
    takeoff_timeout_s: float=.30
    flight_timeout_s: float=.80
    landing_duration_s: float=.20
    landing_stable_s: float=.10
    landing_timeout_s: float=.80
    recovery_duration_s: float=.50
    recovery_stable_s: float=.20
    recovery_timeout_s: float=2.
    jump_total_timeout_s: float=2.

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            value=getattr(self,name)
            if isinstance(value,float) and not finite(value):raise ValueError(name+' nonfinite')
        allowed_monitor=Valid.MOTOR_CURRENT|Valid.MOTOR_TEMP|Valid.POWER
        if int(self.required_motor_bits)&~int(allowed_monitor):raise ValueError('unsupported required motor bits')
        if self.required_motor_bits&Valid.MOTOR_CURRENT and self.current_warn_A6 is None:raise ValueError('required current monitor limits unbound')
        if self.required_motor_bits&Valid.MOTOR_TEMP and self.temperature_warn_C is None:raise ValueError('required temperature monitor limits unbound')
        if self.required_motor_bits&Valid.POWER and self.power_warn_W is None:raise ValueError('required power monitor limits unbound')
        for name in ('frame_warn_age_s','frame_fault_age_s','command_warn_age_s','command_fault_age_s','missing_required_fault_s','tick_fault_gap_s','optional_age_s','arm_stable_s','arm_timeout_s','resume_stable_s','reset_stable_s','tilt_warn_rad','tilt_fault_rad','stable_tilt_rad','stable_omega_rad_s','omega_warn_rad_s','omega_fault_rad_s','force_on_N','force_on_hold_s','force_off_hold_s','contact_max_sample_gap_s','gravity_m_s2','electrical_warn_hold_s','approach_timeout_s','preload_duration_s','push_duration_s','takeoff_timeout_s','flight_timeout_s','landing_duration_s','landing_stable_s','landing_timeout_s','recovery_duration_s','recovery_stable_s','recovery_timeout_s','jump_total_timeout_s'):
            if not finite(getattr(self,name)) or getattr(self,name)<=0:raise ValueError(name+' must be positive finite proposed value')
        if not 0<=self.future_tolerance_s<self.frame_warn_age_s:raise ValueError('future tolerance')
        if not self.frame_warn_age_s<self.frame_fault_age_s or not self.command_warn_age_s<self.command_fault_age_s:raise ValueError('age tiers')
        if not 0<=self.force_off_N<self.force_on_N:raise ValueError('force hysteresis')
        if not 0<self.stable_tilt_rad<self.tilt_warn_rad<self.tilt_fault_rad<=math.pi:raise ValueError('tilt tiers')
        if not self.omega_warn_rad_s<self.omega_fault_rad_s:raise ValueError('omega tiers')
        if not self.push_duration_s<self.takeoff_timeout_s:raise ValueError('takeoff timeout')
        if not self.landing_duration_s<self.landing_timeout_s or not self.recovery_duration_s<self.recovery_timeout_s:raise ValueError('phase timeout')
        for name in ('force_min_confidence','com_model_min_confidence','com_freefall_max_g'):
            if not finite(getattr(self,name)) or not 0<getattr(self,name)<=1:raise ValueError(name)
        for warn,hard in ((self.temperature_warn_C,self.temperature_fault_C),(self.power_warn_W,self.power_fault_W)):
            if (warn is None)!=(hard is None) or (warn is not None and (not finite(warn) or not finite(hard) or not 0<warn<hard)):raise ValueError('bind both electrical tiers')
        if (self.current_warn_A6 is None)!=(self.current_fault_A6 is None):raise ValueError('bind both current tiers')
        if self.current_warn_A6 is not None:
            if not isinstance(self.current_warn_A6,tuple) or not isinstance(self.current_fault_A6,tuple):raise ValueError('immutable current limit tuples required')
            if not vector(self.current_warn_A6,6) or not vector(self.current_fault_A6,6) or any(not 0<a<b for a,b in zip(self.current_warn_A6,self.current_fault_A6)):raise ValueError('current tiers')
        if self.power_warn_W is not None and self.power_limit_kind==PowerKind.UNDECLARED:raise ValueError('declare power kind, electrical != mechanical')
        enabled=self.allow_manual_jump or self.allow_auto_step_launch or self.allow_manual_recovery or self.allow_auto_recovery
        if enabled and self.execution_context not in ('simulation','synthetic_fixture'):raise ValueError('prototype launch/recovery requires explicit simulation/fixture context')
        if (self.allow_manual_jump or self.allow_auto_step_launch) and self.jump is None:raise ValueError('jump binding absent')
        if (self.allow_manual_recovery or self.allow_auto_recovery) and self.recovery is None:raise ValueError('recovery binding absent')
        for binding in (self.jump,self.recovery):
            if binding is None:continue
            targets=[binding.target_q4] if isinstance(binding,RecoveryBinding) else [binding.preload_q4,binding.push_off_q4,binding.flight_q4,binding.landing_q4]
            if any(not isinstance(v,tuple) for v in targets+[binding.joint_min_q4,binding.joint_max_q4]):raise ValueError('immutable trajectory tuples required')
            if not binding.binding_id or not vector(binding.joint_min_q4,4) or not vector(binding.joint_max_q4,4):raise ValueError('unbound joint envelope')
            if any(a>=b for a,b in zip(binding.joint_min_q4,binding.joint_max_q4)):raise ValueError('joint envelope')
            if any(not vector(q,4) or any(x<a or x>b for x,a,b in zip(q,binding.joint_min_q4,binding.joint_max_q4)) for q in targets):raise ValueError('target outside proposed envelope')
        if self.allow_auto_step_approach or self.allow_auto_step_launch:
            if not self.front_sensor_bound or self.eligible_step_min_m is None or self.eligible_step_max_m is None:raise ValueError('bind typed obstacle sensor and proposed eligible range')
            if not 0<=self.eligible_step_min_m<self.eligible_step_max_m:raise ValueError('step eligibility range')
            if not 0<self.launch_range_m<self.approach_trigger_m or min(self.max_range_sigma_m,self.max_height_sigma_m)<=0:raise ValueError('front uncertainty/range')


def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def vector(v,n):return isinstance(v,(tuple,list)) and len(v)==n and all(finite(x) for x in v)
def norm(v):return math.hypot(*v)
def inside_binding(q,b):return b is not None and vector(q,4) and all(a<=x<=z for x,a,z in zip(q,b.joint_min_q4,b.joint_max_q4))
def tilt(rpy):return math.acos(max(-1.,min(1.,math.cos(rpy[0])*math.cos(rpy[1]))))

@dataclass(frozen=True, slots=True)
class ContactEstimate:
    support: Support=Support.UNCERTAIN
    wheel_state2: tuple=(-1,-1)  # -1 unknown,0proxy-unloaded,1proxy-loaded; NOT truth.
    confidence: float=0.
    source: str='unobserved'
    com_freefall_like: Optional[bool]=None
    reasons: tuple=()

class _Debounce:
    def __init__(self):self.state=-1;self.candidate=-1;self.since=None;self.last=None
    def unknown(self):self.state=-1;self.candidate=-1;self.since=None;self.last=None;return -1
    def update(self,value,stamp,c):
        if self.last is not None:
            if stamp<self.last:return self.unknown()
            if stamp==self.last:return self.state  # Replayed sample cannot earn dwell.
            if stamp-self.last>c.contact_max_sample_gap_s:self.unknown()
        self.last=stamp
        candidate=1 if value>=c.force_on_N else 0 if value<=c.force_off_N else self.state
        if candidate<0:self.candidate=-1;self.since=None;return self.state
        if candidate!=self.candidate:self.candidate=candidate;self.since=stamp
        hold=c.force_on_hold_s if candidate else c.force_off_hold_s
        if stamp-self.since>=hold-1e-12:self.state=candidate
        return self.state

class ContactFusion:
    def __init__(self,c):self.c=c;self.wheels=[_Debounce(),_Debounce()];self.com_since=None;self.com_last=None
    def update(self,f,now):
        c=self.c;states=[-1,-1];conf=[0.,0.];why=[];p=f.force_proxy
        usable=bool(f.valid_bits&Valid.FORCE_PROXY) and isinstance(p,ForceProxy) and finite(p.timestamp_s) and -c.future_tolerance_s<=now-p.timestamp_s<=c.optional_age_s and isinstance(p.provenance,str) and bool(p.provenance) and isinstance(p.normal_N2,(tuple,list)) and isinstance(p.confidence2,(tuple,list)) and len(p.normal_N2)==2 and len(p.confidence2)==2
        for i in range(2):
            ok=usable and finite(p.normal_N2[i]) and p.normal_N2[i]>=0 and finite(p.confidence2[i]) and c.force_min_confidence<=p.confidence2[i]<=1
            if ok:states[i]=self.wheels[i].update(p.normal_N2[i],p.timestamp_s,c);conf[i]=p.confidence2[i]
            else:self.wheels[i].unknown()
        trusted_com=(f.proper_reference==ProperReference.WHOLE_ROBOT_COM and vector(f.proper_acc_m_s2,3) and bool(f.valid_bits&Valid.PROPER_ACC) and finite(f.lever_com_confidence) and finite(f.com_force_model_confidence) and c.com_model_min_confidence<=f.lever_com_confidence<=1 and c.com_model_min_confidence<=f.com_force_model_confidence<=1 and -c.future_tolerance_s<=now-f.timestamp_s<=c.frame_warn_age_s)
        freefall=norm(f.proper_acc_m_s2)<=c.gravity_m_s2*c.com_freefall_max_g if trusted_com else None
        state=Support.SUPPORTED if states==[1,1] else Support.UNSUPPORTED if states==[0,0] else Support.PARTIAL if 1 in states else Support.UNCERTAIN
        source='external_motor_force_proxy' if any(x>=0 for x in states) else 'unobserved'
        confidence=min(conf) if all(x>=0 for x in states) else max(conf) if 1 in states else 0.
        if trusted_com and ((freefall and 1 in states) or (freefall is False and states==[0,0])):
            state=Support.UNCERTAIN;confidence=0.;why.append('FORCE_COM_CONFLICT')
        if c.enable_com_freefall_evidence and freefall is True and state==Support.UNCERTAIN and 'FORCE_COM_CONFLICT' not in why:
            stamp=f.timestamp_s
            if self.com_last is not None and (stamp<self.com_last or stamp-self.com_last>c.contact_max_sample_gap_s):self.com_since=None
            if self.com_last is None or stamp>self.com_last:
                if self.com_since is None:self.com_since=stamp
                self.com_last=stamp
            if self.com_since is not None and stamp-self.com_since>=c.force_off_hold_s-1e-12:
                state=Support.UNSUPPORTED;confidence=min(f.lever_com_confidence,f.com_force_model_confidence);source='declared_COM_freefall_model_only'
        else:self.com_since=None;self.com_last=None
        if state==Support.UNCERTAIN:why.append('CONTACT_UNCERTAIN')
        if not trusted_com:why.append('COM_FORCE_UNOBSERVABLE_FROM_THIS_REFERENCE')
        return ContactEstimate(state,tuple(states),confidence,source,freefall,tuple(why))

@dataclass(frozen=True, slots=True)
class Output:
    mode: Mode
    profile: Profile
    phase: Phase
    phase_fraction: float
    expected_q4: Optional[tuple]
    hard_inhibit: bool
    contact: ContactEstimate
    wheel_no_slip_allowed2: tuple
    reasons: tuple
    latched_faults: tuple
    state_entered_s: float
    threshold_role: str=ROLE
    jump_accepted: bool=False
    recovery_accepted: bool=False

class DetectorFSM:
    def __init__(self,c=Config()):
        self.c=c;self.mode=Mode.DISARMED;self.entered=0.;self.last_now=None;self.last_frame=None;self.armed=False
        self.faults=[];self.loss_since=None;self.good_since=None;self.reset_since=None;self.warning_since={}
        self.fusion=ContactFusion(c);self.contact=ContactEstimate();self.last_arm=False;self.last_jump=0;self.last_recovery=0;self.last_reset=0;self.last_obstacle=0
        self.jump_started=None;self.flight_started=None;self.phase_start_q=(0.,)*4;self.extra=[];self.accept_jump=False;self.accept_recovery=False
    def _enter(self,mode,now,f=None):
        if mode!=self.mode:self.mode=mode;self.entered=now;self.good_since=None
        if f is not None and vector(f.encoder_q4,4):self.phase_start_q=tuple(f.encoder_q4)
    def _fault(self,reasons,now):
        for r in reasons:
            if r not in self.faults:self.faults.append(r)
        self._enter(Mode.FAULT_LATCH,now);self.armed=False;self.reset_since=None
        if finite(now) and (self.last_now is None or now>=self.last_now):self.last_now=now
        return self._out(now,['FAULT_LATCHED'])  # Terminal return: no normal profile fallthrough.
    def _stable(self,condition,now,duration):
        if not condition:self.good_since=None;return False
        if self.good_since is None:self.good_since=now
        return now-self.good_since>=duration-1e-12
    def _health(self,f,now):
        c=self.c;hard=[];soft=[];core_bad=False
        if not isinstance(f,SensorFrame) or not isinstance(f.command,Command):return ['BAD_SCHEMA'],[],True
        if f.schema_version!=1 or not isinstance(f.valid_bits,(int,Valid)) or isinstance(f.valid_bits,bool) or int(f.valid_bits)<0 or int(f.valid_bits)&~int(CORE|Valid.FORCE_PROXY|Valid.MOTOR_CURRENT|Valid.MOTOR_TEMP|Valid.POWER|Valid.FRONT_RANGE|Valid.TYPED_STEP|Valid.CLIPPED|Valid.OVERRUN|Valid.DRIVER_FAULT):return ['BAD_SCHEMA'],[],True
        if any(not isinstance(x,int) or isinstance(x,bool) or x<0 for x in (f.command.jump_event,f.command.recovery_event,f.command.reset_event)) or any(not isinstance(x,bool) for x in (f.command.arm,f.command.disarm,f.command.estop)):return ['BAD_COMMAND'],[],True
        if not all(finite(x) for x in (now,f.timestamp_s,f.command.timestamp_s)):return ['NONFINITE_TIME'],[],True
        if self.last_now is not None and now<self.last_now:hard.append('CLOCK_ROLLBACK')
        if self.last_frame is not None and f.timestamp_s<self.last_frame:hard.append('SAMPLE_TIME_ROLLBACK')
        if self.last_now is not None and self.armed and now-self.last_now>c.tick_fault_gap_s:hard.append('CONTROL_TICK_GAP')
        if now-f.timestamp_s < -c.future_tolerance_s or now-f.command.timestamp_s < -c.future_tolerance_s:hard.append('FUTURE_TIMESTAMP')
        if f.valid_bits&Valid.DRIVER_FAULT:hard.append('DRIVER_FAULT')
        if f.valid_bits&(Valid.CLIPPED|Valid.OVERRUN):soft.append('CLIPPED_OR_OVERRUN');core_bad=True
        if f.valid_bits&CORE!=CORE:soft.append('MISSING_REQUIRED_VALID_BITS');core_bad=True
        for bit,value,n in ((Valid.AHRS,f.rpy_rad3,3),(Valid.GYRO,f.omega_rad_s3,3),(Valid.PROPER_ACC,f.proper_acc_m_s2,3),(Valid.ENCODER_Q,f.encoder_q4,4),(Valid.ENCODER_QD,f.encoder_qd4,4)):
            if f.valid_bits&bit and not vector(value,n):hard.append('NONFINITE_OR_BAD_CORE_SHAPE')
        if f.valid_bits&Valid.COMMAND:
            if not finite(f.command.forward_m_s) or not finite(f.command.yaw_rad_s) or any(not isinstance(x,int) or isinstance(x,bool) or x<0 for x in (f.command.jump_event,f.command.recovery_event,f.command.reset_event)):hard.append('BAD_COMMAND')
        if f.proper_reference not in (ProperReference.IMU_SITE,ProperReference.CHASSIS_ORIGIN,ProperReference.WHOLE_ROBOT_COM,ProperReference.DECLARED_OTHER_POINT):soft.append('PROPER_REFERENCE_UNDECLARED');core_bad=True
        age=now-f.timestamp_s;ca=now-f.command.timestamp_s
        if age>c.frame_warn_age_s or ca>c.command_warn_age_s:soft.append('STALE_CORE_OR_COMMAND');core_bad=True
        if (self.armed or self.mode==Mode.ARMING) and (age>c.frame_fault_age_s or ca>c.command_fault_age_s):hard.append('CORE_OR_COMMAND_LOST')
        if vector(f.rpy_rad3,3) and f.valid_bits&Valid.AHRS:
            angle=tilt(f.rpy_rad3)
            if angle>=c.tilt_fault_rad:hard.append('FALL_HARD')
            elif angle>=c.tilt_warn_rad:soft.append('TILT_WARN')
        if vector(f.omega_rad_s3,3) and f.valid_bits&Valid.GYRO:
            speed=norm(f.omega_rad_s3)
            if speed>=c.omega_fault_rad_s:hard.append('OMEGA_HARD')
            elif speed>=c.omega_warn_rad_s:soft.append('OMEGA_WARN')
        motor=f.motor;bits=c.required_motor_bits
        fresh=isinstance(motor,MotorFeedback) and finite(motor.timestamp_s) and -c.future_tolerance_s<=now-motor.timestamp_s<=c.optional_age_s
        for bit,name,limit in ((Valid.MOTOR_CURRENT,'CURRENT',c.current_warn_A6),(Valid.MOTOR_TEMP,'TEMPERATURE',c.temperature_warn_C),(Valid.POWER,'POWER',c.power_warn_W)):
            if limit is None:self.extra.append(name+'_LIMITS_UNBOUND')
            elif not fresh or not f.valid_bits&bit:self.extra.append(name+'_MONITOR_UNAVAILABLE')
        if bits and (f.valid_bits&bits!=bits or not fresh):soft.append('REQUIRED_MOTOR_MONITOR_LOST');core_bad=True
        checks=((Valid.MOTOR_CURRENT,'CURRENT',None if not fresh else motor.current_A6,c.current_warn_A6,c.current_fault_A6,6),
                (Valid.MOTOR_TEMP,'TEMPERATURE',None if not fresh else motor.temperature_C6,c.temperature_warn_C,c.temperature_fault_C,6))
        for bit,name,data,warn,limit,n in checks:
            active=fresh and bool(f.valid_bits&bit)
            if active and not vector(data,n):hard.append('BAD_'+name+'_FEEDBACK');continue
            exceeded=False
            if active and warn is not None:
                values=[abs(x) for x in data] if name=='CURRENT' else data
                ws=warn if isinstance(warn,(tuple,list)) else (warn,)*n;hs=limit if isinstance(limit,(tuple,list)) else (limit,)*n
                if any(x>=h for x,h in zip(values,hs)):hard.append(name+'_HARD')
                exceeded=any(x>=w for x,w in zip(values,ws))
            self._warn_window(name,exceeded,now,soft)
        pw=fresh and bool(f.valid_bits&Valid.POWER)
        if pw and (not finite(motor.power_W) or motor.power_kind==PowerKind.UNDECLARED):hard.append('BAD_POWER_FEEDBACK')
        exceed=False
        if pw and c.power_warn_W is not None:
            if motor.power_kind!=c.power_limit_kind:soft.append('POWER_KIND_MISMATCH')
            else:
                p=max(0.,motor.power_W)
                if p>=c.power_fault_W:hard.append('POWER_HARD')
                exceed=p>=c.power_warn_W
        self._warn_window('POWER',exceed,now,soft)
        return hard,soft,core_bad
    def _warn_window(self,name,exceeded,now,soft):
        if exceeded:
            self.warning_since.setdefault(name,now)
            if now-self.warning_since[name]>=self.c.electrical_warn_hold_s-1e-12:soft.append(name+'_WARN')
        else:self.warning_since.pop(name,None)
    def _front_eligible(self,f,now):
        c=self.c;p=f.front
        if not c.front_sensor_bound or not isinstance(p,FrontObservation):return False
        required=Valid.FRONT_RANGE|Valid.TYPED_STEP
        if f.valid_bits&required!=required or p.kind!=ObstacleKind.TYPED_STEP or not isinstance(p.observation_id,int) or p.observation_id<=0:return False
        values=(p.timestamp_s,p.range_m,p.step_height_m,p.range_sigma_m,p.height_sigma_m)
        return all(finite(x) for x in values) and -c.future_tolerance_s<=now-p.timestamp_s<=c.optional_age_s and p.range_m>=0 and 0<=p.range_sigma_m<=c.max_range_sigma_m and 0<=p.height_sigma_m<=c.max_height_sigma_m and c.eligible_step_min_m is not None and c.eligible_step_min_m<=p.step_height_m<=c.eligible_step_max_m
    def _launch_ok(self,f):
        return inside_binding(f.encoder_q4,self.c.jump) and self.contact.support==Support.SUPPORTED and tilt(f.rpy_rad3)<=self.c.stable_tilt_rad and norm(f.omega_rad_s3)<=self.c.stable_omega_rad_s and abs(f.command.forward_m_s)<=self.c.max_launch_forward_command_m_s and abs(f.command.yaw_rad_s)<=self.c.max_launch_yaw_command_rad_s
    def _start_jump(self,f,now):
        self.jump_started=now;self.flight_started=None;self.accept_jump=True;self._enter(Mode.PRELOAD,now,f)
    def step(self,f,now):
        self.extra=[];self.accept_jump=False;self.accept_recovery=False
        hard,soft,core_bad=self._health(f,now)
        if not isinstance(f,SensorFrame) or not isinstance(f.command,Command) or not finite(now):return self._fault(hard or ['BAD_ARGUMENT'],self.last_now or 0.)
        if f.command.estop:hard.append('ESTOP')
        if hard:return self._fault(hard,now)
        c=self.c;self.last_now=now;self.last_frame=f.timestamp_s
        self.contact=self.fusion.update(f,now)
        supported=self.contact.support==Support.SUPPORTED or (not c.require_both_support_for_arm and self.contact.support==Support.PARTIAL)
        upright=vector(f.rpy_rad3,3) and vector(f.omega_rad_s3,3) and tilt(f.rpy_rad3)<=c.stable_tilt_rad and norm(f.omega_rad_s3)<=c.stable_omega_rad_s
        new_jump=f.command.jump_event>self.last_jump;new_rec=f.command.recovery_event>self.last_recovery;new_reset=f.command.reset_event>self.last_reset
        if not core_bad:
            self.last_jump=max(self.last_jump,f.command.jump_event);self.last_recovery=max(self.last_recovery,f.command.recovery_event);self.last_reset=max(self.last_reset,f.command.reset_event)
        if self.mode==Mode.FAULT_LATCH:
            ready=not core_bad and not soft and supported and upright
            if ready:
                if self.reset_since is None:self.reset_since=now
            else:self.reset_since=None
            if new_reset and f.command.disarm and not f.command.arm and self.reset_since is not None and now-self.reset_since>=c.reset_stable_s-1e-12:
                self.faults=[];self.reset_since=None;self.loss_since=None;self.last_arm=False;self.jump_started=None;self.flight_started=None;self._enter(Mode.DISARMED,now)
                return self._out(now,['EXPLICIT_FAULT_RESET_TO_DISARMED'])
            return self._out(now,['FAULT_LATCHED'])  # No branch below may override this.
        if f.command.disarm:
            self.armed=False;self.last_arm=False;self.loss_since=None;self.jump_started=None;self.flight_started=None;self._enter(Mode.DISARMED,now)
            return self._out(now,['EXPLICIT_DISARM'])
        arm_edge=f.command.arm and not self.last_arm;self.last_arm=f.command.arm
        if core_bad and self.mode!=Mode.DISARMED:
            if self.loss_since is None:self.loss_since=now
            if now-self.loss_since>=c.missing_required_fault_s-1e-12:return self._fault(['REQUIRED_INPUT_LOSS_TIMEOUT'],now)
        else:self.loss_since=None
        if self.mode==Mode.DISARMED:
            if arm_edge and not core_bad and not soft:self._enter(Mode.ARMING,now,f)
            return self._out(now,soft+(['ARM_REQUEST_NOT_READY'] if arm_edge and (core_bad or soft) else []))
        if self.mode==Mode.ARMING:
            if self._stable(not core_bad and not soft and supported and upright,now,c.arm_stable_s):self.armed=True;self._enter(Mode.BALANCE,now)
            elif now-self.entered>=c.arm_timeout_s-1e-12:self._enter(Mode.DEGRADED,now);self.extra.append('ARMING_TIMEOUT_DISARM_REARM_REQUIRED')
            return self._out(now,soft)
        if self.jump_started is not None and now-self.jump_started>=c.jump_total_timeout_s-1e-12:return self._fault(['JUMP_TOTAL_TIMEOUT'],now)
        if self.flight_started is not None and now-self.flight_started>=c.flight_timeout_s-1e-12 and self.mode in (Mode.FLIGHT,Mode.DEGRADED):return self._fault(['FLIGHT_TIMEOUT'],now)
        recoverable_soft=bool(soft) and all(x in ('TILT_WARN','OMEGA_WARN') for x in soft)
        recovery_request=(new_rec and c.allow_manual_recovery) or (c.allow_auto_recovery and 'TILT_WARN' in soft)
        if not core_bad and supported and inside_binding(f.encoder_q4,c.recovery) and recovery_request and (not soft or recoverable_soft) and self.armed and self.mode in (Mode.BALANCE,Mode.DEGRADED):
            self.accept_recovery=True;self._enter(Mode.RECOVERY,now,f);return self._out(now,soft)
        if core_bad or (soft and not (self.mode==Mode.RECOVERY and recoverable_soft)):
            if self.mode in (Mode.PRELOAD,Mode.PUSH_OFF,Mode.STEP_APPROACH):self.jump_started=None
            self._enter(Mode.DEGRADED,now)
            return self._out(now,soft+(['CORE_REQUIRED_UNAVAILABLE'] if core_bad else []),inhibit=core_bad)
        if self.mode==Mode.RECOVERY:
            if now-self.entered>=c.recovery_timeout_s-1e-12:return self._fault(['RECOVERY_TIMEOUT'],now)
            if self._stable(supported and upright,now,c.recovery_stable_s) and now-self.entered>=c.recovery_duration_s-1e-12:self._enter(Mode.BALANCE,now)
            return self._out(now,[])
        if self.mode==Mode.STEP_APPROACH:
            if self.contact.support!=Support.SUPPORTED:self._enter(Mode.DEGRADED,now);return self._out(now,['STEP_SUPPORT_UNCERTAIN'])
            if not self._front_eligible(f,now):self._enter(Mode.DEGRADED,now);return self._out(now,['TYPED_OBSTACLE_LOST_OR_UNCERTAIN'])
            if now-self.entered>=c.approach_timeout_s-1e-12:self._enter(Mode.DEGRADED,now);return self._out(now,['STEP_APPROACH_TIMEOUT'])
            if c.allow_auto_step_launch and f.front.range_m<=c.launch_range_m and self._launch_ok(f):self._start_jump(f,now)
            return self._out(now,[])
        if self.mode==Mode.PRELOAD:
            if self.contact.support!=Support.SUPPORTED:self.jump_started=None;self._enter(Mode.DEGRADED,now);return self._out(now,['PRELOAD_SUPPORT_UNCERTAIN_OR_LOST'])
            if now-self.entered>=c.preload_duration_s-1e-12:self._enter(Mode.PUSH_OFF,now,f)
            return self._out(now,[])
        if self.mode==Mode.PUSH_OFF:
            if self.contact.support==Support.UNSUPPORTED:self.flight_started=now;self._enter(Mode.FLIGHT,now,f)
            elif now-self.entered>=c.takeoff_timeout_s-1e-12:self.jump_started=None;self._enter(Mode.DEGRADED,now);return self._out(now,['TAKEOFF_NOT_OBSERVED_TIMEOUT'])
            elif self.contact.support==Support.UNCERTAIN:self._enter(Mode.DEGRADED,now);return self._out(now,['TAKEOFF_UNCERTAIN'])
            return self._out(now,[])
        if self.mode==Mode.FLIGHT:
            if self.contact.support in (Support.SUPPORTED,Support.PARTIAL):self._enter(Mode.LANDING,now,f)
            elif self.contact.support==Support.UNCERTAIN:self._enter(Mode.DEGRADED,now)
            return self._out(now,[])
        if self.mode==Mode.LANDING:
            if self.contact.support==Support.UNCERTAIN:self._enter(Mode.DEGRADED,now);return self._out(now,['LANDING_SUPPORT_UNCERTAIN'])
            if now-self.entered>=c.landing_timeout_s-1e-12:return self._fault(['LANDING_TIMEOUT'],now)
            if self.contact.support==Support.UNSUPPORTED:self._enter(Mode.FLIGHT,now,f)
            elif self._stable(supported and upright,now,c.landing_stable_s) and now-self.entered>=c.landing_duration_s-1e-12:
                self.jump_started=None;self.flight_started=None;self._enter(Mode.BALANCE,now)
            return self._out(now,[])
        if not self.armed:return self._out(now,['DISARM_REARM_REQUIRED'],inhibit=True)
        if self.contact.support==Support.UNSUPPORTED:
            if self.flight_started is None:self.flight_started=now
            self._enter(Mode.FLIGHT,now,f);return self._out(now,['PROXY_UNLOADED_NOT_GROUND_TRUTH'])
        if self.contact.support in (Support.UNCERTAIN,Support.PARTIAL):self._enter(Mode.DEGRADED,now);return self._out(now,['CONTACT_UNCERTAIN_OR_PARTIAL'])
        if new_rec:
            if c.allow_manual_recovery and inside_binding(f.encoder_q4,c.recovery):self.accept_recovery=True;self._enter(Mode.RECOVERY,now,f);return self._out(now,[])
            self.extra.append('RECOVERY_UNBOUND_OR_DISABLED')
        if new_jump:
            if self.mode==Mode.BALANCE and c.allow_manual_jump and c.jump is not None and self._launch_ok(f):self._start_jump(f,now);return self._out(now,[])
            self.extra.append('JUMP_UNBOUND_DISABLED_OR_NOT_READY')
        if self.mode==Mode.DEGRADED:
            if self.flight_started is not None:self._enter(Mode.LANDING,now,f)
            elif self._stable(upright,now,c.resume_stable_s):self._enter(Mode.BALANCE,now)
            return self._out(now,[])
        if c.allow_auto_step_approach and self._front_eligible(f,now) and f.front.observation_id>self.last_obstacle and f.front.range_m<=c.approach_trigger_m:
            self.last_obstacle=f.front.observation_id;self._enter(Mode.STEP_APPROACH,now,f)
        return self._out(now,[])
    def _out(self,now,reasons,inhibit=False):
        mode=self.mode;c=self.c;phase=Phase.NONE;profile=Profile.INHIBIT;q=None;u=0.
        hard=inhibit or mode in (Mode.DISARMED,Mode.ARMING,Mode.FAULT_LATCH) or not self.armed
        why=list(dict.fromkeys(list(reasons)+self.extra+list(self.contact.reasons)))
        if mode==Mode.ARMING:profile=Profile.ARM_VERIFY
        elif not hard:
            profile={Mode.BALANCE:Profile.BALANCE,Mode.DEGRADED:Profile.BALANCE_LIMITED,Mode.RECOVERY:Profile.RECOVERY,Mode.STEP_APPROACH:Profile.STEP_SLOW,Mode.PRELOAD:Profile.PRELOAD,Mode.PUSH_OFF:Profile.PUSH_OFF,Mode.FLIGHT:Profile.FLIGHT,Mode.LANDING:Profile.LANDING}[mode]
            target=None;duration=1.
            if mode==Mode.RECOVERY and c.recovery is not None:phase=Phase.RECOVERY_UPRIGHT;target=c.recovery.target_q4;duration=c.recovery_duration_s
            elif mode==Mode.STEP_APPROACH:phase=Phase.APPROACH_HOLD
            elif mode in (Mode.PRELOAD,Mode.PUSH_OFF,Mode.FLIGHT,Mode.LANDING):
                if c.jump is None:hard=True;profile=Profile.INHIBIT;why.append('TRAJECTORY_UNBOUND')
                else:
                    phase,target,duration={Mode.PRELOAD:(Phase.PRELOAD_RAMP,c.jump.preload_q4,c.preload_duration_s),Mode.PUSH_OFF:(Phase.PUSH_EXTEND,c.jump.push_off_q4,c.push_duration_s),Mode.FLIGHT:(Phase.FLIGHT_POSE,c.jump.flight_q4,c.flight_timeout_s),Mode.LANDING:(Phase.LANDING_COMPLY,c.jump.landing_q4,c.landing_duration_s)}[mode]
            if target is not None:
                u=max(0.,min(1.,(now-self.entered)/duration));blend=u*u*u*(10.+u*(-15.+6.*u));q=tuple(a+(b-a)*blend for a,b in zip(self.phase_start_q,target))
                if not vector(q,4):return self._fault(['NONFINITE_TRAJECTORY_REFERENCE'],now)
        if hard:profile=Profile.INHIBIT;phase=Phase.NONE;q=None;u=0.
        usable=tuple(x==1 and not hard and self.contact.support in (Support.SUPPORTED,Support.PARTIAL) and mode not in (Mode.FLIGHT,Mode.PUSH_OFF) for x in self.contact.wheel_state2)
        return Output(mode,profile,phase,u,q,hard,self.contact,usable,tuple(why),tuple(self.faults),self.entered,ROLE,self.accept_jump and not hard,self.accept_recovery and not hard)
