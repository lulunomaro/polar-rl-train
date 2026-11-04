"""UNTESTED moving mini-hop candidate; old jump.py/its trial stay unchanged.
Capture forward/yaw on an explicit key-down request; keep them through recovery.
Existing public MOD4 mini-hop legs, limits and Plant PD/DC remain unchanged.
No terrain/contact/root truth inputs or world-state writes. No moving-speed,
all-terrain/270mm/DR qualification. Latest user priority suspends new physics.
"""
import copy
import math
import numpy as np
from RM_FPS_PLAYER_V1.jump import JumpAction as StationaryJumpAction, _smooth
from MINIHOP_LANDING_V3.controller import MiniHop
from MINIHOP_V1.controller import EFFORT, WHEEL

class MovingJumpAction(StationaryJumpAction):
    # Candidate command envelope, NOT demonstrated achievable jump speeds.
    COMMAND_LIMIT_M_S=1.0
    YAW_COMMAND_LIMIT_RAD_S=1.0
    # Same public model no-load limit/envelope used by ground_controller_v4.
    # This is a sampled soft spin guard, not a driver-rate speed certificate.
    MODEL_WHEEL_NOLOAD_RAD_S=55.3557
    VALIDATED_MOVING_JUMP_SPEEDS=()

    def reset(self):
        super().reset()
        self.commanded_forward=0.;self.commanded_yaw=0.;self.commanded_yaw_rate=0.
        self.commanded_heading=0.;self.measured_speed_at_request=0.
        self._heading_at_request=0.;self._wheel_spin_at_request=np.zeros(2)
        self._air_spin_guard_active=False

    def request(self,now,estimate,packet,forward=None,yaw_rate=None):
        if self.active or self.fault_reason:
            self.last_request_rejection='busy_or_latched_fault';return False
        try:
            now,x,q=self._check(now,estimate,packet)
            # Three-argument compatibility captures measured movement; the new
            # runtime should supply explicit current operator forward/yaw commands.
            v=float(x[7]if forward is None else forward)
            w=float(x[8]if yaw_rate is None else yaw_rate)
            if not math.isfinite(v)or not math.isfinite(w):raise ValueError('nonfinite moving jump command')
            if abs(v)>self.COMMAND_LIMIT_M_S or abs(w)>self.YAW_COMMAND_LIMIT_RAD_S:
                raise ValueError('candidate jump envelope is |v|<=1m/s, |yaw|<=1rad/s; 2m/s not validated')
            if abs(x[2])>.15 or abs(float(estimate.roll))>.15:
                raise ValueError('jump requires upright pitch/roll <=.15rad')
            if abs(x[7])>1.4 or abs(float(x[7])-v)>.40:
                raise ValueError('wait for measured speed to track captured command within .40m/s')
            config=dict(operator_enable=True,trigger_time_s=now+self.CROUCH_S,push_for_s=.14,
                predicted_air_after_push_s=.35,capture_blend_s=.10,push_kp=300.,push_kd=3.,
                wheel_push_Nm=0.,max_trigger_speed_m_s=1.4,
                observer_quarantine_after_push_s=.50,landing_transition_enable=True,landing_transition_s=.20)
            h=MiniHop(self.crouch,self.push_end,self.geometry,config,landing_gain=self.gain)
            h.ctrl.ref[0]=float(x[0]);h.ctrl.ref[1]=0.
            # Do not restart the internal landing shaper at zero while already
            # translating. Forward is carried into every existing ground command.
            h.ctrl.shaper.v=float(x[7]);h.ctrl.shaper.a=0.;h.ctrl.shaper.w=0.
            h.ctrl.ref[7]=float(x[7]);h.ctrl.ref[8]=0.
            self._hop=h;self._request_time=now;self._q_from=q.copy();self._last_time=None
            self._return_from=None;self._return_time=None
            self.commanded_forward=v;self.commanded_yaw=w;self.commanded_yaw_rate=w
            self.measured_speed_at_request=float(x[7]);self._heading_at_request=float(x[1])
            self.commanded_heading=float(x[1]);self._wheel_spin_at_request=np.asarray(packet.wheel_vel2,float).copy()
            self.phase='MOVING_CROUCH';self.active=True;self.last_request_rejection=None;self.log={}
            return True
        except Exception as exc:
            self.last_request_rejection=str(exc);return False

    def prepare(self,estimator,now):
        super().prepare(estimator,now)
        if self.active and not self.fault_reason:
            h=self._hop;t=float(now)
            # Liftoff may occur BEFORE the end of push. Quarantine this entire
            # potential decontact window rather than letting spin rewrite vx.
            if h.trigger<=t<h.trigger+h.push+h.quarantine:
                estimator.wheel_measurement_enabled=False
                estimator.ground_kinematic_constraint_enabled=False

    def _heading_view(self,e,now):
        local=copy.copy(e);x=np.asarray(e.state14,float).copy()
        self.commanded_heading=self._heading_at_request+self.commanded_yaw*(now-self._request_time)
        error=float(x[1])-self.commanded_heading
        x[1]=math.atan2(math.sin(error),math.cos(error))
        x[8]-=self.commanded_yaw
        local.state14=x
        return local

    def _bounded_air_wheels(self,tau,packet):
        # Preserve the rolling spin carried into flight, not a zero-speed wheel
        # request. Original attitude/yaw reaction-wheel law remains the source;
        # only reject outward torque at the existing .9*N model envelope.
        out=np.asarray(tau,float).copy();spin=np.asarray(packet.wheel_vel2,float)
        if spin.shape!=(2,)or not np.isfinite(spin).all():raise ValueError('invalid reaction-wheel measurement')
        bound=.9*self.MODEL_WHEEL_NOLOAD_RAD_S;self._air_spin_guard_active=False
        for i,j in enumerate(WHEEL):
            if abs(float(spin[i]))>=bound and float(spin[i])*float(out[j])>0.:
                out[j]=0.;self._air_spin_guard_active=True
        return np.clip(out,-EFFORT,EFFORT)

    def command(self,estimate,packet,now,ground_tau):
        if self.fault_reason:return np.zeros(6)
        if not self.active:return None
        try:
            now,x,q=self._check(now,estimate,packet);base=np.asarray(ground_tau,float)
            if base.shape!=(6,)or not np.isfinite(base).all():raise ValueError('finite ground_tau row6 required')
            if self._estimator is None or self._estimator.q is None:raise ValueError('prepare before sensor/update/command required')
            if self._last_time is not None and not 0.<now-self._last_time<=.0500001:raise ValueError('moving jump command order/gap')
            self._last_time=now;h=self._hop;self._air_spin_guard_active=False
            if now<h.trigger:
                s=_smooth((now-self._request_time)/self.CROUCH_S)
                qa=(1.-s)*self._q_from+s*h.q_start
                h.ctrl.K=(1.-s)*h.K1+s*h.K0;h.ctrl.tau_eq=(1.-s)*h.ff1+s*h.ff0
                h.ctrl.eq=h.eq0.copy();h.ctrl.eq[3:7]=[qa[0],qa[1]-qa[0],qa[2],qa[3]-qa[2]]
                h.ctrl.ref[3:7]=h.ctrl.eq[3:7]
            elif not h.launched:
                h.ctrl.K=h.K0.copy();h.ctrl.tau_eq=h.ff0.copy();h.ctrl.eq=h.eq0.copy();h.ctrl.ref[3:7]=h.eq0[3:7]
            # Desired heading is a moving local reference, not the old absolute
            # yaw-zero command. Actual quaternion/gyro and estimator are untouched.
            local=self._heading_view(estimate,now);h.ctrl.ref[1]=0.
            tau=np.asarray(h.command(local,packet,now,self._estimator.q,forward=self.commanded_forward),float)
            if h.fault:raise ValueError(h.log.get('fault','existing mini-hop fault'))
            if now<h.trigger:
                self.phase='MOVING_CROUCH';tau=tau.copy();tau[WHEEL]=base[WHEEL]
            elif now<h.trigger+h.push:
                self.phase='MOVING_PUSH';tau=tau.copy();tau[WHEEL]=base[WHEEL]
            elif now<h.trigger+h.push+h.air:
                self.phase='MOVING_PREDICTED_FLIGHT';tau=self._bounded_air_wheels(tau,packet)
            else:
                self.phase='MOVING_LANDING'
                if now<h.trigger+h.push+h.quarantine:tau=self._bounded_air_wheels(tau,packet)
            return_at=h.trigger+h.push+max(h.quarantine,h.air+h.landing_seconds)+.35
            if now>=return_at:
                if self._return_time is None:self._return_time=now;self._return_from=tau.copy()
                self.phase='RETURN_MOVING_BALANCE';s=_smooth((now-self._return_time)/self.RETURN_BLEND_S)
                tau=(1.-s)*self._return_from+s*base
                if s>=1.:self.active=False;self.phase='IDLE'
            tau=np.clip(tau,-EFFORT,EFFORT)
            if tau.shape!=(6,)or not np.isfinite(tau).all():raise ValueError('nonfinite moving jump torque')
            self.log=dict(h.log,interactive_phase=self.phase,experimental_moving_jump=True,
                commanded_forward_m_s=self.commanded_forward,commanded_yaw_rad_s=self.commanded_yaw,
                commanded_heading_rad=self.commanded_heading,measured_speed_at_request=self.measured_speed_at_request,
                wheel_spin_at_request_rad_s=self._wheel_spin_at_request.tolist(),air_spin_soft_guard=self._air_spin_guard_active,
                phase_source='operator_timer_not_contact',contact_or_flight_trusted=False,
                moving_jump_physics_tests=0,validated_moving_jump_speeds=[],return_to_player_nominal=True)
            return tau.copy()
        except Exception as exc:
            self.fault_reason=str(exc);self.phase='INHIBIT';self.active=False
            self.log=dict(fault=self.fault_reason,phase='INHIBIT',contact_or_flight_trusted=False)
            return np.zeros(6)

# Optional compatibility alias; parent runtime explicitly imports MovingJumpAction.
JumpAction=MovingJumpAction
