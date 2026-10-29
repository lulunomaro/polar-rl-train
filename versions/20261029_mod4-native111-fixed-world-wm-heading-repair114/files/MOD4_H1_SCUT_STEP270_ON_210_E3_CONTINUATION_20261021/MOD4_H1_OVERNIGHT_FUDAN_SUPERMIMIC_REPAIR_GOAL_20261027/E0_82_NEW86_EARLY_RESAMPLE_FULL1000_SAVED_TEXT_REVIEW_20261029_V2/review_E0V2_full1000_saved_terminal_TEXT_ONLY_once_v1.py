"""Only one saved terminal UTF8 JSON input; never opens JSONL/NPZ/model/host."""
from pathlib import Path
import hashlib,json,math,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
INPUT=L/'E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V2/reports/E0_V2_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json'
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
def H(x):return hashlib.sha256(x).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
checks=[]
def require(ok,label):
 assert bool(ok),label
 checks.append(label)
def bounds(values,n=20000):return dict(lower=max(values,default=0),upper=min(n,sum(values)),exact_union_not_saved=True,profile_unique_counts_not_summed_as_exact_union=True)
def weighted(rows,key,den='population_controls'):
 selected=[r for r in rows if r[den]>0 and r.get(key) is not None];d=sum(r[den] for r in selected)
 return dict(value=sum(r[key]*r[den] for r in selected)/d if d else None,denominator=d,weight=den,not_unweighted_profile_average=True)
