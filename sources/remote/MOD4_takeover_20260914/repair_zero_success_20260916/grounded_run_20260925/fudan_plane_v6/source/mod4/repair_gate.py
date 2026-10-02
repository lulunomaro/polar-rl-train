"""Fail-closed acceptance/retention gate for immutable episode evaluation reports."""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path


def load_report(path):
    d = json.loads(Path(path).read_text(encoding="utf8"))
    if d.get("schema") != "mod4_episode_eval_v1" or d.get("status") != "ROLLOUT_COMPLETE":
        raise ValueError("requires complete pre-reset episode evaluation, not legacy env flags")
    encoded = json.dumps(d["protocol"], sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(encoded).hexdigest() != d.get("protocol_sha256"):
        raise ValueError("evaluation protocol digest mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", d.get("checkpoint_sha256", "")):
        raise ValueError("missing checkpoint fingerprint")
    for key, limit in (("closure_max_m", .002), ("mimic_max_rad", .01)):
        if not math.isfinite(float(d[key])) or not 0 <= float(d[key]) <= limit:
            raise ValueError("invalid or failed physical guard: " + key)
    if int(d.get("steps_completed", 0)) < int(d["protocol"]["max_episode_length"]):
        raise ValueError("evaluation shorter than one full episode horizon")
    # Rebuild counts from episode records. A caller cannot forge high bucket rates
    # accidentally by retaining the old per-environment denominator.
    rows = d.get("episodes")
    if not isinstance(rows, list) or not rows:
        raise ValueError("no completed episodes")
    seen = set()
    for r in rows:
        key = (r["env_id"], r["episode_id"])
        if key in seen:
            raise ValueError("duplicate episode in report")
        seen.add(key)
        if r["kind"] not in d["route_kinds"]:
            raise ValueError("episode route kind missing from buckets")
        if not (r["terminated"] or r["truncated"]):
            raise ValueError("unfinished trial in success denominator")
        expected = bool(r["goal_seen"]) and not bool(r["terminated"])
        if bool(r["success"]) != expected:
            raise ValueError("safety failure incorrectly counted as success")
    for kind, bucket in d["route_kinds"].items():
        selected = [r for r in rows if r["kind"] == kind]
        n, wins = len(selected), sum(bool(r["success"]) for r in selected)
        if bucket.get("episodes") != n or bucket.get("successes") != wins:
            raise ValueError("episode denominator/count mismatch: " + kind)
        rate = bucket.get("complete_rate")
        if n and (rate is None or not math.isfinite(float(rate)) or abs(rate-wins/n)>1e-9):
            raise ValueError("invalid success rate: " + kind)
    return d


def suite(paths, kinds, min_seeds=3, min_episodes=20):
    docs = [load_report(p) for p in paths]
    if len(docs) < min_seeds or len({d["seed"] for d in docs}) != len(docs):
        raise ValueError("insufficient independent seeds or duplicate seeds")
    if len({d["protocol_sha256"] for d in docs}) != 1:
        raise ValueError("evaluation protocols differ")
    if len({d["checkpoint_sha256"] for d in docs}) != 1:
        raise ValueError("suite mixes different policy checkpoints")
    result = {}
    for kind in kinds:
        rows = [r for d in docs for r in d["episodes"] if r["kind"] == kind]
        if any(d["route_kinds"].get(kind, {}).get("episodes", 0) == 0 for d in docs):
            raise ValueError("a seed is missing completed trials: " + kind)
        if len(rows) < min_episodes:
            raise ValueError("insufficient completed episodes: " + kind)
        wins = sum(bool(r["success"]) for r in rows)
        rate = wins / len(rows)
        # Wilson interval is reported as uncertainty; configured bars use raw rate.
        n, z = len(rows), 1.95996398454
        center = (rate+z*z/(2*n))/(1+z*z/n)
        half = z*math.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/(1+z*z/n)
        result[kind] = {"episodes": n, "success_rate": rate,
                        "wilson_95": [center-half, center+half],
                        "underpass_rate": sum(bool(r["underpass_seen"]) for r in rows)/n,
                        "roof_hits": sum(bool(r["terms"].get("tunnel_roof_hit")) for r in rows)}
    return docs, result


def gate(candidate, baseline, kinds, bar=.6, max_drop=.1, min_seeds=3, min_episodes=20):
    if not kinds or len(set(kinds)) != len(kinds):
        raise ValueError("explicit unique route kinds required")
    if not all(math.isfinite(x) and 0 <= x <= 1 for x in (bar, max_drop)):
        raise ValueError("threshold must be finite in [0,1]")
    if min_seeds < 3 or min_episodes < 20:
        raise ValueError("cannot weaken the minimum evidence contract")
    new, summary = suite(candidate, kinds, min_seeds, min_episodes)
    old, previous = suite(baseline, kinds, min_seeds, min_episodes)
    if new[0]["protocol_sha256"] != old[0]["protocol_sha256"]:
        raise ValueError("baseline and candidate must run under the same repaired evaluation protocol")
    if {d["seed"] for d in old} != {d["seed"] for d in new}:
        raise ValueError("baseline/candidate seed sets differ")
    fails = []
    for kind, value in summary.items():
        before = previous[kind]["success_rate"]
        current = value["success_rate"]
        if current < bar:
            fails.append(f"{kind}: {current:.3f} below bar {bar:.3f}")
        if current < before - max_drop:
            fails.append(f"{kind}: regression {before:.3f}->{current:.3f}")
        if kind == "tunnel_cross":
            if value["underpass_rate"] < .8 or value["roof_hits"]:
                fails.append("tunnel entry/roof-contact gate failed")
            # Full articulated envelope and worst-case clearance are a separate mandatory
            # physical validation. The supplied evaluator intentionally cannot certify it.
            fails.append("tunnel physical clearance is NOT certified by the episode evaluator; "
                         "complete the independent envelope/traction acceptance in TASK_LIST.md")
    return {"status": "FAIL" if fails else "PASS", "failures": fails,
            "candidate": summary, "baseline": previous}


def smoke(log, required_iterations):
    if required_iterations < 1:
        raise ValueError("required iterations must be positive")
    text = Path(log).read_text(encoding="utf8", errors="replace")
    found = re.findall(r"Learning iteration\s+(\d+)/(\d+)", text)
    if not found or max(int(i)+1 for i, _ in found) < required_iterations:
        raise ValueError("smoke did not complete the required iterations")
    if re.search(r"Traceback|out of memory|device-side assert|\b(?:nan|inf)\b", text, re.I):
        raise ValueError("runtime/numerical error in smoke log")
    for name, limit in (("closure_err_session_max_m", .002), ("mimic_err_session_max_rad", .01)):
        values = re.findall(re.escape(name)+r":\s*([\d.eE+-]+)", text)
        if not values or any(not math.isfinite(float(v)) or not 0 <= float(v) <= limit for v in values):
            raise ValueError("missing/failed smoke guard: " + name)
    return {"status": "PASS_SMOKE_ONLY", "required_iterations": required_iterations}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", nargs="+")
    ap.add_argument("--baseline", nargs="+")
    ap.add_argument("--kinds", default="run,ramp_up,step_up,rough_cross,slope_spin")
    ap.add_argument("--bar", type=float, default=.6)
    ap.add_argument("--max-drop", type=float, default=.1)
    ap.add_argument("--smoke-log")
    ap.add_argument("--required-iterations", type=int, default=250)
    args = ap.parse_args()
    try:
        if args.smoke_log:
            result = smoke(args.smoke_log, args.required_iterations)
        else:
            if not args.candidate or not args.baseline:
                raise ValueError("explicit candidate AND baseline reports required; no auto-baseline")
            result = gate(args.candidate, args.baseline, args.kinds.split(","), args.bar, args.max_drop)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 1 if result["status"] == "FAIL" else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status":"FAIL_EVIDENCE", "error":str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
