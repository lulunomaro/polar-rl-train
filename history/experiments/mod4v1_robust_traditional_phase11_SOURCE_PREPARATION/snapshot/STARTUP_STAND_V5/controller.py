"""V5: only earlier permission for unchanged V4 pose-wheel branch; no new K/gain/contact inputs."""
import math
import numpy as np
from STARTUP_STAND_V4.controller import StartupStand as PreviousStartupStand, RECOVER
from STARTUP_STAND_V1.controller import scalar, vector, project_reference, legal_reference, quintic, LEG, WHEEL, EFFORT

class StartupStand(PreviousStartupStand):
    def __init__(self, gain_nominal, geometry, config=None, support_reference=None):
        c = {} if config is None else dict(config)
        flag = c.pop('lift_pose_enable', False)
        if type(flag) is not bool:
            raise ValueError('V5 lift_pose_enable requires exact bool')
        if flag and (c.get('support_geometry_enable', False) is not True
                     or c.get('recovery_tracking_enable', False) is not True
                     or c.get('alignment_wheel_enable', False) is not False):
            raise ValueError('V5 requires V4 support/tracking and legacy alignmentFalse')
        super().__init__(gain_nominal, geometry, c, support_reference=support_reference)
        self.lift_pose_enable = flag
        self.lift_pose_active = bool(flag and self.support_geometry_active)
        self.lift_pose_first_branch_s = None

    def command(self, e, packet, now, attitude_q):
        if not self.lift_pose_active:
            return super().command(e, packet, now, attitude_q)
        if self.phase not in ('OBSERVE', 'LIFT_WORLD_SUPPORT') or self.fault_reason is not None:
            return super().command(e, packet, now, attitude_q)
        try:
            # Numerical/type validation only. Existing finite domains, freshness, clock,
            # envelope, readiness and sensor constraints remain inside original V4.
            scalar(now, 'control time')
            scalar(e.roll, 'roll')
            vector(e.state14, 14, 'state14')
            vector(e.omega_body, 3, 'omega')
            scalar(e.sensor_age_s, 'sensor age')
            scalar(e.estimated_time_s, 'estimate time')
            if getattr(packet, 'validity', None) is not True:
                raise ValueError('sensor packet validity not True')
            scalar(packet.time_s, 'source time'); scalar(packet.arrival_s, 'arrival')
            vector(packet.joint_pos4, 4, 'encoder q4')
            vector(packet.joint_vel4, 4, 'encoder qd4')
            vector(packet.accel_proper_body, 3, 'IMU proper')
            vector(packet.gyro_body, 3, 'raw gyro')
            vector(packet.wheel_vel2, 2, 'wheel rate')
            vector(attitude_q, 4, 'attitude quaternion')
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._notes(self._fault(ex))
        return self._command_lift_permission(e, packet, now, attitude_q)

    def _notes(self, tau):
        if not self.lift_pose_active:
            return super()._notes(tau)
        result = super()._notes(tau)
        current = self.fault_reason is None and 'time_s' in self.log
        on = bool(current and self.phase == 'LIFT_WORLD_SUPPORT' and self.capture_active)
        if on and self.lift_pose_first_branch_s is None:
            self.lift_pose_first_branch_s = self.log['time_s']
        self.log.update(lift_pose_enable=self.lift_pose_enable,
            lift_pose_timing_active=self.lift_pose_active,
            lift_pose_branch_on_this_command=on if current else None,
            lift_pose_same_gate_this_command=bool(self.capture_gate) if current else None,
            lift_pose_first_branch_s=self.lift_pose_first_branch_s,
            earlier_lift_latch_carryover_is_timing_change=bool(self.capture_latched and self.lift_pose_first_branch_s is not None),
            no_new_contact_or_hardware_permission=True)
        return result

    def _command_lift_permission(self, e, packet, now, attitude_q):
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
            if self.phase in ('LIFT_WORLD_SUPPORT', 'CAPTURE_WORLD_SUPPORT', 'RETURN_NOMINAL', 'VERIFY'):
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
