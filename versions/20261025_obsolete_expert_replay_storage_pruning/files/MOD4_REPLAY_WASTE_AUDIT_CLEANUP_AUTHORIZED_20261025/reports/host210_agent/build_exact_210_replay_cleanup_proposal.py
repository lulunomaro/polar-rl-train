"""Prepare exact old replay unlink candidates from existing local text and metadata.

This writes reviewable JSON only. It never contacts a host, opens a binary,
hashes a raw file, alters a budget, or deletes a file.
"""
import json
import re
import time
from collections import defaultdict
from pathlib import Path

O = Path(__file__).resolve().parent
S = O.parent
W = S.parent.parent
T = W / "MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021"
DURABLE = "/mnt/mod4_linux_durable_20261013/"
META = O / "PROJECT_NAMESPACE_FILE_METADATA_ACTUAL.jsonl"
rows = {r["path"]: r for r in map(json.loads, META.open(encoding="utf-8"))}
candidates = []
retained = []
sequences = []
uncertain = []

def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))

def record(path, evidence, kind, reason, disposition, source_row=None):
    m = dict(rows[path])
    m["metadata_kind"] = m.pop("kind")
    m.update(kind=kind, disposition=disposition, producer_SHA=None,
             producer_SHA_status="not present in existing producer text; not recomputed",
             closedproof=evidence, reference_unusedreason=reason)
    if source_row:
        sha = source_row.get("SHA", source_row.get("sha256"))
        if sha:
            m["producer_SHA"] = sha
            m["producer_SHA_status"] = "existing producer index; raw not rehashed"
        if "bytes" in source_row:
            assert source_row["bytes"] == m["bytes"], (path, source_row["bytes"], m["bytes"])
    (candidates if disposition == "candidate_exact_unlink_after_fresh_guard" else retained).append(m)
    return m

rank_stage = W / "MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016"
rank_source = rank_stage / "final878_actual/source210"
rank_exit = load(rank_source / "OWNER_EXIT_ACTUAL.json")
rank_final = load(rank_source / "THREE_RANK_FINAL_ACTUAL.json")
assert rank_exit["own_locks_released"] and rank_exit["canonical_active_settled"]
assert rank_final["complete"] and all(r["returncode"] == 0 for r in rank_final["rows"])
rank_index_path = rank_source / "rank0/RETENTION_COMMAND_ACTUAL.json"
rank_index = load(rank_index_path)
rank_prefixes = [r for r in rank_index["trace_files"] if r["path"] in rows]
rank_prefixes.sort(key=lambda r: (r["first"], r["last"]))
all_rank_paths = {p for p in rows if p.startswith(DURABLE + rank_stage.name + "/rank0/") and "/rank0_retention_prefix_" in p and p.endswith(".npz")}
assert {r["path"] for r in rank_prefixes} == all_rank_paths
rank_evidence = {"local_owner_exit": str(rank_source / "OWNER_EXIT_ACTUAL.json"),
                 "local_final": str(rank_source / "THREE_RANK_FINAL_ACTUAL.json"),
                 "local_producer_index": str(rank_index_path),
                 "remote_owner_exit": DURABLE + rank_stage.name + "/OWNER_EXIT_ACTUAL.json",
                 "remote_final": DURABLE + rank_stage.name + "/THREE_RANK_FINAL_ACTUAL.json",
                 "all_three_returncodes": [r["returncode"] for r in rank_final["rows"]],
                 "owner_locks_released": True, "canonical_settled": True,
                 "not_a_claim_of_current_process_liveness": True}
for i,r in enumerate(rank_prefixes):
    keep = i in (0, len(rank_prefixes) - 1)
    record(r["path"], rank_evidence, "superseded_expert_retention_replay",
           "Keep first and terminal representative of closed final878 shared PPO; all original native fixtures, text reports, errors, logs, and final checkpoints retained. Current player uses E0/W35/gate148, H1 pair47/E2 cohort52/E3 pair47 and latest training pair67, so intermediate final878 training trajectories have no current replay dependency.",
           "retain_first_or_terminal_representative" if keep else "candidate_exact_unlink_after_fresh_guard", r)
sequences.append({"id": "closed_rank0_shared_PPO_final878", "present_raw_count": len(rank_prefixes),
                  "retained": [rank_prefixes[0]["path"], rank_prefixes[-1]["path"]],
                  "candidate_raw_count": len(rank_prefixes) - 2,
                  "anomaly_policy": "Original exit/final reports have no failed worker. Native physical controls remain fully protected; this selection does not prune them."})

