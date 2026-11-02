"""Purelocalstdlibsyntheticmetadata tests. Neverreadpending/actualevalpointer,
PT/raw/stdout orwriteactualbestselection. ParentrunsrealCLIafterclosed.
"""
from pathlib import Path
import ast,copy,hashlib,json
import assess_pair2_retention_closed_metadata_v1 as m
B=Path(__file__).resolve().parent;tests=[]
def check(n,v):assert v,n;tests.append(dict(name=n,passed=True))
def reject(fn):
 try:fn()
 except (m.EvidenceError,KeyError):return True
 return False
R=m.ROLES;groups=dict(ascending=dict(environments=27,complete_envs=22,contact_confirmed_envs=22),descending=dict(environments=27,complete_envs=27,contact_confirmed_envs=27),stand=dict(environments=26,complete_envs=0,contact_confirmed_envs=0));terms=dict(time_out=0,bad_orientation=0,base_contact=0,closure=0,mimic=0,low_base=0);std=[9.,.05,.06,.07,.08,.09]
baseline=dict(rows=[dict(role='E2',controls=1200,seconds=24.,source_cache=dict(source_path='MOCK_FROZEN_E2_DO_NOT_OPEN',source_SHA='1'*64),termination_events=copy.deepcopy(terms),diagnostic_fullwindow_body_abs_error_mean_vx_vy_yaw=[.2,.3,.4],skill=dict(original_E2_sameUID_cycle_facts=dict(complete_cycle_events=187,original_false_cycle_events=187,incomplete_events=43,terminal_complete_events=0))),dict(role='CURB_INDEPENDENT113',controls=750,seconds=15.,source_cache=dict(source_SHA='2'*64),termination_events=copy.deepcopy(terms),original_endpoint_groups=copy.deepcopy(groups),stand_no_ordinary_failure=dict(total=26,no_failure=26))])
training=dict(pair=2,original_actual_cost_settled=True,original_leases_released=True,parent_errors=[],H1_excluded=True,rows=[]);tasks={};rows=[]
for i,role in enumerate(R):
 pin=dict(role=role,returncode=0,all_own_child_waited=True,checkpoint='MOCK_CANDIDATE_METADATA_NOT_PT_'+role,SHA=str(i+3)*64,bytes=123456,actual_saved_iteration=123+i,actual_Adam17_unique_from_producer=[1000+i],actual_saved_LR=.0001,actual_STD6_from_producer=None if role=='E2'else std);training['rows'].append(pin)
 task=dict(role=role,group_id='MOCK_PAIR2',GPU_UUID='MOCK_GPU',kind=m.KIND,purpose=m.KIND,num_envs=80,seed=20260928,eval_members=list(R),asset_SHA=m.USD,contract_SHA=m.CONTRACT,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_N=400,stiffness_N_m=2000,damping_Ns_m=3.,fresh_fullDR_cohort=True,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,source_path=pin['checkpoint'],source_SHA=pin['SHA'],source_bytes=pin['bytes'],source_iteration=pin['actual_saved_iteration'],source_Adam17=pin['actual_Adam17_unique_from_producer'][0],source_LR=pin['actual_saved_LR'],controls=1200 if role=='E2' else 750);tasks[role]=task
 f=dict(role=role,group_id='MOCK_PAIR2',GPU_UUID='MOCK_GPU',passed_execution=True,controls=task['controls'],seconds=task['controls']*.02,optimizer_updates=0)
 if role=='E2':
  f.update(num_envs=80,physics_callbacks=9600,feedback_samples=2400,first_eval_epoch=101.,last_eval_epoch=150.,source_cache=dict(source_path=pin['checkpoint'],source_SHA=pin['SHA'],physical_byte_opens=1,SHA_calculations=1,decodes=1,source_iteration=pin['actual_saved_iteration'],source_Adam17=pin['actual_Adam17_unique_from_producer'][0],source_LR=pin['actual_saved_LR'],all_original_root_and_nested_cached=True,wholecachedidentity_passed=True,live_actor_STD_strict=True,source20k_DR_history_applied=False,source20k_state_sliced=False),D0_D7_fresh_audit_before=dict(actual_parameters_pass=True),D0_D7_fresh_audit_after=dict(actual_parameters_pass=True),termination_events_by_reason=copy.deepcopy(terms),skill=dict(body_velocity_absolute_error_time_integral_per_env=[[.1*24,.2*24,.3*24]for _ in range(80)],original_E2_sameUID_cycle_facts=dict(complete_cycle_events=190,original_false_cycle_events=190,incomplete_events=42,terminal_complete_events=0,producer=dict(source_SHA='1'*64,rows=232))))
 else:
  rr=[dict(group=k,first_ordinary_failure_control=None)for k,g in groups.items()for _ in range(g['environments'])]
  f.update(actor_calls=750,group_barrier=dict(barrier_start=dict(group_id='MOCK_PAIR2',GPU_UUID='MOCK_GPU',all_members_ready=True,members=list(R))),physics=6000,feedback=1500,wall_start_epoch=102.,wall_end_epoch=140.,source_cache=dict(source_SHA=pin['SHA'],source_bytes=pin['bytes'],physical_byte_opens=1,SHA_calls=1,decodes=1,metadata=dict(iteration=pin['actual_saved_iteration'],Adam17=[pin['actual_Adam17_unique_from_producer'][0]]*17,LR=pin['actual_saved_LR'],STD6=std),entire_original_root_and_nested_identity_preserved=True,live_actor_STD_loaded=True,saved20k_DR_physically_applied=False,saved20k_history_sliced=False),fresh_fullDR_before=dict(fresh_N80_D0_D7_enabled=True,actual_parameters=dict(actual_parameters_pass=True)),fresh_fullDR_after=dict(fresh_N80_D0_D7_enabled=True,actual_parameters=dict(actual_parameters_pass=True)),termination_counts=copy.deepcopy(terms),metrics=dict(groups=copy.deepcopy(groups),rows=rr))
 rows.append(dict(role=role,pid=900+i,returncode=0,actual_waited=True,passed_execution=True,error=None,ready=True,started=(role=='E2'),pre_close=True,data=f))
