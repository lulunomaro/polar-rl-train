"""CPU-only deterministic synthetic tests. No real expert or frozen evaluation."""
from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from observer_uid_ledger_v1 import (Capture, Command, DT, ExclusiveJsonlSink,
    MeasurementObserver, Provenance, canonical, capture_audit, classify_e2,
    compare_declared_cohorts, heading_xyzw, wrap)
from native_validation_observer_entry_v1 import NativeValidationObserverEntry, describe_future_call_sites


def capture(control, stage, x=0.0, y=0.0, heading=0.0, **changes):
    q = (0.0, 0.0, math.sin(heading / 2), math.cos(heading / 2))
    end = stage == "after_control_pre_reset"
    tick = (control + int(end)) * 8
    values = dict(control=control, tick=tick, stage=stage, root_pos_w_xy=(x, y),
                  heading_w=heading, root_state_w=(x, y, 1.0, *q, 0., 0., 0., 0., 0., 0.),
                  feedback_tick=(control + int(end)) * 2, sim_step_counter=tick)
    values.update(changes)
    return Capture(**values)


def e2_command(sign=1, **changes):
    values = dict(body=(0.5, 0.0, sign * 4.0), profile=9 if sign > 0 else 8,
                  world_direction=0.0, signed_yaw=sign * 4.0, standing=False)
    values.update(changes)
    return Command(**values)


def w35_command(**changes):
    values = dict(body=(0.5, 0.0, 0.0), sampled_heading=0.0, standing=False,
                  source_episode=7, original_counter=10, unused_random_direction=1.7)
    values.update(changes)
    return Command(**values)


def observer(task, **changes):
    return MeasurementObserver(Provenance(run_uid="SYNTHETIC_ONLY", task=task, **changes))


def closes(o):
    return [r for r in o.rows if r["record_type"] == "attempt_close"]


def e2_steps(o, n=79, start=0, sign=1, speed=0.5, cross=0.0, terminal_last=False,
             timeout_last=False, command=None, env_id=0):
    c = command or e2_command(sign)
    for i in range(start, start + n):
        x, y, a = i * DT * speed, i * DT * cross, i * DT * sign * 4
        o.begin(env_id, c, capture(i, "before_control", x, y, wrap(a)))
        o.endpoint(env_id, capture(i, "after_control_pre_reset", x + DT * speed,
                   y + DT * cross, wrap(a + DT * sign * 4)),
                   terminal_last and i == start + n - 1, timeout_last and i == start + n - 1)


def w35_step(o, command=None, control=0, speed=0.5, cross=0.0, term=False,
              trunc=False, axis=0.0, root_offset=0.0, root_heading=None):
    c = command or w35_command()
    co, si = math.cos(axis), math.sin(axis)
    dx, dy = DT * (speed * co - cross * si), DT * (speed * si + cross * co)
    x, y = control * dx, control * dy
    o.begin(0, c, capture(control, "before_control", x, y, c.sampled_heading))
    after = capture(control, "after_control_pre_reset", x + dx, y + dy, c.sampled_heading)
    root = list(after.root_state_w)
    root[0] += root_offset
    if root_heading is not None:
        root[3:7] = [0., 0., math.sin(root_heading / 2), math.cos(root_heading / 2)]
    o.endpoint(0, replace(after, root_state_w=tuple(root)), term, trunc)


def arm_w35(o, command=None, known=True):
    o.initial_packet(0, 0, command or w35_command(), known)


