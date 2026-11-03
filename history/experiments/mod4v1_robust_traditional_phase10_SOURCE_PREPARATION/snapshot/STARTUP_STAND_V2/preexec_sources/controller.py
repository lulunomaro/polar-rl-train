"""Independent default-off startup recovery output hypothesis, not a stand-up proof.
Base owns timing, sensor guards, reference, readiness, observer and balance handoff.
No model, driver, contact or external-state input. See parent-locked METHOD.md.
"""
import numpy as np
from STARTUP_STAND_V1.controller import StartupStand as BaseStartupStand
from STARTUP_STAND_V1.controller import vector, scalar, LEG, WHEEL, EFFORT


class StartupStand(BaseStartupStand):
    def __init__(self, gain_nominal, geometry, config=None):
        c = {} if config is None else dict(config)
        feature = c.pop('recovery_actuation_enable', False)
        if type(feature) is not bool:
            raise ValueError('recovery_actuation_enable requires exact bool')
        super().__init__(gain_nominal, geometry, c)
        self.recovery_actuation_enable = feature
        self.recovery_actuation_active = bool(feature and self.enabled)

    def command(self, e, packet, now, attitude_q):
        # Literal delegation: no extra packet fields, arithmetic or log changes.
        if not self.recovery_actuation_active:
            return super().command(e, packet, now, attitude_q)
        if self.fault_reason is not None:
            return super().command(e, packet, now, attitude_q)
        try:
            # Must fail before the base phase/reference/ready scheduler advances.
            wheel_rate = vector(packet.wheel_vel2, 2, 'recovery same-packet wheel rate')
        except (ValueError, TypeError, AttributeError, OverflowError) as ex:
            return self._fault(ex)
        base_tau = super().command(e, packet, now, attitude_q)
        if self.phase not in ('SHAPE_TO_STAND', 'VERIFY'):
            # BLEND captures the previous actual replacement through last_tau.
            return base_tau
        try:
            scale = scalar(self.log['nominal_ff_scale'], 'published nominal ff scale')
            err = vector(e.state14, 14, 'recovery state14') - self.ctrl.ref.copy()
            err[[0, 1, 7, 8]] = 0.
            err[[2, 9]] *= scale
            linear_leg = scale*self.ff[LEG] - self.ctrl.K[LEG, :] @ err
            roll = float(np.clip(-20.*float(e.roll)-2.*float(e.omega_body[0]), -8., 8.))
            tau = np.zeros(6)
            tau[LEG] = linear_leg + np.array([-roll, roll, roll, -roll])
            tau[WHEEL] = np.clip(-.30*wheel_rate, -2., 2.)
            preclip = vector(tau, 6, 'recovery replacement tau6')
            tau = np.clip(preclip, -EFFORT, EFFORT)
            # The next base command must see this actual output, not its discarded PD.
            self.last_tau = tau.copy()
            self.log['discarded_base_candidate_tau6_Nm'] = np.asarray(base_tau).tolist()
            self.log['discarded_base_startup_wheel_scale'] = self.log.pop('startup_wheel_scale')
            self.log.update(recovery_actuation_override=True,
                recovery_leg_error14_after_coordinate_mask_and_pitch_scale=err.tolist(),
                recovery_leg_linear_tau4_before_roll_Nm=linear_leg.tolist(),
                recovery_roll_scalar_Nm=roll,
                recovery_preclip_tau6_Nm=preclip.tolist(),
                wheel_actuation='same_packet_encoder_rate_damping_not_ff_scaled',
                recovery_wheel_rate2_rad_s=wheel_rate.tolist(),
                recovery_wheel_damping_Nm_per_rad_s=.30,
                recovery_wheel_damping_cap_Nm=2.,
                output_tau6_Nm=tau.tolist(),
                recovery_actuation_is_parent_locked_unqualified_hypothesis=True,
                no_added_parallel_leg_PD=True)
            return tau.copy()
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ArithmeticError) as ex:
            return self._fault(ex)


Controller = StartupStand
