"""Independent review of six already-copied small PH11 JSONs; no capture/replay/Git."""
from pathlib import Path
import hashlib,json,traceback
R=Path(__file__).resolve().parent
S=R.parent/'repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase11_SOURCE_PREPARATION/snapshot'
OUT=R/'PH11_PARENT_SNAPSHOT_NUMERIC_REVIEW_V1.json';ERR=R/'PH11_PARENT_SNAPSHOT_NUMERIC_REVIEW_V1_ERROR.json'
reads=[]
def read_json(p):
    p=p.resolve();assert p.is_file()and p.stat().st_size<2*1024*1024,str(p)
    raw=p.read_bytes();rec=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest());reads.append(rec)
    return json.loads(raw),rec
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def main():
    assert not OUT.exists()and not ERR.exists()
    expected,pin=read_json(R/'PH11_PARENT_CLOSED_EXPECTED_FACTS_V1.json')
    assert expected['status']=='PASS_PARENT_INDEPENDENT_SMALL_CLOSED_JSONS_NOT_CONTROLLER_QA'
    saved={};bindings=[]
    for old in expected['sources']:
        rel=Path(old['path']).resolve().relative_to(R.resolve());p=S/rel
        obj,rec=read_json(p);assert rec['bytes']==old['bytes']and rec['SHA']==old['SHA'],str(rel)
        saved[rel.as_posix()]=obj;bindings.append(dict(original_source=old,snapshot=rec,identity_equal=True))
    assert len(bindings)==6
    cases=[]
    for exp in expected['cases']:
        name=exp['case_id'];x=saved['results/'+name+'/result.json'];b=saved['batches/'+name+'/BATCH_RESULT.json']
        assert b['scheduled']==b['executed']==1 and b['unstarted']==[] and b['software_failure']is False and len(b['rows'])==1
        row=b['rows'][0];assert row['case']==name and row['returncode']==0 and row['result_present']is True and row['ERROR_present']is False and row['software_failure']is False
        assert x['config']['case_id']==name and x['complete']is False and x['startup_stand_original_v1_gate']is False
        assert x['stop']==row['stop']=='controller_fault' and x['controller_phase']==row['controller_phase']=='INHIBIT'
        for key in('controls','physics_steps','complete','startup_stand_original_v1_gate','first_BALANCE_command_s','end_stable_s','controller_fault_reason'):
            assert x[key]==row[key],(name,key)
        assert x['controls']==exp['controls']and x['physics_steps']==exp['physics_steps']==20*x['controls']
        assert x['first_BALANCE_command_s']is None and x['end_stable_s']==0 and x['controller_fault_reason']==exp['fault']
        assert x['trace_artifact']==exp['trace_producer']and x['physical_artifact']==exp['physical_producer']
        cases.append(dict(case_id=name,controls=x['controls'],physics_steps=x['physics_steps'],complete=False,old_gate=False,software_failure=False,trace_and_physics_producer_metadata_equal=True))
    ctrl=sum(x['controls']for x in cases);steps=sum(x['physics_steps']for x in cases)
    assert ctrl==expected['new_cutoff_controls']==381 and steps==expected['new_cutoff_physics_steps']==7620
    cumulative=expected['cumulative_context'];assert cumulative['previous_PH10_controls']+ctrl==cumulative['actual_controls']==2482
    assert cumulative['previous_PH10_physics_steps']+steps==cumulative['actual_physics_steps']==49640 and cumulative['passive_physics_steps']==12000
    link=saved['MOD4_DEPLOYMENT_FIRST_LINK_V16/RESULT.json'];assert link['link_calls']==1 and link['returncode']==0 and link['output_present']is True
    assert link['output_is_old_BSP_stage1_UNBOUND']is True and link['latest_MOD4_C3_startup_integration']is False and link['full_hardware_firmware_qualified']is False
    assert link['image']['SHA']==expected['first_link']['image_producer']and link['image']['bytes']==629048
    assert link['image']['entry']==0x080003dd and link['image']['first_flash_vector_words']['initial_SP']==0x20010330
    result=dict(status='PASS_PARENT_SIX_COPIED_SMALL_JSONS_IDENTITY_AND_NUMBERS_NOT_WHOLE_SOURCE_SEAL',cases=cases,new_controls=ctrl,new_physics_steps=steps,complete_10s=0,old_gate_passes=0,cumulative_through_V5_controls=2482,cumulative_through_V5_physics_steps=49640,passive_steps_separate=12000,old_BSP_first_link_calls=1,old_BSP_link_rc=0,new_MOD4_or_hardware_qualified=False,expected_input=pin,snapshot_bindings=bindings,JSON_reads_this_script=len(reads),source_INDEX_final_receipt_review_still_required=True,original_case_or_raw_payload_opened=False,raw_lib_image_obj_model_payload_reads=0,controller_import_FK_PHY_oldQA_ARM_Git_calls=0,active_V6_V7_C18_excluded=True,source_snapshot_bytes_not_modified=True)
    dump(OUT,result);print(json.dumps({k:result[k]for k in('status','new_controls','new_physics_steps','complete_10s','old_gate_passes','JSON_reads_this_script','old_BSP_first_link_calls','old_BSP_link_rc')},indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        if not ERR.exists():dump(ERR,dict(status='FIRST_PARENT_SNAPSHOT_REVIEW_ERROR_STOP',error=traceback.format_exc(),reads=reads,new_payload_model_PHY_Git_calls=0))
        raise
