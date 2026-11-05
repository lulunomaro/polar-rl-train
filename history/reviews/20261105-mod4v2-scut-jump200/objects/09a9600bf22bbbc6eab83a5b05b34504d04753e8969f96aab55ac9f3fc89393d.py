"""One necessary CPU diagnosis of the returned final60 before full continuation."""
from pathlib import Path
import hashlib, io, json, pickle, time, types
import torch

N = Path(__file__).resolve().parent
A = N/'continuation_final60_1h'; R = A/'reports'
read = lambda p: json.loads(p.read_bytes())
target = R/'FINAL148_LEARNER_DIAGNOSIS.json'
assert not target.exists()
returned = read(R/'POSTROUND_FULL_RETURNED.json')['files']
expected = returned['production/FINAL.json']['checkpoint']
model = A/'models/model_final.pt'; raw = model.read_bytes()
assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['SHA']
class CompatUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith('numpy._core'): module = module.replace('numpy._core', 'numpy.core', 1)
        return super().find_class(module, name)
compat = types.ModuleType('numpy_rng_compat_pickle')
compat.Unpickler, compat.load = CompatUnpickler, pickle.load
with (R/'FINAL148_LEARNER_DIAGNOSIS_ONCE.json').open('x', encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(), checkpoint=expected, model_reads=1,
                   purpose='Verify complete learned state before authorized continuation',
                   for_archive=False, physics=0), stream, indent=2)
saved = torch.load(io.BytesIO(raw), map_location='cpu', weights_only=False, pickle_module=compat)
del raw
required = ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', 'learning_rate',
    'components', 'command_rng', 'command_fields', 'physical_rng', 'physical_episode',
    'motor_episode_gain', 'cpu_rng', 'cuda_rng', 'python_rng', 'numpy_rng',
    'source_reward_state', 'source_reward_dicts', 'source_global_counters', 'target_interface')
assert all(k in saved for k in required)
assert saved['format'] == 'MOD4V2_SCUT_HW300N60_FULL_V1'
assert saved['profile'] == 'jump200' and saved['iter'] == 148 and saved['num_envs'] == 20000
assert saved['actor_dim'] == 35 and saved['critic_dim'] == 78
optimizer = saved['optimizer_state_dict']['state']
steps = [int(value['step']) for value in optimizer.values()]
assert len(optimizer) == 17 and min(steps) == max(steps) == 2960
nonfinite = []
def scan(value, path=''):
    if torch.is_tensor(value):
        mask = ~torch.isfinite(value)
        if bool(mask.any()):
            nonfinite.append(dict(path=path, shape=list(value.shape), count=int(mask.sum()),
                nan=int(torch.isnan(value).sum()), posinf=int(torch.isposinf(value).sum()),
                neginf=int(torch.isneginf(value).sum())))
        return 1
    if isinstance(value, dict): return sum(scan(v, path+'/'+str(k)) for k, v in value.items())
    if isinstance(value, (list, tuple)): return sum(scan(v, path+'/'+str(k)) for k, v in enumerate(value))
    return 0
fields = scan(saved)
assert not any(row['path'].split('/')[1] in
    ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict') for row in nonfinite)
go = returned['GO_PRODUCTION.json']; startup = returned['production/STARTUP.json']
final = returned['production/FINAL.json']; owner = returned['OWNER_EXIT.json']
assert not owner['error'] and all(owner[k] for k in
    ('all_own_waited', 'original_cost_settled', 'original_leases_released'))
assert all(row is None for row in read(R/'POSTROUND_FULL_RETURNED.json')['exact_original_identities'].values())
report = dict(epoch=time.time(), passed=True, checkpoint=expected, model_path=str(model),
    production_model_decodes=1, new_physics=0, optimizer_operations=0,
    required_keys=list(required), tensor_fields_scanned=fields, nonfinite_fields=nonfinite,
    actor_critic_Adam_finite=True, iteration=saved['iter'], Adam_entries=len(optimizer),
    Adam_min=min(steps), Adam_max=max(steps), learning_rate=saved['learning_rate'],
    STD=saved['actor_state_dict']['distribution.std_param'].tolist(),
    components=list(saved['components']), global_counters=saved['source_global_counters'],
    complete_learning_and_DR_RNG_queue_schema_present=True,
    fresh_constructor_nominal_preserved=startup['D0_D7']['new_constructor_nominal_caches_preserved'],
    timings=dict(startup_seconds=startup['epoch']-go['learning_started_epoch'],
        startup_to_final_seconds=final['epoch']-startup['epoch'],
        GO_to_final_seconds=final['epoch']-go['learning_started_epoch'],
        samples_per_PPO_update=20000*24, PPO_updates=88, onpolicy_samples=42240000,
        epochs_per_update=5, minibatches_per_epoch=4, Adam_steps=1760,
        per_environment_physics_steps=16896, aggregate_environment_physics_steps=337920000),
    final_native_skill_review_pending=True,
    original_failed_evaluation_preserved=True)
with target.open('x', encoding='utf8') as stream: json.dump(report, stream, indent=2)
print(json.dumps({k: report[k] for k in ['passed', 'iteration', 'Adam_entries', 'Adam_min',
    'learning_rate', 'STD', 'global_counters', 'nonfinite_fields', 'timings']}))
