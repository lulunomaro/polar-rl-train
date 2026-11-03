"""One-shot NEW source derivation only. No stager, model, SDK, admission or dispatch.
Inputs are reviewed local text files. Outputs use exclusive create in THIS directory.
Run once with stdlib Python -B; never run a derived native parent/worker here.
"""
from pathlib import Path
import ast
import hashlib
import json
import textwrap

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
OLD = R / 'source_frozen_embedded_teacher_native_v1'
CORE = R / 'source_a1_frozen_eval_integration_v2'
E1 = T / 'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'
NAME = 'good_expert_holdout_runtime_v1'

def read(path):
    return path.read_text(encoding='utf-8').replace('\r\n', '\n')

def write(name, value):
    if name.endswith('.py'):
        ast.parse(value)
    path = HERE / name
    assert path.parent == HERE and path.suffix in ('.py', '.json')
    if path.exists():
        assert path.read_text(encoding='utf-8') == value, 'existing NEW derivation output differs; inspect before targeted edit'
        return
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(value)

def node(source, name):
    found = next(n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    return '\n'.join(source.splitlines()[found.lineno-1:found.end_lineno]) + '\n'

def replace_function(source, name, replacement):
    old = node(source, name)
    assert source.count(old) == 1
    return source.replace(old, textwrap.dedent(replacement).strip()+'\n')

def change(source, old, new, count=1):
    assert source.count(old) == count, (old, source.count(old), count)
    return source.replace(old, new)

base = read(CORE / 'a1_frozen_eval_runtime_v2.py')
runtime = read(OLD / 'frozen_embedded_teacher_native_runtime_v1.py')
runtime = change(runtime, 'Embedded ORIGINAL TEACHER reference E3/W35 schema', 'Good-expert ORIGINAL TEACHER holdout C878/S135 schema')
runtime = change(runtime, "BATCH_PURPOSE = 'FROZEN_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1'", "BATCH_FAMILY = 'GOOD_EXPERT_HOLDOUT_C878_S135_V1'\nALLOWED_SEEDS = (20260929, 20260930)\nSOURCE_ENABLED = False\nSOURCE_STAGED = False")
runtime = change(runtime, "PLAN_KIND = 'FROZEN_EMBEDDED_TEACHER_E3_W35_REFERENCE_PLAN_V1'", "PLAN_KIND = 'GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1'")
runtime = change(runtime, "REQUESTED_ROLES = ('E3', 'W35')", "REQUESTED_ROLES = ('CURB_PROTECTED878', 'SLOPE135')")
runtime = runtime.replace('single_gpu_e3_w35_embedded_teacher_parent_v1.py', 'single_gpu_good_expert_holdout_parent_v1.py').replace('frozen_embedded_teacher_native_runtime_v1.py', NAME+'.py')
runtime = change(runtime, "    'worker_sources/parent/worker_five_original_n80.py',", "    'worker_sources/e1/e1_route80_factories.py',")
runtime = change(runtime, 'all sixteen complete reference mappings must be present once', 'all twenty complete holdout overlay mappings must be present once')
runtime = change(runtime, "'supermimic_vendor_v2/networks.py', 'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py')", "'supermimic_vendor_v2/networks.py', 'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py',\n    'worker_sources/e1/worker_curb878_n80.py', 'worker_sources/e1/worker_slope135_n80.py',\n    'worker_sources/e1/e1_endpoint_predicate.py', 'worker_sources/e1/ROLE_CONTRACTS.json')")
runtime = change(runtime, "KIND = 'FROZEN_EMBEDDED_TEACHER_N80_REFERENCE_TASK_V1'", "KIND = 'GOOD_EXPERT_HOLDOUT_C878_S135_N80_TASK_V1'")
runtime = change(runtime, "INTEGRATION = 'FROZEN_EMBEDDED_TEACHER_NATIVE_REFERENCE_INTEGRATION_V1'", "INTEGRATION = 'GOOD_EXPERT_HOLDOUT_E1_EMBEDDED_TEACHER_INTEGRATION_V1'")
for line in ('validate_paired_protocol = _base.validate_paired_protocol',
             'install_paired_pose_before_original_reset = _base.install_paired_pose_before_original_reset',
             'paired_protocol_receipt = _base.paired_protocol_receipt'):
    runtime = change(runtime, line, '# NEW seed-bound implementation below; canonical core remains unchanged.')
runtime = change(runtime, "'this version requests E3 then W35 only'", "'this version requests C878 then S135 only'")
runtime = change(runtime, "type(value) is dict and value.get('batch_purpose') == BATCH_PURPOSE", "type(value) is dict and value.get('batch_purpose') == purpose_for(value.get('seed'))")
runtime = change(runtime, "    need(value.get('comparison') is None, 'reference-only execution has no paired improvement')", "    need(value.get('comparison') is None, 'reference-only execution has no paired improvement')\n    need(value.get('holdout_protocol') == holdout_protocol(value['seed']), 'explicit independent seed protocol differs')")
runtime = change(runtime, "         for key, expected in ORIGINAL_SCOPES[role].items():", "         for key, expected in ORIGINAL_SCOPES[role].items():") if False else runtime
runtime = change(runtime, "        for key, expected in ORIGINAL_SCOPES[role].items():\n            if key in row:", "        for key, expected in ORIGINAL_SCOPES[role].items():\n            if key == 'seed':\n                expected = plan['seed'] if role in REQUESTED_ROLES else 20260928\n            if key in row:")
runtime = change(runtime, "row.get('worker') == 'worker_sources/parent/worker_five_original_n80.py'", "row.get('worker') == WORKER_ALIASES[row['role']]")
runtime = change(runtime, "'requested formal worker must retain its original installed alias'", "'requested E1 worker must retain its original installed alias'")
runtime = change(runtime, "        _producer_descriptor(row.get('a1_producer'), row['role'])", "        _validate_zero_update_baseline(row)")
runtime = change(runtime, 'dict(num_envs=80, seed=20260928, optimizer_updates=0,', "dict(num_envs=80, seed=validate_seed(task.get('seed')), optimizer_updates=0,")
runtime = change(runtime, "    validate_reference_row(task)\n    _validate_approved_reference(task)", "    validate_reference_row(task)\n    _validate_zero_update_baseline(task)\n    _validate_approved_reference(task)")
make = node(base, 'make_task')
make = change(make, 'seed=20260928,', "seed=validate_seed(plan.get('seed')),")
make = change(make, "    validate_paired_protocol(result['paired_reset_protocol'])\n    return result", """    validate_paired_protocol(result['paired_reset_protocol'])
    result.update(batch_purpose=purpose_for(plan['seed']), requested_roles=list(REQUESTED_ROLES),
                  deferred_roles=list(DEFERRED_ROLES), role_catalog=list(ROLES), eval_members=list(REQUESTED_ROLES),
                  overall_eight_pass_rate=None, comparison=None, policy_variant=POLICY_VARIANT,
                  holdout_protocol=holdout_protocol(plan['seed']))
    need(role in select_requested_roles(plan) and role['role'] in REQUESTED_ROLES, 'exact selected E1 row required')
    validate_reference_row(result)
    _validate_batch_members(result, role['role'])
    return result""")
runtime = replace_function(runtime, 'make_task', make)
runtime = change(runtime, '_base.configure_candidate_runtime(task, args.task.parent)', 'configure_candidate_runtime(task, args.task.parent)')
# All dynamic-purpose receipts bind a named seed-bearing object, never a global mutable seed.
for function, expression in (('task_args', "purpose_for(task['seed'])"), ('batch_start', "purpose_for(plan['seed'])"),
                              ('batch_result', "purpose_for(plan['seed'])"), ('grade_closed_reference_group', "purpose_for(plan['seed']) if 'plan' in locals() else None")):
    part = node(runtime, function).replace('batch_purpose=BATCH_PURPOSE', 'batch_purpose='+expression)
    runtime = replace_function(runtime, function, part)
runtime = change(runtime, "return dict(policy_variant=POLICY_VARIANT, group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], members=list(ready),", "return dict(policy_variant=POLICY_VARIANT, seed=plan['seed'], holdout_protocol=holdout_protocol(plan['seed']), group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], members=list(ready),")
runtime = change(runtime, "    members = value.get('members')", "    need(value['seed'] == task['seed'] and value['batch_purpose'] == task['batch_purpose'], 'cross-seed barrier substitution')\n    members = value.get('members')")
runtime = replace_function(runtime, 'wait_start', '''
def wait_group_start(task, group, maximum_seconds=900):
    """E1 ready was published by the unchanged original _ready; no reset/step/RNG here."""
    _validate_batch_members(task, task['role'])
    need(type(maximum_seconds) is int and maximum_seconds == 900, 'original ready wait900 required')
    until = min(task['absolute_worker_deadline_epoch'], time.time() + maximum_seconds)
    while time.time() < until:
        if (Path(group) / 'GROUP_ABORT.json').exists():
            raise RuntimeError('own requested holdout startup aborted')
        path = Path(group) / 'GROUP_EVAL_START.json'
        if path.exists():
            value, _ = _metadata(path)
            validate_start(task, value)
            put_json(Path(group) / 'cases' / task['role'] / 'WORKER_EVAL_STARTED.json',
                     dict(epoch=time.time(), GPU_UUID=task['GPU_UUID'], role=task['role'],
                          group_id=task['group_id'], seed=task['seed'], batch_purpose=task['batch_purpose']))
            return value
        time.sleep(.1)
    raise TimeoutError('requested original ready barrier 900s expired without stepping')
''')
runtime = replace_function(runtime, '_absolute_skill', '''
def _absolute_skill(role, data):
    """Extract existing EndpointPredicate + published standing assessor, not a new skill gate."""
    need(role in REQUESTED_ROLES and type(data) is dict, 'own requested E1 metadata required')
    metrics = data['metrics']; groups = metrics['groups']; rows = metrics['rows']
    need(type(rows) is list and len(rows) == 80 and {v.get('env') for v in rows} == set(range(80)), 'original unique N80 rows required')
    need(metrics.get('standing_not_required_to_cross') is True and metrics.get('all_valid_failed_incomplete_prefixes_retained') is True, 'original endpoint scope differs')
    result = {}
    for index, (group, denominator) in enumerate((('ascending', 27), ('descending', 27), ('stand', 26))):
        subset = [v for v in rows if v['group'] == group]
        need(len(subset) == denominator and all(v['env'] % 3 == index for v in subset), 'original fixed directional cohort differs')
        for v in subset:
            need(type(v.get('complete')) is bool and type(v.get('contact_confirmed')) is bool, 'original endpoint bool required')
            need(not v['contact_confirmed'] or v['complete'], 'contact endpoint must be complete')
            failure = v['first_ordinary_failure_control']
            need(failure is None or type(failure) is int and 0 <= failure < 750, 'original failure control differs')
        ncomplete = sum(v['complete'] for v in subset); ncontact = sum(v['contact_confirmed'] for v in subset)
        need(groups[group] == dict(environments=denominator, complete_envs=ncomplete, contact_confirmed_envs=ncontact), 'original group/row counts differ')
        if group == 'stand':
            # Exact existing assess_pair3_retention_closed_metadata_v1.py no_failure rule.
            no_failure = sum(v['first_ordinary_failure_control'] is None for v in subset)
            result[group] = dict(denominator=denominator, no_failure=no_failure,
                                 no_failure_rate=no_failure / denominator, crossing_required=False)
        else:
            result[group] = dict(denominator=denominator, complete=ncomplete, contact_confirmed=ncontact,
                                 complete_rate=ncomplete / denominator, contact_confirmed_rate=ncontact / denominator)
    return dict(scope='ORIGINAL_E1_CONDITIONAL_DIRECTION_AND_STANDING_ONLY', **result,
                whole_skill_rate=None, new_acceptance_predicate=None, full_expert_graduation=None)
''')
runtime = runtime.replace('ACTUAL_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1', 'ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1')
runtime = change(runtime, "        group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], requested_roles=list(REQUESTED_ROLES),", "        seed=plan['seed'], holdout_protocol=holdout_protocol(plan['seed']), group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], requested_roles=list(REQUESTED_ROLES),")
runtime = change(runtime, "policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN', batch_purpose=BATCH_PURPOSE", "policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN', batch_purpose=purpose_for(self.task['seed'])")
runtime = change(runtime, "final.get('evaluation_purpose') == BATCH_PURPOSE", "final.get('evaluation_purpose') == purpose_for(role_entry.get('seed'))")
runtime = change(runtime, "        evidence = validate_reference_row(role_entry)", "        _validate_e1_execution(final, role_entry)\n        evidence = validate_reference_row(role_entry)")
runtime = change(runtime, "dict(entry, paired_reset_protocol=plan['paired_reset_protocol'])", "dict(entry, seed=plan['seed'], holdout_protocol=plan['holdout_protocol'], paired_reset_protocol=plan['paired_reset_protocol'])")
runtime = change(runtime, "'SOURCE_MICROBATCH_PLAN_VALIDATION_NOT_NATIVE'", "'SOURCE_GOOD_EXPERT_HOLDOUT_PLAN_VALIDATION_NOT_NATIVE'")
# Own context is essential: canonical core's protocol remains seed20260928 and is not monkey-patched.
protocol = node(base, 'validate_paired_protocol')
protocol = change(protocol, 'seed=20260928,', "seed=validate_seed(candidate.get('seed') if type(candidate) is dict else None),")
config = '\n'.join(node(base, name) for name in ('configure_candidate_runtime', 'install_paired_pose_before_original_reset', 'paired_protocol_receipt'))
extra = read(HERE / 'holdout_protocol_components_v1.py')
insert = ("\nPOSE_PIN, POSE_VERSION, POSE_TIMING = _base.POSE_PIN, _base.POSE_VERSION, _base.POSE_TIMING\nCONTEXT = {}\n"+extra+'\n'+protocol+'\n'+config+'\n')
runtime = change(runtime, '\ndef _batch_fields(value):', insert+'\ndef _batch_fields(value):')
runtime = change(runtime, 'APPROVED_RSL_MODEL_SOURCE = _base.APPROVED_RSL_MODEL_SOURCE', 'APPROVED_RSL_MODEL_SOURCE = _base.APPROVED_RSL_MODEL_SOURCE\nAPPROVED_REFERENCE_PROVENANCE = _base.APPROVED_REFERENCE_PROVENANCE')
runtime = change(runtime, "    validate_paired_protocol(plan.get('paired_reset_protocol'))", "    need(validate_paired_protocol(plan.get('paired_reset_protocol'))['seed'] == plan['seed'], 'plan/pose seed binding differs')")
runtime = change(runtime, "    _batch_fields(task)\n    need(role in REQUESTED_ROLES", "    _batch_fields(task)\n    need(validate_paired_protocol(task.get('paired_reset_protocol'))['seed'] == task['seed'], 'task/pose seed binding differs')\n    need(role in REQUESTED_ROLES")
runtime = change(runtime, '        producer = _producer_descriptor(role_entry.get(\'a1_producer\'), role)', '        producer = _validate_zero_update_baseline(role_entry)')
runtime = change(runtime, 'original_scopes=copy.deepcopy(ORIGINAL_SCOPES), common_start_epoch=group_start,', "original_scopes={role: dict(scope, seed=plan['seed']) if role in REQUESTED_ROLES else copy.deepcopy(scope) for role, scope in ORIGINAL_SCOPES.items()}, published_baseline_seed=20260928, common_start_epoch=group_start,")
assert 'BATCH_PURPOSE' not in runtime
write(NAME+'.py', runtime)

parent = read(OLD / 'single_gpu_e3_w35_embedded_teacher_parent_v1.py')
parent = parent.replace('Independent E3/W35', 'Independent C878/S135 holdout').replace('frozen_embedded_teacher_native_runtime_v1', NAME)
parent = change(parent, 'ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1', 'ONEGPU_GOOD_EXPERT_HOLDOUT_C878_S135_V1')
parent = change(parent, "dict(r,paired_reset_protocol=plan['paired_reset_protocol'])", "dict(r,seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],paired_reset_protocol=plan['paired_reset_protocol'])")
parent = change(parent, 'def reference_parent_entry():\n main()', "def reference_parent_entry():\n # Source templates remain disabled; a future reviewed plan must explicitly be materialized.\n plan=json.loads((B/'GROUP_PLAN.json').read_bytes())\n assert plan.get('enabled') is True and plan.get('staged') is True,'SOURCE disabled: review/CPU/preflight/stage precede dispatch'\n main()")
write('single_gpu_good_expert_holdout_parent_v1.py', parent)

worker = read(CORE / 'e1_parallel_worker_a1_frozen_candidate_v2.py')
worker = change(worker, 'Four E1 workers', 'Two good-expert holdout E1 workers')
worker = change(worker, 'from e1_group_scope import KIND,put_json,wait_group_start', 'from '+NAME+' import KIND,put_json,wait_group_start,REQUESTED_ROLES,current_seed,POLICY_VARIANT')
worker = change(worker, 'from a1_frozen_eval_runtime_v2 import', 'from '+NAME+' import')
worker = change(worker, node(worker, 'build_slope50_training_axis_factory'), '')
worker = change(worker, "dict(kind=KIND,role=task['role']", "dict(seed=task['seed'],batch_purpose=task['batch_purpose'],policy_variant=POLICY_VARIANT,kind=KIND,role=task['role']")
worker = change(worker, 'def main_role(role):\n', 'def main_role(role):\n    assert role in REQUESTED_ROLES\n')
worker = change(worker, 'torch.manual_seed(20260928)', 'torch.manual_seed(current_seed())')
worker = change(worker, "        if role=='SLOPE_INDEPENDENT50':bundle=build_slope50_training_axis_factory(task,mod,identity,torch,tensor)\n        else:\n            from e1_route80_factories import build_original_route80\n            bundle=build_original_route80(role,task,case,identity,torch,np,wp,tensor)", "        from e1_route80_factories import build_original_route80\n        bundle=build_original_route80(role,task,case,identity,torch,np,wp,tensor)")
worker = change(worker, ";result['group_barrier']=barrier", ";result.update(group_barrier=barrier,seed=task['seed'],holdout_protocol=task['holdout_protocol'],policy_variant=POLICY_VARIANT,evaluation_purpose=task['batch_purpose'],actor_semantics=task['actor_semantics'])")
write('e1_good_expert_holdout_worker_v1.py', worker)
bridge = read(CORE / 'e1_fresh_bridge_a1_frozen_candidate_v2.py')
bridge = change(bridge, 'from e1_identity_cache import PURPOSE', 'from '+NAME+' import current_seed,purpose_for')
bridge = change(bridge, 'from a1_frozen_eval_runtime_v2 import', 'from '+NAME+' import')
bridge = change(bridge, '    assert env.num_envs==80', '    assert env.cfg.seed==current_seed()\n    assert env.num_envs==80')
bridge = change(bridge, 'purpose=PURPOSE', 'purpose=purpose_for(current_seed())')
bridge = change(bridge, 'original_seed=20260928', 'original_seed=current_seed()')
write('e1_good_expert_holdout_bridge_v1.py', bridge)
factory = read(E1 / 'e1_route80_factories.py')
factory = change(factory, 'from e1_fresh_runtime_bridge import attach_fresh_guard,fresh_full_dr_audit', 'from e1_fresh_runtime_bridge import attach_fresh_guard,fresh_full_dr_audit\nfrom '+NAME+' import validate_seed')
for function in ('_factory_curb_protected878', '_factory_slope135'):
    part = node(factory, function)
    part = change(part, 'seed=20260928,', "seed=validate_seed(descriptor.get('seed')),")
    part = change(part, 'args.seed == 20260928', "args.seed == validate_seed(descriptor.get('seed'))")
    factory = replace_function(factory, function, part)
factory = change(factory, "assert role in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135')", "assert role in ('CURB_PROTECTED878','SLOPE135')")
write('e1_good_expert_holdout_factories_v1.py', factory)
print(json.dumps(dict(kind='NEW_SOURCE_DERIVATION_ONLY', files=5, enabled=False, staged=False, dispatched=False)))
