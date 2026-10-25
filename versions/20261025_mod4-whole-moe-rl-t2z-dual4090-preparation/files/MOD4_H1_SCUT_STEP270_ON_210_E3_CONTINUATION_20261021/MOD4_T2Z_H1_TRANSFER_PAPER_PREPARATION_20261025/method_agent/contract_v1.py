"""CPU-only H1 RGB/action manifest validation and lossless interval conversion.

No simulator, model loading, training, remote access, image generation or installs.
This is a proposed interchange contract, not the upstream T2-z dataset loader.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "mod4.h1.t2z.raw.v1"
PACKED_SCHEMA = "mod4.h1.t2z.packed.v1"
ACTION_ORDER = ["left_crank", "left_hip", "right_crank", "right_hip",
                "left_wheel_spin", "right_wheel_spin"]
ACTION_UNITS = ["rad"] * 4 + ["rad/s"] * 2
PHYSICS_NS = 2_500_000
FRAME_TICKS = 20
PRIVATE_KEYS = {"physical_values", "friction_mu", "mass", "pd_gains", "reward",
                "success", "contact", "state", "future_rgb", "checkpoint_path"}


class ContractError(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def require(condition, code, detail):
    if not condition:
        raise ContractError(code, detail)


def integer(value, code, name, minimum=0):
    require(type(value) is int and value >= minimum, code, name)
    return value


def finite6(value):
    require(isinstance(value, list) and len(value) == 6, "ACTION_DIM", "six named targets required")
    require(all(type(v) in (int, float) and math.isfinite(v) for v in value),
            "NONFINITE", "target6 must be finite numeric values")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def require_real_data(raw):
    require(raw.get("synthetic") is False, "SYNTHETIC_NOT_TRAINING", "synthetic fixtures cannot become training data")
    require(bool(raw.get("episodes")), "DATASET_MISSING", "no native H1 RGB/action episodes supplied")
    for ep in raw["episodes"]:
        require(bool(ep.get("frames")), "RGB_MISSING", ep.get("episode_id", "unknown episode"))
        require(all(f.get("origin") == "NATIVE_SIM_RGB" for f in ep["frames"]),
                "RGB_NOT_NATIVE", "generated/reconstructed renderings are not recorded native RGB")
        require(all(a.get("provenance") == "ARTICULATION_TARGET_READBACK" for a in ep.get("applied_actions", [])),
                "ACTION_NOT_ACTUAL", "actual applied articulation-target readback is required")


def validate_raw(raw, *, require_real=False):
    require(raw.get("schema") == SCHEMA, "SCHEMA", SCHEMA)
    require(type(raw.get("synthetic")) is bool, "SYNTHETIC_FLAG", "explicit boolean required")
    if require_real:
        require_real_data(raw)
    require(raw.get("action_order") == ACTION_ORDER and raw.get("action_units") == ACTION_UNITS,
            "ACTION_SEMANTICS", "four leg position and two wheel velocity targets in source policy order")
    require(bool(raw.get("episodes")), "DATASET_MISSING", "no episodes supplied")
    ids = set()
    seen_source_episodes = {}
    for ep in raw["episodes"]:
        eid = ep["episode_id"]
        require(eid not in ids, "EPISODE_DUPLICATE", eid)
        ids.add(eid)
        for name in ("source_episode_uuid", "physical_group_id", "simulator_run_id",
                     "physics_profile_sha256", "action_contract_sha256", "policy_checkpoint_sha256"):
            require(isinstance(ep.get(name), str) and bool(ep[name]), "PROVENANCE_MISSING", name)
        group = ep["physical_group_id"]
        source_episode = ep["source_episode_uuid"]
        require(source_episode not in seen_source_episodes or seen_source_episodes[source_episode] == group,
                "GROUP_CHANGED_WITHIN_EPISODE", source_episode)
        seen_source_episodes[source_episode] = group
        physics = ep["clock"]
        require(physics["physics_dt_ns"] == PHYSICS_NS, "PHYSICS_CLOCK", "selected 2.5ms profile")
        require(physics["control_decimation"] in (4, 8), "CONTROL_CLOCK", "H1=4; E3=8, never silently mix")
        require(physics["video_frame_period_ns"] == PHYSICS_NS * FRAME_TICKS,
                "VIDEO_CLOCK", "this v1 adapter uses native 20fps")
        frames = ep.get("frames", [])
        require(len(frames) >= 5 and len(frames) % 4 == 1, "FRAME_COUNT", "T=4k+1; no repeated-frame padding")
        expected_origin = "SYNTHETIC_ONLY" if raw["synthetic"] else "NATIVE_SIM_RGB"
        for index, frame in enumerate(frames):
            tick = integer(frame["sim_tick"], "FRAME_TICK", "nonnegative physics boundary")
            require(frame["sim_time_ns"] == tick * PHYSICS_NS, "TIME_MISMATCH", eid)
            require(frame.get("origin") == expected_origin, "RGB_ORIGIN", expected_origin)
            require(frame.get("uri") and len(frame.get("sha256", "")) == 64, "RGB_REFERENCE", "uri and SHA256 required")
            require(frame.get("channels") == "RGB" and frame.get("width", 0) > 0 and frame.get("height", 0) > 0,
                    "RGB_SHAPE", eid)
            require(frame.get("available_at_tick") == tick, "FRAME_AVAILABILITY", "v1 uses instantaneous boundary capture")
            require(frame.get("camera_calibration_sha256"), "CAMERA_PROVENANCE", eid)
            if index:
                require(tick - frames[index - 1]["sim_tick"] == FRAME_TICKS,
                        "FRAME_GAP", "exact 20 physics ticks; missing/duplicated frames rejected")
                require(frame["camera_calibration_sha256"] == frames[0]["camera_calibration_sha256"],
                        "CAMERA_CHANGED", "split the episode/capture profile first")
        start, end = frames[0]["sim_tick"], frames[-1]["sim_tick"]
        require(not any(start <= t <= end for t in ep.get("reset_ticks", [])),
                "RESET_CROSSING", "each accepted episode fragment is reset-free including decision/end boundaries")
        actions = ep.get("applied_actions", [])
        require(bool(actions), "ACTION_MISSING", eid)
        cursor = start
        for row in actions:
            lo = integer(row["start_tick"], "ACTION_TICK", "start_tick")
            hi = integer(row["end_tick"], "ACTION_TICK", "end_tick", 1)
            require(lo == cursor and hi > lo and hi <= end, "ACTION_COVERAGE", "ordered exact half-open coverage; no gaps/overlaps")
            finite6(row["target6"])
            require(row.get("provenance") == ("SYNTHETIC_ONLY" if raw["synthetic"] else "ARTICULATION_TARGET_READBACK"),
                    "ACTION_NOT_ACTUAL", "actual applied target, not sampled/clipped/requested action")
            integer(row["issued_control_step"], "ISSUE_CLOCK", "global control step")
            cursor = hi
        require(cursor == end, "ACTION_COVERAGE", "all frame intervals need actual targets")
    return raw


def pack_episode(ep, synthetic):
    """First frame is a no-action anchor; interval j-1 -> j belongs to frame j.

    Each future frame packs ordered [20,7]: six targets and one validity mask.
    Integer physics boundaries remove H1/E3 noninteger control/frame ambiguity.
    """
    frames = ep["frames"]
    rows = ep["applied_actions"]
    action_cursor = 0
    packed = [[[0.0] * 7 for _ in range(FRAME_TICKS)]]
    intervals = []
    for index in range(1, len(frames)):
        left, right = frames[index - 1]["sim_tick"], frames[index]["sim_tick"]
        ticks = []
        fragments = []
        for tick in range(left, right):
            while rows[action_cursor]["end_tick"] <= tick:
                action_cursor += 1
            row = rows[action_cursor]
            require(row["start_tick"] <= tick < row["end_tick"], "ACTION_COVERAGE", str(tick))
            ticks.append(list(row["target6"]) + [1.0])
            if not fragments or fragments[-1]["source_action_index"] != action_cursor:
                fragments.append({"source_action_index": action_cursor,
                                  "offset_start_ns": (tick - left) * PHYSICS_NS,
                                  "offset_end_ns": (tick + 1 - left) * PHYSICS_NS,
                                  "target6": list(row["target6"]),
                                  "issued_control_step": row["issued_control_step"]})
            else:
                fragments[-1]["offset_end_ns"] += PHYSICS_NS
        packed.append(ticks)
        intervals.append({"destination_frame_index": index, "start_tick": left,
                          "end_tick": right, "segments": fragments})
    return {"schema": PACKED_SCHEMA, "synthetic": synthetic,
            "sample_id": digest([ep["simulator_run_id"], ep["source_episode_uuid"],
                                 frames[0]["sim_tick"], frames[-1]["sim_tick"]]),
            "routing": {k: ep[k] for k in ("episode_id", "source_episode_uuid", "physical_group_id")},
            "clock": copy.deepcopy(ep["clock"]), "frames": copy.deepcopy(frames),
            "action_packed_t20x7": packed, "action_intervals": intervals,
            "audit_provenance": {k: ep[k] for k in ("simulator_run_id", "policy_checkpoint_sha256",
                                                     "physics_profile_sha256", "action_contract_sha256")},
            "evaluation_only": copy.deepcopy(ep.get("evaluation_only", {}))}


def validate_splits(raw, plan):
    """Held-out physical groups; support/query must be different source episodes."""
    episodes = {e["episode_id"]: e for e in raw["episodes"]}
    group_roles = {}
    seen = set()
    for item in plan["assignments"]:
        eid, split, role = item["episode_id"], item["split"], item["role"]
        require(eid in episodes and eid not in seen, "SPLIT_EPISODE", eid)
        seen.add(eid)
        require(split in ("train", "validation", "test"), "SPLIT_NAME", split)
        require(role in (("fit",) if split == "train" else ("support", "query")), "ROLE", role)
        ep = episodes[eid]
        group = ep["physical_group_id"]
        require(group not in group_roles or group_roles[group] == split,
                "PHYSICAL_GROUP_LEAK", group)
        group_roles[group] = split
    require(seen == set(episodes), "UNASSIGNED_EPISODES", "all episodes need explicit assignment")
    source_roles = {}
    frame_owner = {}
    source_splits = {}
    for item in plan["assignments"]:
        ep = episodes[item["episode_id"]]
        key = (ep["physical_group_id"], item["split"])
        source_roles.setdefault(key, {}).setdefault(item["role"], set()).add(ep["source_episode_uuid"])
        sid = ep["source_episode_uuid"]
        require(sid not in source_splits or source_splits[sid] == item["split"], "SOURCE_EPISODE_LEAK", sid)
        source_splits[sid] = item["split"]
        for frame in ep["frames"]:
            # Native RGB can be visually identical; identity is source capture, not image bytes.
            identity = (ep["simulator_run_id"], ep["source_episode_uuid"], frame["sim_tick"], frame["camera_calibration_sha256"])
            owner = (item["split"], item["role"])
            require(identity not in frame_owner or frame_owner[identity] == owner, "FRAME_LEAK", str(identity))
            frame_owner[identity] = owner
    for (group, split), roles in source_roles.items():
        if split != "train":
            require(bool(roles.get("support")) and bool(roles.get("query")), "SUPPORT_QUERY_MISSING", group)
            require(roles["support"].isdisjoint(roles["query"]), "SUPPORT_QUERY_EPISODE_LEAK", group)
    return plan


def model_view(packed, role):
    require(role in ("fit", "support", "query"), "ROLE", role)
    # Allowlist prevents hidden numeric labels/contact/future state/checkpoint/path routing leakage.
    view = {"sample_id": packed["sample_id"], "synthetic": packed["synthetic"],
            "initial_rgb": copy.deepcopy(packed["frames"][0]),
            "action_packed_t20x7": copy.deepcopy(packed["action_packed_t20x7"])}
    if role in ("fit", "support"):
        view["observed_target_rgb"] = copy.deepcopy(packed["frames"][1:])
    return view


def convert(raw, plan, *, require_real=False):
    validate_raw(raw, require_real=require_real)
    validate_splits(raw, plan)
    by_id = {e["episode_id"]: pack_episode(e, raw["synthetic"]) for e in raw["episodes"]}
    return {"schema": "mod4.h1.t2z.converted.v1", "synthetic": raw["synthetic"],
            "training_ready": False,
            "readiness_reason": "synthetic fixture" if raw["synthetic"] else "content existence/SHA, native collector, loader and pipeline integration still require independent audit",
            "records": [{"split": item["split"], "role": item["role"],
                         "routing": by_id[item["episode_id"]]["routing"],
                         "model": model_view(by_id[item["episode_id"]], item["role"]),
                         "evaluation": {"target_rgb": by_id[item["episode_id"]]["frames"][1:],
                                        "audit": by_id[item["episode_id"]]["audit_provenance"],
                                        "metrics_truth": by_id[item["episode_id"]]["evaluation_only"]},
                         "lossless_action_intervals": by_id[item["episode_id"]]["action_intervals"]}
                        for item in plan["assignments"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("split_plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--require-real", action="store_true", help="reject all synthetic/missing-native datasets; does not grant training readiness")
    args = parser.parse_args()
    require(not args.output.exists(), "OUTPUT_EXISTS", "append a new result; never overwrite an earlier attempt")
    raw = json.loads(args.manifest.read_text(encoding="utf-8"))
    plan = json.loads(args.split_plan.read_text(encoding="utf-8"))
    result = convert(raw, plan, require_real=args.require_real)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "CONVERTED_NOT_TRAINING_READY", "synthetic": result["synthetic"],
                      "records": len(result["records"]), "output": str(args.output)}))


if __name__ == "__main__":
    main()
