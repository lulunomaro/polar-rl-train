"""Pure stdlib synthetic metadata tests; never read pending pair4/old raw/model.
No actual CLI or reports/BEST publication. Temporary synthetic files are isolated.
"""
from pathlib import Path
import ast,copy,hashlib,json,tempfile
import assess_pair4_retention_closed_metadata_v1 as m
B=Path(__file__).resolve().parent
TESTS=[]
def check(name,ok):assert ok,name;TESTS.append(dict(name=name,passed=True))
def reject(fn):
    try:fn()
    except (m.EvidenceError,KeyError):return True
    return False

def fixtures():
    terms=dict(time_out=0,bad_orientation=0,base_contact=0,closure=0,mimic=0,low_base=0,rough_route_boundary=0)
    events=dict(opened_commands=315,natural_complete_intervals=87,complete_kinematic_bounds_met=44,complete_kinematic_false=43,
        partial_intervals=228,source_parameter_breaks=0,route_episodes=228,route_goal_entries=0,observed_nonterminal_catalog_goal_facts=0,reset_events=148)
    producer=dict(SHA='a'*64,bytes=171547,schema_SHA='b'*64,producer_SHA_without_reread=True)
    wold=dict(role='W35',controls=1600,seconds=32.,termination_events=dict(terms,time_out=62,rough_route_boundary=86),
        source_cache=dict(source_SHA='1'*64,source_path='MOCK_FROZEN_MOTHER_W35_POINTER'),
        skill=dict(original_RM70_interval_route_facts=dict(events=events,producer=producer)))
    sold=dict(role='SLOPE_INDEPENDENT50',controls=1000,seconds=20.,termination_events=dict(terms,time_out=47,rough_route_boundary=41),source_cache=dict(source_SHA='2'*64))
    baseline=dict(group_id='MOCK_OLD_V8',root='MOCK_OLD_ROOT_NO_READ',rows=[wold,sold])
    ref=dict(source_SHA='1'*64,num_envs=80,seconds=32.,group_id=baseline['group_id'],root=baseline['root'],
        raw=dict(SHA=producer['SHA'],bytes=producer['bytes']),schema=dict(SHA=producer['schema_SHA']),
        moving_complete=dict(count=61,original_bounds_met=18),standing_complete=dict(count=26,original_bounds_met=26),
        original_CAD_span_reached=0,observed_nonterminal_catalog_goal_facts=0,
        backend_getter_linkCOM_cachephase_independentvalidation=False,unpaired_freshN80_not_original20k_cohort=True)
    training=dict(pair=4,original_actual_cost_settled=True,original_leases_released=True,parent_errors=[],H1_excluded=True,source='MOCK_TRAIN_CLOSED_JSON_NOT_OPENED',rows=[])
    tasks={};rows=[]
    for i,role in enumerate(m.ROLES):
        # Raw saved labels deliberately not Mother+20; no arithmetic reconstruction.
        pin=dict(role=role,returncode=0,all_own_child_waited=True,actual_PPO_updates=20,checkpoint='MOCK_CANDIDATE_POINTER_'+role,
            SHA=str(i+3)*64,bytes=123456,actual_saved_iteration=32662 if i==0 else 32137,
            actual_Adam17_unique_from_producer=[654900 if i==0 else 644380],actual_saved_LR=.00001,
            actual_STD6_from_producer=None)
        training['rows'].append(pin)
        task=dict(role=role,group_id='MOCK_NEW_PAIR4',GPU_UUID='MOCK_GPU',kind=m.KIND,purpose=m.KIND,num_envs=80,seed=20260928,eval_members=list(m.ROLES),
            source_path=pin['checkpoint'],source_SHA=pin['SHA'],source_bytes=pin['bytes'],source_iteration=pin['actual_saved_iteration'],source_Adam17=pin['actual_Adam17_unique_from_producer'][0],source_LR=pin['actual_saved_LR'],
            asset_SHA=m.USD,contract_SHA=m.CONTRACT,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,
            gas_N=400,stiffness_N_m=2000,damping_Ns_m=3.,fresh_fullDR_cohort=True,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,
            controls=1600 if i==0 else 1000)
        tasks[role]=task
        f=dict(role=role,group_id=task['group_id'],GPU_UUID=task['GPU_UUID'],passed_execution=True,controls=task['controls'],seconds=task['controls']*.02,optimizer_updates=0)
        if i==0:
            f.update(num_envs=80,physics_callbacks=12800,feedback_samples=3200,first_eval_epoch=100.,last_eval_epoch=180.,
                source_cache=dict(source_path=pin['checkpoint'],source_SHA=pin['SHA'],physical_byte_opens=1,SHA_calculations=1,decodes=1,
                    source_iteration=pin['actual_saved_iteration'],source_Adam17=pin['actual_Adam17_unique_from_producer'][0],source_LR=pin['actual_saved_LR'],
                    all_original_root_and_nested_cached=True,wholecachedidentity_passed=True,live_actor_STD_strict=True,source20k_DR_history_applied=False,source20k_state_sliced=False),
                D0_D7_fresh_audit_before=dict(actual_parameters_pass=True),D0_D7_fresh_audit_after=dict(actual_parameters_pass=True),termination_events_by_reason=copy.deepcopy(terms),
                skill=dict(original_RM70_interval_route_facts=dict(events=copy.deepcopy(events),producer=dict(source_SHA='STALE_OBSERVER_LABEL_DO_NOT_USE_AS_ACTOR_ID'))))
        else:
            f.update(physics=8000,feedback=2000,actor_calls=1000,wall_start_epoch=101.,wall_end_epoch=151.,
                source_cache=dict(purpose=m.KIND,source_SHA=pin['SHA'],source_bytes=pin['bytes'],physical_byte_opens=1,SHA_calls=1,decodes=1,
                    metadata=dict(iteration=pin['actual_saved_iteration'],Adam17=[pin['actual_Adam17_unique_from_producer'][0]]*17,LR=pin['actual_saved_LR'],STD6=[2.,.1,.1,.1,.1,.1]),
                    entire_original_root_and_nested_identity_preserved=True,source_raw_bytes_retained=True,saved20k_DR_physically_applied=False,saved20k_history_sliced=False,
                    live_actor_STD_loaded=True,critic17AdamLRiter_cached_unchanged_not_live_runner_restore=True),
                fresh_fullDR_before=dict(actual_parameters_pass=True),fresh_fullDR_after=dict(actual_parameters_pass=True),
                group_barrier=dict(all_members_ready=True,expected_names=list(m.ROLES)),termination_counts=copy.deepcopy(terms),
                saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,
                metrics=dict(kind='SLOPE50_DEFAULT_TRAINING_AXIS_DESCRIPTIVE_ONLY',accepted_original_cohort_rule_saved=False,
                    no_SLOPE135_predicate_or27_27_scope_borrowed=True,all_environment_local_root_xy_min=[[0.,0.]for _ in range(80)],all_environment_local_root_xy_max=[[.1,.2]for _ in range(80)]))
        rows.append(dict(role=role,pid=700+i,returncode=0,actual_waited=True,passed_execution=True,error=None,ready=True,pre_close=True,data=f))
    closed=dict(pair=4,roles=list(m.ROLES),root='MOCK_NEW_CLOSED_ROOT',parent_error=None,
        final=dict(group_id='MOCK_NEW_PAIR4',GPU_UUID='MOCK_GPU',all_pair_actual_execution_complete=True,rows=rows),
        parent_exit=dict(errors=[],all_own_children_waited=True,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,
            child_waits=[dict(pid=700+i,actual_waited=True,returncode=0)for i in range(2)]))
    contracts={'SLOPE_INDEPENDENT50':dict(source=dict(path='MOCK_FROZEN_S50_POINTER',SHA='2'*64))}
    errors={r:[]for r in m.ROLES}
    return [closed,baseline,training,contracts,tasks,errors,ref]

