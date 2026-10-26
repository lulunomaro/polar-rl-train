"""Derive finite method-test input only from an already returned small79c array."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np

J = Path(__file__).resolve().parent
T = J.parent
source = T / 'H1_STEP270_CLOSED79C_SAVED_REPLAY_AFTER_V8_20261026/SELECTED_RECORDED_MOTION.npz'
expected = '0bc4e9116d697c9d5dec9d40d54d4296c27fd3ced11dfa54f52201e95ffe7c65'
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
with np.load(source, allow_pickle=False) as z:
    root = z['root13'].copy()
    root[..., :3] -= z['env_origins'][None]
    # Native recorded XYZW -> upstream's explicit WXYZ representation.
    root[..., 3:7] = root[..., [6, 3, 4, 5]]
    state = np.concatenate((root, z['q30'], z['joint_velocity']), axis=-1)
    context = np.concatenate((z['history5ms'].reshape(48, 91, -1), z['applied_torque'], z['public_request'][..., None]), axis=-1).astype('float32')
    same = z['same_episode_transition'] & (z['episode'][1:] == z['episode'][:-1])
    valid = same & ~z['done'][:-1].astype(bool) & ~z['done'][1:].astype(bool)
    ti, ei = np.nonzero(valid)
    # Complete rows are post-step. Row(t+1)'s action produced state(t)->state(t+1).
    values = dict(s=state[ti, ei], s1=state[ti+1, ei], a=z['executed6'][ti+1, ei], xi=context[ti, ei],
                  env_id=z['env_ids'][ei], control_from=z['control_rows'][ti], control_to=z['control_rows'][ti+1])
    values['held_out_env'] = values['env_id'] % 5 == 0
assert values['s'].shape[1] == 73 and values['xi'].shape[1] == 49 and values['a'].shape[1] == 6
assert np.all(values['control_to'] - values['control_from'] == 1)
assert np.all(np.abs(values['a']) <= 6)
for key in ('s', 's1', 'a', 'xi'):
    assert np.isfinite(values[key]).all()
assert values['held_out_env'].any() and (~values['held_out_env']).any()
(J / 'artifacts').mkdir()
p = J / 'artifacts/mod4_native30_action6_saved_transition_test.npz'
with p.open('xb') as f:
    np.savez_compressed(f, **values)
report = dict(epoch=time.time(), source_small_derived_path=str(source), source_bytes=source.stat().st_size,
    source_SHA=expected, path=str(p), bytes=p.stat().st_size, SHA=hashlib.sha256(p.read_bytes()).hexdigest(),
    transitions=len(ti), train_transitions=int((~values['held_out_env']).sum()), held_out_transitions=int(values['held_out_env'].sum()),
    source_scope='Closed79c selected91 trajectories,48 controls, not a representative or expert demonstration set',
    state_joint_count=30, action_dim=6, action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],
    quaternion='native XYZW converted to upstream WXYZ', prediction_dt_s=.01,
    action_alignment='post-state row t to t+1 uses executed6 at t+1', reset_crossing_transitions_excluded=True,
    held_out_split='env_id modulo5, no frame-wise random split',
    context='49 known current-state features:18 contact-history+30 applied torque+public request',
    limitations=['DR parameters and complete actuator delay state are not reconstructed','No new policy rollout, physics, G1 motion data or production checkpoint input','Offline prediction accuracy does not establish closed-loop dynamics validity or 270mm success'])
with (J / 'reports/ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json').open('x', encoding='utf8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps({k:report[k] for k in ('transitions','train_transitions','held_out_transitions','bytes','SHA')}))
