"""Prepare dynamic bookkeeping only; live imported old supervisor is unchanged."""
import ast
import hashlib
import json
import shutil
import time
from pathlib import Path

ROOT = Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
CODE = ROOT/'isaac/mod4'
BACKUP = ROOT/'reports/budget_extension20h_runtime_before'
BACKUP.mkdir(exist_ok=True)
record = {}
for name in ('supervise_native_floor.py', 'supervise_mild_trial.py'):
    path = CODE/name
    text = path.read_text()
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    if 'dynamic_authorized_budget_v1' in text:
        record[name] = {'already_prepared_sha256': before}
        continue
    shutil.copy2(path, BACKUP/name)
    if name == 'supervise_native_floor.py':
        old = "    assert b['authorized_training_seconds'] == 36000 and b['checkpoint_sha256'] == EXPECTED_SOURCE"
        assert text.count(old) == 1
        text = text.replace('STATE = {}', 'STATE = {}\n# dynamic_authorized_budget_v1\nfrom budget_authority import validate_budget')
        text = text.replace(old, "    validate_budget(b)\n    assert b['checkpoint_sha256'] == EXPECTED_SOURCE")
        text = text.replace('max(0., 36000-charged)', "max(0., float(b['authorized_training_seconds'])-charged)")
        text = text.replace('authorized_training_seconds=36000,', "authorized_training_seconds=b['authorized_training_seconds'],")
        text = text.replace("36000-float(budget_state().get('charged_training_seconds',0))",
                            "float(budget_state()['authorized_training_seconds'])-float(budget_state().get('charged_training_seconds',0))")
        text = text.replace("36000-float(b.get('charged_training_seconds',0))",
                            "float(b['authorized_training_seconds'])-float(b.get('charged_training_seconds',0))")
    else:
        text = text.replace('LOCKS = []', 'LOCKS = []\n# dynamic_authorized_budget_v1')
        text = text.replace("max(0., 36000-b['charged_training_seconds'])",
                            "max(0., float(b['authorized_training_seconds'])-b['charged_training_seconds'])")
        text = text.replace("36000-float(b['charged_training_seconds'])",
                            "float(b['authorized_training_seconds'])-float(b['charged_training_seconds'])")
        text = text.replace("budget_scope='Same 36000 seconds: all PPO processes including preflight; isolated frozen evaluation pause excluded'",
                            "budget_scope='Canonical explicit effective-time budget: all PPO including preflight; frozen evaluation while no trainer excluded'")
        marker = "        num_envs=count,steps_per_env=24,active_log=str(log),resume_checkpoint=base.checkpoint(ck),"
        assert text.count(marker) == 1
        text = text.replace(marker, marker+"\n        authorized_training_seconds=b['authorized_training_seconds'],budget_seconds=b['authorized_training_seconds'],")
    ast.parse(text)
    # Numeric ten-hour ceilings must no longer occur in executable statements.
    assert not any(isinstance(node, ast.Constant) and node.value == 36000 for node in ast.walk(ast.parse(text)))
    temp = path.with_suffix('.py.partial');temp.write_text(text);temp.replace(path)
    record[name] = {'before_sha256': before, 'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
for name in ('budget_authority.py', 'supervise_budget30h.py'):
    src = Path(__file__).with_name(name)
    ast.parse(src.read_text());shutil.copy2(src, CODE/name)
    record[name] = {'sha256': hashlib.sha256((CODE/name).read_bytes()).hexdigest()}
(ROOT/'reports/BUDGET_RUNTIME_PREPARED_20261001.json').write_text(json.dumps(
    {'created_epoch': time.time(), 'files': record, 'physics_reward_ppo_changed': False,
     'budget_changed_yet': False, 'live_supervisor_hot_reloaded': False}, indent=2))
print(json.dumps(record))

