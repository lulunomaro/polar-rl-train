"""Sensor-only world-support startup TRAIN hypothesis; METHOD.md is the contract.
Default off. No model/FK, contact identity, true state, actuator or board I/O.
"""
import math
import numpy as np
from STARTUP_STAND_V3.controller import StartupStand as PreviousStartupStand
from STARTUP_STAND_V1.controller import (vector, scalar, LEG, WHEEL, EFFORT,
    QMIN, QMAX, project_reference, legal_reference, quintic)

RECOVER = ('LIFT_WORLD_SUPPORT', 'CAPTURE_WORLD_SUPPORT', 'RETURN_NOMINAL', 'VERIFY')
RATE_CAP = .999


class StartupStand(PreviousStartupStand):
    def __init__(self, gain_nominal, geometry, config=None, support_reference=None):
        c = {} if config is None else dict(config)
        feature = c.pop('support_geometry_enable', False)
        if type(feature) is not bool:
            raise ValueError('V4 support_geometry_enable requires exact bool')
        if feature and (c.get('recovery_tracking_enable', False) is not True
                        or c.get('alignment_wheel_enable', False) is not False):
            raise ValueError('V4 requires tracking=True and legacy alignment=False')
        super().__init__(gain_nominal, geometry, c)
        self.support_geometry_enable = feature
        self.support_geometry_active = bool(feature and self.enabled)
        # No support_reference access at all in the disabled delegate path.
        self.support_q = self.support_ff = None
        if self.support_geometry_active:
            if not isinstance(support_reference, dict):
                raise ValueError('Explicit public support reference dict required')
            g = support_reference.get('gain', support_reference)
            q = vector(g['q'], 7, 'public support q7')
            self.support_q = np.array([q[3], q[3]+q[4], q[5], q[5]+q[6]])
            self.support_ff = vector(g['tau'], 6, 'public support trim6')
            legal_reference(self.support_q, np.zeros(4))
            expected = np.array([.0025360756709216082, .20253607567092162]*2)
            if np.max(np.abs(self.support_q-expected)) > 1e-10:
                raise ValueError('Only studied public delta20 support reference admitted')
        self.support_ready_since = None
        self.return_from = None
        self.capture_latched = self.capture_gate = self.capture_active = False
        self.capture_ever = False
        self.capture_first_s = None
        self._ref_time = None
        self.ref_gamma = 1.
        self.common_unclipped = self.common_clipped = None
        self.support_goal = None
        self.nominal_mix = 0.
        self.ff_scale = 0.
        self.pose_common = 0.
        self.soft_limited = np.zeros(2, dtype=bool)
        self.preclip_tau = np.zeros(6)
        self.ground_candidate = None
        self._last_pub_q = self._last_pub_v = self._last_pub_t = None

    def _goal(self, pitch):
        self.common_unclipped = -scalar(pitch, 'estimated support pitch')
        lo = float(np.max(QMIN-self.support_q))
        hi = float(np.min(QMAX-self.support_q))
        self.common_clipped = float(np.clip(self.common_unclipped, lo, hi))
        # Reference-only roundoff clamp; encoder measurements never change.
        goal = project_reference(self.support_q+self.common_clipped)
        legal_reference(goal, np.zeros(4))
        self.support_goal = goal.copy()
        return goal

    def _reference(self, desired, t):
        desired = vector(desired, 4, 'V4 desired reference')
        legal_reference(desired, np.zeros(4))
        previous = self.qref.copy()
        if self._ref_time is None:
            self._ref_time = t
            self.vref = np.zeros(4)
            return
        dt = t-self._ref_time
        if not 0. < dt <= .05+1e-8:
            raise ValueError('V4 reference clock mismatch')
        step = desired-previous
        largest = float(np.max(np.abs(step)))
        self.ref_gamma = min(1., RATE_CAP*dt/largest) if largest else 1.
        # A single convex segment preserves coupled hip/crank delta constraints.
        self.qref = project_reference(previous+self.ref_gamma*step)
        self.vref = (self.qref-previous)/dt
        self._ref_time = t
        legal_reference(self.qref, self.vref)

    def _travel(self, wheels, t):
        if self._travel_time is not None:
            dt = t-self._travel_time
            if not 0. < dt <= .05+1e-8:
                raise ValueError('V4 recovery travel control clock mismatch')
            self.encoder_travel_m += dt*.0625*float(np.mean(np.abs(wheels)))
        self._travel_time = t
        if not np.isfinite(self.encoder_travel_m) or self.encoder_travel_m > .50:
            raise ValueError('recovery encoder rotation travel exceeds0.50m')

    def _notes(self, tau):
        # Faults have no current reference: explicitly label only last published.
        current = self.fault_reason is None and 'time_s' in self.log
        if current:
            self._last_pub_q = self.qref.copy()
            self._last_pub_v = self.vref.copy()
            self._last_pub_t = float(self.log['time_s'])
        self.log.pop('startup_wheel_scale', None)
        self.log.update(support_geometry_enable=self.support_geometry_enable,
            support_geometry_active=self.support_geometry_active,
            recovery_tracking_enable=self.recovery_tracking_enable,
            alignment_wheel_enable=self.alignment_wheel_enable,
            support_common_unclipped_rad=self.common_unclipped if current else None,
            support_common_clipped_rad=self.common_clipped if current else None,
            support_goal_q4=None if not current or self.support_goal is None else self.support_goal.tolist(),
            support_reference_rate_gamma=self.ref_gamma if current else None,
            support_reference_rate_cap_rad_s=RATE_CAP,
            last_published_reference_q4=None if self._last_pub_q is None else self._last_pub_q.tolist(),
            last_published_reference_qd4=None if self._last_pub_v is None else self._last_pub_v.tolist(),
            last_published_reference_time_s=self._last_pub_t,
            support_nominal_trim_mix=self.nominal_mix if current else None,
            support_trim_scale=self.ff_scale if current else None,
            support_capture_gate_this_command=self.capture_gate if current else None,
            support_capture_latched=self.capture_latched,
            support_capture_active_this_command=self.capture_active if current else None,
            support_capture_eligible_ever=self.capture_ever,
            support_capture_first_eligible_s=self.capture_first_s,
            support_gate_is_NOT_contact_or_unloading_certificate=True,
            alignment_pose_common_before_damping_Nm=self.pose_common if current else None,
            alignment_soft_overspeed_limited2=self.soft_limited.tolist() if current else None,
            alignment_soft_limit_is_NOT_physical_speed_guarantee=True,
            recovery_encoder_travel_m=self.encoder_travel_m,
            recovery_travel_last_control_s=self._travel_time,
            recovery_travel_is_wheel_rotation_proxy_not_true_path=True,
            recovery_preclip_tau6_Nm=self.preclip_tau.tolist() if current else None,
            discarded_ground_candidate_tau6_Nm=None if not current or self.ground_candidate is None else self.ground_candidate.tolist(),
            output_tau6_Nm=np.asarray(tau).tolist(),hardware_send_permission=False)
        return np.asarray(tau).copy()

    def command(self, e, packet, now, attitude_q):
        if not self.support_geometry_active:
            return super().command(e, packet, now, attitude_q)
        if self.fault_reason is not None:
            return self._notes(self._fault(self.fault_reason))
        try:
            t = self._time(now, self.last_command)
            if self.prepared is None or abs(self.prepared-t) > 1e-8:
                raise ValueError('prepare_estimator required before this command epoch')
            self.last_command = t
            x, roll, omega, q, qd, proper, gyro, fresh, age, stamp = self._sample(e, packet, t, attitude_q)
            wheels = vector(packet.wheel_vel2, 2, 'V4 same-packet wheel rate')
            self._ready_wheel_rate = wheels.copy()
            if self.phase != 'BALANCE' and t-self.started >= 6.-1e-10:
                raise ValueError('startup timeout6s')
            self.capture_gate = self.capture_active = False
            self.pose_common = 0.
            self.soft_limited[:] = False
            if self.phase in RECOVER:
                # Includes the final VERIFY interval before transition to BLEND.
                self._travel(wheels, t)
            goal = self._goal(x[2])
            scale, blend = 1., 0.
            if self.phase == 'OBSERVE':
                scale = 0.
                norm = float(np.linalg.norm(proper))
                pr = math.atan2(proper[1], proper[2])
                pp = math.atan2(-proper[0], math.hypot(proper[1], proper[2]))
                static = bool(fresh and .8*9.81 <= norm <= 1.2*9.81
                    and np.linalg.norm(gyro) <= .15 and np.linalg.norm(omega) <= .15
                    and np.max(np.abs(qd)) <= .15 and abs(pr-roll) <= .1 and abs(pp-x[2]) <= .1)
                if static and self.static_since is not None and np.max(np.abs(q-self.static_q0)) > .02:
                    static = False
                if not static:
                    self.static_since = self.static_q0 = None
                elif self.static_since is None:
                    self.static_since, self.static_q0 = t, q.copy()
                self.qref, self.vref = project_reference(q), np.zeros(4)
                if self.static_since is not None and t-self.static_since >= .25-1e-10:
                    self.measured_q0, self.q0 = q.copy(), project_reference(q)
                    self.project_delta = self.q0-self.measured_q0
                    self._anchor_ground(x)
                    self._enter('LIFT_WORLD_SUPPORT', t)
                    self._ref_time = self._travel_time = t
                else:
                    self.last_tau = np.zeros(6)
                    self.ff_scale = 0.
                    return self._notes(self._publish(t, self.last_tau, 0., 0., q, age, stamp))
            if self.phase == 'LIFT_WORLD_SUPPORT':
                u = (t-self.entered)/2.2
                scale, _ = quintic(u)
                desired = self.q0+(goal-self.q0)*scale
                if t > self._ref_time+1e-10:
                    self._reference(desired, t)
                if u >= 1.-1e-10:
                    self.support_ready_since = None
                    self._enter('CAPTURE_WORLD_SUPPORT', t)
            elif self.phase == 'CAPTURE_WORLD_SUPPORT':
                self._reference(goal, t)
            elif self.phase == 'RETURN_NOMINAL':
                u = (t-self.entered)/1.
                self.nominal_mix, _ = quintic(u)
                self._reference(self.return_from+(self.target-self.return_from)*self.nominal_mix, t)
                if u >= 1.-1e-10 and np.max(np.abs(self.qref-self.target)) <= 1e-10:
                    self.ready_since = None
                    self._enter('VERIFY', t)
            elif self.phase in ('VERIFY', 'BLEND', 'BALANCE'):
                self.nominal_mix = 1.
                self._reference(self.target, t)
            else:
                raise ValueError('unknown V4 startup phase')
            self.ff_scale = scale
            support_error = float(np.max(np.abs(q-goal)))
            if self.phase in ('CAPTURE_WORLD_SUPPORT', 'RETURN_NOMINAL', 'VERIFY'):
                self.capture_gate = bool(fresh and np.max(np.abs(q-self.qref)) <= .08
                    and np.max(np.abs(qd)) <= .40 and .8*9.81 <= np.linalg.norm(proper) <= 1.2*9.81)
                if self.capture_gate and np.max(np.abs(wheels)) <= 2.:
                    self.capture_latched = True
                    self.capture_ever = True
                    if self.capture_first_s is None:
                        self.capture_first_s = t
                self.capture_active = bool(self.capture_latched and self.capture_gate)
            if self.phase == 'CAPTURE_WORLD_SUPPORT':
                ready = bool(self.capture_gate and abs(x[2]) < .12 and abs(roll) < .12
                    and support_error <= .08 and np.max(np.abs(qd)) <= .20
                    and np.max(np.abs(self.vref)) <= .20 and np.linalg.norm(omega) <= .50
                    and np.max(np.abs(wheels)) <= 2.)
                if not ready:
                    self.support_ready_since = None
                elif self.support_ready_since is None:
                    self.support_ready_since = t
                if self.support_ready_since is not None and t-self.support_ready_since >= .25-1e-10:
                    self.return_from = self.qref.copy()
                    self._enter('RETURN_NOMINAL', t)
            if self.phase == 'VERIFY':
                if not self._ready(x, roll, omega, q, qd, fresh):
                    self.ready_since = None
                elif self.ready_since is None:
                    self.ready_since = t
                if self.ready_since is not None and t-self.ready_since >= .5-1e-10:
                    self.blend_from = self.last_tau.copy()
                    self._anchor_ground(x)
                    self._enter('BLEND', t)
            if self.phase == 'BLEND' and not self._ready(x, roll, omega, q, qd, fresh):
                raise ValueError('handoff readiness lost during blend')
            legal_reference(self.qref, self.vref)
            self._ground_reference()
            ground = vector(self.ctrl.command(e, 0., 0.), 6, 'GroundController tau')
            if not self.ctrl.valid_command:
                raise ValueError('GroundController invalid command')
            self.ground_candidate = ground.copy()
            if self.phase in RECOVER:
                ff = (1.-self.nominal_mix)*self.support_ff+self.nominal_mix*self.ff
                tau = np.zeros(6)
                tau[LEG] = scale*ff[LEG]+120.*(self.qref-q)+4.*(self.vref-qd)
                r = float(np.clip(-20.*roll-2.*omega[0], -8., 8.))
                tau[LEG] += np.array([-r, r, r, -r])
                wheel = np.clip(-.30*wheels, -2., 2.)
                if self.capture_active:
                    self.pose_common = scalar(float(np.mean(-self.ctrl.K[WHEEL, 2]*x[2]
                        -self.ctrl.K[WHEEL, 9]*x[9])), 'V4 pose common')
                    wheel = np.clip(self.pose_common-.30*wheels, -3., 3.)
                    self.soft_limited = (np.abs(wheels) > 12.) & (wheel*wheels > 0.)
                    for i in range(2):
                        if self.soft_limited[i]:
                            wheel[i] = float(np.clip(-.30*np.sign(wheels[i])*(abs(wheels[i])-12.), -3., 3.))
                tau[WHEEL] = wheel
            elif self.phase == 'BLEND':
                blend, _ = quintic((t-self.entered)/.5)
                tau = (1.-blend)*self.blend_from+blend*ground
                if t-self.entered >= .5-1e-10:
                    self._enter('BALANCE', t)
            elif self.phase == 'BALANCE':
                blend, tau = 1., ground
            else:
                raise ValueError('unknown V4 actuation phase')
            self.preclip_tau = vector(tau, 6, 'V4 preclip tau')
            tau = np.clip(self.preclip_tau, -EFFORT, EFFORT)
            self.last_tau = tau.copy()
            return self._notes(self._publish(t, tau, scale, blend, q, age, stamp))
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._notes(self._fault(ex))


Controller = StartupStand
