"""Manual relative-odometry trigger hypothesis, not obstacle/contact detection.

The frozen V3 push/flight/capture equations and trigger-state guards remain.
An optional position decision is made from the current sensor estimate, but
schedules the NEXT 100Hz control tick: prepare_estimator can then disable the
same channels BEFORE that tick's acquisition/update. No retroactive flag edit.
Default disabled; no simulator, terrain, true-force, or DR imports.
"""
import math
import numpy as np
from MINIHOP_LANDING_V3.controller import MiniHop as V3


class PositionScheduler:
    def __init__(self,distance_m=1.18,min_time_s=1.,deadline_s=2.6,period_s=.01):
        self.distance=float(distance_m);self.minimum=float(min_time_s);self.deadline=float(deadline_s);self.period=float(period_s)
        assert all(math.isfinite(x)for x in(self.distance,self.minimum,self.deadline,self.period))
        assert 0.<self.distance<=3. and 0.<=self.minimum<self.deadline<=10. and self.period==.01
        self.origin=None;self.last_time=None;self.latch_time=None;self.decision_time=None
        self.relative=None;self.reason=None

    def step(self,distance_estimate,age_s,now):
        if self.reason is not None:return self.latch_time
        d=float(distance_estimate);age=float(age_s);now=float(now)
        if not all(math.isfinite(v)for v in(d,age,now))or now<0. or not 0.<=age<=.05:
            self.reason='position_trigger_invalid_estimate_or_time';return None
        if self.last_time is not None and(now<=self.last_time or now-self.last_time>.05):
            self.reason='position_trigger_clock_order_or_gap';return None
        self.last_time=now
        ticks=int(round(now/self.period))
        if abs(now-ticks*self.period)>1e-8:
            self.reason='position_trigger_off_control_grid';return None
        if self.origin is None:self.origin=d
        self.relative=d-self.origin
        if self.latch_time is not None:return self.latch_time
        if now>=self.deadline:
            self.reason='position_trigger_timeout';return None
        if now>=self.minimum and self.relative>=self.distance:
            candidate=(ticks+1)*self.period
            if candidate>self.deadline:
                self.reason='position_trigger_no_next_tick_before_deadline';return None
            self.decision_time=now;self.latch_time=candidate
        return self.latch_time


class MiniHop(V3):
    def __init__(self,start_gain,end_gain,geometry,config,landing_gain):
        super().__init__(start_gain,end_gain,geometry,config,landing_gain=landing_gain)
        self.position_enable=self.c.get('position_trigger_enable',False)
        assert type(self.position_enable)is bool
        self.position_active=bool(self.position_enable and self.enabled)
        self.scheduler=PositionScheduler(self.c.get('position_trigger_distance_m',1.18),
            self.c.get('position_trigger_min_time_s',1.),self.c.get('position_trigger_deadline_s',2.6))
        self.fixed_trigger_original=self.trigger
        if self.position_active:
            # Only a pending sentinel. Timeout is latched BEFORE this timer can
            # launch; it is never permission to hop if distance was not reached.
            self.trigger=self.scheduler.deadline+self.scheduler.period

    def command(self,e,packet,now,attitude_q,forward=0.):
        if self.position_active and not self.fault:
            try:
                x=np.asarray(e.state14,float)
                if x.shape!=(14,)or not np.isfinite(x).all():
                    self.scheduler.reason='position_trigger_invalid_state14'
                else:
                    trigger=self.scheduler.step(x[0],e.sensor_age_s,now)
                    if trigger is not None:self.trigger=trigger
            except (TypeError,ValueError,OverflowError):
                self.scheduler.reason='position_trigger_invalid_input_type'
            if self.scheduler.reason is not None:self.fault=True
        tau=super().command(e,packet,now,attitude_q,forward)
        self.log.update(position_trigger_enabled=bool(self.position_enable),
            position_trigger_active=bool(self.position_active),position_trigger_is_manual_odometry=True,
            position_trigger_trusted_world_position=False,position_trigger_contact_permission=False,
            position_origin_estimate_m=self.scheduler.origin,position_relative_estimate_m=self.scheduler.relative,
            position_target_m=self.scheduler.distance,position_decision_time_s=self.scheduler.decision_time,
            position_latched_push_time_s=self.scheduler.latch_time,
            position_trigger_timeout_s=self.scheduler.deadline)
        if self.position_active:
            self.log.update(phase_source='manual_odometry_next_tick_schedule_not_contact',
                original_torque_phase_timing_unchanged=False,relative_phase_durations_unchanged=True,
                fixed_trigger_superseded=True,fixed_trigger_original_s=self.fixed_trigger_original)
            if self.scheduler.reason is not None:self.log['reason']=self.scheduler.reason
        return tau
