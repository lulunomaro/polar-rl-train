"""Assemble receipts/archive by reading saved artifacts; never rerun solver/tests."""
from pathlib import Path
import hashlib,json,struct,zipfile
HERE=Path(__file__).resolve().parent
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(n,v):
    with(HERE/n).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def load(n):return json.loads((HERE/n).read_bytes())
def fbits(x):return struct.pack('<d',float(x))
def differences(a,b,path=''):
    if isinstance(a,dict):
        assert a.keys()==b.keys();return sum((differences(a[k],b[k],path+'.'+k)for k in a),[])
    if isinstance(a,list):
        assert len(a)==len(b);return sum((differences(x,y,path+'['+str(i)+']')for i,(x,y)in enumerate(zip(a,b))),[])
    if isinstance(a,(int,float))and isinstance(b,(int,float)):
        same=(fbits(a)==fbits(b))if(isinstance(a,float)or isinstance(b,float))else a==b
        return []if same else[dict(path=path.lstrip('.'),before_bits='0x%016x'%struct.unpack('<Q',fbits(a))[0],after_bits='0x%016x'%struct.unpack('<Q',fbits(b))[0])]
    assert a==b;return []
def main():
    first=load('HOST_BUILD_01.json');second=load('HOST_BUILD_02.json');comp1=load('COMPARISON_01.json');comp2=load('COMPARISON_02.json');arm=load('ARM_BUILD_01.json');objects=load('OBJECT_SUMMARY.json');prereg=load('PREREGISTRATION_RECEIPT.json')
    assert not first['success']and second['success']and arm['success']
    assert comp1['native_checks']==comp2['native_checks']==2290 and comp1['native_failures']==1 and comp2['native_failures']==0
    assert comp1['numerical_checks']==comp2['numerical_checks']==38508 and comp1['numerical_failures']==3 and comp2['numerical_failures']==0 and comp2['CPP_pass']
    changed=[n for n in first['sources']if first['sources'][n]!=second['sources'][n]];assert changed==['pa1_allocator.c']
    for attempt,record in [(1,first),(2,second)]:
        folder=HERE/f'host_attempt_{attempt:02d}'
        for n,h in record['sources'].items():assert sha(folder/n)==h
        for command in record['commands']:
            if 'artifact'in command:assert command['artifact_exists']and sha(command['artifact'])==command['sha256']and Path(command['artifact']).stat().st_size==command['bytes']
        for n,h in second['sources'].items():assert sha(HERE/n)==h
    old=(HERE/'host_attempt_01/pa1_allocator.c').read_bytes();new=(HERE/'pa1_allocator.c').read_bytes()
    first_order=b'  if(s==0.||a==b) { w->rounded_tau[i]=a; w->torque[i]=point(a); continue; }\n  if(s==1.) { w->rounded_tau[i]=b; w->torque[i]=point(b); continue; }\n'
    second_order=b'  /* Endpoint priority preserves requested -0.0 bits at s==1; numeric\n     equality a==b alone does not imply equal signed-zero representations. */\n  if(s==1.) { w->rounded_tau[i]=b; w->torque[i]=point(b); continue; }\n  if(s==0.||a==b) { w->rounded_tau[i]=a; w->torque[i]=point(a); continue; }\n'
    assert new.count(second_order)==1 and new.replace(second_order,first_order,1)==old
    raw1=[json.loads(s)for s in(HERE/'C_RUNS_01.jsonl').read_bytes().splitlines()];raw2=[json.loads(s)for s in(HERE/'C_RUNS_02.jsonl').read_bytes().splitlines()]
    changes=[]
    for index,(a,b)in enumerate(zip(raw1,raw2)):
        for item in differences(a,b):changes.append(dict(row=index-1,case=a.get('name','environment'),**item))
    assert len(raw1)==len(raw2)==220 and len(changes)==3
    assert {r['path']for r in changes}=={'tau[0]','tau[2]','tau[4]'}and all(r['case']=='signed_negative_zero_full_endpoint'and r['before_bits']=='0x0000000000000000'and r['after_bits']=='0x8000000000000000'for r in changes)
    assert sha(HERE/'NUMERICAL_BUDGET.json')==prereg['budget_SHA']and sha(HERE/'MODEL_CONTRACT.json')==prereg['contract_SHA']
    assert comp1['case_SHA']==comp2['case_SHA']==sha(HERE/'CASES.json')and comp1['reference_SHA']==comp2['reference_SHA']==sha(HERE/'REFERENCE.json')
    for i,comp in [(1,comp1),(2,comp2)]:assert sha(HERE/f'C_RUNS_{i:02d}.jsonl')==comp['raw_SHA']
    dump('ANALYSIS_RECEIPT.json',dict(kind='READ_ONLY_SAVED_EVIDENCE_VERIFICATION_NO_RERUN',only_changed_build_input=changed,exact_source_reversal_restores_first=True,raw_numeric_bit_changes=changes,all_other_saved_raw_fields_bit_identical=True,original_first_numerical_failures=comp1['errors'],first_native_failure_retained=True,second_numerical_checks=comp2['numerical_checks'],second_native_checks=comp2['native_checks'],analyzer_SHA=sha(HERE/'analyze_pa1.py'),case_SHA=comp2['case_SHA'],reference_SHA=comp2['reference_SHA'],budget_SHA=prereg['budget_SHA'],physics_steps=0))
    dump('CORE_RECEIPT.json',dict(status='NEW_NATIVE_MATH_CORE_HOST_QUALIFIED_ARM_OBJECT_FACTS_SEPARATE',runtime_source_closure={n:sha(HERE/n)for n in ('pa1_allocator.c','pa1_allocator.h')},axes=6,arithmetic='binary64 RN gradual no-fast-math no-contraction with outward nextafter',bisections=40,host_sizeof=dict(context=488,workspace=672,result=464,input=608),default_real_calibration='UNBOUND_INVALID',model_contract_SHA=prereg['contract_SHA'],global_exact_optimum_claim=False,hardware_or_electrical_qualified=False,thermal_or_battery_qualified=False,balance_stability_qualified=False,driver_or_C3_enqueue_qualified=False,PH4_cutoff_excludes_component=True,PH5_and_later_pending=True))
    pe=[]
    exes=[dict(name=Path(c['artifact']).stem,path=c['artifact'],bytes=c['bytes'],sha256=c['sha256'])for c in second['commands']if 'artifact'in c and Path(c['artifact']).suffix=='.exe']
    assert len(exes)==3
    for entry in exes:
        p=Path(entry['path']);blob=p.read_bytes();offset=struct.unpack_from('<I',blob,0x3c)[0];assert blob[:2]==b'MZ'and blob[offset:offset+4]==b'PE\0\0'
        machine=struct.unpack_from('<H',blob,offset+4)[0];magic=struct.unpack_from('<H',blob,offset+24)[0];assert machine==0x14c and magic==0x10b and sha(p)==entry['sha256']
        pe.append(dict(**entry,machine='I386',optional_header='PE32'))
    dump('HOST_QUALIFICATION.json',dict(status='PASSED_FIXED_REVISION02_WITH_FAILED_REVISION01_RETAINED',cases=219,valid_cases=209,reserve_model_infeasible=7,reserve_arithmetic_uncertified=3,numerical_checks=38508,numerical_failures=0,native_checks=2290,native_failures=0,actual_CPP_extern_C_pass=True,logical_clock_cases=36,logical_clock_is_not_hardware_timing=True,well_conditioned_valid_cases=204,maximum_s_gap_all_valid=comp2['maximum_s_gap_all_valid'],maximum_affine_representation_error_Nm=comp2['maximum_affine_representation_error_Nm'],full_endpoint_cases=39,accepted_declared_model_violation_tolerance=0,executables=pe,failed_first_native_checks=2290,failed_first_native_failures=1,failed_first_endpoint_bit_checks=3,physics_steps=0,ARM_execution=0))
    names=['pa1_allocator.c','pa1_allocator.h','BUILD.txt','MODEL_CONTRACT.json','NUMERICAL_BUDGET.json']
    with zipfile.ZipFile(HERE/'pa1_source_bundle.zip','x',compression=zipfile.ZIP_DEFLATED)as z:
        for n in names:z.writestr(n,(HERE/n).read_bytes())
    with zipfile.ZipFile(HERE/'pa1_source_bundle.zip')as z:assert z.namelist()==names and all(hashlib.sha256(z.read(n)).hexdigest()==sha(HERE/n)for n in names)
    print(json.dumps(dict(source_revision_only=changed,raw_field_changes=changes,current_host_checks=38508+2290,current_HOST_CPP=True,ARM_objects=len(objects['objects']),source_bundle_SHA=sha(HERE/'pa1_source_bundle.zip'),no_test_or_compile_rerun=True),indent=2))
if __name__=='__main__':main()
