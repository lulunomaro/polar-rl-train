"""CPU-testable contracts for this MOD4 task; no Isaac imports."""
from __future__ import annotations

import math
import json
from pathlib import Path
import torch

POLICY_TERMS = (
    ("commands", 3), ("height_command", 1), ("base_ang_vel", 3),
    ("projected_gravity", 3), ("leg_pos", 4), ("wheel_pos_slots", 2),
    ("leg_vel", 4), ("wheel_vel", 2), ("last_action", 6), ("mode_onehot", 7),
)


def assert_checkpoint_semantics(path, manifest_path=""):
    """Do not load an old sequence policy under corrected observation semantics."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if any(k.startswith("encoder.") for k in ck.get("actor_state_dict", {})):
        manifest = Path(manifest_path) if manifest_path else Path(path).parent / "run_manifest.json"
        data = json.loads(manifest.read_text(encoding="utf8")) if manifest.is_file() else {}
        if data.get("observation_semantics") != "mod4_term_major_latest_gather_v1":
            raise ValueError("sequence checkpoint semantics unknown/legacy; use the plain 35-D baseline"
                             " or evaluate legacy and corrected policies separately")


def latest_term_indices(history: int, frame_dim: int = 35):
    """Isaac concatenates [term0 history, term1 history, ...], not whole frames."""
    if history < 1 or frame_dim != sum(d for _, d in POLICY_TERMS):
        raise ValueError("unsupported policy observation contract")
    out, offset = [], 0
    for _, dim in POLICY_TERMS:
        out.extend(range(offset + (history - 1) * dim, offset + history * dim))
        offset += history * dim
    return torch.tensor(out, dtype=torch.long)


def validate_warmstart(actor, critic, checkpoint, allow_new_encoder: bool):
    """Reject missing policy/critic weights BEFORE any runner state is changed."""
    for label, target in (("actor", actor), ("critic", critic)):
        source = checkpoint.get(label + "_state_dict")
        if not isinstance(source, dict) or not source:
            raise ValueError(f"missing {label}_state_dict")
        missing, extra = set(target) - set(source), set(source) - set(target)
        allowed = set()
        enc = {k for k in target if k.startswith("encoder.")}
        if label == "actor" and allow_new_encoder and enc and not (enc & source.keys()):
            allowed = enc
        if extra or missing - allowed:
            raise ValueError(f"{label} incompatible: missing={sorted(missing)}, extra={sorted(extra)}")
        for key in source:
            value = source[key]
            if value.shape != target[key].shape or not bool(torch.isfinite(value).all()):
                raise ValueError(f"{label}/{key}: wrong shape or nonfinite weight")
    return sorted(set(actor) - set(checkpoint["actor_state_dict"]))


def episode_counts(route_ids, route_names, kind_names, done, success, failed):
    """One attempt per END of an episode, mapped route index -> semantic kind."""
    table = torch.tensor([kind_names.index(k) for k in route_names],
                         dtype=torch.long, device=route_ids.device)
    # Do not clamp route indices into the last kind (the previous implementation did).
    mapped = table[route_ids.long()]
    ids = mapped[done.bool()]
    won = (success.bool() & ~failed.bool())[done.bool()].to(torch.float32)
    attempts = torch.bincount(ids, minlength=len(kind_names)).to(torch.float32)
    successes = torch.bincount(ids, weights=won, minlength=len(kind_names))
    return attempts, successes


class EpisodeLedger:
    """Consume pre-reset terminal snapshots; never pool successes across resets."""
    def __init__(self, num_envs, route_names):
        self.num_envs = num_envs
        self.route_names = list(route_names)
        self.records = []
        self.seen = set()
        self.last_episode = {}

    def consume(self, batch):
        # Batch contains only completed episodes and immutable scalar/list values.
        for row in batch:
            env_id, ep = int(row["env_id"]), int(row["episode_id"])
            if not 0 <= env_id < self.num_envs or ep < 0:
                raise ValueError("invalid episode identity")
            key = (env_id, ep)
            if key in self.seen:
                raise ValueError(f"duplicate terminal episode: {key}")
            if env_id in self.last_episode and ep != self.last_episode[env_id] + 1:
                raise ValueError("episode gap or out-of-order terminal snapshot")
            rid = int(row["route_id"])
            if not 0 <= rid < len(self.route_names):
                raise ValueError("invalid route id")
            if not (row["terminated"] or row["truncated"]):
                raise ValueError("unfinished episode submitted as terminal")
            for key_num in ("duration_s", "spin_deg", "peak_rise_m", "max_air_time_s"):
                if not math.isfinite(float(row[key_num])):
                    raise ValueError(f"nonfinite {key_num}")
            rec = dict(row)
            rec["kind"] = self.route_names[rid]
            # Safety failure wins even when a goal is reached on the same step.
            rec["success"] = bool(row["goal_seen"]) and not bool(row["terminated"])
            self.records.append(rec)
            self.seen.add((env_id, ep))
            self.last_episode[env_id] = ep

    def buckets(self):
        result = {}
        for kind in sorted(set(self.route_names)):
            rows = [r for r in self.records if r["kind"] == kind]
            n = len(rows)
            wins = sum(r["success"] for r in rows)
            rec = {"episodes": n, "successes": wins,
                   "complete_rate": wins / n if n else None,
                   "terminated": sum(bool(r["terminated"]) for r in rows),
                   "timeouts": sum(bool(r["truncated"]) for r in rows)}
            for field in ("underpass_seen", "launched", "air_after_launch", "landed"):
                count = sum(bool(r[field]) for r in rows)
                rec[field] = count
                rec[field + "_rate"] = count / n if n else None
            rec["roof_hit_terminations"] = sum(bool(r["terms"].get("tunnel_roof_hit")) for r in rows)
            rec["failure_reasons"] = {
                name: sum(bool(r["terms"].get(name)) for r in rows)
                for name in sorted({name for r in rows for name in r["terms"]})
            }
            result[kind] = rec
        return result


class PerKindProgress:
    """Poll live episode state without counting an episode or success twice.

    Training owns one active episode per environment.  Polling is asynchronous, so a
    success flag can remain true for several polls and different environments commonly
    have the same episode number.  The old implementation stored one episode number per
    *kind*, which inflated both counters.  This ledger keys state by environment id and
    latches success for that environment/episode exactly once.
    """

    def __init__(self):
        self.env_state = {}
        self.counts = {}

    def update(self, route_ids, episode_ids, successes, route_names):
        if not (len(route_ids) == len(episode_ids) == len(successes)):
            raise ValueError("per-kind vectors have different lengths")
        for env_id, (rid, episode, success) in enumerate(
                zip(route_ids, episode_ids, successes)):
            rid, episode = int(rid), int(episode)
            if not 0 <= rid < len(route_names):
                raise ValueError("invalid live route id")
            kind = str(route_names[rid])
            key = (episode, kind)
            prev = self.env_state.get(env_id)
            rec = self.counts.setdefault(kind, {"att": 0, "suc": 0})
            if prev is None or prev[0] != key:
                rec["att"] += 1
                prev = [key, False]
                self.env_state[env_id] = prev
            if bool(success) and not prev[1]:
                rec["suc"] += 1
                prev[1] = True
        return self.counts


REQUIRED_TRAINING_ENV = (
    "RM_MOD4_USD", "RM_MOD4_MAP", "RM_MOD4_TERRAIN",
    "RM_LEG_KP", "RM_LEG_KD", "RM_LEG_KI", "RM_LEG_KI_CLIP",
    "RM_LEG_ACTION_SCALE", "RM_CRANK_ACTION_SCALE",
    "RM_DR_OFF", "RM_ROUTE_KINDS", "RM_ROUTE_WEIGHTS",
    "RM_SEQ_ENCODER", "RM_SEQ_HISTORY", "RM_SEQ_LATENT",
    "RM_SEQ_ENCODER_HIDDEN", "RM_INIT_STD",
)


def require_explicit_training_env(environ):
    """Fail before Isaac starts when the deployment/control contract is incomplete."""
    missing = [key for key in REQUIRED_TRAINING_ENV if key not in environ]
    if missing:
        raise ValueError("incomplete training contract; missing: " + ", ".join(missing))
    map_terrain = (environ["RM_MOD4_MAP"], environ["RM_MOD4_TERRAIN"])
    if map_terrain not in (("rmuc2026", "field"), ("fudan_plane", "flat")):
        raise ValueError("unsupported explicit map/terrain contract: %r" % (map_terrain,))
    if map_terrain != ("fudan_plane", "flat") and float(environ["RM_CRANK_ACTION_SCALE"]) < 0.60:
        raise ValueError("crank action range cannot reach the verified crouch pose")
    if int(environ["RM_SEQ_HISTORY"]) < 1:
        raise ValueError("sequence history must be positive even when encoder is disabled")
