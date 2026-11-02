"""One-shot stdlib builder: NEW source-only owner/worker/core copies, never launch.
Existing source_runtime/source_core_review and previous review artifacts stay read-only.
"""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNTIME = ROOT / 'source_runtime'
CORE = ROOT / 'source_core_review' / 'ctx_reward_learner.py'
EXPECTED_CORE = '2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039'


def sha(data):
    return hashlib.sha256(data).hexdigest()


WORKER_INDENT_ADJUST = False

def _one_less_indent(text):
    return '\n'.join(line[1:] if line.startswith(' ') else line for line in text.split('\n'))

def swap(text, old, new):
    if WORKER_INDENT_ADJUST:
        # Original compact worker uses one-space indentation; inserted source
        # blocks below were written with a two-space outer body for readability.
        if text.count(old) == 0:
            old = _one_less_indent(old)
        new = _one_less_indent(new)
    assert text.count(old) == 1, (old[:120], text.count(old))
    return text.replace(old, new, 1)


def write_new(name, text):
    path = HERE / name
    if path.exists():
        assert path.read_text(encoding='utf-8') == text, 'Only byte-identical partial-build outputs may be reused'
    else:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(text)
    ast.parse(text) if name.endswith('.py') else None
    compile(text, str(path), 'exec') if name.endswith('.py') else None
    return path


def functions(tree):
    return {n.name: ast.dump(n, include_attributes=False) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def class_methods(text, name):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == name)
    return {n.name: ast.dump(n, include_attributes=False) for n in node.body if isinstance(n, ast.FunctionDef)}


def protected_calls(text):
    names = {'fcntl.flock', 'account', 'b.charge_values', 'time.sleep', 'admit', 'gpu',
             'authority_budget_GO_allowed', 'authority_original_extension_count',
             'authority_tracking_schema_admitted'}
    def dotted(node):
        return ast.unparse(node)
    return sorted(ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(text))
                  if isinstance(node, ast.Call) and dotted(node.func) in names)


changes = []
source_receipts = []
core_old = CORE.read_text(encoding='utf-8')
assert sha(CORE.read_bytes()) == EXPECTED_CORE
core_new = swap(core_old,
    "        payload = torch.load(path, map_location='cpu', weights_only=True)\n        ext = payload.get('context_reward_extension', {})",
    "        payload = torch.load(path, map_location='cpu', weights_only=True)\n        return self.load_full_checkpoint(payload, allow_environment_reset=allow_environment_reset,\n                                         allow_partial_update=allow_partial_update)\n\n    def load_full_checkpoint(self, payload, *, allow_environment_reset=False, allow_partial_update=False):\n        # Already byte-pinned/decoded exactly once by the admitted future worker.\n        # Original full restore body below: all models/optimizers/replay/RNG/counts.\n        ext = payload.get('context_reward_extension', {})")
core_target = write_new('ctx_reward_full_resume_candidate_v2.py', core_new)
old_methods = class_methods(core_old, 'ContextRewardLearner')
new_methods = class_methods(core_new, 'ContextRewardLearner')
assert {k for k in old_methods if old_methods[k] != new_methods[k]} == {'load'}
for cls in ('UpdateCounts', 'ContextReplayBuffer', 'TaskAuxiliaryModel'):
    a = next(n for n in ast.parse(core_old).body if isinstance(n, ast.ClassDef) and n.name == cls)
    b = next(n for n in ast.parse(core_new).body if isinstance(n, ast.ClassDef) and n.name == cls)
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
changes.append((CORE, core_target, core_old, core_new))

