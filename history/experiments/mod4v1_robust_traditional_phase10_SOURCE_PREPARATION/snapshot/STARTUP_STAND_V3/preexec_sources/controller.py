"""Default-off recovery tracking plus optional eligible pose alignment.
Parent METHOD.md + METHOD_CLARIFICATION_001.json are the specification.
No model, driver, contact/true-state input, or physical stand-up guarantee.
"""
import numpy as np
from STARTUP_STAND_V1.controller import StartupStand as BaseStartupStand
from STARTUP_STAND_V1.controller import vector, scalar, LEG, WHEEL, EFFORT


class StartupStand(BaseStartupStand):
    def __init__(self, gain_nominal, geometry, config=None):
        c = {} if config is None else dict(config)
        tracking = c.pop('recovery_tracking_enable', False)
        alignment = c.pop('alignment_wheel_enable', False)
        if type(tracking) is not bool or type(alignment) is not bool:
            raise ValueError('V3 recovery/alignment flags require exact bool')
        if alignment and not tracking:
            raise ValueError('alignment_wheel_enable requires recovery_tracking_enable')
        super().__init__(gain_nominal, geometry, c)
        self.recovery_tracking_enable = tracking
        self.alignment_wheel_enable = alignment
        self.recovery_tracking_active = bool(tracking and self.enabled)
        self.alignment_wheel_active = bool(alignment and self.recovery_tracking_active)
        self.alignment_latched = False
        self.alignment_eligible_ever = False
        self.alignment_first_eligible_s = None
        self.encoder_travel_m = 0.
        self._travel_time = None
        self._ready_wheel_rate = None

    def _ready(self, x, roll, omega, q, qd, fresh):
        original = super()._ready(x, roll, omega, q, qd, fresh)
        if not self.recovery_tracking_active:
            return original
        return bool(original and self._ready_wheel_rate is not None
                    and np.max(np.abs(self._ready_wheel_rate)) <= 2.)

    def _fault_note(self, tau):
        self.log.update(recovery_encoder_travel_m=self.encoder_travel_m,
            recovery_travel_last_control_s=self._travel_time,
            recovery_travel_is_wheel_rotation_proxy_not_true_path=True,
            alignment_latched=self.alignment_latched,
            alignment_candidate_eligible_ever=self.alignment_eligible_ever,
            output_tau6_Nm=np.asarray(tau).tolist())
        return tau

    def command(self, e, packet, now, attitude_q):
        if not self.recovery_tracking_active:
            # No extra field reads, readiness constraint, travel update or logs.
            return super().command(e, packet, now, attitude_q)
        if self.fault_reason is not None:
            return self._fault_note(super().command(e, packet, now, attitude_q))
        try:
            wheels = vector(packet.wheel_vel2, 2, 'V3 same-packet wheel rate')
            q = vector(packet.joint_pos4, 4, 'V3 same-packet q4')
            qd = vector(packet.joint_vel4, 4, 'V3 same-packet qd4')
        except (ValueError, TypeError, AttributeError, OverflowError) as ex:
            return self._fault_note(self._fault(ex))
        self._ready_wheel_rate = wheels.copy()
        previous_phase = self.phase
        base_tau = super().command(e, packet, now, attitude_q)
        if self.fault_reason is not None:
            return self._fault_note(base_tau)
        try:
            t = scalar(self.log['time_s'], 'published validated control time')
            recover = self.phase in ('SHAPE_TO_STAND', 'VERIFY')
            last_interval = previous_phase == 'VERIFY' and self.phase == 'BLEND'
            # Both profiles use the SAME current-sample rectangle proxy and guard.
            # Last VERIFY interval is included even though the base already chose BLEND.
            if recover or last_interval:
                if self._travel_time is not None:
                    dt = t-self._travel_time
                    if not 0. < dt <= .05+1e-8:
                        raise ValueError('recovery travel control-clock mismatch')
                    self.encoder_travel_m += dt*.0625*float(np.mean(np.abs(wheels)))
                self._travel_time = t
                if not np.isfinite(self.encoder_travel_m):
                    raise ValueError('nonfinite recovery encoder travel')
                if self.encoder_travel_m > .50:
                    raise ValueError('recovery encoder rotation travel exceeds0.50m')
            eligible = bool(self.phase == 'VERIFY'
                and np.max(np.abs(q-self.target)) <= .08
                and np.max(np.abs(qd)) <= .40)
            if eligible:
                self.alignment_eligible_ever = True
                if self.alignment_first_eligible_s is None:
                    self.alignment_first_eligible_s = t
                if self.alignment_wheel_active:
                    self.alignment_latched = True
            self.log.update(recovery_tracking_enable=self.recovery_tracking_enable,
                alignment_wheel_enable=self.alignment_wheel_enable,
                alignment_candidate_eligible_this_command=eligible,
                alignment_candidate_eligible_ever=self.alignment_eligible_ever,
                alignment_first_eligible_s=self.alignment_first_eligible_s,
                alignment_latched=self.alignment_latched,
                alignment_is_sensor_proxy_not_contact_permission=True,
                recovery_encoder_travel_m=self.encoder_travel_m,
                recovery_travel_last_control_s=self._travel_time,
                recovery_travel_rule='current_packet_rate_rectangle_actual_validated_control_dt',
                recovery_travel_is_wheel_rotation_proxy_not_true_path=True,
                ready_also_requires_max_packet_wheel_rate_le2=True,
                recovery_actuation_override=False)
            if not recover:
                return base_tau
            scale = scalar(self.log['nominal_ff_scale'], 'published nominal ff scale')
            x = vector(e.state14, 14, 'V3 state14')
            roll = float(np.clip(-20.*float(e.roll)-2.*float(e.omega_body[0]), -8., 8.))
            tau = np.zeros(6)
            tau[LEG] = scale*self.ff[LEG]+120.*(self.qref-q)+4.*(self.vref-qd)
            tau[LEG] += np.array([-roll, roll, roll, -roll])
            wheel = np.clip(-.30*wheels, -2., 2.)
            common = 0.
            limited = np.zeros(2, dtype=bool)
            aligned = bool(self.alignment_wheel_active and self.alignment_latched)
            if aligned:
                common = scalar(float(np.mean(-self.ctrl.K[WHEEL, 2]*x[2]
                                     - self.ctrl.K[WHEEL, 9]*x[9])), 'alignment pose common')
                wheel = np.clip(common-.30*wheels, -3., 3.)
                limited = (np.abs(wheels) > 12.) & (wheel*wheels > 0.)
                for i in range(2):
                    if limited[i]:
                        wheel[i] = float(np.clip(-.30*np.sign(wheels[i])*(abs(wheels[i])-12.), -3., 3.))
            tau[WHEEL] = wheel
            preclip = vector(tau, 6, 'V3 replacement tau6')
            tau = np.clip(preclip, -EFFORT, EFFORT)
            self.last_tau = tau.copy()
            self.log['discarded_base_candidate_tau6_Nm'] = np.asarray(base_tau).tolist()
            self.log['discarded_base_startup_wheel_scale'] = self.log.pop('startup_wheel_scale')
            self.log.update(recovery_actuation_override=True,
                recovery_subphase='ELIGIBLE_POSE_ALIGNMENT' if aligned else 'TRACKING_QUIET_WHEELS',
                recovery_leg_policy='120_tracking_4rate_scaled_ff_original_roll_no_parallel_Kleg',
                recovery_wheel_rate2_rad_s=wheels.tolist(),
                alignment_pose_common_before_damping_Nm=common,
                alignment_soft_overspeed_limited2=limited.tolist(),
                alignment_soft_limit_is_NOT_physical_speed_guarantee=True,
                recovery_roll_scalar_Nm=roll,
                recovery_preclip_tau6_Nm=preclip.tolist(),output_tau6_Nm=tau.tolist())
            return tau.copy()
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._fault_note(self._fault(ex))


Controller = StartupStand