closed=dict(pair=2,roles=list(R),parent_error=None,parent_exit=dict(errors=[],all_own_children_waited=True,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,child_waits=[dict(pid=900+i,actual_waited=True,returncode=0)for i in range(2)]),final=dict(all_pair_actual_execution_complete=True,rows=rows,common_start_epoch=100.,group_id='MOCK_PAIR2',GPU_UUID='MOCK_GPU'));contracts={'CURB_INDEPENDENT113':dict(source=dict(path='MOCK_FROZEN_CURB_DO_NOT_OPEN',SHA='2'*64,bytes=111111))};errors={r:[]for r in R}
def run(c=closed,b=baseline,t=tasks,e=errors):return m.assess_pair2(c,b,training,contracts,t,e)
a=run();check('synthetic_complete_assessment_has_explicit_two_selections',a['retention_assessment_complete']is True and a['H1_excluded']is True and {x['selection']for x in a['rows']}=={'CANDIDATE'})
e2,curb=a['rows'];check('body_existing_integrals_divided80xseconds',all(abs(n-o)<1e-12 for n,o in zip(e2['diagnostic_body_abs_error_mean_vx_vy_yaw'],[.1,.2,.3])))
check('E2cycle_true_false_complete_incomplete_copied_not_PPOgrade',e2['original_signed2pi_cycle_counts']==dict(complete=190,false=190,accepted_true=0,incomplete=42,terminal_complete=0)and e2['baseline_original_signed2pi_cycle_counts']['accepted_true']==0 and e2['E2_world_getter_phase_reference_observer_gap']is True and e2['original_full_expert_graduated']is False)
check('CurbNoTopNumenvsAndStandNoCrossingAccepted','num_envs'not in rows[1]['data']and curb['stand_crossing_required']is False and curb['stand_no_ordinary_failure']['no_failure']==26)
check('CandidateAndMotherBothKeptNoOverwrite',all(r['do_not_overwrite_mother_or_failed_candidate']and r['candidate_preserved']and r['frozen_mother_preserved']for r in a['rows']))
bad=copy.deepcopy(closed);bad['final']['rows'][0]['data']['skill']['body_velocity_absolute_error_time_integral_per_env'][0][0]=1000.;r=run(c=bad);check('oneBodyAxisWorseMeansMotherButAssessmentComplete',r['retention_assessment_complete']is True and r['rows'][0]['selection']=='FROZEN_MOTHER')
bad=copy.deepcopy(closed);bad['final']['rows'][0]['data']['termination_events_by_reason']['closure']=1;check('ordinaryFailuresCannotIncrease',run(c=bad)['rows'][0]['selection']=='FROZEN_MOTHER')
b=copy.deepcopy(baseline);b['rows'][0]['skill']['original_E2_sameUID_cycle_facts']['original_false_cycle_events']=182;check('acceptedTrueCountCannotDrop',run(b=b)['rows'][0]['selection']=='FROZEN_MOTHER')
bad=copy.deepcopy(closed);bad['final']['rows'][1]['data']['metrics']['groups']['ascending']['contact_confirmed_envs']=21;check('CurbAscendingContactDropMeansMother',run(c=bad)['rows'][1]['selection']=='FROZEN_MOTHER')
bad=copy.deepcopy(closed);next(x for x in bad['final']['rows'][1]['data']['metrics']['rows']if x['group']=='stand')['first_ordinary_failure_control']=7;check('CurbStandFailureDropMeansMother',run(c=bad)['rows'][1]['selection']=='FROZEN_MOTHER')
for label,mutate in [('notClosed',lambda x:x.update(parent_exit=None)),('RC1',lambda x:x['final']['rows'][0].update(returncode=1)),('notAllwait',lambda x:x['parent_exit'].update(all_own_children_waited=False)),('EXnotreleased',lambda x:x['parent_exit'].update(original_global_finite_EX_released=False)),('wrongSourceSHA',lambda x:x['final']['rows'][0]['data']['source_cache'].update(source_SHA='BAD')),('differentGroup',lambda x:x['final']['rows'][0]['data'].update(group_id='WRONG')),('20khistoryApplied',lambda x:x['final']['rows'][0]['data']['source_cache'].update(source20k_DR_history_applied=True)),('CurbGroupNot80',lambda x:x['final']['rows'][1]['data']['metrics']['groups']['ascending'].update(environments=26))]:
 bad=copy.deepcopy(closed);mutate(bad)
 try:ok=reject(lambda:run(c=bad))
 except TypeError:ok=True
 check('invalidEvidenceDoesNotPublishFakeAssessment_'+label,ok)
