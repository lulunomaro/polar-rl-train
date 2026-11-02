"""Source-only builder. Writes only sibling NEW teacher-reference artifacts."""
from pathlib import Path
import ast, copy, hashlib, json, re
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OLD = PROJECT / 'source_frozen_eval_microbatch_parent_v1'
OLD_STAGE = PROJECT / 'source_stage_a1_microbatch_eval_v2'
CORE = PROJECT / 'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py'
RUNTIME = 'frozen_embedded_teacher_native_runtime_v1'
PARENT = 'single_gpu_e3_w35_embedded_teacher_parent_v1.py'
VARIANT = 'ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1'
PURPOSE = 'FROZEN_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1'
PLAN = 'FROZEN_EMBEDDED_TEACHER_E3_W35_REFERENCE_PLAN_V1'
INDEX_KIND = 'SOURCE_ONLY_16_MAPPINGS_EMBEDDED_ORIGINAL_TEACHER_NATIVE_V1'


def load(path, pin=None):
    raw = path.read_bytes()
    if pin: assert (len(raw), hashlib.sha256(raw).hexdigest()) == pin
    return raw.decode('utf-8').replace('\r\n', '\n')


def change(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


def put(name, text):
    path = HERE / name
    if path.exists(): path.read_bytes()  # These are this builder's own NEW outputs, not old seals.
    path.write_bytes(text.encode('utf-8'))
    if name.endswith('.py'): compile(text, str(path), 'exec')
    return path


def function(text, name):
    node = next(n for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef,ast.ClassDef)) and n.name == name)
    return ast.get_source_segment(text,node)


core = load(CORE, (37927,'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'))
runtime = load(OLD / 'frozen_eval_microbatch_runtime_v1.py', (19987,'a7ed3e5df9fc5239e9ad490aab0fa677dd43dc7d62de4b2ebccc0ad0838e1e91'))
runtime = change(runtime, 'Candidate-only E3/W35 subset schema and barrier; original A1 mechanisms reused.', 'Embedded ORIGINAL TEACHER reference E3/W35 schema; original plant/barrier/close retained.')
runtime = change(runtime, 'No reference evaluator, training, ledger, lock acquisition, or model decoder here.', 'Import executes no training, ledger, lock acquisition, model decoder, SDK, or actor.')
runtime = runtime.replace('A1_FROZEN_CANDIDATE_ONLY_E3_W35_MICROBATCH_V1', PURPOSE).replace('A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1', PLAN)
runtime = change(runtime, 'KIND, INTEGRATION = _base.KIND, _base.INTEGRATION', "KIND = 'FROZEN_EMBEDDED_TEACHER_N80_REFERENCE_TASK_V1'\nINTEGRATION = 'FROZEN_EMBEDDED_TEACHER_NATIVE_REFERENCE_INTEGRATION_V1'\nPOLICY_VARIANT = '" + VARIANT + "'\nfrom producer_teacher_guard_v1 import validate_reference_row\n_ref = _base._pinned_module('embedded_teacher_reference_v1', (16333, '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'))")
guard_raw = (HERE/'producer_teacher_guard_v1.py').read_bytes()
guard_pin = (len(guard_raw), hashlib.sha256(guard_raw).hexdigest())
runtime = change(runtime, 'from producer_teacher_guard_v1 import validate_reference_row',
    '_guard = _base._pinned_module(\'producer_teacher_guard_v1\', '+repr(guard_pin)+')\nvalidate_reference_row = _guard.validate_reference_row')
