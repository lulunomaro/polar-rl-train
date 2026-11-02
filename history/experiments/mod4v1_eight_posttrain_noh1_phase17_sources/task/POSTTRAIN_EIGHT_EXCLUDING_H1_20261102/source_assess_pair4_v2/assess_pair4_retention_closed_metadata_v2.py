"""SOURCE ONLY until parent runs CLI after actual pair4 close.
Pure metadata assessor + JSON/current collected stdout reader. No PT/model stat,
SDK/SSH/C/GO/replay/NPZ/JSONL/old raw access. Assessment completion is not PASS.
Original predicates, hardware, DR, commands/reward and clocks are never changed.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, math, re
D=Path(__file__).resolve().parents[1];T=D.parent
ROLES=('W35','SLOPE_INDEPENDENT50')
KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
ORDINARY=('bad_orientation','base_contact','closure','mimic','low_base')
CAPACITY=re.compile(r'overflow|out of memory|CUDA error|buffer.*(too small|insufficient|exceeded)|contact.*capacity.*exceeded',re.I)
SPLIT_MAPPING=dict(record_type='same_UID_original_RM70_command',group_field='standing',
    complete_field='natural_complete_nonterminal_interval',accepted_field='complete_interval_bounds_fact')
class EvidenceError(ValueError):pass

def need(ok,message):
    if not ok:raise EvidenceError(message)
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def count(x):return type(x)is int and x>=0
def rows_by_role(rows,expected,label):
    need(isinstance(rows,list)and len(rows)==len(expected),'Missing/duplicate '+label)
    result={x['role']:x for x in rows};need(set(result)==set(expected),'Wrong roles '+label);return result

def scan_closed_stdout(raw):return [dict(line=i,text=line[:1000])for i,line in enumerate(raw.decode('utf-8','replace').splitlines(),1)if CAPACITY.search(line)]

def interval_events(facts):
    e=facts['events']
    for k in('opened_commands','natural_complete_intervals','complete_kinematic_bounds_met','complete_kinematic_false',
        'partial_intervals','source_parameter_breaks','route_episodes','route_goal_entries','observed_nonterminal_catalog_goal_facts','reset_events'):
        need(count(e[k]),'Invalid original W35 producer count '+k)
    need(e['complete_kinematic_bounds_met']+e['complete_kinematic_false']==e['natural_complete_intervals'],'Original complete=true+false mismatch')
    return dict(e)

def split_counts(value,label):
    need(isinstance(value,dict),'Published split dictionary '+label)
    n=value['count'];accepted=value['original_bounds_met']
    need(count(n)and count(accepted)and accepted<=n,'Invalid published split '+label)
    return dict(count=n,original_bounds_met=accepted,original_false=n-accepted)

def compare_w35(f,old,reference,reasons,old_reasons):
    facts=f['skill']['original_RM70_interval_route_facts'];oldfacts=old['skill']['original_RM70_interval_route_facts']
    events=interval_events(facts);old_events=interval_events(oldfacts)
    need(reference['source_SHA']==old['source_cache']['source_SHA']and reference['num_envs']==80 and reference['seconds']==32.,'W35 published old reference identity')
    baseline={k:split_counts(reference[k],k)for k in('moving_complete','standing_complete')}
    need(baseline['moving_complete']['count']+baseline['standing_complete']['count']==old_events['natural_complete_intervals']
        and baseline['moving_complete']['original_bounds_met']+baseline['standing_complete']['original_bounds_met']==old_events['complete_kinematic_bounds_met'],
        'Old CPU summary not same old compact producer population')
    gaps=['PHASE_REFERENCE_ROOT_VS_COM_WORLD_GETTER_INDEPENDENT_VALIDATION_GAP',
        'FRESH80_NATURAL_EPISODE_COMMAND_POPULATION_NOT_ORIGINAL_FULL20K_ACCEPTED_COHORT',
        'GOAL_IS_OBSERVER_NOT_ORIGINAL_TRAINED_TARGET_OR_NEW_FAILURE_GATE',
        'NO_FULL_RM70_OR_HIGH_SPEED_EXPERT_GRADUATION_FROM_THIS_WINDOW']
    split=facts.get('published_moving_standing_counts')
    comparison=dict(published_split_available=isinstance(split,dict),counts_non_degraded=None,strict_population_and_predicate_comparable=False)
    new_split=None
    if split is None:
        gaps.append('MOVING_STANDING_DENOMINATORS_NOT_PUBLISHED_IN_THIS_FINAL_NO_44_OF_87_PROXY')
    else:
        need(split.get('source_row_field_mapping')==SPLIT_MAPPING,'Split provenance must name original row fields, not a velocity proxy')
        need(split.get('metric_or_grouping_threshold_changed')is False,'No new split threshold accepted')
        new_split={k:split_counts(split[k],k)for k in('moving_complete','standing_complete')}
        need(sum(x['count']for x in new_split.values())==events['natural_complete_intervals']
            and sum(x['original_bounds_met']for x in new_split.values())==events['complete_kinematic_bounds_met'],
            'Published split does not sum to original producer aggregates')
        denominator_match=all(new_split[k]['count']==baseline[k]['count']for k in baseline)
        comparison['denominators_match_published_old']=denominator_match
        comparison['counts_non_degraded']=denominator_match and all(new_split[k]['original_bounds_met']>=baseline[k]['original_bounds_met']for k in baseline)
        if not denominator_match:gaps.append('NATURAL_COMPLETE_MOVING_OR_STANDING_DENOMINATOR_CHANGED_NO_RATE_SUBSTITUTION')
        # Matching counts alone are not a matching command-UID cohort or a proof
        # of getter/reference semantics. This optional evidence is NOT fabricated
        # by the observer; actual old V8 reference has neither fingerprint.
        a=reference.get('strict_comparison_scope');b=facts.get('strict_comparison_scope')
        strict=bool(isinstance(a,dict)and isinstance(b,dict)and a.get('command_uid_population_SHA')
            and a.get('original_acceptance_predicate_SHA')and a==b
            and a.get('reference_frame_and_sample_phase_validated')is True
            and a.get('original_interval_boundaries_unchanged')is True
            and reference.get('backend_getter_linkCOM_cachephase_independentvalidation')is True)
        comparison['strict_population_and_predicate_comparable']=strict
        if not strict:gaps.append('PUBLISHED_OLD_REFERENCE_HAS_NO_MATCHED_UID_POPULATION_PREDICATE_REFERENCE_PHASE_PROOF')
    ordinary_non_degraded=all(reasons[k]<=old_reasons[k]for k in ORDINARY)
    regression=[]
    if not ordinary_non_degraded:regression.append('ordinary_or_integrity_termination_count_increased')
    if new_split and comparison['denominators_match_published_old'] and comparison['counts_non_degraded']is False:regression.append('original_published_split_accepted_count_decreased')
    if events['source_parameter_breaks']>0:gaps.append('ORIGINAL_PRODUCER_SOURCE_PARAMETER_BREAKS_PRESENT')
    choose=bool(new_split and comparison['counts_non_degraded']is True and comparison['strict_population_and_predicate_comparable']
        and ordinary_non_degraded and events['source_parameter_breaks']==0)
    return dict(selection='CANDIDATE'if choose else'FROZEN_MOTHER',
        decision='Strict comparable original published counts retained; not global graduation'if choose else'Conservative mother retained; keep candidate artifact and all diagnostics',
        old_original_events=old_events,candidate_original_events=events,
        baseline_published_split=baseline,candidate_published_split=new_split,comparison=comparison,
        original_CAD_span_reference=reference.get('original_CAD_span_reached'),
        candidate_CAD_span_published=facts.get('original_CAD_span_reached'),
        catalog_goal_reference=reference.get('observed_nonterminal_catalog_goal_facts'),
        goal_zero_is_not_new_fail=True,no_acceleration_gate_or_x8_correction=True,
        original_producer_metadata=facts.get('producer'),producer_source_label_not_actor_identity=True,
        reference_semantics_gaps_retained=True,non_degradation_and_rollback_evidence=regression,
        unresolved_scope_gaps=gaps,full_skill_graduation=False)

def compare_s50(f,old,reasons,old_reasons):
    metrics=f['metrics'];need(metrics['kind']=='SLOPE50_DEFAULT_TRAINING_AXIS_DESCRIPTIVE_ONLY','Use original S50 own-axis metric only')
    need(metrics.get('accepted_original_cohort_rule_saved')is False and metrics.get('no_SLOPE135_predicate_or27_27_scope_borrowed')is True,'S50 original acceptance gap must remain explicit')
    for k in('all_environment_local_root_xy_min','all_environment_local_root_xy_max'):
        v=metrics[k];need(len(v)==80 and all(len(x)==2 and all(finite(y)for y in x)for x in v),'S50 actual 80x2 descriptive root metadata')
    return dict(selection='FROZEN_MOTHER',decision='Original fullramp accepted cohort/predicate remains unavailable; descriptive result is not a skill pass',
        old_boundary=old_reasons['rough_route_boundary'],old_timeouts=old_reasons['time_out'],
        candidate_boundary=reasons['rough_route_boundary'],candidate_timeouts=reasons['time_out'],
        ordinary_counts_non_degraded=all(reasons[k]<=old_reasons[k]for k in ORDINARY),
        candidate_own_axis_metrics=metrics,zero_falls_alone_is_not_skill_pass=True,no_SLOPE135_endpoint_borrowed=True,
        non_degradation_and_rollback_evidence=[k for k in ORDINARY if reasons[k]>old_reasons[k]],
        unresolved_scope_gaps=['S50_ORIGINAL_FULLRAMP_COMPLETE_ACCEPTED_COHORT_MISSING',
            'S50_ORIGINAL_COMPLETE_ACCEPTANCE_PREDICATE_UNJOINED',
            'OWN20S_BOUNDARY_TIMEOUT_COUNTS_ARE_DESCRIPTIVE_NOT_FULLRAMP_ACCEPTANCE'],full_skill_graduation=False)

def assess_pair4(closed,baseline,training_summary,contracts,tasks,stdout_errors_by_role,w35_reference):
    need(closed['pair']==4 and set(closed['roles'])==set(ROLES)and closed['parent_error']is None,'Actual closed pair4 only')
    s=closed['final'];ex=closed['parent_exit'];need(s is not None and ex is not None,'Pending assessment: actual final/parent exit required')
    need(ex['errors']==[]and ex['all_own_children_waited']is True and ex['original_single_GPU_private_EX_released']is True
        and ex['original_global_finite_EX_released']is True,'Actual allwait/two original EX releases required')
    need(s['all_pair_actual_execution_complete']is True,'Actual both windows complete')
    evalrows=rows_by_role(s['rows'],ROLES,'evaluation');oldrows={r['role']:r for r in baseline['rows']}
    need(set(ROLES)<=set(oldrows),'Published old V8 compact rows required')
    need(training_summary['pair']==4 and training_summary['original_actual_cost_settled']is True
        and training_summary['original_leases_released']is True and training_summary['parent_errors']==[]
        and training_summary['H1_excluded']is True,'Original candidate training must already be closed/settled')
    saved=rows_by_role(training_summary['rows'],ROLES,'candidate training')
    need(baseline['group_id']==w35_reference['group_id'] and baseline['root']==w35_reference['root'],'Old published compact/reference same V8 case')
    oldproducer=oldrows['W35']['skill']['original_RM70_interval_route_facts']['producer']
    need(w35_reference['raw']['SHA']==oldproducer['SHA'] and w35_reference['raw']['bytes']==oldproducer['bytes']
        and w35_reference['schema']['SHA']==oldproducer['schema_SHA'],'Old published reference byte/schema metadata join only; never open raw')
    waits=ex['child_waits'];need(len(waits)==2 and {w['pid']for w in waits}=={r['pid']for r in s['rows']}
        and all(w['actual_waited']is True and w['returncode']==0 for w in waits),'Actual wait PID identity/RC0')
    out=[];starts=[];ends=[]
    for role in ROLES:
        row=evalrows[role];f=row['data'];task=tasks[role];pin=saved[role];old=oldrows[role];cache=f['source_cache']
        need(row['returncode']==0 and row['actual_waited']is True and row['passed_execution']is True and row['error']is None
            and row['ready']is True and row['pre_close']is True and f['passed_execution']is True,'Closed ready/start/preclose/RC0 '+role)
        need(f['role']==task['role']==role and f['group_id']==task['group_id']==s['group_id']
            and f['GPU_UUID']==task['GPU_UUID']==s['GPU_UUID'],'Same actual group/GPU '+role)
        need(pin['returncode']==0 and pin['all_own_child_waited']is True and type(pin['actual_PPO_updates'])is int
            and 0<pin['actual_PPO_updates']<=20,'Actual nonzero finite candidate producer '+role)
        need(task['source_path']==pin['checkpoint']and task['source_SHA']==pin['SHA']and task['source_bytes']==pin['bytes'],'Actual candidate checkpoint metadata join '+role)
        need(task['source_iteration']==pin['actual_saved_iteration']and task['source_LR']==pin['actual_saved_LR'],'Use producer raw saved iteration/LR, never source+N '+role)
        steps=pin['actual_Adam17_unique_from_producer'];need(len(steps)==1 and task['source_Adam17']==steps[0],'Actual producer Adam unique state '+role)
        need(task['kind']==task['purpose']==KIND and task['num_envs']==80 and task['seed']==20260928 and set(task['eval_members'])==set(ROLES),'Original fresh80 group/seed '+role)
        for k,v in dict(asset_SHA=USD,contract_SHA=CONTRACT,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],
            closure_m=.01,mimic_rad=.01,gas_N=400,stiffness_N_m=2000,damping_Ns_m=3.).items():need(task[k]==v,'Unchanged original task '+k+' '+role)
        need(task['fresh_fullDR_cohort']is True and task['saved20k_DR_physically_applied']is False
            and task['state_projection_or_slicing']is False and task['whole20k_savedrestore_claim']is False,'No saved20k apply/slice '+role)
        controls=1600 if role=='W35'else 1000
        need(f['controls']==task['controls']==controls and f['seconds']==controls*.02 and f['optimizer_updates']==0,'Original W35/S50 finite frozen window '+role)
        need(cache['source_SHA']==pin['SHA']and cache['physical_byte_opens']==1 and cache['decodes']==1,'One cached actual candidate input '+role)
        need(not stdout_errors_by_role[role],'Current collected stdout capacity/CUDA error '+role)
        if role=='W35':
            need(f['num_envs']==80 and f['physics_callbacks']==8*controls and f['feedback_samples']==2*controls,'W35 actual clock/population')
            need(cache['source_path']==pin['checkpoint']and cache['SHA_calculations']==1 and cache['source_iteration']==pin['actual_saved_iteration']
                and cache['source_Adam17']==steps[0]and cache['source_LR']==pin['actual_saved_LR'],'W35 full cached identity')
            need(cache['all_original_root_and_nested_cached']is True and cache['wholecachedidentity_passed']is True
                and cache['live_actor_STD_strict']is True and cache['source20k_DR_history_applied']is False and cache['source20k_state_sliced']is False,'W35 full CPU cache not live20k')
            need(f['D0_D7_fresh_audit_before']['actual_parameters_pass']is True and f['D0_D7_fresh_audit_after']['actual_parameters_pass']is True,'W35 fresh DR audits')
            reasons=f['termination_events_by_reason'];start=f['first_eval_epoch'];end=f['last_eval_epoch']
            mother=dict(path=old['source_cache']['source_path'],SHA=old['source_cache']['source_SHA'])
        else:
            meta=cache['metadata'];need(f['physics']==8*controls and f['feedback']==2*controls and f['actor_calls']==controls,'S50 actual clock/actor')
            need(cache['purpose']==KIND and cache['source_bytes']==pin['bytes']and cache['SHA_calls']==1 and meta['iteration']==pin['actual_saved_iteration']
                and len(meta['Adam17'])==17 and set(meta['Adam17'])==set(steps)and meta['LR']==pin['actual_saved_LR'],'S50 cached raw producer core')
            need(cache['entire_original_root_and_nested_identity_preserved']is True and cache['source_raw_bytes_retained']is True
                and cache['saved20k_DR_physically_applied']is False and cache['saved20k_history_sliced']is False
                and cache['live_actor_STD_loaded']is True and cache['critic17AdamLRiter_cached_unchanged_not_live_runner_restore']is True,'S50 cache/frozen actor, no20k projection')
            if pin['actual_STD6_from_producer']is not None:need(meta['STD6']==pin['actual_STD6_from_producer'],'S50 actual saved STD metadata')
            need(f['fresh_fullDR_before']['actual_parameters_pass']is True and f['fresh_fullDR_after']['actual_parameters_pass']is True,'S50 fresh DR audits')
            need(f['saved20k_DR_physically_applied']is False and f['state_projection_or_slicing']is False and f['whole20k_savedrestore_claim']is False,'S50 result no fullrestore claim')
            need(f['group_barrier']['all_members_ready']is True and set(f['group_barrier']['expected_names'])==set(ROLES),'S50 actual same group barrier')
            reasons=f['termination_counts'];start=f['wall_start_epoch'];end=f['wall_end_epoch']
            mother=dict(contracts[role]['source']);need(mother['SHA']==old['source_cache']['source_SHA'],'S50 mother baseline/contract metadata')
        need(finite(start)and finite(end)and end>=start,'Actual wallstart/end '+role);starts.append(start);ends.append(end)
        old_reasons=old['termination_events'];need(old['controls']==controls and old['seconds']==f['seconds'],'Original old/new horizon '+role)
        need(all(count(reasons[k])and count(old_reasons[k])for k in ORDINARY+('rough_route_boundary','time_out')),'Original reasons counts '+role)
        decision=compare_w35(f,old,w35_reference,reasons,old_reasons)if role=='W35'else compare_s50(f,old,reasons,old_reasons)
        candidate=dict(pin);chosen=candidate if decision['selection']=='CANDIDATE'else mother
        out.append(dict(role=role,alias='S50'if role!='W35'else'W35',retention_assessment_complete=True,
            actual_execution_complete=True,original_scope=dict(num_envs=80,controls=controls,seconds=f['seconds']),
            frozen_mother=mother,new_candidate_artifact=candidate,selected_artifact=chosen,
            actual_actor_identity=dict(path=task['source_path'],SHA=task['source_SHA'],bytes=task['source_bytes']),
            actual_saved_iteration=pin['actual_saved_iteration'],saved_iteration_copied_from_producer_not_filled=True,
            original_termination_counts_before=old_reasons,original_termination_counts_after=reasons,
            source_pointers=dict(group_id=f['group_id'],GPU_UUID=f['GPU_UUID'],closed_root=closed['root'],training_summary_source=training_summary.get('source')),
            do_not_overwrite_frozen_mother=True,do_not_delete_new_candidate_or_rollback_evidence=True,**decision))
    overlap=min(ends)-max(starts);need(overlap>0,'Both actual control windows must overlap on same GPU')
    return dict(kind='PAIR4_FROZEN_RETENTION_CONSERVATIVE_METADATA_SELECTION_NOT_GRADUATION',pair=4,
        retention_assessment_complete=True,H1_excluded=True,rows=out,actual_common_control_overlap_seconds=overlap,
        unresolved_scope_gaps={r['role']:r['unresolved_scope_gaps']for r in out},
        assessment_completion_does_not_require_skill_PASS=True,original_metrics_or_thresholds_changed=False,
        no_new_goal_failure_gate_or_acceleration_or_x8_scaling=True,no_PT_model_NPZ_JSONL_old_raw_SDK_or_C_access=True,
        do_not_overwrite_frozen_mothers=True,do_not_delete_candidates_or_rollback_evidence=True)

def load_json(path):
    p=Path(path)
    need(p.suffix.lower()=='.json'and not p.name.upper().startswith('TRAINING_BUDGET'),'JSON metadata only; no model/raw/C path')
    raw=p.read_bytes();return json.loads(raw),dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())

def verified_collected_file(root,relative,manifest):
    rel=PurePosixPath(relative);need(not rel.is_absolute()and '..'not in rel.parts and rel.suffix.lower()in('.json','.log'),'Owned collected JSON/current stdout only')
    p=Path(root).joinpath(*rel.parts);resolved=p.resolve();need(resolved.is_relative_to(Path(root).resolve())and resolved.suffix.lower()in('.json','.log'),'Collected metadata escaped root')
    need(relative in manifest,'Missing collector hash row '+relative);raw=p.read_bytes();r=manifest[relative]
    need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA'],'Collector bytes/SHA mismatch '+relative)
    return raw,dict(path=str(p),relative=relative,bytes=len(raw),SHA=r['SHA'])

def common_best_metadata_aliases(result,closed):
    """Stableoutputenvelopeonly; sourcefacts/selection/oldoriginalfieldskept."""
    rows=[];actual=rows_by_role(closed['final']['rows'],ROLES,'validated actual evaluator')
    def candidate_pointer(item):
        path=item.get('path',item.get('checkpoint'))
        need(isinstance(path,str)and path and len(item['SHA'])==64 and type(item['bytes'])is int,'Actual candidate pointer')
        return dict(path=path,SHA=item['SHA'],bytes=item['bytes'])
    for original in result['rows']:
        r=dict(original);role=r['role'];source=actual[role];cache=source['data']['source_cache'];candidate=candidate_pointer(r['new_candidate_artifact']);mother=dict(r['frozen_mother']);selected=candidate if r['selection']=='CANDIDATE'else mother
        chosen=r['selected_artifact'];need(chosen['SHA']==selected['SHA']and chosen.get('path',chosen.get('checkpoint'))==selected['path'],'Selection alias must preserve original exact choice')
        identity=cache['wholecachedidentity_passed']if role=='W35'else cache['entire_original_root_and_nested_identity_preserved']
        need(source['returncode']==0 and source['actual_waited']is True and r['actual_execution_complete']is True,'Actual RC evidence for alias')
        r.update(actual_eval_RC=source['returncode'],actual_scope_seconds=r['original_scope']['seconds'],actual_controls=r['original_scope']['controls'],source_candidate_SHA=r['actual_actor_identity']['SHA'],new_PPO_updates_in_eval=source['data']['optimizer_updates'],selected_source=selected,candidate_preserved=candidate,frozen_mother_preserved=mother,do_not_overwrite_mother_or_failed_candidate=r['do_not_overwrite_frozen_mother']and r['do_not_delete_new_candidate_or_rollback_evidence'],whole_source_cache_identity_preserved=identity,selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation=True,unpaired_trajectory_after_policy_dependent_resets_not_causal_claim=True,common_metadata_aliases_do_not_change_original_choice=True)
        rows.append(r)
    out=dict(result);out.update(rows=rows,actual_control_windows_overlap_seconds=result['actual_common_control_overlap_seconds'],common_metadata_envelope_added_without_reassessment=True);return out


def evaluate_closed_files(pointer_path,baseline_path,training_path,contracts_path,reference_path):
    pointer,pr=load_json(pointer_path);closed_path=Path(pointer['path']);closed,cr=load_json(closed_path)
    baseline,br=load_json(baseline_path);training,tr=load_json(training_path);contracts,cor=load_json(contracts_path);reference,rr=load_json(reference_path)
    manifest={r['relative']:r for r in closed['files']if'relative'in r}
    need(len(manifest)==len([r for r in closed['files']if'relative'in r]),'Duplicate collector manifest paths')
    roots=[]
    for name,key in [('FINAL.json','final'),('PARENT_EXIT_SCOPE.json','parent_exit')]:
        raw,ref=verified_collected_file(closed_path.parent,name,manifest);need(json.loads(raw)==closed[key],'Collected root JSON differs from closed snapshot '+name);roots.append(ref)
    tasks={};errors={};refs=[]
    for role in ROLES:
        for leaf in('task.json','FINAL.json','SDK_FULL_STDOUT_STDERR.log'):
            raw,ref=verified_collected_file(closed_path.parent,'cases/'+role+'/'+leaf,manifest);refs.append(ref)
            if leaf=='task.json':tasks[role]=json.loads(raw)
            elif leaf=='FINAL.json':
                need(json.loads(raw)==next(x['data']for x in closed['final']['rows']if x['role']==role),'Case FINAL differs from collector row '+role)
            else:errors[role]=scan_closed_stdout(raw)
    result=assess_pair4(closed,baseline,training,contracts,tasks,errors,reference)
    result=common_best_metadata_aliases(result,closed)
    result.update(source=str(closed_path),input_metadata_refs=[pr,cr,br,tr,cor,rr],verified_collector_file_refs=roots+refs,
        collector_root_and_case_TASK_FINAL_stdout_hashes_verified=True,only_current_collected_stdout_scanned=True,
        old_reference_is_already_published_CPU_summary_not_raw_replay=True)
    return result

def main():
    p=argparse.ArgumentParser(description='POST-CLOSE ONLY pair4 pure metadata retention assessment; no model/raw re-read')
    p.add_argument('--closed-pointer',type=Path,default=D/'PAIR4_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json')
    p.add_argument('--baseline',type=Path,default=T/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json')
    p.add_argument('--training-summary',type=Path,default=D/'reports/PAIR4_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json')
    p.add_argument('--contracts',type=Path,default=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json')
    p.add_argument('--w35-reference',type=Path,default=T/'reports/NINE_V8_W35_OWN_NEW_ROWS_CPU_ONCE.json')
    p.add_argument('--out',type=Path,default=D/'reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json');a=p.parse_args()
    result=evaluate_closed_files(a.closed_pointer,a.baseline,a.training_summary,a.contracts,a.w35_reference)
    need(a.out.suffix.lower()=='.json','JSON metadata report only')
    with a.out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
    print(a.out);print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
