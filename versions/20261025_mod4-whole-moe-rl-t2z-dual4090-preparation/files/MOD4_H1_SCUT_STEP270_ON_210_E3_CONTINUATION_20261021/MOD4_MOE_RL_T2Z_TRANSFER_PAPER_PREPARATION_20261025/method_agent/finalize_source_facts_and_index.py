"""Read only small saved text/source, inventory this preparation; no Git/remote."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
WORKSPACE, STAGE = BASE.parents[2], BASE.parents[1]
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def receipt(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


manifest_path = WORKSPACE / "MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json"
manifest = json.loads(manifest_path.read_text())
player = WORKSPACE / "MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player"
negative_paths = [STAGE / "MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024/reports/4090_MATCHED_FROZEN_FINITE_RETURNED_ACTUAL.json",
                  STAGE / "MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024/reports/4090_SERIES_BASELINE_FROZEN_FINITE_RETURNED_ACTUAL.json",
                  STAGE / "MOE_SMALL_CURB_CONTACT_REPLAY_20261024/reports/4090_SMALL_CURB_V3_FROZEN_FINITE_RETURNED_ACTUAL.json"]
negative = []
for path in negative_paths:
    saved = json.loads(path.read_text())
    negative.append({"source": receipt(path), "saved_passed_frozen_execution": saved["final"]["passed_frozen_execution"],
                     "not_skill_qualification": True,
                     "cases": [{"case": row["case"], "variant": row["variant"],
                                "target_vx": row.get("target_vx"), "controls": row.get("controls"),
                                "expert_switches": row["expert_switches"],
                                "selected_expert_counts": row["selected_expert_counts"]}
                               for row in saved["final"]["cases"]]})
source_paths = [manifest_path, player / "rm7v7_moe_sim.py", player / "sim_runtime.py",
                player / "rm7v7_latest_moe.xml", player / "runtime_config.json",
                WORKSPACE / "AGENTS.md", WORKSPACE / "polar-rl-train/AGENTS.md",
                WORKSPACE / "polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md",
                WORKSPACE / "polar-rl-train/docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md"]
source_dir = STAGE / "MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/method_agent/integration_v1/upstream_source_receipts"
source_paths.extend(sorted(source_dir.glob("*")))
facts = {"id": "WHOLE_MOE_SOURCE_FACTS_" + stamp, "observed_utc": stamp,
         "current_player_manifest": receipt(manifest_path),
         "source_registry_from_saved_manifest_not_weights_rehashed": manifest["sources"],
         "current_gate_alias": "gate148", "new_five_way_learned_gate": manifest["new_five_way_learned_gate"],
         "whole_six_action_selection": manifest["whole_six_action_selection"],
         "weight_or_action_averaging": manifest["weight_or_action_averaging"],
         "skill_qualification": manifest["skill_qualification"], "policy_hz": manifest["policy_hz"],
         "mujoco_timestep_s_from_saved_xml": float(re.search(r'timestep="([^"]+)"', (player / "rm7v7_latest_moe.xml").read_text()).group(1)),
         "primary_research_backend_proposed_not_run": {"name": "PhysX", "physics_dt_ns": 2_500_000, "TGS": [32, 4]},
         "newer_training_source67_from_root_not_current_player": {
             "H1": {"Adam": 790000, "sha256": "d1dd187177a1878f007b05da26e39c5ee101e937d2d86f0948dde1ffd37f062e"},
             "E3": {"Adam": 837200, "sha256": "0487231c1feec62c9c60063b7f7227ebc7e859ef881a31879a719b0ef03196f7"}},
         "saved_routing_negative_evidence_not_new_evaluation": negative,
         "small_local_input_receipts": [receipt(p) for p in source_paths],
         "weights_or_large_npz_opened": False, "archive_status": "PENDING_ROOT_SUPPLEMENTAL_GIT"}
fact_path = BASE / "source_facts.json"
if fact_path.exists():
    raise RuntimeError("Freeze prior source_facts; append a new version rather than overwrite")
fact_path.write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
inventory = []
for path in sorted(BASE.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts or path.name == "REPRODUCIBILITY_INDEX.json":
        continue
    inventory.append(dict(receipt(path), relative_path=path.relative_to(BASE).as_posix()))
index = {"schema": "mod4.whole_moe.t2z.preparation.inventory.v1", "observed_utc": stamp,
         "scope": "WHOLE_MOE_E0_W35_H1_E2_E3_GATE_SOURCE_CONTRACT_ADAPTER_UPSTREAM_BINDING_CPU_STUB_ONLY",
         "training_ready": False, "archive_status": "LOCAL_ONLY_PENDING_ROOT_UNIQUE_TRIAL_MAIN_TAG_PEELED",
         "files": inventory, "external_source_receipts": facts["small_local_input_receipts"],
         "self_hash_note": "root archive manifest must hash this index; index excludes itself",
         "cache_exclusion": "__pycache__ interpreter caches only; all actual source/report failures retained"}
index_path = BASE / "reports/REPRODUCIBILITY_INDEX.json"
index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"source_facts": str(fact_path), "indexed_files": len(inventory), "index": str(index_path)}))