def main():
 raw=INPUT.read_bytes();v=json.loads(raw);require(v['purpose']=='terminal','normal-purpose actual saved terminal')
 require(v['passed_original_frozen_execution'] and v['requested1000_controls_100warm_900steady_complete'],'full1000 execution, independent of skill')
 require(v['source_SHA']==MODEL and not v['original_errors'] and not v['integrity'],'source and original error/integrity')
 require(v['original_terminal_and_allownout_proven'] and v['worker_state']['original_out'] and v['supervisor_state']['original_out'],'known original allout')
 tt=v['original_terminal'];require(tt['actual_worker_waited'] and tt['returncode']==0 and not tt['deadline_terminated'] and tt['private_EX_released'],'actual wait/private release, rc0 alone insufficient')
 rows={}
 for r in v['complete_original_own_stage_UTF8']:
  rel=r['relative'];require(rel not in rows,'unique saved text '+rel);b=r['UTF8'].encode('utf8');require(len(b)==r['bytes'] and H(b)==r['SHA'],'exact saved UTF8 bytes/SHA '+rel);rows[rel]=r
 selected={};evidence=[]
 def original(rel):
  r=rows[rel];value=json.loads(r['UTF8']);selected[rel]=value;evidence.append({k:r[k] for k in ('relative','path','bytes','SHA')});return value
 final=original('frozen_regression/BOUNDED_FROZEN_E0_N20K_PROFILES_ACTUAL.json')
 d=original('frozen_regression/E0_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json')
 early=original('frozen_regression/ACTUAL_E0_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json')
 observed=original('frozen_regression/early_original_resample/E0_REAL_POSTRESTORE_ORIGINAL_RESAMPLE_OBSERVER_ACTUAL.json')
 criterion=original('frozen_regression/ORIGINAL_E0_COMMAND_AND_TERMINATION_CRITERIA.json')
 task=original('FROZEN_CASE_TASK.json')
 healthpath=next(k for k in rows if k.endswith('/CLOCK_TRAINING_HEALTH.json'))
 health=original(healthpath)
 require(final['num_envs']==20000 and final['controls']==final['requested_controls']==1000 and final['warmup_controls']==100 and final['steady_controls']==900 and final['simulated_seconds']==20 and not final['wall_time_limited'],'20k/20s/100warm900steady complete')
 require(final['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and final['all17_Adam_steps']==641200 and final['actual_LR_unchanged']==.00038443359375000017,'source norm/core/STD/17Adam641200/LR unchanged')
 require(v['native24']['controls']==24 and v['native24']['physics_callbacks']==192 and v['native24']['feedback_samples']==48 and v['native24']['legs_queue_apply']==v['native24']['wheels_queue_apply']==192 and v['native24']['trace_controls']==list(range(1,25)),'actual native24 full queue and clock')
 require(health['control_steps']==1000 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==8000 and health['control_dt_s']==.02 and health['physics_dt_s']==.0025,'whole-clock actual8000')
 require(health['termination_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None,'no original nonfinite/stop; reason coverage exact')
 require(v['passed_actual_early_observation_and_adoption'] and early['actual_original_postrestore_event_adopted'] and early['initial_left_censored'] is False,'real original early-adoption, not inferred initial start')
 require(early['observed_ids_count']==20000 and early['actual_physics_tick']==0 and early['actual_phase_zero'],'actual initial IDs/physics0/phase0')
 require(12<=early['sampled_timer_min']<=early['sampled_timer_max']<=16 and observed['diagnostic_valid'] and not observed['errors'] and not observed['event_retention_limited'],'original sampled timer12..16; observer valid')
 require(criterion['command_kind']=='E0_DIRECTIONAL_SPIN_V1' and criterion['resampling_time_range']==[12.,16.] and criterion['original_criteria_unmodified'],'original E0 command/criterion, no other-expert profile')
 profiles=d['profiles'];by={(r['phase'],r['profile']):r for r in profiles};require(len(by)==30,'ten profile labels in3 phases')
 for i in range(10):
  a,b,c=[by[(k,i)] for k in ('whole','warmup','steady')]
  require(a['population_controls']==b['population_controls']+c['population_controls'],'population warm+steady '+str(i))
  require(a['terminated_events']==b['terminated_events']+c['terminated_events'] and a['truncated_events']==b['truncated_events']+c['truncated_events'],'terminal event warm+steady '+str(i))
  require(a['unique_exposed_env']<=20000 and a['unique_env_with_sampled_window']<=a['unique_exposed_env'],'perprofile unique bounds '+str(i))
 for phase,count in [('whole',20000000),('warmup',2000000),('steady',18000000)]:require(sum(by[(phase,i)]['population_controls'] for i in range(10))==count,'complete population denominator '+phase)
 ci=d['command_instances'];crows=ci['profiles'];require(len(crows)==10 and ci['acted_and_zero_control_denominators_separate'],'command labels/acted-zero separation')
 totals={key:sum(r[key] for r in crows) for key in ('closed_instance_events','acted_instance_events','zero_control_instance_events','all_acted_instance_population_controls','acted_initial_left_censored_events','acted_reset_ended_events','acted_window_end_events','fully_observed_resample_to_resample_instance_events','complete_instance_population_controls','complete_instance_seconds','left_censored_instance_events','window_end_right_censored_instance_events','reset_ended_instance_events','complete_transition_instances_with_all_pre12_bins')}
 for r in crows:
  i=r['profile'];require(r['closed_instance_events']==r['acted_instance_events']+r['zero_control_instance_events'],'acted+zero partition '+str(i))
  require(r['all_acted_instance_population_controls']==by[('whole',i)]['population_controls'],'acted-instance population matches original profile '+str(i))
  require(r['acted_instance_events']==r['fully_observed_resample_to_resample_instance_events']+r['acted_reset_ended_events']+r['acted_window_end_events'],'complete-vs-acted-reset/window partition '+str(i))
  require(math.isclose(r['complete_instance_seconds'],r['complete_instance_population_controls']*.02,rel_tol=0,abs_tol=1e-9),'complete instance time/population '+str(i))
  require(r['unique_env_with_complete_instance']<=r['fully_observed_resample_to_resample_instance_events'] and r['unique_env_with_acted_instance']==by[('whole',i)]['unique_exposed_env'],'instance unique counts retain perprofile '+str(i))
  require(r['acted_initial_left_censored_events']==r['left_censored_instance_events']==0,'actual newcase initial leftcensor0 '+str(i))
 require(totals['closed_instance_events']==ci['instance_record_rows']==60000 and totals['acted_instance_events']==40000 and totals['zero_control_instance_events']==20000,'60k closed !=40k acted;20k zero not successes')
 require(totals['fully_observed_resample_to_resample_instance_events']==20000 and totals['acted_reset_ended_events']==20000 and totals['acted_window_end_events']==0,'20k complete vs20k reset-ended acted')
 require(totals['window_end_right_censored_instance_events']==20000 and totals['all_acted_instance_population_controls']==20000000,'20k window-end zero records;20M acted population')
 require(not ci['instance_record_retention_limited'] and not d['trace_limited'],'retention not truncated')
 producer=[]
 for rel in ('frozen_regression/E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl.PRODUCER_INDEX_ACTUAL.json','frozen_regression/early_original_resample/E0_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl.PRODUCER_INDEX_ACTUAL.json'):
  r=original(rel);require(r['producer_stream_SHA_no_reread'] and not r['retention_limited'] and r['content_transfer_default'] is False,'producer-only JSONL index '+rel)
  require(r in v['typed_JSONL_producer_indexes_metadata_only'],'published JSONL index consistent '+rel);producer.append(r)
 require(producer[0]['rows']==60000 and producer[1]['rows']==20000,'producer rows instance/initial20k, contents not read')
 groups={}
 for phase in ('whole','warmup','steady'):
  groups[phase]={}
  for name,ids in [('all',range(10)),('standing',[0]),('straight_signed',[1,3]),('pure_spin_signed',[4,5]),('transition_signed',[6,7]),('moving_signed',[8,9])]:
   rr=[by[(phase,i)] for i in ids];groups[phase][name]=dict(population_controls=sum(r['population_controls'] for r in rr),unique_env_union_bounds=bounds([r['unique_exposed_env'] for r in rr]),body_forward_MAE=weighted(rr,'body_forward_MAE'),yaw_MAE=weighted(rr,'yaw_MAE'),height_MAE=weighted(rr,'height_MAE'),terminated_events=sum(r['terminated_events'] for r in rr),timeout_events=sum(r['truncated_events'] for r in rr))
 moving=[]
 for phase in ('whole','warmup','steady'):
  rr=[by[(phase,i)] for i in (8,9)];seconds=sum(r['sampled_window_seconds'] for r in rr);pop=sum(r['population_controls'] for r in rr)
  moving.append(dict(phase=phase,population_controls=pop,population_seconds=pop*.02,sampled_window_seconds=seconds,sampled_window_population_time_fraction=seconds/(pop*.02) if pop else None,sampled_cycle_window_events=sum(r['complete_sampled_window_events'] for r in rr),unique_sampled_cycle_env_union_bounds=bounds([r['unique_env_with_sampled_window'] for r in rr]),actual_cycle_progress=weighted(rr,'actual_cycle_projected_progress_m_s','sampled_window_seconds'),integrated_command_reference_progress=weighted(rr,'integrated_command_reference_progress_m_s','sampled_window_seconds'),nominal_point5_cycle_absolute_error=weighted(rr,'nominal_half_m_s_cycle_abs_error_time_weighted','sampled_window_seconds'),integrated_reference_cycle_absolute_error=weighted(rr,'integrated_reference_cycle_abs_error_time_weighted','sampled_window_seconds'),signed_profiles=rr,cycle_event_not_command_instance_or_unique_env=True,unsampled_time_not_assumed_successful=True,cycle_error_not_body_velocity_MAE_or_instantaneous_world_speed=True))
 transition=[];phase_names=d['transition_phase_names']
 require(d['transition_phase_error_denominators']==d['transition_phase_controls'],'transition actual error denominators equal profile-time counts')
 for j,name in enumerate(phase_names):
  rr=[]
  for sign in (0,1):
   den=sum(d['transition_phase_controls'][p][j][sign] for p in (0,1));un=[d['transition_phase_unique_env'][p][j][sign] for p in (0,1)]
   rr.append(dict(initial_sign='negative' if sign==0 else 'positive',population_controls=den,population_seconds=den*.02,warm_steady_unique_union_bounds=bounds(un),saved_error_axis_means=[sum(d['transition_phase_error_sums'][p][axis][j][sign] for p in (0,1))/den if den else None for axis in range(3)],error_axis_names_not_explicitly_saved_in_terminal_schema=True,complete_initial_command_phase_population_controls=crows[6+sign]['complete_instance_transition_phase_controls'][j]))
  transition.append(dict(phase=name,by_initial_sign=rr))
 require(totals['complete_transition_instances_with_all_pre12_bins']==crows[6]['fully_observed_resample_to_resample_instance_events']+crows[7]['fully_observed_resample_to_resample_instance_events']==1979,'1979 complete transition command instances cover all pre12 bins')
 require(sum(r['terminated_events'] for r in profiles if r['phase']=='whole')==0 and health['termination_events_by_reason']=={'time_out':20000,'bad_orientation':0,'base_contact':0,'closure':0,'mimic':0,'low_base':0},'actual timeout20000; no original non-timeout failures')
 legacy=dict(first_written_phase_valid_initially_unknown=d['first_written_phase_valid_initially_unknown'],command_summary_initial_instances_left_censored=ci['initial_instances_left_censored'],actual_newcase_admission_initial_left_censored=early['initial_left_censored'],actual_all_profile_acted_initial_leftcensor_events=totals['acted_initial_left_censored_events'],interpretation='Two generic legacy summary booleans remain True in original saved profile text. Preserve them; new V2 actual event/adoption receipt and per-instance aggregate counters explicitly establish observed initial start for this case. Old V1 remains unchanged; no retrospective reclassification or JSONL content validation claimed.')
 pending=['No original numerical skill pass tolerances/per-command success thresholds saved; do not invent a graduation rule.','straight_zero has0 exposure; original continuous straight command has a zero label but no discrete zero atom guaranteed. No exposure is pending, not failed/success.','Only one20s window/seed and sampled original commands; no full stochastic range or long-term reliability claim.','Moving worldprogress metrics cover only accepted sampled same-command2pi windows (~68%movingtime), not every command/all elapsed movingtime.','Complete command summaries provide body/yaw/height errors but not per-command worldprogress success counts or distributions; JSONL content intentionally NOT transferred/read.','Global unique env unions across changing signed profiles are not saved. Retain perprofile exactunique and conservative union bounds, never sum overlaps as exact globalunique.','Per-transition error tensor axis names are not explicit in saved schema; report axis0/1/2 only, no guessed physical labels.','20k reset-ended acted commands are incomplete despite no non-timeout failure;20k0-control window-end rows cannot be positive skill evidence.','No complete127-state/executedaction/queue/DR/reset WM transition dataset; command JSONL and weights are not that dataset.']
 result=dict(kind='E0V2_full1000_early_original_resample_saved_text_acceptance_review_v1',passed_text_integrity_and_accounting=True,check_count=len(checks),checks=checks,input_terminal=dict(path=str(INPUT),bytes=len(raw),SHA=H(raw)),selected_original_text_evidence=evidence,actual_runtime_scope=final,original_criterion=criterion,actual_early_admission=early,original_observer_final=dict(diagnostic_valid=observed['diagnostic_valid'],errors=observed['errors'],events=len(observed['events']),retention_limited=observed['event_retention_limited'],initial_start_eligible=observed['new_initial_start_eligible']),legacy_labels_preserved=legacy,profiles_original_saved=profiles,command_instances_original_saved=ci,command_instance_totals=totals,global_unique_env_interpretation=dict(initial_original_adopted_ids=20000,closed=bounds([r['unique_env_with_closed_instance'] for r in crows]),acted=bounds([r['unique_env_with_acted_instance'] for r in crows]),complete=bounds([r['unique_env_with_complete_instance'] for r in crows]),not_summed_to_claim_unique=True),population_control_weighted_groups=groups,signed_moving_sampled_cycle_metrics=moving,transition_phase_coverage=transition,whole_clock_and_reasons=health,typed_JSONL_producer_indexes_metadata_only=producer,JSONL_contents_read=False,raw_NPZ_model_SDK_host_GPU_access=False,skill_status='PENDING_ORIGINAL_ACCEPTANCE_NOT_GRADUATED',complete_WM_dataset=False,pending=pending,no_old_V1_report_reclassified=True)
 put('E0_V2_FULL1000_EARLY_COMMAND_INSTANCE_SAVED_TEXT_ACCEPTANCE_REVIEW_ACTUAL.json',result)
 put('EXACT_TERMINAL_UTF8_SELECTED_SMALL_TEXT_EVIDENCE.json',dict(input_terminal=result['input_terminal'],sources=evidence,values=selected,all65_saved_text_rows_bytes_SHA_verified=True,no_external_content_opened=True))
 mw=moving[0];counts=totals
 lines=['E0V2 full1000 early-command review — saved text only','',f"20k ×1000controls /20s /100warm900steady completed;17Adam641200/LR unchanged. Native24=24/192/48+legs/wheels192, full8000physics. Originalwait0/allownout/private released/errors[]/integrity[] verified. This is execution and exposure evidence; skill graduation remains pending.",'',f"Actual early original postrestore resample adopted20000 IDs at physics0/phase0; timer {early['sampled_timer_min']:.9f}..{early['sampled_timer_max']:.9f}s. No extra reset/RNG was needed. New per-profile initial-leftcensored counters all0. The saved profile's two old generic booleans still say initialunknown/leftcensored; both are retained and labelled alongside the realV2 admission, not silently overwritten. OldV1 is unchanged.",'',f"Closed records {counts['closed_instance_events']:,}: acted {counts['acted_instance_events']:,},0-control {counts['zero_control_instance_events']:,}. Fully observed resample-to-resample events {counts['fully_observed_resample_to_resample_instance_events']:,}; reset-ended acted {counts['acted_reset_ended_events']:,}; acted-window-end0. All20k window-end rows have0controls. Events are not uniqueenv and0-control records are not successes.",'','| Original profile | Acted events | Complete command events /perprofile uniqueenv | Complete controls | Complete bodyVx MAE | Complete yaw MAE | Complete height MAE |','|---|---:|---:|---:|---:|---:|---:|']
 for r in crows:
  fmt=lambda x:'unknown' if x is None else f'{x:.6f}'
  lines.append(f"| {r['label']} | {r['acted_instance_events']} | {r['fully_observed_resample_to_resample_instance_events']} / {r['unique_env_with_complete_instance']} | {r['complete_instance_population_controls']} | {fmt(r['complete_instance_body_forward_MAE'])} | {fmt(r['complete_instance_yaw_MAE'])} | {fmt(r['complete_instance_height_MAE'])} |")
 lines+=['',f"Moving signed yaw profiles8/9: {mw['sampled_cycle_window_events']:,} accepted signed2pi sampled-window events, {mw['sampled_window_seconds']:.6f} population-seconds ({mw['sampled_window_population_time_fraction']*100:.3f}% of moving exposure). Time-weighted worldprojected progress {mw['actual_cycle_progress']['value']:.9f}m/s vs integrated commandreference {mw['integrated_command_reference_progress']['value']:.9f}; nominal.5 cycle absolute error {mw['nominal_point5_cycle_absolute_error']['value']:.9f}m/s; integrated-reference error {mw['integrated_reference_cycle_absolute_error']['value']:.9f}. These are sampled-cycle metrics, not bodyvelocity MAE, instantaneousworldvelocity or fullcommand success rates.",'',f"Both original transition signs have complete instances covering every pre12s bin:987negative+992positive=1979 events. Later incomplete commands still contribute exposure, so whole phase metrics cannot be relabelled complete-command metrics. Original non-timeout events0; timeout20000. All thresholds retained; maxclosure {health['max_closure_error_m']:.9g}m is an observed maximum, not an added skill line.",'','Pending original acceptance:']
 lines += ['- '+x for x in pending]
 lines += ['',f"Producer indexes only: instances60000rows/31308073B/SHA8313411b…a1f63; initial20000rows/4534848B/SHA0ac3f985…8dc25. Contents not opened or fetched. {len(checks)} bounded saved-text integrity/accounting checks passed. Full numeric and exact path/bytes/SHA evidence are in adjacent JSON. No remote/SDK/GPU/model/NPZ/raw/JSONL access. Root ordinaryGit pending; no new trial/tag."]
 with (B/'HANDOFF_FROZEN_E0V2_FULL1000_SAVED_TEXT_REVIEW.md').open('x',encoding='utf8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(dict(passed=True,checks=len(checks),closed=counts['closed_instance_events'],acted=counts['acted_instance_events'],zero=counts['zero_control_instance_events'],complete_commands=counts['fully_observed_resample_to_resample_instance_events'],transition_complete=1979,moving_progress=mw['actual_cycle_progress']['value'],moving_nominal_cycle_error=mw['nominal_point5_cycle_absolute_error']['value'],skill='pending')))
if __name__=='__main__':
 try:main()
 except BaseException:put('SAVED_TEXT_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_external_artifact_content_or_remote_access=True));raise