def run():
    source=B/'assess_pair4_retention_closed_metadata_v1.py';raw=source.read_bytes();tree=ast.parse(raw.decode('utf-8'));compile(tree,str(source),'exec')
    check('stdlib_source_AST',not any(isinstance(n,ast.Import)and any(a.name.split('.')[0]in('torch','numpy','paramiko')for a in n.names)for n in ast.walk(tree)))
    x=fixtures();result=m.assess_pair4(*x)
    check('assessment_complete_without_fake_PASS',result['retention_assessment_complete']and all(r['selection']=='FROZEN_MOTHER'for r in result['rows']))
    check('missing_W35_split_is_gap_not44of87_proxy',result['rows'][0]['candidate_published_split']is None and any('DENOMINATORS_NOT_PUBLISHED'in g for g in result['rows'][0]['unresolved_scope_gaps']))
    check('S50_zero_falls_not_skill_pass',result['rows'][1]['zero_falls_alone_is_not_skill_pass']and not result['rows'][1]['full_skill_graduation'])
    check('actual_actor_identity_not_stale_book_label',result['rows'][0]['actual_actor_identity']['SHA']=='3'*64)
    check('raw_saved_iteration_no_plusN',result['rows'][0]['actual_saved_iteration']==32662 and result['rows'][1]['actual_saved_iteration']==32137)
    y=copy.deepcopy(x);facts=y[0]['final']['rows'][0]['data']['skill']['original_RM70_interval_route_facts']
    facts['published_moving_standing_counts']=dict(source_row_field_mapping=m.SPLIT_MAPPING,metric_or_grouping_threshold_changed=False,
        moving_complete=dict(count=61,original_bounds_met=20),standing_complete=dict(count=26,original_bounds_met=26))
    facts['events'].update(complete_kinematic_bounds_met=46,complete_kinematic_false=41)
    r=m.assess_pair4(*y)['rows'][0]
    check('nondegraded_split_stillMother_without_population_phase_proof',r['comparison']['counts_non_degraded']is True and r['selection']=='FROZEN_MOTHER')
    z=copy.deepcopy(y);scope=dict(command_uid_population_SHA='5'*64,original_acceptance_predicate_SHA='6'*64,reference_frame_and_sample_phase_validated=True,original_interval_boundaries_unchanged=True)
    z[-1]['strict_comparison_scope']=scope;z[-1]['backend_getter_linkCOM_cachephase_independentvalidation']=True
    z[0]['final']['rows'][0]['data']['skill']['original_RM70_interval_route_facts']['strict_comparison_scope']=scope
    check('hypothetical_fully_proven_scope_can_select_candidate_without_global_grade',m.assess_pair4(*z)['rows'][0]['selection']=='CANDIDATE')
    q=copy.deepcopy(y);q[0]['final']['rows'][0]['data']['skill']['original_RM70_interval_route_facts']['published_moving_standing_counts']['moving_complete']['original_bounds_met']=17
    q[0]['final']['rows'][0]['data']['skill']['original_RM70_interval_route_facts']['events'].update(complete_kinematic_bounds_met=43,complete_kinematic_false=44)
    check('published_regression_keeps_mother',m.assess_pair4(*q)['rows'][0]['selection']=='FROZEN_MOTHER')
    for name,mut in [('unclosed',lambda a:a[0]['parent_exit'].update(all_own_children_waited=False)),
        ('wrong_candidate_SHA',lambda a:a[4]['W35'].update(source_SHA='f'*64)),
        ('partial_original_window',lambda a:a[0]['final']['rows'][0]['data'].update(controls=1599)),
        ('model_raw_counter_mismatch',lambda a:a[4]['W35'].update(source_iteration=32663)),
        ('saved20k_slice',lambda a:a[4]['W35'].update(state_projection_or_slicing=True)),
        ('capacity_error',lambda a:a[5].update(W35=[dict(text='CUDA error 2')])),
        ('borrowed_S135',lambda a:a[0]['final']['rows'][1]['data']['metrics'].update(no_SLOPE135_predicate_or27_27_scope_borrowed=False))]:
        q=copy.deepcopy(x);mut(q);check(name+'_rejected',reject(lambda:m.assess_pair4(*q)))
    check('model_pointer_not_opened',reject(lambda:m.load_json('NEVER_OPEN_MODEL.pt')))
    check('current_stdout_capacity_scan',bool(m.scan_closed_stdout(b'Warp CUDA error 2: out of memory\n')))
    # Test only synthetic current metadata files and collector hashes, never real
    # pending pointers, SDK stdout, producer JSONL/NPZ or actual output report.
    with tempfile.TemporaryDirectory(prefix='SYNTHETIC_ONLY_PAIR4_',dir=B)as td:
        root=Path(td);q=fixtures();manifest=[]
        def put(rel,value,is_log=False):
            p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);data=value if is_log else json.dumps(value,indent=2).encode();p.write_bytes(data)
            manifest.append(dict(relative=rel,bytes=len(data),SHA=hashlib.sha256(data).hexdigest()));return p
        put('FINAL.json',q[0]['final']);put('PARENT_EXIT_SCOPE.json',q[0]['parent_exit'])
        for role in m.ROLES:
            put('cases/'+role+'/TASK.json',q[4][role]);put('cases/'+role+'/FINAL.json',next(r['data']for r in q[0]['final']['rows']if r['role']==role));put('cases/'+role+'/SDK_FULL_STDOUT_STDERR.log',b'SYNTHETIC ONLY no real SDK ran\n',True)
        q[0]['files']=manifest
        closed=root/'CLOSED_RESULT.json';closed.write_text(json.dumps(q[0]),encoding='utf-8')
        ptr=root/'pointer.json';ptr.write_text(json.dumps(dict(path=str(closed))),encoding='utf-8')
        paths=[]
        for name,obj in [('baseline',q[1]),('training',q[2]),('contracts',q[3]),('reference',q[6])]:
            p=root/(name+'.json');p.write_text(json.dumps(obj),encoding='utf-8');paths.append(p)
        out=m.evaluate_closed_files(ptr,*paths)
        check('synthetic_collector_TASK_FINAL_stdout_hashes_pass',out['collector_root_and_case_TASK_FINAL_stdout_hashes_verified'])
        p=root/'cases/W35/SDK_FULL_STDOUT_STDERR.log';p.write_bytes(b'SYNTHETIC TAMPER')
        check('collector_byte_SHA_tamper_rejected',reject(lambda:m.evaluate_closed_files(ptr,*paths)))
    proof=dict(kind='SOURCE_ONLY_SYNTHETIC_STDLIB_NOT_REAL_PAIR4_ASSESSMENT',tests=TESTS,all_passed=True,
        no_actual_pair4_pointer_read=True,no_actual_best_report_written=True,no_model_PT_stat_hash_decode=True,
        no_NPZ_JSONL_old_raw_SDK_GPU_SSH_C_GO_or_Git_access=True,
        synthetic_scope_fingerprints_not_real_old_V8_evidence=True,
        capability_selection=dict(matched_skill=None,catalog='Office/ACL not applicable',tools='FS + stdlib AST/synthetic metadata'))
    p=B/'PAIR4_ASSESSOR_STDLIB_SOURCE_PROOF_V1.json'
    with p.open('x',encoding='utf-8')as f:json.dump(proof,f,indent=2)
    files=[source,Path(__file__),p]
    index=dict(kind='SOURCE_READY_FOR_PARENT_POSTCLOSE_ONLY_NOT_ACTUAL_PAIR4_ASSESSMENT',
        processor=dict(path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),
        command='python -S -B "'+str(source)+'"',default_output=str(m.D/'reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json'),
        actual_processor_executed=False,best_output_published=False,synthetic_tests_passed=len(TESTS),
        files=[dict(path=str(f),bytes=len(f.read_bytes()),SHA=hashlib.sha256(f.read_bytes()).hexdigest())for f in files])
    p=B/'FINAL_PAIR4_METADATA_ASSESSOR_SOURCE_INDEX_V1.json'
    with p.open('x',encoding='utf-8')as f:json.dump(index,f,indent=2)
    print(json.dumps(dict(index_path=str(p),processor=index['processor'],synthetic_tests=len(TESTS),actual_pair4_best_report_written=False),indent=2))
if __name__=='__main__':run()
