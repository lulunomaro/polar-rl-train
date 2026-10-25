"""Whole-MoE CPU manifest bridge. No policy, physics, model or remote execution."""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path

EXPERTS = ("E0", "W35", "H1", "E2", "E3")
EXPERT_PERIOD_NS = {"E0": 10_000_000, "W35": 10_000_000, "H1": 10_000_000,
                    "E2": 20_000_000, "E3": 20_000_000}
BACKENDS = {"PhysX": 2_500_000, "MuJoCo": 500_000}
FRAME_NS = 50_000_000
SCHEMA = "mod4.moe.t2z.raw.v1"


class DataError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def need(condition, code, message):
    if not condition:
        raise DataError(code, message)


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def finite(value, count, code):
    need(isinstance(value, list) and len(value) == count and
         all(type(x) in (int, float) and math.isfinite(x) for x in value), code, f"{count} finite values required")


def validate(raw, plan, require_real=True):
    need(raw.get("schema") == SCHEMA, "SCHEMA", SCHEMA)
    need(type(raw.get("synthetic")) is bool, "SYNTHETIC_FLAG", "explicit flag required")
    if require_real:
        need(not raw["synthetic"], "SYNTHETIC_NOT_TRAINING", "fixtures cannot become actual data")
    need(bool(raw.get("episodes")), "DATASET_MISSING", "native whole-MoE RGB/action/routing data absent")
    backend = raw["backend"]
    need(backend["name"] in BACKENDS and backend["physics_dt_ns"] == BACKENDS[backend["name"]],
         "BACKEND_CLOCK", "PhysX2.5ms and MuJoCo0.5ms are distinct domains")
    need(backend["video_period_ns"] == FRAME_NS and backend["dispatch_period_ns"] == 10_000_000,
         "SCHEDULER_CLOCK", "20fps /100Hz dispatcher contract")
    need(backend["expert_period_ns"] == EXPERT_PERIOD_NS, "EXPERT_CLOCK", "preserve100/50Hz schedules")
    need(set(raw["expert_pool"]) == set(EXPERTS), "EXPERT_POOL", "all five source identities required")
    for source in raw["expert_pool"].values():
        need(isinstance(source.get("sha256"), str) and len(source["sha256"]) == 64, "SOURCE_SHA", "checkpoint SHA missing")
    ticks_per_frame = FRAME_NS // backend["physics_dt_ns"]
    episodes = {}
    for ep in raw["episodes"]:
        eid = ep["episode_id"]
        need(eid not in episodes, "DUPLICATE_EPISODE", eid)
        episodes[eid] = ep
        need(ep.get("source_episode_uuid") and ep.get("physical_config_id") and ep.get("collector_sha256"),
             "PROVENANCE", eid)
        need(set(ep["task_tags"]) <= set(EXPERTS) | {"SWITCH_MIX"}, "TASK_TAG", eid)
        frames = ep.get("frames", [])
        need(len(frames) in (5, 41), "FRAME_COUNT", "5-frame synthetic smoke or41-frame native geometry")
        if require_real:
            need(len(frames) == 41, "REAL_FRAME_COUNT", "primary41-native-frame clip required")
        for i, frame in enumerate(frames):
            tick = frame["tick"]
            need(type(tick) is int and tick >= 0 and frame["time_ns"] == tick * backend["physics_dt_ns"],
                 "FRAME_TIME", eid)
            need(frame["origin"] == ("SYNTHETIC_ONLY" if raw["synthetic"] else "NATIVE_SIM_RGB"), "RGB_ORIGIN", eid)
            need(frame.get("uri") and len(frame.get("sha256", "")) == 64, "RGB_MISSING", eid)
            if i:
                need(tick - frames[i - 1]["tick"] == ticks_per_frame, "FRAME_GAP", eid)
        start, end = frames[0]["tick"], frames[-1]["tick"]
        need(not any(start <= t <= end for t in ep.get("reset_ticks", [])), "RESET_CROSSING", eid)
        steps = ep.get("applied_steps", [])
        need(len(steps) == end - start, "APPLIED_COVERAGE", eid)
        for tick, step in zip(range(start, end), steps):
            need(step["tick"] == tick and step["expert"] in EXPERTS, "APPLIED_CLOCK", eid)
            finite(step["target6"], 6, "APPLIED_TARGET")
            finite(step["gate_weights5"], 5, "GATE_WEIGHTS")
            need(all(w >= 0 for w in step["gate_weights5"]) and abs(sum(step["gate_weights5"]) - 1) < 1e-6,
                 "GATE_WEIGHTS", "record weights separately; never infer weighted action averaging")
        events = ep.get("policy_events", [])
        dispatch_ticks = 10_000_000 // backend["physics_dt_ns"]
        need([x["tick"] for x in events] == list(range(start, end, dispatch_ticks)), "POLICY_EVENT_COVERAGE", eid)
        for event in events:
            need(event["selected_expert"] in EXPERTS, "EXPERT_ACTIVATION", eid)
            need(set(event["inference_ticks"]) == set(EXPERTS), "EXPERT_INFERENCE_CLOCK", eid)
            for name, when in event["inference_ticks"].items():
                need(when is None or (type(when) is int and when <= event["tick"]), "FUTURE_INFERENCE_RECEIPT", name)
            finite(event["command4"], 4, "COMMAND")
        proposal = ep.get("proposal")
        need(proposal is not None and proposal["committed_at_tick"] <= start, "PROPOSAL_MISSING", "causal command/route candidate fixed at initial decision")
        need(proposal.get("semantics") == "PRECOMMITTED_COMMAND_ROUTE", "PROPOSAL_SEMANTICS", "future actual closed-loop gate outputs are forbidden")
        rows = proposal["steps"]
        need([x["tick"] for x in rows] == list(range(start, end)), "PROPOSAL_COVERAGE", eid)
        for row in rows:
            finite(row["command4"], 4, "COMMAND")
            need(row["route"] in EXPERTS, "ROUTE_PLAN", eid)
    assignments = plan["assignments"]
    need(len(assignments) == len(episodes) and {x["episode_id"] for x in assignments} == set(episodes),
         "SPLIT_ASSIGNMENT", "one assignment per episode")
    group_split, source_role, roles = {}, {}, {}
    for a in assignments:
        ep = episodes[a["episode_id"]]
        split, role, group = a["split"], a["role"], ep["physical_config_id"]
        need(split in ("train", "validation", "test") and role in (("fit",) if split == "train" else ("support", "query")), "SPLIT_ROLE", a)
        need(group not in group_split or group_split[group] == split, "PHYSICAL_CONFIG_LEAK", group)
        group_split[group] = split
        source = ep["source_episode_uuid"]
        need(source not in source_role or source_role[source] == (split, role), "SOURCE_EPISODE_LEAK", source)
        source_role[source] = split, role
        roles.setdefault((split, group), set()).add(role)
    for (split, group), group_roles in roles.items():
        if split != "train":
            need(group_roles == {"support", "query"}, "SUPPORT_QUERY_MISSING", group)
    return raw


