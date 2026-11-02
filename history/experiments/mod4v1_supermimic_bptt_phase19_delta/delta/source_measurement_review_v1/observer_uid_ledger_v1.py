"""SOURCE-ONLY E2/W35 observer, stdlib only. Never import or call an environment.

Inputs must be detached scalar copies made by a separate future native-validation
owner at the documented points. This module neither installs hooks nor reads old
streams/checkpoints. Original predicates and conditional denominators stay exact.
A Boolean measured here is not expert qualification or runtime getter validation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

DT = 0.02
PHYSICS_DT = 0.0025
SUBSTEPS = 8


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def heading_xyzw(q: tuple[float, ...]) -> float:
    x, y, z, w = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def finite(values: Any) -> bool:
    if values is None:
        return False
    if isinstance(values, (list, tuple)):
        return all(finite(v) for v in values)
    return isinstance(values, (int, float)) and not isinstance(values, bool) and math.isfinite(values)


def classify_e2(standing: bool, pure: bool, moving: bool, transition: bool,
                body_vx: float, signed_yaw: float) -> int:
    """Scalar equivalent of original catalogue lines 5-15; no speed proxy."""
    if any(type(v) is not bool for v in (standing, pure, moving, transition)):
        raise ValueError("Original E2 Boolean flags required")
    if (standing and (pure or moving)) or (pure and moving) or (transition and not pure):
        raise ValueError("Original E2 flag exclusivity mismatch")
    if standing:
        return 0
    if not (standing or pure or moving):
        return 1 if body_vx < 0 else 2 if body_vx == 0 else 3
    if signed_yaw == 0:
        raise ValueError("Unclassified actual E2 command flags; no silent profile replacement")
    if moving:
        return 8 if signed_yaw < 0 else 9
    if transition:
        return 6 if signed_yaw < 0 else 7
    return 4 if signed_yaw < 0 else 5


@dataclass(frozen=True)
class Command:
    body: Optional[tuple[float, float, float]] = None
    profile: Optional[int] = None
    world_direction: Optional[float] = None
    signed_yaw: Optional[float] = None
    sampled_heading: Optional[float] = None
    standing: Optional[bool] = None
    is_pure_spin: Optional[bool] = None
    is_moving_spin: Optional[bool] = None
    is_transition_spin: Optional[bool] = None
    source_episode: Optional[int] = None
    original_counter: Optional[int] = None
    unused_random_direction: Optional[float] = None
    # Supplied by preregistered paired native sampling, never inferred from counts.
    cohort_event_uid: Optional[str] = None


@dataclass(frozen=True)
class Capture:
    control: int
    tick: int
    stage: str
    root_pos_w_xy: Optional[tuple[float, float]] = None
    heading_w: Optional[float] = None
    # Original W35 pre-reset frame['root']; world xyz, xyzw, velocities.
    root_state_w: Optional[tuple[float, ...]] = None
    frame_capture_physics_tick: Optional[int] = None
    frame_capture_sim_step_counter: Optional[int] = None
    frame_capture_feedback_tick: Optional[int] = None
    frame_identity: Optional[dict[str, Any]] = None
    feedback_tick: Optional[int] = None
    sim_step_counter: Optional[int] = None
    root_link_pos_w: Optional[tuple[float, float, float]] = None
    root_com_pos_w: Optional[tuple[float, float, float]] = None
    root_link_quat_xyzw: Optional[tuple[float, float, float, float]] = None
    root_com_quat_xyzw: Optional[tuple[float, float, float, float]] = None
    env_origin_xyz: Optional[tuple[float, float, float]] = None
    native_packed_local_xyz: Optional[tuple[float, float, float]] = None
    getter_cache: Optional[dict[str, Any]] = None
    caller_read_order: Optional[tuple[str, ...]] = None
    active_backend_type: Optional[str] = None
    active_backend_source_sha: Optional[str] = None


@dataclass(frozen=True)
class Provenance:
    run_uid: str
    task: str
    candidate_actor_sha: Optional[str] = None
    source_manifest_sha: Optional[str] = None
    seed: Optional[int] = None
    cohort_namespace: Optional[str] = None
    reference_frame_and_sample_phase_validated: Optional[bool] = None
    actual_frozen_validation_result: Optional[bool] = None


class ExclusiveJsonlSink:
    """Optional NEW-run writer. Exclusive create, no pruning, no input reads.

    A capacity limit raises before loss, and the validation owner must mark the
    run observation-incomplete. No silently truncated stream is a passing run.
    """
    def __init__(self, path: str | Path, maximum_bytes: Optional[int] = None):
        self.path = Path(path)
        self.file = self.path.open("xb")
        self.maximum_bytes = maximum_bytes
        self.bytes = self.rows = 0
        self.digest = hashlib.sha256()

    def __call__(self, row: dict[str, Any]) -> None:
        raw = canonical(row) + b"\n"
        if self.maximum_bytes is not None and self.bytes + len(raw) > self.maximum_bytes:
            raise BufferError("Observer retention limit: abort measurement scope; no dropped rows")
        self.file.write(raw)
        self.digest.update(raw)
        self.bytes += len(raw)
        self.rows += 1

    def finish(self) -> dict[str, Any]:
        self.file.close()
        return {"path": str(self.path), "bytes": self.bytes, "rows": self.rows,
                "SHA256": self.digest.hexdigest(), "stream_hashed_without_reread": True}


@dataclass
class EnvUID:
    episode: int = 0
    command: int = 0
    command_start_observed: bool = False
    episode_start_observed: bool = False
    sample_packet: Optional[Command] = None
    resample_pending: bool = False


class UIDLedger:
    """Explicit event UIDs, run/task/env scoped. Not source-counter aliases.

    Zero is observer arm origin, not proof of a reset/sample at time zero. Source
    _e1_episode and command_counter stay independent nullable fields. Equal local
    integers in two runs are never asserted to identify a matched command cohort.
    """
    def __init__(self, provenance: Provenance, emit: Callable[[dict], None]):
        self.provenance = provenance
        self.emit = emit
        self.envs: dict[int, EnvUID] = {}
        self.sequence = 0

    def state(self, env_id: int) -> EnvUID:
        if type(env_id) is not int or env_id < 0:
            raise ValueError("Nonnegative integer env_id required")
        return self.envs.setdefault(env_id, EnvUID())

    def identity(self, env_id: int) -> dict[str, Any]:
        state = self.state(env_id)
        return {"run_uid": self.provenance.run_uid, "task": self.provenance.task,
                "env_id": env_id, "episode_uid": state.episode,
                "command_uid": state.command,
                "uid_origin": "explicit_events_zero_at_observer_arm_v1"}

    def event(self, env_id: int, kind: str, tick: int, **extra: Any) -> None:
        self.sequence += 1
        self.emit({"record_type": "uid_boundary", **self.identity(env_id),
                   "event_sequence": self.sequence, "kind": kind, "tick": tick, **extra})

    def initial_sample(self, env_id: int, tick: int, command: Command,
                       exact_initial_packet_verified: bool) -> None:
        s = self.state(env_id)
        s.command_start_observed = exact_initial_packet_verified
        s.episode_start_observed = exact_initial_packet_verified
        s.sample_packet = command
        self.event(env_id, "initial_packet", tick,
                   exact_initial_packet_verified=exact_initial_packet_verified,
                   command=asdict(command))

    def reset(self, env_id: int, tick: int) -> None:
        s = self.state(env_id)
        s.episode += 1
        s.episode_start_observed = True
        s.command_start_observed = False
        self.event(env_id, "reset_begin_before_original_reset", tick)

    def sample_after(self, env_id: int, tick: int, command: Command) -> None:
        s = self.state(env_id)
        if not s.resample_pending:
            raise ValueError("sample_after requires explicit sample_before event")
        s.resample_pending = False
        s.command += 1
        s.command_start_observed = True
        s.sample_packet = command
        self.event(env_id, "sample_after_original", tick, command=asdict(command),
                   command_packet_SHA256=sha(asdict(command)))


def capture_audit(capture: Capture) -> dict[str, Any]:
    """Exact residuals only. No guessed cache timestamps or acceptance gates."""
    c = capture
    def sub(a: Any, b: Any, n: int) -> Any:
        return [a[i] - b[i] for i in range(n)] if finite(a) and finite(b) else None
    root_xy = c.root_state_w[:2] if c.root_state_w is not None else None
    root_heading = heading_xyzw(c.root_state_w[3:7]) if c.root_state_w is not None and len(c.root_state_w) >= 7 and finite(c.root_state_w) else None
    local = tuple(c.root_state_w[i] - c.env_origin_xyz[i] for i in range(3)) if c.root_state_w is not None and finite(c.root_state_w) and finite(c.env_origin_xyz) else None
    return {"root_pos_minus_root_state_xy": sub(c.root_pos_w_xy, root_xy, 2),
            "root_pos_minus_actor_xy": sub(c.root_pos_w_xy, c.root_link_pos_w, 2),
            "root_pos_minus_COM_xy": sub(c.root_pos_w_xy, c.root_com_pos_w, 2),
            "actor_minus_COM_xyz": sub(c.root_link_pos_w, c.root_com_pos_w, 3),
            "heading_w_minus_root_state_heading_wrapped": wrap(c.heading_w - root_heading) if finite(c.heading_w) and finite(root_heading) else None,
            "packed_local_minus_root_world_minus_origin_xyz": sub(c.native_packed_local_xyz, local, 3),
            "frame_capture_physics_tick": c.frame_capture_physics_tick,
            "frame_age_physics_ticks": c.tick - c.frame_capture_physics_tick if c.frame_capture_physics_tick is not None else None,
            "frame_capture_sim_step_counter": c.frame_capture_sim_step_counter,
            "frame_capture_feedback_tick": c.frame_capture_feedback_tick,
            "frame_identity": c.frame_identity,
            "getter_cache": c.getter_cache, "caller_read_order": c.caller_read_order,
            "backend_type": c.active_backend_type, "backend_source_sha": c.active_backend_source_sha,
            "same_point_and_cache_phase_validated": None}


@dataclass
class Span:
    env_id: int
    identity: dict[str, Any]
    command: Command
    number: int
    start_observed: bool
    first_control: int
    first_tick: int
    axis: float
    nominal: float
    sign: float
    segment: int = 0
    controls: int = 0
    last_control: Optional[int] = None
    last_tick: Optional[int] = None
    along: float = 0.0
    cross: float = 0.0
    turn: float = 0.0
    commanded_yaw: float = 0.0
    reference_along: float = 0.0
    reference_cross: float = 0.0
    terminated: bool = False
    truncated: bool = False
    crossed_phase: bool = False
    reasons: dict[str, bool] = field(default_factory=dict)


class MeasurementObserver:
    """Consume copied events only; no actor/getter/update/reset/step calls."""
    def __init__(self, provenance: Provenance, sink: Optional[Callable[[dict], None]] = None):
        if provenance.task not in ("E2", "W35"):
            raise ValueError("Only E2 and W35 original predicates are implemented")
        self.provenance = provenance
        self.rows: list[dict[str, Any]] = []
        self.sink = sink
        self.uid = UIDLedger(provenance, self._emit)
        self.spans: dict[int, Span] = {}
        self.pending: dict[int, tuple[Command, Capture]] = {}
        self.last_end: dict[int, tuple[int, int]] = {}
        self.numbers: dict[int, int] = {}
        self.segments: dict[int, int] = {}
        self.integrity_gaps: list[dict[str, Any]] = []

    def _emit(self, row: dict[str, Any]) -> None:
        row = {"schema": "mod4.source_measurement_review.v1", **row,
               "provenance": asdict(self.provenance)}
        canonical(row)  # Fail on NaN/Inf; never coerce to zero.
        if self.sink is not None:
            self.sink(row)
        # The full control stream lives in the exclusive writer when provided;
        # retain only lightweight boundary/attempt rows for in-memory accounting.
        if self.sink is None or row.get("record_type") != "control_capture":
            self.rows.append(row)

    def _gap(self, env_id: int, reason: str, control: Optional[int] = None) -> None:
        gap = {**self.uid.identity(env_id), "reason": reason, "control": control}
        self.integrity_gaps.append(gap)
        if env_id in self.spans:
            self._close(env_id, "measurement_gap:" + reason, None)
        self._emit({"record_type": "measurement_gap", **gap,
                    "original_accepted": None, "conditional_denominator": None})

    def initial_packet(self, env_id: int, tick: int, command: Command,
                       exact_initial_packet_verified: bool) -> None:
        if env_id in self.pending or env_id in self.spans:
            raise ValueError("Initial packet must precede measured controls")
        self.uid.initial_sample(env_id, tick, command, exact_initial_packet_verified)

    def _new_span(self, env_id: int, command: Command, c: Capture) -> bool:
        state = self.uid.state(env_id)
        if self.provenance.task == "W35" and state.command_start_observed and state.sample_packet is not None:
            # Original open() samples body/axis/group/counter at resample, while
            # begin() first records source _e1_episode; acted body stays current.
            command = replace(state.sample_packet, source_episode=command.source_episode)
        if self.provenance.task == "E2":
            if command.profile not in (8, 9):
                if command.profile is None:
                    self._gap(env_id, "missing_original_E2_profile", c.control)
                return False
            if not finite(command.world_direction) or not finite(command.signed_yaw) or command.signed_yaw == 0:
                self._gap(env_id, "missing_original_E2_direction_or_sign", c.control)
                return False
            axis, v, sign = command.world_direction, 0.5, math.copysign(1.0, command.signed_yaw)
        else:
            if not finite(command.body) or not finite(command.sampled_heading) or type(command.standing) is not bool or command.source_episode is None or command.original_counter is None:
                self._gap(env_id, "missing_original_W35_command_axis_group_or_source_identity", c.control)
                return False
            axis = command.sampled_heading + (math.pi if command.body[0] < 0 else 0.0)
            v, sign = abs(command.body[0]), 0.0
        self.numbers[env_id] = self.numbers.get(env_id, 0) + 1
        state = self.uid.state(env_id)
        span = Span(env_id, self.uid.identity(env_id), command, self.numbers[env_id],
                    state.command_start_observed, c.control, c.tick, axis, v, sign,
                    segment=self.segments.get(env_id, 0))
        self.spans[env_id] = span
        self._emit({"record_type": "attempt_open", **span.identity,
                    "attempt_number": span.number, "same_UID_segment": span.segment,
                    "first_control": c.control, "first_tick": c.tick,
                    "start_observed": span.start_observed, "command": asdict(command),
                    "group": self._group(span), "command_packet_SHA256": sha(asdict(command))})
        return True

    def _same(self, span: Span, command: Command, env_id: int) -> bool:
        now = self.uid.identity(env_id)
        if any(span.identity[k] != now[k] for k in ("episode_uid", "command_uid")):
            return False
        old = span.command
        if self.provenance.task == "E2":
            return (command.profile == old.profile and command.world_direction == old.world_direction
                    and finite(command.signed_yaw) and command.signed_yaw != 0
                    and math.copysign(1, command.signed_yaw) == span.sign)
        return command.body == old.body and command.source_episode == old.source_episode

    def begin(self, env_id: int, command: Command, before: Capture) -> None:
        if before.stage != "before_control":
            raise ValueError("begin requires before_control copy")
        if env_id in self.pending:
            raise ValueError("Previous control is missing pre-reset endpoint")
        previous = self.last_end.get(env_id)
        if previous is not None and (before.tick != previous[1] or before.control != previous[0] + 1):
            self._gap(env_id, "nonconsecutive_physics_or_control", before.control)
        span = self.spans.get(env_id)
        if span is not None and not self._same(span, command, env_id):
            self._close(env_id, "original_UID_episode_profile_direction_sign_or_parameter_break", False)
            if self.provenance.task == "W35":
                self.segments[env_id] = self.segments.get(env_id, 0) + 1
                self.uid.state(env_id).command_start_observed = False
        if env_id not in self.spans:
            self._new_span(env_id, command, before)
        self.pending[env_id] = (command, before)

    def endpoint(self, env_id: int, after: Capture, terminated: bool, truncated: bool,
                 reason_masks: Optional[dict[str, bool]] = None,
                 reason_timeout_flags: Optional[dict[str, bool]] = None) -> None:
        if after.stage != "after_control_pre_reset":
            raise ValueError("endpoint requires pre-reset copy; post-reset state is not endpoint")
        if type(terminated) is not bool or type(truncated) is not bool:
            raise ValueError("Original terminal Boolean masks required")
        command, before = self.pending.pop(env_id)
        if after.control != before.control or after.tick != before.tick + SUBSTEPS:
            self._gap(env_id, "Need original eight2.5ms applied substeps", before.control)
            self.last_end[env_id] = (after.control, after.tick)
            return
        self.last_end[env_id] = (after.control, after.tick)
        audit = {"record_type": "control_capture", **self.uid.identity(env_id),
                 "command": asdict(command), "before": asdict(before), "after": asdict(after),
                 "before_getter_audit": capture_audit(before), "after_getter_audit": capture_audit(after),
                 "physics_delta": after.tick - before.tick,
                 "feedback_delta": after.feedback_tick - before.feedback_tick if after.feedback_tick is not None and before.feedback_tick is not None else None,
                 "terminated_before_reset": terminated, "truncated_before_reset": truncated,
                 "original_reason_masks": reason_masks, "original_reason_timeout_flags": reason_timeout_flags}
        self._emit(audit)
        if reason_masks is not None and reason_timeout_flags is not None:
            if set(reason_masks) != set(reason_timeout_flags) or any(type(v) is not bool for v in (*reason_masks.values(), *reason_timeout_flags.values())):
                self._gap(env_id, "original_terminal_reason_schema_mismatch", before.control)
                return
            term = any(v for k, v in reason_masks.items() if not reason_timeout_flags[k])
            trunc = any(v for k, v in reason_masks.items() if reason_timeout_flags[k])
            if (term, trunc) != (terminated, truncated):
                self._gap(env_id, "original_terminal_reason_OR_mismatch", before.control)
                return
        span = self.spans.get(env_id)
        if span is None:
            return
        if not finite(command.body) or not finite(before.root_pos_w_xy) or not finite(before.heading_w):
            self._gap(env_id, "missing_or_nonfinite_before_measurement", before.control)
            return
        if self.provenance.task == "E2":
            xy, heading = after.root_pos_w_xy, after.heading_w
        else:
            root = after.root_state_w
            xy = root[:2] if root is not None and len(root) >= 7 else None
            heading = heading_xyzw(root[3:7]) if root is not None and len(root) >= 7 and finite(root) else None
        if not finite(xy) or not finite(heading):
            self._gap(env_id, "missing_or_nonfinite_original_endpoint_getter", before.control)
            return
        dx, dy = xy[0] - before.root_pos_w_xy[0], xy[1] - before.root_pos_w_xy[1]
        co, si = math.cos(span.axis), math.sin(span.axis)
        span.along += dx * co + dy * si
        span.cross += -dx * si + dy * co
        span.turn += wrap(heading - before.heading_w)
        angle = before.heading_w - span.axis
        span.reference_along += DT * (command.body[0] * math.cos(angle) - command.body[1] * math.sin(angle))
        span.reference_cross += DT * (command.body[0] * math.sin(angle) + command.body[1] * math.cos(angle))
        span.commanded_yaw += DT * command.body[2]
        span.controls += 1
        span.last_control, span.last_tick = before.control, after.tick
        span.crossed_phase |= (span.first_control < 100) != (before.control < 100)
        span.terminated |= terminated
        span.truncated |= truncated
        for key, value in (reason_masks or {}).items():
            span.reasons[key] = span.reasons.get(key, False) or value
        if self.provenance.task == "E2":
            if span.turn * span.sign >= 2 * math.pi:
                self._close(env_id, "original_sampled_signed_2pi_endpoint", True)
            elif terminated or truncated:
                self._close(env_id, "original_terminal_before_reset", False)

    def resample_before(self, env_id: int, tick: int, timer_before: Optional[float],
                        within_reset: bool) -> None:
        if env_id in self.pending:
            raise ValueError("Resample boundary occurred before pre-reset endpoint was delivered")
        state = self.uid.state(env_id)
        if state.resample_pending:
            raise ValueError("Nested sample event without matching sample_after")
        natural = None if timer_before is None else timer_before <= 0 and not within_reset
        if self.provenance.task == "E2":
            self._close(env_id, "original_resample", False)
        else:
            span = self.spans.get(env_id)
            complete = natural and span.start_observed and not span.terminated and not span.truncated if span is not None and natural is not None else None
            self._close(env_id, "original_resample", complete)
        state.resample_pending = True
        self.uid.event(env_id, "sample_before_original", tick, timer_before=timer_before,
                       within_reset=within_reset, natural_outer_timer_event=natural)

    def resample_after(self, env_id: int, tick: int, command: Command) -> None:
        self.uid.sample_after(env_id, tick, command)
        self.segments[env_id] = 0

    def reset_before(self, env_id: int, tick: int) -> None:
        if env_id in self.pending:
            raise ValueError("Reset boundary occurred before pre-reset endpoint was delivered")
        self._close(env_id, "original_reset", False)
        self.uid.reset(env_id, tick)

    def _group(self, span: Span) -> Optional[str]:
        if self.provenance.task == "E2":
            return "moving_yaw_minus4" if span.command.profile == 8 else "moving_yaw_plus4"
        return "standing" if span.command.standing is True else "moving" if span.command.standing is False else None

    def _close(self, env_id: int, reason: str, complete: Optional[bool]) -> None:
        span = self.spans.pop(env_id, None)
        if span is None:
            return
        seconds = span.controls * DT
        known = complete is not None
        if seconds > 0:
            along, cross = span.along / seconds, span.cross / seconds
            yaw = (span.turn - span.commanded_yaw) / seconds
            tol = 0.05 if self.provenance.task == "E2" else max(0.03, 0.1 * span.nominal)
            kin = abs(along - span.nominal) <= tol and abs(cross) <= tol and abs(yaw) <= 0.2
        else:
            along = cross = yaw = None
            tol = 0.05 if self.provenance.task == "E2" else max(0.03, 0.1 * span.nominal)
            kin = False
        # E2 complete+terminal remains denominator/false. W35 complete is natural,
        # start-observed, nonterminal and count>0; terminal spans remain partial.
        denominator = bool(complete and seconds > 0) if known else None
        accepted = bool(denominator and kin and not span.terminated and not span.truncated) if known else None
        row = {"record_type": "attempt_close", **span.identity, "attempt_number": span.number,
               "same_UID_segment": span.segment, "group": self._group(span),
               "command": asdict(span.command), "cohort_event_uid": span.command.cohort_event_uid,
               "first_control": span.first_control, "last_control": span.last_control,
               "first_physics_tick": span.first_tick, "last_physics_tick": span.last_tick,
               "controls": span.controls, "seconds": seconds, "start_observed": span.start_observed,
               "end_reason": reason, "complete_sampled_span": complete,
               "conditional_denominator": denominator, "original_accepted": accepted,
               "original_kinematic_bounds_met": kin if known else None,
               "nominal_speed_m_s": span.nominal, "along_cross_tolerance_m_s": tol,
               "signed_yaw_tolerance_rad_s": 0.2, "fixed_axis_rad": span.axis,
               "along_displacement_m": span.along, "cross_displacement_m": span.cross,
               "along_speed_m_s": along, "cross_speed_m_s": cross,
               "actual_signed_yaw_rad": span.turn, "commanded_signed_yaw_rad": span.commanded_yaw,
               "signed_yaw_error_rad_s": yaw,
               "BODY_reference_along_displacement_m": span.reference_along,
               "BODY_reference_cross_displacement_m": span.reference_cross,
               "crossed_warmup_steady_boundary": span.crossed_phase,
               "terminated_before_reset": span.terminated, "truncated_before_reset": span.truncated,
               "original_terminal_reasons": span.reasons,
               "evidence_state": "copied_measurements_only" if known else "measurement_gap",
               "runtime_reference_validation": self.provenance.reference_frame_and_sample_phase_validated,
               "real_expert_pass": None}
        self._emit(row)

    def finish(self) -> dict[str, Any]:
        for env_id in list(self.pending):
            self._gap(env_id, "window_end_missing_pre_reset_endpoint", self.pending[env_id][1].control)
        self.pending.clear()
        for env_id, state in list(self.uid.envs.items()):
            if state.resample_pending:
                self._gap(env_id, "window_end_missing_resample_after")
        for env_id in list(self.spans):
            self._close(env_id, "window_end_partial", False)
        groups = ("moving_yaw_minus4", "moving_yaw_plus4") if self.provenance.task == "E2" else ("moving", "standing")
        counts = {}
        for group in groups:
            rows = [r for r in self.rows if r["record_type"] == "attempt_close" and r["group"] == group]
            complete = [r for r in rows if r["conditional_denominator"] is True]
            counts[group] = {"opened_attempts": sum(r["record_type"] == "attempt_open" and r["group"] == group for r in self.rows),
                             "complete": len(complete), "true": sum(r["original_accepted"] is True for r in complete),
                             "false": sum(r["original_accepted"] is False for r in complete),
                             "partial": sum(r["conditional_denominator"] is False for r in rows),
                             "unknown": sum(r["conditional_denominator"] is None for r in rows),
                             "close_reasons": {key: sum(r["end_reason"] == key for r in rows) for key in sorted({r["end_reason"] for r in rows})}}
        return {"schema": "mod4.source_measurement_summary.v1", "provenance": asdict(self.provenance),
                "groups": counts, "measurement_integrity_gap_count": len(self.integrity_gaps),
                "full_expert_pass": None, "target90_or_outer_attempt_pass": None,
                "runtime_frame_cache_validation": self.provenance.reference_frame_and_sample_phase_validated,
                "not_a_real_expert_or_frozen_validation_result": True}


def compare_declared_cohorts(left: Iterable[dict], right: Iterable[dict]) -> dict[str, Any]:
    """Pure join of NEW attempt-open records. No stream reads, no count proxy.

    Cross-policy matching requires owner-declared namespace/event UID AND equal
    original sample packets. Duplicate/absent keys mean comparison pending.
    """
    def index(rows: Iterable[dict]) -> Optional[dict]:
        result = {}
        for r in rows:
            if r.get("record_type") != "attempt_open":
                continue
            p, c = r["provenance"], r["command"]
            namespace, uid = p.get("cohort_namespace"), c.get("cohort_event_uid")
            if namespace is None or uid is None:
                return None
            key = (namespace, r["task"], r["env_id"], uid)
            packet = {k: v for k, v in c.items() if k != "cohort_event_uid"}
            value = (r["episode_uid"], r["command_uid"], sha(packet))
            if key in result and result[key] != value:
                return None
            # Repeated E2 cycles under one source command are one command cohort
            # member, but reusing a declared event for two commands is ambiguous.
            result[key] = value
        return {k: v[2] for k, v in result.items()}
    a, b = index(left), index(right)
    if a is None or b is None:
        return {"matched_UID_cohort": None, "reason": "missing_or_duplicate_preregistered_pair_keys"}
    both = a.keys() & b.keys()
    mismatch = [list(k) for k in sorted(both) if a[k] != b[k]]
    return {"matched_UID_cohort": bool(a) and a == b,
            "matched_packet_count": sum(a[k] == b[k] for k in both),
            "packet_mismatch_keys": mismatch,
            "left_only_keys": [list(k) for k in sorted(a.keys() - b.keys())],
            "right_only_keys": [list(k) for k in sorted(b.keys() - a.keys())],
            "equal_numerators_or_local_UIDs_are_not_match_proof": True}
