"""Private grading-only instrumentation: observe, never recompute actuation.
Mixin calls the existing clip/apply/contact methods exactly once. No sensor
publication, model construction, integration, driver, geometry or DR changes.
Do not feed these simulator-side diagnostics into a controller/proxy/FSM.
"""
import numpy as np


class ActuationTelemetryMixin:
    def __init__(self, *args, motor_telemetry=False, **kwargs):
        self.motor_telemetry_enabled = bool(motor_telemetry)
        self._mt_active = False
        self.motor_telemetry_window = []
        self.motor_telemetry_summary = {'enabled': False, 'complete': False}
        super().__init__(*args, **kwargs)

    def apply_torque_request(self, *args, **kwargs):
        if not self.motor_telemetry_enabled:
            self.motor_telemetry_window = []
            self.motor_telemetry_summary = {'enabled': False, 'complete': False}
            return super().apply_torque_request(*args, **kwargs)
        self.motor_telemetry_window = []
        self._mt_clips = {}
        self._mt_active = True
        self._mt_start_tick = int(self.tick_phys)
        self._mt_projection_start = int(getattr(self, 'target_projection_calls', 0))
        complete = False
        try:
            result = super().apply_torque_request(*args, **kwargs)
            complete = True
            return result
        finally:
            self._mt_active = False
            rows = self.motor_telemetry_window
            good = all(len(row['clip_stages']) == 2 for row in rows)
            counts = [[0] * 6 for _ in range(2)]
            for row in rows:
                for stage, record in enumerate(row['clip_stages'][:2]):
                    for j, changed in enumerate(record['changed6']):
                        counts[stage][j] += int(changed)
            ticks = int(self.tick_phys) - self._mt_start_tick
            self.motor_telemetry_summary = dict(
                enabled=True, complete=bool(complete and good and len(rows) == ticks and not self._mt_clips),
                actual_observed_substeps=len(rows), driver_tick_delta=ticks,
                first_dc_changed_ticks6=counts[0], post_gain_dc_changed_ticks6=counts[1],
                first_dc_changed_duty6=[v / len(rows) if rows else None for v in counts[0]],
                post_gain_dc_changed_duty6=[v / len(rows) if rows else None for v in counts[1]],
                target_rewrite_or_lift_count=int(getattr(self, 'target_projection_calls', 0))-self._mt_projection_start,
                controller_truth_input=False, sensor_packet_modified=False,
                note='Changed means exact input/output difference at the existing clip call; not rail occupancy, current/thermal clipping or hardware delivery')

    def clip(self, tau):
        active = self._mt_active
        before = np.asarray(tau, dtype=float).copy() if active else None
        result = super().clip(tau)
        if active:
            tick = int(self.tick_phys)
            records = self._mt_clips.setdefault(tick, [])
            records.append(dict(
                stage='first_signed_DC' if not records else 'post_gain_signed_DC' if len(records)==1 else 'unexpected_extra_clip',
                before_tau6=before.tolist(), after_tau6=np.asarray(result).copy().tolist(),
                changed6=np.not_equal(before, np.asarray(result)).tolist(),
                speed6_pre=np.asarray(self.d.qvel[self.vids]).copy().tolist()))
        return result

    def _grade_contact_sample(self):
        # Preserve original grading callback and call order after mj_step.
        result = super()._grade_contact_sample()
        if self._mt_active:
            previous_tick = int(self.tick_phys) - 1
            records = self._mt_clips.pop(previous_tick, [])
            self.motor_telemetry_window.append(dict(
                physics_tick_pre=previous_tick,
                time_s_post=float(self.d.time), time_s_pre=float(self.d.time)-float(self.dt),
                cache_contact_time_is_pre_step=True,
                clip_stages=records,
                held_ctrl_tau6=np.asarray(self.d.ctrl).copy().tolist(),
                post_clip_mechanical_power_stage_may_differ=True,
                request_is_not_measured_torque=True))
        return result
