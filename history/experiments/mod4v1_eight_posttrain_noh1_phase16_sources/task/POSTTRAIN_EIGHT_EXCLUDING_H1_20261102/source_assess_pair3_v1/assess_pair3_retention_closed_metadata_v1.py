"""SOURCE-onlypair3post-closemetadataassessor. Neverreadfuturepointeronimport.
RealCLIonparentonly: collectedJSON/Task/closedstdout,nomodel/rawtrajectory/
PT/NPZ/JSONL/SDK/SSH/C/GO/Git. Noactualbestiscreatedbysourcetests.
"""
from pathlib import Path
import argparse,hashlib,json,math,re
D=Path(__file__).resolve().parents[1];T=D.parent
ROLES=('E3','SLOPE135');ORDINARY=('bad_orientation','base_contact','closure','mimic','low_base')
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
CAPACITY=re.compile(r'overflow|out of memory|CUDA error|buffer.*(too small|insufficient|exceeded)|contact.*capacity.*exceeded',re.I)
class EvidenceError(ValueError):pass
def need(ok,msg):
 if not ok:raise EvidenceError(msg)
def finite(x):return type(x)in(int,float)and math.isfinite(x)

def recovery_scope(skill,baseline_skill):
 """Conservativeoriginalcreditedfieldcomparison; scopegapdoesnotfakeapass.
 Twelveinitialrequestedrecipes0..11total74; recipe12normal6excluded.
 """
 result=dict(scope_complete=False,scope_gaps=[],credit_nondecrease_per_same_recipe=False,credited_evidence_beyond_zero_zero=False,metric_allows_candidate=False,credited_metric='first_episode_original_stable_credit_from_recovery.credited_and_first_episode_live_NOT_delta',normal_recipe_id=12,normal_excluded_from_rescue_denominator=True,original_full_E3_graduated=False)
 try:
  tables=[]
  for label,s in [('candidate',skill),('baseline',baseline_skill)]:
   if s['stable50_public100Hz_age_equals_seconds']!=.5 or s['stable50_equals_policy_controls']!=25 or s['request300_age_seconds']!=3. or s['no_reset_stitched_credit']is not True:result['scope_gaps'].append(label+':original50public100Hz/request300/firstepisodecontractnotverified')
   rr=s['original_recovery_recipe_rows'];ids=[r['recipe']for r in rr]
   if len(rr)!=13 or len(set(ids))!=13 or set(ids)!=set(range(13)):result['scope_gaps'].append(label+':expected12rescuerecipesplusnormalrow12')
   table={r['recipe']:r for r in rr}
   for r in rr:
    required=('initial_envs','first_episode_original_stable_credit','first_episode_physical_terminated')
    if not all(type(r[k])is int and r[k]>=0 for k in required)or r['first_episode_original_stable_credit']>r['initial_envs']or r['first_episode_physical_terminated']>r['initial_envs']:result['scope_gaps'].append(label+':invalidexistingperrecipecounters')
    if type(r['original_request'])is not bool or r['original_request']!=(r['recipe']!=12):result['scope_gaps'].append(label+':originalrequestmaskmismatch')
   tables.append(table)
  now,old=tables
  if result['scope_gaps']:return result
  nowN=sum(now[i]['initial_envs']for i in range(12));oldN=sum(old[i]['initial_envs']for i in range(12));normalN=now[12]['initial_envs'];oldNormal=old[12]['initial_envs'];result.update(initial_rescue_environments=nowN,baseline_initial_rescue_environments=oldN,normal_environments_excluded=normalN,baseline_normal_environments_excluded=oldNormal,rescue_recipe_count=12,total_recipe_rows=13)
  if nowN!=oldN or nowN!=74 or normalN!=oldNormal or normalN!=6:result['scope_gaps'].append('initialrescue74/normal6denominatornotcomparable')
  if any(now[i]['initial_envs']!=old[i]['initial_envs']for i in range(13)):result['scope_gaps'].append('same-recipeinitialdenominatorsdiffer')
  comparisons=[dict(recipe=i,initial_rescuable=now[i]['initial_envs'],baseline_initial_rescuable=old[i]['initial_envs'],first_episode_credited=now[i]['first_episode_original_stable_credit'],baseline_first_episode_credited=old[i]['first_episode_original_stable_credit'],first_episode_physical_terminated=now[i]['first_episode_physical_terminated'],baseline_first_episode_physical_terminated=old[i]['first_episode_physical_terminated'])for i in range(12)]
  credit=sum(r['first_episode_credited']for r in comparisons);before=sum(r['baseline_first_episode_credited']for r in comparisons);keep=all(r['first_episode_credited']>=r['baseline_first_episode_credited']for r in comparisons)
  result.update(same_recipe_comparisons=comparisons,first_episode_credited=credit,baseline_first_episode_credited=before,normal_recipe_row_reported_not_scored=now[12],credit_nondecrease_per_same_recipe=keep,credited_evidence_beyond_zero_zero=not(credit==0 and before==0),strict_credited_count_improvement=credit>before,stable50_public100Hz_age_equals_seconds=.5,stable50_equals_policy_controls=25,request300_age_seconds=3.,both_zero_no_improvement_evidence=credit==0 and before==0)
  result['scope_complete']=not result['scope_gaps'];result['metric_allows_candidate']=result['scope_complete']and keep and result['credited_evidence_beyond_zero_zero']
 except (KeyError,TypeError,ValueError)as error:
  result['scope_gaps'].append('Missing_or_incompatible_actual_recovery_scope_metadata:'+str(error));result['metric_allows_candidate']=False;result['scope_complete']=False
 return result


