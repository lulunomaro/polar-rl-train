r"""Offline test for the per-route acceptance buckets (audit item 9).

No Isaac, no GPU, no torch: run it with the repo's plain venv

    .\.venv\Scripts\python.exe isaac\mod4\test_eval_buckets.py

What it pins down (the audit found all three of these broken or unverifiable):
  1. the per-kind counts and rates are arithmetically right;
  2. a run filtered to `run,jump_in_place` produces NO tunnel bucket -- the old evaluator
     could label a tunnel route "run" because the spawn was filtered but the ids were not;
  3. the label follows the ROUTE ID, never the position in the list.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from route_isaac import bucket_by_route  # noqa: E402

ROUTES_JSON = (HERE.parents[1] / "incoming" / "rmuc2026_field_20260911" /
               "rmuc2026_training" / "data" / "routes.json")


def kinds_table():
    if ROUTES_JSON.is_file():
        routes = json.loads(ROUTES_JSON.read_text(encoding="utf8"))
        return [r["kind"] for r in routes]
    return ["run", "jump_in_place", "ramp_up", "ramp_down", "slope_spin", "rough_cross",
            "rough_cross", "fly_jump", "fly_jump", "step_up", "step_down", "step_up",
            "ramp_up", "tunnel_cross", "tunnel_cross"]


def check_all_routes(kinds):
    ids = list(range(len(kinds)))
    done = [True] * len(ids)
    prog = [1.5] * len(ids)
    failed = [False] * len(ids)
    b = bucket_by_route(kinds, ids, done, prog, failed)
    assert sum(v["envs"] for v in b.values()) == len(ids), b
    for kind, rec in b.items():
        assert rec["envs"] == kinds.count(kind), (kind, rec, kinds.count(kind))
        assert rec["complete_rate"] == 1.0, (kind, rec)
        assert abs(rec["progress_sum"] - 1.5 * rec["envs"]) < 1e-6, (kind, rec)
        assert rec["failed"] == 0, (kind, rec)
    print("[buckets] all-routes OK: %s" % {k: v["envs"] for k, v in b.items()})


def check_filtered(kinds):
    """RM_ROUTE_KINDS=run,jump_in_place: the allowed ids are 0 and 1 in the shipped table."""
    keep = [i for i, k in enumerate(kinds) if k in ("run", "jump_in_place")]
    ids = [keep[i % len(keep)] for i in range(8)]
    b = bucket_by_route(kinds, ids, [False] * 8, [0.25] * 8, [False] * 8)
    assert set(b) == {"run", "jump_in_place"}, b
    assert "tunnel_cross" not in b and "fly_jump" not in b, b
    assert sum(v["envs"] for v in b.values()) == 8, b
    assert all(v["complete_rate"] == 0.0 for v in b.values()), b
    assert all(abs(v["progress_sum"] - 0.25 * v["envs"]) < 1e-6 for v in b.values()), b
    print("[buckets] filtered OK: %s" % {k: v["envs"] for k, v in b.items()})


def check_label_follows_id(kinds):
    """Three envs on route id 2 must report route 2's kind, whatever the list order is."""
    ids = [2, 2, 2]
    b = bucket_by_route(kinds, ids, [True, False, False], [2.0, 0.0, -1.0], [True, False, False])
    assert list(b) == [kinds[2]], b
    rec = b[kinds[2]]
    assert rec["envs"] == 3 and rec["completed"] == 1 and rec["failed"] == 1, b
    assert rec["complete_rate"] == 0.333, b
    assert abs(rec["progress_sum"] - 1.0) < 1e-6, b
    print("[buckets] id/label OK: %s -> %s" % (ids, b))


def main() -> None:
    kinds = kinds_table()
    assert len(kinds) == 15, "expected the 15-route table, got %d" % len(kinds)
    check_all_routes(kinds)
    check_filtered(kinds)
    check_label_follows_id(kinds)
    print("[buckets] ALL CHECKS PASSED (source=%s)"
          % ("routes.json" if ROUTES_JSON.is_file() else "synthetic table"))


if __name__ == "__main__":
    main()
