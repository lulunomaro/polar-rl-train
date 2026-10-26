"""Offline text-only V85 native-H1 curve analysis. No model or plant imports.

Reads explicit JSON/JSONL text only; paths stored inside checkpoint metadata are
never opened. Analysis errors are evidence limitations, never training gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

SCHEMA = "native_H1_text_curve_analysis_v1"
EVENTS = ("takeoff_count", "both_leading_edges_cross_event_count", "landing_count", "recovery_count")
COUNTERS = ("native_iteration", "world_updates", "policy_updates", "completed_control_rows", "environment_transitions")
WM_NAMES = ("window_normalized_WM_prediction_loss", "masked_last_step_prediction_error")
PI_NAMES = ("negative_imagination_objective", "imagined_critic_MSE", "normalized_imagined_reward", "policy_gradient_norm", "imagined_survival_mean")
MAX_TEXT_BYTES = 64 * 1024 * 1024


def _finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def decode_json(text: str):
    return json.loads(text, object_pairs_hook=_object_pairs,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite JSON constant: " + v)))


def read_text(path: str | Path, suffixes=(".json", ".jsonl")):
    path = Path(path)
    if path.suffix.lower() not in suffixes:
        raise ValueError("text-only suffix refused: " + str(path))
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError("bounded text limit exceeded")
    raw = path.read_bytes()
    return raw.decode("utf-8-sig"), dict(path=str(path.resolve()), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def read_json(path):
    text, pin = read_text(path, (".json",))
    return decode_json(text), pin


def parse_curve(text):
    rows, issues = [], []
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = decode_json(line)
            if not isinstance(row, dict):
                raise ValueError("curve row must be an object")
            rows.append((number, row))
        except (ValueError, TypeError) as error:
            issues.append(dict(line=number, kind="malformed_jsonl_record",
                               error=str(error), raw_line=line,
                               last_nonblank_line=not any(s.strip() for s in lines[number:]),
                               possible_interrupted_tail=number == len(lines) and not text.endswith("\n")))
    return rows, issues


def validate_events(snapshot, expected_rows=None, expected_envs=20000):
    errors = []
    if not isinstance(snapshot, dict):
        return None, ["event_snapshot_missing_or_not_object"]
    if snapshot.get("schema") != "completed_control_goal_events_v1":
        errors.append("original_counter_schema_unknown")
    rows, envs, transitions = (snapshot.get(k) for k in ("complete_control_rows", "num_envs", "environment_control_transitions"))
    if not all(_count(v) for v in (rows, envs, transitions)) or envs != expected_envs:
        errors.append("counter_row_env_transition_types_or_env_count")
    elif transitions != rows * envs:
        errors.append("counter_transition_product_mismatch")
    if expected_rows is not None and rows != expected_rows:
        errors.append("counter_coverage_does_not_equal_completed_controls")
    if snapshot.get("diagnostic_valid") is not True:
        errors.append("producer_diagnostic_not_valid")
    for key in ("invalid_rows", "negative_counter_envframes"):
        if type(snapshot.get(key)) is not int or snapshot.get(key) != 0:
            errors.append(key + "_not_zero")
    if snapshot.get("last_error") is not None:
        errors.append("producer_last_error_present")
    if snapshot.get("diagnostic_write_errors") != []:
        errors.append("diagnostic_write_error_or_coverage_unknown")
    for key in ("selected_resets_accounted_from_previous_complete_row_done",
                "only_completed_control_rows_not_partial_physics_callbacks",
                "cross_event_is_original_leading_edge_truth_not_complete_footprint_landing"):
        if snapshot.get(key) is not True:
            errors.append(key + "_not_proven")
    event_dict = snapshot.get("events")
    if not isinstance(event_dict, dict):
        errors.append("event_counts_missing")
        event_dict = {}
    values = {k: event_dict.get(k) for k in ("takeoff_count", "landing_count", "recovery_count")}
    values["both_leading_edges_cross_event_count"] = snapshot.get("both_leading_edges_cross_event_count")
    if not all(_count(v) for v in values.values()):
        errors.append("event_count_type_or_negative")
    unique = snapshot.get("unique_env_ids_with_event")
    initial = snapshot.get("initial_counter_snapshot_sums")
    if not isinstance(unique, dict) or not isinstance(initial, dict):
        errors.append("initial_or_unique_counter_metadata_missing")
    else:
        for key in ("takeoff_count", "landing_count", "recovery_count"):
            if not _count(initial.get(key)) or not _count(unique.get(key)):
                errors.append(key + "_initial_or_unique_type")
            elif _count(envs) and unique[key] > envs:
                errors.append(key + "_unique_count_exceeds_envs")
    return values, errors


def _losses(value, names):
    if value is None:
        return None, []
    if not isinstance(value, list) or len(value) != len(names) or not all(_finite(v) for v in value):
        return dict(raw=value), ["loss_tuple_schema_or_nonfinite"]
    return dict(zip(names, value)), []


def _first_positive(rows, key, event=False):
    previous_zero = None
    for row in rows:
        coverage_valid = row["event_coverage_valid"] if event else row["update_counters_valid"]
        if not coverage_valid:
            continue
        value = row["original_completed_events"][key] if event else row[key]
        if value > 0:
            return dict(status="first_curve_positive_interval_censored",
                        lower_GO_elapsed_s=None if previous_zero is None else previous_zero["GO_elapsed_s"],
                        upper_GO_elapsed_s=row["GO_elapsed_s"],
                        lower_completed_controls=None if previous_zero is None else previous_zero["completed_control_rows"],
                        upper_completed_controls=row["completed_control_rows"],
                        interval="(last valid zero observation, first valid positive observation]",
                        exact_event_time_unknown=True, observed_count=value,
                        first_observation_already_positive=previous_zero is None)
        previous_zero = row
    return dict(status="no_positive_observed" if previous_zero is not None else "unknown_no_valid_coverage",
                exact_event_time_unknown=True)


def validate_prefix(prefix):
    if prefix is None:
        return dict(status="pending_prefix_index", valid=None, controls=None)
    errors = []
    controls = prefix.get("controls") if isinstance(prefix, dict) else None
    chunks = prefix.get("index") if isinstance(prefix, dict) else None
    if not _count(controls) or not isinstance(chunks, list):
        return dict(status="invalid_prefix_schema", valid=False, controls=controls)
    if not all(isinstance(v, dict) and _count(v.get("controls")) for v in chunks):
        errors.append("chunk_control_schema")
    elif sum(v["controls"] for v in chunks) != controls:
        errors.append("chunk_controls_do_not_sum_to_total")
    if prefix.get("physical_callback_replay") is not False:
        errors.append("control_prefix_not_declared_distinct_from_physics_replay")
    return dict(status="text_index_counts_valid" if not errors else "invalid_prefix_coverage",
                valid=not errors, controls=controls, errors=errors,
                NPZ_contents_read=False, model_contents_read=False)


def analyze_curve(text=None, *, go=None, prefix=None, lifetime=None, final=None,
                  generic_metrics=None, expected_envs=20000, provenance=None):
    go = go if isinstance(go, dict) else None
    go_epoch = None if go is None else go.get("learning_started_epoch")
    go_valid = _finite(go_epoch)
    source_sha = None if go is None else go.get("source_SHA")
    result = dict(schema=SCHEMA, analysis_only_not_training_admission=True,
                  actual_closing_inputs_status="pending" if text is None else "provided_text_only",
                  GO=go, bootstrap_source_SHA=source_sha,
                  bootstrap_source_status="known_from_original_GO" if source_sha is not None else "unknown",
                  provenance=provenance or {}, rows=[], issues=[],
                  not_frozen_skill_or_causal_PPO_comparison=True,
                  count_semantics=dict(takeoff="original task counter cumulative positive deltas",
                                       cross="both original leading edges crossed; not whole footprint or landing",
                                       landing="original task landing counter cumulative positive deltas",
                                       recovery="original task recovery counter cumulative positive deltas"),
                  losses_are_imagination_and_prediction_not_physical_success=True,
                  generic_velocity_metrics_uninterpreted=generic_metrics,
                  generic_velocity_success_is_not_H1_step270_graduation=True,
                  physical_trajectory_or_foreign_dynamics_read=False)
    if text is None:
        result.update(status="pending_actual_85_closing_curve", curve_summary=None,
                      first_positive=None, prefix_coverage=validate_prefix(prefix),
                      final_manifest=final, native_FINAL_status="unknown_no_FINAL" if final is None else "provided_unvalidated")
        return result
    parsed, parse_issues = parse_curve(text)
    result["issues"].extend(parse_issues)
    previous = None
    previous_events = None
    known_fields = set(COUNTERS) | {"epoch", "GO_elapsed_s", "events", "wm_last", "policy_last", "not_frozen_evaluation_or_causal_PPO_comparison"}
    for line, raw in parsed:
        errors = []
        elapsed, epoch = raw.get("GO_elapsed_s"), raw.get("epoch")
        if not _finite(elapsed) or elapsed < 0 or not _finite(epoch):
            errors.append("clock_schema_or_negative_elapsed")
        elif go_valid and abs((epoch - go_epoch) - elapsed) > 0.05:
            errors.append("GO_elapsed_disagrees_with_original_GO_epoch")
        for key in COUNTERS:
            if not _count(raw.get(key)):
                errors.append(key + "_not_nonnegative_integer")
        if _count(raw.get("completed_control_rows")) and raw.get("environment_transitions") != raw["completed_control_rows"] * expected_envs:
            errors.append("curve_transition_product_mismatch")
        if previous is not None:
            for key in COUNTERS + ("GO_elapsed_s", "epoch"):
                if _finite(raw.get(key)) and raw[key] < previous[key]:
                    errors.append(key + "_decreased")
        event_values, event_errors = validate_events(raw.get("events"), raw.get("completed_control_rows"), expected_envs)
        if not event_errors and previous_events is not None:
            if any(event_values[k] < previous_events[k] for k in EVENTS):
                event_errors.append("cumulative_original_event_count_decreased")
        wm, wm_errors = _losses(raw.get("wm_last"), WM_NAMES)
        pi, pi_errors = _losses(raw.get("policy_last"), PI_NAMES)
        row = dict(line=line, epoch=epoch, GO_elapsed_s=elapsed,
                   **{k: raw.get(k) for k in COUNTERS},
                   update_counters_valid=not errors,
                   original_completed_events=event_values,
                   event_coverage_valid=not errors and not event_errors,
                   update_errors=errors, event_coverage_errors=event_errors,
                   WM_losses=wm, Pi_imagination_outputs=pi,
                   loss_errors=wm_errors + pi_errors,
                   original_counter_snapshot=raw.get("events"),
                   uninterpreted_fields={k: v for k, v in raw.items() if k not in known_fields})
        result["rows"].append(row)
        if not errors:
            previous = row
        if row["event_coverage_valid"]:
            previous_events = event_values
    valid = [v for v in result["rows"] if v["update_counters_valid"]]
    event_valid = [v for v in result["rows"] if v["event_coverage_valid"]]
    prefix_report = validate_prefix(prefix)
    expected_final_rows = prefix_report.get("controls") if prefix_report.get("valid") else None
    lifetime_values, lifetime_errors = validate_events(lifetime, expected_final_rows, expected_envs)
    if lifetime is None:
        lifetime_status = "pending_final_original_counter_snapshot"
    elif prefix_report.get("valid") is not True:
        lifetime_status = "partial_no_valid_text_prefix_coverage"
    else:
        lifetime_status = "full_completed_control_coverage" if not lifetime_errors else "invalid_final_counter_coverage"
    if lifetime is not None and not lifetime_errors and event_valid:
        last_events = event_valid[-1]
        if lifetime["complete_control_rows"] < last_events["completed_control_rows"]:
            lifetime_errors.append("final_counter_earlier_than_curve")
        if any(lifetime_values[k] < last_events["original_completed_events"][k] for k in EVENTS):
            lifetime_errors.append("final_cumulative_event_count_below_curve")
        if lifetime_errors:
            lifetime_status = "invalid_final_counter_coverage"
    summary = None if not valid else {k: valid[-1][k] for k in COUNTERS + ("epoch", "GO_elapsed_s")}
    if summary is not None:
        summary["scope"] = "last_valid_curve_observation_not_necessarily_terminal"
    result.update(curve_summary=summary, parsed_curve_rows=len(parsed), valid_update_rows=len(valid),
                  valid_event_rows=len(event_valid), prefix_coverage=prefix_report,
                  final_counter_coverage=dict(status=lifetime_status, errors=lifetime_errors,
                                              raw_snapshot=lifetime, observed_counts=lifetime_values),
                  final_manifest=final,
                  native_FINAL_status="unknown_no_FINAL" if final is None else "present_metadata_only_not_checkpoint_qualified",
                  first_positive={key: _first_positive(result["rows"], key, True) for key in EVENTS})
    result["first_positive"].update({key: _first_positive(result["rows"], key) for key in ("world_updates", "policy_updates")})
    all_valid = len(valid) == len(parsed) and len(event_valid) == len(parsed) and not parse_issues and bool(parsed)
    result["status"] = "curve_text_valid_final_coverage_pending" if all_valid else "partial_or_invalid_curve_text_preserved"
    if all_valid and lifetime_status == "full_completed_control_coverage":
        result["status"] = "curve_text_and_final_completed_control_coverage_valid"
    if not go_valid:
        result["issues"].append(dict(kind="original_GO_epoch_unknown", GO_elapsed_values_preserved_but_not_independently_verified=True))
    if final is not None and isinstance(final, dict):
        final_epoch = final.get("epoch")
        result["final_manifest_write_GO_elapsed_s"] = final_epoch - go_epoch if go_valid and _finite(final_epoch) else None
        result["final_manifest_write_is_not_original_accounting_terminal"] = True
        declared = final.get("final")
        result["native_final_checkpoint_metadata"] = declared  # Metadata only. Never open its path.
        if isinstance(declared, dict) and summary is not None:
            checks = {"updates": "native_iteration", "world_updates": "world_updates", "policy_updates": "policy_updates"}
            result["final_counters_not_earlier_than_last_curve"] = all(_count(declared.get(k)) and declared[k] >= summary[v] for k, v in checks.items())
    return result


def collector_inputs(collector):
    """Resolve exact known basenames from producer-pinned all_texts; no scan."""
    if not isinstance(collector, dict):
        raise ValueError("collector object required")
    records = collector.get("all_texts")
    if not isinstance(records, list):
        raise ValueError("collector all_texts missing")
    result, pins = {}, {}
    suffixes = {"curve": "/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl",
                "go": "/job0/GO_PRODUCTION.json",
                "prefix": "/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json",
                "lifetime": "/job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json",
                "final": "/job0/production/FINAL.json"}
    for key, suffix in suffixes.items():
        matches = [r for r in records if isinstance(r, dict)
                   and str(r.get("relative", "")).replace("\\", "/").startswith("e2/")
                   and str(r.get("relative", "")).replace("\\", "/").endswith(suffix)]
        if len(matches) > 1:
            raise ValueError("ambiguous collector text path for " + key)
        if not matches:
            continue
        record = matches[0]
        text, pin = read_text(record["local_path"])
        if pin["bytes"] != record.get("bytes") or pin["SHA"] != record.get("SHA"):
            raise ValueError("collector text pin mismatch: " + key)
        result[key] = text if key == "curve" else decode_json(text)
        pins[key] = pin
    result["provenance"] = dict(text_inputs=pins,
                                 collector_actual_finite_transport_returned=collector.get("actual_finite_transport_returned"),
                                 original_accounting_segment_uninterpreted=(collector.get("authority72") or {}).get("original_segment"),
                                 no_model_metadata_paths_opened=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector-json")
    parser.add_argument("--curve-jsonl")
    for name in ("go", "prefix", "lifetime", "final", "generic-metrics"):
        parser.add_argument("--" + name + "-json")
    parser.add_argument("--out-dir", required=True, help="fresh local output directory")
    args = parser.parse_args(argv)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=False)
    values, pins = {}, {}
    try:
        if args.collector_json:
            collector, pin = read_json(args.collector_json)
            values = collector_inputs(collector)
            pins["collector"] = pin
        if args.curve_jsonl:
            if "curve" in values:
                raise ValueError("collector plus explicit curve is ambiguous")
            values["curve"], pins["curve"] = read_text(args.curve_jsonl, (".jsonl",))
        for key in ("go", "prefix", "lifetime", "final", "generic_metrics"):
            path = getattr(args, key + "_json")
            if path:
                if key in values:
                    raise ValueError("collector plus explicit " + key + " is ambiguous")
                values[key], pins[key] = read_json(path)
        provenance = values.pop("provenance", {})
        provenance["explicit_inputs"] = pins
        curve = values.pop("curve", None)
        report = analyze_curve(curve, provenance=provenance, **values)
    except Exception as error:
        report = dict(schema=SCHEMA, status="reader_input_error_preserved", exception_type=type(error).__name__,
                      error=str(error), provenance=pins, no_model_or_plant_access=True)
        (out / "READER_ORIGINAL_ERROR.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf8")
        raise
    (out / "NATIVE_CURVE_TEXT_ANALYSIS.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf8")
    print(json.dumps(dict(status=report["status"], output=str(out.resolve()), actual_curve_provided=curve is not None)))
    return report


if __name__ == "__main__":
    main()