def assess_pair3(closed,baseline,training,contracts,tasks,stdout_errors):
 need(closed['pair']==3 and set(closed['roles'])==set(ROLES)and closed['parent_error']is None,'Actualpair3closedroles/noerrorrequired');s=closed['final'];ex=closed['parent_exit'];need(s is not None and ex is not None,'Neverassesspendingwindow')
 need(ex['errors']==[]and ex['all_own_children_waited']is True and ex['original_single_GPU_private_EX_released']is True and ex['original_global_finite_EX_released']is True,'Originalclosewait/twoEXrelease')
 need(s['all_pair_actual_execution_complete']is True and len(s['rows'])==2 and{r['role']for r in s['rows']}==set(ROLES),'Bothoriginal80windowsRC0')
 need(training['pair']==3 and training['original_actual_cost_settled']is True and training['original_leases_released']is True and training['parent_errors']==[]and training['H1_excluded']is True,'Actualtrainingclosedproducerrequired')
 b={r['role']:r for r in baseline['rows']};pins={r['role']:r for r in training['rows']};need(set(pins)==set(ROLES),'Exactactualpair3candidatepins');waits=ex['child_waits'];need(len(waits)==2 and {w['pid']for w in waits}=={r['pid']for r in s['rows']}and all(w['returncode']==0 and w['actual_waited']is True for w in waits),'Actualownparentwaitidentities')
 result_rows=[];starts=[];ends=[]
 for row in s['rows']:
  role=row['role'];f=row['data'];task=tasks[role];pin=pins[role];old=b[role];cache=f['source_cache'];expected=160 if role=='E3'else 750
  need(row['returncode']==0 and row['actual_waited']is True and row['passed_execution']is True and row['error']is None and row['ready']is True and row['pre_close']is True,'Actualclosedexecution '+role)
  need(f['role']==task['role']==role and f['group_id']==task['group_id']==s['group_id']and f['GPU_UUID']==task['GPU_UUID']==s['GPU_UUID'],'Sameactualgroup '+role)
  need(pin['returncode']==0 and pin['all_own_child_waited']is True and len(pin['actual_Adam17_unique_from_producer'])==1,'Actualcandidatecompleteproducer '+role)
  need(task['kind']==task['purpose']==KIND and task['num_envs']==80 and task['seed']==20260928 and len(task['eval_members'])==2 and set(task['eval_members'])==set(ROLES),'Originalseedandtwofresh80members')
  need(task['asset_SHA']==USD and task['contract_SHA']==CONTRACT and task['policy_hz']==50 and task['feedback_hz']==100 and task['physics_dt']==.0025 and task['TGS']==[32,4]and task['closure_m']==.01 and task['mimic_rad']==.01 and task['gas_N']==400 and task['stiffness_N_m']==2000 and task['damping_Ns_m']==3.,'OriginalassetclockTGSthresholdgasprotocol')
  need(task['fresh_fullDR_cohort']is True and task['saved20k_DR_physically_applied']is False and task['state_projection_or_slicing']is False and task['whole20k_savedrestore_claim']is False,'Not20kDRprojection')
  need(task['source_path']==pin['checkpoint']and task['source_SHA']==cache['source_SHA']==pin['SHA']and task['source_bytes']==pin['bytes']and task['source_iteration']==pin['actual_saved_iteration']and task['source_Adam17']==pin['actual_Adam17_unique_from_producer'][0]and task['source_LR']==pin['actual_saved_LR'],'Actualsavedcandidatepin')
  need(f['passed_execution']is True and f['controls']==task['controls']==old['controls']==expected and f['seconds']==old['seconds']==expected*.02 and f['optimizer_updates']==0,'OriginalE3/S135window')
  need(stdout_errors[role]==[],'Closedstdoutcapacityerror '+role)
  terms=f.get('termination_events_by_reason',f.get('termination_counts'));need(terms is not None and all(type(terms[k])is int and terms[k]>=0 for k in ORDINARY),'Originalordinarytermfacts');ordinary_keep=all(terms[k]<=old['termination_events'][k]for k in ORDINARY)
  start=f.get('first_eval_epoch',f.get('wall_start_epoch'));end=f.get('last_eval_epoch',f.get('wall_end_epoch'));need(finite(start)and finite(end)and start>=s['common_start_epoch']and end>start,'Actualcontrolledwindow');starts.append(start);ends.append(end)
  item=dict(role=role,actual_eval_RC=0,actual_scope_seconds=f['seconds'],actual_controls=f['controls'],termination_events=terms,baseline_termination_events=old['termination_events'],ordinary_failure_nonincrease=ordinary_keep,ordinary_failure_event_sum=sum(terms[k]for k in ORDINARY),baseline_ordinary_failure_event_sum=sum(old['termination_events'][k]for k in ORDINARY),closed_stdout_capacity_errors=[],new_PPO_updates_in_eval=0,original_full_expert_graduated=False)
  candidate=dict(path=pin['checkpoint'],SHA=pin['SHA'],bytes=pin['bytes'])
  if role=='E3':
   need(row['started']is True and f['num_envs']==80 and f['physics_callbacks']==expected*8 and f['feedback_samples']==expected*2,'E3actualstarted80clock')
   need(cache['source_path']==pin['checkpoint']and cache['physical_byte_opens']==cache['SHA_calculations']==cache['decodes']==1 and cache['source_iteration']==pin['actual_saved_iteration']and cache['source_Adam17']==pin['actual_Adam17_unique_from_producer'][0]and cache['source_LR']==pin['actual_saved_LR'],'E3fullcandidatecachepin')
   need(cache['all_original_root_and_nested_cached']is True and cache['wholecachedidentity_passed']is True and cache['live_actor_STD_strict']is True and cache['source20k_DR_history_applied']is False and cache['source20k_state_sliced']is False,'E3wholeCPUcacheactoronly')
   need(f['D0_D7_fresh_audit_before']['actual_parameters_pass']is True and f['D0_D7_fresh_audit_after']['actual_parameters_pass']is True,'E3originalD0-D7actualbeforeafter')
   recovery=recovery_scope(f.get('skill',{}),old.get('skill',{}));nonreg=recovery['metric_allows_candidate']and ordinary_keep
   item.update(original_recovery=recovery,scopeGap=not recovery['scope_complete'],scope_gap_reasons=recovery['scope_gaps'],initial_rescue_recipe_policy='12requestedrecipes0..11(74);normalrecipe12(6)excluded',zero74_baseline_not_full_E3_pass=True,firstepisode_credit_NOT_generic_delta=True,conservative_selection_rule='Sameinitialrecipe/denominatororiginalcreditednondecrease+ordinaryfailurenonincrease; bothzero=>Mother; scopeGap=>Mother,notnewgraduation')
   mother=dict(path=old['source_cache']['source_path'],SHA=old['source_cache']['source_SHA'])
  else:
   barrier=f['group_barrier']['barrier_start'];need(f['actor_calls']==expected and barrier['group_id']==s['group_id']and barrier['GPU_UUID']==s['GPU_UUID']and barrier['all_members_ready']is True and len(barrier['members'])==2 and set(barrier['members'])==set(ROLES),'S135originalactorcontrols+commonbarrier')
   need(f['physics']==expected*8 and f['feedback']==expected*2 and cache['source_bytes']==pin['bytes']and cache['physical_byte_opens']==cache['SHA_calls']==cache['decodes']==1,'S135candidatecacheclocks')
   meta=cache['metadata'];need(meta['iteration']==pin['actual_saved_iteration']and len(meta['Adam17'])==17 and set(meta['Adam17'])==set(pin['actual_Adam17_unique_from_producer'])and meta['LR']==pin['actual_saved_LR']and meta['STD6']==pin['actual_STD6_from_producer'],'S135ownnewcoreSTD')
   need(cache['entire_original_root_and_nested_identity_preserved']is True and cache['live_actor_STD_loaded']is True and cache['saved20k_DR_physically_applied']is False and cache['saved20k_history_sliced']is False,'S135whole20kcacheunsliced')
   for name in('fresh_fullDR_before','fresh_fullDR_after'):need(f[name]['fresh_N80_D0_D7_enabled']is True and f[name]['actual_parameters']['actual_parameters_pass']is True,'S135originalfreshDR '+name)
   groups=f['metrics']['groups'];rr=f['metrics']['rows'];before=old['original_endpoint_groups'];need(set(groups)=={'ascending','descending','stand'}and sum(g['environments']for g in groups.values())==80 and len(rr)==80,'S135actualgroup80notabsenttopnum_envs')
   need(all(sum(z['group']==k for z in rr)==g['environments']for k,g in groups.items()),'S135declaredgroupcounts')
   same=all(groups[k]['environments']==before[k]['environments']for k in groups);crossing=all(groups[k][q]>=before[k][q]for k in('ascending','descending')for q in('complete_envs','contact_confirmed_envs'));stand=dict(total=sum(z['group']=='stand'for z in rr),no_failure=sum(z['group']=='stand'and z['first_ordinary_failure_control']is None for z in rr));stand_keep=stand['total']==old['stand_no_ordinary_failure']['total']and stand['no_failure']>=old['stand_no_ordinary_failure']['no_failure'];nonreg=same and crossing and stand_keep and ordinary_keep
   item.update(original_endpoint_groups=groups,baseline_endpoint_groups=before,stand_no_ordinary_failure=stand,baseline_stand_no_ordinary_failure=old['stand_no_ordinary_failure'],same_declared_group_sizes=same,endpoint_contact_nondecrease=crossing,stand_no_ordinary_failure_nondecrease=stand_keep,stand_crossing_required=False,baseline_from_own_SLOPE135_not_Curb=True,scopeGap=False,scope_gap_reasons=[],conservative_selection_rule='OwnS135ascending25/27descending27/27stand26/26endpoint/contactandordinaryfactsnotregressed; nostandcrossing/newgraduation')
   mother={k:contracts[role]['source'][k]for k in('path','SHA','bytes')};need(mother['SHA']==old['source_cache']['source_SHA'],'OwnS135frozenmotheridentity')
  item.update(selection='CANDIDATE'if nonreg else'FROZEN_MOTHER',selected_source=candidate if nonreg else mother,candidate_preserved=candidate,frozen_mother_preserved=mother,do_not_overwrite_mother_or_failed_candidate=True,whole_source_cache_identity_preserved=True,selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation=True,unpaired_trajectory_after_policy_dependent_resets_not_causal_claim=True);result_rows.append(item)
 need(min(ends)>max(starts),'Actualcommoncontrolwindowoverlap')
 return dict(kind='ACTUAL_PAIR3_ORIGINAL_SCOPE_FROZEN_RETENTION_AND_CONSERVATIVE_BEST_SELECTION',retention_assessment_complete=True,H1_excluded=True,rows=result_rows,actual_control_windows_overlap_seconds=min(ends)-max(starts),do_not_overwrite_mother_or_failed_candidate=True,all_scope_claims_limited=True,selection_is_not_original_skill_graduation_rule=True,full20k_or_hardware_graduated=False,next_pair_dispatch_requires_real_assessment_and_explicit_selection_not_fake_pass=True,remaining_PPO_not_started_by_thisprocessor=True,original_asset_physics_rewards_skill_predicates_unchanged=True,model_PT_rawtrajectory_SDK_replay_C_GO_Git_operations=0)


