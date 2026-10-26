"""Synthetic schema fixtures only; no actual V85 closing curves are fabricated."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

import native_curve_text_reader_v1 as reader


def snapshot(rows, takeoff=0, cross=0, landing=0, recovery=0):
    return dict(schema="completed_control_goal_events_v1", complete_control_rows=rows,
                num_envs=20000, environment_control_transitions=rows * 20000,
                events=dict(takeoff_count=takeoff, landing_count=landing, recovery_count=recovery),
                initial_counter_snapshot_sums=dict(takeoff_count=7, landing_count=3, recovery_count=1),
                unique_env_ids_with_event=dict(takeoff_count=min(takeoff, 20000), landing_count=min(landing, 20000), recovery_count=min(recovery, 20000)),
                both_leading_edges_cross_event_count=cross, negative_counter_envframes=0, invalid_rows=0,
                last_error=None, diagnostic_valid=True, diagnostic_write_errors=[],
                selected_resets_accounted_from_previous_complete_row_done=True,
                only_completed_control_rows_not_partial_physics_callbacks=True,
                cross_event_is_original_leading_edge_truth_not_complete_footprint_landing=True,
                not_frozen_policy_skill_graduation_or_new_training_gate=True)


def fixtures():
    go = dict(learning_started_epoch=1000.0, source_SHA="a" * 64, run_id="SYNTHETIC_NOT_ACTUAL85")
    rows = []
    for i in range(3):
        rows.append(dict(epoch=1010.0 + i * 10, GO_elapsed_s=10.0 + i * 10, native_iteration=i,
                         world_updates=i * 10, policy_updates=int(i == 2),
                         environment_transitions=(i + 1) * 20000, completed_control_rows=i + 1,
                         events=snapshot(i + 1, takeoff=i, cross=int(i == 2)),
                         wm_last=None if i == 0 else [0.2 / i, 0.1 / i],
                         policy_last=None if i < 2 else [-0.1, 0.03, 0.4, 2.1, 0.9],
                         not_frozen_evaluation_or_causal_PPO_comparison=True))
    prefix = dict(controls=5, index=[dict(controls=2, path="MUST_NOT_OPEN_A.npz"), dict(controls=3, path="MUST_NOT_OPEN_B.npz")],
                  physical_callback_replay=False, preupdate_full_sources=[dict(path="MUST_NOT_OPEN.pt")])
    lifetime = snapshot(5, takeoff=2, cross=1, landing=1)
    final = dict(epoch=1040, passed=True, counters=dict(updates=2, world_updates=20, policy_updates=1),
                 final=dict(path="MUST_NOT_OPEN_NATIVE_MODEL.pt", SHA=None, updates=2, world_updates=20, policy_updates=1))
    return dict(go=go, rows=rows, prefix=prefix, lifetime=lifetime, final=final)


def line_text(rows):
    return "".join(json.dumps(r) + "\n" for r in rows)


def run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    f = fixtures()
    (out / "SYNTHETIC_SCHEMA_FIXTURES_NOT_ACTUAL85.json").write_text(json.dumps(f, indent=2), encoding="utf8")
    results = []

    def test(name, function):
        try:
            detail = function()
            results.append(dict(name=name, passed=True, detail=detail))
        except BaseException as error:
            results.append(dict(name=name, passed=False, error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc()))

    def analyze(rows=None, **changes):
        kwargs = {k: copy.deepcopy(f[k]) for k in ("go", "prefix", "lifetime", "final")}
        kwargs.update(changes)
        return reader.analyze_curve(line_text(f["rows"] if rows is None else rows), **kwargs)

    def valid_coverage():
        r = analyze()
        assert r["status"] == "curve_text_and_final_completed_control_coverage_valid"
        assert r["curve_summary"]["environment_transitions"] == 60000
        assert r["final_counter_coverage"]["raw_snapshot"]["environment_control_transitions"] == 100000
        assert r["native_FINAL_status"] == "present_metadata_only_not_checkpoint_qualified"
        assert r["native_final_checkpoint_metadata"]["SHA"] is None
        assert r["rows"][-1]["Pi_imagination_outputs"]["imagined_critic_MSE"] == .03
        assert r["rows"][-1]["WM_losses"]["window_normalized_WM_prediction_loss"] == .1
        return dict(curve_rows=3, final_completed_controls=5, actual_model_files_opened=0)

    def intervals():
        r = analyze()
        takeoff = r["first_positive"]["takeoff_count"]
        assert (takeoff["lower_GO_elapsed_s"], takeoff["upper_GO_elapsed_s"]) == (10, 20)
        assert r["first_positive"]["policy_updates"]["upper_GO_elapsed_s"] == 30
        assert r["first_positive"]["both_leading_edges_cross_event_count"]["lower_GO_elapsed_s"] == 20
        assert r["first_positive"]["recovery_count"]["status"] == "no_positive_observed"
        assert r["curve_summary"]["GO_elapsed_s"] == 30  # Not controls * 0.01.
        rows = copy.deepcopy(f["rows"])
        rows[0]["events"] = snapshot(1, takeoff=1)
        first = analyze(rows)["first_positive"]["takeoff_count"]
        assert first["lower_GO_elapsed_s"] is None and first["first_observation_already_positive"]
        return "interval censoring and unknown first lower endpoint retained"

    def invalid_counter():
        rows = copy.deepcopy(f["rows"])
        rows[-1]["events"]["negative_counter_envframes"] = 1
        rows[-1]["events"]["diagnostic_valid"] = False
        r = analyze(rows)
        assert r["valid_update_rows"] == 3 and r["valid_event_rows"] == 2
        assert r["first_positive"]["both_leading_edges_cross_event_count"]["status"] == "no_positive_observed"
        assert r["rows"][-1]["original_counter_snapshot"]["both_leading_edges_cross_event_count"] == 1
        return "invalid original counter preserved and not credited"

    def partial_missing_counter():
        rows = copy.deepcopy(f["rows"])
        for row in rows:
            row.pop("events")
        r = analyze(rows, lifetime=None, prefix=None)
        assert r["valid_update_rows"] == 3 and r["valid_event_rows"] == 0
        assert r["first_positive"]["landing_count"]["status"] == "unknown_no_valid_coverage"
        assert r["final_counter_coverage"]["status"].startswith("pending")
        return "native updates retained independently of unavailable physical-event coverage"

    def malformed_tail():
        r = reader.analyze_curve(line_text(f["rows"]) + '{"epoch":', go=f["go"])
        assert r["parsed_curve_rows"] == 3 and r["valid_update_rows"] == 3
        assert r["issues"][0]["possible_interrupted_tail"] is True
        assert r["issues"][0]["raw_line"] == '{"epoch":'
        assert r["status"] == "partial_or_invalid_curve_text_preserved"
        return "malformed tail original text retained; earlier observations stay scoped"

    def monotonicity():
        rows = copy.deepcopy(f["rows"])
        rows[-1]["world_updates"] = 1
        rows[-1]["events"]["events"]["takeoff_count"] = 0
        r = analyze(rows)
        assert not r["rows"][-1]["update_counters_valid"]
        assert "world_updates_decreased" in r["rows"][-1]["update_errors"]
        assert "cumulative_original_event_count_decreased" in r["rows"][-1]["event_coverage_errors"]
        return "decreasing cumulative native and task counters rejected as evidence"

    def unknown_states():
        r = analyze(go=None, final=None)
        assert r["bootstrap_source_SHA"] is None
        assert r["bootstrap_source_status"] == "unknown"
        assert r["native_FINAL_status"] == "unknown_no_FINAL"
        assert r["issues"][-1]["kind"] == "original_GO_epoch_unknown"
        pending = reader.analyze_curve()
        assert pending["curve_summary"] is None and pending["first_positive"] is None
        assert pending["status"] == "pending_actual_85_closing_curve"
        return "null FINAL/source and unavailable actual curve remain unknown/pending"

    def generic_not_graduation():
        generic = {"Metrics/velocity/success_rate": 1.0, "task_scope": "generic_velocity_only"}
        r = analyze(generic_metrics=generic)
        assert r["generic_velocity_metrics_uninterpreted"] == generic
        assert r["generic_velocity_success_is_not_H1_step270_graduation"] is True
        assert r["final_counter_coverage"]["observed_counts"]["recovery_count"] == 0
        return "velocity success=1 does not manufacture recovery or skill proof"

    def coverage_failure():
        prefix = copy.deepcopy(f["prefix"])
        prefix["controls"] = 6
        a = analyze(prefix=prefix)
        assert a["prefix_coverage"]["valid"] is False
        assert a["final_counter_coverage"]["status"] != "full_completed_control_coverage"
        lifetime = copy.deepcopy(f["lifetime"])
        lifetime["complete_control_rows"] = 4
        lifetime["environment_control_transitions"] = 80000
        b = analyze(lifetime=lifetime)
        assert "counter_coverage_does_not_equal_completed_controls" in b["final_counter_coverage"]["errors"]
        return "chunk sum and final counter rows must cover original completed prefix"

    def collector_exact_schema():
        folder = out / "collector_synthetic_text_only"
        folder.mkdir()
        inputs = {"curve": ("e2/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl", line_text(f["rows"])),
                  "go": ("e2/job0/GO_PRODUCTION.json", json.dumps(f["go"])),
                  "prefix": ("e2/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json", json.dumps(f["prefix"])),
                  "lifetime": ("e2/job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json", json.dumps(f["lifetime"])),
                  "final": ("e2/job0/production/FINAL.json", json.dumps(f["final"]))}
        records = []
        for key, (relative, content) in inputs.items():
            p = folder / Path(relative).name
            raw = content.encode("utf8")
            p.write_bytes(raw)
            records.append(dict(relative=relative, local_path=str(p), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
        c = dict(actual_finite_transport_returned=True, all_texts=records,
                 complete_models={"recovery": [dict(path="MUST_NOT_OPEN.pt")]}, native_H1_method_fullstate=[dict(path="MUST_NOT_OPEN.pt")])
        loaded = reader.collector_inputs(c)
        assert loaded["go"] == f["go"]
        assert loaded["curve"] == line_text(f["rows"])
        c["all_texts"][0]["SHA"] = "0" * 64
        try:
            reader.collector_inputs(c)
        except ValueError as error:
            assert "pin mismatch" in str(error)
        else:
            raise AssertionError("wrong text pin accepted")
        return "current collector all_texts and actual job0 GO path resolved without model/raw access"

    def strict_json_and_suffix():
        for text in ('{"a":1,"a":2}', '{"a":NaN}'):
            try:
                reader.decode_json(text)
            except ValueError:
                pass
            else:
                raise AssertionError("ambiguous/nonfinite JSON accepted")
        try:
            reader.read_text(out / "MUST_NOT_OPEN.pt")
        except ValueError:
            pass
        else:
            raise AssertionError("model suffix accepted")
        return "duplicate keys, nonfinite JSON, and model suffix refused"

    for name, fn in (("valid_current_curve_and_full_completed_control_coverage", valid_coverage),
                     ("original_GO_walltime_and_first_positive_intervals", intervals),
                     ("invalid_original_counter_not_credited", invalid_counter),
                     ("partial_counter_coverage_native_updates_kept", partial_missing_counter),
                     ("interrupted_tail_preserved", malformed_tail),
                     ("monotonicity_errors_preserved", monotonicity),
                     ("null_FINAL_unknown_source_and_actual_curve_pending", unknown_states),
                     ("generic_velocity_success_not_H1_skill", generic_not_graduation),
                     ("prefix_and_lifetime_coverage_mismatch", coverage_failure),
                     ("collector_producer_pin_and_GO_path", collector_exact_schema),
                     ("strict_JSON_and_text_only_suffix", strict_json_and_suffix)):
        test(name, fn)
    report = dict(schema="native_curve_text_reader_synthetic_CPU_proof_v1", epoch=time.time(),
                  synthetic_only_not_actual_V85_curves=True, no_remote_model_policy_GPU_physics_or_RNG=True,
                  tests=results, passed=all(r["passed"] for r in results),
                  pass_count=sum(r["passed"] for r in results), test_count=len(results))
    (out / "CPU_PARSER_FIXTURE_RESULT.json").write_text(json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps(dict(passed=report["passed"], pass_count=report["pass_count"], tests=len(results), output=str(out))))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(run(sys.argv[1]))
