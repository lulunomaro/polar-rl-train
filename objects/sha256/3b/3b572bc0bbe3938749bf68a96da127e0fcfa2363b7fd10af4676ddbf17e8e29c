import ast
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "files"
for name in ("mod4_curriculum.py", "repair_step.py", "skills_isaac.py", "mod4_task.py",
             "train_mod4_ppo.py", "eval_episodes_mod4.py", "aggregate_acceptance.py"):
    ast.parse((root / name).read_text(encoding="utf8"), filename=name)

skills = (root / "skills_isaac.py").read_text(encoding="utf8")
assert "is_fly.float() * gate * air" in skills
assert "(landed_real & in_place).float()" in skills
assert "(reached_land & in_place).float()" in skills
assert "_mod4_jump_windows" in skills

curriculum = (root / "mod4_curriculum.py").read_text(encoding="utf8")
assert curriculum.index("_mod4_live_route_stats") < curriculum.index(
    'RM_ROUTE_CURRICULUM", "0"')

train = (root / "train_mod4_ppo.py").read_text(encoding="utf8")
assert '"robot_usd": str(mod4_task.USD_PATH)' in train
assert "_pk_dir = log_dir" in train

evaluation = (root / "eval_episodes_mod4.py").read_text(encoding="utf8")
assert "closure_post_grace_max_m" in evaluation
assert "prev_delta_valid" in evaluation

print("PASS_STATIC_FOLLOWUP")
