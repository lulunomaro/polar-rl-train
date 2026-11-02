"""SOURCEprocessor forparentEXECUTIONONLYAFTERactualpair2closed.
NoSDK/model/PT/rawtrajectory/JSONL/NPZ/replay/C/GO/Git. Readsoneclosedcollection
JSON+itscollectedTask/stdouttextonly; pureassessoravailableforstdlibfixtures.
Conservativebestselectionisnotoriginalgraduationorpairedcausalproof.
"""
from pathlib import Path
import argparse,hashlib,json,math,re
D=Path(__file__).resolve().parents[1];T=D.parent
ROLES=('E2','CURB_INDEPENDENT113');ORDINARY=('bad_orientation','base_contact','closure','mimic','low_base')
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
CAPACITY=re.compile(r'overflow|out of memory|CUDA error|buffer.*(too small|insufficient|exceeded)|contact.*capacity.*exceeded',re.I)
class EvidenceError(ValueError):pass
def need(ok,message):
 if not ok:raise EvidenceError(message)
def finite_number(x):return type(x)in(int,float)and math.isfinite(x)
def cycles(c):
 complete=c['complete_cycle_events'];false=c['original_false_cycle_events'];partial=c['incomplete_events'];terminal=c['terminal_complete_events']
 need(all(type(x)is int and x>=0 for x in(complete,false,partial,terminal))and false<=complete and terminal<=complete,'InvalidexistingE2producercounters')
 return dict(complete=complete,false=false,accepted_true=complete-false,incomplete=partial,terminal_complete=terminal)
def body_means(f):
 values=f['skill']['body_velocity_absolute_error_time_integral_per_env'];need(len(values)==80 and all(len(x)==3 and all(finite_number(z)and z>=0 for z in x)for x in values),'E2existingbodyintegralsmustbe80x3finite')
 return [sum(x[i]for x in values)/(80*f['seconds'])for i in range(3)]

