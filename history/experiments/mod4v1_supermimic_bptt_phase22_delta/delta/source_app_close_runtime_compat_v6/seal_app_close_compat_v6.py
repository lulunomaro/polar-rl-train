"""Append-only V6 source seal; no SDK import, old source write or worker execution."""
import ast
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import re

B=Path(__file__).resolve().parent;ROOT=B.parent;S=B/'GATE_SCRATCH_V6'

def record(path):
    raw=path.read_bytes()
    return dict(name=path.name,path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())

def put(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def verify_old(directory,expected):
    manifest=directory/'DELIVERABLES_SHA256_V1.json' if directory.name=='source_eval_a1_raw35_v1' else directory/'DELIVERABLES_SHA256_V5.json'
    assert record(manifest)['SHA256']==expected
    entries=json.loads(manifest.read_text(encoding='utf-8'))['files']
    for entry in entries:
        now=record(Path(entry['path']));assert (now['bytes'],now['SHA256'])==(entry['bytes'],entry['SHA256']),entry['path']
    return dict(manifest=record(manifest),unchanged_sealed_entries=len(entries))

def main():
    assert not (B/'DELIVERABLES_SHA256_V6.json').exists(),'sealed; use NEW version/scratch'
    target=record(B/'app_close_semantics_v6.py')
    assert target['bytes']==27769 and target['SHA256']=='3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39'
    assert (B/'app_close_semantics_v6.py').read_bytes()==(S/'app_close_semantics_v5.py').read_bytes()
    old5=verify_old(ROOT/'source_app_close_semantics_v5','c363463155bfd47cc6e781be3bec3f243479d6758ca11391f3bca0d3d5868311')
    oldeval=verify_old(ROOT/'source_eval_a1_raw35_v1','62312d159d3b038b7c22818bb2229c85c8723e7ecedd93828e6b4e95823ee7f1')
    sources=[ROOT/'source_app_close_semantics_v5/app_close_semantics_v5.py',ROOT/'source_app_close_semantics_v5/test_app_close_semantics_v5.py',
      ROOT/'source_app_close_semantics_v5/_synthetic_app_fixture_v5.py',ROOT/'source_app_close_semantics_v5/resume_runtime_app_close_v5.py',
      ROOT/'source_app_close_semantics_v5/build_app_close_candidates_v5.py',ROOT/'source_resume_runtime_v2/resume_runtime_contracts_v3.py',
      ROOT/'discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py',ROOT/'discovery/sdk_app_launcher_actual_v6/app_launcher.py',
      ROOT/'discovery/sdk_warp_buffer_appclose_v3/app/exts_0_simulation_app.py',ROOT/'reports/A1_V5_CLOSED_TIMESTAMP_APPCLOSE_DIAGNOSIS_V1.json']
    put('AUDIT_INPUTS_SHA256_V6.json',dict(kind='BOUNDED_SOURCE_AND_SMALL_CLOSED_DIAGNOSIS_ONLY',files=[record(p) for p in sources],old_V5=old5,old_eval=oldeval))
    alias=json.loads((B/'CPU_ALIAS_TEST_RESULTS_V6.json').read_text(encoding='utf-8'))
    gates=json.loads((S/'CPU_TEST_RESULTS_V5.json').read_text(encoding='utf-8'))
    assert (alias['tests'],gates['tests'])==(16,64)
    for result in (alias,gates):assert result['passed'] is True and result['failures']==result['errors']==0
    oldtree=ast.parse(sources[0].read_bytes());newtree=ast.parse((B/'app_close_semantics_v6.py').read_bytes())
    changed={'_AppPin','_pin_original_app_close','_validate_binding_receipt'};same=[]
    for node in oldtree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name not in changed:
            other=next(n for n in newtree.body if isinstance(n,type(node)) and n.name==node.name)
            assert ast.dump(node,include_attributes=False)==ast.dump(other,include_attributes=False),node.name
            same.append(node.name)
    assert len(same)==15
    own_sources=list(B.glob('*.py'))+list(S.glob('*.py'))
    for path in own_sources:compile(path.read_text(encoding='utf-8'),str(path),'exec')
    doc=(B/'APP_CLOSE_ALIAS_COMPAT_V6.md').read_text(encoding='utf-8');links=re.findall(r'\]\(<([^>]+)>\)',doc)
    for link in links:
        filename,_,fragment=link.partition('#');path=Path(filename);assert path.is_file(),link
        if fragment:
            count=len(path.read_text(encoding='utf-8').splitlines());assert all(0<int(n)<=count for n in re.findall(r'\d+',fragment)),link
    scratch=[]
    for path in sorted(S.rglob('*')):
        if path.is_file():
            assert path.resolve().is_relative_to(S)
            item=record(path);item['path']=str(path.relative_to(B));scratch.append(item)
    tree_SHA=hashlib.sha256(json.dumps(scratch,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    # Compact own-fixture digest: recomputable here, not hundreds of KB raw logs.
    put('OWN_SCRATCH_DIGEST_V6.json',dict(kind='ONLY_NEW_CPU_FAKE_FILES_NO_MODEL_OR_SDK',files=len(scratch),bytes=sum(x['bytes'] for x in scratch),tree_SHA256=tree_SHA,algorithm='SHA256 of sorted full record(name,relative path,bytes,SHA256) list encoded json sort_keys=True separators=comma/colon',selected_source_and_result_files=[record(p) for p in sorted(S.glob('*')) if p.is_file()]))
    verification=dict(kind='V6_ALIAS_COMPAT_SOURCE_CPU_NOT_NATIVE',latest_tests=80,alias_tests=16,reused_behavioral_tests=64,passed=True,
      actual_CPU_fake_child_scenarios_per_gate_run=6,total_own_CPU_fake_child_executions_in_two_attempts=12,
      excluded_old_worker_source_AST_tests=9,direct_unchanged_gate_function_or_class_AST=same,
      old_V5_sealed_entries_unchanged=old5['unchanged_sealed_entries'],old_eval_sealed_entries_unchanged=oldeval['unchanged_sealed_entries'],
      bounded_source_inputs_hashed=len(sources),compiled_without_import=len(own_sources),valid_report_links_and_line_ranges=len(links),
      logical_ABI_copy_same_bytes=True,new_helper=target,SDK_Torch_GPU_PT_native_account_Git_or_training_operations=0,
      past_actual_app_module=None,new_native_app_binding=None)
    put('SOURCE_REVIEW_VERIFICATION_V6.json',verification)
    files=[record(p) for p in sorted(B.glob('*')) if p.is_file()]
    bundle=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    put('DELIVERABLES_SHA256_V6.json',dict(kind='NEW_ONLY_V6_PUBLISHED_APP_EXPORT_ALIAS_COMPAT',created_at_UTC=datetime.now(timezone.utc).isoformat(),files=files,bundle_SHA256=bundle,self_excluded=True,scratch_digest=tree_SHA))
    print(json.dumps(dict(verification=verification,seal=record(B/'DELIVERABLES_SHA256_V6.json'),bundle_SHA256=bundle),ensure_ascii=False))

if __name__=='__main__':main()
