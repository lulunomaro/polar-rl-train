"""Patch only replay diagnostics; never edit the live physics/training code."""
import ast
import hashlib
import json
import shutil
import time
from pathlib import Path

ROOT = Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
CODE = ROOT / 'isaac/mod4'
path = CODE / 'validate_speed.py'
source = path.read_text()
original_sha = hashlib.sha256(path.read_bytes()).hexdigest()
if 'actuator_local_order_v1' in source:
    print(json.dumps({'already_applied': True, 'validate_sha256': original_sha}))
    raise SystemExit(0)
assert original_sha == '527aba878a5ce5fb3c47cf63e6992dd710106c82bd5b1513e865aa7200605103'


def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)


replace('from contact_geometry import ControlGeometry',
        'from contact_geometry import ControlGeometry\n    from actuator_clip_diagnostics import rating_clipped')
replace("'wheel_rating_clip_fraction','leg_rating_clip_fraction']}",
        "'wheel_rating_clip_fraction','leg_rating_clip_fraction','wheel_rating_clip_fraction_unmapped_shadow','leg_rating_clip_fraction_unmapped_shadow']}")
replace("        rated_wc=(computed[:,wheelids]*robot.actuators['wheels'].episode_scale-applied[:,wheelids]).abs()>.1\n"
        "        rated_lc=(computed[:,legids]*robot.actuators['legs'].episode_scale-applied[:,legids]).abs()>.1\n"
        "        values.update(wheel_rating_clip_fraction=rated_wc.float().mean(1),\n"
        "                      leg_rating_clip_fraction=rated_lc.float().mean(1))",
        "        unmapped_wc=(computed[:,wheelids]*robot.actuators['wheels'].episode_scale-applied[:,wheelids]).abs()>.1\n"
        "        unmapped_lc=(computed[:,legids]*robot.actuators['legs'].episode_scale-applied[:,legids]).abs()>.1\n"
        "        rated_wc=rating_clipped(robot.actuators['wheels'])\n"
        "        rated_lc=rating_clipped(robot.actuators['legs'])\n"
        "        values.update(wheel_rating_clip_fraction=rated_wc.float().mean(1),\n"
        "                      leg_rating_clip_fraction=rated_lc.float().mean(1),\n"
        "                      wheel_rating_clip_fraction_unmapped_shadow=unmapped_wc.float().mean(1),\n"
        "                      leg_rating_clip_fraction_unmapped_shadow=unmapped_lc.float().mean(1))")
replace("    result['gain_compensated_clipping_semantics']='requested PD torque times episode output gain minus final applied torque; 10ms snapshots, not substep peaks. Raw computed-minus-applied and original speed_safety_pass are retained separately.'",
        "    result['gain_compensated_clipping_semantics']='actuator_local_order_v1: raw requested PD torque times episode and step gains minus final applied torque, all in the actuator joint order; includes pre/post gain hardware envelope clipping. 10ms snapshots, not substep peaks. Raw and unmapped gain shadow fields are retained.'\n"
        "    result['rating_diagnostic_version']='actuator_local_order_v1'\n"
        "    result['actuator_joint_order']={k:list(robot.actuators[k].joint_names) for k in ('legs','wheels')}\n"
        "    result['policy_joint_order']={'legs':task.LEG_ORDER,'wheels':task.WHEEL_ORDER}")
ast.parse(source)
backup = ROOT / 'reports/validate_speed_before_rating_order_fix_20261001.py'
assert not backup.exists()
shutil.copy2(path, backup)
helper_source = Path(__file__).with_name('actuator_clip_diagnostics.py')
shutil.copy2(helper_source, CODE / helper_source.name)
temp = path.with_suffix('.py.partial')
temp.write_text(source)
temp.replace(path)
receipt = {'created_epoch': time.time(), 'scope': 'replay diagnostics only; physics/reward/optimizer unchanged',
           'previous_validate_sha256': original_sha,
           'new_validate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'helper_sha256': hashlib.sha256((CODE/helper_source.name).read_bytes()).hexdigest(),
           'reason': 'Policy leg order is crank/hip; articulation and actuator order may be hip/crank. Never multiply policy-ordered torque by actuator-local gains without a mapping.',
           'legacy_admission_gate_changed': False, 'previous_reports_rewritten': False,
           'applied_torque_changed': False, 'requires_next_scheduled_replay_readback': True}
(ROOT/'reports/RATING_DIAGNOSTIC_ORDER_FIX_20261001.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt))

