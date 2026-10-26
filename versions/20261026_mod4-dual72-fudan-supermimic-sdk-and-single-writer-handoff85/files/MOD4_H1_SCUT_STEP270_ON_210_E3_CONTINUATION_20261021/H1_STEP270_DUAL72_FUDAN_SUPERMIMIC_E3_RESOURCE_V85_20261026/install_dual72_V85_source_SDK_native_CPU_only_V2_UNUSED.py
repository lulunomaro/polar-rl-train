"""UNEXECUTED finite72-only installer/CPU reader. Never210/owner/canonical/GO.

Actual resource/source checks use target72 and historical qualified83B evidence;
their pass is explicitly not a pass of the currently unreachable live account.
"""
from pathlib import Path
import importlib.util
import json
import sys
import time
import traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))


def put(name,value):
    with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)


def main():
    q=json.loads((R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())
    assert q['passed'] and set(q['specs'])=={'e2','recovery'} and q['deferred_experts']==['h1']
    assert q['preparation_scope']=='SOURCE_PREPARED_PAIR_NOT_LIVE_ACCOUNT_ADMITTED'
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    from dual72_V85_resource_install_source_v1 import CODE
    original_code=d.code;expected="import runpy,sys;sys.argv=['target_two50_source_sdk_cpu_review.py',v['root']];runpy.run_path(v['root']+'/target_two50_source_sdk_cpu_review.py',run_name='__main__')"
    proof=json.loads((N/'payloads/e2/CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes())
    def code(client,py,source,args,timeout=90):
        if source==d.INSTALL:
            assert args['spec']['key'] in ('e2','recovery')
            source=CODE;args=dict(args,closedproof=proof)
        if source==expected:
            if args['root']==q['roots']['e2']:
                source="from pathlib import Path;import contextlib,io,json,os,runpy,sys;os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(v['root']);sys.path.insert(0,str(B));buffer=io.StringIO()\nwith contextlib.redirect_stdout(buffer):\n sys.argv=['target_H1_step270_closed_source_sdk_cpu_review_v1.py',str(B)];runpy.run_path(str(B/'target_H1_step270_closed_source_sdk_cpu_review_v1.py'),run_name='__main__')\n sys.argv=[str(B/'test_native_h1_fudan_reference_CPU_v84.py')];runpy.run_path(sys.argv[0],run_name='__main__')\ncpu=json.loads((B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').read_bytes());cpu['new_native_H1_method_CPU']=json.loads((B/'reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V84_ACTUAL.json').read_bytes());print(json.dumps(cpu))"
            else:
                assert args['root']==q['roots']['recovery'];source=source.replace('import runpy,sys;','import runpy,sys;sys.path.insert(0,v[\'root\']);',1)
        guard="from pathlib import Path;import json,sys;sys.path.insert(0,v['root']);from original_account_policy50_source_CPU import load;print(json.dumps(load(v['spec'],Path(v['root']))))"
        if source==guard and args['root']==q['roots']['e2']:
            source=source.replace('from original_account_policy50_source_CPU import load','from closed_production_continuation_CPU_v2 import load',1)
        return original_code(client,py,source,args,timeout=timeout)
    d.code=code;d.put=put
    put('V85_ONLY72_INSTALL_SOURCE_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),no210_route=True,no_owner_or_GO=True,original_live_account_checked=False))
    module_spec=importlib.util.spec_from_file_location('existing_hidden72_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(memory)
    secret=memory.recover();client=None
    try:
        client=d.connect72(secret);secret=None
        for key in ('recovery','e2'):
            d.upload(client,d.PY72,key,q)
        validation={}
        for key in ('e2','recovery'):
            validation[key]=d.code(client,d.PY72,"from pathlib import Path;import json,sys;sys.path.insert(0,v['root']);from three_slot_common_v1 import valid_ready\nB=Path(v['root']);s=v['spec']\nif s['key']=='recovery':\n from original_account_policy50_source_CPU import load\nelse:\n from closed_production_continuation_CPU_v2 import load\nr=load(s,B);row=dict(key=s['key'],phase='ready',closed_source_CPU=r,manifest_SHA=s['manifest_SHA'],original_error=False);assert valid_ready(row,s);print(json.dumps(dict(target_source_valid_ready_CPU=True,value=r,original_live_account_checked=False,no_owner_or_GO=True)))",dict(root=q['roots'][key],spec=q['specs'][key]),timeout=90)
        put('V85_ONLY72_INSTALLED_SOURCE_SDK_NATIVE_CPU_FINITE_RETURNED_ACTUAL.json',dict(
            epoch=time.time(),actual_finite_returned=True,target_source_CPU_passed=True,validation=validation,
            slots=['e2','recovery'],deferred=['h1'],roots=q['roots'],specs=q['specs'],
            original_live_account_checked=False,original_canonical_read_or_write=False,
            owner_launched=False,node_launched=False,GO=False,no_GPU_environment_or_policy_training=True,
            source_qualification_kind_revision_V84_preserved=True))
        print(json.dumps(dict(target_source_CPU_passed=True,original_live_account_checked=False,no_owner_or_GO=True)))
    finally:
        secret=None
        if client:client.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        put('V85_ONLY72_INSTALL_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(
            epoch=time.time(),error=traceback.format_exc(),no_auto_retry_same_namespace=True,
            no210_route_or_live_account_check=True,no_owner_or_GO=True));raise
