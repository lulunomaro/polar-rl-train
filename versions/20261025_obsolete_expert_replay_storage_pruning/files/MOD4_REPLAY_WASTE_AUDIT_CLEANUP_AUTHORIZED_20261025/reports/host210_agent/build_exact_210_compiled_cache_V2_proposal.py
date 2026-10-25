"""Incremental local metadata/text-only review of closed, task-owned compiler caches."""
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

O = Path(__file__).resolve().parent
S = O.parent
W = S.parent.parent
T = W / "MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021"
DURABLE = "/mnt/mod4_linux_durable_20261013/"
rows = [json.loads(x) for x in (O / "PROJECT_NAMESPACE_FILE_METADATA_ACTUAL.jsonl").open(encoding="utf-8")]
by_path = {r["path"]: r for r in rows}
registry = {}
errors = []

def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))

reports = list(T.glob("*/reports/*CLOSED*CANONICAL_COST_ACTUAL.json"))
reports += [p for stage in W.glob("MOD4_TWO_LINUX_POLICY50_COHORT_*")
            for p in (stage / "reports").glob("TWO50_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json")]
for p in reports:
    d = load(p)
    outflags = {k: v for k,v in d.items() if isinstance(v, bool) and "actual_out" in k}
    if not outflags or not all(outflags.values()):
        continue
    owner = d.get("owner_exit", {})
    if not owner.get("original_cost_settled"):
        continue
    node = d.get("H1_node_exit", d.get("e2_node_exit", {}))
    if not node.get("actual_all_own_children_waited"):
        continue
    roots = Counter()
    textrows = d.get("text_files", [])
    for r in textrows:
        path = r.get("path", "")
        relative = r.get("relative", "")
        if path.startswith(DURABLE) and relative and path.endswith("/" + relative):
            roots[path[:-(len(relative) + 1)]] += 1
    if not roots:
        continue
    root = roots.most_common(1)[0][0]
    # These receipts bind one exact task root, rather than a broad MOD4 prefix.
    if len(roots) != 1:
        errors.append({"path": str(p), "reason": "Multiple task roots in receipt; excluded", "roots": list(roots)})
        continue
    node_rows = [r for r in textrows if r.get("path", "").endswith("/NODE_EXIT_ACTUAL.json")]
    evidence = {"local_closed_receipt": str(p), "actual_out_flags": outflags,
                "owner_exit": owner, "node_exit": node,
                "remote_owner_exit": root + "/owner/OWNER_EXIT_ACTUAL.json",
                "remote_node_exit": node_rows[0]["path"] if node_rows else None,
                "remote_node_exit_producer_SHA": node_rows[0].get("SHA") if node_rows else None,
                "scope": "Historical terminal receipt; current no-owner and unchanged metadata still require fresh execution guard."}
    registry[root] = evidence

# The rank0 owner terminal text was inspected directly in the first batch.
rank = "MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016"
rank_local = W / rank / "final878_actual/source210"
rank_owner = load(rank_local / "OWNER_EXIT_ACTUAL.json")
rank_final = load(rank_local / "THREE_RANK_FINAL_ACTUAL.json")
assert rank_owner["own_locks_released"] and rank_owner["canonical_active_settled"]
assert rank_final["complete"] and all(r["returncode"] == 0 for r in rank_final["rows"])
registry[DURABLE + rank] = {"local_closed_receipt": str(rank_local / "THREE_RANK_FINAL_ACTUAL.json"),
    "local_owner_exit": str(rank_local / "OWNER_EXIT_ACTUAL.json"), "owner_exit": rank_owner,
    "remote_owner_exit": DURABLE + rank + "/OWNER_EXIT_ACTUAL.json",
    "remote_final": DURABLE + rank + "/THREE_RANK_FINAL_ACTUAL.json", "all_three_returncodes": [0,0,0]}

def cache_kind(r):
    p = r["path"]
    if r["kind"] != "cache_or_temporary_candidate_only":
        return None
    if "/runtime/" in p or "/installed/" in p or "/site-packages/" in p or "/__pycache__/" in p:
        return None
    if re.search(r"/(?:job0/)?tmp/wp_pch_[^/]+/[^/]+\.pch$", p):
        return "task_private_Warp_precompiled_header"
    if "/cache/warp/" in p and p.endswith(".cubin"):
        return "task_private_Warp_compiled_CUDA_binary"
    if re.search(r"/home/\.nv/ComputeCache/[0-9a-f]/[0-9a-f]/[0-9a-f]+$", p):
        return "task_private_NVIDIA_ComputeCache"
    return None

candidates = []
pending = defaultdict(lambda: {"files": 0, "bytes": 0, "allocated_bytes": 0, "remote_terminal_receipt_paths_metadata_present": []})
candidate_groups = defaultdict(lambda: {"files": 0, "bytes": 0, "allocated_bytes": 0, "by_kind": Counter()})
all_cache_total = sum(r["bytes"] for r in rows if r["kind"] == "cache_or_temporary_candidate_only")
compiler_total = 0
for r in rows:
    kind = cache_kind(r)
    if kind is None:
        continue
    compiler_total += r["bytes"]
    namespace = r["root"] + "/" + r["relative"].split("/")[0]
    if r["nlink"] != 1 or namespace not in registry:
        g = pending[namespace]
        g["files"] += 1
        g["bytes"] += r["bytes"]
        g["allocated_bytes"] += r["allocated_bytes"]
        continue
    c = dict(r)
    c.update(metadata_kind=c.pop("kind"), kind=kind,
             regular=True, symlink=False,
             file_type_evidence="Original inventory only writes stat.S_ISREG entries and skips symlinks; mode stores permission bits only.",
             producer_SHA=None, producer_SHA_status="Not supplied in producer text; compiled content not opened or rehashed.",
             closedproof=registry[namespace],
             reference_unusedreason="Task-private rebuildable compiler output under closed namespace. Runtime code, dependencies, original .cu/.meta/JSON/log/report text and checkpoints are retained.",
             disposition="candidate_exact_unlink_after_fresh_closed_owner_and_metadata_guard")
    candidates.append(c)
    g = candidate_groups[namespace]
    g["files"] += 1
    g["bytes"] += c["bytes"]
    g["allocated_bytes"] += c["allocated_bytes"]
    g["by_kind"][kind] += c["bytes"]

