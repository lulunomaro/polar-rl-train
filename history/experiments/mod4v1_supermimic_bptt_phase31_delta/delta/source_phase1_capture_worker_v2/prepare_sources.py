"""Local SOURCE preparation only: mechanical two-function reuse + read-only pins.

No remote materializer/dispatcher or SDK execution. All writes stay in HERE.
Run once before sealing; exact repeated content accepted while unsealed.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'source_bound_only_native_integration_v1'
SEALS={
 'sensor':('source_phase1_passive_sensor_capture_v1','3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881'),
 'actuation':('source_phase1_actuation_capture_v1','ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081'),
 'adapter':('source_phase1_native_probe_integration_v1',None),
 'partition':('source_phase1_state_context_partition_v1','e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630')}


def identity(path):
    path=Path(path);raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw,filename=str(path))
    return dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def write_same(path, text):
    if (HERE/'SOURCE_SEAL.json').exists():raise RuntimeError('frozen package; new lineage required')
    path=Path(path)
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise RuntimeError('existing new SOURCE differs: '+path.name)
    else:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)


def mechanical_parent():
    path=OLD/'single_gpu_e3_w35_bound_only_parent_v1.py'
    if identity(path)!=dict(bytes=9348,SHA256='63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80'):raise ValueError('original parent pin differs')
    text=path.read_text(encoding='utf-8')
    replacements={
     'Independent E3/W35 ZERO_UPDATE BOUND ONLY probe; original EX/readiness/wait blocks unchanged.':'NEW passive E3-only capture; complete original EX/readiness/wait/finally blocks retained.',
     'from bound_only_native_runtime_v1 import make_task,ROLES,evaluate_waited_eval_case,select_requested_roles,batch_start,batch_result,grade_closed_bound_probe_group':'from phase1_capture_runtime import make_task,ROLES,evaluate_waited_eval_case,select_requested_roles,batch_start,batch_result,grade_closed_capture_group',
     "kind='ONEGPU_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1'":"kind='ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1'",
     'assert len(children)==len(requested)==2;':'assert requested==(\'E3\',) and len(children)==len(requested)==1;',
     'def bound_probe_parent_entry():':'def capture_parent_entry():',
     "grade=grade_closed_bound_probe_group(B);put('BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json',grade)":"grade=grade_closed_capture_group(B);put('PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json',grade)",
     "grade['passed_closed_bound_probe_source_grade']":"grade['passed_closed_capture_execution']",
     "if __name__=='__main__':bound_probe_parent_entry()":"if __name__=='__main__':capture_parent_entry()"}
    for old,new in replacements.items():
        if text.count(old)!=1:raise ValueError('mechanical parent anchor differs: '+old)
        text=text.replace(old,new)
    original=path.read_text(encoding='utf-8').splitlines(keepends=True);new=text.splitlines(keepends=True)
    for first,last in ((17,44),(46,78)):
        if original[first-1:last]!=new[first-1:last]:raise ValueError('original complete resource/wait/finally block changed')
    write_same(HERE/'single_gpu_passive_capture_parent_v1.py',text)
    return dict(original=identity(path),unchanged_original_line_blocks=[[17,44],[46,78]],
                generated=identity(HERE/'single_gpu_passive_capture_parent_v1.py'),executed=False)


def mechanical_close():
    original=OLD/'bound_only_native_runtime_v1.py'
    if identity(original)!=dict(bytes=40234,SHA256='e6b64b0757c97f02a9df936fe6d8edfd9e99914fb3d372c9021eb301d700d30f'):raise ValueError('original runtime pin differs')
    lines=original.read_text(encoding='utf-8').splitlines(keepends=True)
    tree=ast.parse(''.join(lines));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='close_original_eval_resources')
    body=''.join(lines[node.lineno-1:node.end_lineno])
    body=body.replace('ENV_CLOSE_RETURNED_A1_EVAL_V2','ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1').replace('APP_CLOSE_BINDING_A1_EVAL_V2','APP_CLOSE_BINDING_PHASE1_CAPTURE_V1')
    body=body.replace('APP_FAST_CLOSE_INTENT_A1_EVAL_V2','APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1').replace('APP_CLOSE_RETURNED_A1_EVAL_V2','APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1')
    body=body.replace('PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2','PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1')
    old="need(final.get('passed_execution') is True and final.get('integration') == INTEGRATION, 'successful A1 evaluation FINAL required')"
    if body.count(old)!=1:raise ValueError('original evalclose408 predicate differs')
    body=body.replace(old,'validate_preclose(final, task)  # NEW capture-only predicate; no old quality/training predicate relaxed.')
    binding_call="put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding)"
    if body.count(binding_call)!=1:raise ValueError('original binding publication anchor differs')
    body=body.replace(binding_call,binding_call[:-1]+', add_capture_epoch=False)')
    body=body.replace('        app.close()  # EXACT original call, no mode changes, no replacement close, once.',
                      "        publish(case / 'APP_CLOSE_CALLED_PHASE1_CAPTURE_V1.json', dict(epoch=time.time(), original_call_about_to_execute=True))\n        app.close()  # EXACT original call, no mode changes, no replacement close, once.")
    # Original env/App call counts, binding validation, fsync intent and error
    # handling remain byte-for-byte apart from capture namespaces/precondition.
    path=HERE/'phase1_capture_runtime.py';current=path.read_text(encoding='utf-8')
    marker='# close_original_eval_resources body is mechanically copied from the complete\n'
    prefix=current.split(marker)[0]
    final=prefix+marker+'# original evaluator with NEW capture-only predicate/labels.\n'+body+'\n'
    if 'def close_original_eval_resources(' not in current:
        if (HERE/'SOURCE_SEAL.json').exists():raise RuntimeError('frozen runtime')
        path.write_text(final,encoding='utf-8',newline='\n')
    elif current!=final:raise ValueError('generated close source differs')
    return dict(original=identity(original),original_function_lines=[node.lineno,node.end_lineno],
                exact_original_env_close_calls=1,exact_original_app_close_calls=1,executed=False)


def sealed_members(folder, expected):
    seal_path=folder/'SOURCE_SEAL.json';info=identity(seal_path)
    if expected is not None and info['SHA256']!=expected:raise ValueError('dependency seal differs: '+folder.name)
    value=json.loads(seal_path.read_text(encoding='utf-8'));files=value['files']
    if type(files) is dict:files=[dict(relative=k,**v) for k,v in files.items()]
    members=[]
    for row in files:
        path=folder/row['relative'];actual=identity(path)
        expected_sha=row.get('sha256',row.get('SHA256'))
        if actual['SHA256']!=expected_sha or actual['bytes']!=row['bytes']:raise ValueError('sealed dependency member differs: '+str(path))
        members.append(dict(relative=row['relative'],**actual))
    if folder.name=='source_phase1_native_probe_integration_v1' and value.get('content_root_sha256')!='9c8e85e30fb1499d818c8933ac46a871cc6a8970a023051d636320d67aa93c96':raise ValueError('old adapter lineage differs')
    return dict(path=str(seal_path),**info,members=members,content_root_sha256=value.get('content_root_sha256'))


def source_derivation():
    v1=ROOT/'source_phase1_capture_worker_v1'
    sealed=sealed_members(v1,'3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7')
    if sealed['content_root_sha256']!='d792dce3f110fe5fdfe30ded8840da657c22c72eaac42f60093cbe814c095028':raise ValueError('frozen V1 derivation differs')
    for leaf in ('phase1_capture_contract.py','phase1_capture_observer.py','single_gpu_passive_capture_parent_v1.py'):
        if (HERE/leaf).read_bytes()!=(v1/leaf).read_bytes():raise ValueError('V2 immutable protocol/observer/parent differs: '+leaf)
    old=(v1/'phase1_capture_runtime.py').read_text(encoding='utf-8')
    changes={
        'core()._validate_returned_app_binding(binding)':'core()._validate_returned_app_binding(binding, helper)',
        'def put_json(path, value):':'def put_json(path, value, *, add_capture_epoch=True):',
        'if type(value) is dict else value':'if type(value) is dict and add_capture_epoch else value',
        "put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding)":"put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding, add_capture_epoch=False)"}
    expected=old
    for before,after in changes.items():
        if expected.count(before)!=1:raise ValueError('V1 runtime derivation anchor differs')
        expected=expected.replace(before,after)
    if (HERE/'phase1_capture_runtime.py').read_text(encoding='utf-8')!=expected:raise ValueError('V2 runtime diff exceeds nonfast helper argument and exact binding publication fixes')
    report=ROOT/'reports/PHASE1_E3_CAPTURE_V1_FIRST_ACTUAL_ADMISSION_SNAPSHOT.json'
    published=json.loads(report.read_text(encoding='utf-8'))['actual']['published_metadata']
    error=published['cases/E3/WORKER_ERROR.json']['error']
    if "ModuleNotFoundError: No module named 'launch_storage_contract'" not in error:raise ValueError('actual V1 bootstrap failure evidence differs')
    return dict(kind='PHASE1_CAPTURE_WORKER_V2_MINIMAL_FAILURE_FIX_DERIVATION',v1_frozen_seal=sealed,
                unchanged_V1_files=['phase1_capture_contract.py','phase1_capture_observer.py','single_gpu_passive_capture_parent_v1.py'],
                preserved_V1_typed_protocol=True,parent_source_unchanged=True,
                runtime_only_diff='canonical core491(binding,helper) second argument restored in nonfast returned branch',
                first_actual_failure=dict(report=dict(path=str(report),**identity(report)),error=error,
                    original_parent_PID=published['PARENT_STARTED.json']['pid'],child_PID=published['CHILDREN.json'][0]['pid'],
                    common_GO=published['GROUP_EVAL_START.json'],child_waits=published['PARENT_EXIT_SCOPE.json']['child_waits'],
                    complete_EX_release=[published['PARENT_EXIT_SCOPE.json']['original_single_GPU_private_EX_released'],published['PARENT_EXIT_SCOPE.json']['original_global_finite_EX_released']],
                    actual_parent_wait=published['PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'],
                    SDK_App_not_constructed='SOURCE_ORDER_INFERENCE_AT_IMPORT35_NOT_PRODUCER_COUNTER_RECEIPT',
                    producer_counters=None,skill_score=None),
                source_nonfast_bug=dict(status='SEPARATE_CONFIRMED_SOURCE_SIGNATURE_BUG_NOT_TRIGGERED_IN_FIRST_ACTUAL_FAILURE',
                    canonical_signature='_validate_returned_app_binding(binding, helper)',fixed_argument='actual loaded full AppV6 helper module',
                    fast_mode_or_binding_policy_changes=False),actual_V2_native_or_resource_run=False)


def build_index():
    parent=mechanical_parent();close=mechanical_close();derivation=source_derivation()
    old_index=OLD/'BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json'
    if identity(old_index)!=dict(bytes=6085,SHA256='d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a'):raise ValueError('complete17 index differs')
    rows=json.loads(old_index.read_text(encoding='utf-8'))['entries'];original=[]
    for row in rows:
        actual=identity(row['path'])
        if actual!={k:row[k] for k in ('bytes','SHA256')}:raise ValueError('full original source differs')
        original.append(dict(path=row['path'],install_relative=row['relative'],**actual))
    deps={name:sealed_members(ROOT/folder,expected) for name,(folder,expected) in SEALS.items()}
    dependency_sources=[]
    for name,names in dict(sensor=['source_api.py','passive_capture.py','SOURCE_API_MANIFEST.json'],actuation=['actuation_tap.py','SOURCE_PINS.json']).items():
        folder=ROOT/SEALS[name][0]
        for leaf in names:dependency_sources.append(dict(path=str(folder/leaf),install_relative='phase1_deps/'+name+'/'+leaf,**identity(folder/leaf)))
    sources=json.loads((ROOT/SEALS['actuation'][0]/'SOURCE_PINS.json').read_text(encoding='utf-8'))['sources']
    for path,row in sources.items():
        actual=identity(ROOT/path)
        if (actual['bytes'],actual['SHA256'])!=(row['bytes'],row['sha256']):raise ValueError('full actuation source pin differs')
    helper=ROOT.parent/'mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py'
    new_names=['phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py']
    new=[dict(path=str(HERE/name),install_relative=name,**identity(HERE/name)) for name in new_names]
    index=dict(kind='PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1',source_only=True,native_executed=False,
               original_index=dict(path=str(old_index),**identity(old_index)),original17=original,new_sources=new,
               dependency_sources=dependency_sources,dependency_seals=deps,actuation_original_source_count=len(sources),
               all_actuation_original_sources=sources,original_capacity_helper=dict(path=str(helper),**identity(helper)),
               parent_mechanical_diff=parent,evalclose_mechanical_diff=close,
               full_original_static_tree_banks_and_vendor7_preservation='REQUIRED_FUTURE_PARENT_REVIEWED_COMPLETE_INVENTORY_NOT_CREATED_HERE',
               full_static_baseline_provenance='SOURCE_GAP_NOT_A_SOURCE_SUBSET_QUALIFICATION',
               new_purpose_original_canonical_cost_authorization='EXISTING_FINITE_VALIDATION_READONLY_PARENT_PROTOCOL; EXTERNAL_SETTLEMENT_SOURCE_REFERENCE_UNKNOWN_NO_NEW_APPROVAL_OR_WRITER',
               outer_controller_actual_parent_wait='NOT_IMPLEMENTED_OR_EXECUTED_HERE',
               capture_interface_passed=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
    text=json.dumps(index,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    path=HERE/'CAPTURE_SOURCE_INDEX.json'
    if path.exists():
        if (HERE/'SOURCE_SEAL.json').exists():raise RuntimeError('frozen SOURCE index')
        path.write_text(text,encoding='utf-8',newline='\n')
    else:write_same(path,text)
    return dict(index=identity(path),original17=len(original),new_sources=len(new),dependencies=len(dependency_sources),
                dependency_sealed_members={name:len(x['members']) for name,x in deps.items()},parent=parent,close=close)


if __name__=='__main__':print(json.dumps(build_index(),indent=2))