runtime = change(runtime, '_producer_descriptor = _base._producer_descriptor', '# Metadata-only wrapper below avoids pre-admission checkpoint lstat; original schema remains unchanged.')
runtime = change(runtime, 'A1CheckpointAdapter = _base.A1CheckpointAdapter', '# Reference adapter is defined below; original cache implementation remains unchanged.')
runtime = change(runtime, 'record_primary_error = _base.record_primary_error', '# Original error/close bodies are copied below with this explicit reference integration label.')
runtime = change(runtime, 'close_original_eval_resources = _base.close_original_eval_resources', '# close_original_eval_resources: original reviewed body, defined below.')
runtime = change(runtime, 'evaluate_waited_eval_case = _base.evaluate_waited_eval_case', '# Reference policy component gate plus unchanged common cache/close semantic body, below.')
old_aliases = "    'single_gpu_e3_w35_a1_frozen_parent_v1.py', 'frozen_eval_microbatch_runtime_v1.py',"
runtime = change(runtime, old_aliases, "    '" + PARENT + "', '" + RUNTIME + ".py',\n    'embedded_teacher_reference_v1.py', 'producer_teacher_guard_v1.py', 'resume_runtime_contracts_v3.py',")
runtime = change(runtime, "    need(type(value) is dict and value.get('batch_purpose') == BATCH_PURPOSE,", "    need(value.get('policy_variant') == POLICY_VARIANT, 'explicit original teacher reference policy required')\n    need(type(value) is dict and value.get('batch_purpose') == BATCH_PURPOSE,")
runtime = runtime.replace('explicit independent candidate-only microbatch purpose required', 'explicit independent ORIGINAL TEACHER reference purpose required')
runtime = runtime.replace('candidate-only schema has no paired improvement', 'reference-only execution has no paired improvement')
runtime = runtime.replace('all thirteen reviewed/current mappings must be present once', 'all sixteen complete reference mappings must be present once')
runtime = runtime.replace('this candidate-only version does not verify or execute a mother reference', 'same-seed configuration does not establish matched reference/candidate UID or pose')
runtime = runtime.replace('actual reference is unimplemented in this candidate-only batch', 'actual paired reference/candidate equivalence remains unverified')
runtime = change(runtime, "        _producer_descriptor(row.get('a1_producer'), row['role'])", "        _producer_descriptor(row.get('a1_producer'), row['role'])\n        validate_reference_row(row)")
runtime = change(runtime, "    _validate_batch_members(result, role['role'])", "    result.update(kind=KIND, purpose=KIND, integration=INTEGRATION, policy_variant=POLICY_VARIANT)\n    validate_reference_row(result)\n    _validate_batch_members(result, role['role'])")
runtime = change(runtime, '    _validate_approved_reference(task)', '    validate_reference_row(task)\n    _validate_approved_reference(task)')
runtime = change(runtime, "    _base.configure_candidate_runtime(task, args.task.parent)", "    _base.configure_candidate_runtime(task, args.task.parent)\n    _base.put_json(args.task.parent / 'REFERENCE_POLICY_IDENTITY.json', dict(policy_variant=POLICY_VARIANT,\n        batch_purpose=BATCH_PURPOSE, actor_semantics=task['actor_semantics'], actor_container_identity=task['actor_container_identity'],\n        source_path=task['source_path'], source_SHA=task['source_SHA'], source_bytes=task['source_bytes'],\n        original_bootstrap_teacher=task['original_bootstrap_teacher'], actual_paired_protocol_UID_match=None))")
runtime = change(runtime, '    return dict(group_id=plan', '    return dict(policy_variant=POLICY_VARIANT, group_id=plan')
runtime = change(runtime, "        zero_controls_before_group_barrier=True, batch_purpose=BATCH_PURPOSE, **ready))", "        zero_controls_before_group_barrier=True, batch_purpose=BATCH_PURPOSE, **ready))")
runtime = change(runtime, "    return dict(kind='ACTUAL_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1', batch_purpose=BATCH_PURPOSE,", "    return dict(kind='ACTUAL_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1', batch_purpose=BATCH_PURPOSE, policy_variant=POLICY_VARIANT,")
runtime = runtime.replace('BothRequestedOriginalScenes_FrozenA1_N80FullDR_BeforeAnyControlledStep', 'BothRequestedOriginalScenes_EmbeddedOriginalTeacher_N80FullDR_BeforeAnyControlledStep')
runtime = change(runtime, "        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))", "        policy_variant=POLICY_VARIANT, reference_not_candidate=True,\n        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))")
# Copies preserve complete bodies; no cropped modules are executed at stage/runtime.
common = '\n\n_metadata = _base._metadata\n_pinned_module = _base._pinned_module\nput_json = _base.put_json\nAPP_PIN = _base.APP_PIN\nAPPROVED_RSL_MODEL_SOURCE = _base.APPROVED_RSL_MODEL_SOURCE\n_validate_returned_app_binding = _base._validate_returned_app_binding\nimport sys, traceback\n\n'
common += function(core, 'record_primary_error') + '\n\n' + function(core, 'close_original_eval_resources')
extras = r'''

def _producer_descriptor(value, role):
    """Original descriptor schema; metadata never resolves/stats checkpoint paths.

    Actual admitted A1CheckpointAdapter/cache physical containment and byte checks
    stay unchanged. This narrow temporary wrapper is used only for metadata.
    """
    original = Path.resolve
    def lexical_checkpoint(path, *args, **kwargs):
        if path.suffix.lower() in ('.pt', '.pth', '.ckpt', '.safetensors', '.onnx'):
            return Path(os.path.abspath(os.path.normpath(os.fspath(path))))
        return original(path, *args, **kwargs)
    try:
        Path.resolve = lexical_checkpoint
        return _base._producer_descriptor(value, role)
    finally:
        Path.resolve = original


class ReferenceCaller(_ref.EmbeddedTeacherReferenceCaller):
    def receipt(self):
        return dict(super().receipt(), paired_reset_protocol=paired_protocol_receipt(), unresolved_evidence=unresolved_evidence())


class A1CheckpointAdapter(_base.A1CheckpointAdapter):
    """Same ONE whole A1 cache; effective actor is only the embedded original teacher."""
    def __init__(self, torch_module, task):
        validate_reference_row(task)
        super().__init__(torch_module, task)
    def actor(self, device, n=80):
        original = super().actor(device, n)
        from tensordict import TensorDict
        reference = _ref.EmbeddedTeacherMeanReference(original.mean, tensor_dict_cls=TensorDict,
            producer_final=self.task['a1_producer']['FINAL'], expected_rsl_source=self.task['approved_RSL_model_source'],
            producer_freeze_evidence=validate_reference_row(self.task))
        self.caller = ReferenceCaller(reference, boundary=original.boundary)
        return self.caller
    def receipt(self):
        result = dict(self.cache.receipt(), integration=INTEGRATION, policy_variant=POLICY_VARIANT,
            policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN', batch_purpose=BATCH_PURPOSE,
            actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
            original_bootstrap_teacher=dict(self.task['original_bootstrap_teacher']),
            producer_teacher_freeze_evidence=validate_reference_row(self.task),
            old_RSL_actor_checkpoint_loader_used=False,
            approved_reference_provenance=dict(self.task['approved_reference_provenance']),
            approved_RSL_model_source=dict(self.task['approved_RSL_model_source']),
            actual_eval_RSL_source_binding=(dict(self.caller.mean.actual_RSL_source) if self.caller is not None else None),
            admitted_producer_run_id=self.task['a1_producer']['run_id'],
            actual_BPTT_policy_steps=self.task['a1_producer']['FINAL']['actual_BPTT_policy_steps'])
        if self.caller is not None:
            reference = self.caller.receipt()
            result['embedded_teacher_reference'] = reference
            states = reference['full_teacher_state_manifest']
            norms = [row['name'] for row in states if 'norm' in row['name'].lower()]
            buffers = [row['name'] for row in states if row['kind'] == 'buffer']
            result['actual_teacher_state_capabilities'] = dict(normalization_state_names=norms, named_buffers=buffers,
                normalization='identity_no_persistent_teacher_norm_state_observed' if not norms else 'actual_manifest_above',
                persistent_buffer_case='not_applicable_no_buffer_in_actual_schema' if not buffers else 'all_buffers_value_checked',
                std_state_names=[row['name'] for row in states if 'std' in row['name'].lower()],
                whole_pi_residual_RMS_guard_still_active=True)
        return result
'''
semantic = function(core, 'evaluate_waited_eval_case')
start = semantic.index("        mean = source.get('frozen_mean')")
end = semantic.index("        need((case / 'PRE_CLOSE.json')", start)
replacement = '''        need(final.get('policy_variant') == POLICY_VARIANT and final.get('evaluation_purpose') == BATCH_PURPOSE,
             'explicit reference FINAL variant/purpose required')
        evidence = validate_reference_row(role_entry)
        reference = source.get('embedded_teacher_reference')
        _ref.validate_reference_semantics(reference, expected_role=role, expected_source_sha=checkpoint['SHA'],
            expected_bootstrap_teacher_sha=role_entry['original_bootstrap_teacher']['source_SHA'], expected_actor_calls=CONTROLS[role])
        need(reference.get('producer_teacher_state_guard') == evidence
             and source.get('producer_teacher_freeze_evidence') == evidence and 'frozen_mean' not in source
             and source.get('policy_variant') == POLICY_VARIANT
             and source.get('policy_family') == 'EMBEDDED_ORIGINAL_TEACHER_MEAN'
             and source.get('original_bootstrap_teacher') == role_entry['original_bootstrap_teacher'], 'reference source/producer/actor identity differs')
        paired = reference.get('paired_reset_protocol')
        need(type(paired) is dict and paired.get('candidate_pose_installed') is True
             and paired.get('protocol') == validate_paired_protocol(role_entry.get('paired_reset_protocol')),
             'shared original pose installer/protocol receipt missing; no matched UID claim')
'''
semantic = semantic[:start] + replacement + semantic[end:]
semantic = semantic.replace('ACTUAL_WAITED_A1_N80_EVAL_SEMANTIC_V2', 'ACTUAL_WAITED_EMBEDDED_ORIGINAL_TEACHER_N80_REFERENCE_SEMANTIC_V1')
grade = r'''

def grade_closed_reference_group(group_root):
    """Read-only original close/exit receipts; never creates external parent-wait proof."""
    root = Path(group_root).resolve(); reasons = []; checked = []
    def read(name):
        path = root / name
        with path.open('rb') as stream:
            raw = stream.read(8 * 1024 * 1024 + 1)
        need(len(raw) <= 8 * 1024 * 1024, 'bounded group metadata required: ' + name)
        return json.loads(raw)
    try:
        for name in ('PARENT_ORIGINAL_ERROR.json', 'GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json'):
            need(not (root / name).exists(), 'original group error remains: ' + name)
        plan = read('GROUP_PLAN.json'); rows = select_requested_roles(plan)
        need(plan['group_id'] == root.name, 'own closed reference group identity differs')
        final = read('FINAL.json'); _batch_fields(final)
        need(final.get('kind') == 'ACTUAL_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1'
             and final.get('group_id') == plan['group_id'] and final.get('GPU_UUID') == plan['GPU_UUID']
             and final.get('all_requested_actual_execution_complete') is True
             and final.get('requested_ready_before_start') is True
             and final.get('original_eight_role_catalog') == plan['roles'], 'original reference batch FINAL incomplete or mismatched')
        admission = read('ACTUAL_GROUP_ADMISSION.json')
        need(admission.get('group_id') == plan['group_id'] and admission.get('original_private_GPU_EX_held') is True
             and admission.get('original_global_finite_EX_held') is True and admission.get('canonical_writes') == 0
             and admission.get('canonical_owner_at_read') is None, 'original group admission receipt incomplete')
        exit_receipt = read('PARENT_EXIT_SCOPE.json')
        need(all(exit_receipt.get(key) is True for key in ('all_own_children_waited',
             'original_single_GPU_private_EX_released', 'original_global_finite_EX_released'))
             and exit_receipt.get('errors') == [] and exit_receipt.get('canonical_writes') == 0,
             'original actual waits/resource release/errors do not qualify')
        waits = exit_receipt.get('child_waits'); terminal = read('TERMINAL_ROWS.json')
        need(type(waits) is list and len(waits) == 2 and type(terminal) is list and len(terminal) == 2
             and {v.get('role') for v in waits} == set(REQUESTED_ROLES)
             and {v.get('role') for v in terminal} == set(REQUESTED_ROLES)
             and final.get('rows') == terminal, 'exact original two waited child rows required')
        for entry in rows:
            role = entry['role']; waited = next(v for v in waits if v['role'] == role)
            row = next(v for v in terminal if v['role'] == role)
            need(waited.get('actual_waited') is True and type(waited.get('returncode')) is int
                 and waited['returncode'] == 0 and waited.get('pid') == row.get('pid')
                 and _terminal_success(row), 'original terminal/cleanup child wait differs: ' + role)
            case = root / 'cases' / role
            semantic = evaluate_waited_eval_case(case, row['returncode'],
                dict(entry, paired_reset_protocol=plan['paired_reset_protocol']), plan['group_id'])
            need(semantic.get('passed_execution') is True and row.get('semantic') == semantic,
                 'reference original semantic gate differs after close: ' + role)
            case_final, _ = _base._metadata(case / 'FINAL.json')
            need(row.get('data') == case_final, 'original terminal/actual case FINAL differs: ' + role)
            checked.append(role)
    except Exception as error:
        reasons.append(type(error).__name__ + ':' + str(error))
    return dict(kind='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1', policy_variant=POLICY_VARIANT,
        batch_purpose=BATCH_PURPOSE, group_root=str(root), passed_closed_reference_source_grade=not reasons,
        original_error=bool(reasons), reasons=reasons, checked_roles=checked,
        external_executing_parent_actual_wait_required=True, external_parent_wait_proof_created_here=False,
        qualified_reference_execution=None, UID_alignment=None, reference_cache_match=None,
        relative_improvement=None, paired_reward_effect=None, overall_eight_pass_rate=None,
        C_or_lock_or_SDK_or_checkpoint_operations=0)
'''
marker = "\n\nif __name__ == '__main__':"
runtime = change(runtime, marker, common + extras + '\n\n' + semantic + grade + marker)
runtime = change(runtime, "    parser.add_argument('--validate-plan', required=True, type=Path)",
    "    modes = parser.add_mutually_exclusive_group(required=True)\n    modes.add_argument('--validate-plan', type=Path)\n    modes.add_argument('--grade-closed-group', type=Path)")