def read_json(p):
 p=Path(p);need(p.suffix.lower()=='.json','MetadataJSONonly');raw=p.read_bytes();return json.loads(raw),dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def scan_closed_stdout(raw):return [x for x in raw.decode('utf-8',errors='replace').splitlines()if CAPACITY.search(x)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--closed-pointer',type=Path,default=D/'PAIR3_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json');p.add_argument('--baseline',type=Path,default=T/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json');p.add_argument('--training-summary',type=Path,default=D/'reports/PAIR3_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json');p.add_argument('--contracts',type=Path,default=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json');p.add_argument('--out',type=Path,default=D/'reports/PAIR3_FROZEN_RETENTION_BEST_SELECTION_V1.json');a=p.parse_args();need(not a.out.exists(),'Neveroverwriteexistingassessment')
 pointer,pref=read_json(a.closed_pointer);cp=Path(pointer['path']);closed,cref=read_json(cp);need(closed['parent_exit']is not None and closed['final']is not None,'Neverassesspendingwindow');baseline,bref=read_json(a.baseline);training,tref=read_json(a.training_summary);contracts,rref=read_json(a.contracts);manifest={x['relative']:x for x in closed['files']if'relative'in x};tasks={};errors={};logs=[]
 for role in ROLES:
  rel='cases/'+role+'/task.json';task,ref=read_json(cp.parent/rel);need(ref['SHA']==manifest[rel]['SHA']and ref['bytes']==manifest[rel]['bytes'],'CollectedTaskmanifestidentity');tasks[role]=task
  rel='cases/'+role+'/SDK_FULL_STDOUT_STDERR.log';raw=(cp.parent/rel).read_bytes();ref=dict(path=str(cp.parent/rel),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest());need(ref['SHA']==manifest[rel]['SHA']and ref['bytes']==manifest[rel]['bytes'],'Collectedclosedstdoutmanifestidentity');errors[role]=scan_closed_stdout(raw);logs.append(ref)
 result=assess_pair3(closed,baseline,training,contracts,tasks,errors);result.update(source=str(cp),input_metadata_refs=[pref,cref,bref,tref,rref],closed_stdout_metadata_refs=logs,only_this_collected_closed_stdout_scanned=True,no_old_raw_NPZ_JSONL_or_PT_read=True)
 with a.out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
 print(a.out);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
