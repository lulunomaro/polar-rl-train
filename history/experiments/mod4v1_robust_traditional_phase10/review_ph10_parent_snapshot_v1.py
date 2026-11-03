"""Fresh archive-snapshot bookkeeping: no original raw, old tests, model or Git calls."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
REPO=Path(r'F:\RMPOLAR-RL\repo-lqr-robust')
S=REPO/'history/experiments/mod4v1_robust_traditional_phase10_SOURCE_PREPARATION'
O=R/'PH10_PARENT_SNAPSHOT_REVIEW_V1.json'
READ=[]
def get(p):
    raw=p.read_bytes();assert len(raw)<1024*1024
    READ.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    return json.loads(raw),READ[-1]
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def main():
    assert not O.exists(),'Existing parent snapshot receipt: inspect, do not replay'
    expected,_=get(R/'PH10_PARENT_CLOSED_EXPECTED_FACTS_V1.json')
    archived={}
    for rec in expected['inputs']:
        p=Path(rec['path'])
        if p.is_relative_to(R):rel=p.relative_to(R)
        else:
            assert p.is_relative_to(REPO)
            rel=Path('@repo')/p.relative_to(REPO)
        x,rr=get(S/'snapshot'/rel)
        assert rr['SHA']==rec['SHA'] and rr['bytes']==rec['bytes'],str(rel)
        archived[p.name if p.name!='result.json' else p.parent.name]=x
    error=archived['ERROR.json']
    cases=[archived[k] for k in ('startup_front065_coupled_v2_nominal1','startup_front065_tracking_v3a_nominal1','startup_front065_tracking_v3b_nominal1')]
    assert all(x['complete'] is False and x['startup_stand_original_v1_gate'] is False and x['first_BALANCE_command_s'] is None for x in cases)
    controls=error['controls']+sum(x['controls'] for x in cases)
    phy=error['physics_steps']+sum(x['physics_steps'] for x in cases)
    assert (controls,phy)==(2101,42020)
    passive=archived['BATCH_RESULT.json'];assert sum(x['physics_steps'] for x in passive['rows'])==12000
    comp=archived['COMPILE_RESULT_V6_01.json'];assert comp['C_compile_count']==1 and comp['ASM_compile_count']==0 and comp['first_object_gate']['pass_gate'] is False
    recon,_=get(S/'CASE_RECONCILIATION.json');cons,_=get(S/'FINAL_CONSISTENCY_RECEIPT.json')
    assert recon['controlled_actual_controls']==controls and recon['controlled_actual_physics_steps']==phy and recon['passive_model_steps']==12000
    assert cons['summary']['source_entries']==3048 and cons['summary']['new_text_copies']==1603 and cons['summary']['text_SHA_pairs_verified']==2625
    assert cons['summary']['source_changes']==cons['summary']['redactions']==0 and cons['record_stage_commit_tag_push_calls']==0
    # Existing copy receipts bind exact member+size+CRC+identity without opening libs.
    supplement,_=get(S/'snapshot/MOD4_DEPLOYMENT_PORT_V1/SUPPLEMENT_RECEIPT.json')
    closure,_=get(S/'snapshot/MOD4_DEPLOYMENT_PORT_V1/BUILD_CLOSURE_FINAL.json')
    binding=[]
    for name,size,digest,crc in [('AHRS.lib',34756,'ace29e114d892a48a473cc3421f0c22d16841c1316313746650b8f441749413a','396f45e3'),
        ('arm_cortexM4lf_math.lib',13294064,'ba416f23efb992105c36b67d9002d8142e38877d1010c0e0a1d0f74b83325ab7','e439b083')]:
        member='StandardRobotpp-balance1/components/algorithm/'+name
        a=[x for x in walk(supplement) if x.get('member')==member and x.get('raw_SHA')==digest and x.get('bytes')==size and x.get('copied_original_bytes') is True]
        b=[x for x in walk(closure) if x.get('member')==member and x.get('raw_SHA')==digest and x.get('provided') is True]
        assert len(a)==len(b)==1 and a[0]['CRC32']==b[0]['CRC32']==crc
        binding.append(dict(derived_relative='MOD4_DEPLOYMENT_PORT_V1/derived/'+member,member=member,bytes=size,raw_producer_SHA=digest,CRC32=crc,
            provenance='existing supplement copied_original_bytes + exact closure project member, both archived small receipts',
            current_payload_rehashed=False,current_payload_or_ABI_newly_validated=False))
    result=dict(status='PASS_PARENT_INDEPENDENT_SNAPSHOT_NUMERICS_AND_EXISTING_COPY_RECEIPT_BINDINGS',
        archive_snapshot_7_input_SHA_match_prior_parent_receipt=True,controls=controls,controlled_steps=phy,controlled_formal_results=3,software_error_without_result_backfill=1,
        controlled_full_duration_completions=0,original_formal_passes=0,passive_steps_separate=12000,
        V6_logical_main_compile1_original_gate_false=True,PH10_entry_summary=cons['summary'],
        additional_existing_library_copy_producer_bindings=binding,
        original_sealed_manifest_and_unknown4_kept_unchanged=True,
        clarification='Two libs have bound existing producer copy claims shown here; no new current payload hash or ABI claim. Original immutable capture419known/4unknown is retained as historical collector coverage, not silently revised.',
        inputs=READ,original_raw_lib_ZIP_USD_obj_model_FK_PHY_oldQA_Git_calls=0,active_geometry_V4_C7_C8_C9_C10_not_in_PH10=True,
        parent_review_only_not_record_commit_push_permission=True)
    with O.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','PH10_entry_summary','additional_existing_library_copy_producer_bindings')},indent=2))
if __name__=='__main__':main()
