"""Prepare an isolated candidate. Does not start PPO, stop processes or own a ledger."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

OLD = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
ROOT = Path('/home/egde/rl_candidates/MOD4_fps_turn_candidate_20261003')
HERE = Path(__file__).resolve().parent
ROOT.mkdir(exist_ok=True)
assert not (ROOT/'reports/CANDIDATE_PREPARED.json').exists(), 'Inspect existing deployment; do not overwrite'
assert not (ROOT/'TRAINING_BUDGET_10H.json').exists(), 'No candidate budget copy allowed'
for directory in ('isaac', 'train'):
    shutil.copytree(OLD/directory, ROOT/directory,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.log', 'logs'), dirs_exist_ok=True)
code = ROOT/'isaac/mod4'
reports = ROOT/'reports'; reports.mkdir(exist_ok=True)
for name in ('turn_commands.py', 'turn_probe.py'):
    shutil.copy2(HERE/name, code/name)
patches = {
    'mod4_task.py': [("            configure(self)\n        # Explicit straight-speed phase:",
                     "            configure(self)\n        elif os.environ.get('RM_SPIN_STAGE') == 'body_turn_v1':\n            from turn_commands import configure\n            configure(self)\n        # Explicit straight-speed phase:")],
    'mod4_env.py': [("            if os.environ.get('RM_GYRO_CURRICULUM','1') == '0' and os.environ.get('RM_SPIN_STAGE') != 'pure_yaw_v1'",
                    "            if os.environ.get('RM_SPIN_STAGE') == 'body_turn_v1':\n                from turn_commands import audit as audit_turn\n                audit['turn_command_audit'] = audit_turn(self)\n            if os.environ.get('RM_GYRO_CURRICULUM','1') == '0' and os.environ.get('RM_SPIN_STAGE') not in ('pure_yaw_v1','body_turn_v1')")]
}
diff = {}
for name, changes in patches.items():
    path = code/name; original = path.read_text(); changed = original
    for old, new in changes:
        assert changed.count(old) == 1, 'Ambiguous patch '+name
        changed = changed.replace(old, new)
    ast.parse(changed)
    (reports/(name+'.original')).write_text(original)
    path.write_text(changed)
    diff[name] = {'before_sha256': hashlib.sha256(original.encode()).hexdigest(),
                  'after_sha256': hashlib.sha256(changed.encode()).hexdigest(),
                  'changes': 'Only explicit command configure/audit dispatch for new isolated stage'}
cfg = json.loads((code/'env.json').read_text())
cfg.update(RM_SPIN_STAGE='body_turn_v1', RM_SPIN_MAX_RAD_S='4.0', RM_TURN_FRACTION='.15',
           RM_TURN_SPEED_MAX='.6', RM_TURN_YAW_MAX='.8', RM_SIM2REAL_SENSOR_PROFILE='off')
cfg.pop('RM_RESCUE_DEADLINE', None)
(code/'env.json').write_text(json.dumps(cfg, indent=2))
unchanged = {}
for name in ('scut_flat_rescue.py','reset_bank.json','mild_dr.py','contact_capture.py','contact_geometry.py',
             'spin_commands.py','skills_isaac.py','actuator_clip_diagnostics.py'):
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(code/name) == digest(OLD/'isaac/mod4'/name)
    unchanged[name] = digest(code/name)
evidence = {'prepared_epoch': time.time(), 'old_root': str(OLD), 'candidate_root': str(ROOT),
            'stage': 'candidate_only_no_PPO_no_handover', 'patches': diff,
            'unchanged_sha256': unchanged, 'only_added_task': 'low-speed body arcs',
            'fractions': {'stand': .1, 'straight': .45, 'pure_spin': .3, 'arc': .15},
            'body_arc_vx_abs_range': [.15,.6], 'body_arc_yaw_abs_range': [.2,.8],
            'reference_mature_spin_cap': 4., 'production_cap_unchanged': True,
            'canonical_budget_not_touched': True, 'world_directed_spin_motion_implemented': False}
(reports/'CANDIDATE_PREPARED.json').write_text(json.dumps(evidence, indent=2))
print(json.dumps(evidence))
