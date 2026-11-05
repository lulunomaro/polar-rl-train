"""Optional SIM pipeline timestamps only; no values, physics, DR or SDK imports."""
from copy import deepcopy
from dataclasses import dataclass
from numbers import Real, Integral
import math

TOL = 1e-8  # Floating SIM clock comparison only; not a hardware timing bound.
ROLES = {
    'encoder_q4': 'encoder_endpoint_output_joint_angles',
    'encoder_qd4': 'encoder_rates',
    'wheel_vel2': 'encoder_wheel_rates',
    'gyro_B': 'gyro_BODY_components',
    'proper_imu_B': 'proper_acceleration_at_IMU_not_chassis_origin',
    'motor_tau6': 'sim_actuator_ctrl_hold_NOT_measured_output_torque',
}
def number(x):
    return float(x) if isinstance(x, Real) and not isinstance(x, bool) and math.isfinite(x) else None

def integer(x):
    return int(x) if isinstance(x, Integral) and not isinstance(x, bool) and x >= 0 else None

def channel(name, provenance, timestamp=None, start=None, end=None, count=None, kind='unknown', **extra):
    return dict(timestamp_s=timestamp, window_start_s=start, window_end_s=end, sample_count=count,
                kind=kind, provenance=provenance, measurement_role=ROLES[name],
                usable_for_alignment=timestamp is not None, clock_error_bound_s=None,
                noise_error_bound=None, hardware_filter_delay_bound_s=None, **extra)

@dataclass(frozen=True)
class FrameClock:
    epoch_s: object
    sample_period_s: object
    window_count: object
    total_samples: object
    physics_tick: object
    previous_torque_available: bool

