"""Interactive experimental mini-hop, not270mm clearance/fullDR qualification.
Reuse the real MINIHOP_LANDING_V3 -> OBSERVER_V2 -> MINIHOP_V1 torque laws.
No MuJoCo/contact/terrain/DR/root-state reads, assists, teleports or gain fitting.
Call prepare(estimator, now) BEFORE every sensor/update; Space uses request ONCE
per key-down edge. command returns None only when idle, never on latched fault.
"""
from pathlib import Path
import json
import math
import numpy as np
from MINIHOP_LANDING_V3.controller import MiniHop
from MINIHOP_V1.controller import absolute_q, EFFORT, LEG, WHEEL

ROOT=Path(__file__).resolve().parents[1]

def _arrays(gain):
    g=dict(gain)
    for k in ('q','tau','K','A','B','Ad','Bd','P','Q','R'):
        if k in g:g[k]=np.array(g[k],dtype=float,copy=True)
    return g

def _public_gain(path, key=None):
    d=json.loads(path.read_text(encoding='utf-8'))
    return _arrays(d['gains'][key] if key else d.get('gain',d))

def _smooth(u):
    u=float(np.clip(u,0.,1.));return u*u*(3.-2.*u)

class JumpAction:
    CROUCH_S=.50
    RETURN_BLEND_S=.25

    def __init__(self,gain,geometry,ground_controller):
        self.gain=_arrays(gain);self.geometry=geometry;self.ground_controller=ground_controller
        self.crouch=_public_gain(ROOT/'JUMP270_V1/GAIN_BANK.json','crouch')
        self.push_end=_public_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')
        self.reset()

    def reset(self):
        self.phase='IDLE';self.active=False;self.fault_reason=None;self.last_request_rejection=None
        self._hop=None;self._estimator=None;self._last_time=None;self._request_time=None
        self._q_from=None;self._return_from=None;self._return_time=None;self.log={}

    @staticmethod
    def _check(now,e,packet):
        now=float(now);packet.validate()
        x=np.asarray(e.state14,float);q=np.asarray(packet.joint_pos4,float);v=np.asarray(packet.joint_vel4,float)
        omega=np.asarray(e.omega_body,float)
        if (not math.isfinite(now)or now<0 or x.shape!=(14,)or q.shape!=(4,)or v.shape!=(4,)
            or omega.shape!=(3,)or not all(np.isfinite(z).all()for z in(x,q,v,omega))
            or not math.isfinite(float(e.roll))or not math.isfinite(float(e.sensor_age_s))
            or not 0.<=float(e.sensor_age_s)<=.05 or not math.isfinite(float(e.estimated_time_s))
            or abs(now-float(e.estimated_time_s))>.0500001):
            raise ValueError('jump sensor/time contract')
        return now,x,q

    def request(self,now,estimate,packet):
        if self.active or self.fault_reason:
            self.last_request_rejection='busy_or_latched_fault';return False
        try:
            now,x,q=self._check(now,estimate,packet)
            if abs(x[2])>.15 or abs(float(estimate.roll))>.15 or abs(x[7])>.2:
                self.last_request_rejection='requires low-speed upright sensor state';return False
            config=dict(operator_enable=True,trigger_time_s=now+self.CROUCH_S,push_for_s=.14,
                predicted_air_after_push_s=.35,capture_blend_s=.10,push_kp=300.,push_kd=3.,
                wheel_push_Nm=0.,max_trigger_speed_m_s=.2,observer_quarantine_after_push_s=.50,
                landing_transition_enable=True,landing_transition_s=.20)
            # Existing tested mini-hop family, with this player's OWN nominal gain
            # as final landing equilibrium. No SPR coefficients/mechanical constants.
            self._hop=MiniHop(self.crouch,self.push_end,self.geometry,config,landing_gain=self.gain)
            self._hop.ctrl.ref[0]=float(x[0]);self._hop.ctrl.ref[1]=float(x[1])
            self._request_time=now;self._q_from=q.copy();self._last_time=None
            self._return_from=None;self._return_time=None
            self.phase='CROUCH';self.active=True;self.last_request_rejection=None;self.log={}
            return True
        except Exception as exc:
            self.last_request_rejection=str(exc);return False

    def prepare(self,estimator,now):
        self._estimator=estimator
        if self.fault_reason:
            estimator.wheel_measurement_enabled=False
            estimator.ground_kinematic_constraint_enabled=False
            estimator.accel_correction=0.
        elif self.active:
            self._hop.prepare_estimator(estimator,float(now))
        else:
            estimator.wheel_measurement_enabled=True
            estimator.ground_kinematic_constraint_enabled=True
            estimator.accel_correction=1.5

    def command(self,estimate,packet,now,ground_tau):
        if self.fault_reason:return np.zeros(6)
        if not self.active:return None
        try:
            now,x,q=self._check(now,estimate,packet)
            base=np.asarray(ground_tau,float)
            if base.shape!=(6,)or not np.isfinite(base).all():raise ValueError('ground_tau must be finite row6')
            if self._estimator is None or self._estimator.q is None:raise ValueError('prepare(estimator,now) required before update/command')
            if self._last_time is not None and not 0.<now-self._last_time<=.0500001:raise ValueError('jump command order/gap')
            self._last_time=now;h=self._hop
            if now<h.trigger:
                # Smooth compression using the SAME existing ground-PD/LQR path.
                # This is interpolation of public equilibria, not a root assist.
                s=_smooth((now-self._request_time)/self.CROUCH_S)
                qa=(1.-s)*self._q_from+s*h.q_start
                h.ctrl.K=(1.-s)*h.K1+s*h.K0
                h.ctrl.tau_eq=(1.-s)*h.ff1+s*h.ff0
                h.ctrl.eq=h.eq0.copy();h.ctrl.eq[3:7]=[qa[0],qa[1]-qa[0],qa[2],qa[3]-qa[2]]
                h.ctrl.ref[3:7]=h.ctrl.eq[3:7]
            elif not h.launched:
                h.ctrl.K=h.K0.copy();h.ctrl.tau_eq=h.ff0.copy();h.ctrl.eq=h.eq0.copy()
                h.ctrl.ref[3:7]=h.eq0[3:7]
            tau=np.asarray(h.command(estimate,packet,now,self._estimator.q,forward=0.),float)
            if h.fault:raise ValueError(h.log.get('fault','existing mini-hop fault'))
            if now<h.trigger:
                self.phase='CROUCH';tau=tau.copy();tau[WHEEL]=base[WHEEL]
            elif now<h.trigger+h.push:self.phase='PUSH'
            elif now<h.trigger+h.push+h.air:self.phase='PREDICTED_FLIGHT'
            else:self.phase='LANDING'
            # Finish only after timer quarantine and the existing nominal landing
            # schedule. This is NOT a sensed contact/landing declaration.
            return_at=h.trigger+h.push+max(h.quarantine,h.air+h.landing_seconds)+.35
            if now>=return_at:
                if self._return_time is None:self._return_time=now;self._return_from=tau.copy()
                self.phase='RETURN_BALANCE';s=_smooth((now-self._return_time)/self.RETURN_BLEND_S)
                tau=(1.-s)*self._return_from+s*base
                if s>=1.:
                    self.active=False;self.phase='IDLE'
                    # Caller recaptures ONLY ground ref[:2]/park_error on this
                    # active->idle edge. Never reset estimator or overwrite root.
            tau=np.clip(tau,-EFFORT,EFFORT)
            if tau.shape!=(6,)or not np.isfinite(tau).all():raise ValueError('nonfinite jump torque')
            self.log=dict(h.log,interactive_phase=self.phase,experimental_jump=True,
                phase_source='operator_timer_not_contact',contact_or_flight_trusted=False,
                return_to_player_nominal=True)
            return tau.copy()
        except Exception as exc:
            self.fault_reason=str(exc);self.phase='INHIBIT';self.active=False
            self.log=dict(fault=self.fault_reason,phase='INHIBIT',contact_or_flight_trusted=False)
            return np.zeros(6)