class E2OriginalTests(unittest.TestCase):
    def test_positive_original_cycle_and_exact_constants(self):
        o = observer("E2"); e2_steps(o)
        r = closes(o)[0]
        self.assertTrue(r["conditional_denominator"] and r["original_accepted"])
        self.assertEqual(r["controls"], 79)
        self.assertEqual(r["nominal_speed_m_s"], .5)
        self.assertEqual(r["along_cross_tolerance_m_s"], .05)
        self.assertEqual(r["signed_yaw_tolerance_rad_s"], .2)
        self.assertIsNone(r["real_expert_pass"])

    def test_negative_cycle_separate_group(self):
        o = observer("E2"); e2_steps(o, sign=-1)
        self.assertTrue(closes(o)[0]["original_accepted"])
        self.assertEqual(closes(o)[0]["group"], "moving_yaw_minus4")
        self.assertEqual(o.finish()["groups"]["moving_yaw_plus4"]["complete"], 0)

    def test_no_early_2pi_interpolation(self):
        o = observer("E2"); e2_steps(o, n=78); o.finish()
        self.assertFalse(closes(o)[0]["conditional_denominator"])
        self.assertEqual(closes(o)[0]["end_reason"], "window_end_partial")

    def test_terminal_complete_remains_denominator_false(self):
        o = observer("E2"); e2_steps(o, terminal_last=True)
        r = closes(o)[0]
        self.assertTrue(r["conditional_denominator"])
        self.assertFalse(r["original_accepted"])
        self.assertTrue(r["terminated_before_reset"])

    def test_timeout_complete_remains_denominator_false(self):
        o = observer("E2"); e2_steps(o, timeout_last=True)
        self.assertTrue(closes(o)[0]["conditional_denominator"])
        self.assertFalse(closes(o)[0]["original_accepted"])

    def test_terminal_before_completion_is_partial(self):
        o = observer("E2"); e2_steps(o, n=10, terminal_last=True)
        self.assertFalse(closes(o)[0]["conditional_denominator"])

    def test_phase_crossing_does_not_break_span(self):
        o = observer("E2"); e2_steps(o, start=70)
        r = closes(o)[0]
        self.assertTrue(r["crossed_warmup_steady_boundary"])
        self.assertEqual(len(closes(o)), 1)
        self.assertEqual(r["controls"], 79)

    def test_repeated_cycles_drop_overshoot(self):
        o = observer("E2"); e2_steps(o); e2_steps(o, n=78, start=79); o.finish()
        rows = closes(o)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]["conditional_denominator"])
        self.assertFalse(rows[1]["conditional_denominator"])
        self.assertEqual(rows[1]["controls"], 78)

    def test_direction_change_partial_not_stitched(self):
        o = observer("E2"); e2_steps(o, n=10)
        c = e2_command(world_direction=.1)
        e2_steps(o, n=1, start=10, command=c); o.finish()
        self.assertEqual(len(closes(o)), 2)
        self.assertTrue(all(not r["conditional_denominator"] for r in closes(o)))

    def test_no_x8_rescaling(self):
        o = observer("E2"); e2_steps(o, speed=.5 / 8)
        self.assertFalse(closes(o)[0]["original_accepted"])
        self.assertAlmostEqual(closes(o)[0]["along_speed_m_s"], .0625)

    def test_cross_and_along_original_tolerances(self):
        for speed, cross, expected in ((.549, .049, True), (.551, 0, False), (.5, .051, False)):
            o = observer("E2"); e2_steps(o, speed=speed, cross=cross)
            self.assertEqual(closes(o)[0]["original_accepted"], expected)

    def test_wrong_yaw_not_replaced_by_reference(self):
        o = observer("E2"); e2_steps(o, command=e2_command(body=(.5, 0., 3.79)))
        self.assertFalse(closes(o)[0]["original_accepted"])
        self.assertGreater(closes(o)[0]["signed_yaw_error_rad_s"], .2)

    def test_reference_integral_is_diagnostic_not_nominal_goal(self):
        o = observer("E2"); e2_steps(o)
        r = closes(o)[0]
        self.assertTrue(r["original_accepted"])
        self.assertNotAlmostEqual(r["BODY_reference_along_displacement_m"], r["along_displacement_m"])

    def test_classifier_uses_original_flags(self):
        self.assertEqual(classify_e2(False, False, True, False, .0, -4.), 8)
        self.assertEqual(classify_e2(False, False, True, False, .0, 4.), 9)
        self.assertEqual(classify_e2(True, False, False, False, 10., 0.), 0)
        with self.assertRaises(ValueError):
            classify_e2(True, False, True, False, 0., 4.)