for namespace,g in pending.items():
    g["reason"] = "No directly bound closed receipt inspected locally in this bounded review. Presence alone is not terminal content proof; excluded from executable candidates."
    g["remote_terminal_receipt_paths_metadata_present"] = [r["path"] for r in rows
        if r["path"].startswith(namespace + "/") and PurePosixPath(r["path"]).name in
        {"OWNER_EXIT_ACTUAL.json", "NODE_EXIT_ACTUAL.json", "WORKER_EXIT_ACTUAL.json", "PARENT_EXIT_ACTUAL.json", "production_WAITED_EXIT_ACTUAL.json"}]

# Explain the apparent 12 GB raw group without treating every .npz as replay waste.
curb_root = DURABLE + "MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016"
curb_arrays = [r for r in rows if r["path"].startswith(curb_root + "/") and r["kind"] == "array_or_replay_candidate_only"]
curb_grouped = defaultdict(list)
for r in curb_arrays:
    curb_grouped[str(PurePosixPath(r["path"]).parent)].append(r)
curb_explained = []
for parent,files in sorted(curb_grouped.items()):
    is_native = "/native20k_then_production" in parent
    curb_explained.append({"path": parent, "files": len(files), "bytes": sum(r["bytes"] for r in files),
        "kind": "native_numerical_fixture" if is_native else "single_combined_production_retention_replay",
        "disposition": "retain_exact_native_fixture" if is_native else "retain_only_first_and_terminal_representative_same_file",
        "reason": "Exact source-bound original native chunks are a separate protected class; no permission inferred to discard a middle numerical fixture." if is_native else "This producer wrote one combined retention_prefix file for this stage. There is no middle path to unlink while preserving its first and last file; NPZ contents were not opened or rewritten.",
        "files_metadata": files})

inodes = {(r["device"], r["inode"]): r for r in candidates}
assert len(inodes) == len(candidates)
summary = {"candidate_files": len(candidates), "candidate_namespaces": len(candidate_groups),
           "logical_bytes": sum(r["bytes"] for r in candidates),
           "distinct_allocated_bytes": sum(r["allocated_bytes"] for r in inodes.values()),
           "nlink_gt1_candidate_count": 0, "actual_freed_bytes": None,
           "all_cache_classification_logical_bytes": all_cache_total,
           "strict_compiled_binary_scope_logical_bytes": compiler_total,
           "pending_closedproof_namespaces": len(pending), "pending_compiled_bytes": sum(g["bytes"] for g in pending.values()),
           "not_selected_other_cache_classification_bytes": all_cache_total-compiler_total,
           "THREE4090_raw_total_bytes": sum(r["bytes"] for r in curb_arrays),
           "THREE4090_native_fixture_bytes": sum(r["bytes"] for r in curb_arrays if "/native20k_then_production/" in r["path"]),
           "THREE4090_single_combined_retention_bytes": sum(r["bytes"] for r in curb_arrays if "/production_only/" in r["path"])}
out = {"epoch": time.time(), "host": "210", "status": "V2_INCREMENTAL_PROPOSAL_ONLY_NO_NETWORK_OR_MUTATION",
       "first_batch_103_reexecution_forbidden": True,
       "source_metadata": str(S / "HOST210_ALL_OWNED_PROJECT_FILE_METADATA.jsonl"),
       "source_regular_file_filter": str(S.parent / "remote_owned_replay_storage_metadata_v1.py"),
       "scope": "Only task-private .pch, Warp .cubin and NVIDIA ComputeCache binary outputs bound to inspected closed receipts. No shared .cache, installed environment, runtime code/dependencies, pyc, source or textual records selected.",
       "summary": summary,
       "required_fresh_guards": ["Exact metadata tuple and regular non-symlink nlink1", "Read bound owner/node terminal receipts and reject active task owner", "Only listed file unlinks; no directory recursion or wildcard deletion", "Keep all source/FINAL/latest/player/native/query/report/log/JSON/.cu/.meta/dependency files", "Measure actual space after execution; proposal bytes are not a freed-space claim"],
       "candidate_groups": [{"path": k, **v} for k,v in sorted(candidate_groups.items())],
       "candidates": candidates,
       "pending_closedproof_excluded_groups": [{"path": k, **v} for k,v in sorted(pending.items(), key=lambda kv:-kv[1]["bytes"])],
       "THREE4090_raw_group_explanation": curb_explained,
       "reader_errors_and_exclusions": errors,
       "no_remote_content_reads_raw_open_rehash_delete_move_training_GPU_inference_or_budget_write": True,
       "archive_status": "PENDING_ROOT_UNIQUE_GIT_STAGE"}
p = O / "EXACT_210_COMPILED_CACHE_INCREMENTAL_V2_PROPOSAL_ACTUAL.json"
p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
print("written",p)