stage_specs = [
    ("H1_STEP270_E3_REPAIR_PAIR_V3_20261022", "PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json", "H1step270_repair_2210v3"),
    ("H1_STEP270_E3_BOUNDED_TRACE_PAIR_V12_20261022", "PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json", "H1step270_boundedtrace_2210v12"),
    ("H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022", "PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json", "H1step270_rewardmigration_2210v18"),
    ("H1_STEP270_REWARD_H1_ONLY_V20_20261022", "H1_ONLY_CLOSED_CANONICAL_COST_ACTUAL.json", "H1step270_reward_H1only_2210v20"),
    ("H1_STEP270_REWARD_BOUNDARY_RESOURCE_V24_20261022", "H1_ONLY_CLOSED_CANONICAL_COST_ACTUAL.json", "H1step270_reward_boundary_2210v24"),
]
for stage_name, close_name, remote_name in stage_specs:
    stage = T / stage_name
    close_path = stage / "reports" / close_name
    close = load(close_path)
    h1 = close["cohort"]["rows"]["h1"]
    assert close["all_owner_H1_children_actual_out"]
    assert close["H1_node_exit"]["actual_all_own_children_waited"]
    assert close["owner_exit"]["original_cost_settled"]
    assert h1["returncode"] == 0 and h1.get("errors", []) == []
    prefix_parent = DURABLE + remote_name + "/h1/job0/production/control_prefix_raw/"
    index_path = stage / "current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json"
    index = load(index_path)
    indexed = {r["path"]: r for r in index["index"]}
    present = [p for p in rows if p.startswith(prefix_parent + "control_prefix_") and p.endswith(".npz")]
    present.sort(key=lambda p: int(re.search(r"control_prefix_(\d+)\.npz$", p).group(1)))
    assert len(present) > 2
    assert all(p in indexed for p in present)
    evidence = {"local_closed_receipt": str(close_path), "local_producer_index": str(index_path),
                "remote_owner_exit": DURABLE + remote_name + "/owner/OWNER_EXIT_ACTUAL.json",
                "remote_node_exit": DURABLE + remote_name + "/h1/NODE_EXIT_ACTUAL.json",
                "remote_worker_exit": DURABLE + remote_name + "/h1/job0/production_WAITED_EXIT_ACTUAL.json",
                "all_owner_H1_children_actual_out": True, "worker_returncode": h1["returncode"],
                "worker_errors": h1.get("errors", []), "owner_original_cost_settled": True,
                "not_a_claim_of_current_process_liveness": True}
    keep_paths = [present[0], present[-1]]
    counterpart_candidates = []
    for i,p in enumerate(present):
        keep = p in keep_paths
        disposition = "retain_first_or_terminal_representative" if keep else "candidate_exact_unlink_after_fresh_guard"
        record(p, evidence, "superseded_H1_training_control_replay",
               "Closed worker returncode 0 and empty error list. Retain first and last existing raw and their preupdate checkpoints; delete intermediate obsolete control prefixes after new human authorization. Latest65/67 and current player/source/native/query are different protected namespaces.", disposition, indexed[p])
        counterpart = indexed[p].get("preupdate_source")
        if counterpart and counterpart["path"] in rows:
            record(counterpart["path"], evidence, "preupdate_checkpoint_paired_only_with_obsolete_replay",
                   "Exact preupdate counterpart for " + p + "; source/FINAL/latest/current optimizer checkpoints excluded. Retained representatives keep their exact preupdate sources.", disposition, counterpart)
            if not keep:
                counterpart_candidates.append(counterpart["path"])
        elif counterpart:
            uncertain.append({"path": counterpart["path"], "disposition": "not_in_210_metadata_no_unlink_no_freed_bytes_claim", "paired_raw": p})
    sequences.append({"id": remote_name, "present_raw_count": len(present),
                      "retained": keep_paths, "candidate_raw_count": len(present)-2,
                      "candidate_preupdate_count": len(counterpart_candidates),
                      "anomaly_policy": "Closed worker errors are empty. First/terminal representatives and all textual diagnostics retained. This is not a skill graduation claim."})

assert len({r["path"] for r in candidates}) == len(candidates)
assert not ({r["path"] for r in candidates} & {r["path"] for r in retained})
inodes = defaultdict(list)
for r in candidates:
    inodes[(r["device"], r["inode"])].append(r)
