"""Save the actual116 source call chain; no runtime import/model/physics."""
from pathlib import Path
import ast
import hashlib
import json
import time

T = Path(__file__).resolve().parent
B = T / 'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/source'
D = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native120_original_closure_vs_imagined_stop_CPU_review_v1/reports'
OUT = D / 'ACTUAL116_LEARNER_CALL_CHAIN_AND_FUTURE_RETURN_SOURCE_ONLY.json'
assert not OUT.exists(), 'Source publication already exists; do not repeat'
spec = {
    'native_flat5cm_training_entry_candidate_v4_typed_producer.py': [(14, 20), (81, 88), (130, 140)],
    'native_fudan_step_bridge_v1.py': [(1, 12)],
    'native_wheel_leg_bridge_v4.py': [(55, 73)],
    'supermimic_wheel_leg_v3/contract.py': [(78, 82)],
    'supermimic_wheel_leg_v3/learner.py': [(117, 125), (290, 299), (428, 449)],
}
rows = []
for rel, ranges in spec.items():
    p = B / rel
    raw = p.read_bytes()
    txt = raw.decode('utf-8-sig')
    ast.parse(txt)
    lines = txt.splitlines()
    rows.append(dict(path=str(p), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(),
        exact_line_excerpts=[dict(first=lo, last=hi, lines=lines[lo-1:hi]) for lo, hi in ranges]))
learner = next(x for x in rows if x['path'].endswith('learner.py'))
joined = '\n'.join(s for x in learner['exact_line_excerpts'] for s in x['lines'])
for expected in ['get_supermimic_mdp(env)', 'self.mdp.soft_termination(',
                 'alive = torch.cumprod(1 - dones, 0)',
                 'objective = (discount * continuation * rewards).sum(0)',
                 'survival = alive[-1]']:
    assert expected in joined, expected
report = dict(epoch=time.time(), phase='ordinary118_source120_supplement',
    verified_actual116_entry_injects_same_task_MDP_into_learner=True,
    verified_imagined_stop_used_for_future_rewards_and_critic_survival=True,
    failure_step_current_reward_not_automatically_zeroed=True,
    source_call_chain=rows,
    no_runtime_import_checkpoint_raw_NPZ_SDK_GPU_or_physics=True,
    limits='Static source binding, not proof a particular imagined branch visited the saved physical failure state.')
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
error = D / 'LOCAL_OPTIONAL_SOURCE_LOOKUP_ERRORS_AND_CORRECT_CALL_CHAIN.json'
assert not error.exists()
error.write_text(json.dumps(dict(epoch=time.time(), kind='local_source_lookup_only',
    original_failed_guessed_paths=['supermimic_wheel_leg_v3/supermimic.py',
        'supermimic_wheel_leg_v3/algorithm.py', 'native_wheel_leg_bridge_v1.py',
        'supermimic_wheel_leg_v3/env_isaac.py', 'supermimic_wheel_leg_v3/mdp.py'],
    original_error='rg: system cannot find specified files (os error 2); one lookup command returned1.',
    corrective_method='Read actual imports and use rg --files, then inspect actual native_wheel_leg_bridge_v4.py and contract.py.',
    original_or_candidate_runtime_source_changed=False,
    no_model_raw_GPU_or_experiment_executed=True), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(passed_source_binding=True, output=str(OUT), sources=len(rows),
    runtime_actions=0), ensure_ascii=False))
