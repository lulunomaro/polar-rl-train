"""Prepare one NEW V3 profileA nominal: metadata/AST only, never imports robot.
B requires actual failed A sensor eligibility; physics still needs separate review/approval.
"""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V3/front_B_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
proof=R/'STARTUP_STAND_V3/PREFLIGHT_RESULT.json';p=json.loads(proof.read_bytes());rc=json.loads((R/'STARTUP_STAND_V3/RECEIPT.json').read_bytes())
assert p['status'].startswith('PASS')and p['counts']==rc['counts']
assert p['counts']['enabled_external_commands_total_A_and_B']<=420 and p['counts']['disabled_external_commands_including_base']<=40 and p['counts']['typed_cases']<=12
assert p['counts']['geometry_model_FK_PHY_DR_oldQA_Git_agent_calls']==0
assert sha(proof)==rc['result_SHA']
entry=R/'run_startup_stand_case_v5.py';core=R/'STARTUP_STAND_V3/controller.py'
assert sha(entry)==rc['unexecuted_entry_SHA']=='dc542b53ebe0c549aa0308886e635b1176ac0718ddc2bc6f5938aeb1d43b0275'
assert sha(core)==rc['core_SHA']=='0a29053da9270932037889130ad514345571d222bb9d3e34c3a6ef335a9fc3b2'
def parts(path):
    tree=ast.parse(path.read_text(encoding='utf-8'));loop=next(x for x in ast.walk(tree)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='k')
    assignments={n.targets[0].id:ast.dump(n,include_attributes=False)for n in ast.walk(tree)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('healthy','good','complete','passed')}
    return ast.dump(loop,include_attributes=False),assignments
assert parts(R/'run_startup_stand_case_v4.py')==parts(entry)
Aresult=R/'results/startup_front065_tracking_v3a_nominal1/result.json';Aanalysis=R/'STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json'
ar=json.loads(Aresult.read_bytes());az=json.loads(Aanalysis.read_bytes())
assert ar['config']['case_id']==az['case_id']=='startup_front065_tracking_v3a_nominal1'
assert ar['startup_stand_original_v1_gate']is False and ar['stop']=='controller_fault'and ar['controller_fault_reason']=='startup timeout6s'
assert az['future_B_condition_available_but_NOT_launch_permission']is True and az['actual_A_sensor_alignment_eligible_count']>0
assert ar['trace_artifact']==az['source_trace_producer']and az['actual_control_stream_open_count']==1 and az['actual_physics_stream_or_old_raw_open_count']==0
old=json.loads((R/'STARTUP_STAND_V1/front_admission001/CONFIG.json').read_bytes());cfg=dict(old)
cfg.update(case_id='startup_front065_tracking_v3b_nominal1',kind='NEW_STARTUP_ELIGIBLE_ALIGNMENT_FRONT_NOMINAL_V3B',controller=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=True))
a=dict(cfg);b=dict(old)
for x in(a,b):
    x.pop('case_id');x.pop('kind');x['controller']=dict(x['controller']);x['controller'].pop('recovery_tracking_enable',None);x['controller'].pop('alignment_wheel_enable',None)
assert a==b
assert not(R/'results'/cfg['case_id']).exists()and not(R/'batches'/cfg['case_id']).exists()
D.mkdir(exist_ok=False);dump(D/'CONFIG.json',cfg)
idx=json.loads((R/'STARTUP_STAND_V2/front_admission001/SOURCE_PREEXEC.json').read_bytes());paths={Path(x['path']).resolve()for x in idx['files']}
paths.update([Path(__file__).resolve(),entry,core,proof,*[R/'STARTUP_STAND_V3'/s for s in('METHOD.md','METHOD_CLARIFICATION_001.json','ENTRY_DERIVATION.json','RECEIPT.json','REPORT.md','SOURCE_PREEXEC.json','SYNTHETIC_PLAN.json')]])
paths.update([Aresult,Aanalysis,R/'STARTUP_STAND_V3/front_A_admission001/CONFIG.json',R/'STARTUP_STAND_V3/front_A_admission001/PROTOCOL.json'])
roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()];records=[]
for f in sorted(paths):
    assert any(f.is_relative_to(root)for root in roots),str(f)
    records.append(dict(path=str(f),bytes=f.stat().st_size,SHA=sha(f)))
dump(D/'SOURCE_PREEXEC.json',dict(files=records,allowed_readonly_source_roots=[str(x)for x in roots],original_runtime_robot_asset_guard_retained=True,no_model_assets_or_raw_opened_here=True))
dump(D/'PROTOCOL.json',dict(kind='STARTUP_V3B_ELIGIBLE_POSE_ALIGNMENT_FRONT065_ONE_NOMINAL_TRAIN',runner=entry.name,config=cfg,max_workers=1,
    maximum_controls=1000,maximum_physics_steps=20000,old_failed_cases_not_replayed=True,new_physical_actuation_hypothesis_not_reporting_repair=True,
    independent_parent_loop_and_private_gate_AST_equal=True,private_grade_gates_observer_model_driver_unchanged=True,
    controller_ready_narrowed_with_packet_wheel_quiet_le2=True,one_passive_fixture_initialization_no_upright_prior_reset_or_assist=True,
    no_automatic_DR_back_side_or_retry=True,profile_B_not_admitted=False,A_saved_evidence_required=True,A_sensor_eligible_count=az['actual_A_sensor_alignment_eligible_count'],A_first_sensor_eligible_s=az['actual_A_first_sensor_alignment_eligible_s'],
    B_offline_admission_only_no_truth_control='Actual A originalgateFalse+sensor eligibility already observed; this does not add ground-truth inputs to runtime controller.',
    B_is_training_not_holdout_or_reliability_certificate=True,parent_actual_code_saved_proof_and_source_binding_review_required=True))
dump(D/'PREPARATION_RECEIPT.json',dict(status='PREPARED_V3B_AFTER_REAL_A_SENSOR_ELIGIBILITY_NOT_EXECUTED',config_SHA=sha(D/'CONFIG.json'),protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),runner_SHA=sha(entry),candidate_SHA=sha(core),saved_proof_SHA=sha(proof),files_pinned=len(records),
    independent_loop_private_gate_AST_equal=True,actual_model_FK_PHY_oldQA_Git_calls=0))
print(json.dumps(json.loads((D/'PREPARATION_RECEIPT.json').read_bytes()),indent=2))
