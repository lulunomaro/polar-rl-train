"""CPU-only frozen-plan checks.  Run before Kit/GPU startup."""
import ast, hashlib, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "isaac" / "mod4"
ASSET = Path(os.environ["RM_MOD4_USD"])
BASELINE = Path(os.environ["TAKEOVER_BASELINE"])

for p in (ASSET, ASSET.parent / "import_contract.json", BASELINE):
    if not p.is_file():
        raise FileNotFoundError(p)
for p in CODE.glob("*.py"):
    ast.parse(p.read_text(encoding="utf8"), filename=str(p))

sys_path_added = str(CODE)
import sys
sys.path.insert(0, sys_path_added)
from repair_contracts import require_explicit_training_env
require_explicit_training_env(os.environ)

source = (CODE / "mod4_task.py").read_text(encoding="utf8")
if source.count("tunnel_height = RewTerm") != 1:
    raise RuntimeError("duplicate/missing tunnel_height reward")
routes = json.loads((ROOT / "incoming" / "rmuc2026_field_20260911" /
                     "rmuc2026_training" / "data" / "routes.json").read_text(encoding="utf8"))
required = {"run", "ramp_up", "ramp_down", "step_up", "step_down", "rough_cross",
            "slope_spin", "fly_jump", "jump_in_place", "tunnel_cross"}
found = {r["kind"] for r in routes}
if required - found:
    raise RuntimeError("missing route kinds: " + str(sorted(required - found)))

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report = {
    "status": "PASS", "asset": str(ASSET), "asset_sha256": sha(ASSET),
    "baseline": str(BASELINE), "baseline_sha256": sha(BASELINE),
    "route_kinds": sorted(found),
    "source_sha256": {p.name: sha(p) for p in sorted(CODE.glob("*.py"))},
    "explicit_rm_env": {k: v for k, v in sorted(os.environ.items()) if k.startswith("RM_")},
}
(ROOT / "takeover" / "PRECHECK.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps(report, ensure_ascii=False, indent=2))
