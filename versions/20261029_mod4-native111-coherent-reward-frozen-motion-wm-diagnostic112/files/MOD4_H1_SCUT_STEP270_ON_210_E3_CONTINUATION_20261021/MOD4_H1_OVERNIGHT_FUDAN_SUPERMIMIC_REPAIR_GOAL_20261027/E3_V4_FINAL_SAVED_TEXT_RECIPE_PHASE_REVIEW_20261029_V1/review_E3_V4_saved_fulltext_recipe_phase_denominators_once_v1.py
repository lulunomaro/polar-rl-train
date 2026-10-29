"""Bounded saved JSON/UTF8 review only; no policy/raw/NPZ/gzip/SDK/host IO."""
from pathlib import Path
import hashlib,json,math,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
SOURCE=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4/reports/E3_SOURCE210_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json'
MODEL='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 raw=SOURCE.read_bytes();v=json.loads(raw);checks=[]
 def check(name,value):
  assert value,name;checks.append(name)
 check('selected source E3_97 final',v['source_SHA']==MODEL)
 check('actual native24 / allout / original execution',v['passed_first_actual_E3_CUDA_fullrestore_native24_queue'] and v['original_terminal_and_allownout_proven'] and v['passed_original_frozen_execution'])
 check('full requested600/100warm/500steady',v['requested600_controls_100warm_500steady_complete'])
 check('original errors/integrity empty',not v['original_errors'] and not v['integrity'])
 term=v['original_terminal'];r=term['result'];native=v['native24']
 check('original waited0 / private release / no deadline',term['actual_worker_waited'] and term['returncode']==0 and term['private_EX_released'] and not term['deadline_terminated'])
 check('600/12 seconds/literal model optimizer',r['controls']==r['requested_controls']==600 and r['simulated_seconds']==12 and r['num_envs']==20000 and r['warmup_controls']==100 and r['steady_controls']==500 and not r['wall_time_limited'] and r['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and r['all17_Adam_steps']==866060 and r['actual_LR_unchanged']==.0002562890625000001)
 check('original native24 exact clock/queue',native['passed'] and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and native['legs_queue_apply']==native['wheels_queue_apply']==192 and native['trace_controls']==list(range(1,25)))
 texts=v['complete_original_own_stage_UTF8'];selected={};manifest=[]
 for row in texts:
  data=row['UTF8'].encode('utf8');name=Path(row['path']).name
  check('UTF8 size '+row['path'],len(data)==row['bytes']);check('UTF8 fullSHA '+row['path'],H(data)==row['SHA'])
  manifest.append({k:row[k] for k in ('path','bytes','SHA')})
  if name in ('E3_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json','CLOCK_TRAINING_HEALTH.json','ORIGINAL_E3_COMMAND_AND_TERMINATION_CRITERIA.json'):assert name not in selected;selected[name]=json.loads(row['UTF8'])
 report=selected['E3_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json'];clock=selected['CLOCK_TRAINING_HEALTH.json'];criteria=selected['ORIGINAL_E3_COMMAND_AND_TERMINATION_CRITERIA.json']
 check('E3 own recovery/13 recipe schema',report['kind']=='E3_97_original13recipe_phase_domain_diagnostic_v1' and report['original_source_kind']=='E3_PUBLIC_RECOVERY' and report['source_model_SHA']==MODEL and criteria['recipes']==13)
 check('original3s request/.5s stability',report['original_request_age_lt300_public100Hz_ticks_3s'] and report['original_stable_ge50_public100Hz_ticks_point5s'] and criteria['original_request_public100Hz_age_lt300_seconds']==3 and criteria['original_stable_public100Hz_ticks_ge50_seconds']==.5)
 check('real full clock600/4800',clock['control_steps']==600 and clock['actual_physics_callbacks']==clock['expected_physics_callbacks']==4800 and clock['physics_dt_s']==.0025 and clock['control_dt_s']==.02)
 check('clock no nonfinite/unknown / thresholds unchanged',not clock['nonfinite_observed'] and clock['unknown_task_reset_events']==0 and clock['termination_reason_coverage_exact'] and clock['ordinary_task_thresholds_unchanged'] and clock['closure_2mm_still_resets_only_this_environment'])
 rows=report['profiles'];check('three partitions of25 E3 phase profiles',len(rows)==75 and len({(x['phase'],x['profile']) for x in rows})==75)
 phases={p:{x['profile']:x for x in rows if x['phase']==p} for p in ('whole','warmup','steady')}
 exact_fields=('population_controls','original_new_recovery_credit_events','terminated_events','truncated_events','raw_soft_orientation_positive_controls','raw_soft_base_contact_positive_controls')
 float_partition_deltas=[]
 for k,x in phases['whole'].items():
  check('row recipe/profile identity '+str(k),x['recipe']==(k//2 if k<24 else 12))
  for name in exact_fields:check('partition '+str(k)+' '+name,x[name]==phases['warmup'][k][name]+phases['steady'][k][name])
  check('profile unique counts bounded '+str(k),x['unique_env_with_original_credit']<=x['unique_exposed_env']<=20000 and x['unique_terminated_env']<=x['terminated_events'] and x['unique_truncated_env']<=x['truncated_events'])
  for metric,value in x['mean_errors'].items():
   den=x['population_controls'];summean=math.fsum(phases[p][k]['mean_errors'][metric]*phases[p][k]['population_controls'] for p in ('warmup','steady') if phases[p][k]['population_controls'])
   float_partition_deltas.append(dict(profile=k,metric=metric,whole_mean_minus_partition_weighted_mean=None if not den else value-summean/den,interpretation='source float32 separate reductions; not a physics/bitwise gate'))
 for phase,n in (('whole',600),('warmup',100),('steady',500)):check('population coverage '+phase,sum(x['population_controls'] for x in phases[phase].values())==20000*n)
 whole=list(phases['whole'].values());request=[x for x in whole if x['profile']<24 and x['profile']%2==0];post=[x for x in whole if x['profile']<24 and x['profile']%2==1];baseline=phases['whole'][24]
 terminated=sum(x['terminated_events'] for x in whole);truncated=sum(x['truncated_events'] for x in whole)
 reason={name:sum(x['original_reason_events'][name] for x in whole) for name in whole[0]['original_reason_events']}
 check('termination union versus actual clock resets',terminated==clock['ordinary_episode_reset_events']==clock['actual_task_reset_events']==report['run_local_reset_UID_increments'])
 check('actual reset unique count',report['unique_env_reset']==clock['failed_environments'])
 check('closure original reason exact clock',reason['closure']==clock['closure_episode_reset_events'])
 check('no timeout events observed',truncated==reason['time_out']==0)
 check('credit only requesting fall recipes',sum(x['original_new_recovery_credit_events'] for x in post)==baseline['original_new_recovery_credit_events']==0)
 recipe=[]
 for q in request:
  z=phases['whole'][q['profile']+1];den=q['attempt_profile_exposures'];events=q['original_new_recovery_credit_events']
  recipe.append(dict(recipe=q['recipe'],request_profile=q['label'],request_population_controls=q['population_controls'],request_env_seconds=q['population_controls']*.02,request_unique_env=q['unique_exposed_env'],request_attempt_profile_exposures=den,original_new_credit_events=events,unique_env_with_request_credit=q['unique_env_with_original_credit'],credit_events_per_observed_request_profile_exposure=events/den if den else None,unique_credit_fraction_within_request_exposed_env=q['unique_env_with_original_credit']/q['unique_exposed_env'] if q['unique_exposed_env'] else None,
   post_request_population_controls=z['population_controls'],post_request_unique_env=z['unique_exposed_env'],post_request_attempt_profile_exposures=z['attempt_profile_exposures'],request_terminated_events=q['terminated_events'],post_request_terminated_events=z['terminated_events'],request_unique_terminated_env=q['unique_terminated_env'],post_request_unique_terminated_env=z['unique_terminated_env'],original_request_mean_metrics=q['mean_errors'],post_request_mean_metrics=z['mean_errors'],maximum_source_stable_seconds_during_request=q['maximum_source_stable_seconds'],combined_phase_attempt_exposures_not_unique_global_attempts=True,no_graduation_threshold_invented=True))
 total_credit=sum(x['original_new_recovery_credit_events'] for x in request);exposure=sum(x['attempt_profile_exposures'] for x in request)
 def weighted(items):
  den=sum(x['population_controls'] for x in items)
  return dict(population_controls=den,env_seconds=den*.02,means={k:math.fsum(x['mean_errors'][k]*x['population_controls'] for x in items if x['population_controls'])/den if den else None for k in whole[0]['mean_errors']})
 unions={name:dict(lower_bound=max(x[name] for x in whole),upper_bound=min(20000,sum(x[name] for x in whole)),exact_global_union_unavailable_without_saved_IDsets=True) for name in ('unique_exposed_env','unique_env_with_original_credit','unique_terminated_env')}
 out=dict(kind='E3_V4_complete600_original13recipe_phase_saved_text_review_v1',scope='saved JSON/UTF8 only; no PT/raw/gzip/NPZ/model/SDK/remote',epoch=time.time(),source_report=dict(path=str(SOURCE),bytes=len(raw),SHA=H(raw)),passed_text_integrity_and_execution_review=True,source_model_SHA=MODEL,actual_execution=dict(controls=600,physics_callbacks=4800,simulated_seconds=12,num_envs=20000,warmup_controls=100,steady_controls=500,literal_model_norm_STD_optimizer=True,Adam=866060,LR=.0002562890625000001,actual_waited=True,returncode=0,private_EX_released=True),original_criteria=criteria,
  totals=dict(recovery_credit_events=total_credit,observed_request_attempt_profile_exposures=exposure,credit_event_per_observed_request_profile_exposure=total_credit/exposure,ratio_not_global_success_rate=True,recipes_with_positive_credit=[x['recipe'] for x in recipe if x['original_new_credit_events']>0],recipes_without_credit=[x['recipe'] for x in recipe if x['original_new_credit_events']==0],non_timeout_termination_events=terminated,timeout_events=truncated,reset_events=report['run_local_reset_UID_increments'],unique_reset_env=report['unique_env_reset'],original_reason_events=reason,reason_sum=sum(reason.values()),reason_overlap_excess_not_extra_termination=sum(reason.values())-terminated,closure_reason_share_of_termination_union=reason['closure']/terminated),
  measured_population_weighted_metrics=dict(requesting_fall=weighted(request),post_request_fall=weighted(post),normal_recipe12_zero_command=weighted([baseline]),all_population=weighted(whole)),
  per_recipe=recipe,original75_profile_phase_rows=rows,unique_env_union_bounds=unions,
  metric_semantics=dict(all_E3_command3='original zero from RecoveryEnv.publish; recovery task, not E2 moving or W35standing complement',baseline='only recipe12 is authored normal-zero-command baseline; other zero-command samples can be fallen/requesting',request='source age_before<300 and recipe!=12; actual age advances2 per50Hzcontrol/public100Hz',credit='original terminal-before-reset credited false→true; request required; gravity_z<-.984807753 and root_speed<.03 and angular_speed<.2 stable>=50 public100Hz ticks=.5s',attempt_profile_exposures='distinct run-local episode UID exposures WITHIN each profile/partition; request and post or warm and steady can represent SAME attempt; never sum as global attempts',credit_events_vs_unique='each profile provides exact unique credited env; cross-profile union IDsets not in text, only bounds',raw_soft_positive_controls='unmasked orientation/base-contact positives per population-control, not termination events or env IDs; original request masks retained',peak_upright_gain='sum of positive changes in source running peak; not recovery credit',maximum_live_profile_seconds='source resets continuity at warmup→steady; whole takes max of partitions, NOT true continuous duration across boundary',world_progress='E3 emits zero commands; body_vx_abs is motion magnitude, not E2 cycle progress or a nonzero command tracking score',MAE_means='population-control weighted source aggregates; per-env distributions/tails not reconstructed',trace='44 selected controls ending576; not full per-env or full WM transfer'),
  pending_original_skill_conditions=['No inherited old graduation: recipes0/5/11 have zero original recovery credits in this case','Only141 original credit events versus414048 observed request-profile exposures, repeated failures concentrated; no global attempt success estimate','Per-profile/phase denominators saved, but full per-attempt timelines and cross-profile unique ID unions absent from saved text','12s case does not establish original complete episode/timeout coverage or held-out seeds/DR generalization','Maximum continuity field splits warmup boundary; cannot prove full continuous requests/stability from its max alone','Raw soft positives and upright gain are not task credit; original failures/reset values preserved','Selected partial domain traces are not complete typed WM dataset'],
  floating_partition_mean_deltas=float_partition_deltas,checks=checks,check_count=len(checks),saved_fulltext_manifest=manifest,original_large_artifact_metadata_reference=v['large_artifact_metadata_only'],no_binary_open_stat_hash_decode_or_download=True,no_new_model_statistics_actor_or_extra_simulation=True,skill_graduation=False,complete_WM_dataset=False,Git_status='PENDING_ROOT_ORDINARY_SUPPLEMENT')
 put('E3_V4_COMPLETE600_RECIPE_PHASE_TEXT_REVIEW_ACTUAL.json',out)
 table=['|recipe|request exposures|credit events|credited / exposed env|request term events|post term events|','|---:|---:|---:|---:|---:|---:|']
 for x in recipe:table.append(f"|{x['recipe']}|{x['request_attempt_profile_exposures']}|{x['original_new_credit_events']}|{x['unique_env_with_request_credit']}/{x['request_unique_env']}|{x['request_terminated_events']}|{x['post_request_terminated_events']}|")
 narrative=f'''E3 V4 saved-text review — execution passed; skill not qualified

600 controls/12s/N20k completed with actual4800 physics callbacks, native24 queue proof and original core/norm/STD/17Adam866060/LR.0002562890625000001 unchanged. Original waited0/allout/private released; errors/integrity empty. Source E3_97 model1cd999…7c84b8. No additional model/raw/NPZ/gzip/host reads.

Recovery credits: {total_credit} original events / {exposure} observed REQUEST-PROFILE attempt exposures ({100*total_credit/exposure:.6f}%). This is an exposure ratio, NOT global success probability. Per-recipe unique credited/env denominators are shown; repeated events are not unique environments. Recipes0/5/11 have zero credit; recipe12 baseline has no request and zero credit is not a recovery failure.

{chr(10).join(table)}

Non-timeout reset/termination union {terminated}, across {report['unique_env_reset']} unique reset envs; timeout0. Original reasons closure{reason['closure']}, orientation{reason['bad_orientation']}, base_contact{reason['base_contact']} overlap by{sum(reason.values())-terminated}; reason sum is not union. Original per-env2mm resets preserved; max source closure{clock['max_closure_error_m']:.9f}m is not a new whole-batch stop gate.

Original recovery: request first3s, gravity_z<-.984807753, root3D speed<.03m/s and angular speed<.2rad/s continuously50 public100Hz ticks=.5s; original credited edge before reset. Raw soft contact/orientation positives and running-peak gain are NOT recovery credits. All commands here are original zero; fallen zero-command cases are not 'standing'. Only recipe12 is normal-zero-command baseline. This case does not test E2 nonzero tracking or H1 true270 jump.

All75 source profile/whole-warm-steady rows and their exact population/unique/exposure/error denominators are retained in JSON. Full12M population-controls=2M warm+10M steady. Request/post and warm/steady exposures may overlap the SAME attempt; do not add them as unique global attempts. Global credited-env union bounded{unions['unique_env_with_original_credit']['lower_bound']}..{unions['unique_env_with_original_credit']['upper_bound']} from text only, not an exact ID union. Source maximum_live_profile_seconds resets at warmup boundary; whole max is not continuous full-window max.

Skill remains pending: zero-credit recipes and heavy repeated resets; no complete per-attempt timeline/ID unions, no full episode timeout/held-out coverage, no existing original graduation threshold proven. Selected44 traces endingcontrol576 are partial diagnostic records, not a complete WM dataset. {len(checks)} saved-text/integer consistency checks passed. All prior false/repair evidence remains unchanged. Ordinary Git pending root.
'''
 with (B/'REVIEW_E3_V4_RECIPE_PHASE_EXPOSURE.md').open('x',encoding='utf8') as f:f.write(narrative)
 print(json.dumps(dict(passed_text_review=True,credits=total_credit,request_exposures=exposure,terminated=terminated,closure=reason['closure'],unique_reset_env=report['unique_env_reset'],checks=len(checks),skill_graduation=False)))
if __name__=='__main__':
 B.mkdir(exist_ok=True)
 try:main()
 except BaseException:
  with (B/('ORIGINAL_REVIEW_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),scope='saved-text only'),f,indent=2)
  raise