for source_name, target_name in (
    ('supermimic_original_owner.py', 'supermimic_original_owner_resume_candidate_v2.py'),
    ('supermimic_original_owner_shared_v2.py', 'supermimic_original_owner_shared_resume_candidate_v2.py'),
):
    source = RUNTIME / source_name
    old = source.read_text(encoding='utf-8')
    new = swap(old, 'import three_slot_common_v1 as b\n',
               'import three_slot_common_v1 as b\nfrom resume_runtime_contracts_v2 import evaluate_waited_worker,bind_future_task_extensions\n')
    new = swap(new,
        "rc=p.wait();J=Path(e['job_root']);final=b.read(J/'production/FINAL.json');rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=rc!=0)",
        "rc=p.wait();J=Path(e['job_root']);semantic=evaluate_waited_worker(J,rc,e,run);final=semantic['final'];rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=semantic['original_error'],semantic_result=semantic)")
    new = swap(new, "if rc!=0:", "if semantic['original_error']:")
    new = swap(new, "errors.append(dict(role=e['role'],returncode=rc,reason='Realerrorpreservednoautomaticunchangedretry'));blocked=True",
               "errors.append(dict(role=e['role'],returncode=rc,reason='Realerrorpreservednoautomaticunchangedretry',semantic_reasons=semantic['reasons']));blocked=True")
    new = swap(new,
        "e=pending[0];resource=gpu(u);J=Path(e['job_root']);task,g=admit(e,u,c,run,locks,private[u],finite,resource)",
        "e=pending[0];resource=gpu(u);J=Path(e['job_root']);task,g=admit(e,u,c,run,locks,private[u],finite,resource);task=bind_future_task_extensions(task,e);put(J/'TASK.json',task)")
    new = swap(new, "str(J/'worker_sources/worker_supermimic_bptt.py')", "str(J/'worker_sources/worker_supermimic_bptt_resume_candidate_v2.py')")
    new = swap(new,
        "if s['p'].poll()is not None:e=s['entry'];rc=s['p'].wait();rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),original_error=True,final=b.read(Path(e['job_root'])/'production/FINAL.json'));del slots[u]",
        "if s['p'].poll()is not None:e=s['entry'];rc=s['p'].wait();semantic=evaluate_waited_worker(Path(e['job_root']),rc,e,run);rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),original_error=True,final=semantic['final'],semantic_result=semantic);del slots[u]")
    original_functions = functions(ast.parse(old))
    modified_functions = functions(ast.parse(new))
    assert {k for k in original_functions if original_functions[k] != modified_functions[k]} == {'main'}
    assert protected_calls(old) == protected_calls(new), 'Accounting/resource/finite call AST changed'
    old_assignments = [ast.dump(n, include_attributes=False) for n in ast.parse(old).body if isinstance(n, ast.Assign)]
    new_assignments = [ast.dump(n, include_attributes=False) for n in ast.parse(new).body if isinstance(n, ast.Assign)]
    assert old_assignments == new_assignments, 'C/UUID/reserve/roles/kind globals changed'
    target = write_new(target_name, new)
    changes.append((source, target, old, new))

source = RUNTIME / 'worker_supermimic_bptt.py'
old = source.read_text(encoding='utf-8')
WORKER_INDENT_ADJUST = True
new = swap(old, "KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'\n",
    "KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'\n_WORKER_JOB_ROOT_V2=None\nfrom resume_runtime_contracts_v2 import (FINAL_KIND,LIFECYCLE_KIND,BASELINE_ACTOR_VIEW,PinnedOwnFullCheckpoint,load_decoded_full_checkpoint_once,resolve_future_bridge_adapter,preserve_worker_error,close_original_resources)\n")
new = swap(new, 'def main():\n', 'def main():\n  global _WORKER_JOB_ROOT_V2\n')
new = swap(new, "J=a.job_root.resolve();task=", "J=a.job_root.resolve();_WORKER_JOB_ROOT_V2=J;task=")
new = swap(new,
    "out.mkdir();ns=env=teacher=bridge=learner=guard=None;error=None;latest=None;stop=False;role=task['role'];start=time.time();saved_count=0",
    "out.mkdir();ns=env=teacher=bridge=learner=guard=None;error=None;latest=None;stop=False;role=task['role'];start=time.time();saved_count=0;resume_source=None;resume_receipt=None;command_binding=None;bridge_adapter=None;actor_snapshot=None\n  assert task.get('actor_view',BASELINE_ACTOR_VIEW)==BASELINE_ACTOR_VIEW,'raw35 requires a separate fresh-zero branch'\n  task['actor_view']=BASELINE_ACTOR_VIEW")
