"""Review the completed target repair window and its actual recorded episodes."""
from pathlib import Path
import hashlib
import io
import json
import pickle
import sys
import time
import types
import numpy as np
import torch

N = Path(__file__).resolve().parent
A = N/'env20000_target_axis_repair_1h_20261104'
R = A/'reports'
out = R/'ACTUAL_TARGET_AXIS_FINAL_REVIEW.json'
if out.exists():
    raise FileExistsError(out)
returned = json.loads((R/'POSTROUND_FULL_RETURNED.json').read_bytes())
f = returned['files']
rows = f['evaluation/ALL80.json']['first_episodes']
curves = f['evaluation/CONTROL_CURVES.json']['curves']
array = lambda key: np.asarray([c[key] for c in curves])
active = array('active')
actions, applied, targets = (array(k) for k in ('action', 'applied_action', 'joint_target'))
contacts, rp = (array(k) for k in ('reset_body_contact_force', 'roll_pitch_rad'))
counter, raw = (array(k) for k in ('termination_duration_counter', 'termination_raw'))
commands, height = (array(k) for k in ('command', 'effective_height'))
t = np.load(A/'evaluation/actual400hz.npz')
mask = t['active']
assert t['top_force'].shape == (3200, 80, 2)
assert len(rows) == 80 and all(row['controls']*8 == row['physics_ticks'] for row in rows)
assert all(f['OWNER_EXIT.json'][k] for k in ('all_own_waited', 'original_cost_settled', 'original_leases_released'))
assert all(v is None for v in returned['exact_original_identities'].values())
assert not t['top_force'][mask].any()
assert np.max(abs(applied[active])) <= 6
lower, upper = np.asarray([-1.2, -.5, -1.2, -.5]), np.asarray([.9, .5, .9, .5])
assert (targets[active] >= lower-1.e-6).all() and (targets[active] <= upper+1.e-6).all()
difference = targets[..., [0, 2]]-targets[..., [1, 3]]
assert (difference[active] >= -1.0843-1.e-6).all() and (difference[active] <= .85+1.e-6).all()
terminal = []
names = f['evaluation/RESULT.json']['reset_contact_body_names']
for row in rows:
    if not row['terminated']:
        continue
    eid, end = row['env'], row['controls']
    window = slice(end-20, end)
    assert (contacts[window, eid] > 1).any(-1).all()
    assert not (abs(rp[window, eid]) > np.deg2rad(40)).any()
    assert raw[window, eid].all() and counter[window, eid].tolist() == list(range(1, 21))
    terminal.append(dict(env=eid, controls=end, consecutive_contacts_over1={
        name: int((contacts[window, eid, i] > 1).sum()) for i, name in enumerate(names)},
        max_roll_pitch_deg=np.rad2deg(abs(rp[window, eid]).max(0)).tolist()))

# This single production decode diagnoses the actual learned policy and full
# learning state. It is not performed for archival, and makes no optimizer step.
class CompatUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith('numpy._core'):
            module = module.replace('numpy._core', 'numpy.core', 1)
        return super().find_class(module, name)

compat = types.ModuleType('numpy_rng_compat_pickle')
compat.Unpickler, compat.load = CompatUnpickler, pickle.load
path = A/'models/model_final.pt'
checkpoint = path.read_bytes()
expected = f['production/FINAL.json']['checkpoint']
assert len(checkpoint) == expected['bytes'] and hashlib.sha256(checkpoint).hexdigest() == expected['SHA']
saved = torch.load(io.BytesIO(checkpoint), map_location='cpu', weights_only=False, pickle_module=compat)
del checkpoint
required = ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', 'learning_rate',
            'components', 'command_rng', 'command_fields', 'physical_rng', 'physical_episode',
            'motor_episode_gain', 'cpu_rng', 'cuda_rng', 'python_rng', 'numpy_rng',
            'source_reward_state', 'source_reward_dicts', 'source_global_counters', 'target_interface')
assert all(k in saved for k in required)
assert saved['format'] == 'MOD4V1_SCUT_FULL_V4' and saved['iter'] == 59
state = saved['optimizer_state_dict']['state']
steps = [int(v['step']) for v in state.values()]
finite = all(bool(torch.isfinite(v).all()) for group in ('actor_state_dict', 'critic_state_dict')
             for v in saved[group].values() if torch.is_tensor(v))