def assess_pair2(closed,baseline,training_summary,contracts,tasks,stdout_errors_by_role):
 need(closed['pair']==2 and set(closed['roles'])==set(ROLES)and closed['parent_error']is None,'Expectedactualpair2closedroles/no-parenterror')
 s=closed['final'];ex=closed['parent_exit'];need(s is not None and ex is not None,'ActualclosedFINAL/parentexitrequired')
 need(ex['errors']==[]and ex['all_own_children_waited']is True and ex['original_single_GPU_private_EX_released']is True and ex['original_global_finite_EX_released']is True,'Originalallwait/twoEXrelease/noerrorsrequired')
 need(s['all_pair_actual_execution_complete']is True and len(s['rows'])==2 and {r['role']for r in s['rows']}==set(ROLES),'BothactualexecutionRC0complete')
 need(training_summary['pair']==2 and training_summary['original_actual_cost_settled']is True and training_summary['original_leases_released']is True and training_summary['parent_errors']==[] and training_summary['H1_excluded']is True,'Candidateproducertrainingmustalreadybeclosedsettled')
 b={r['role']:r for r in baseline['rows']};saved={r['role']:r for r in training_summary['rows']};need(set(saved)==set(ROLES),'Actualtwo candidateproducerrowsrequired');rows=[];starts=[];ends=[]
 waits=ex['child_waits'];need(len(waits)==2 and {w['pid']for w in waits}=={r['pid']for r in s['rows']}and all(w['actual_waited']is True and w['returncode']==0 for w in waits),'Parentactualchildwaitidentity/RC0required')
 for row in s['rows']:
  role=row['role'];f=row['data'];task=tasks[role];pin=saved[role];old=b[role];cache=f['source_cache']
  need(row['returncode']==0 and row['actual_waited']is True and row['passed_execution']is True and row['error']is None and row['ready']is True and row['pre_close']is True,'Actualclosedreadystartwait/RC0 '+role)
  need(f['role']==role and task['role']==role and f['group_id']==task['group_id']==s['group_id']and f['GPU_UUID']==task['GPU_UUID']==s['GPU_UUID'],'Sameactualgroup/sourceworker '+role)
  need(pin['returncode']==0 and pin['all_own_child_waited']is True,'Actualcandidatecompleteproducer '+role)
  need(task['kind']==task['purpose']==KIND and task['num_envs']==80 and task['seed']==20260928 and set(task['eval_members'])==set(ROLES)and len(task['eval_members'])==2,'Originalfresh80seed/protocol '+role)
  need(task['asset_SHA']==USD and task['contract_SHA']==CONTRACT and task['policy_hz']==50 and task['feedback_hz']==100 and task['physics_dt']==.0025 and task['TGS']==[32,4]and task['closure_m']==.01 and task['mimic_rad']==.01 and task['gas_N']==400 and task['stiffness_N_m']==2000 and task['damping_Ns_m']==3.,'Original2c/baephysicsprotocol '+role)
  need(task['fresh_fullDR_cohort']is True and task['saved20k_DR_physically_applied']is False and task['state_projection_or_slicing']is False and task['whole20k_savedrestore_claim']is False,'Freshcohortnotsaved20kprojection '+role)
  need(task['source_path']==pin['checkpoint']and task['source_SHA']==cache['source_SHA']==pin['SHA']and task['source_bytes']==pin['bytes']and task['source_iteration']==pin['actual_saved_iteration']and task['source_Adam17']==pin['actual_Adam17_unique_from_producer'][0]and len(pin['actual_Adam17_unique_from_producer'])==1 and task['source_LR']==pin['actual_saved_LR'],'Actualsavedcandidatepin '+role)
  need(f['passed_execution']is True and f['controls']==old['controls']==task['controls']and f['seconds']==old['seconds']and f['optimizer_updates']==0,'Originalwindowcontrols/nolearn '+role)
  need(stdout_errors_by_role[role]==[],'Closedstdoutcapacity/CUDAerror '+role)
  term=f.get('termination_events_by_reason',f.get('termination_counts'));need(term is not None and all(type(term[k])is int and term[k]>=0 for k in ORDINARY),'Existingterminationfactsrequired '+role)
  ordinary_keep=all(term[k]<=old['termination_events'][k]for k in ORDINARY)
  start=f.get('first_eval_epoch',f.get('wall_start_epoch'));end=f.get('last_eval_epoch',f.get('wall_end_epoch'));need(finite_number(start)and finite_number(end)and start>=s['common_start_epoch']and end>start,'Actualcommoncontrolwindow '+role);starts.append(start);ends.append(end)
  item=dict(role=role,actual_eval_RC=0,actual_scope_seconds=f['seconds'],actual_controls=f['controls'],source_candidate_SHA=pin['SHA'],termination_events=term,baseline_termination_events=old['termination_events'],ordinary_failure_nonincrease=ordinary_keep,ordinary_failure_event_sum=sum(term[k]for k in ORDINARY),baseline_ordinary_failure_event_sum=sum(old['termination_events'][k]for k in ORDINARY),closed_stdout_capacity_errors=[],new_PPO_updates_in_eval=0,original_full_expert_graduated=False)
  candidate=dict(path=pin['checkpoint'],SHA=pin['SHA'],bytes=pin['bytes'])
  if role=='E2':
   need(row['started']is True,'E2actualWORKER_EVAL_STARTEDevidence')
   need(f['num_envs']==80 and f['physics_callbacks']==f['controls']*8 and f['feedback_samples']==f['controls']*2,'E2actual80clocks')
   need(cache['source_path']==pin['checkpoint']and cache['physical_byte_opens']==cache['SHA_calculations']==cache['decodes']==1 and cache['source_iteration']==pin['actual_saved_iteration']and cache['source_Adam17']==pin['actual_Adam17_unique_from_producer'][0]and cache['source_LR']==pin['actual_saved_LR'],'E2wholecandidateCPUcacheidentity')
   need(cache['all_original_root_and_nested_cached']is True and cache['wholecachedidentity_passed']is True and cache['live_actor_STD_strict']is True and cache['source20k_DR_history_applied']is False and cache['source20k_state_sliced']is False,'E2whole20kcacheunslicedactoronly')
   need(f['D0_D7_fresh_audit_before']['actual_parameters_pass']is True and f['D0_D7_fresh_audit_after']['actual_parameters_pass']is True,'E2originalfreshDRbeforeafter')
   means=body_means(f);oldmeans=old['diagnostic_fullwindow_body_abs_error_mean_vx_vy_yaw'];need(len(oldmeans)==3 and all(finite_number(x)for x in oldmeans),'E2baselinebodydiagnostics')
   facts=f['skill']['original_E2_sameUID_cycle_facts'];oldfacts=old['skill']['original_E2_sameUID_cycle_facts'];nowcycles=cycles(facts);oldcycles=cycles(oldfacts)
   body_keep=all(n<=o for n,o in zip(means,oldmeans));true_keep=nowcycles['accepted_true']>=oldcycles['accepted_true'];nonreg=body_keep and ordinary_keep and true_keep
   item.update(diagnostic_body_abs_error_mean_vx_vy_yaw=means,baseline_body_abs_error_mean_vx_vy_yaw=oldmeans,delta_vx_vy_yaw=[n-o for n,o in zip(means,oldmeans)],all_three_existing_bodydiagnostics_nonworse=body_keep,original_signed2pi_cycle_counts=nowcycles,baseline_original_signed2pi_cycle_counts=oldcycles,original_accepted_true_count_nondecrease=true_keep,E2_world_getter_phase_reference_observer_gap=True,baseline_zero_true_0of187_is_not_full_skill_pass=True,world_metric_not_used_for_blind_tuning_or_graduation=True,original_cycle_producer_metadata=facts['producer'],observer_producer_source_SHA_label=facts['producer'].get('source_SHA'),actor_candidate_source_SHA=pin['SHA'],observer_label_is_not_actor_identity=True,conservative_selection_rule='Existingbodydiagnosticsallnonworse+ordinaryfailuresnonincrease+originalacceptedtruecountnotlower; notoriginalgraduationrule',no_diagnostic_regression_in_this_screen=nonreg)
   mother=dict(path=old['source_cache']['source_path'],SHA=old['source_cache']['source_SHA'])
  else:
   barrier=f['group_barrier']['barrier_start'];need(f['actor_calls']==f['controls']and barrier['group_id']==s['group_id']and barrier['GPU_UUID']==s['GPU_UUID']and barrier['all_members_ready']is True and len(barrier['members'])==2 and set(barrier['members'])==set(ROLES),'CurbactualFINALactorcontrols+commonbarrier;noWORKER_EVAL_STARTEDfileinoriginalE1worker')
   groups=f['metrics']['groups'];rr=f['metrics']['rows'];oldgroups=old['original_endpoint_groups'];need(set(groups)=={'ascending','descending','stand'}and sum(g['environments']for g in groups.values())==80 and len(rr)==80,'Curbactualnum_envsfromgroupssum80/notabsenttopfield')
   need(all(sum(z['group']==k for z in rr)==g['environments']for k,g in groups.items()),'Curbrowgroupsmatchdeclaredcounts')
   need(f['physics']==f['controls']*8 and f['feedback']==f['controls']*2 and cache['source_bytes']==pin['bytes']and cache['physical_byte_opens']==cache['SHA_calls']==cache['decodes']==1,'Curbwholecandidatecache/clocks')
   meta=cache['metadata'];need(meta['iteration']==pin['actual_saved_iteration']and len(meta['Adam17'])==17 and set(meta['Adam17'])==set(pin['actual_Adam17_unique_from_producer'])and meta['LR']==pin['actual_saved_LR']and meta['STD6']==pin['actual_STD6_from_producer'],'CurbactualupdatedcoreandSTDcache')
   need(cache['entire_original_root_and_nested_identity_preserved']is True and cache['live_actor_STD_loaded']is True and cache['saved20k_DR_physically_applied']is False and cache['saved20k_history_sliced']is False,'Curbwhole20kretainednotprojected')
   for key in('fresh_fullDR_before','fresh_fullDR_after'):need(f[key]['fresh_N80_D0_D7_enabled']is True and f[key]['actual_parameters']['actual_parameters_pass']is True,'CurboriginalfullDR '+key)
   stand=dict(total=sum(z['group']=='stand'for z in rr),no_failure=sum(z['group']=='stand'and z['first_ordinary_failure_control']is None for z in rr));same_counts=all(groups[k]['environments']==oldgroups[k]['environments']for k in groups)
   crossing=all(groups[k][q]>=oldgroups[k][q]for k in('ascending','descending')for q in('complete_envs','contact_confirmed_envs'));stand_keep=stand['total']==old['stand_no_ordinary_failure']['total']and stand['no_failure']>=old['stand_no_ordinary_failure']['no_failure'];nonreg=same_counts and crossing and stand_keep and ordinary_keep
   item.update(original_endpoint_groups=groups,baseline_endpoint_groups=oldgroups,stand_no_ordinary_failure=stand,baseline_stand_no_ordinary_failure=old['stand_no_ordinary_failure'],same_declared_group_sizes=same_counts,endpoint_contact_nondecrease=crossing,stand_no_ordinary_failure_nondecrease=stand_keep,stand_crossing_required=False,original_scoped_skill_facts_not_regressed=nonreg,conservative_selection_rule='Existingownascending/descendingendpoint+contactandstandnoordinaryfailurefactsnondecrease; nostandcrossingornewgraduation')
   mother={k:contracts[role]['source'][k]for k in('path','SHA','bytes')};need(mother['SHA']==old['source_cache']['source_SHA'],'CurbfrozenmotherbaselineSHA')
  item.update(selection='CANDIDATE'if nonreg else'FROZEN_MOTHER',selected_source=candidate if nonreg else mother,candidate_preserved=candidate,frozen_mother_preserved=mother,do_not_overwrite_mother_or_failed_candidate=True,whole_source_cache_identity_preserved=True,selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation=True,unpaired_trajectory_after_policy_dependent_resets_not_causal_claim=True);rows.append(item)
 need(min(ends)>max(starts),'Actualsamegrouppaircontrolwindowoverlap')
 return dict(kind='ACTUAL_PAIR2_ORIGINAL_SCOPE_FROZEN_RETENTION_AND_CONSERVATIVE_BEST_SELECTION',retention_assessment_complete=True,H1_excluded=True,rows=rows,actual_control_windows_overlap_seconds=min(ends)-max(starts),do_not_overwrite_mother_or_failed_candidate=True,all_scope_claims_limited=True,selection_is_not_original_skill_graduation_rule=True,full20k_or_hardware_graduated=False,next_pair_dispatch_requires_real_assessment_and_explicit_selection_not_fake_pass=True,remaining_PPO_not_started_by_thisprocessor=True,original_asset_physics_rewards_skill_predicates_unchanged=True,model_PT_rawtrajectory_SDK_replay_C_GO_Git_operations=0)