new = swap(new,
    "   from native_supermimic_bridge import PinnedTeacher,NativeTaskBridge,TeacherResidualPolicy",
    "   from original_role_command_binding_candidate_v2 import bind_original_command_after_fresh_reset\n   obs,command_binding=bind_original_command_after_fresh_reset(env,role,obs);put(out/'ORIGINAL_COMMAND_BINDING_V2.json',command_binding)\n   from native_supermimic_bridge import PinnedTeacher,NativeTaskBridge,TeacherResidualPolicy")
new = swap(new, '   from ctx_reward_learner import ContextRewardLearner',
    '   from ctx_reward_full_resume_candidate_v2 import ContextRewardLearner')
new = swap(new,
    "teacher=PinnedTeacher(task);actor=teacher.build_actor(env.device);bridge=NativeTaskBridge(env,task,out,tensor,teacher,initial_obs=obs);bridge.init_state()",
    "teacher=PinnedTeacher(task);actor=teacher.build_actor(env.device);BridgeClass,bridge_adapter=resolve_future_bridge_adapter(NativeTaskBridge,task,J);bridge=BridgeClass(env,task,out,tensor,teacher,initial_obs=obs);bridge.init_state()\n   actor_snapshot={key:value.detach().clone() for key,value in actor.state_dict().items()}\n   def assert_teacher_actor_unchanged():\n    teacher.assert_frozen();current=actor.state_dict();assert set(current)==set(actor_snapshot);assert all(torch.equal(current[key],value) for key,value in actor_snapshot.items());assert all(not p.requires_grad for p in actor.parameters())")
new = swap(new,
    "value=super()._checkpoint(include_optimizers);value.update(bootstrap_teacher=teacher.receipt(),role=role,original_task_protocol=task['original_protocol'],new_algorithm_not_PPO_resume=True,asset_SHA=task['asset_SHA'],contract_SHA=task['contract_SHA']);return value",
    "value=super()._checkpoint(include_optimizers);value.update(bootstrap_teacher=teacher.receipt(),role=role,run_id=task['run_id'],role_key=task['role_key'],actor_view=BASELINE_ACTOR_VIEW,source_resume_receipt=resume_receipt,command_binding=command_binding,bridge_adapter=bridge_adapter,original_task_protocol=task['original_protocol'],new_algorithm_not_PPO_resume=True,asset_SHA=task['asset_SHA'],contract_SHA=task['contract_SHA']);return value")
new = swap(new,
    "teacher.assert_frozen();saved_count+=1;dest=",
    "assert_teacher_actor_unchanged();saved_count+=1;dest=")
new = swap(new,
    "bridge.learner=learner;last_report=[-1]",
    "bridge.learner=learner;last_report=[-1]\n   if task.get('resume_bptt') is not None:\n    resume_source=PinnedOwnFullCheckpoint(task['resume_bptt'],lambda stream:torch.load(stream,map_location='cpu',weights_only=True));resume_receipt=load_decoded_full_checkpoint_once(learner,resume_source,task,bridge.observed_context_layout);assert_teacher_actor_unchanged();put(out/'OWN_BPTT_FULL_RESET_RESUME_V2.json',dict(epoch=time.time(),role=role,one_original_fresh_reset_before_load=True,extra_reset_after_load=0,actor_view=BASELINE_ACTOR_VIEW,**resume_receipt))\n   else:\n    assert learner.counts.pi_bptt_optimizer_steps==0;put(out/'OWN_BPTT_FRESH_ZERO_V2.json',dict(role=role,actor_view=BASELINE_ACTOR_VIEW,native_BPTT_start=0,no_old_actor_optimizer_or_count_splicing=True))")
new = swap(new,
    "teacher.assert_frozen();put(out/'PROGRESS.json'",
    "assert_teacher_actor_unchanged();put(out/'PROGRESS.json'")
new = swap(new,
    "target_actual_BPTT_policy_steps=task['target_bptt_steps'],WM_warmup_iters=100",
    "target_actual_BPTT_policy_steps=task['target_bptt_steps'],cumulative_target_no_fresh_count_offset=True,resume_receipt=resume_receipt,command_binding=command_binding,bridge_adapter=bridge_adapter,actor_view=BASELINE_ACTOR_VIEW,WM_warmup_iters=100")
