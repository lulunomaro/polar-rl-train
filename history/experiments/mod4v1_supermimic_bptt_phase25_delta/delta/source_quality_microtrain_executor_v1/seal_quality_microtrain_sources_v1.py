"""One-shot SOURCE seal; never execute owner/worker or repeat tests."""
from pathlib import Path
import ast,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
SEALED=HERE.parent/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source'
def H(raw):return hashlib.sha256(raw).hexdigest()
def info(p):
    raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),SHA256=H(raw))
def put(name,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    with(HERE/name).open('xb')as stream:stream.write(raw)
def load(name):
    spec=importlib.util.spec_from_file_location('SOURCE_SEAL_'+name,HERE/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    outputs=('QUALITY_MICROTRAIN_PROTECTED_AST_PROOF_V1.json','QUALITY_MICROTRAIN_SOURCE_BINDINGS_V1.json','QUALITY_MICROTRAIN_SOURCE_DELIVERY_V1.json','SHA256_QUALITY_MICROTRAIN_V1.txt')
    assert not any((HERE/n).exists()for n in outputs),'source seal exists; never overwrite'
    for p in HERE.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
    for p in HERE.glob('*.json'):json.loads(p.read_bytes())
    test=load('test_quality_microtrain_stdlib_v1');builder=load('build_quality_microtrain_sources_v1')
    owner,worker=builder.sources()
    assert (HERE/'owner_quality_microtrain_v1.py').read_text(encoding='utf-8')==owner
    assert (HERE/'worker_quality_microtrain_v1.py').read_text(encoding='utf-8')==worker
    oldowner=test.source('supermimic_original_owner_shared_app_close_candidate_v5.py');oldworker=test.source('worker_supermimic_bptt_app_close_candidate_v5.py')
    proof=dict(kind='QUALITY_MICROTRAIN_SOURCE_AST_NOT_RUNTIME_PROOF_V1',source_only=True,old_original_files={name:info(SEALED/name)for name in builder.PINS},
        owner_unchanged_functions={},owner_and_worker_complete_normalized_main={},
        allowed_owner_main_changes=['pure requested-plan binding','pure task/GO microtrain metadata binding','truthful target metadata and requested/deferred sidefile fields'],
        allowed_worker_main_changes=['legacy cumulative-target predicate replaced by finite-segment validator','decoded payload lineage check before unchanged full loader','post-load actual counter baseline and cumulative train target','segment metadata only in startup/checkpoint/FINAL'],
        original_resource_charge_and_close_operations_not_replaced=True,actual_native_or_Torch_software_validation=None)
    for name in ('require','gpu','account','environment','admit','plan_protocol'):
        a=test.dump(test.function(oldowner,name));b=test.dump(test.function(owner,name));assert a==b
        proof['owner_unchanged_functions'][name]=dict(equal=True,AST_SHA256=H(a.encode()))
    for label,a,b in(('owner',oldowner,owner),('worker',oldworker,worker)):
        x=test.dump(test.function(a,'main'));y=test.dump(test.Normalize().visit(test.function(b,'main')));assert x==y
        proof['owner_and_worker_complete_normalized_main'][label]=dict(equal=True,AST_SHA256=H(x.encode()))
    proof['worker_entry_error_boundary_exact']=test.dump(test.function(oldworker,'worker_entry_v2'))==test.dump(test.function(worker,'worker_entry_v2'));assert proof['worker_entry_error_boundary_exact']
    required={'ctx_reward_full_resume_candidate_v2.py':'8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac',
        'resume_runtime_contracts_v3.py':'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
        'app_close_semantics_v6.py':'3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39',
        'three_slot_common_v1.py':'eaf6aa1a06d2a49570eff54af5447395210c6de9f3a9c43d566d1adad4e53044',
        'native_supermimic_bridge.py':'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'}
    proof['unchanged_full_dependencies']={}
    for name,h in required.items():
        p=SEALED/name;observed=info(p);assert observed['SHA256']==h;proof['unchanged_full_dependencies'][name]=observed
    result=json.loads((HERE/'TEST_RESULTS_QUALITY_MICROTRAIN_STDLIB_V1.json').read_bytes())
    assert result['passed']is True and result['tests']==20 and result['errors']==result['failures']==0 and result['Torch_imported']is False
    put(outputs[0],proof)
    bindings=dict(kind='QUALITY_MICROTRAIN_NEW_SOURCE_BINDINGS_NOT_A_STAGER_V1',requires_complete_original_V6_layout=True,not_for_existing_or_active_roots=True,
        actual_training_implemented=False,actual_training_enabled=False,
        entries=[dict(**info(HERE/'owner_quality_microtrain_v1.py'),installed_aliases=['owner_quality_microtrain_v1.py']),
            dict(**info(HERE/'worker_quality_microtrain_v1.py'),installed_aliases=['worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py']),
            dict(**info(HERE/'quality_microtrain_contracts_v1.py'),installed_aliases=['quality_microtrain_contracts_v1.py','worker_sources/quality_microtrain_contracts_v1.py'])],
        transitive_dependency_notes=['retain full existing V6 owner/worker/libs/vendor/assets/role metadata dependencies; no AST slicing',
            'retain complete AppV6 under logical app_close_semantics_v5.py AND full resume_runtime_contracts_v3.py in original import locations',
            'no changes to original single C/authority dependencies or resource admission; this file installs or dispatches nothing'])
    put(outputs[1],bindings)
    files=['quality_microtrain_contracts_v1.py','owner_quality_microtrain_v1.py','worker_quality_microtrain_v1.py','build_quality_microtrain_sources_v1.py',
        'test_quality_microtrain_stdlib_v1.py','seal_quality_microtrain_sources_v1.py','QUALITY_MICROTRAIN_FIELDS_CONTRACT_V1.json','QUALITY_MICROTRAIN_EXECUTOR_V1.md',
        'QUALITY_MICROTRAIN_WHITELIST_DIFF_V1.patch','TEST_RESULTS_QUALITY_MICROTRAIN_STDLIB_V1.json',outputs[0],outputs[1]]
    delivery=dict(kind='QUALITY_MICROTRAIN_SOURCE_ONLY_DELIVERY_V1',status=test.q.SOURCE_ONLY_STATUS,files=[info(HERE/n)for n in files],tests=result,
        actual_new_training_or_remote_dispatch=0,actual_new_tensor_full_resume_software_validation=None,skill_pass_rate=None,quality_decision='future executing parent from actual feedback; no automatic enable')
    put(outputs[2],delivery);files.append(outputs[2])
    with(HERE/outputs[3]).open('x',encoding='utf-8',newline='\n')as stream:
        for name in files:
            row=info(HERE/name);stream.write(row['SHA256']+'  '+str(row['bytes'])+'  '+row['path']+'\n')
    print(json.dumps(dict(core=bindings['entries'],proof=info(HERE/outputs[0]),delivery=info(HERE/outputs[2]),tests=result),indent=2))
if __name__=='__main__':main()
