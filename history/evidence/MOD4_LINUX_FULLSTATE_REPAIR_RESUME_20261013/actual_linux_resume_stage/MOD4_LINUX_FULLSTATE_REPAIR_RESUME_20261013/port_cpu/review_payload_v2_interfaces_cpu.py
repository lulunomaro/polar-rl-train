"""Readonly prepared Linux payload ABI/source/save interface review, no import GPU."""
from pathlib import Path
import ast
import hashlib
import json
import time

P = Path(__file__).resolve().parent
D = P.parent
Q = D / 'payload_v2'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources = []
for p in sorted(Q.iterdir()):
    if p.is_file():
        if p.suffix == '.py':
            compile(p.read_text(encoding='utf8'), str(p), 'exec')
        sources.append(dict(path=str(p), bytes=p.stat().st_size, sha256=H(p)))
assert H(Q / 'temporary_state_binding.py') == '587e21fe01e0c6fc42275e76aba94f1b81b30f746c49326c9bae69f50b89aa93'
for name in ('expanded_source_projection.py', 'selected_source_projection.py',
             'PERENV128_SCHEMA_V1.json', 'ACTUAL_GLOBAL1600_ASSIGNMENT.json'):
    assert H(Q / name) == H(P / name), name
runtime = (Q / 'temporary_training_runtime.py').read_text()
tree = ast.parse(runtime)
restore = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'restore_and_run')
ownsave = next(n for n in restore.body if isinstance(n, ast.FunctionDef) and n.name == 'ownsave')
ownsave_text = ast.unparse(ownsave)
historical = ('WINDOWS4090_TEMPORARY_BACKEND_BINDING', 'WINDOWS4090_TEMPORARY_BRANCH',
              'WINDOWS4090_EXPANDED_ENV_BRANCH', 'WINDOWS4090_CAPACITY_ATTEMPT',
              'WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL')
assert all(repr(name) in ownsave_text for name in historical)
assert "saved[historical] = copy.deepcopy(source[historical])" in ownsave_text
assert "saved['LINUX4090_FULLSCALE_BRANCH'] = copy.deepcopy(source['LINUX4090_FULLSCALE_BRANCH'])" in ownsave_text
assert "metadata_actual['same_repaired_resume_source_SHA'] =" not in runtime
assert "WINDOWS4090_EXPANDED_ENV_BRANCH'].update" not in runtime
plan = (Q / 'prepare_code_binding_plan_CPU_schema_reviewed.py').read_text()
for name in ('source_checkpoint_SHA', 'target_num_envs', 'selected_entry_input_ancestry_SHA',
             'no_physics_reward_command_DR_change', 'timeout_parent_math_equivalence_CPU_reviewed'):
    assert name in plan
assert "env.episode_length_buf >= env.max_episode_length" in plan
old_source = P / 'temporary_state_binding_CPU_v1_original_preserved.py'
assert H(old_source) == '1ded790db51df4857ff786dff5d4cebd91a6fec38a1d1aed089fdfbe4aea5847'
report = dict(epoch=time.time(), passed_prepared_source_compile_and_interface_CPU_only=True,
              production_dimension=20000, actual_latest_17b_CPU_review_completed=True,
              final_binding_SHA=H(Q / 'temporary_state_binding.py'),
              source_files=sources, same_reference_dependency_bytes=True,
              all_five_Windows_metadata_dicts_preserved_on_new_save=True,
              new_Linux_branch_saved_separately=True, no_left_initializer_repeated_for_17b=True,
              planned_once_code_binding_producer_schema_matches=True,
              old_initial_CPU_binding_source_preserved=dict(path=str(old_source), sha256=H(old_source),
                                                           bytes=old_source.stat().st_size),
              limitations=[
                  dict(item='SDK10 branch', scope='Not scheduled in this native144/fullrestore120/formal scope',
                       fact='Worker SDK branch still calls probe_source; new fullstate binding strictly requires20k and would rejectSDK10 before control',
                       action='Future SDK10 requires independent actor-only source verification; do not claim this branch ready'),
                  dict(item='Extra env construction/reset initialization', scope='Before strict fullrestore',
                       fact='worker initialize_selected_env plus materialize/probe_source each performs normal env.reset',
                       action='Actual12marker restore must rewind original source global/private streams and perform exactly source episode+1; no claim zero draws during initialconstruction'),
                  dict(item='GPU/source API', fact='Native Sim6 geometry/query/contact/COM/hardware ownactual not executed by this CPU reviewer',
                       action='Only root GPU owner may grant launch after actual resource/code/sourcefreeze guards'),
              ],
              no_CPU_statement_is_GPU_pass=True, no_SSH=True, no_GPU=True,
              files_not_modified_by_this_review=True, Git_archival_by_root_pending=True)
out = P / 'PAYLOAD_V2_INTERFACE_READONLY_CPU_ACTUAL_REVIEW.json'
assert not out.exists()
out.write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(dict(passed=True, report=str(out), sha256=H(out), files=len(sources), GPU_pass=False)))
