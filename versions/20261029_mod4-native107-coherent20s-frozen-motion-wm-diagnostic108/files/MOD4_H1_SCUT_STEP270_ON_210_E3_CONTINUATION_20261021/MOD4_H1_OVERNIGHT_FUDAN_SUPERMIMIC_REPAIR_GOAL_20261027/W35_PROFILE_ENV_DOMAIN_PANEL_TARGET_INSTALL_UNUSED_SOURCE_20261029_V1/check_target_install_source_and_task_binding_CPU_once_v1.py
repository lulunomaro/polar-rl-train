"""Bounded stdlib-only source/task fixture; remote CODE is never invoked."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback

D=Path(__file__).resolve().parent


def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)


def main():
    config=json.loads((D/'LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json').read_bytes())
    manifest_path=D/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json'
    assert H(manifest_path)==config['input_manifest_SHA']
    manifest=json.loads(manifest_path.read_bytes())
    assert len(manifest['files'])==469
    paths=[r['relative'] for r in manifest['files']]
    assert len(set(paths))==469 and 'FROZEN_CASE_TASK_TEMPLATE.json' not in paths
    assert 'FROZEN_CASE_TASK.json' not in paths and config['static_task_input'] in paths
    source_rows=[]
    for p in sorted(D.glob('*.py')):
        raw=p.read_bytes();tree=ast.parse(raw,filename=str(p));source_rows.append(dict(name=p.name,SHA=hashlib.sha256(raw).hexdigest(),AST_passed=True))
    entry_tree=ast.parse((D/'install_admit_detach_W35_profile_domain_panel210_UNUSED_once_v1.py').read_bytes())
    dcalls={ast.unparse(n.func) for n in ast.walk(entry_tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='d'}
    assert dcalls=={'d.connect72','d.code'}
    copy_raw=(D/'COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py').read_bytes()
    assert hashlib.sha256(copy_raw).hexdigest()==config['copy_CODE_SHA']
    proof=json.loads((D/'SOURCE_DERIVATION_EXACT_INVERSE_AND_METADATA_MAPPING_ACTUAL.json').read_bytes())
    assert proof['AUTH_PRE_exact_original_bytes'] and proof['worker_inverse_bytes_exact'] and proof['remote_RUN_inverse_bytes_exact']
    block=next(x['new'] for x in proof['remote_RUN_exact_changes'] if x['old'].startswith('task=dict(kind='))
    fixture=D/'reports/CPU_SOURCE_TASK_BINDING_FIXTURE'
    fixture.mkdir()
    # New tiny source/JSON fixture copies only, no policy/model/NPZ/USD inputs.
    names=[config['static_task_input'],config['worker'],'w35_profile_env_domain_panel_v1.py']
    for name in names:
        row=next(x for x in manifest['files'] if x['relative']==name)
        p=Path(row['local_path']);raw=p.read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
        with (fixture/name).open('xb') as f:f.write(raw)
    before={name:H(fixture/name) for name in names}
    base=dict(static_task_input=config['static_task_input'],worker=config['worker'],expected=copy.deepcopy(config['expected']),
              authority=dict(passed=True,passed_readonly_original72_finite_authority=True,synthetic_fixture_not_Canonical=True),python='/synthetic/never/executed/python')
    variants=[('exact_static_source_and_synthetic_authority',{},True),
              ('wrong_model_SHA',{'expected_model_SHA':'0'*64},False),
              ('source_readonly_authority_false',{'readonly_authority':False},False),
              ('authority_result_false',{'authority_passed':False},False),
              ('wrong_worker_source_file',{'worker':'w35_profile_env_domain_panel_v1.py'},False)]
    results=[]
    for name,delta,expected_pass in variants:
        v=copy.deepcopy(base)
        if 'expected_model_SHA' in delta:v['expected']['model_SHA']=delta['expected_model_SHA']
        if 'readonly_authority' in delta:v['authority']['passed_readonly_original72_finite_authority']=delta['readonly_authority']
        if 'authority_passed' in delta:v['authority']['passed']=delta['authority_passed']
        if 'worker' in delta:v['worker']=delta['worker']
        ns=dict(J=fixture,v=v,json=json,H=H)
        try:
            exec(compile(block,'synthetic_source_Task_block_only','exec'),ns)
            passed=True;error=None
        except AssertionError as e:passed=False;error=repr(e)
        assert passed==expected_pass,(name,passed,expected_pass)
        results.append(dict(name=name,expected_accept=expected_pass,actual_accept=passed,original_expected_negative_exception=error))
    assert before=={name:H(fixture/name) for name in names}
    assert not (fixture/'FROZEN_CASE_TASK_TEMPLATE.json').exists()
    static=json.loads((D/config['static_task_input']).read_bytes())
    assert all(static[k] is False for k in ('actual_source210_SDK_admission_passed','actual_private_GPU_EX_held_by_parent','canonical72_known_owner_readonly_passed')) and static['known72_readonly_authority'] is None
    worker_ast=ast.parse((D/config['worker']).read_bytes())
    text=(D/config['worker']).read_text(encoding='utf-8')
    assert "panel_delta=={'legs':192,'wheels':192}" in text and 'ACTUAL_NATIVE24_W35_PROFILE_PANEL_CLOCK_QUEUE_ACTUAL.json' in text
    assert "real._integrated_contact.tick-tick==8" in text and "real._feedback_100hz_tick-fb==2" in text
    put('SOURCE_AST_AND_SYNTHETIC_TASK_BINDING_ACTUAL.json',dict(epoch=time.time(),passed=True,AST_rows=source_rows,
        Task_block_fixture_results=results,static_source_files_unchanged=True,no_dynamic_grant_written=True,
        known72_pending_not_filled=True,original_AUTH_PRE_literal_unchanged=True,
        old_model_CPU_load_count=0,remote_GPU_SDK_actor_or_Canonical_IO=False,
        new_native24_receipt_requires_actual_group192_and_trace24=True,
        actual_target_admission_and_new_model_GPU_fullrestore_still_pending=True))
    print(json.dumps(dict(passed=True,AST_files=len(source_rows),Task_fixture_cases=len(results),old_model_CPU_load_count=0,remote=False)))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('reports/ORIGINAL_LOCAL_SOURCE_BINDING_CHECK_ERROR_'+str(time.time_ns())+'.json',dict(passed=False,error=traceback.format_exc(),remote=False,model_read=False))
        raise