assert finite and steps and min(steps) == max(steps) == 1180
origin = np.asarray([[(i//9)*8., (i%9)*8., 0.] for i in range(80)])
local = t['root_pos']-origin[None]
endpoints = np.arange(7, 3200, 8)
error = local[endpoints, :, 2]-height
controls = np.asarray([r['controls'] for r in rows])
report = dict(epoch=time.time(), kind='TARGET_AXIS_FINAL_NATIVE_TRAJECTORY_AND_LEARNING_REVIEW',
    final=f['production/FINAL.json'], owner_exit=f['OWNER_EXIT.json'], train_closed=f['TRAIN_CLOSED.json'],
    exact_original_identities=returned['exact_original_identities'],
    actual_samples=59*24*20000, optimizer_steps=1180,
    full_save_diagnosis=dict(path=str(path), bytes=expected['bytes'], SHA=expected['SHA'],
        production_model_decodes=1, purpose='Actual learned STD and complete learning-state diagnosis',
        keys_present=list(required), tensor_finite=finite, Adam_entries=len(state), Adam_min=min(steps), Adam_max=max(steps),
        STD=saved['actor_state_dict']['distribution.std_param'].tolist(), learning_rate=saved['learning_rate'],
        component_names=list(saved['components']), global_counters=saved['source_global_counters'],
        new_physical_constructor_nominal_preserved=f['production/STARTUP.json']['D0_D7']['new_constructor_nominal_caches_preserved']),
    independent80=dict(strict=0, wholeclear=0, leading=0, anytop=0, bothtop=0, max_top_force=0.,
        counts={k: sum(bool(r[k]) for r in rows) for k in ('terminated', 'time_out', 'observation_outlier', 'closure_reset', 'mimic_reset', 'numerical_reset')},
        cap8s_without_task_done=sum(not r['terminated'] and not r['time_out'] for r in rows),
        controls=dict(min=int(controls.min()), max=int(controls.max()), mean=float(controls.mean()), mean_seconds=float(controls.mean()*.02)),
        actual_400Hz_callbacks=3200, all80_first_episode_mask_checked=True,
        terminal_contact_paths=terminal,
        raw_action_min=actions[active].min(0).tolist(), raw_action_max=actions[active].max(0).tolist(),
        clip_fraction=(abs(actions[active])>6).mean(0).tolist(),
        target_min=targets[active].min(0).tolist(), target_max=targets[active].max(0).tolist(),
        target_upper_hit_fraction=np.isclose(targets[active], upper, atol=1.e-6).mean(0).tolist(),
        all_targets_and_CAD_difference_compliant=True,
        max_body_xy_coordinate_from_birth=float(abs(local[..., :2])[mask].max()),
        max_displacement_from_first_callback=float(np.linalg.norm(t['root_pos'][..., :2]-t['root_pos'][0, :, :2], axis=-1)[mask].max()),
        root_height_range=[float(local[..., 2][mask].min()), float(local[..., 2][mask].max())],
        height_tracking_mae=float(abs(error[active]).mean()),
        command_zero_fraction=float((np.linalg.norm(commands[active], axis=-1)<1.e-6).mean()),
        command_abs_yaw_over1_fraction=float((abs(commands[..., 2][active])>1).mean()),
        selected={str(i): dict(controls=rows[i]['controls'], seconds=rows[i]['controls']*.02,
            terminated=rows[i]['terminated']) for i in (0, 1, 40, 41)}),
    native_visual_review=dict(current_model_view_image=True, images=4, quaternion='saved wxyz',
        reports=[str(A/'evaluation'/p/'RENDER_REPORT.json') for p in ('recorded_native', 'recorded_native_late')],
        findings='Selected robots descend into the central low area. Env0 terminates1.16s and its later panels clamp. Env1/40/41 remain below the platform through8s; no edge traversal or tabletop support.'),
    decision='No unchanged270mm replay. Human now removes270mm requirement; prepare the pinned SCUT stair branch with original5-40mm steps and10cm treads, original reward/PPO, no full rough restoration.',
    optimizer_operations_in_review=0, new_physics=0)
with out.open('x', encoding='utf8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
print(json.dumps(dict(report=str(out), samples=report['actual_samples'], counts=report['independent80']['counts'],
    mean_seconds=report['independent80']['controls']['mean_seconds'], STD=report['full_save_diagnosis']['STD'],
    Adam_entries=len(state), Adam_steps=steps[0], learning_rate=saved['learning_rate'])))