runtime = change(runtime, '    plan, _ = _base._metadata(args.validate_plan)',
    "    if args.grade_closed_group is not None:\n        result = grade_closed_reference_group(args.grade_closed_group)\n        print(json.dumps(result, sort_keys=True))\n        raise SystemExit(0 if result['passed_closed_reference_source_grade'] else 1)\n    plan, _ = _base._metadata(args.validate_plan)")
put(RUNTIME + '.py', runtime)

worker = load(OLD / 'worker_formal_a1_microbatch_v1.py', (15016,'a370656816f134c13219f5e013cedfddc8f16ca41d85ef1f7cb9b751152cce56'))
worker = worker.replace('from frozen_eval_microbatch_runtime_v1 import', 'from ' + RUNTIME + ' import')
worker = change(worker, 'meanA0, oneGPU9barrier', 'EMBEDDED ORIGINAL TEACHER MEAN, explicit E3/W35 reference barrier')
worker = change(worker, 'ready=dict(resource_only_GPU_capacity=', "ready=dict(policy_variant=task['policy_variant'],evaluation_purpose=task['batch_purpose'],resource_only_GPU_capacity=")
worker = change(worker, "result=dict(kind=task['kind'],", "result=dict(policy_variant=task['policy_variant'],evaluation_purpose=task['batch_purpose'],actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',kind=task['kind'],")
put('worker_formal_embedded_teacher_v1.py', worker)
parent = load(OLD / 'single_gpu_e3_w35_a1_frozen_parent_v1.py', (8991,'9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b'))
parent = parent.replace('Independent requested E3/W35 candidate batch;', 'Independent E3/W35 EMBEDDED ORIGINAL TEACHER reference;')
parent = parent.replace('from frozen_eval_microbatch_runtime_v1 import', 'from ' + RUNTIME + ' import')
parent = parent.replace('ONEGPU_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1', 'ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1')
parent = change(parent, 'select_requested_roles,batch_start,batch_result', 'select_requested_roles,batch_start,batch_result,grade_closed_reference_group')
parent = change(parent, "if __name__=='__main__':main()", '''def reference_parent_entry():
 main()
 # Original complete main/finally ran first; no lock/account/wait operation is replaced.
 grade=grade_closed_reference_group(B);put('REFERENCE_GROUP_CLOSED_SOURCE_GRADE_V1.json',grade)
 if not grade['passed_closed_reference_source_grade']:raise SystemExit(1)
if __name__=='__main__':reference_parent_entry()''')
put(PARENT, parent)

