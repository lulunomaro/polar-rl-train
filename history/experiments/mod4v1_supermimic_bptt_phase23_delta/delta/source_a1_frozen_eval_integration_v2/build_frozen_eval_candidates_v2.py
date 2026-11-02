"""One-shot NEW source copies/diffs only. Never import/execute a worker or parent."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'mod4v1_experts_fulldr_rm70_20261101'
NINE = BASE / 'NINE_N80_PARALLEL_SOURCE_V8'
E1 = BASE / 'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'
PINS = {
    'formal': (NINE / 'worker_five_original_n80.py', 14735, 'aff36092bf1502a6bedd5d4b347b6eb1e5675996cd191c58fbcda7b4f9bc5b1c'),
    'parent': (NINE / 'single_gpu_group_supervisor.py', 9247, '7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27'),
    'e1': (E1 / 'e1_parallel_worker_safe.py', 16275, 'f1218603d369f955a855d45ac97441901ee022f45055f45fdb001e8601d8b795'),
    'bridge': (E1 / 'e1_fresh_runtime_bridge.py', 6110, '59ab2e23ab7d28129391c7897f8f9661ca39f94634be414dfacf047a89fc5c30'),
}


def read_pinned(key):
    path, size, sha = PINS[key]
    raw = path.read_bytes()
    assert (len(raw), hashlib.sha256(raw).hexdigest()) == (size, sha), key
    return raw.decode('utf-8').replace('\r\n', '\n')


def patch(text, old, new):
    assert text.count(old) == 1, ('literal uniqueness', old, text.count(old))
    return text.replace(old, new)


def node(text, name):
    return next(x for x in ast.parse(text).body if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name == name)


def dump(value):
    return ast.dump(value, include_attributes=False)


def body_source(text, statements):
    return ''.join(text.splitlines(True)[statements[0].lineno-1:statements[-1].end_lineno])


def replace_finally(text, function_name, statement):
    outer = next(x for x in node(text, function_name).body if isinstance(x, ast.Try))
    body = outer.finalbody
    old = body_source(text, body)
    return patch(text, old, ' ' * body[0].col_offset + statement + '\n')


def save(name, text):
    destination = HERE / name
    ast.parse(text, filename=str(destination))
    compile(text, str(destination), 'exec')
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    raw = destination.read_bytes()
    return dict(path=str(destination), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def main():
    originals = {key: read_pinned(key) for key in PINS}
    outputs = {}; candidates = {}
    formal = originals['formal']
    formal = patch(formal, 'from parallel_eval_safe import task_args,put,WholeCheckpointFreshCache,wait_start',
        "sys.path.insert(0,str(Path(__file__).resolve().parents[2]))\nfrom parallel_eval_safe import put,wait_start\nfrom a1_frozen_eval_runtime_v2 import task_args,A1CheckpointAdapter,install_paired_pose_before_original_reset,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence")
    formal = patch(formal, "assert role in('E0','E2','E3','H1_normal','W35')", "assert role in('E0','E2','E3','W35')")
    formal = patch(formal, 'cache=WholeCheckpointFreshCache(torch,task)', 'cache=A1CheckpointAdapter(torch,task)')
    formal = patch(formal, 'guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);',
                          'install_paired_pose_before_original_reset(env);guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);')
    formal = patch(formal, 'obs,reward,ter,tru,extra=env.step(applied);completed+=1;',
                          'obs,reward,ter,tru,extra=env.step(applied);actor.observe_transition(ter,tru);completed+=1;')
    formal = patch(formal, 'actor_STD_before_after_exact=True,', 'A1_entire_pi_weights_norms_before_after_frozen=True,')
    formal = patch(formal, "canonical_access=False,new_PPO_or_BPTT=False,", "integration=INTEGRATION,paired_reset_protocol=paired_protocol_receipt(),unresolved_evidence=unresolved_evidence(),canonical_access=False,new_PPO_or_BPTT=False,")
    formal = patch(formal,
        "put(out/'WORKER_ERROR.json',dict(role=role,epoch=time.time(),controls_completed=completed,error=traceback.format_exc(),source_cache=(cache.receipt() if cache is not None else None),no_retry_samepurpose=True));raise",
        "record_primary_error(out,role=role,phase='formal_worker',error=traceback.format_exc(),cache=cache);raise")
    formal = replace_finally(formal, 'main', "close_original_eval_resources(env,None if ns is None else ns['app'],out,task)")
    formal = patch(formal, "scope='FreshN80source-ownfactoryandrecipes; saved20khistoryretainedincachenotapplied/sliced'",
                   "scope='FreshN80originalfactoryandrecipes;wholeOwnA1N1024CPUrootretained;noenvDRorhistoryrestoreorslice'")
    candidates['formal'] = ('worker_formal_a1_frozen_candidate_v2.py', formal)

    e1 = originals['e1']
    e1 = patch(e1, 'from e1_group_scope import KIND,validate_group_task,put_json,wait_group_start',
        "sys.path.insert(0,str(Path(__file__).resolve().parents[2]))\nfrom e1_group_scope import KIND,put_json,wait_group_start\nfrom a1_frozen_eval_runtime_v2 import validate_group_task,A1CheckpointAdapter,configure_candidate_runtime,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence")
    e1 = patch(e1, 'actor_A0_STRICT_with_learned_STD_loaded=True,', 'actor_A1_whole_pi_and_norms_strict_frozen=True,')
    e1 = patch(e1,
        "        for k,v in HOLDER['actor'].state_dict().items():assert torch.equal(v.detach().cpu(),cache.core('actor_state_dict')[k]),k",
        "        cache.check_actor(HOLDER['actor'])")
    e1 = patch(e1, 'cached_critic17AdamLRiter_preserved_not_live_runner_restore=True,',
        'cached_whole_A1_CPU_root_not_live_WM_critic_optimizer_restore=True,')
    e1 = patch(e1, 'Appclose_and_parent_wait_required=True)',
        'integration=INTEGRATION,paired_reset_protocol=paired_protocol_receipt(),unresolved_evidence=unresolved_evidence(),Appclose_and_parent_wait_required=True)')
    e1 = patch(e1,
        "task=json.loads(cli.task.read_bytes());contracts=json.loads((Path(__file__).parent/'ROLE_CONTRACTS.json').read_bytes());validate_group_task(task,role,group,case,contracts)",
        "task=json.loads(cli.task.read_bytes());contracts=json.loads((Path(__file__).parent/'ROLE_CONTRACTS.json').read_bytes());validate_group_task(task,role,group,case,contracts);configure_candidate_runtime(task,case)")
    e1 = patch(e1,
        "cache=WholeCheckpointIdentityCache(task['source_path'],torch,expected_metadata=contracts[role]['core'],expected_SHA=task['source_SHA'],expected_bytes=task['source_bytes'])",
        'cache=A1CheckpointAdapter(torch,task)')
    e1 = patch(e1, 'from e1_identity_cache import WholeCheckpointIdentityCache\n', '')
    e1 = patch(e1,
        "        error=dict(kind=KIND,role=role,stage=stage,error=traceback.format_exc(),no_independent_retry=True,parent_must_cancel_entire_group_scope=True,saved20k_DR_physically_applied=False)",
        "        error=dict(kind=KIND,role=role,stage=stage,error=traceback.format_exc(),no_independent_retry=True,parent_must_cancel_entire_group_scope=True,saved20k_DR_physically_applied=False)\n        record_primary_error(case,role=role,phase=stage,error=error['error'],cache=cache)")
    e1 = patch(e1, "        put_json(case/'WORKER_ERROR.json',error);raise", "        raise")
    e1 = replace_finally(e1, 'main_role', "close_original_eval_resources(HOLDER.get('env'),app,case,task,env_already_closed=HOLDER.get('closed',False))")
    # No geometry, termination, forces, endpoint, reward, or loop ordering edits.
    assert dump(node(e1, '_configure_environment')) == dump(node(originals['e1'], '_configure_environment'))
    assert dump(node(e1, 'build_slope50_training_axis_factory')) == dump(node(originals['e1'], 'build_slope50_training_axis_factory'))
    e1 = patch(e1, "return dict(kind=KIND,role=task['role']", "return dict(kind=KIND,num_envs=80,role=task['role']")
    candidates['e1'] = ('e1_parallel_worker_a1_frozen_candidate_v2.py', e1)

    bridge = originals['bridge']
    bridge = patch(bridge, 'from e1_identity_cache import PURPOSE',
        'from e1_identity_cache import PURPOSE\nfrom a1_frozen_eval_runtime_v2 import install_paired_pose_before_original_reset,build_a1_original_vec')
    bridge = patch(bridge, 'def attach_fresh_guard(env,identity,torch_module,tensor):\n',
        'def attach_fresh_guard(env,identity,torch_module,tensor):\n    install_paired_pose_before_original_reset(env)\n')
    start = bridge.index('class A0NoResetDecisionVec:')
    bridge = bridge[:start] + 'def build_cached_frozen_policy(env,cache,torch_module,tensor):\n    return build_a1_original_vec(env,cache,torch_module,tensor,HOLDER)\n'
    assert dump(node(bridge, 'fresh_full_dr_audit')) == dump(node(originals['bridge'], 'fresh_full_dr_audit'))
    candidates['bridge'] = ('e1_fresh_bridge_a1_frozen_candidate_v2.py', bridge)

    parent = originals['parent']
    parent = patch(parent, 'from worker_sources.parent.task_contract import make_task',
        'from a1_frozen_eval_runtime_v2 import make_task,ROLES,evaluate_waited_eval_case')
    parent = patch(parent, "assert len(roles)==9 and len({r['role']for r in roles})==9;", "assert len(roles)==8 and {r['role']for r in roles}==set(ROLES);")
    parent = patch(parent, 'assert len(children)==9;', 'assert len(children)==8;')
    parent = patch(parent, 'if len(ready)==9:', 'if len(ready)==8:')
    parent = patch(parent, 'ONEGPU_NINE_FRESH80_SKILL_EVAL_NO_LEARNING', 'ONEGPU_EIGHT_A1_FROZEN80_NO_LEARNING_V2')
    parent = patch(parent, 'All9SDKscenes+liveactors+N80fullDRreadybeforeanycontrolledstep', 'All8originalSDKscenes+frozenA1pi+N80fullDRreadybeforeanycontrolledstep')
    parent = patch(parent, 'ACTUAL_SINGLE_GPU_NINE_FRESH80_PARALLEL_SKILL_SCREEN', 'ACTUAL_SINGLE_GPU_EIGHT_A1_FROZEN80_SOURCE_CANDIDATE_V2')
    parent = patch(parent, 'nine_ready_before_start=True,all_nine_actual_execution_complete=', 'eight_ready_before_start=True,all_eight_actual_execution_complete=')
    parent = patch(parent,
        "rc=p.wait();data=json.loads((out/'FINAL.json').read_bytes())if(out/'FINAL.json').exists()else None;err=json.loads((out/'WORKER_ERROR.json').read_bytes())if(out/'WORKER_ERROR.json').exists()else None;terminal.append(dict(role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=bool(rc==0 and data and data.get('passed_execution')and err is None and(out/'PRE_CLOSE.json').exists()),data=data,error=err));put('TERMINAL_ROWS.json',terminal)",
        "rc=p.wait();semantic=evaluate_waited_eval_case(out,rc,dict(r,paired_reset_protocol=plan['paired_reset_protocol']),plan['group_id']);data=json.loads((out/'FINAL.json').read_bytes())if(out/'FINAL.json').exists()else None;err=json.loads((out/'WORKER_ERROR.json').read_bytes())if(out/'WORKER_ERROR.json').exists()else None;terminal.append(dict(role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=semantic['passed_execution'],semantic=semantic,data=data,error=err));put('TERMINAL_ROWS.json',terminal)")
    for name in ('put', 'nvidia'):
        assert dump(node(parent, name)) == dump(node(originals['parent'], name))
    # Original C/privateEX/finiteEX/resource checks and closewait are LF-text/AST identical.
    admission_start = 'class BusyResource(Exception):pass\n'
    admission_end = 'deadline=time.time()+2400\n'
    original_admission = originals['parent'].split(admission_start, 1)[1].split(admission_end, 1)[0]
    assert parent.split(admission_start, 1)[1].split(admission_end, 1)[0] == original_admission
    old_try = next(x for x in node(originals['parent'], 'main').body if isinstance(x, ast.Try))
    new_try = next(x for x in node(parent, 'main').body if isinstance(x, ast.Try))
    assert body_source(parent, new_try.finalbody) == body_source(originals['parent'], old_try.finalbody)
    candidates['parent'] = ('single_gpu_eight_a1_frozen_parent_candidate_v2.py', parent)
    # Validate every candidate before creating any candidate output.
    for name, text in candidates.values():
        ast.parse(text, filename=name); compile(text, name, 'exec')
        assert not (HERE / name).exists(), name
    outputs = {key: save(name, text) for key, (name, text) in candidates.items()}

    all_diffs = []
    for key, original in originals.items():
        newpath = Path(outputs[key]['path'])
        all_diffs.extend(difflib.unified_diff(original.splitlines(True), newpath.read_text(encoding='utf-8').splitlines(True),
                                             fromfile=str(PINS[key][0]), tofile=str(newpath)))
    with (HERE / 'FROZEN_EVAL_WHITELIST_DIFF_V2.patch').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(''.join(all_diffs))
    receipt = dict(kind='SOURCE_ONLY_N80_A1_ACTOR_CACHE_RESET_SEMANTIC_PATCH_NOT_EVAL',
        sources={k:dict(path=str(v[0]), bytes=v[1], SHA=v[2]) for k,v in PINS.items()}, outputs=outputs,
        original_parent_admission_and_finally_text_LF_identical=True, source_newlines_normalized_to_LF=True, original_DR_and_slope50_factory_AST_identical=True,
        original_e1_route_factories_endpoint_E2_W35_observers_not_modified=True,
        install_aliases={'worker_formal_a1_frozen_candidate_v2.py':'worker_sources/parent/worker_five_original_n80.py',
                        'e1_parallel_worker_a1_frozen_candidate_v2.py':'worker_sources/e1/e1_parallel_worker_safe.py',
                        'e1_fresh_bridge_a1_frozen_candidate_v2.py':'worker_sources/e1/e1_fresh_runtime_bridge.py',
                        'single_gpu_eight_a1_frozen_parent_candidate_v2.py':'single_gpu_group_supervisor.py',
                        'a1_frozen_eval_runtime_v2.py':'a1_frozen_eval_runtime_v2.py'},
        original_models_raw_JSONL_NPZ_C_SDK_GPU_SSH_Git_or_native_operations=0)
    with (HERE / 'BUILD_FROZEN_EVAL_CANDIDATES_V2.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
