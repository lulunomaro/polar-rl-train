"""Estimated-only TRAIN air leg reference plus continuous capture anchor.

No plant, contact, DR, truth or physics imports. This is not an airborne/contact
permission or stability certificate. Parent fixed .25/.04/1 and asymmetric domain.
"""
import math
from numbers import Real
import numpy as np
from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop as PositionMiniHop

PITCH_K=.25
PITCH_RATE_K=.04
H_MIN=-.10
H_MAX=.03
RATE=1.
PERIOD=.01

class MiniHop(PositionMiniHop):
    def __init__(self,start_gain,end_gain,geometry,config,landing_gain):
        super().__init__(start_gain,end_gain,geometry,config,landing_gain=landing_gain)
        self.air_pitch_ref_enable=self.c.get('air_pitch_ref_enable',False)
        if type(self.air_pitch_ref_enable)is not bool:raise ValueError('air_pitch_ref_enable must be bool')
        if self.air_pitch_ref_enable and not self.landing_enable:
            raise ValueError('enabled air reference requires declared V3 landing transition for continuous anchor')
        self.air_h_rad=0.
        self.air_goal_rad=0.
        self.capture_anchor_rad=None
        self.air_fault_reason=None

    @staticmethod
    def _scalar(x):
        return isinstance(x,Real)and not isinstance(x,(bool,np.bool_))and math.isfinite(float(x))

    @staticmethod
    def _vector(x,n):
        a=np.asarray(x)
        return a.shape==(n,)and a.dtype.kind in 'iuf'and bool(np.isfinite(a).all())

    def _time_valid(self,now):
        if not self._scalar(now)or now<0:return False
        t=float(now)
        if abs(t-round(t/PERIOD)*PERIOD)>1e-8:return False
        return self.last_time is None or(self.last_time<t and t-self.last_time<=.05)

    def _inhibit(self,reason):
        self.fault=True;self.air_fault_reason=reason
        self.log=dict(phase='INHIBIT',reason=reason,contact_or_flight_trusted=False,
                      air_pitch_ref_enabled=True,air_pitch_ref_fault_latched=True,
                      air_pitch_ref_h_rad=self.air_h_rad,air_pitch_ref_capture_anchor_rad=self.capture_anchor_rad)
        return np.zeros(6)

    def prepare_estimator(self,estimator,now):
        if not self.air_pitch_ref_enable:return super().prepare_estimator(estimator,now)
        try:valid=self._time_valid(now)
        except (TypeError,ValueError,OverflowError):valid=False
        if self.fault or not valid:
            self._inhibit(self.air_fault_reason or'contact_free_air_ref_invalid_or_faulted_time')
            return
        return super().prepare_estimator(estimator,now)

    def command(self,e,packet,now,attitude_q,forward=0.):
        # The OFF path is literally the old Position/V3 path, including logs.
        if not self.air_pitch_ref_enable:return super().command(e,packet,now,attitude_q,forward)
        if self.fault:return self._inhibit(self.air_fault_reason or self.log.get('reason','legacy_controller_fault'))
        try:
            valid=(self._time_valid(now)and self._vector(e.state14,14)
                   and self._scalar(e.sensor_age_s)and 0.<=e.sensor_age_s<=.05
                   and self._vector(packet.joint_pos4,4)and self._vector(packet.joint_vel4,4)
                   and self._vector(e.omega_body,3)and self._scalar(e.roll)
                   and self._vector(attitude_q,4)and abs(float(np.linalg.norm(attitude_q))-1.)<=1e-6
                   and self._scalar(forward))
        except (TypeError,ValueError,OverflowError,AttributeError):valid=False
        if not valid:return self._inhibit('air_pitch_ref_invalid_estimate_packet_or_time')
        t=float(now);since=t-self.trigger
        flight=bool(self.enabled and self.launched and self.push<=since<self.push+self.air)
        first_capture=bool(self.enabled and self.launched and self.landing_enable
                           and since>=self.push+self.air and self.capture_anchor_rad is None)
        if flight:
            self.air_goal_rad=float(np.clip(PITCH_K*float(e.state14[2])+PITCH_RATE_K*float(e.state14[9]),H_MIN,H_MAX))
            self.air_h_rad=float(np.clip(self.air_h_rad+float(np.clip(self.air_goal_rad-self.air_h_rad,-RATE*PERIOD,RATE*PERIOD)),H_MIN,H_MAX))
        elif first_capture:
            # Do this BEFORE V3: at its first capture u==0, it does not write ref.
            self.capture_anchor_rad=float(self.air_h_rad)
            self.eq0=self.eq0.copy()
            self.eq0[[3,5]]+=self.capture_anchor_rad
            self.ctrl.eq=self.eq0.copy()
            self.ctrl.ref[3:7]=self.eq0[3:7]
        original=self.q_start
        try:
            if flight:self.q_start=original+self.air_h_rad*np.ones(4)
            tau=super().command(e,packet,t,attitude_q,forward)
        finally:
            self.q_start=original
        # Metadata only. Never change already computed tau or manufacture target.
        self.log.update(air_pitch_ref_enabled=True,air_pitch_ref_h_rad=self.air_h_rad,
                        air_pitch_ref_goal_rad=self.air_goal_rad,air_pitch_ref_capture_anchor_rad=self.capture_anchor_rad,
                        air_pitch_ref_active_predicted_flight=flight,air_pitch_ref_input_is_estimated_only=True,
                        air_pitch_ref_is_timed_hypothesis=True,air_pitch_ref_contact_permission=False,
                        air_pitch_ref_dynamic_or_DR_limits_qualified=False)
        return tau