index = json.loads((OLD_STAGE / 'MICROBATCH_STAGE_INDEX_V2.json').read_bytes())
index['kind'] = INDEX_KIND
index['original_fourteen_entries_unchanged_except_three_explicit_routes'] = True
index['new_dependency_only'] = False
index['original_thirteen_entries_unchanged'] = False
index['original_runtime_requires_thirteen_as_subset_unchanged'] = False
index['source_variant'] = 'EMBEDDED_ORIGINAL_TEACHER_REFERENCE_NOT_CANDIDATE'
entries = index['entries']
for row in entries:
    if row['relative'] == 'single_gpu_e3_w35_a1_frozen_parent_v1.py': row.update(path=str(HERE/PARENT), relative=PARENT)
    elif row['relative'] == 'frozen_eval_microbatch_runtime_v1.py': row.update(path=str(HERE/(RUNTIME+'.py')), relative=RUNTIME+'.py')
    elif row['relative'] == 'worker_sources/parent/worker_five_original_n80.py': row['path'] = str(HERE/'worker_formal_embedded_teacher_v1.py')
entries += [dict(path=str(PROJECT/'source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py'), relative='embedded_teacher_reference_v1.py'),
            dict(path=str(HERE/'producer_teacher_guard_v1.py'),relative='producer_teacher_guard_v1.py')]