wrong=copy.deepcopy(tasks);wrong['E2']['seed']=7;check('wrongSeedCannotQualify',reject(lambda:run(t=wrong)))
err=copy.deepcopy(errors);err['E2']=['CUDA error out of memory'];check('capacityErrorsCannotQualify',reject(lambda:run(e=err)))
check('closedStdoutCapacityScan',m.scan_closed_stdout(b'normal warning\nCUDA error 2 out of memory\n')==['CUDA error 2 out of memory'])
check('normalWarningsNotCapacityFailures',m.scan_closed_stdout(b'normal deprecated warning\n')==[])
for p in B.glob('*.py'):compile(ast.parse(p.read_bytes()),str(p),'exec')
proof=dict(kind='SOURCE_ONLY_SYNTHETIC_METADATA_ASSESSOR_TEST_NOT_ACTUAL_BEST_SELECTION',tests=len(tests),passed=True,rows=tests,pending_or_actual_eval_pointer_reads=0,actual_best_selection_written=False,actual_model_rawtrajectory_stdout_SDK_SSH_GPU_C_GO_Git_operations=0)
p=B/'PAIR2_ASSESSOR_STDLIB_SOURCE_PROOF_V1.json'
with p.open('x',encoding='utf-8')as f:json.dump(proof,f,indent=2)
source=B/'assess_pair2_retention_closed_metadata_v1.py';sraw=source.read_bytes();index=dict(kind='SOURCE_READY_FOR_PARENT_POSTCLOSE_EXECUTION_NOT_ACTUAL_ASSESSMENT',processor=dict(path=str(source),bytes=len(sraw),SHA=hashlib.sha256(sraw).hexdigest()),proof=dict(path=str(p),bytes=len(p.read_bytes()),SHA=hashlib.sha256(p.read_bytes()).hexdigest()),command='python -B "'+str(source)+'"',default_output=str(m.D/'reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json'),actual_processor_executed=False,best_output_published=False,parent_archive_append_pending=True,files=[dict(path=str(x),bytes=len(x.read_bytes()),SHA=hashlib.sha256(x.read_bytes()).hexdigest())for x in sorted(B.glob('*'))if x.is_file()])
q=B/'FINAL_PAIR2_METADATA_ASSESSOR_SOURCE_INDEX_V1.json'
with q.open('x',encoding='utf-8')as f:json.dump(index,f,indent=2)
print(json.dumps(dict(index_path=str(q),index_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),processor=index['processor'],tests=len(tests),actual_best_selection_written=False),indent=2))