class TimeMetadataPublisher:
    """One previous source descriptor: exact current/previous V3 selection only.
    Irregular D3 stamps never get 'repaired' by relabelling returned values.
    """
    def __init__(self):
        self.previous = None
        self.last_packet = None
        self.last_metadata = None
        self.serial = 0

    def _frame(self, raw):
        t, dt = number(raw.epoch_s), number(raw.sample_period_s)
        n, total, tick = integer(raw.window_count), integer(raw.total_samples), integer(raw.physics_tick)
        known = t is not None and t >= 0
        mean_known = (known and dt is not None and dt > 0 and n is not None and n > 0
                      and total is not None and tick is not None and n <= total == tick
                      and abs(t-tick*dt) <= TOL and t-n*dt >= -TOL)
        if self.previous and mean_known:
            prev = self.previous
            if prev['epoch_s'] is not None and abs(t-prev['epoch_s']-n*dt) > TOL:
                mean_known = False
        ch = {}
        ch['encoder_q4'] = channel('encoder_q4', 'SIM V3 qpos endpoint before observe; not hardware calibration',
                                    t if known else None, count=1, kind='endpoint')
        for name in ('encoder_qd4', 'wheel_vel2', 'gyro_B', 'proper_imu_B'):
            if mean_known:
                start, end = t-n*dt, t-dt
                ch[name] = channel(name, 'SIM driver uniform PRE samples; BODY-component boxcar then observe/D1',
                    (start+end)/2, start, end, n, 'sampled_boxcar', aperture_end_s=t,
                    sample_period_s=dt, window_second_moment_s2=(n*n-1)*dt*dt/12)
            elif n == 0 and name in ('encoder_qd4', 'wheel_vel2'):
                ch[name] = channel(name, 'SIM empty-window fallback reads CURRENT qvel endpoint, not a mean',
                                   t if known else None, count=1, kind='endpoint', window_second_moment_s2=0.)
            else:
                ch[name] = channel(name, 'SIM no proved accumulated window/cache epoch; boot or incoherent counters',
                                   count=1 if n == 0 else None, accumulated_window_count=n)
        # ctrl was computed at the final PRE driver stage, then held. Do not call it a torque sensor.
        tau_t = t-dt if mean_known else None
        ch['motor_tau6'] = channel('motor_tau6', 'SIM final PRE driver ctrl held at publication; empty-window setter UNKNOWN',
                                   tau_t, count=1, kind='held_command', held_snapshot_epoch_s=t if known else None)
        return dict(epoch_s=t if known else None, total_samples=total, physics_tick=tick,
                    source_frame_id=self.serial, accumulated_window_count=n, channels=ch)

    def publish(self, raw, packet):
        self.serial += 1
        t = number(raw.epoch_s)
        stamp, arrival = number(getattr(packet, 'time_s', None)), number(getattr(packet, 'arrival_s', None))
        reset = bool(self.previous and ((t is not None and self.previous['epoch_s'] is not None
                       and t < self.previous['epoch_s']-TOL)
            or (integer(raw.total_samples) is not None and self.previous['total_samples'] is not None
                and int(raw.total_samples) < self.previous['total_samples'])))
        duplicate = bool(self.previous and t is not None and self.previous['epoch_s'] is not None
                         and abs(t-self.previous['epoch_s']) <= TOL)
        if reset:
            self.previous = None
        if packet is self.last_packet and self.last_metadata is not None and not reset:
            result = deepcopy(self.last_metadata)
            result.update(publication_observed_at_s=t, returned_packet_object_held=True,
                          new_source_observation=False, usable_for_alignment=False)
            for c in result['channels'].values():c['usable_for_alignment'] = False
            return result
        frame = self._frame(raw)
        age = arrival-stamp if stamp is not None and arrival is not None else None
        delayed = age is not None and age > TOL
        candidate = self.previous if delayed else frame
        reason = None
        if stamp is None or arrival is None or t is None or stamp < 0 or arrival-stamp < -TOL:
            reason = 'INVALID_OR_UNKNOWN_PACKET_CLOCK'
        elif getattr(packet, 'validity', None) is not True:
            reason = 'PACKET_VALIDITY_NOT_TRUE'
        elif abs(arrival-t) > TOL:
            reason = 'RETURNED_ARRIVAL_NOT_CURRENT_PUBLICATION'
        elif reset or duplicate:
            reason = 'SOURCE_CLOCK_RESET_OR_DUPLICATE_PUBLICATION'
        elif delayed and abs(age-.01) > TOL:
            reason = 'NOT_THE_OBSERVED_V3_ZERO_OR_ONE_100HZ_DELAY_CONTRACT'
        elif candidate is None or candidate['epoch_s'] is None:
            reason = 'PREVIOUS_SOURCE_NOT_OBSERVED_BY_THIS_WRAPPER'
        elif candidate.get('invalid_source_reason'):
            reason = candidate['invalid_source_reason']
        elif abs(candidate['epoch_s']-stamp) > TOL:
            reason = 'PACKET_SOURCE_EPOCH_MISMATCH'
        if reason:
            ch = {name: channel(name, reason) for name in ROLES}
        else:
            ch = deepcopy(candidate['channels'])
            # Torque is NOT inside the five-channel DR feedback queue.
            tau_source = self.previous if delayed and raw.previous_torque_available else frame
            ch['motor_tau6'] = (deepcopy(tau_source['channels']['motor_tau6']) if tau_source
                                else channel('motor_tau6', 'PREVIOUS_CTRL_SNAPSHOT_SOURCE_UNKNOWN'))
        result = dict(packet_epoch_s=stamp, packet_arrival_s=arrival, publication_observed_at_s=t,
            source_frame_epoch_s=candidate['epoch_s'] if reason is None else None,
            source_frame_id=candidate['source_frame_id'] if reason is None else None,
            known_pipeline_source=dict(epoch_s=candidate['epoch_s'], source_frame_id=candidate['source_frame_id'],
                accumulated_window_count=candidate['accumulated_window_count']) if candidate else None,
            channels=ch, source_selection_reason=reason or ('PREVIOUS_PUBLISHED_SOURCE' if delayed else 'CURRENT_SOURCE'),
            packet_source_epoch_mismatch=bool(candidate and candidate['epoch_s'] is not None
                and stamp is not None and abs(candidate['epoch_s']-stamp) > TOL),
            pipeline_history_reset_or_rollback=reset, duplicate_publication_epoch=duplicate,
            returned_packet_object_held=False, new_source_observation=not duplicate,
            usable_for_alignment=reason is None and all(c['timestamp_s'] is not None for c in ch.values()),
            alpha_B=None, force_input_ready=False, hardware_clock_calibrated=False,
            clock_domain='SIM_PIPELINE_TIME_NOT_HARDWARE_ACQUISITION_CALIBRATION',
            values='UNCHANGED_ORIGINAL_PACKET_ONLY; side metadata carries no sensor/actuation values',
            no_inertial_transport_or_derivative_performed=True)
        if reset or duplicate:
            frame['invalid_source_reason'] = 'PREVIOUS_SOURCE_FOLLOWS_CLOCK_RESET_OR_DUPLICATE'
        self.previous = frame
        self.last_packet, self.last_metadata = packet, deepcopy(result)
        return result

class SensorTimeMetadataMixin:
    """Use as class OptionalPlant(SensorTimeMetadataMixin, ExistingV2Plant).
    Enable explicitly after construction/reset; default OFF is literal delegation.
    Never reads root/contact/ctrl values or DR configuration/state.
    """
    sensor_time_metadata_enabled = False
    last_sensor_time_metadata = None

    def configure_sensor_time_metadata(self, enabled=False):
        if type(enabled) is not bool:raise ValueError('metadata enable requires exact bool')
        self.sensor_time_metadata_enabled = enabled
        self._sensor_time_publisher = TimeMetadataPublisher() if enabled else None
        self.last_sensor_time_metadata = None

    def sensor_packet(self):
        if self.sensor_time_metadata_enabled is not True:
            return super().sensor_packet()
        try:
            raw = FrameClock(self.d.time, self.dt, self.imu_window_count, self.total_highrate_IMU_samples,
                             self.tick_phys, self.previous_torque is not None)
        except (AttributeError, TypeError, ValueError, OverflowError):
            raw = FrameClock(None, None, None, None, None, False)
        packet = super().sensor_packet()  # Exactly once; original exceptions remain original.
        if getattr(self, '_sensor_time_publisher', None) is None:
            self._sensor_time_publisher = TimeMetadataPublisher()
        self.last_sensor_time_metadata = self._sensor_time_publisher.publish(raw, packet)
        return packet
