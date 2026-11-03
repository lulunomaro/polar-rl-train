"""New nominal spring-release PUSH hypothesis; disabled by default.
Only the static endpoint feed-forward's nominal gas cancellation is removed.
The physical spring/plant, original guards, PD, roll/yaw, clipping, observer,
position scheduler, flight and capture equations remain in frozen base classes.
"""
import math
import numpy as np
from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop as Base

LEG = np.array([0, 1, 3, 4])
WHEEL = np.array([2, 5])


def _gas6(value, label):
    raw = np.asarray(value)
    if raw.shape != (6,) or raw.dtype.kind not in 'fiu' or not np.isfinite(raw).all():
        raise ValueError(label + ': six finite numeric output-joint torques required')
    out = np.asarray(raw, dtype=float).copy()
    if np.any(out[WHEEL] != 0.):
        raise ValueError(label + ': gas virtual torque must not include wheel torque')
    out.setflags(write=False)
    return out


def _overlay(gain, gas):
    # DO NOT mutate gain['tau']: GroundController.tau_eq can alias its array.
    original = np.asarray(gain['tau'], dtype=float)
    if original.shape != (6,) or not np.isfinite(original).all():
        raise ValueError('invalid original endpoint feed-forward')
    tau = original.copy()
    tau[LEG] = original[LEG] + gas[LEG]
    if not np.isfinite(tau).all():
        raise ValueError('nonfinite feed-forward after nominal gas add-back')
    tau.setflags(write=False)
    overlay = dict(gain)
    overlay['tau'] = tau
    return overlay


class MiniHop(Base):
    def __init__(self, start_gain, end_gain, geometry, config, landing_gain,
                 *, start_gas_tau6=None, end_gas_tau6=None):
        # Original dictionaries/arrays initialize every ground controller first.
        super().__init__(start_gain, end_gain, geometry, config, landing_gain=landing_gain)
        self.spring_release_requested = self.c.get('release_spring_compensation_during_push', False)
        if type(self.spring_release_requested) is not bool:
            raise ValueError('release_spring_compensation_during_push requires bool')
        self.spring_release_active = bool(self.spring_release_requested and self.enabled)
        self._gas_start = self._gas_end = None
        self._push_start_gain = self._push_end_gain = None
        if self.spring_release_active:
            self._gas_start = _gas6(start_gas_tau6, 'start_gas_tau6')
            self._gas_end = _gas6(end_gas_tau6, 'end_gas_tau6')
            self._push_start_gain = _overlay(self.g, self._gas_start)
            self._push_end_gain = _overlay(self.end, self._gas_end)

    def command(self, e, packet, now, attitude_q, forward=0.):
        overlay = False
        # No fake trigger or guard. In particular the first push has launched=False.
        if self.spring_release_active and not self.fault:
            try:
                t = float(now)
                overlay = bool(math.isfinite(t) and 0. <= t-self.trigger < self.push)
            except (TypeError, ValueError, OverflowError):
                pass  # The original command owns type/clock/fault handling.
        original_g, original_end = self.g, self.end
        try:
            if overlay:
                self.g, self.end = self._push_start_gain, self._push_end_gain
            tau = super().command(e, packet, now, attitude_q, forward)
        finally:
            # Includes any exception/fault; never leak FF into approach/capture.
            self.g, self.end = original_g, original_end
        used = bool(overlay and not self.fault and self.log.get('phase') == 'timed_push')
        delta = np.zeros(6)
        if used:
            u = float(np.clip((float(now)-self.trigger)/self.push, 0., 1.))
            s = 3*u*u-2*u*u*u
            delta[LEG] = (1-s)*self._gas_start[LEG] + s*self._gas_end[LEG]
        self.log.update(spring_release_requested=bool(self.spring_release_requested),
                        spring_release_enabled=bool(self.spring_release_active),
                        spring_release_applied_this_command=used,
                        nominal_endpoint_feedforward_delta6_before_PD_clip=delta.tolist(),
                        physical_gas_spring_changed=False,
                        spring_release_is_nominal_endpoint_hypothesis=True,
                        gas_addback_is_actual_torque_or_bus_power=False)
        return tau