class W35OriginalTests(unittest.TestCase):
    def test_moving_original_natural_complete(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        o.resample_before(0, 8, 0.0, False)
        r = closes(o)[0]
        self.assertTrue(r["original_accepted"])
        self.assertAlmostEqual(r["along_cross_tolerance_m_s"], .05)
        self.assertEqual(r["group"], "moving")

    def test_standing_uses_flag_and_tolerance_floor(self):
        c = w35_command(body=(0., 0., 0.), standing=True)
        o = observer("W35"); arm_w35(o, c); w35_step(o, c, speed=0.)
        o.resample_before(0, 8, -.1, False)
        r = closes(o)[0]
        self.assertEqual(r["group"], "standing")
        self.assertEqual(r["along_cross_tolerance_m_s"], .03)
        self.assertTrue(r["original_accepted"])

    def test_no_speed_derived_standing_proxy(self):
        c = w35_command(body=(0., 0., 0.), standing=False)
        o = observer("W35"); arm_w35(o, c); w35_step(o, c, speed=0.)
        o.resample_before(0, 8, 0., False)
        self.assertEqual(closes(o)[0]["group"], "moving")

    def test_negative_BODY_vx_fixed_heading_plus_pi(self):
        c = w35_command(body=(-1., 0., 0.), sampled_heading=.4)
        o = observer("W35"); arm_w35(o, c)
        w35_step(o, c, speed=1., axis=.4 + math.pi)
        o.resample_before(0, 8, 0., False)
        self.assertTrue(closes(o)[0]["original_accepted"])
        self.assertAlmostEqual(closes(o)[0]["fixed_axis_rad"], .4 + math.pi)
        self.assertAlmostEqual(closes(o)[0]["along_cross_tolerance_m_s"], .1)

    def test_positive_timer_and_nested_reset_are_partial(self):
        for timer, within in ((.01, False), (0., True)):
            o = observer("W35"); arm_w35(o); w35_step(o)
            o.resample_before(0, 8, timer, within)
            self.assertFalse(closes(o)[0]["conditional_denominator"])

    def test_unknown_start_never_conditional_complete(self):
        o = observer("W35"); w35_step(o)
        o.resample_before(0, 8, 0., False)
        self.assertFalse(closes(o)[0]["start_observed"])
        self.assertFalse(closes(o)[0]["conditional_denominator"])

    def test_terminal_and_timeout_excluded_not_promoted_to_failure_denom(self):
        for term, trunc in ((True, False), (False, True)):
            o = observer("W35"); arm_w35(o); w35_step(o, term=term, trunc=trunc)
            o.resample_before(0, 8, 0., False)
            self.assertFalse(closes(o)[0]["conditional_denominator"])
            self.assertFalse(closes(o)[0]["original_accepted"])

    def test_parameter_break_same_UID_new_unknown_start_segment(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        w35_step(o, w35_command(body=(.6, 0., 0.)), control=1, speed=.6)
        o.resample_before(0, 16, 0., False)
        rows = closes(o)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["command_uid"], rows[1]["command_uid"])
        self.assertEqual(rows[1]["same_UID_segment"], 1)
        self.assertFalse(rows[1]["start_observed"])
        self.assertTrue(all(not r["conditional_denominator"] for r in rows))

    def test_source_episode_break_is_partial(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        w35_step(o, w35_command(source_episode=8), control=1)
        o.finish()
        self.assertEqual(len(closes(o)), 2)
        self.assertTrue(all(not r["conditional_denominator"] for r in closes(o)))

    def test_sampled_axis_and_body_retained_before_first_control(self):
        sample = w35_command(body=(.5, 0., 0.), sampled_heading=.0)
        o = observer("W35"); arm_w35(o, sample)
        changed = w35_command(body=(.6, 0., 0.), sampled_heading=.2)
        w35_step(o, changed, speed=.5)
        o.resample_before(0, 8, 0., False)
        r = closes(o)[0]
        self.assertEqual(r["nominal_speed_m_s"], .5)
        self.assertEqual(r["fixed_axis_rad"], 0.)
        self.assertEqual(r["command"]["body"], (.5, 0., 0.))

    def test_preserve_mixed_getter_not_automatically_repair(self):
        o = observer("W35"); arm_w35(o); w35_step(o, root_offset=.01)
        o.resample_before(0, 8, 0., False)
        self.assertAlmostEqual(closes(o)[0]["along_speed_m_s"], 1.)
        self.assertFalse(closes(o)[0]["original_accepted"])
        rows = [r for r in o.rows if r["record_type"] == "control_capture"]
        self.assertAlmostEqual(rows[0]["after_getter_audit"]["root_pos_minus_root_state_xy"][0], -.01)
        self.assertIsNone(rows[0]["after_getter_audit"]["same_point_and_cache_phase_validated"])

    def test_W35_endpoint_yaw_uses_xyzw_root_not_heading_alias(self):
        o = observer("W35"); arm_w35(o); w35_step(o, root_heading=.1)
        o.resample_before(0, 8, 0., False)
        self.assertAlmostEqual(closes(o)[0]["signed_yaw_error_rad_s"], 5.)
        self.assertFalse(closes(o)[0]["original_accepted"])

    def test_missing_timer_is_null_not_false_measured_fact(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        o.resample_before(0, 8, None, False)
        self.assertIsNone(closes(o)[0]["conditional_denominator"])
        self.assertIsNone(closes(o)[0]["original_accepted"])

    def test_original_yaw_and_cross_bounds(self):
        for cross, root_yaw, expected in ((.049, .0039, True), (.051, 0., False), (0., .0041, False)):
            o = observer("W35"); arm_w35(o)
            w35_step(o, cross=cross, root_heading=root_yaw)
            o.resample_before(0, 8, 0., False)
            self.assertEqual(closes(o)[0]["original_accepted"], expected)


class IntegrityAndEntryTests(unittest.TestCase):
    def test_clock_mismatch_marks_unknown_not_new_threshold(self):
        o = observer("E2"); c = e2_command()
        o.begin(0, c, capture(0, "before_control"))
        o.endpoint(0, replace(capture(0, "after_control_pre_reset"), tick=7), False, False)
        self.assertIsNone(closes(o)[0]["conditional_denominator"])
        self.assertEqual(o.finish()["measurement_integrity_gap_count"], 1)

    def test_nonconsecutive_control_marks_gap(self):
        o = observer("E2"); e2_steps(o, n=1); e2_steps(o, n=1, start=2); o.finish()
        self.assertEqual(o.integrity_gaps[0]["reason"], "nonconsecutive_physics_or_control")

    def test_missing_original_getter_is_null_not_proxy(self):
        o = observer("E2"); c = e2_command()
        o.begin(0, c, capture(0, "before_control"))
        o.endpoint(0, replace(capture(0, "after_control_pre_reset"), root_pos_w_xy=None), False, False)
        self.assertIsNone(closes(o)[0]["original_accepted"])

    def test_post_reset_stage_is_not_accepted_endpoint(self):
        o = observer("E2"); o.begin(0, e2_command(), capture(0, "before_control"))
        with self.assertRaises(ValueError):
            o.endpoint(0, replace(capture(0, "after_control_pre_reset"), stage="post_reset"), False, False)

    def test_terminal_reason_OR_mismatch_is_gap(self):
        o = observer("E2"); o.begin(0, e2_command(), capture(0, "before_control"))
        o.endpoint(0, capture(0, "after_control_pre_reset"), True, False,
                   {"fall": False}, {"fall": False})
        self.assertIsNone(closes(o)[0]["original_accepted"])

    def test_explicit_reset_and_resample_increment_separate_UIDs(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        o.reset_before(0, 8)
        o.resample_before(0, 8, 0., True)
        o.resample_after(0, 8, w35_command(source_episode=8, original_counter=11))
        state = o.uid.state(0)
        self.assertEqual((state.episode, state.command), (1, 1))
        self.assertEqual(state.sample_packet.source_episode, 8)
        self.assertTrue(state.command_start_observed)

    def test_missing_resample_before_is_error(self):
        o = observer("E2")
        with self.assertRaises(ValueError):
            o.resample_after(0, 0, e2_command())

    def test_snapshot_COM_actor_and_origin_residuals_are_only_diagnostic(self):
        c = capture(0, "before_control", x=10., root_link_pos_w=(10., 0., 1.),
                    root_com_pos_w=(10.2, 0., 1.), env_origin_xyz=(8., 0., 0.),
                    native_packed_local_xyz=(2., 0., 1.))
        a = capture_audit(c)
        self.assertAlmostEqual(a["actor_minus_COM_xyz"][0], -.2)
        self.assertEqual(a["packed_local_minus_root_world_minus_origin_xyz"], [0., 0., 0.])
        self.assertIsNone(a["getter_cache"])

    def test_xyzw_and_heading_wrap_math(self):
        h = 2.8
        self.assertAlmostEqual(heading_xyzw((0., 0., math.sin(h / 2), math.cos(h / 2))), h)
        self.assertAlmostEqual(wrap(-math.pi + .01 - (math.pi - .01)), .02)

    def test_new_sink_exclusive_mode_stream_hash_and_fail_before_drop(self):
        stream = io.BytesIO()
        with patch.object(Path, "open", return_value=stream) as opened:
            sink = ExclusiveJsonlSink("synthetic_never_opened.jsonl")
            opened.assert_called_once_with("xb")
            row = {"synthetic_only": True}
            sink(row)
            expected = canonical(row) + b"\n"
            self.assertEqual(sink.bytes, len(expected))
            self.assertEqual(sink.digest.hexdigest(), hashlib.sha256(expected).hexdigest())
            sink.maximum_bytes = sink.bytes
            with self.assertRaises(BufferError):
                sink(row)
            self.assertEqual(sink.rows, 1)
            sink.finish()

    def test_native_entry_uses_copies_without_live_env(self):
        entry = NativeValidationObserverEntry(Provenance("SYNTHETIC_ENTRY", "W35"))
        c = w35_command()
        entry.submit(dict(kind="initial_packet", env_id=0, tick=0,
                          command=asdict(c), exact_initial_packet_verified=True))
        entry.submit(dict(kind="before_control", env_id=0, command=asdict(c),
                          capture=asdict(capture(0, "before_control"))))
        entry.submit(dict(kind="pre_reset_endpoint", env_id=0,
                          capture=asdict(capture(0, "after_control_pre_reset", x=.01)),
                          terminated=False, truncated=False))
        entry.submit(dict(kind="resample_before", env_id=0, tick=8, timer_before=0., within_reset=False))
        s = entry.finish()
        self.assertEqual(s["groups"]["moving"]["true"], 1)
        self.assertIsNone(s["full_expert_pass"])
        self.assertIsNone(describe_future_call_sites()["runtime_points_validated"])

    def test_cohort_equal_counts_not_enough(self):
        a = observer("W35"); b = observer("W35")
        arm_w35(a); arm_w35(b); w35_step(a); w35_step(b)
        self.assertIsNone(compare_declared_cohorts(a.rows, b.rows)["matched_UID_cohort"])

    def test_cohort_declared_exact_packets_match_and_mismatch(self):
        c = w35_command(cohort_event_uid="preregistered_event_1")
        a = observer("W35", cohort_namespace="SYNTHETIC_PAIR")
        b = observer("W35", cohort_namespace="SYNTHETIC_PAIR")
        arm_w35(a, c); arm_w35(b, c); w35_step(a, c); w35_step(b, c)
        self.assertTrue(compare_declared_cohorts(a.rows, b.rows)["matched_UID_cohort"])
        changed = [dict(r) for r in b.rows]
        for row in changed:
            if row["record_type"] == "attempt_open":
                row["command"] = {**row["command"], "original_counter": 11}
        self.assertFalse(compare_declared_cohorts(a.rows, changed)["matched_UID_cohort"])

    def test_cohort_repeated_cycles_deduplicate_only_same_command(self):
        c = e2_command(cohort_event_uid="command_event_1")
        a = observer("E2", cohort_namespace="SYNTHETIC_PAIR")
        b = observer("E2", cohort_namespace="SYNTHETIC_PAIR")
        e2_steps(a, n=158, command=c); e2_steps(b, n=79, command=c)
        matched = compare_declared_cohorts(a.rows, b.rows)
        self.assertTrue(matched["matched_UID_cohort"])
        self.assertEqual(matched["matched_packet_count"], 1)
        # This says command populations match, NOT that attempt outcomes match.
        modified = [dict(r) for r in a.rows]
        opens = [r for r in modified if r["record_type"] == "attempt_open"]
        opens[1]["command_uid"] += 1
        self.assertIsNone(compare_declared_cohorts(modified, b.rows)["matched_UID_cohort"])

    def test_unmatched_resample_boundary_reported(self):
        o = observer("W35"); arm_w35(o); w35_step(o)
        o.resample_before(0, 8, 0., False)
        result = o.finish()
        self.assertTrue(closes(o)[0]["original_accepted"])
        self.assertEqual(result["measurement_integrity_gap_count"], 1)
        self.assertEqual(o.integrity_gaps[0]["reason"], "window_end_missing_resample_after")

    def test_frame_capture_timestamp_not_fabricated_from_read_tick(self):
        c = capture(0, "after_control_pre_reset", frame_capture_physics_tick=0)
        self.assertEqual(capture_audit(c)["frame_age_physics_ticks"], 8)
        self.assertIsNone(capture_audit(capture(0, "after_control_pre_reset"))["frame_age_physics_ticks"])

    def test_zero_control_and_window_missing_endpoint_stay_explicit(self):
        o = observer("E2"); o.begin(0, e2_command(), capture(0, "before_control")); o.finish()
        self.assertEqual(closes(o)[0]["controls"], 0)
        self.assertIsNone(closes(o)[0]["conditional_denominator"])

    def test_no_environment_or_tensor_dependencies_loaded(self):
        forbidden = ("torch", "isaaclab", "omni", "pxr", "warp", "numpy")
        self.assertFalse(any(name == p or name.startswith(p + ".") for name in sys.modules for p in forbidden))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-json", type=Path, default=HERE / "CPU_SYNTHETIC_TEST_RESULT_V1.json")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    text = log.getvalue()
    print(text)
    receipt = {"schema": "mod4.source_measurement_CPU_synthetic_result.v1",
               "scope": "deterministic_stdlib_CPU_synthetic_only",
               "tests_run": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "skipped": len(result.skipped),
               "successful": result.wasSuccessful(),
               "test_names": [line.split(" ... ")[0] for line in text.splitlines() if " ... " in line],
               "failures_and_errors": [str(test) + "\n" + trace for test, trace in (*result.failures, *result.errors)],
               "source_only_no_real_expert_pass": True, "actual_frozen_evaluation": None,
               "SDK_GPU_model_remote_access": False,
               "existing_sources_written": False}
    out = args.result_json.resolve()
    if out.parent != HERE:
        raise ValueError("Synthetic receipt must stay inside this new review directory")
    # Test result is new inside the requested output directory. Re-runs use a
    # separate caller-controlled output directory rather than replacing evidence.
    with out.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
