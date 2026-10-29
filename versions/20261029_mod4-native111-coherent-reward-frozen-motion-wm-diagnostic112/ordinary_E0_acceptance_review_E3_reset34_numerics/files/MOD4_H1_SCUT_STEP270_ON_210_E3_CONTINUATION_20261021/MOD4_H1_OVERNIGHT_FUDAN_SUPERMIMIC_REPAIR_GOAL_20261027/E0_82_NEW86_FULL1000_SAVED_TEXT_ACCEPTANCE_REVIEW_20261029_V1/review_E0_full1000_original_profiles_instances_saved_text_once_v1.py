"""Saved terminal UTF8 review only. No PT/raw/NPZ/gzip/SDK/host reread."""
from pathlib import Path,PurePosixPath
import hashlib,json,math,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
SOURCE=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1/reports/E0_V4_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json'
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 raw=SOURCE.read_bytes();v=json.loads(raw);checks=[]
 def check(name,value):assert value,name;checks.append(name)
 check('E0 source model SHA',v['source_SHA']==MODEL)
 check('actual first/terminal/complete execution',v['passed_first_actual_E0_CUDA_fullrestore_native24_queue'] and v['passed_original_frozen_execution'] and v['original_terminal_and_allownout_proven'] and v['requested1000_controls_100warm_900steady_complete'])
 check('no original errors or integrity failures',not v['original_errors'] and not v['integrity'])
 terminal=v['original_terminal'];result=terminal['result'];native=v['native24']
 check('original waited0/released/out, no wall deadline',terminal['actual_worker_waited'] and terminal['returncode']==0 and terminal['private_EX_released'] and not terminal['deadline_terminated'])
 check('20k/1000/20s/100warm/900steady source fullstate literal',result['num_envs']==20000 and result['controls']==result['requested_controls']==1000 and result['simulated_seconds']==20 and result['warmup_controls']==100 and result['steady_controls']==900 and not result['wall_time_limited'] and result['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and result['all17_Adam_steps']==641200 and result['actual_LR_unchanged']==.00038443359375000017)
 check('actual24/192/48 and both queue192',native['passed'] and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and native['legs_queue_apply']==native['wheels_queue_apply']==192 and native['trace_controls']==list(range(1,25)))
 texts=v['complete_original_own_stage_UTF8'];manifest=[];parsed={}
 profile_rel='frozen_regression/'+result['profile_report'];check('profile report is exact relative string',isinstance(result['profile_report'],str) and '/' not in result['profile_report'] and profile_rel=='frozen_regression/E0_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json')
 for row in texts:
  data=row['UTF8'].encode('utf8');check('UTF8 bytes '+row['path'],len(data)==row['bytes']);check('UTF8 SHA '+row['path'],H(data)==row['SHA']);manifest.append({k:row[k] for k in ('path','bytes','SHA')})
  if row.get('relative')==profile_rel:
   check('exact profile path unique','panel' not in parsed);parsed['panel']=json.loads(row['UTF8']);parsed['profile_receipt']={k:row[k] for k in ('path','relative','bytes','SHA')}
  if row['path'].endswith('/CLOCK_TRAINING_HEALTH.json'):check('clock unique','clock' not in parsed);parsed['clock']=json.loads(row['UTF8'])
  if row.get('relative')=='frozen_regression/ORIGINAL_E0_COMMAND_AND_TERMINATION_CRITERIA.json':parsed['criteria']=json.loads(row['UTF8'])
 a=parsed['panel'];clock=parsed['clock'];check('correct original E0 domain',a['source_model_SHA']==MODEL and a['original_kind']=='E0_DIRECTIONAL_SPIN_V1' and a['original_world_progress_goal_m_s']==.5)
 check('actual full clock1000/8000',clock['control_steps']==1000 and clock['actual_physics_callbacks']==clock['expected_physics_callbacks']==8000 and clock['physics_dt_s']==.0025 and clock['control_dt_s']==.02)
 check('no nonfinite or unknown term resets',not clock['nonfinite_observed'] and clock['unknown_task_reset_events']==0 and clock['ordinary_task_thresholds_unchanged'] and clock['termination_reason_coverage_exact'])
 rows=a['profiles'];check('three10-profile partitions',len(rows)==30 and len({(x['phase'],x['profile']) for x in rows})==30)
 phases={p:{x['profile']:x for x in rows if x['phase']==p} for p in ('whole','warmup','steady')}
 fields=('population_controls','terminated_events','truncated_events','measured_signed_turn_events','complete_sampled_window_events')
 for k,q in phases['whole'].items():
  for field in fields:check('exact integer partition '+str(k)+' '+field,q[field]==phases['warmup'][k][field]+phases['steady'][k][field])
  check('unique env bounded '+str(k),q['unique_exposed_env']<=20000 and q['unique_terminated_env']<=q['terminated_events'] and q['unique_truncated_env']<=q['truncated_events'] and q['unique_env_with_sampled_window']<=q['unique_exposed_env'])
  if not q['population_controls']:check('unexposed profile errors null '+str(k),all(q[name] is None for name in ('body_forward_MAE','yaw_MAE','height_MAE')))
 for phase,controls in (('whole',1000),('warmup',100),('steady',900)):check('full population-controls '+phase,sum(q['population_controls'] for q in phases[phase].values())==20000*controls)
 # No cycle population-mixture shortcut: measured displacement/ref errors use window seconds.
 def weighted(items,keys):
  den=sum(q['population_controls'] for q in items)
  return dict(population_controls=den,env_seconds=den*.02,means={key:math.fsum(q[key]*q['population_controls'] for q in items if q['population_controls'])/den if den else None for key in keys})
 def cycle(items):
  sec=math.fsum(q['sampled_window_seconds'] for q in items);den=sum(q['population_controls'] for q in items)
  names=('actual_cycle_projected_progress_m_s','integrated_command_reference_progress_m_s','nominal_half_m_s_cycle_abs_error_time_weighted','integrated_reference_cycle_abs_error_time_weighted')
  return dict(population_controls=den,moving_population_env_seconds=den*.02,sampled_window_seconds=sec,sampled_window_fraction_of_mode_exposure=sec/(den*.02) if den else None,measured_signed_turn_events=sum(q['measured_signed_turn_events'] for q in items),sampled_window_events=sum(q['complete_sampled_window_events'] for q in items),window_seconds_weighted={name:math.fsum(q[name]*q['sampled_window_seconds'] for q in items if q['sampled_window_seconds'])/sec if sec else None for name in names},cycle_events_not_unique_env_or_complete_command_instances=True)
 group={}
 for phase in ('whole','warmup','steady'):
  p=phases[phase];group[phase]=dict(actual_zero_command_standing=weighted([p[0]],('body_forward_MAE','yaw_MAE','height_MAE')),straight_signed_body_command=weighted([p[1],p[2],p[3]],('body_forward_MAE','yaw_MAE','height_MAE')),pure_signed_yaw=weighted([p[4],p[5]],('body_forward_MAE','yaw_MAE','height_MAE')),transition_signed_yaw=weighted([p[6],p[7]],('body_forward_MAE','yaw_MAE','height_MAE')),moving_signed_yaw1_to2=weighted([p[8],p[9]],('body_forward_MAE','yaw_MAE','height_MAE')),moving_real_cycle=cycle([p[8],p[9]]),all_population=weighted(list(p.values()),('body_forward_MAE','yaw_MAE','height_MAE')))
 count=a['transition_phase_controls'];error=a['transition_phase_error_sums'];check('transition error exact denominators',a['transition_phase_error_denominators']==count)
 phase_rows=[]
 for ph,pname in enumerate(('warmup','steady')):
  for bin,label in enumerate(a['transition_phase_names']):
   for sign,key in enumerate((6,7)):
    den=count[ph][bin][sign];phase_rows.append(dict(partition=pname,phase_name=label,initial_sign='negative' if sign==0 else 'positive',population_controls=den,unique_exposed_env=a['transition_phase_unique_env'][ph][bin][sign],body_forward_MAE=error[ph][0][bin][sign]/den if den else None,yaw_MAE=error[ph][1][bin][sign]/den if den else None,height_MAE=error[ph][2][bin][sign]/den if den else None,denominator_controls_not_unique_env=True))
 observed_phase_controls=sum(q['population_controls'] for q in phase_rows);total_transition_controls=phases['whole'][6]['population_controls']+phases['whole'][7]['population_controls'];unknown_phase=total_transition_controls-observed_phase_controls
 check('transition written-phase missing only firstframe observer unknown',unknown_phase>=0 and observed_phase_controls<=total_transition_controls)
 inst=a['command_instances'];byprofile=inst['profiles'];check('instance summary ten profiles',len(byprofile)==10 and [q['profile'] for q in byprofile]==list(range(10)))
 instance_totals={name:sum(q[name] for q in byprofile) for name in ('closed_instance_events','fully_observed_resample_to_resample_instance_events','complete_instance_population_controls','left_censored_instance_events','window_end_right_censored_instance_events','reset_ended_instance_events','complete_transition_instances_with_all_pre12_bins')}
 check('all complete instance denominators correctly zero',instance_totals['fully_observed_resample_to_resample_instance_events']==instance_totals['complete_instance_population_controls']==instance_totals['complete_transition_instances_with_all_pre12_bins']==0)
 check('initial left-censored actual20k',instance_totals['left_censored_instance_events']==20000)
 check('instance retained count source-cap observed',inst['instance_record_rows']==instance_totals['closed_instance_events']==60000 and inst['instance_record_capacity']==80000 and not inst['instance_record_retention_limited'])
 for q in byprofile:
  check('closed origin partition observed '+str(q['profile']),q['closed_instance_events']==q['left_censored_instance_events']+q['window_end_right_censored_instance_events']+q['reset_ended_instance_events'])
  check('missing complete-instance metrics remain pending '+str(q['profile']),q['no_exposure_is_pending_not_pass'] and q['complete_instance_body_forward_MAE'] is None and q['complete_instance_yaw_MAE'] is None and q['complete_instance_height_MAE'] is None)
 non_timeout=sum(q['terminated_events'] for q in phases['whole'].values());timeout=sum(q['truncated_events'] for q in phases['whole'].values())
 check('non-timeout clock consistent0',non_timeout==clock['actual_task_reset_events']==clock['ordinary_episode_reset_events']==clock['closure_episode_reset_events']==0 and clock['timeout_excluded'])
 check('natural timeouts match observed resets20000',timeout==instance_totals['reset_ended_instance_events']==20000)
 # Existing collector omitted .jsonl from both its text and large suffix sets.
 record_path=str(PurePosixPath(v['supervisor_state']['expected']['cwd'])/'frozen_regression'/inst['record_file'])
 in_text=[r for r in texts if r['path']==record_path];in_meta=[r for r in v['large_artifact_metadata_only'] if r['path']==record_path]
 record_gap=dict(path=record_path,producer_reported_rows=inst['instance_record_rows'],producer_retention_limited=inst['instance_record_retention_limited'],collected_in_original_fulltexts=bool(in_text),collected_in_large_artifact_metadata=bool(in_meta),actual_bytes=None,actual_SHA=None,contents_not_read_or_fetched=True,not_an_exact_global_unique_or_per_instance_distribution_source_here=True)
 check('JSONL collection gap explicitly preserved',not in_text and not in_meta)
 zero_exposure_bounds=[dict(profile=q['profile'],unique_closed=q['unique_env_with_closed_instance'],unique_actually_exposed=phases['whole'][q['profile']]['unique_exposed_env'],minimum_closed_unique_env_without_observed_profile_action=max(0,q['unique_env_with_closed_instance']-phases['whole'][q['profile']]['unique_exposed_env']),closed_zero_control_count_not_saved_in_summary=True) for q in byprofile]
 report=dict(kind='E0_adapted82_original20k_full1000_saved_text_profile_transition_instance_acceptance_review_v1',epoch=time.time(),scope='saved terminal JSON and exact embedded UTF8 only; no PT/raw/NPZ/gzip/SDK/host',source_report=dict(path=str(SOURCE),bytes=len(raw),SHA=H(raw)),selected_profile_report_exact_UTF8_receipt=parsed['profile_receipt'],actual_execution=dict(num_envs=20000,controls=1000,seconds=20,warmup100=True,steady900=True,actual_physics_callbacks=8000,literal_core_norm_STD17Adam641200_LR=.00038443359375000017,waited_out_private_released=True,no_PPO_or_Cwrite=True),checks=checks,check_count=len(checks),saved_fulltext_manifest=manifest,
  source_original_criteria=parsed.get('criteria'),original_domain=dict(name='E0_DIRECTIONAL_SPIN_V1',body_frame_vx_range=[-1.5,1.5],moving_signed_abs_yaw_rad_s=[1,2],pure_signed_abs_yaw_rad_s=[1,4*math.pi],world_progress_goal_m_s=.5,command_resampling_s=[12,16],episode_s=20,transition_names=a['transition_phase_names'],standing_is_actual_source_zero_command_flag_not_moving_complement=True,no_new_global_MAE_graduation_threshold=True),
  population_weighted_means_and_cycle_window_metrics=group,original30_profile_partition_rows=rows,transition_error_rows_by_partition_bin_sign=phase_rows,transition_written_phase_coverage=dict(total_transition_population_controls=total_transition_controls,known_written_phase_controls=observed_phase_controls,initial_unknown_phase_population_controls=unknown_phase,unknown_not_filled_from_raw_phase_or_previous_control=True,phase_exposure_not_same_instance_full12s_coverage=True),
  original_command_instance_profiles=byprofile,observed_instance_totals=instance_totals,instance_summary_semantics=dict(initial_start_unknown=True,full_definition=inst['full_command_definition'],complete_command_vs_sampled2pi_are_different=True,all_complete_instance_population_denominators_zero_pending=True,closed_count_can_include_zero_control_instances=True,unique_closed_not_unique_actually_exposed=True,zero_control_per_profile_exact_unknown_without_collected_instance_rows=True,closed_event_origins=['initial-left-censored','reset-ended','window-end-right-censored'],no_cross_reset_credit=True),minimum_unexposed_closed_unique_bounds=zero_exposure_bounds,original_instance_JSONL_collection_gap=record_gap,
  termination=dict(non_timeout_events=non_timeout,timeout_events=timeout,clock_non_timeout_reset_events=clock['actual_task_reset_events'],clock_timeout_excluded=True,instance_reset_end_events=instance_totals['reset_ended_instance_events'],max_actual_closure_m=clock['max_closure_error_m'],max_actual_mimic_rad=clock['max_mimic_error_rad'],no_new_stop_gate=True),
  trace=dict(controls=a['trace_controls'],bytes_uncompressed_reported=a['trace_bytes'],retention_limited=a['trace_limited'],selected_trace_not_full_WM=True),artifact_metadata_only=v['large_artifact_metadata_only'],
  acceptance=dict(execution_and_integrity_passed=True,longer_than_original120controls_2point4s=True,conditional_moving_real_cycle_evidence_measured=True,complete_command_instance_acceptance='PENDING_ZERO_COMPLETE_INSTANCE_EXPOSURE',complete12s_transition_same_instance_acceptance='PENDING_ZERO_COMPLETE_INSTANCE_EXPOSURE',straight_exact_zero_nonsourceStanding_profile='NO_EXPOSURE',per_env_error_tails_and_full_command_distributions='UNKNOWN_SAVED_TEXT_ONLY',cross_profile_unique_IDunions='UNKNOWN_NO_IDSETS',instance_JSONL_producer_file_actual_bytes_SHA='UNKNOWN_ORIGINAL_COLLECTOR_SUFFIX_GAP',heldout_seed_and_DR_generalization='NOT_ESTABLISHED',graduation='NOT_CLAIMED_OR_INHERITED',complete_WM_dataset=False),
  no_binary_read_rehash_or_new_model_statistics=True,remote_GPU_SDK_actor_calls=0,skill_graduation=False,complete_WM_dataset=False,Git_status='PENDING_ROOT_ORDINARY_SUPPLEMENT')
 put('E0_FULL1000_PROFILE_TRANSITION_COMMAND_INSTANCE_TEXT_REVIEW_ACTUAL.json',report)
 mov=group['whole']['moving_real_cycle'];m=mov['window_seconds_weighted'];stand=phases['whole'][0]
 table=['|profile|population-controls|unique exposed env|body-v MAE|yaw MAE|timeouts|','|---|---:|---:|---:|---:|---:|']
 for q in phases['whole'].values():table.append(f"|{q['label']}|{q['population_controls']}|{q['unique_exposed_env']}|{q['body_forward_MAE']}|{q['yaw_MAE']}|{q['truncated_events']}|")
 text=f'''E0 adapted82 — complete20s execution; skill acceptance incomplete

ActualN20k1000controls/20s,100warm900steady,8000physicscallbacks. CUDAfullrestore/native24(24/192/48,bothqueue192)/core+norm+STD+17Adam641200/finalLR.00038443359375000017 unchanged. Originalwait0/out/private released; errors/integrity empty. No new actor/model/raw/NPZ/gzip/SDK/host calls in this review.

Conditional moving: {mov['population_controls']} population-controls; actual signed2pi sampled windows {mov['sampled_window_events']} events /{mov['sampled_window_seconds']:.6f} env-seconds, covering{100*mov['sampled_window_fraction_of_mode_exposure']:.4f}% of moving exposure. Time-weighted actual projected progress {m['actual_cycle_projected_progress_m_s']:.9f}m/s vs integrated command reference {m['integrated_command_reference_progress_m_s']:.9f}; time-weighted absolute reference error {m['integrated_reference_cycle_abs_error_time_weighted']:.9f}m/s. These are measured same-command/episode sampled cycle-window metrics, not population-wideMAE, instantaneous cos² comparison, full-command completion or uniqueenv count. E0 moving yaw abs1..2rad/s, not E2±4.

True source zero-command standing: {stand['population_controls']} controls/{stand['unique_exposed_env']} unique exposed env; body forwardMAE{stand['body_forward_MAE']:.9f}, yawMAE{stand['yaw_MAE']:.9f}, heightMAE{stand['height_MAE']:.9f}m. No invented MAE threshold. Nonsource-standing straight_exact_zero profile had0exposure, so is pending.

{chr(10).join(table)}

All9 original transition bins (start/hold/brake/stop/reverse/hold/brake/stop/post12stop), signs, and warm/steady errors/denominators are retained in JSON. {observed_phase_controls}/{total_transition_controls} transition controls have observed written-phase cache; {unknown_phase} initially unknown are NOT guessed. Phase coverage across manycommands is not complete12s same-instance acceptance. Stop-phase samples are not relabelled standing.

Command-instance result: {instance_totals['closed_instance_events']} closed-event records reported, including20000 initial-left-censored,20000 reset-ended,20000 window-end. Fully observed resample→resample instances ZERO; complete-instance population denominator ZERO across all10profiles; complete12s transitions ZERO. Initial phase/start unknown staysleft-censored. Source close can count0-control instances (newly resampled at end); unique_closed can exceed unique_exposed. Do not call60000 all acted attempts or add profileunique counts as a global union. Per-instance population/tails cannot be reconstructed from aggregate summaries.

Originalrecord_file {record_path} is reported60000rows/80kcap-notlimited, but prior reader suffix sets omitted .jsonl from bothfulltexts andlarge metadata. Its actual bytes/SHA are UNKNOWN here; no content/raw/host read was made to patch the gap. Existingaggregate JSON and producer declaration are preserved; not a full dataset claim.

Non-timeout events0, natural timeout-events20000; clock explicitly excludes timeouts and thus reports non-timeout reset0, while instance reset-ended counts20000. No contradiction. Actual maximum closure{clock['max_closure_error_m']:.9f}m/mimic{clock['max_mimic_error_rad']:.9f}rad retained; no newwholebatchgate. Longer20s evidence improves the prior2.4s case but does not establish full original command-life/heldout/generalization/skill graduation. Selectedtrace is partial diagnostic data, not complete WM dataset. {len(checks)} saved-text/denominator checks passed. RootordinaryGit pending.
'''
 with (B/'REVIEW_E0_FULL1000_PROFILE_INSTANCE_COVERAGE.md').open('x',encoding='utf8') as f:f.write(text)
 print(json.dumps(dict(passed_text_review=True,checks=len(checks),moving_progress=m['actual_cycle_projected_progress_m_s'],moving_reference_error=m['integrated_reference_cycle_abs_error_time_weighted'],complete_instances=0,left_censored=20000,timeout_events=timeout,non_timeout_events=0,skill_graduation=False)))
if __name__=='__main__':
 B.mkdir(exist_ok=True)
 try:main()
 except BaseException:
  with (B/('ORIGINAL_E0_SAVED_TEXT_REVIEW_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),scope='saved-text only, no binary/remote'),f,indent=2)
  raise