new = swap(new,
    "teacher.assert_frozen();put(out/'FINAL.json',dict(epoch=time.time(),role=role,passed_execution=True",
    "assert_teacher_actor_unchanged();put(out/'FINAL.json',dict(epoch=time.time(),kind=FINAL_KIND,run_id=task['run_id'],role_key=task['role_key'],role=role,teacher_unchanged=True,actor_view=BASELINE_ACTOR_VIEW,resume_receipt=resume_receipt,passed_execution=True")
new = swap(new,
    "  except BaseException:\n   error=traceback.format_exc();put(out/'WORKER_ERROR.json',dict(epoch=time.time(),role=role,error=error,counts=None if learner is None else vars(learner.counts),source_cache=None if teacher is None else teacher.receipt(),no_unchanged_automatic_retry=True));raise\n  finally:\n   if bridge is not None:bridge.close()\n   if env is not None:\n    put(out/'APP_CLOSING.json',dict(epoch=time.time(),calling_original_env_close=True));env.close();put(out/'ENV_CLOSED.json',dict(epoch=time.time(),closed=True))\n   if ns is not None:ns['app'].close();put(out/'APP_CLOSED.json',dict(epoch=time.time(),closed=True))\nif __name__=='__main__':main()",
    "  except BaseException:\n   error=traceback.format_exc();preserve_worker_error(out,role=role,error=error,phase='original_constructor_or_full_learner',counts=None if learner is None else vars(learner.counts),source_cache=None if teacher is None else teacher.receipt())\n  finally:\n   closure=close_original_resources(bridge,env,ns,lambda name,value:put(out/name,value))\n   if closure['errors']:\n    close_error=json.dumps(closure['errors'],indent=2);preserve_worker_error(out,role=role,error=close_error,phase='original_close',counts=None if learner is None else vars(learner.counts))\n    error=error or close_error\n   put(out/'WORKER_LIFECYCLE_COMPLETE_V2.json',dict(epoch=time.time(),kind=LIFECYCLE_KIND,role=role,run_id=task['run_id'],passed_execution=error is None,**closure))\n  if error is not None:raise RuntimeError('Worker failure preserved in source-owned error sidefiles; original App close attempted')\n\ndef worker_entry_v2():\n  try:main()\n  except BaseException:\n   failure=traceback.format_exc()\n   if _WORKER_JOB_ROOT_V2 is not None:preserve_worker_error(_WORKER_JOB_ROOT_V2/'production',role='PRESTART_OR_TERMINAL_ENTRY',error=failure,phase='worker_entry_v2')\n   else:sys.stderr.write(failure);sys.stderr.flush()\n   return 1\n  return 0\n\nif __name__=='__main__':raise SystemExit(worker_entry_v2())")
worker_target = write_new('worker_supermimic_bptt_resume_candidate_v2.py', new)
changes.append((source, worker_target, old, new))

patch = []
for source, target, old, new in changes:
    source_receipts.append(dict(path=str(source), bytes=source.stat().st_size, SHA256=sha(source.read_bytes())))
    patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(source), tofile=str(target)))
with (HERE / 'SOURCE_ONLY_RESUME_DIFF_V2.patch').open('x', encoding='utf-8') as stream:
    stream.writelines(patch)
receipt = dict(kind='SOURCE_ONLY_COPIES_AST_COMPILE_NOT_NATIVE_RESTORATION',
               existing_sources_unchanged=True, original_core_SHA256=EXPECTED_CORE,
               source_files=source_receipts,
               outputs=[dict(path=str(target), SHA256=sha(target.read_bytes()), bytes=target.stat().st_size)
                        for _, target, _, _ in changes],
               original_owner_functions_except_main_AST_identical=True,
               original_owner_C_UUID_RESERVE_global_assignments_AST_identical=True,
               original_owner_account_lock_admit_resource_and_sleep_call_AST_identical=True,
               core_original_methods_except_load_AST_identical=True,
               core_UpdateCounts_ContextReplayBuffer_TaskAuxiliaryModel_AST_identical=True,
               SDK_imports=0, PT_reads=0, native_runs=0, training_updates=0)
assert sha(CORE.read_bytes()) == EXPECTED_CORE
for entry in source_receipts:
    assert sha(Path(entry['path']).read_bytes()) == entry['SHA256']
with (HERE / 'BUILD_SOURCE_CANDIDATES_RECEIPT_V2.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt, indent=2))
