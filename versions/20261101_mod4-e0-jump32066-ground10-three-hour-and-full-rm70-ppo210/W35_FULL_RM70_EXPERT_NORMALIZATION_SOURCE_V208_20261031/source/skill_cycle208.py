"""Complete original W35 cycle fields; consumes only natural caller buffers.

The legacy producer and its old records are frozen. This extends its NEW rows,
never reads the consumed 5039-row stream, and adds no sampler/actor/physics call.
"""
import math
from w35_base208 import W35UIDCycleBook


class FullWorldCycle208(W35UIDCycleBook):
    def __init__(self, t, n, device, out):
        super().__init__(t, n, device, out)
        self.cross = t.zeros(n, device=device)
        self.actual_signed_yaw = self.cross.clone()
        self.command_signed_yaw = self.cross.clone()
        self.ended_non_timeout = t.zeros(n, device=device, dtype=t.bool)
        self.ended_timeout = self.ended_non_timeout.clone()
        self.first_tick208 = t.zeros(n, device=device, dtype=t.long)
        self.last_tick208 = self.first_tick208.clone()
        self.term_reasons208 = {}
        self.strict_counts208 = dict(observed_pass_events=0, observed_false_events=0,
                                     incomplete_events=0, terminal_complete_events=0)

    def begin(self, cmd, ctx):
        super().begin(cmd, ctx)
        ids = self.ids[self.cycle_active & (self.cycle_count == 0)]
        for value in (self.cross, self.actual_signed_yaw, self.command_signed_yaw):
            value[ids] = 0
        self.ended_non_timeout[ids] = False
        self.ended_timeout[ids] = False
        self.first_tick208[ids] = int(cmd._env._sim_step_counter)
        self.last_tick208[ids] = int(cmd._env._sim_step_counter)
        ctx['physics_begin_tick208'] = int(cmd._env._sim_step_counter)

    def observe208(self, ctx, root_xy, heading, errors, terminated, truncated,
                   *, physics_end_tick, termination_reasons):
        t = self.t
        if physics_end_tick != ctx['physics_begin_tick208'] + 8:
            raise ValueError('Need the original eight 2500us physics callbacks')
        if not all(bool(t.isfinite(x).all()) for x in
                   (root_xy, heading, ctx['before_root_xy'], ctx['command'])):
            raise ValueError('Nonfinite natural pre-reset frame')
        self.term_reasons208 = {k: v.clone() for k, v in termination_reasons.items()}
        ids = self.ids[self.cycle_active]
        delta_xy = root_xy - ctx['before_root_xy']
        cross = -delta_xy[:, 0] * t.sin(ctx['direction']) + delta_xy[:, 1] * t.cos(ctx['direction'])
        signed_delta = t.atan2(t.sin(heading - ctx['heading']), t.cos(heading - ctx['heading']))
        self.cross[ids] += cross[ids]
        self.actual_signed_yaw[ids] += signed_delta[ids]
        self.command_signed_yaw[ids] += .02 * ctx['command'][ids, 2]
        self.last_tick208[ids] = physics_end_tick
        self.ended_non_timeout[ids] |= terminated[ids]
        self.ended_timeout[ids] |= truncated[ids]
        super().observe_original_terminal(ctx, root_xy, heading, errors, terminated, truncated)

    def _write_columns(self, writer, columns, extra):
        if writer is self.cycle_records:
            ids = columns['env_id']; t = self.t
            seconds = self.cycle_count[ids].float() * .02
            positive = seconds > 0
            safe = t.where(positive, seconds, t.ones_like(seconds))
            along = self.cycle_progress[ids] / safe
            cross = self.cross[ids] / safe
            yaw_error = (self.actual_signed_yaw[ids] - self.command_signed_yaw[ids]) / safe
            complete = bool(extra['complete_sampled_span'])
            tolerance = max(.03, .1 * .5)  # original W35 V=.5, never a new threshold
            passes = (along - .5).abs() <= tolerance
            passes &= cross.abs() <= tolerance
            passes &= yaw_error.abs() <= .2
            columns = dict(columns,
                original_episode_uid=self.source_episode[ids],
                first_physics_tick=self.first_tick208[ids], last_physics_tick=self.last_tick208[ids],
                complete_seconds=seconds,
                actual_world_cross_displacement_m=self.cross[ids],
                actual_world_cross_speed_m_s=cross,
                actual_signed_yaw_increment_rad=self.actual_signed_yaw[ids],
                original_commanded_signed_yaw_integral_rad=self.command_signed_yaw[ids],
                signed_yaw_error_rad_s=yaw_error,
                original_along_error_m_s=along - .5,
                original_along_cross_tolerance_m_s=t.full_like(seconds, tolerance),
                original_signed_yaw_tolerance_rad_s=t.full_like(seconds, .2),
                non_timeout_before_reset=self.ended_non_timeout[ids],
                timeout_before_reset=self.ended_timeout[ids],
                original_strict_cycle_observed_pass=passes & positive & complete)
            for name, mask in self.term_reasons208.items():
                columns['original_terminal_reason_' + name] = mask[ids]
            extra = dict(extra, schema_extension='W35_full_world_signed_cycle208_v1',
                cross_reference='fixed original sampled world direction; perpendicular left',
                signed_yaw_reference='integral of original acted command[:,2]; not abs(yaw)',
                incomplete_fields_are_diagnostics_not_a_pass=not complete,
                pre_reset_endpoint_only=True, no_new_aggregate_pass_rate=True)
            if complete:
                self.strict_counts208['observed_pass_events'] += int(passes.sum())
                self.strict_counts208['observed_false_events'] += int((~passes).sum())
                self.strict_counts208['terminal_complete_events'] += int((
                    self.ended_non_timeout[ids] | self.ended_timeout[ids]).sum())
            else:
                self.strict_counts208['incomplete_events'] += len(ids)
        return super()._write_columns(writer, columns, extra)

    def finish(self):
        value = super().finish()
        value['full_world208'] = dict(self.strict_counts208,
            thresholds='original max(.03,.1V) along/cross and .2rad/s signed yaw',
            no_new_aggregate_pass_rate=True, full_skill_graduation=False,
            actual_WM_dataset=False,
            note='Every false, terminal and partial row remains; unexposed profiles stay UNKNOWN')
        return value
