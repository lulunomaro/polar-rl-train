"""New R2 two-source admission; no old attempted CPU is rerun or reclassified."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
from native87_install_activate_support_v1 import REMOTE_ACCOUNT,REMOTE_INSTALL,REMOTE_VERIFY,REMOTE_CPU
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    prepared=R/'AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json';q=json.loads(prepared.read_bytes())
    assert set(q['specs'])=={'h1','recovery'} and q['deferred_experts']==['e2']
    sys.path.insert(0,str(N/q['controllers_relative']))
    from native87_available_two_schedule_v1 import validate_schedule
    from native87_protocol_v1 import native87_valid_ready
    validate_schedule(dict(experts=q['specs'],deferred_experts=['e2'],scheduling_authority='human_requested_available_experts',authority_generation='MOD4_SINGLE_WRITER72_20261026',resource_boundary_relative=q['resource_boundary_relative'],resource_boundary_SHA=q['resource_boundary_SHA']))
    old=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/reports';p=old/'THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json';v=json.loads(p.read_bytes());assert v['passed'] and v['original_canonical_cost_settled'] and not v['errors'];closure=dict(passed=True,allout_and_cost_settled=True,typed_report_SHA=hashlib.sha256(p.read_bytes()).hexdigest())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    sp=importlib.util.spec_from_file_location('native87R2_existing_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;results={};specs={}
    put('AVAILABLE_TWO_NATIVE87R2_INSTALL_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),fresh_roots=q['roots'],no_owner_GO_or_fee=True))
    try:
        for key in ('h1','recovery'):
            s=q['specs'][key];P=Path(q['payloads'][key]);manifest=json.loads((P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert hashlib.sha256((P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']
            c=route.connect() if key=='h1' else d.connect72(secret);python=route.PY if key=='h1' else d.PY72
            account=d.code(c,python,REMOTE_ACCOUNT,{},timeout=45) if key!='h1' else None
            copied=d.code(c,python,REMOTE_INSTALL,dict(key=key,root=q['roots'][key],expected_roots=q['roots'],spec=s,manifest=manifest,source=q['sources'][key],previous86_close=closure,current_account=account),timeout=120)
            put(key.upper()+'_NATIVE87R2_EXACT_COPY_RESOURCE_ACTUAL.json',copied)
            sf=c.open_sftp();sf.get_channel().settimeout(90)
            try:
                for row in copied['need_upload']:sf.put(str(P/row['relative']),q['roots'][key]+'/'+row['relative'])
                sf.put(str(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),q['roots'][key]+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
            finally:sf.close()
            verified=d.code(c,python,REMOTE_VERIFY,dict(root=q['roots'][key],spec=s,manifest=manifest),timeout=240)
            put(key.upper()+'_NATIVE87R2_FULLSHA_AFTER_PAYLOAD_ACTUAL.json',verified)
            actual=d.code(c,python,REMOTE_CPU,dict(root=q['roots'][key],spec=s),timeout=900)
            put(key.upper()+'_NATIVE87R2_TARGET_SOURCE_SDK_CPU_RAW_ACTUAL.json',dict(actual_finite_returned=True,**actual))
            assert actual['passed'],actual.get('original_error')
            proof=d.code(c,python,"from pathlib import Path;import hashlib,json;B=Path(v['root']);p=B/'job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json';x=json.loads(p.read_bytes());assert x['not_synthetic'] and x['actual_CPU_waited_EXIT0'] and x['manifest_SHA']==v['manifest_SHA'];print(json.dumps(dict(SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=x)))",dict(root=q['roots'][key],manifest_SHA=s['manifest_SHA']),timeout=45)
            actual.update(preinstalled_CPU_proof_SHA=proof['SHA'],preinstalled_CPU_proof=proof['value']);results[key]=actual;specs[key]=dict(s,preinstalled_CPU_proof_SHA=proof['SHA'])
            assert native87_valid_ready(dict(key=key,phase='ready',manifest_SHA=s['manifest_SHA'],closed_source_CPU=actual['ready_envelope'],original_error=False),s)
            put(key.upper()+'_NATIVE87R2_SOURCE_SDK_CPU_AND_PROOF_RETURNED_ACTUAL.json',dict(root=q['roots'][key],actual_finite_returned=True,**actual))
            c.close();c=None
        put('AVAILABLE_TWO_NATIVE87R2_ACTUAL_SOURCE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,prepared_source_report_SHA=hashlib.sha256(prepared.read_bytes()).hexdigest(),results=results,specs_with_preinstalled_CPU_proof=specs,actual_source_CPU_once_each_new_R2_root=True,old_attempts_preserved=True,no_owner_GO_or_fee=True))
        print(json.dumps(dict(actual_finite_returned=True,both_R2_actual_source_SDK_CPU_passed=True,no_owner_GO_or_fee=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('AVAILABLE_TWO_NATIVE87R2_INSTALL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_same_root_rearm_or_GO=True));raise