unique_allocated = sum(v[0]["allocated_bytes"] for v in inodes.values())
single_link_allocated = sum(v[0]["allocated_bytes"] for v in inodes.values() if v[0]["nlink"] == 1)
by_kind = defaultdict(lambda: {"files": 0, "logical_bytes": 0, "allocated_bytes": 0})
for r in candidates:
    by_kind[r["kind"]]["files"] += 1
    by_kind[r["kind"]]["logical_bytes"] += r["bytes"]
    by_kind[r["kind"]]["allocated_bytes"] += r["allocated_bytes"]
summary = {"candidate_files": len(candidates), "candidate_logical_bytes": sum(r["bytes"] for r in candidates),
           "candidate_distinct_allocated_bytes": unique_allocated,
           "candidate_singlelink_distinct_allocated_bytes": single_link_allocated,
           "hardlinked_candidate_paths": [r["path"] for r in candidates if r["nlink"] > 1],
           "actually_freed_bytes": None, "by_kind": dict(by_kind),
           "retained_representative_files": len(retained),
           "retained_representative_logical_bytes": sum(r["bytes"] for r in retained)}
proposal = {"epoch": time.time(), "host": "210", "status": "PROPOSAL_ONLY_NO_REMOTE_MUTATION",
            "authorization": "New user instruction explicitly lowers threshold: obsolete closed replay sequences retain first/last and key abnormal representatives; intermediate raw and exact preupdate counterparts may be removed.",
            "metadata_source": str(S / "HOST210_ALL_OWNED_PROJECT_FILE_METADATA.jsonl"),
            "metadata_summary": str(S / "HOST210_NEW_REPLAY_STORAGE_METADATA_ACTUAL.json"),
            "protection_baseline": str(S / "CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json"),
            "required_fresh_execution_guard": ["Revalidate exact metadata tuple path/bytes/allocated_bytes/device/inode/nlink/mtime_ns and regular no-symlink status", "Read explicit owner/node/worker terminal receipts where needed; refuse a namespace with a current running owner", "No glob or recursive delete; unlink listed paths only and leave all report/log/index/source files", "Treat current FINAL/latest/source/player/native/query/current65-67 and unique current collision diagnostics as protected", "Keep before/after filesystem-space receipts; report measured bytes rather than sum of logical lengths as freed"],
            "summary": summary, "sequences": sequences,
            "candidates": candidates, "retained_representatives": retained, "uncertain_or_absent": uncertain,
            "other_retained_groups": [
                {"path_prefix": DURABLE + "H1step270_full20k_native180_2110v3", "reason": "Current reused exact H1 native fixture; all raw and text preserved."},
                {"path_prefix": DURABLE + "H1step270_cookedquery_full20k_2110v9", "reason": "Current reused 160k query/numerical fixture; preserved."},
                {"path_prefixes": [DURABLE + n for n in ["T3_1710v2", "T3_1710v10hr", "H125_1710n1"]], "reason": "Large controls/physics/native captures require distinct fixture classification; no filename-only deletion."},
                {"path_prefix": "/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results", "reason": "Mixed worldmesh query fixtures and distinct old diagnostic routes. Not included in first exact raw batch."},
                {"path_prefix": DURABLE + "H1step270_precision_rslv3_after67_2510", "reason": "Current valid FP32 baseline and failed benchmark diagnostics preserved in this first batch; no benchmark snapshot promoted to qualified source."},
                {"reason": "Unrelated InternVL/Mistral/Matlab/VIVE/recycle data, shared caches, installations and unknown owners excluded. No installation environment cleanup."}
            ],
            "read_errors_and_corrections": [
                {"action": "Initial local whole-workspace rg --files", "error": "Access denied to unrelated rmuc2026_work/unpack_verify_4zomhj13", "correction": "Subsequent searches restricted to project metadata and named MOD4 stages; this unrelated directory is excluded."},
                {"action": "Inline local reporting Python", "error": "SyntaxError: assignment expression cannot be used in a comprehension iterable expression", "correction": "Retried as a normal for loop; no remote operation or data mutation occurred."},
                {"action": "Initial inspection used Windows pathlib.Path for POSIX parent display", "error": "Only printed parent groups with Windows backslashes", "correction": "Final proposal preserves exact original POSIX path strings; no path rewriting."}
            ],
            "no_raw_content_load_rehash_delete_move_training_GPU_inference_network_or_budget_write": True,
            "archive_status": "PENDING_ROOT_UNIQUE_GIT_STAGE"}
out = O / "EXACT_210_REPLAY_CLEANUP_PROPOSAL_ACTUAL.json"
out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print("written", out)
