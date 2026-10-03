"""Review existing frozen outputs; no simulator, training or budget access."""
import hashlib
import json
import statistics
from pathlib import Path

D = Path(__file__).resolve().parent
read = lambda name: json.loads((D / name).read_text(encoding="utf8"))
receipt = read("MATURE5_CONTACT_RETRY1_PAIRED_CONTACT_READBACK.json")
assert receipt["stage"] == "completed"
assert all(receipt[k] for k in (
    "initial_root_q_parameters_exact", "read_only_hook_behavior_exact",
    "non_highrate_groups_exact", "ledger_bytes_exact"))
assert not any(receipt[k] for k in ("PPO_performed", "production_changed", "budget_changed"))
reports = {}
for mode in ("control6", "substep6", "substep5"):
    p = D / f"MATURE5_CONTACT_RETRY1_{mode}.json"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == receipt["output_sha256"][mode]
    r = read(p.name)
    assert r["checkpoint"] == receipt["source"]["path"]
    assert r["profile"] == "white_v2" and r["seed"] == 20261002
    assert all(r["alive"]) and not r["nonfinite"] and r["physical_smoke_pass"]
    reports[mode] = r
assert reports["control6"]["per_environment"] == reports["substep6"]["per_environment"]
metrics = {}
keys = (
    "loaded_substep_fraction", "mean_normal_force_N", "normal_force_rms_N",
    "peak_normal_force_N", "loaded_time_mean_tangent_speed",
    "loaded_impulse_weighted_tangent_speed", "rolling_impulse_weighted_abs_speed",
    "lateral_impulse_weighted_abs_speed", "mesh_all_substep_mean_speed",
    "mesh_loaded_substep_mean_speed", "mesh_unloaded_substep_mean_speed",
    "loaded_frames_over015_fraction", "positive_force_point_peak_speed",
    "longest_wheel_under10_s")
body_keys = (
    "yaw_rate", "spin_translation_speed", "peak_tilt", "peak_wheel_speed_rad_s",
    "peak_wheel_applied_torque_nm", "wheel_rating_clip", "leg_rating_clip",
    "left_slip", "right_slip")
summarize = lambda values: dict(min=min(values), mean=statistics.mean(values), max=max(values))
for mode in ("substep5", "substep6"):
    r = reports[mode]
    sub = r["substep_contact_readback"]
    assert sub["callbacks"] == 6000 and sub["sampling_s"] == .0005
    assert not sub["gate_changed"] and not sub["reward_changed"]
    a = sub["per_environment"]
    assert all(t == 5000 for row in a["valid_ticks"] for t in row)
    metrics[mode] = {}
    for gid in (7, 8):
        ids = [i for i, g in enumerate(r["group_ids"]) if g == gid]
        assert len(ids) == 8
        m = {name: {k: summarize([a[k][i][wheel] for i in ids]) for k in keys}
             for wheel, name in enumerate(("left", "right"))}
        m["body"] = {k: summarize([r["per_environment"][k][i] for i in ids]) for k in body_keys}
        m["environment_ids"] = ids
        metrics[mode][str(gid)] = m
output = dict(
    source=receipt["source"], receipt=receipt, sampling_seconds=.0005,
    rollout_seconds=3, warmup_excluded_seconds=.5,
    summaries="Per-environment min/mean/max; wheel indices left,right; interleaved group_ids",
    metrics=metrics,
    findings=[
        "Positive6 right mesh increase is strongest during force<10N intervals; loaded rolling residual also increases.",
        "Positive6 right loaded fraction declines while force RMS and body XY speed increase; causality is not established.",
        "Pure +/-5 and +/-6 have zero recorded actuator rating clips in this short control-sampled window.",
        "The previous COM/link evaluation repair is correct; it did not modify policy, reward or contact dynamics."
    ],
    next_decision="Prepare a single isolated rolling/load behavior adaptation; actual input/physical/old-skill/PPO checks must precede bounded trial. No blind mature5 loop or rejected6 restart.",
    caveats=[
        "Solver report-point post-step rigid-body speed is not tracked material-patch slip or real-hardware evidence.",
        "Force>=10N is a diagnostic filter; low force does not prove airborne state.",
        "Loaded statistics do not replace the original unfiltered15-second .15m/s admission gate.",
        "Three seconds and one seed do not certify skill or transfer. No reward or targeted PPO deployed."
    ])
(D / "MATURE5_CONTACT_PAIRED_REVIEW.json").write_text(json.dumps(output, indent=2), encoding="utf8")
print("Existing paired5/6 evidence verified; review saved. Production, budget and gates unchanged.")
