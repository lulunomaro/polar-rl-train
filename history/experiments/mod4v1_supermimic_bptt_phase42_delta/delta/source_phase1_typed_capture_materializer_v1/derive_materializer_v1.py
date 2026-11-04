"""Derive the complete frozen V4 text by audited local function edits only.

This is not an AST-tree selector, runtime assembler, prepare or stage command.
Unchanged complete functions and all 17 shared helpers retain original bytes.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'source_phase1_capture_materializer_v4'
OLD_PIN = (45850, 'f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507')


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def derive():
    raw = (OLD / 'stage_phase1_capture_v4.py').read_bytes()
    assert (len(raw), H(raw)) == OLD_PIN
    original = raw.decode('utf-8')
    text = original
    def whole_once(old, new):
        nonlocal text
        assert text.count(old) == 1, old[:100]
        text = text.replace(old, new, 1)
    def local(name, old, new):
        nonlocal text
        lines = text.splitlines(keepends=True)
        node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
        section = ''.join(lines[node.lineno-1:node.end_lineno])
        assert section.count(old) == 1, (name, old[:100])
        section = section.replace(old, new, 1)
        text = ''.join(lines[:node.lineno-1]) + section + ''.join(lines[node.end_lineno:])
    whole_once('source-only mirror of the local R directory.', 'explicit source-only R/T mirrors (T is one pinned source file).')
    whole_once('from static_source_helpers_v1 import *\n',
        'from static_source_helpers_v1 import *\nfrom typed_source_support_v1 import (SCHEMA, PLAN_KIND, INDEX_KIND, verify_source_mirror,\n    patch_proof_allowed, typed_publication, verify_active_aliases, require_import_root,\n    validate_task_metadata)\n')
    for old, new in (
        ("WORKER_FOLDER='source_phase1_capture_worker_v4'", "WORKER_FOLDER='source_phase1_typed_native_capture_v1'"),
        ("WORKER_SEAL_PIN=(2919, 'ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180')", "WORKER_SEAL_PIN=(3503, 'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966')"),
        ("WORKER_ROOT_SHA='758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8'", "WORKER_ROOT_SHA='e7ff849c171f2eddc1053c5d1fc0779c31d6f8df73937616a7482abb85e8b897'"),
        ("WORKER_INDEX_PIN=(134423, '75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d')", "WORKER_INDEX_PIN=(148229, '92da4a44ca9b7b6246c82d4dd281b73fa176bc1bdfbac981aa3403e43d7873d8')"),
        (" 'sensor':(13,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'),", " 'sensor':(21,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3'),"),
        (" 'partition':(9,'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630')}", " 'partition':(9,'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630'),\n 'codec':(7,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219'),\n 'actuation_clock_scope_v2':(5,'105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b')}"),
        ('SOURCE_DERIVATION_VERSION=4', "SOURCE_DERIVATION_VERSION=1\nSOURCE_DERIVATION_LINEAGE='COMPLETE_FROZEN_V4_TO_TYPED_V1'"),
    ):
        whole_once(old, new)
    local('verify_package', "'worker complete13 canonical root differs'", "'worker complete15 canonical root differs'")
    local('verify_package', "rows=seal['files']", "rows=seal.get('files',seal.get('members'))")
    local('verify_package', "rel=safe_relative(row['relative']);need(rel not in result,'duplicate sealed package member')\n        need(Path(rel).suffix.lower() in ('.py','.json','.md','.txt'),'non-source sealed package member')", "rel=safe_relative(row.get('relative',row.get('name')));need(rel not in result,'duplicate sealed package member')\n        need(not any(denied(p) for p in rel.split('/')),'non-source sealed member denied before filesystem access')\n        pin=(row['bytes'],row.get('sha256',row.get('SHA256')))\n        ordinary=Path(rel).suffix.lower() in ('.py','.json','.md','.txt')\n        need(ordinary or patch_proof_allowed(folder.name,rel,expected_SHA,pin),'non-source or unqualified patch proof member')")
    local('verify_package', "content_root_sha256=seal.get('content_root_sha256')", "content_root_sha256=seal.get('content_root_sha256',seal.get('content_root_SHA256'))")
    local('load_sources', 'def load_sources(source_root):', 'def load_sources(source_root, *, t_source_root):')
    local('load_sources', 'source_root=lexical(source_root);folder=source_root/WORKER_FOLDER',
          'source_root=lexical(source_root);t_source_root=lexical(t_source_root);folder=source_root/WORKER_FOLDER\n    mirror_receipt=verify_source_mirror(source_root,t_source_root)')
    local('load_sources', 'WORKER_SEAL_PIN[1],13,worker=True', 'WORKER_SEAL_PIN[1],15,worker=True')
    local('load_sources', "need(index.get('kind')=='PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1' and index.get('source_version')==4,'final SOURCE V4 with preserved typed index required')",
          "need(index.get('kind')==INDEX_KIND and index.get('source_version')==1 and index.get('typed_producer_schema')==SCHEMA,'final frozen typed SOURCE index required')\n    active_bindings,producer_abi=typed_publication(source_root,t_source_root,index,folder)")
    local('load_sources', "len(index['dependency_sources'])==5", "len(index['dependency_sources'])==9")
    local('load_sources', "'exact original17/new5/dependency5 closure required'", "'exact original17/new5/dependency9 closure required'")
    local('load_sources', "for row in old_rows+index['new_sources']+index['dependency_sources']:", "for row in old_rows+index['new_sources']+index['dependency_sources']+[index['producer_abi']]:")
    local('load_sources', "    pinned=index['all_actuation_original_sources']", "    original_B2=index['original_B2_reference_seal']\n    need((original_B2['bytes'],original_B2['SHA256'])==(2909,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'),'original B2 reference seal differs')\n    original_B2_path=reference_path(source_root,original_B2['path'])\n    members,receipt=verify_package(original_B2_path.parent,original_B2['SHA256'],13)\n    need(len(original_B2['members'])==13 and {r['relative']:(r['bytes'],r['SHA256']) for r in original_B2['members']}=={r:(i['bytes'],i['SHA']) for r,(_,i) in members.items() if r!='SOURCE_SEAL.json'},'complete original B2 reference listing differs')\n    receipts['original_B2_reference']=receipt\n    for rel,value in members.items():sources['phase1_source_proof/original_B2_reference/'+rel]=value\n    pinned=index['all_actuation_original_sources']")
    local('load_sources', 'return dict(sources=sources,index=index,source_root=source_root,B2_source_inputs=B2_inputs,',
          'return dict(sources=sources,index=index,source_root=source_root,t_source_root=t_source_root,active_bindings=active_bindings,producer_abi=producer_abi,B2_source_inputs=B2_inputs,')
    local('load_sources', "kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V4',source_derivation_version=4", "kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_TYPED_PHASE1_V1',source_derivation_version=1,source_mirror=mirror_receipt,typed_producer_schema=SCHEMA")
    local('load_sources', 'source_mappings=27', 'source_mappings=34,overlay_source_mappings=32,independent_baseline_bootstrap_mappings=2')
    local('prepare', '*, controls=64):', '*, controls=64, t_source_root):')
    local('prepare', 'original_group_root,lexical(source_root),lexical(native_root)', 'original_group_root,lexical(source_root),lexical(t_source_root),lexical(native_root)')
    local('prepare', 'bundle=load_sources(source_root);', 'bundle=load_sources(source_root,t_source_root=t_source_root);')
    local('prepare', "plan=dict(kind='PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1',batch_purpose=PURPOSE", "plan=dict(kind=PLAN_KIND,typed_producer_schema=SCHEMA,batch_purpose=PURPOSE")
    local('prepare', "    bundle=dict(bundle,materials=materials,originals=originals)", "    bundle=dict(bundle,materials=materials,originals=originals)\n    verify_active_aliases(bundle['active_bindings'],bundle)")
    local('metadata_validate', "'source_api','passive_capture','phase1_sealed_actuation_tap','_phase1_capture_pinned_a1_core',", "'typed_capture_codec','source_api','field_snapshot','dependency_contract','passive_capture',\n        'phase1_sealed_actuation_tap','phase1_sealed_actuation_c2','_phase1_capture_pinned_a1_core',")
    local('metadata_validate', '        close=verify_close_dependency_imports(', "        active=verify_active_aliases(bundle['active_bindings'],bundle,actual_root=root)\n        close=verify_close_dependency_imports(")
    local('metadata_validate', "        selected=contract.validate_plan(plan,bundle['index'])", "        require_import_root(root,runtime)\n        if actual_root is not None:runtime.validate_installed_root(root,runtime.HERE)\n        selected=contract.validate_plan(plan,bundle['index'])")
    local('metadata_validate', "        runtime.dependency('source_api','phase1_deps/sensor/source_api.py');runtime.dependency('passive_capture','phase1_deps/sensor/passive_capture.py')\n        runtime.dependency('phase1_sealed_actuation_tap','phase1_deps/actuation/actuation_tap.py')", "        runtime.dependency('typed_capture_codec','phase1_deps/codec/typed_capture_codec.py')\n        runtime.dependency('source_api','phase1_deps/sensor/source_api.py')\n        runtime.dependency('field_snapshot','phase1_deps/sensor/field_snapshot.py')\n        runtime.dependency('dependency_contract','phase1_deps/sensor/dependency_contract.py')\n        runtime.dependency('passive_capture','phase1_deps/sensor/passive_capture.py')\n        runtime.dependency('phase1_sealed_actuation_c2','phase1_deps/actuation_c2/actuation_tap_v2.py')")
    old_task = "        task=runtime.make_task(selected[0],plan,2000.,[101,102])  # placeholders only, validate_task not fstat/admission\n        need(task['controls']==plan['capture_controls'] and task['model_PT_reads']==0 and not any(k in task for k in ('teacher_path','source_path','checkpoint','a1_producer')),'synthetic task carries model fallback')\n        negatives=0\n        for key,value in (('controls',160),('seed',20260929),('requested_roles',['E3','W35']),('checkpoint','NO_FILE_MODEL_DESCRIPTOR')):\n            bad=copy.deepcopy(task);bad[key]=value\n            try:contract.validate_task(bad)\n            except ValueError:negatives+=1\n            else:raise ValueError('capture task negative unexpectedly passed: '+key)"
    local('metadata_validate', old_task, "        task_protocol=validate_task_metadata(runtime,contract,plan,bundle['index'])")
    local('metadata_validate', "kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V4',source_derivation_version=4", "kind='REAL_WHOLE_SAFE_TYPED_CAPTURE_METADATA_IMPORT_CHECK_V1',source_derivation_version=1,typed_producer_schema=SCHEMA,active_bindings=active,task_protocol=task_protocol,ROOT_equals_HERE=True")
    local('metadata_validate', "task_controls=task['controls'],negative_tasks_rejected=negatives", "task_controls=plan['capture_controls'],positive_task_controls=task_protocol['positive_controls'],negative_tasks_rejected=task_protocol['real_task_and_plan_negative_checks']")
    local('metadata_validate', 'full_safe_module_names=list(watched)', 'full_safe_module_names=[n for n in watched if n in sys.modules],namespace_cleanup_watchlist=list(watched)')
    local('preflight_summary', "kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V4'", "kind='SOURCE_PHASE1_TYPED_CAPTURE_PREFLIGHT_NOT_ADMISSION_V1',typed_producer_schema=SCHEMA")
    local('stage', "kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V4'", "kind='SOURCE_PHASE1_TYPED_CAPTURE_MATERIALIZED_NOT_ADMISSION_V1',typed_producer_schema=SCHEMA")
    local('main', "('original-group-root','source-root','native-root','new-root')", "('original-group-root','source-root','t-source-root','native-root','new-root')")
    local('main', 'gpu_uuid,controls=args.controls)', 'gpu_uuid,controls=args.controls,t_source_root=args.t_source_root)')
    old_nodes = {n.name:n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)}
    new_nodes = {n.name:n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    assert old_nodes.keys() == new_nodes.keys()
    same = [name for name in old_nodes if ast.dump(old_nodes[name],include_attributes=False)==ast.dump(new_nodes[name],include_attributes=False)]
    changed = [name for name in old_nodes if name not in same]
    assert same == ['canonical','reference_path','normalize_B2_source_paths','verify_B2_source_closure','native_boundary','retain_originals','validate_preservation']
    assert changed == ['verify_package','load_sources','prepare','metadata_validate','preflight_summary','stage','main']
    helper = (OLD / 'static_source_helpers_v1.py').read_bytes()
    assert (HERE / 'static_source_helpers_v1.py').read_bytes() == helper
    target = HERE / 'stage_phase1_typed_capture_v1.py'
    with target.open('xb') as stream:
        stream.write(text.encode('utf-8'))
    report = dict(kind='COMPLETE_FROZEN_V4_TYPED_DERIVATION_SOURCE_DIFF_V1', source_only=True,
        original_file=dict(path=str(OLD/'stage_phase1_capture_v4.py'),bytes=len(raw),SHA256=H(raw)),
        new_file=dict(relative=target.name,bytes=len(text.encode()),SHA256=H(text.encode())),
        original_top_level_functions=len(old_nodes), same_complete_functions=same,
        necessary_changed_complete_functions=changed,
        shared_helper_functions=17, helper_whole_bytes_identical=True,
        copied_original_tree_is_not_cropped=True, complete_baseline_retention_protocol_unchanged=True,
        parent_wait_close_resource_protocol_not_changed=True,
        prepare_calls=0, preflight_calls=0, stage_calls=0, native_enabled=False, exact=False)
    with (HERE/'FUNCTION_DIFF.json').open('xb') as stream:
        stream.write((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    derive()
