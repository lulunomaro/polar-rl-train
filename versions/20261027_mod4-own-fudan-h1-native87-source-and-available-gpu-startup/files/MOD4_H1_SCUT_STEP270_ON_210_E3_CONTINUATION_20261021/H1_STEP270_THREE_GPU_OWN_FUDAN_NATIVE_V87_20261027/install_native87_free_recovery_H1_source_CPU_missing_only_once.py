"""Install only unused free c27 H1 slot; retain H1 CPU proof and busy e2 untouched."""
from pathlib import Path
import sys,importlib.util,json,hashlib,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
from native87_install_activate_support_v1 import ROOTS,REMOTE_ACCOUNT,REMOTE_INSTALL,REMOTE_VERIFY,REMOTE_CPU

def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
    q=json.loads((R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json').read_bytes())
    old=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/reports'
    typed_path=old/'THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json';typed=json.loads(typed_path.read_bytes());assert typed['passed'] and typed['original_canonical_cost_settled'] and not typed['errors']
    closure=dict(passed=True,allout_and_cost_settled=True,typed_report_SHA=hashlib.sha256(typed_path.read_bytes()).hexdigest())
    assert json.loads((R/'H1_NATIVE87_MISSING_ACTUAL_CPU_IMMUTABLE_PROOF_RETURNED_ACTUAL.json').read_bytes())['passed']
    boundary=json.loads((R/'NATIVE87_DUAL72_ACTUAL_GPU_RESOURCE_BOUNDARY_RETURNED_ACTUAL.json').read_bytes())
    assert boundary['resources']['new_target_roots']['recovery']['exists'] is False
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('native87_existing_memory_only_free_slot',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
    secret=memory.recover();client=None
    try:
        key='recovery';s=q['specs'][key];local=Path(q['payloads'][key]);manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
        assert hashlib.sha256((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']
        client=d.connect72(secret);account=d.code(client,d.PY72,REMOTE_ACCOUNT,{},timeout=45)
        copied=d.code(client,d.PY72,REMOTE_INSTALL,dict(key=key,root=ROOTS[key],expected_roots=ROOTS,spec=s,manifest=manifest,source=q['sources'][key],previous86_close=closure,current_account=account),timeout=120)
        put('RECOVERY_NATIVE87_FREE_SLOT_EXACT_COPY_RESOURCE_ACTUAL.json',copied)
        sf=client.open_sftp();sf.get_channel().settimeout(90)
        try:
            for row in copied['need_upload']:sf.put(str(local/row['relative']),ROOTS[key]+'/'+row['relative'])
            sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),ROOTS[key]+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
        finally:sf.close()
        verified=d.code(client,d.PY72,REMOTE_VERIFY,dict(root=ROOTS[key],spec=s,manifest=manifest),timeout=240)
        put('RECOVERY_NATIVE87_FREE_SLOT_FULLSHA_AFTER_PAYLOAD_ACTUAL.json',verified)
        actual=d.code(client,d.PY72,REMOTE_CPU,dict(root=ROOTS[key],spec=s),timeout=900)
        put('RECOVERY_NATIVE87_FREE_SLOT_TARGET_SOURCE_SDK_CPU_RAW_ACTUAL.json',dict(actual_finite_returned=True,**actual))
        assert actual['passed'],actual.get('original_error')
        proof=d.code(client,d.PY72,"from pathlib import Path;import hashlib,json;B=Path(v['root']);p=B/'job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json';x=json.loads(p.read_bytes());assert x['not_synthetic'] and x['actual_CPU_waited_EXIT0'] and x['manifest_SHA']==v['manifest_SHA'];print(json.dumps(dict(SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=x)))",dict(root=ROOTS[key],manifest_SHA=s['manifest_SHA']),timeout=45)
        put('RECOVERY_NATIVE87_MISSING_ONLY_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,root=ROOTS[key],**actual,preinstalled_CPU_proof_SHA=proof['SHA'],preinstalled_CPU_proof=proof['value'],spec_with_preinstalled_CPU_proof=dict(s,preinstalled_CPU_proof_SHA=proof['SHA']),other_H1_CPU_not_reexecuted=True,busy_e2_untouched=True,no_owner_GO_or_fee=True))
        print(json.dumps(dict(actual_finite_returned=True,recovery_H1_actual_source_CPU_passed=True,H1_source_proof_retained=True,no_owner_GO_or_fee=True)))
    finally:
        secret=None
        if client:client.close()

if __name__=='__main__':
    try:main()
    except BaseException:
        put('RECOVERY_NATIVE87_MISSING_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_CPU_rearm_or_GO=True));raise