class SafeMoEIndex:
    """Never calls upstream metadata.py; opaque groups remain routing only."""
    def __init__(self, raw, plan, *, require_real=True):
        validate(raw, plan, require_real=require_real)
        self.raw, self.plan = copy.deepcopy(raw), copy.deepcopy(plan)
        self.episodes = {e["episode_id"]: e for e in self.raw["episodes"]}
        train_groups = sorted({self.episodes[a["episode_id"]]["physical_config_id"]
                               for a in self.plan["assignments"] if a["split"] == "train"})
        self.train_group_index = {g: i for i, g in enumerate(train_groups)}

    def rows(self, split, role):
        return [copy.deepcopy(a) for a in self.plan["assignments"] if a["split"] == split and a["role"] == role]

    def train_metadata(self):
        return [{"episode_id": a["episode_id"], "source_episode_uuid": self.episodes[a["episode_id"]]["source_episode_uuid"],
                 "dataset_split": "train", "role": "fit", "action_id": i,
                 "context_index": self.train_group_index[self.episodes[a["episode_id"]]["physical_config_id"]]}
                for i, a in enumerate(self.rows("train", "fit"))]

    def packed(self, episode_id, mode="command_route", *, for_planning=False):
        ep = self.episodes[episode_id]
        backend = self.raw["backend"]
        m = FRAME_NS // backend["physics_dt_ns"]
        if mode == "applied_diagnostic":
            need(not for_planning, "FUTURE_APPLIED_PRIVILEGE", "actual future targets/gate receipts cannot drive candidate selection")
            feature = [s["target6"] + [float(s["expert"] == e) for e in EXPERTS] + s["gate_weights5"] for s in ep["applied_steps"]]
        elif mode == "command_route":
            feature = [s["command4"] + [float(s["route"] == e) for e in EXPERTS] for s in ep["proposal"]["steps"]]
        else:
            raise DataError("MODE", mode)
        c = len(feature[0])
        action = [[[0.0] * (c + 1) for _ in range(m)]]
        action.extend([[list(v) + [1.0] for v in feature[i:i + m]] for i in range(0, len(feature), m)])
        return action

    def model_view(self, episode_id, split, role, *, mode="command_route", for_planning=False):
        need(any(a == {"episode_id": episode_id, "split": split, "role": role} for a in self.rows(split, role)), "VIEW_SCOPE", episode_id)
        ep = self.episodes[episode_id]
        result = {"sample_id": sha(ep["source_episode_uuid"]), "synthetic": self.raw["synthetic"],
                  "initial_rgb": copy.deepcopy(ep["frames"][0]),
                  "action": self.packed(episode_id, mode, for_planning=for_planning)}
        if role != "query":
            result["observed_rgb"] = copy.deepcopy(ep["frames"])
        return result


class MoETrainingDataset:
    """Upstream build_dataset-compatible dataset restricted to train/fit only."""
    def __init__(self, index, *, mode="command_route", decoder=None):
        self.index, self.mode, self.decoder = index, mode, decoder
        self.data = index.train_metadata()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        import torch
        row = self.data[item]
        view = self.index.model_view(row["episode_id"], "train", "fit", mode=self.mode)
        need(self.decoder is not None, "RGB_DECODER_MISSING", "native file-content/SHA decoder required")
        return {"video": [self.decoder(f) for f in view["observed_rgb"]],
                "action": torch.tensor([view["action"]], dtype=torch.float32, device="cpu"),
                "context_index": row["context_index"]}


def local_native_decoder(root):
    """PIL native RGB loader; verifies actual bytes/SHA and forbids URI escape."""
    root = Path(root).resolve()
    def decode(frame):
        import io
        from PIL import Image
        path = (root / frame["uri"]).resolve()
        need(path.is_relative_to(root), "RGB_PATH_ESCAPE", str(path))
        need(path.is_file(), "RGB_FILE_MISSING", str(path))
        body = path.read_bytes()
        need(hashlib.sha256(body).hexdigest() == frame["sha256"], "RGB_SHA_MISMATCH", str(path))
        image = Image.open(io.BytesIO(body))
        need(image.mode == "RGB", "RGB_MODE", "explicit native RGB encoding required")
        image.load()
        return image
    return decode
