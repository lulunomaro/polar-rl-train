"""Read-only W35 telemetry component; no SDK import, policy, RNG draw, or writer.

This is a source candidate, not an admitted runtime or a complete WM dataset.
All tensor operations use the caller's existing torch/device. No default CUDA.
"""
import gzip
import json
import math
import types
from pathlib import Path

MODEL_SHA = 'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
METRICS = ('forward_abs_error', 'yaw_abs_error', 'height_abs_error', 'moving_world_progress_abs_error')
FAMILIES = ('outside', 'plane_for_rm', 'tiny_step', 'slope_for_rm_high', 'inv_slope_for_rm_low', 'random_uniform_for_rm')
MODES = ('gentle', 'standing', 'negative_straight', 'positive_straight', 'negative_world_yaw', 'positive_world_yaw', 'eligible_without_retained_mode')


def tensor(value):
    return value.torch if hasattr(value, 'torch') else value


class ProfileBook:
    """Fresh run-local counters; profile x actual environment denominators.

    Counts are exposure, not success. Full and steady are independently readable
    via phase0+phase1 and phase1. No legacy audit lifetime counters are consumed.
    """
    def __init__(self, torch, n, device, reason_names):
        self.t = torch
        self.n = n
        self.ids = torch.arange(n, device=device)
        self.reason_names = tuple(reason_names)
        self.count = torch.zeros((2, 42, n), dtype=torch.int64, device=device)
        self.errors = torch.zeros((2, 4, 42, n), dtype=torch.float32, device=device)
        self.terminated = torch.zeros_like(self.count)
        self.truncated = torch.zeros_like(self.count)
        self.reasons = torch.zeros((2, len(reason_names), 42, n), dtype=torch.int64, device=device)
        self.cycles = torch.zeros_like(self.count)
        self.longest_live = torch.zeros_like(self.count, dtype=torch.float32)
        self.previous_key = torch.full((n,), -1, dtype=torch.long, device=device)
        self.previous_uid = torch.full_like(self.previous_key, -1)
        self.previous_live = torch.zeros(n, dtype=torch.bool, device=device)
        self.age = torch.zeros(n, device=device)
        self.turn = torch.zeros_like(self.age)
        self.previous_phase = -1

    def observe(self, phase, key, uid, errors, heading_delta, signed_yaw, terminated, truncated, reasons):
        t = self.t
        assert phase in (0, 1) and key.shape == uid.shape == (self.n,)
        assert key.dtype == t.long and bool(((key >= 0) & (key < 42)).all())
        assert len(errors) == 4 and len(reasons) == len(self.reason_names)
        assert all(x.shape == (self.n,) and bool(t.isfinite(x).all()) for x in errors)
        assert terminated.dtype == truncated.dtype == t.bool
        assert all(x.dtype == t.bool and x.shape == (self.n,) for x in reasons)
        idx = (key, self.ids)
        self.count[phase][idx] += 1
        for m, value in enumerate(errors):
            self.errors[phase, m][idx] += value
        self.terminated[phase][idx] += terminated.to(t.int64)
        self.truncated[phase][idx] += truncated.to(t.int64)
        for m, value in enumerate(reasons):
            self.reasons[phase, m][idx] += value.to(t.int64)
        live = ~(terminated | truncated)
        same = (key == self.previous_key) & (uid == self.previous_uid) & self.previous_live
        if phase != self.previous_phase:
            same = t.zeros_like(same)
        self.age = t.where(same, self.age + .02, t.full_like(self.age, .02))
        self.turn = t.where(same, self.turn + heading_delta, heading_delta)
        current = self.longest_live[phase][idx]
        self.longest_live[phase][idx] = t.maximum(current, t.where(live, self.age, t.zeros_like(self.age)))
        moving = ((key % 7 == 4) | (key % 7 == 5)) & live & (phase == 1)
        turns = t.floor((self.turn * t.sign(signed_yaw)).clamp_min(0) / (2 * math.pi)).to(t.long)
        completed = t.where(moving, turns, t.zeros_like(turns))
        self.cycles[phase][idx] += completed
        self.turn -= t.sign(signed_yaw) * (2 * math.pi) * completed
        self.age = t.where(live, self.age, t.zeros_like(self.age))
        self.turn = t.where(live, self.turn, t.zeros_like(self.turn))
        self.previous_key = key.clone()
        self.previous_uid = uid.clone()
        self.previous_live = live.clone()
        self.previous_phase = phase

    def _views(self, scope):
        if scope == 'whole':
            return (self.count.sum(0), self.errors.sum(0), self.terminated.sum(0), self.truncated.sum(0),
                    self.reasons.sum(0), self.cycles.sum(0), self.longest_live.max(0).values)
        phase = 0 if scope == 'warmup' else 1
        return (self.count[phase], self.errors[phase], self.terminated[phase], self.truncated[phase],
                self.reasons[phase], self.cycles[phase], self.longest_live[phase])

    def summary(self):
        output = []
        for scope in ('whole', 'warmup', 'steady'):
            counts, errors, terminated, truncated, reasons, cycles, longest = self._views(scope)
            for p in range(42):
                count = counts[p]
                denominator = int(count.sum())
                means = {}
                for m, name in enumerate(METRICS):
                    applicable = m != 3 or p % 7 in (4, 5)
                    means[name] = float(errors[m, p].sum()) / denominator if denominator and applicable else None
                output.append(dict(
                    phase=scope, profile=p,
                    family=FAMILIES[p // 7], mode=MODES[p % 7],
                    population_control_denominator=denominator,
                    unique_exposed_env_denominator=int((count > 0).sum()),
                    means=means,
                    terminated_mask_events=int(terminated[p].sum()),
                    unique_env_with_terminated_mask=int((terminated[p] > 0).sum()),
                    truncated_mask_events=int(truncated[p].sum()),
                    unique_env_with_truncated_mask=int((truncated[p] > 0).sum()),
                    reason_events={name: int(reasons[j, p].sum()) for j, name in enumerate(self.reason_names)},
                    reason_unique_env={name: int((reasons[j, p] > 0).sum()) for j, name in enumerate(self.reason_names)},
                    complete_signed_cycle_events=int(cycles[p].sum()),
                    unique_env_with_complete_signed_cycle=int((cycles[p] > 0).sum()),
                    maximum_live_continuous_seconds=float(longest[p].max()),
                ))
        return output

    def condition_summary(self):
        output = []
        groups = dict(all=tuple(range(7)), gentle=(0,), standing=(1,), straight=(2, 3), moving_world_yaw=(4, 5), eligible_other=(6,))
        for scope in ('whole', 'warmup', 'steady'):
            count, errors, terminated, truncated, reasons, cycles, longest = self._views(scope)
            for name, modes in groups.items():
                profiles = [p for p in range(42) if p % 7 in modes]
                denominator = int(count[profiles].sum())
                means = {key: float(errors[m, profiles].sum()) / denominator if denominator and (m != 3 or name == 'moving_world_yaw') else None for m, key in enumerate(METRICS)}
                output.append(dict(phase=scope, condition=name, population_control_denominator=denominator,
                                   unique_exposed_env_denominator=int((count[profiles].sum(0) > 0).sum()),
                                   means=means, terminated_mask_events=int(terminated[profiles].sum()),
                                   unique_env_with_terminated_mask=int((terminated[profiles].sum(0) > 0).sum()),
                                   truncated_mask_events=int(truncated[profiles].sum()),
                                   complete_signed_cycle_events=int(cycles[profiles].sum()),
                                   unique_env_with_complete_signed_cycle=int((cycles[profiles].sum(0) > 0).sum())))
        return output

    def export_sparse_per_env(self, path):
        # New output only. No existing NPZ is opened or decoded.
        import numpy as np
        phase, profile, env_id = (self.count > 0).nonzero(as_tuple=True)
        indexes = (phase, profile, env_id)
        data = dict(phase=phase.cpu().numpy(), profile=profile.cpu().numpy(), env_id=env_id.cpu().numpy(),
                    population_controls=self.count[indexes].cpu().numpy(),
                    terminated_events=self.terminated[indexes].cpu().numpy(),
                    truncated_events=self.truncated[indexes].cpu().numpy(),
                    cycle_events=self.cycles[indexes].cpu().numpy(),
                    longest_live_seconds=self.longest_live[indexes].cpu().numpy())
        for m, name in enumerate(METRICS):
            data[name + '_sum'] = self.errors[phase, m, profile, env_id].cpu().numpy()
        for m, name in enumerate(self.reason_names):
            data['reason_' + name + '_events'] = self.reasons[phase, m, profile, env_id].cpu().numpy()
        with Path(path).open('xb') as f:
            np.savez_compressed(f, **data)


class W35DomainPanel:
    """Hooks only original queue return values, reset IDs and termination caches.

    It never changes commands, actions, reset IDs, RNG, physics, queue ordering,
    model state, or optimizer. Original exceptions propagate. The queue target
    is labelled before original articulation apply, not torque/force truth.
    """
    def __init__(self, real, torch, output, task):
        assert task['kind'] == 'MOD4_W35_ADAPTED92_PROFILE_ENV_DOMAIN_PANEL_V1'
        assert task['source_SHA'] == MODEL_SHA and task['controls'] == 600 and task['warmup_controls'] == 100
        assert real.num_envs == 20000 and real.physics_dt == .0025 and real.step_dt == .02 and real.cfg.decimation == 8
        assert real._physics_action_delay.queue.control_us == 20000
        self.real = real
        self.t = torch
        self.out = Path(output)
        self.task = task
        self.robot = real.scene['robot']
        self.names = tuple(real.termination_manager.active_terms)
        self.book = ProfileBook(torch, real.num_envs, real.device, self.names)
        self.uid = torch.zeros(real.num_envs, dtype=torch.long, device=real.device)
        self.stream = gzip.open(self.out / 'W35_selected_profile_domain_before_terminal_reset.jsonl.gz', 'xb')
        self.bytes_written = 0
        self.limit = 512 * 1024 ** 2
        self.retention_limited = False
        self.trace_controls = []
        self.frame = None
        self.selected = torch.zeros(0, dtype=torch.long, device=real.device)
        self.terminal_count = 0
        self.control = None
        self.old_apply = real._physics_action_delay.queue.apply
        self.old_reset = real._reset_idx
        self.installed = False
        self._write(dict(kind='W35_frozen_profile_domain_diagnostic_v1', source_SHA=MODEL_SHA,
                         physics_dt_s=.0025, control_dt_s=.02, decimation=8, policy_hz=50, feedback_hz=100,
                         num_envs=real.num_envs, selection='first4 current IDs per actual profile; no RNG; at trace controls only',
                         state_layout='root13+q30+dq30, not pack127',
                         queue_target_semantics='queue.apply returned processed position/velocity targets before original articulation apply, not actual torque',
                         domain=task['domain_binding'], output_retention_uncompressed_limit_bytes=self.limit,
                         no_complete_WM_dataset=True, no_skill_graduation=True))

        def apply(key, tick):
            value = self.old_apply(key, tick)
            if self.frame is not None:
                q = real._physics_action_delay.queue
                self.frame['physical_queue_targets'].append(dict(
                    group=key, physics_tick_before_integration=int(tick),
                    selected_queue_target=self._snapshot(value),
                    timing_receipt=self._snapshot(q.receipt(key, tick))))
            return value

        panel = self
        def reset(this, env_ids):
            ids = torch.as_tensor(env_ids, device=real.device, dtype=torch.long)
            # Original is called exactly once with the original argument object.
            result = panel.old_reset(env_ids)
            panel.uid[ids] += 1
            if panel.frame is not None:
                panel.frame['resets_after_terminal'].append(dict(
                    actual_reset_env_ids=ids.detach().cpu().tolist(),
                    selected_post_reset=panel._physical(),
                    selected_DR_after_reset=panel._domain()))
            return result
        real._physics_action_delay.queue.apply = apply
        real._reset_idx = types.MethodType(reset, real)
        self.installed = True

    def _snapshot(self, value, path=''):
        t = self.t
        if t.is_tensor(value):
            rng = any(x in path.lower() for x in ('rng', 'generator'))
            per_env = value.ndim > 0 and value.shape[0] == self.real.num_envs and not rng
            v = value[self.selected] if per_env else value
            return dict(dtype=str(v.dtype), shape=list(v.shape), original_shape=list(value.shape),
                        axis0_is_selected_env=per_env, value=v.detach().cpu().tolist())
        if isinstance(value, dict):
            return {str(k): self._snapshot(v, path + '/' + str(k)) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [self._snapshot(v, path + '/' + str(i)) for i, v in enumerate(value)]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        raise TypeError('Unsupported actual domain value at ' + path + ': ' + type(value).__name__)

    def _physical(self):
        r = self.robot
        return dict(env_ids=self.selected.detach().cpu().tolist(), local_episode_uid=self._snapshot(self.uid),
                    root13=self._snapshot(tensor(r.data.root_state_w)),
                    q30=self._snapshot(tensor(r.data.joint_pos)), dq30=self._snapshot(tensor(r.data.joint_vel)),
                    ground_z=self._snapshot(self.real._mod4_ground_z))

    def _domain(self):
        e = self.real
        # Existing restored objects only; lazy constructors/getters are avoided.
        data = dict(sensor_DR=e._sensor_mild.state_dict(), feedback_delay=e._feedback_delay_mild.state_dict(),
                    physical_action_delay=e._physics_action_delay.state_dict(),
                    spring_pressure=e._spring_pressure.state_dict(), gas_damping=e._gas_damping.state_dict(),
                    chassis_COM=e._chassis_com.state_dict(), chassis_PD=e._explicit_pd.state_dict(),
                    actual_cached_stiffness_N_m=tensor(self.robot.data.joint_stiffness)[:, e._spring_pressure.ids],
                    actual_cached_damping_N_s_m=tensor(self.robot.data.joint_damping)[:, e._spring_pressure.ids],
                    nominal_stiffness_N_m=e._spring_pressure.nominal)
        return self._snapshot(data)

    def _write(self, row):
        raw = (json.dumps(row, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
        if self.bytes_written + len(raw) > self.limit:
            self.retention_limited = True
            return False
        self.stream.write(raw)
        self.bytes_written += len(raw)
        return True

    def begin(self, index, ctx):
        assert self.control is None
        self.control = index
        self.start_tick = int(self.real._integrated_contact.tick)
        self.start_feedback = int(self.real._feedback_100hz_tick)
        self.before_uid = self.uid.clone()
        self.terminal_count = 0
        self.frame = None
        if not self.retention_limited and (index < 24 or (index >= 100 and (index - 100) % 10 == 0)):
            selected = [(ctx['profile_key'] == p).nonzero(as_tuple=True)[0][:4] for p in range(42)]
            self.selected = self.t.cat(selected)
            self.frame = dict(control=index+1, phase='warmup' if index < 100 else 'steady',
                              start_physics_tick=self.start_tick, start_feedback_tick=self.start_feedback,
                              actual_before=self._physical(), DR_before=self._domain(),
                              profile_key_before=self._snapshot(ctx['profile_key']),
                              actual_command3=self._snapshot(ctx['command']),
                              world_direction=self._snapshot(ctx['direction']),
                              physical_queue_targets=[], resets_after_terminal=[])

    def requested(self, action, obs):
        if self.frame is not None:
            self.frame['raw_actor_ingress6'] = self._snapshot(action)
            self.frame['observations_given_to_original_actor'] = self._snapshot(obs)

    def terminal(self, ctx):
        self.terminal_count += 1
        assert self.terminal_count == 1
        t, e, r = self.t, self.real, self.robot
        tm = e.termination_manager
        key = ctx['profile_key']
        moving = (key % 7 == 4) | (key % 7 == 5)
        assert bool(t.equal(moving, ctx['moving']))
        heading = tensor(r.data.heading_w)
        delta = t.atan2(t.sin(heading - ctx['heading']), t.cos(heading - ctx['heading']))
        world = tensor(r.data.root_lin_vel_w)
        progress = world[:, 0] * t.cos(ctx['direction']) + world[:, 1] * t.sin(ctx['direction'])
        errors = [(ctx['command'][:, 0] - tensor(r.data.root_lin_vel_b)[:, 0]).abs(),
                  (ctx['command'][:, 2] - tensor(r.data.root_ang_vel_b)[:, 2]).abs(),
                  (tensor(r.data.root_pos_w)[:, 2] - e._mod4_ground_z - .25).abs(),
                  t.where(moving, (progress - .5).abs(), t.zeros_like(progress))]
        self.book.observe(0 if self.control < 100 else 1, key, self.before_uid, errors, delta, ctx['command'][:, 2],
                          tm.terminated, tm.time_outs, [tm.get_term(n).bool() for n in self.names])
        if self.frame is not None:
            self.frame['terminal_before_autoreset'] = self._physical()
            self.frame['DR_terminal_before_autoreset'] = self._domain()
            self.frame['action_manager_ingress6_after_original_processing'] = self._snapshot(e.action_manager.action)
            self.frame['terminated_mask'] = self._snapshot(tm.terminated)
            self.frame['truncated_mask'] = self._snapshot(tm.time_outs)
            self.frame['reason_masks'] = {n: self._snapshot(tm.get_term(n).bool()) for n in self.names}

    def after_step(self, done, info):
        assert self.terminal_count == 1
        assert int(self.real._integrated_contact.tick) - self.start_tick == 8
        assert int(self.real._feedback_100hz_tick) - self.start_feedback == 2
        if self.frame is not None:
            for group in ('legs', 'wheels'):
                ticks = [x['physics_tick_before_integration'] for x in self.frame['physical_queue_targets'] if x['group'] == group]
                assert ticks == list(range(self.start_tick, self.start_tick + 8)), (group, ticks, self.start_tick)
            self.frame['end_physics_tick'] = int(self.real._integrated_contact.tick)
            self.frame['end_feedback_tick'] = int(self.real._feedback_100hz_tick)
            self.frame['returned_done_after_autoreset'] = self._snapshot(done)
            self.frame['returned_info_keys_only'] = sorted(info)
            self.frame['post_step_after_autoreset'] = self._physical()
            if self._write(self.frame):
                self.trace_controls.append(self.control + 1)
        self.frame = None
        self.control = None

    def uninstall(self):
        if self.installed:
            self.real._physics_action_delay.queue.apply = self.old_apply
            self.real._reset_idx = self.old_reset
            self.installed = False
        self.stream.close()

    def finish(self):
        assert self.control is None
        self.uninstall()
        self.book.export_sparse_per_env(self.out / 'W35_profile_phase_env_fresh_denominators_sums_events.npz')
        report = dict(kind='W35_profile_env_domain_panel_diagnostic_v1', source_SHA=MODEL_SHA,
                      profile_phase_metrics=self.book.summary(), condition_phase_metrics=self.book.condition_summary(), trace_controls=self.trace_controls,
                      trace_uncompressed_bytes=self.bytes_written, trace_retention_limited=self.retention_limited,
                      actual_local_episode_uid_final=self.uid.detach().cpu().tolist(),
                      domain_binding=self.task['domain_binding'],
                      errors_are_actual_population_control_weighted=True,
                      continuous_definition='live completed intervals only; break on profile/phase/episode change or done; no cross-reset credit',
                      unique_env_is_not_unique_episode=True, signed_cycle_event_is_not_unique_env=True,
                      no_per_profile_success_threshold_invented=True,
                      complete_WM_dataset=False, skill_graduation=False,
                      pending='Actual SDK/fullrestore/clock/hook non-interference/runtime performance and profile coverage admission; original legacy graduation thresholds remain external')
        with (self.out / 'W35_PROFILE_ENV_DOMAIN_PANEL_ACTUAL.json').open('x', encoding='utf-8') as f:
            json.dump(report, f, indent=2, allow_nan=False)
