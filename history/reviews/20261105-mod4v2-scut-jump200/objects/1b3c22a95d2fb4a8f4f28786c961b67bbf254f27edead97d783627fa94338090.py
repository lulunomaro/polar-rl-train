"""One complete learner diagnosis plus all80 saved-trajectory numeric review."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import pickle
import re
import time
import types
import numpy as np
import torch

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
args = parser.parse_args()
A = args.root.resolve()
R = A/'reports'
read = lambda path: json.loads(Path(path).read_bytes())
returned = read(R/'POSTROUND_FULL_RETURNED.json')
f = returned['files']
final = f['production/FINAL.json']
expected = final['checkpoint']
assert not (R/'FUDAN_COMPLETE_LEARNER_AND_ALL80.json').exists()
assert f['OWNER_EXIT.json']['all_own_waited'] and not f['OWNER_EXIT.json']['error']
assert not any(returned['exact_original_identities'].values())
model = A/'models/model_final.pt'
raw = model.read_bytes()
assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['SHA']
with (R/'FUDAN_LEARNER_DIAGNOSIS_ONCE.json').open('x', encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(), checkpoint=expected, model_decodes=1, physics=0), stream, indent=2)
class Compat(pickle.Unpickler):
    def find_class(self, module, name):
        return super().find_class(module.replace('numpy._core', 'numpy.core'), name)
compat = types.ModuleType('numpy_rng_compat_pickle')
compat.Unpickler, compat.load = Compat, pickle.load
saved = torch.load(io.BytesIO(raw), map_location='cpu', weights_only=False, pickle_module=compat)
assert saved['iter'] == expected['iteration'] and saved['reward_family'] == 'FUDAN_JUMP'
assert saved['num_envs'] == 20000 and saved['actor_dim'] == 35 and saved['critic_dim'] == 78
optimizer = saved['optimizer_state_dict']['state']
steps = [int(row['step']) for row in optimizer.values()]
assert len(steps) == 17 and min(steps) == max(steps) == saved['iter']*20
for key in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict'):
    def finite(value):
        if torch.is_tensor(value):
            return bool(torch.isfinite(value).all())
        if isinstance(value, dict):
            return all(finite(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return all(finite(v) for v in value)
        return True
    assert finite(saved[key]), key
components = ('_sensor_mild', '_feedback_delay_mild', '_physics_action_delay', '_spring_pressure', '_gas_damping', '_chassis_com', '_explicit_pd')
assert set(components) == set(saved['components'])
for key in ('command_rng', 'command_fields', 'physical_rng', 'physical_episode', 'motor_episode_gain', 'cpu_rng', 'cuda_rng', 'python_rng', 'numpy_rng', 'source_reward_state', 'source_reward_dicts', 'source_global_counters'):
    assert key in saved
fudan_fields = [k for k in saved['source_reward_state'] if k.startswith('fudan_')]
assert len(fudan_fields) == 6
logs = read(R/'DIRECT_COMPLETE_LOGS.json')['logs']
errors = {name:[line for line in row['text'].splitlines() if any(term in line.lower() for term in ('[error]', 'traceback (most recent call last)', 'cooking failure', 'patch buffer overflow', 'outofmemoryerror', 'dropped pair'))] for name,row in logs.items()}
assert not any(errors.values())
timings = {}
for label in ('Collection time', 'Learning time', 'Steps per second'):
    values = [float(v) for v in re.findall(re.escape(label)+r':\s*([0-9.]+)', logs['WORKER.log']['text'])]
    timings[label] = dict(count=len(values), mean=float(np.mean(values)) if values else None, last=values[-1] if values else None)
result = f['evaluation/RESULT.json']
rows = f['evaluation/ALL80.json']['first_episodes']
curves = f['evaluation/CONTROL_CURVES.json']['curves']
assert result['source_SHA'] == expected['SHA'] and result['optimizer_operations'] == 0 and len(rows) == 80
assert result['saved_pose_quaternion_order'] == 'wxyz'
with np.load(A/'evaluation/actual400hz.npz') as tick:
    mask = tick['active']
    local = tick['root_pos'] - np.asarray(result['environment_origins'])[None]
    numeric = dict(callbacks=len(mask), active_samples=int(mask.sum()),
        ground_flight_envs=int(((tick['flight_id']>0)&mask).any(0).sum()),
        upward_flight_envs=int((tick['upward_flight']&mask).any(0).sum()),
        wholeclear_envs=int((tick['wholeclear']&mask).any(0).sum()),
        landed_top_envs=int((tick['landed_top']&mask).any(0).sum()),
        success_envs=int((tick['strict']&mask).any(0).sum()),
        actual_top_force_max=float(tick['top_force'][mask].max()),
        root_x=[float(local[...,0][mask].min()),float(local[...,0][mask].max())],
        root_z=[float(local[...,2][mask].min()),float(local[...,2][mask].max())],
        vz=[float(tick['root_velocity'][...,2][mask].min()),float(tick['root_velocity'][...,2][mask].max())])
arr = lambda key:np.asarray([row[key] for row in curves])
active = arr('active')
numeric['done_counts'] = {key:sum(bool(row[key]) for row in rows) for key in ('terminated','time_out','closure_reset','mimic_reset','numerical_reset','observation_outlier')}
numeric['control_range'] = [min(row['controls'] for row in rows),max(row['controls'] for row in rows)]
numeric['commands'] = dict(vx=np.unique(arr('command')[...,0][active]).tolist(), height=np.unique(arr('command_height')[active]).tolist())
numeric['action_absmax'] = float(np.abs(arr('applied_action')[active]).max())
targets = arr('joint_target')
delta = targets[...,[0,2]]-targets[...,[1,3]]
numeric['mechanical_delta'] = [float(delta[active].min()),float(delta[active].max())]
assert numeric['action_absmax'] <= 6 and numeric['mechanical_delta'][0] >= -1.0863195404360622-1.e-6 and numeric['mechanical_delta'][1] <= .49192233306644084+1.e-6
for key in ('fudan_leg_length','fudan_leg_theta','fudan_was_in_flight','fudan_base_air_time'):
    # Existing evaluator persists these in each actual terminal snapshot;
    # its control curves predate Fudan and have no such columns.
    value = np.asarray([row[key] for row in rows])
    numeric[key] = dict(min=float(value.min()), max=float(value.max()), mean=float(value.mean()),
                        evidence='all80_actual_terminal_snapshots')
numeric['fudan_reward_active_mean'] = {key:float(np.mean([row['weighted_reward_active_mean'][key] for row in curves]))
    for key in curves[0]['weighted_reward_active_mean']}
report = dict(epoch=time.time(), passed=True, checkpoint=expected, production_model_decodes=1,
    actor_critic_Adam_finite=True, Adam_entries=len(steps), Adam_min=min(steps), Adam_max=max(steps),
    learning_rate=saved['learning_rate'], STD=saved['actor_state_dict']['distribution.std_param'].tolist(),
    components=list(saved['components']), fudan_state_fields=fudan_fields,
    counters=saved['source_global_counters'], complete_DR_RNG_queue_state=True,
    new_constructor_nominal_preserved=f['production/STARTUP.json']['D0_D7']['new_constructor_nominal_caches_preserved'],
    full_log_errors=errors, timings=timings, PPO_updates=final['PPO_updates'], samples=final['PPO_updates']*480000,
    numeric=numeric, actual_pose_visual_review_pending=True, new_physics=0, optimizer_operations=0)
with (R/'FUDAN_COMPLETE_LEARNER_AND_ALL80.json').open('x', encoding='utf8') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps({k:report[k] for k in ('checkpoint','PPO_updates','timings','numeric')}))