for row in entries:
    raw = Path(row['path']).read_bytes(); row.update(bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())
index_raw = (json.dumps(index,indent=2)+'\n').encode()
put('EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json',index_raw.decode())

stage = load(OLD_STAGE/'stage_a1_microbatch_eval_v2.py', (32953,'9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952'))
stage = change(stage, "INDEX_PIN = (4886, '69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50')", 'INDEX_PIN = '+repr((len(index_raw),hashlib.sha256(index_raw).hexdigest())))
stage = stage.replace('SOURCE_ONLY_14_MAPPINGS_MICROBATCH_CLOSE_DEPENDENCY_V2_NOT_INSTALLED', INDEX_KIND)
stage = change(stage, 'len(entries) == 14', 'len(entries) == 16')
stage = stage.replace('fourteen-mapping','sixteen-mapping').replace('exact fourteen mappings','exact sixteen mappings').replace('original thirteen plus one close dependency','complete sixteen reference mappings')
stage = stage.replace("'single_gpu_e3_w35_a1_frozen_parent_v1.py'",repr(PARENT)).replace("'frozen_eval_microbatch_runtime_v1.py'",repr(RUNTIME+'.py'))
stage = change(stage, "'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py', 'resume_runtime_contracts_v3.py'}", "'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py', 'resume_runtime_contracts_v3.py',\n    'embedded_teacher_reference_v1.py', 'producer_teacher_guard_v1.py'}")
stage = stage.replace("kind='A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1', batch_purpose='A1_FROZEN_CANDIDATE_ONLY_E3_W35_MICROBATCH_V1'", "kind='"+PLAN+"', batch_purpose='"+PURPOSE+"', policy_variant='"+VARIANT+"'")
stage = change(stage, "        plan['roles'].append(row)", "            guard_path = sources['producer_teacher_guard_v1.py'][0]\n            spec = importlib.util.spec_from_file_location('_teacher_guard_stage_v1', guard_path)\n            guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)\n            row.update(policy_variant='"+VARIANT+"', actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',\n                actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',\n                original_bootstrap_teacher=guard.teacher_identity(producers[role]['FINAL']['teacher']),\n                producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]))\n        plan['roles'].append(row)")
stage = change(stage, "watched = ('a1_frozen_eval_runtime_v2', 'frozen_eval_microbatch_runtime_v1', 'app_close_semantics_v5', 'resume_runtime_contracts_v3')", "watched = ('a1_frozen_eval_runtime_v2', '"+RUNTIME+"', 'embedded_teacher_reference_v1', 'producer_teacher_guard_v1', 'app_close_semantics_v5', 'resume_runtime_contracts_v3')")
# The prior single-quoted filename replacement above also routes the complete --validate-plan module.
stage = change(stage, "        need(result.get('requested_roles') == list(REQUESTED) and result.get('resources_acquired') == result.get('model_opens') == 0,", "        need(result.get('policy_variant') == '"+VARIANT+"' and result.get('reference_not_candidate') is True, 'reference metadata CLI variant differs')\n        need(result.get('requested_roles') == list(REQUESTED) and result.get('resources_acquired') == result.get('model_opens') == 0,")
stage = stage.replace('MICROBATCH_V2', 'EMBEDDED_TEACHER_REFERENCE_V1')
stage = stage.replace('SOURCE_MICROBATCH_PREFLIGHT_ONLY_NO_ADMISSION_V2','SOURCE_TEACHER_REFERENCE_PREFLIGHT_ONLY_NO_ADMISSION_V1').replace('SOURCE_MICROBATCH_STAGE_COMPLETE_NOT_DISPATCH_V2','SOURCE_TEACHER_REFERENCE_STAGE_COMPLETE_NOT_DISPATCH_V1')
stage = change(stage, 'V2 stdlib ONLY: original thirteen plus complete close dependency;', 'Teacher-reference stdlib ONLY: sixteen complete mappings and original static plant;')
put('stage_embedded_teacher_native_v1.py', stage)
print(json.dumps(dict(source_only=True,index_entries=len(entries),runtime=RUNTIME,parent=PARENT,actual_native_or_model_operations=0),indent=2))
