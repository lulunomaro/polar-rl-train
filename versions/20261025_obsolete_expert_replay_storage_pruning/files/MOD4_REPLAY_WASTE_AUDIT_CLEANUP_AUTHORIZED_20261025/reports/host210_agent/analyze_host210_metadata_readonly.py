"""Local metadata-only analysis; no remote, binaries, hashing, or mutations."""
import json
from collections import defaultdict
from pathlib import Path

S = Path(__file__).resolve().parent.parent
O = Path(__file__).resolve().parent
groups = defaultdict(lambda: {"files": 0, "bytes": 0, "allocated_bytes": 0, "kinds": defaultdict(int)})
rows = []
with (S / "HOST210_ALL_OWNED_PROJECT_FILE_METADATA.jsonl").open(encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        rel = r["relative"].split("/")
        first = rel[0]
        if not first.startswith(("MOD4", "H1step", "H125", "T3", "T2policy", "C275", "S4", "E3")):
            continue
        rows.append(r)
        group = r["root"] + "/" + first
        g = groups[group]
        g["files"] += 1
        g["bytes"] += r["bytes"]
        g["allocated_bytes"] += r["allocated_bytes"]
        g["kinds"][r["kind"]] += r["bytes"]
out = {"metadata_source": str(S / "HOST210_ALL_OWNED_PROJECT_FILE_METADATA.jsonl"),
       "scope": "Exact top-level MOD4/H1step/H125/T3/T2policy/C275/S4/E3 namespaces only; unrelated data excluded.",
       "rows": len(rows), "groups": [{"path": k, **v} for k,v in sorted(groups.items(), key=lambda kv: -kv[1]["bytes"])]}
(O / "PROJECT_NAMESPACE_GROUPS_ACTUAL.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
with (O / "PROJECT_NAMESPACE_FILE_METADATA_ACTUAL.jsonl").open("w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("project_rows", len(rows), "groups", len(groups))
for g in out["groups"][:70]:
    print(json.dumps(g, ensure_ascii=False))
print("BIG_REPLAY_FILES")
for r in sorted((r for r in rows if r["kind"] == "array_or_replay_candidate_only"), key=lambda r: -r["bytes"])[:45]:
    print(json.dumps(r, ensure_ascii=False))