def scan_closed_stdout(raw):return [line for line in raw.decode('utf-8',errors='replace').splitlines()if CAPACITY.search(line)]
def read_json(path):
 p=Path(path);need(p.suffix.lower()=='.json','MetadataJSONonly');raw=p.read_bytes();return json.loads(raw),dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--closed-pointer',type=Path,default=D/'PAIR2_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json');p.add_argument('--baseline',type=Path,default=T/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json');p.add_argument('--training-summary',type=Path,default=D/'reports/PAIR2_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json');p.add_argument('--contracts',type=Path,default=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json');p.add_argument('--out',type=Path,default=D/'reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json');a=p.parse_args();need(not a.out.exists(),'Neveroverwriteexistingbestassessment')
 pointer,pointer_ref=read_json(a.closed_pointer);closed_path=Path(pointer['path']);closed,closed_ref=read_json(closed_path);need(closed['parent_exit']is not None and closed['final']is not None,'Neverassesspendingwindow');baseline,base_ref=read_json(a.baseline);training,training_ref=read_json(a.training_summary);contracts,contract_ref=read_json(a.contracts);manifest={x['relative']:x for x in closed['files']if'relative'in x};tasks={};errors={};stdout_refs=[]
 for role in ROLES:
  rel='cases/'+role+'/task.json';task,task_ref=read_json(closed_path.parent/rel);need(task_ref['SHA']==manifest[rel]['SHA']and task_ref['bytes']==manifest[rel]['bytes'],'CollectedTaskmanifestidentity');tasks[role]=task
  rel='cases/'+role+'/SDK_FULL_STDOUT_STDERR.log';raw=(closed_path.parent/rel).read_bytes();r=dict(path=str(closed_path.parent/rel),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest());need(r['SHA']==manifest[rel]['SHA']and r['bytes']==manifest[rel]['bytes'],'Collectedclosedstdoutmanifestidentity');errors[role]=scan_closed_stdout(raw);stdout_refs.append(r)
 result=assess_pair2(closed,baseline,training,contracts,tasks,errors);result.update(source=str(closed_path),input_metadata_refs=[pointer_ref,closed_ref,base_ref,training_ref,contract_ref],closed_stdout_metadata_refs=stdout_refs,only_this_collected_closed_stdout_scanned=True,no_old_raw_NPZ_JSONL_or_PT_read=True)
 with a.out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
 print(a.out);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
