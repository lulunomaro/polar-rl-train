"""One-shot SOURCE-ONLY additions; v2 and the frozen raw35 module stay byte-identical."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = ('resume_runtime_contracts_v2.py', 'worker_supermimic_bptt_resume_candidate_v2.py',
           'supermimic_original_owner_resume_candidate_v2.py',
           'supermimic_original_owner_shared_resume_candidate_v2.py',
           'ctx_reward_full_resume_candidate_v2.py')
before = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in SOURCES}
frozen = ROOT / 'source_command_review_v1/command_tracking_torch_candidate_v1.py'
frozen_sha = 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223'
assert hashlib.sha256(frozen.read_bytes()).hexdigest() == frozen_sha


def swap(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old), count)
    return text.replace(old, new)


def swap_function(text, name, replacement):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno - 1]) + replacement.strip() + '\n' + ''.join(lines[node.end_lineno:])


helper = (HERE / 'resume_runtime_contracts_v2.py').read_text(encoding='utf-8')
helper = swap(helper, "FINAL_KIND = 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V2'", "FINAL_KIND = 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'")
helper = swap(helper, "LIFECYCLE_KIND = 'MOD4V1_SUPERMIMIC_ORIGINAL_CLOSE_COMPLETE_V2'", "LIFECYCLE_KIND = 'MOD4V1_SUPERMIMIC_ORIGINAL_CLOSE_COMPLETE_V3'")
helper = swap(helper, "BASELINE_ACTOR_VIEW = 'baseline_fullctx_v1'", "BASELINE_ACTOR_VIEW = 'baseline_fullctx_v1'\nRAW35_ACTOR_VIEW = 'raw35_legacy_held_aux_v1'")
helper = swap(helper, "def require(value, message):", '''def validate_worker_variant(task):
    resume = task.get('resume_bptt') is not None
    view = task.get('actor_view', BASELINE_ACTOR_VIEW)
    default = ('A1_RAW35_RESUME' if resume else 'A1_RAW35_FRESH') if view == RAW35_ACTOR_VIEW else ('A0_FULLCTX_RESUME' if resume else 'A0_FULLCTX_FRESH')
    variant = task.get('algorithm_variant', default)
    choices = {
        'A0_FULLCTX_FRESH': (BASELINE_ACTOR_VIEW, 'a0_fullctx_legacy_v1', False),
        'A0_FULLCTX_RESUME': (BASELINE_ACTOR_VIEW, 'a0_fullctx_legacy_v1', True),
        'A1_RAW35_FRESH': (RAW35_ACTOR_VIEW, 'a1_raw35_legacy_v1', False),
        'A1_RAW35_RESUME': (RAW35_ACTOR_VIEW, 'a1_raw35_legacy_v1', True),
    }
    require(variant in choices, 'explicit A0/A1 algorithm variant differs')
    expected_view, family, expected_resume = choices[variant]
    require(view == expected_view and resume == expected_resume, 'actor view/resume descriptor does not match selected variant')
    if resume:
        require(task['resume_bptt'].get('actor_view') == view, 'cross-view weights/Adam/history/counter migration is not admitted')
    return dict(algorithm_variant=variant, actor_view=view, algorithm_family=family,
                actor_observation_dim=35 if view == RAW35_ACTOR_VIEW else None,
                command_tracking_fixed=False, sensor_projection_exact=False,
                bound_anchor_reward_changes=0)


def require(value, message):''')
helper = swap(helper, "require(value.get('actor_view') == BASELINE_ACTOR_VIEW, 'raw35 migration is a separate fresh-zero branch')", "require(value.get('actor_view') in (BASELINE_ACTOR_VIEW, RAW35_ACTOR_VIEW), 'known actor view is required')\n    if value['actor_view'] == RAW35_ACTOR_VIEW:\n        require(value.get('algorithm_family') == 'a1_raw35_legacy_v1', 'A1 resumes require an own same-variant full checkpoint')")
helper = swap_function(helper, 'bind_future_task_extensions', '''def bind_future_task_extensions(task, entry):
    """Pure future metadata; all original owner admission/accounting stays outside."""
    output = dict(task)
    output['actor_view'] = entry.get('actor_view', BASELINE_ACTOR_VIEW)
    if entry.get('algorithm_variant') is not None:
        output['algorithm_variant'] = entry['algorithm_variant']
    if entry.get('resume_bptt') is not None:
        output['resume_bptt'] = validate_resume_descriptor(entry['resume_bptt'])
    else:
        output.pop('resume_bptt', None)
    output.update(validate_worker_variant(output))
    if entry.get('bridge_adapter') is not None:
        output['bridge_adapter'] = validate_bridge_adapter_descriptor(entry['bridge_adapter'])
    return output''')
helper = swap(helper, "require(task.get('actor_view') == BASELINE_ACTOR_VIEW, 'baseline actor view is required')", "variant = validate_worker_variant(task)\n    view = variant['actor_view']\n    require(descriptor['actor_view'] == view, 'descriptor/worker actor view differs')")
helper = swap(helper, "require(contract.get('obs_dim') == 79 + contract.get('context_dim', -1000), 'original invariant+action+full-context observation required')", "expected_obs = 35 if view == RAW35_ACTOR_VIEW else 79 + contract.get('context_dim', -1000)\n    require(contract.get('obs_dim') == expected_obs, 'same-view full observation/norm/optimizer dimensions required')\n    if view == RAW35_ACTOR_VIEW:\n        require(payload.get('actor_view') == view and payload.get('algorithm_family') == variant['algorithm_family'], 'A1 requires embedded same-view/family full-checkpoint provenance')\n    else:\n        require(payload.get('actor_view', view) == view and payload.get('algorithm_family', variant['algorithm_family']) == variant['algorithm_family'], 'A0 checkpoint actor family differs')")
helper = swap(helper, "'WORKER_LIFECYCLE_COMPLETE_V2.json'", "'WORKER_LIFECYCLE_COMPLETE_V3.json'")
helper = swap(helper, "require(final.get('run_id') == run_id, 'FINAL run identity differs')", "require(final.get('run_id') == run_id, 'FINAL run identity differs')\n            selected = validate_worker_variant(entry)\n            require(final.get('actor_view') == selected['actor_view'] and final.get('algorithm_family') == selected['algorithm_family'], 'FINAL A0/A1 actor family differs')")

worker = (HERE / 'worker_supermimic_bptt_resume_candidate_v2.py').read_text(encoding='utf-8')
worker = swap(worker, 'from resume_runtime_contracts_v2 import (FINAL_KIND,LIFECYCLE_KIND,BASELINE_ACTOR_VIEW,', 'from resume_runtime_contracts_v3 import (FINAL_KIND,LIFECYCLE_KIND,BASELINE_ACTOR_VIEW,RAW35_ACTOR_VIEW,validate_worker_variant,')
worker = swap(worker, " assert task.get('actor_view',BASELINE_ACTOR_VIEW)==BASELINE_ACTOR_VIEW,'raw35 requires a separate fresh-zero branch'\n task['actor_view']=BASELINE_ACTOR_VIEW", " variant=validate_worker_variant(task);task.update(variant);actor_view=variant['actor_view'];algorithm_family=variant['algorithm_family']")
needle = 'actor_snapshot={key:value.detach().clone() for key,value in actor.state_dict().items()}'
replacement = '''if actor_view==RAW35_ACTOR_VIEW:
   source=J/'worker_sources/command_tracking_torch_candidate_v1.py';assert H(source)=='bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223';assert any(f['relative']=='worker_sources/command_tracking_torch_candidate_v1.py'and f['SHA']=='bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223'for f in manifest['files'])
   import command_tracking_torch_candidate_v1 as actor_view_module
   assert Path(actor_view_module.__file__).resolve()==source.resolve();bridge.mdp=actor_view_module.Raw35ActorMDP(bridge.mdp,transition_projector=None);assert bridge.mdp.obs_dim==35 and bridge.mdp.actor_context_offset==0
  actor_snapshot={key:value.detach().clone() for key,value in actor.state_dict().items()}'''
# Source uses two-space indentation inside the original try.
worker = swap(worker, needle, replacement)
worker = swap(worker, 'actor_view=BASELINE_ACTOR_VIEW', 'actor_view=actor_view,algorithm_family=algorithm_family,algorithm_variant=variant[\'algorithm_variant\']', count=5)
worker = swap(worker, "assert learner.counts.pi_bptt_optimizer_steps==0;put", "assert all(value==0 for value in vars(learner.counts).values());put")
worker = swap(worker, "one_explicit_fresh_reset=True,", "one_explicit_fresh_reset=True,actor_view_control_only=actor_view==RAW35_ACTOR_VIEW,command_tracking_fixed=False,sensor_projection_exact=False,bound_anchor_reward_changes=0,")
worker = swap(worker, "'WORKER_LIFECYCLE_COMPLETE_V2.json'", "'WORKER_LIFECYCLE_COMPLETE_V3.json'")

outputs = {'resume_runtime_contracts_v3.py': helper, 'worker_supermimic_bptt_actor_variant_candidate_v3.py': worker}
for old in ('supermimic_original_owner_resume_candidate_v2.py', 'supermimic_original_owner_shared_resume_candidate_v2.py'):
    owner = (HERE / old).read_text(encoding='utf-8')
    owner = swap(owner, 'from resume_runtime_contracts_v2 import ', 'from resume_runtime_contracts_v3 import ')
    owner = swap(owner, 'worker_supermimic_bptt_resume_candidate_v2.py', 'worker_supermimic_bptt_actor_variant_candidate_v3.py')
    name = old.replace('resume_candidate_v2', 'actor_variant_candidate_v3')
    outputs[name] = owner
    source_tree = ast.parse((HERE / old).read_text(encoding='utf-8'))
    new_tree = ast.parse(owner)
    protected = lambda tree: [ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, (ast.Assign, ast.FunctionDef)) and getattr(n, 'name', None) != 'main']
    assert protected(source_tree) == protected(new_tree)

patches = []
rows = []
for name, text in outputs.items():
    ast.parse(text)
    compile(text, name, 'exec')
    path = HERE / name
    assert not path.exists()
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    old = ('resume_runtime_contracts_v2.py' if name == 'resume_runtime_contracts_v3.py' else
           'worker_supermimic_bptt_resume_candidate_v2.py' if name.startswith('worker_') else
           name.replace('actor_variant_candidate_v3', 'resume_candidate_v2'))
    patches.extend(difflib.unified_diff((HERE / old).read_text(encoding='utf-8').splitlines(True), text.splitlines(True),
                                     fromfile=str(HERE / old), tofile=str(path)))
    rows.append(dict(path=str(path), bytes=path.stat().st_size, SHA=hashlib.sha256(path.read_bytes()).hexdigest()))
assert before == {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in SOURCES}
assert hashlib.sha256(frozen.read_bytes()).hexdigest() == frozen_sha
with (HERE / 'ACTOR_VARIANT_DIFF_V3.patch').open('x', encoding='utf-8') as stream:
    stream.write(''.join(patches))
receipt = dict(kind='SOURCE_ONLY_ACTOR_VARIANT_BUILD_V3', outputs=rows, v2_source_SHA_unchanged=before,
               frozen_raw35_SHA_unchanged=frozen_sha, core_used_unchanged='ctx_reward_full_resume_candidate_v2.py',
               Torch_imports=0, SDK_imports=0, GPU_operations=0, native_runs=0, real_checkpoint_opens=0)
with (HERE / 'BUILD_ACTOR_VARIANTS_RECEIPT_V3.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, indent=2)
print(json.dumps(receipt, indent=2))
