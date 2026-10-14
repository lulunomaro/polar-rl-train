"""Compile the new source and persist an unadmitted template/work order only."""
from pathlib import Path
import ast
import hashlib
import json
import time

B = Path(__file__).resolve().parent
P = B / 'payload_v1'; R = B / 'reports'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
template = P / 'BODYFRAME_TARGET_CPU_TEMPLATE_NOT_ADMITTED.json'
work = B / 'NEXT_BODYFRAME_ACTUAL_TARGET_CPU_NATIVE_FULLRESTORE_WORK_ORDER.json'
assert not template.exists() and not work.exists()
one = R / 'BODYFRAME_WHOLE20K_RESET_COMMAND_SAVE_CHAIN_CPU_ACTUAL.json'
two = R / 'BODYFRAME_TWO_STAGE_OLD_RESTORE_FIRST_SAVE_RESUME_COMPOSITION_CPU_ACTUAL.json'
assert json.loads(one.read_bytes())['passed_CPU_reset_command_checkpoint_component'] is True
assert json.loads(two.read_bytes())['passed_CPU_restore_save_resume_composition'] is True
compiled = {}
for p in P.glob('*.py'):
    compile(p.read_bytes(), str(p), 'exec'); compiled[p.name] = sha(p)
worker_ast = ast.parse((P / 'bodyframe_native_worker_v1.py').read_bytes())
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('learn', 'update', 'backward') for n in ast.walk(worker_ast))
source = 'e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
value = dict(scope_profile='E1_WAVE50_balanced_birth_bodyframe_runtime_v1', num_envs=20000,
    initial_whole20k_source_SHA=source, actual_source_SHA=source, source_path='UNMATERIALIZED',
    actual_target_root='UNMATERIALIZED', reinitialize_left_head=False, new_geometry=False,
    new_world_route_or_lifetime=False, new_entry_pose=True, new_BODY_direction_identity=True,
    new_RNG_draws=False, live_heading_position_correction=False, CPU_fixture_only=False,
    approved_GPU=False, actual_target_CPU_source_bound=False,
    actual_resource_and_original_budget_admitted=False, actual_unique_GPU_lease_held=False,
    actual_parent_pid=None, sourcefreeze_SHA='', sourcefreeze_relative_path='UNMATERIALIZED',
    mode='native144_0PPO', PPO_updates_authorized=0)
template.write_text(json.dumps(value, indent=2), encoding='utf8')
steps = [
    'Root alone reads actual 210 original source/root/PID/locks/canonical/resources. No old task or completed GPU re-run; no budget transaction for CPU/native0PPO.',
    'Materialize one independent durable Linux target with old original522 runtime/assets bytes exact, all new owned bodyframe files and original typed13 schema; full20k e3 source only. No CPU fixture checkpoint can be a source.',
    'Actually run target CPU107/99/all195 source disk/storage and strict source/metadata/sourcefreeze guards. CPU template is never promoted by flipping booleans; create a separately measured manifest.',
    'Unique original two-fcntl lease and a bounded own native0PPO parent, with actual RAM/GPU/durable admission and original solver buffers/parameters. Native worker refuses PPO and all unadmitted templates.',
    'Actual native getter+xyzw heading and setter witnesses, full25200-point own raycast placement, old13 source restore before the new body14 declaration, selected resets/sourceepisode+1, raw/contactCOMhardware/query/health and full own save must be independently reviewed after parent/child exit and two locks free.',
    'Only after native own save/source freeze/actual exit can a distinct fullrestore120 zeroPPO case resume the new bodyframe state. Confirm orientation alternates at its one new birth, source fullactorcriticstdAdam/allD0D7/privateCPUCUDA exact, no initializer repeat and no extra reset.',
    'Then prepare the distinct first <=300s load-learn-save-exit/save25/15s guardian learning parent from actual own0PPO source. Original canonical only, pending localWindows costs kept separate. No same-left-axis third blind duration, no70.',
    'After own final closeout and full traces, 3060 original fourcase behavior review with original1N/200mm/15s/query/signedcircle and full failure prefixes; max2 new-axis learning blocks then full audit.'
]
work.write_text(json.dumps(dict(epoch=time.time(), current_stage='S3/E1_WAVE/G1 50mm bodyframe integration CPU prepared',
    actual_CPU_component=True, actual_CPU_first_and_same_scope_restore_composition=True,
    real_13_CUDA_restores_and_native_ABI_not_yet_run=True,
    new_native_worker_compiled_only=True, actual_target_or_GPU_or_PPO_admitted=False,
    no_new_training_or_canonical_write=True, no_new_S4_learning=True,
    required_next_actions=steps, no_new_human_permission_invented=True,
    frozen_source_e3=source, CPU_fixture_files_forbidden_for_production=True,
    original_v1_source_and_errors_preserved=True,
    references=[dict(path=str(x), bytes=x.stat().st_size, sha256=sha(x)) for x in (one, two)],
    prepared_sourcefreeze=compiled, new_native_CPU_template_SHA=sha(template), Git_pending=True), ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(dict(compiled_new_sources=len(compiled), native_template_always_unadmitted=True,
                      no_learner_in_prepared_native_worker=True, real_target_GPU_pending=True)))
