"""Bounded LOCAL saved-text review. Reads exactly two JSON texts; no referenced files.

No models/source/runtime/NPZ/assets/remote reads, imports, simulation, or promotion.
Run once with stdlib Python -B. Exclusive output creation preserves original failures.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import time
import traceback


HERE = Path(__file__).resolve().parent
L = HERE.parent
INPUT210 = L / "W35_210_OWN_STORAGE_PROFILE_READONLY_READERS_SOURCE_V1/reports/W35_210_OWN_STORAGE_FINAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json"
INPUT86 = L.parent / "MOD4_H1_FUDAN270_SHARED4090_RESOURCE_V104_20261029/reports/NEW86_W35_ACTUAL906_PARTIAL_FROZEN_COVERAGE_AND_NEW210_GPU_NATIVE24_ACTUAL.json"
METRICS = (
    "forward_abs_tracking_error_mean",
    "yaw_abs_tracking_error_mean",
    "height_abs_error_mean",
)


def emit_json(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def saved_text(path):
    raw = path.read_bytes()
    return json.loads(raw), {
        "path": str(path), "bytes": len(raw),
        "SHA256": hashlib.sha256(raw).hexdigest(),
        "read_scope": "this saved JSON text only; no referenced path followed",
    }


def numeric_finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def main():
    a, receipt210 = saved_text(INPUT210)
    b, receipt86 = saved_text(INPUT86)
    t = a["original_terminal"]
    r = t["result"]
    rows = r["all_population_metrics"]
    audit = r["original_command_audit_final"]
    families = audit["histogram_rows"]
    modes = audit["histogram_columns"]
    criterion_rows = [x for x in a["complete_original_own_UTF8"] if x["relative"].endswith("frozen_regression/ORIGINAL_W35_TASK_COMMAND_AND_TERMINATION_CRITERIA.json")]
    assert len(criterion_rows) == 1
    criteria = json.loads(criterion_rows[0]["UTF8"])
    flags = {x["name"]: x["time_out"] for x in criteria["criterion_terms"]}

    checks = {}
    def check(name, value):
        checks[name] = bool(value)
        assert value, name

    check("210_original_actual_wait_zero_no_deadline", t["actual_worker_waited"] and t["returncode"] == 0 and not t["deadline_terminated"])
    check("210_original_ownout_private_released", a["actual_terminal_allownout_private_release"] and t["private_EX_released"])
    check("210_original_execution_and_integrity", a["passed_original_frozen_execution"] and a["integrity_errors"] == [] and t["original_error"] is None and t["original_worker_errors"] == [])
    check("same_frozen_source", r["source_SHA"] == a["source_SHA"] == b["original20k_source_sha"])
    check("same_78_source_adaptation_updates", r["source_adaptation_updates"] == b["original_source_adaptation_updates"] == 78)
    check("210_unchanged_frozen_mean_17Adam648360", r["actual_mean_policy"] and r["core_actor_critic_STD_norm_optimizer_literal_unchanged"] and r["no_optimizer_step_no_norm_update"] and r["all17_Adam_steps"] == 648360)
    check("86_saved_frozen_integrity", b["original_allownout_wait_private_release"] and b["actor_critic_STD_norm_and_all17Adam648360_literal_unchanged"])
    check("source_assignment_same", audit["assignment_sha256"] == b["original_command_audit"]["assignment_sha256"] == criteria["retained_command_scope"]["assignment_sha256"])
    check("42_profiles_6_families_7_modes", len(families) == 6 and len(modes) == 7)
    check("210_full_request_1200_100_1100", len(rows) == r["controls"] == r["requested_controls"] == 1200 and r["warmup_controls"] == 100 and r["steady_controls"] == 1100 and not r["wall_time_limited"])
    check("210_24_seconds_50Hz_record", r["simulated_seconds"] == 24.0 and r["num_envs"] == 20000)
    check("210_controls_and_phases", all(x["control"] == i and x["phase"] == ("warmup" if i <= 100 else "steady") for i, x in enumerate(rows, 1)))
    check("210_all_population_counts", all(len(x["profile_counts"]) == 42 and all(isinstance(n, int) and n >= 0 for n in x["profile_counts"]) and sum(x["profile_counts"]) == 20000 for x in rows))
    check("210_metric_values_finite", all(numeric_finite(x[k]) for x in rows for k in METRICS + ("moving_world_progress_abs_error_mean",)))
    check("210_height_command_025", all(x["height_command_m"] == criteria["height_command_m"] == .25 for x in rows))
    check("210_physics_8_callbacks_per_control", all(x["physics_tick"] == 8 * x["control"] for x in rows))
    phase_counts = [[sum(x["profile_counts"][p] for x in rows if x["phase"] == phase) for p in range(42)] for phase in ("warmup", "steady")]
    check("210_fresh_window_histograms_exact", phase_counts == r["warmup_and_steady_profile_control_counts"])
    check("210_reason_schema_original_flags", set(r["original_termination_reason_counts"]) == set(flags))

    def aggregate(selected):
        population = sum(sum(x["profile_counts"]) for x in selected)
        moving_counts = [sum(x["profile_counts"][p] for p in range(42) if p % 7 in (4, 5)) for x in selected]
        moving = sum(moving_counts)
        means = {k: sum(x[k] * sum(x["profile_counts"]) for x in selected) / population for k in METRICS}
        means["moving_world_progress_abs_error_population_weighted_mean"] = sum(x["moving_world_progress_abs_error_mean"] * n for x, n in zip(selected, moving_counts)) / moving if moving else None
        return {
            "controls": len(selected), "seconds_at_recorded_50Hz": len(selected) * .02,
            "population_environment_controls": population,
            "moving_environment_controls": moving,
            "moving_share_of_population_controls": moving / population,
            "means": means,
            "terminated_mask_events": sum(x["terminated_count"] for x in selected),
            "truncated_mask_events": sum(x["truncated_count"] for x in selected),
        }

    stats210 = {phase: aggregate([x for x in rows if phase == "whole" or x["phase"] == phase]) for phase in ("whole", "warmup", "steady")}
    stats86 = {}
    for phase, key in (("whole", "whole_window_means"), ("steady", "steady_means")):
        source = b[key]
        stats86[phase] = {
            "controls": source["controls"], "seconds_at_recorded_50Hz": source["controls"] * .02,
            "moving_environment_controls": source["moving_environment_control_count"],
            "means": {k: source[k] for k in METRICS + ("moving_world_progress_abs_error_population_weighted_mean",)},
            "provenance": "previous saved text summary; underlying row arrays not present in this permitted input, not recomputed",
        }
    delta = {phase: {k: stats210[phase]["means"][k] - stats86[phase]["means"][k] for k in stats86[phase]["means"]} for phase in stats86}

    reasons = []
    for name, values in r["original_termination_reason_counts"].items():
        check("210_reason_counts_" + name, len(values) == 2 and all(len(v) == 42 and all(isinstance(n, int) and n >= 0 for n in v) for v in values))
        sums = list(map(sum, values))
        old = b["original_termination_reason_counts"][name]
        check("86_original_timeout_flag_" + name, old["original_time_out"] == flags[name])
        reasons.append({"name": name, "original_time_out": flags[name], "210_warmup_occurrences": sums[0], "210_steady_occurrences": sums[1], "210_total_occurrences": sum(sums), "86_warmup_occurrences": old["warmup"], "86_steady_occurrences": old["steady"], "86_total_occurrences": old["total"]})
    reason_timeout_sum = sum(x["210_total_occurrences"] for x in reasons if x["original_time_out"])
    check("210_saved_reason_unions_exact", r["termination_and_truncation_union_exact"])
    timeout_overlap = reason_timeout_sum - stats210["whole"]["truncated_mask_events"]
    check("timeout_reason_occurrences_not_less_than_mask", timeout_overlap >= 0)

    profile_rows = []
    for p in range(42):
        profile_rows.append({
            "index": p, "family": families[p // 7], "mode": modes[p % 7],
            "warmup_environment_controls": phase_counts[0][p],
            "steady_environment_controls": phase_counts[1][p],
            "full_environment_controls": phase_counts[0][p] + phase_counts[1][p],
            "210_maximum_continuous_seconds_saved": r["profile_maximum_continuous_seconds"][p],
            "210_steady_complete_signed_world_cycle_events": r["steady_actual_complete_signed_world_cycles_no_cross_reset"][p],
            "86_saved_signed_world_cycle_events": b["signed_world_cycles_by_profile"][p],
            "per_profile_MAE": "not saved; cannot derive from aggregate means",
            "unique_environment_success_count": "not saved; event counts cannot identify unique environments",
        })
    family_rows = [{
        "family": name,
        "210_warmup_environment_controls": sum(phase_counts[0][f*7:(f+1)*7]),
        "210_steady_environment_controls": sum(phase_counts[1][f*7:(f+1)*7]),
        "210_modes_observed": [modes[m] for m in range(7) if sum(phase_counts[k][f*7+m] for k in (0,1))],
        "210_final_population_snapshot": audit["actual_family_counts"][f],
        "86_final_population_snapshot": b["original_command_audit"]["actual_family_counts"][f],
    } for f, name in enumerate(families)]

    missing = [
        "No saved per-profile tracking/height/world-progress MAE or tail/quantile; aggregate errors cannot certify each retained command/family/sign.",
        "Signed world cycles are completion events, not distinct successful environments; no saved unique-environment success denominator or per-environment all-sign completion proof.",
        "Continuous-duration maxima are saved per profile, not a population survival distribution or a duration assigned to every environment. Straight/moving maxima do not cover the entire 22s steady window per mode.",
        "The five G3 families are represented, but retained straight/world-yaw coverage occurs only on plane in this case; do not claim those modes on the other four families or pure high spin.",
        "Original termination checks remain unchanged. Four non-timeout base_contact events are observed; no statement that every environment satisfies uninterrupted full criteria is supported.",
        "The saved original criteria text has termination parameters but no full legacy quantitative graduation thresholds/required population pass rate or per-profile sustained-error criterion; original graduation cannot be reproduced from these two texts.",
        "The 86 run is wall-time-limited at 906 of 1200 controls. The 210 run completes its requested 1200, but unequal horizons and unmatched per-environment trajectories prevent a hardware or causal skill-improvement conclusion.",
        "The retained profile literal world05_yaw12 and radius1.0 are saved; actual per-step command vectors/ranges by profile are not available in the two permitted inputs, so numerical command coverage beyond saved labels is unverified.",
        "Authoring-mesh ground support queries are explicitly not contact-force certification.",
        "No complete typed WM transition dataset is established: aggregate metrics and selected32 artifact metadata do not supply pack127/ingress/executed action/queue/xi-DR/terminal-before-reset/dt fields for all transitions.",
    ]
    out = {
        "epoch": time.time(), "kind": "W35_saved_text_210_full_vs_NEW86_partial_profile_review_v1",
        "scope": "Only the two specified saved JSON texts; no referenced file followed, source/model/NPZ/assets/remote/simulation read or execution",
        "input_receipts": [receipt210, receipt86], "same_source_SHA": r["source_SHA"],
        "original_criteria_saved_text_receipt": {k:v for k,v in criterion_rows[0].items() if k != "UTF8"},
        "original_criteria_preserved": criteria,
        "original210_execution": {k:v for k,v in t.items() if k != "result"},
        "saved_text_consistency_checks": checks,
        "210_recomputed_actual_population_weighted_metrics": stats210,
        "86_saved_summary_metrics_not_recomputed": stats86,
        "210_minus86_different_observed_window_mean_differences_not_causal": delta,
        "formulas": {
            "population_MAE": "sum(control population count * saved control mean) / sum(control population count)",
            "moving_count": "sum(actual profile_counts[7*k+4] + profile_counts[7*k+5]) for k=0..5 at each control",
            "moving_MAE": "sum(actual moving_count * saved moving_world_progress_abs_error_mean) / sum(actual moving_count)",
            "saved_metric_units": "preserve source field names; no unsupported world-progress metric unit inferred",
        },
        "original_termination_reason_occurrences": reasons,
        "210_timeout_reason_occurrence_total": reason_timeout_sum,
        "210_truncated_mask_event_total": stats210["whole"]["truncated_mask_events"],
        "210_extra_timeout_reason_occurrences_due_to_overlap": timeout_overlap,
        "termination_interpretation": "time_out and rough_route_boundary are original timeout terms. Reason counts can overlap; mask events are not unique environments, and terminated/truncated combined union is not saved.",
        "profile_rows_all42": profile_rows,
        "family_coverage": family_rows,
        "signed_cycle_event_totals": {"210_steady": sum(x["210_steady_complete_signed_world_cycle_events"] for x in profile_rows), "86_saved": sum(x["86_saved_signed_world_cycle_events"] for x in profile_rows)},
        "audit_histogram_scope": "Final audit sample/control histograms are not used as fresh-case exposure; use saved per-control rows and exact fresh warmup/steady histograms. Final eligible/linear/moving/standing values are snapshots, not unique counts or cumulative successes.",
        "original_command_audit_final210": audit,
        "original_command_audit_final86": b["original_command_audit"],
        "210_selected32_metadata_only": r["selected32_motion_trace"],
        "86_selected32_metadata_only": b["selected32_artifact_metadata_only"],
        "210_large_artifact_metadata_only_preserved": a["large_artifact_metadata_only"],
        "original86_acceptance_text_preserved": b["acceptance"],
        "skill_remaining_conditions_and_evidence_limits": missing,
        "conclusion": "210 requested frozen execution coverage is complete; 86 requested coverage is partial. Frozen integrity passes in saved receipts. Skill graduation remains PENDING, not inherited; no new model/source promotion and no complete typed WM dataset claim.",
        "skill_graduation": False, "complete_typed_WM_dataset": False,
        "no_new_GPU_training_evaluation_or_authority_write": True,
        "git_state": "EXPLICIT_PENDING ordinary supplement by root; no trial/tag created by this text-only review",
    }
    emit_json("W35_SAVED_TEXT_COMPARISON_COMPLETE_ACTUAL.json", out)
    emit_json("INPUT_SAVED_TEXT_BYTES_SHA_AND_SCOPE_ACTUAL.json", out["input_receipts"])

    def f(value):
        return f"{value:.9f}"
    md = [
        "# W35：210完整冻结回归与86部分回归的保存文本审查", "",
        "210已完成请求的1200 controls（24.00s），含100 warmup/1100 steady（2.00s/22.00s）；86只完成906（18.12s），含100/806（2.00s/16.12s），原wall-time-limited状态保留。两份文本的同源模型、mean策略与原17个Adam648360/归一化不变证据成立；这不等于技能毕业。", "",
        "本审查只读取指定两个JSON文本；未跟随其中路径，未读取代码、模型、NPZ、USD或其他原始数据，未联网或运行仿真。86使用原保存汇总，210从1200行指标按真实人口重算。输入字节SHA见同目录JSON。", "",
        "## 全人口与moving子集", "",
        "|指标（原保存字段）|86全窗906|210全窗1200|86 steady806|210 steady1100|", "|---|---:|---:|---:|---:|",
    ]
    for key in METRICS + ("moving_world_progress_abs_error_population_weighted_mean",):
        md.append("|" + key + "|" + "|".join(f(v) for v in (stats86["whole"]["means"][key],stats210["whole"]["means"][key],stats86["steady"]["means"][key],stats210["steady"]["means"][key])) + "|")
    md += ["", f"210全窗人口control={stats210['whole']['population_environment_controls']:,}，moving人口control={stats210['whole']['moving_environment_controls']:,}（{stats210['whole']['moving_share_of_population_controls']:.4%}）；steady分别{stats210['steady']['population_environment_controls']:,}/{stats210['steady']['moving_environment_controls']:,}（{stats210['steady']['moving_share_of_population_controls']:.4%}）。86原汇总moving分母为{stats86['whole']['moving_environment_controls']:,}/{stats86['steady']['moving_environment_controls']:,}。", "",
        "全人口MAE按各control人口加权。moving误差仅按每行实际profile_counts[7*k+4/5]人口加权，不能对control均值简单平均，不能用全人口forward/yaw小误差代替moving能力。原指标未在这两份文本中给出world-progress单位，本报告不补造单位或验收阈值。两窗时长不同且没有逐环境配对，不推断硬件/模型因果提升。", "",
        "## 原终止原因", "", "|原term|原timeout标记|86 warmup/steady/合计|210 warmup/steady/合计|", "|---|---|---:|---:|",
    ]
    for x in reasons:
        md.append(f"|{x['name']}|{x['original_time_out']}|{x['86_warmup_occurrences']}/{x['86_steady_occurrences']}/{x['86_total_occurrences']}|{x['210_warmup_occurrences']}/{x['210_steady_occurrences']}/{x['210_total_occurrences']}|")
    md += ["", f"210 terminated mask事件{stats210['whole']['terminated_mask_events']}，truncated mask事件{stats210['whole']['truncated_mask_events']}。timeout原因发生数合计{reason_timeout_sum}，比truncated mask多{timeout_overlap}个重叠原因发生数；不能把原因相加当独立reset。原time_out和rough_route_boundary均属于timeout，后者不能重分类为技能失败。base_contact两机各4次，不能据此声称只失败4个独立环境；combined done union及unique env并未保存。", "",
        "原阈值逐项保留在JSON：bad_orientation .75rad、base_contact 50、closure .002m、mimic .05、low_base -1.0；未修改奖励/重置阈值。", "",
        "## 五G3与retained命令覆盖", "", "|family|210 warmup人口control|210 steady人口control|本窗出现模式|210/86最终人口快照|", "|---|---:|---:|---|---:|",
    ]
    for x in family_rows:
        md.append(f"|{x['family']}|{x['210_warmup_environment_controls']}|{x['210_steady_environment_controls']}|{', '.join(x['210_modes_observed']) or '未出现'}|{x['210_final_population_snapshot']}/{x['86_final_population_snapshot']}|")
    md += ["", "outside无人口不是缺失第六种G3；五种实际G3均有gentle/standing。本窗retained signed straight/world-yaw只出现在plane，其他四类没有这些命令覆盖。原profile literal为E1_G3_verified_plane_signed_straight_world05_yaw12_v1，radius1.0；pure_high_spin=false、position_correction=false。不能从profile名称补造未保存的逐帧命令范围。", "",
        "最终eligible/linear/moving/standing是瞬时快照；恢复的audit sample/control histogram不能当本24秒新窗口。下表使用每control原保存计数重算，且与原2×42 warmup/steady直方图逐项完全相同。", "",
        "|profile index/family/mode|warmup人口control|steady人口control|210保存最长连续秒|210 steady signed cycle事件|86保存signed cycle事件|", "|---|---:|---:|---:|---:|---:|",
    ]
    for x in profile_rows:
        md.append(f"|{x['index']} / {x['family']} / {x['mode']}|{x['warmup_environment_controls']}|{x['steady_environment_controls']}|{x['210_maximum_continuous_seconds_saved']:.9f}|{x['210_steady_complete_signed_world_cycle_events']}|{x['86_saved_signed_world_cycle_events']}|")
    md += ["", "210 steady负/正world-yaw各720/694，共1414次完整有符号world cycle事件；86各444/428，共872次。事件不是unique env，不是完成率。210 plane straight最长连续约3.54/2.94s，moving约6.52/6.32s；gentle/standing约19.64/20.00s，其余四G3约18.00s。每profile最长值既不是每环境持续时长，也不证明所有moving环境连续完成22s steady。保留原float32时长，不新增精度门槛。86输入汇总没有保存每profile连续时长，因此不推算。", "",
        "## 验收仍缺的证据", "",
    ]
    md += [f"- {x}" for x in missing]
    md += ["", "结论：210请求的冻结执行覆盖完成，86请求覆盖仍为部分；技能毕业保持PENDING，不继承原legacy毕业标签，不提升模型来源资格。本次只做文本审查，不是新PPO/评测/WM训练。全部新文件交root普通Git补档，未创建trial/tag。", ""]
    with (HERE / "W35_SAVED_TEXT_COMPARISON_COMPLETE_REVIEW.md").open("x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))
    print(json.dumps({"passed_saved_text_consistency": all(checks.values()), "checks": len(checks), "210_whole": stats210["whole"], "210_steady": stats210["steady"], "reason_overlap": timeout_overlap, "report": str(HERE / "W35_SAVED_TEXT_COMPARISON_COMPLETE_ACTUAL.json"), "skill_graduation": False}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        emit_json(f"ORIGINAL_TEXT_REVIEW_ERROR_{time.time_ns()}.json", {"epoch": time.time(), "original_traceback": traceback.format_exc(), "passed": False, "scope": "local two saved text inputs only"})
        raise
