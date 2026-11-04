"""New parent small-JSON reconciliation for PH11 cutoff. Excludes active V6. No tests/physics/raw."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;O=R/'PH11_PARENT_CLOSED_EXPECTED_FACTS_V1.json'
assert not O.exists();sources=[]
def get(p):
    p=p.resolve();assert p.is_relative_to(R)and p.is_file()and p.stat().st_size<2*1024*1024
    raw=p.read_bytes();sources.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()));return json.loads(raw)
ids=[('startup_front065_world_support_v4_nominal1',193,3860),('startup_front065_lift_pose_v5_nominal1',188,3760)];rows=[]
for name,n,steps in ids:
    p=R/'results'/name;r=get(p/'result.json');b=get(R/'batches'/name/'BATCH_RESULT.json')
    assert r['config']['case_id']==name and r['config']['nominal']is True and r['config']['seed']==0
    assert r['complete']is False and r['stop']=='controller_fault'and r['controls']==n and r['physics_steps']==steps==20*n
    assert r['startup_stand_original_v1_gate']is False and r['end_stable_s']==0. and r['first_BALANCE_command_s']is None
    assert r['controller_truth_inputs']is False and r['root_assist_forces']==r['root_overwrites_after_initialization']==0
    assert r['sensor_tilt_prior_is_not_upright']is True and r['original_model_driver_contact_limits_unchanged']is True
    assert b['scheduled']==b['executed']==1 and b['unstarted']==[]and b['software_failure']is False and len(b['rows'])==1
    br=b['rows'][0];assert br['case']==name and br['returncode']==0 and br['result_present']is True and br['ERROR_present']is False and br['software_failure']is False
    assert br['controls']==n and br['physics_steps']==steps and not(p/'ERROR.json').exists()
    assert all(r[k]['SHA']and r[k]['bytes']>0 for k in ['trace_artifact','physical_artifact'])
    rows.append(dict(case_id=name,controls=n,physics_steps=steps,formal_result_present=True,software_failure=False,complete=False,original_gate=False,first_BALANCE_command_s=None,end_stable_s=0.,fault=r['controller_fault_reason'],trace_producer=r['trace_artifact'],physical_producer=r['physical_artifact'],no_raw_payload_reopen_or_hash=True))
l=get(R/'MOD4_DEPLOYMENT_FIRST_LINK_V16/RESULT.json')
assert l['link_calls']==1 and l['returncode']==0 and l['output_present']is True and l['output_bytes']==629048
assert l['input_current_SHA_matched165']is l['inputs_poststat_unchanged']is l['small_pins_before_after_equal']is True
assert l['diagnostic_lines']==[]and l['output_is_old_BSP_stage1_UNBOUND']is True and l['latest_MOD4_C3_startup_integration']is l['full_hardware_firmware_qualified']is False
assert l['image']['SHA']=='a70772a2c56bf38c144817b86a27d2ca01d32aa288c17bdcb9b592987ff4f601'and l['image']['bytes']==629048
assert l['image']['ELF_type']==2 and l['image']['first_flash_vector_words']['initial_SP']==0x20010330 and l['image']['entry']==0x080003dd
cut=get(R/'ARCHIVE_PHASE11_V5_FIRST_LINK_V17_CUTOFF_FINAL.json');decl=cut['new_physical_registry']
assert [r['case_id']for r in rows]==decl['ids']and sum(r['controls']for r in rows)==decl['total_controls']==381 and sum(r['physics_steps']for r in rows)==decl['total_physics_steps']==7620
assert cut['cumulative_context']['actual_controls']==2101+381==2482 and cut['cumulative_context']['actual_physics_steps']==42020+7620==49640
out=dict(status='PASS_PARENT_INDEPENDENT_SMALL_CLOSED_JSONS_NOT_CONTROLLER_QA',new_cutoff_case_count=2,new_cutoff_controls=381,new_cutoff_physics_steps=7620,formal_results=2,complete_10s=0,old_gate_passes=0,cases=rows,
    cumulative_context=dict(previous_PH10_controls=2101,previous_PH10_physics_steps=42020,prior_immutable_commit='e176d2a6401fafb9d618a042acba8190023c3273',controlled_attempts=6,actual_controls=2482,actual_physics_steps=49640,formal_false=5,V1_APIERROR_prefix_no_result_backfill=True,passive_cases=3,passive_physics_steps=12000,not_independent_0_of6_rate=True),
    first_link=dict(calls=1,returncode=0,image_producer=l['image']['SHA'],file_bytes=629048,old_BSP_stage1_UNBOUND=True,latest_control_hardware_qualified=False,ROM_RAM_NOT_file_bytes=True),
    sources=sources,saved_small_JSON_reads=len(sources),raw_lib_image_obj_model_payload_reads=0,controller_import_test_model_FK_PHY_oldQA_native_Git_calls=0,
    active_V6_249control4980PHY_explicitly_excluded_and_not_read=True,scope_only_through_V5_C17=True)
with O.open('x',encoding='utf-8',newline='\n')as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v for k,v in out.items()if k not in('sources','cases')},indent=2))
