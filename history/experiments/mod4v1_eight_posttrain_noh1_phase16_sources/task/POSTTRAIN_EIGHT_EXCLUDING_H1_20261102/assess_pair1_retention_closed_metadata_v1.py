"""Only process newclosedpublishedFINAL+closedstdout, notcheckpoint/raw/replay.
Conservative best selection is NOT an original graduation rule. Never promote
on merePPOcount. Mustcompleteactualfrozenoriginalscope beforethisscript.
"""
from pathlib import Path
import json,re,sys
D=Path(__file__).resolve().parent;R=D.parent

def main():
 p=D/'reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json';assert not p.exists()
 pointer=D/'PAIR1_RETENTION_V4_LATEST_CLOSED_RESULT_PATH.json';cp=Path(json.loads(pointer.read_bytes())['path']);v=json.loads(cp.read_bytes());s=v['final'];ex=v['parent_exit'];assert s is not None and not ex['errors']and ex['all_own_children_waited']and ex['original_single_GPU_private_EX_released']and ex['original_global_finite_EX_released']
 assert s['all_pair_actual_execution_complete']and len(s['rows'])==2
 base=json.loads((R/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json').read_bytes());b={x['role']:x for x in base['rows']};pins=json.loads((D/'PAIR1_RETENTION_EVAL_SOURCE_V3/ACTUAL_CANDIDATE_PINS_FROM_CLOSED_FINAL.json').read_bytes());contracts=json.loads((R/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json').read_bytes());rows=[];starts=[];ends=[]
 for row in s['rows']:
  role=row['role'];f=row['data'];assert role in('E0','CURB_PROTECTED878')and row['returncode']==0 and row['actual_waited']and row['passed_execution']
  actual_N=f['num_envs']if'num_envs'in f else sum(g['environments']for g in f['metrics']['groups'].values())
  assert f['passed_execution']and actual_N==80 and f['controls']==b[role]['controls']and f['seconds']==b[role]['seconds']and f['optimizer_updates']==0
  task=json.loads((cp.parent/'cases'/role/'task.json').read_bytes());assert task['asset_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and task['seed']==20260928
  if 'asset_SHA'in f:assert f['asset_SHA']==task['asset_SHA']
  if 'asset_USD_SHA'in f:assert f['asset_USD_SHA']==task['asset_SHA']
  cache=f['source_cache'];newpin=pins[role];assert cache['source_SHA']==newpin['SHA']
  start=f.get('first_eval_epoch',f.get('wall_start_epoch'));end=f.get('last_eval_epoch',f.get('wall_end_epoch'));assert start>=s['common_start_epoch']and end>start;starts.append(start);ends.append(end)
  term=f.get('termination_events_by_reason',f.get('termination_counts'));assert term is not None
  oldterm=b[role]['termination_events'];ordinary=('bad_orientation','base_contact','closure','mimic','low_base');nonreg_terms=all(term[k]<=oldterm[k]for k in ordinary)
  log=cp.parent/'cases'/role/'SDK_FULL_STDOUT_STDERR.log';text=log.read_bytes().decode('utf-8',errors='replace');bad=[l for l in text.splitlines()if re.search(r'(?i)overflow|out of memory|CUDA error|buffer.*(too small|insufficient|exceeded)|contact.*capacity.*exceeded',l)];assert not bad
  item=dict(role=role,actual_eval_RC=0,actual_scope_seconds=f['seconds'],actual_controls=f['controls'],source_candidate_SHA=cache['source_SHA'],termination_events=term,baseline_termination_events=oldterm,ordinary_failure_nonincrease=nonreg_terms,closed_stdout_capacity_errors=bad,whole_source_cache_identity_preserved=cache.get('wholecachedidentity_passed',cache.get('entire_original_root_and_nested_identity_preserved')),new_PPO_updates_in_eval=0,original_full_expert_graduated=False)
  if role=='E0':
   values=f['skill']['body_velocity_absolute_error_time_integral_per_env'];assert len(values)==80 and all(len(a)==3 for a in values);means=[sum(z[i]for z in values)/(len(values)*f['seconds'])for i in range(3)];old=b[role]['diagnostic_fullwindow_body_abs_error_mean_vx_vy_yaw'];nonreg=all(n<=o for n,o in zip(means,old))and nonreg_terms
   item.update(diagnostic_body_abs_error_mean_vx_vy_yaw=means,baseline_body_abs_error_mean_vx_vy_yaw=old,delta_vx_vy_yaw=[n-o for n,o in zip(means,old)],conservative_selection_rule='Pareto nonworse in all three existingdiagnostics and ordinaryfailures, not newskillpass/graduationthreshold',no_diagnostic_regression_in_this_screen=nonreg)
   mother=dict(path=b[role]['source_cache']['source_path'],SHA=b[role]['source_cache']['source_SHA']);candidate=dict(path=newpin['path'],SHA=newpin['SHA'],bytes=newpin['bytes'])
  else:
   m=f['metrics'];groups=m['groups'];old=b[role]['original_endpoint_groups'];rr=m['rows'];stand=dict(total=sum(z['group']=='stand'for z in rr),no_failure=sum(z['group']=='stand'and z['first_ordinary_failure_control']is None for z in rr));same_counts=all(groups[k]['environments']==old[k]['environments']for k in('ascending','descending','stand'));crossing=all(groups[k][q]>=old[k][q]for k in('ascending','descending')for q in('complete_envs','contact_confirmed_envs'));standkeep=stand['total']==b[role]['stand_no_ordinary_failure']['total']and stand['no_failure']>=b[role]['stand_no_ordinary_failure']['no_failure'];nonreg=same_counts and crossing and standkeep and nonreg_terms
   item.update(original_endpoint_groups=groups,baseline_endpoint_groups=old,stand_no_ordinary_failure=stand,baseline_stand_no_ordinary_failure=b[role]['stand_no_ordinary_failure'],same_declared_group_sizes=same_counts,conservative_selection_rule='Existingownsameepisode two-wheel endpoint/contact groups andstandfailure factsnondecrease; no standcrossingrequired/noinventedtotalgrade',original_scoped_skill_facts_not_regressed=nonreg)
   mother=dict(path=contracts[role]['source']['path'],SHA=contracts[role]['source']['SHA']);candidate={k:newpin[k]for k in('path','SHA','bytes')}
  item.update(selection='CANDIDATE'if nonreg else'FROZEN_MOTHER',selected_source=candidate if nonreg else mother,candidate_preserved=candidate,frozen_mother_preserved=mother,do_not_overwrite_mother_or_failed_candidate=True,selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation=True,unpaired_trajectory_after_policy_dependent_resets_not_causal_claim=True);rows.append(item)
 assert min(ends)>max(starts)
 result=dict(kind='ACTUAL_PAIR1_ORIGINAL_SCOPE_FROZEN_RETENTION_AND_CONSERVATIVE_BEST_SELECTION',rows=rows,actual_control_windows_overlap_seconds=min(ends)-max(starts),retention_assessment_complete=True,all_scope_claims_limited=True,H1_excluded=True,remaining_six_PPO_not_started_by_thisprocessor=True,source=str(cp),source_checkpoint_raw_SDK_or_replay_ops=0,original_asset_physics_rewards_skill_predicates_unchanged=True)
 p.write_text(json.dumps(result,indent=2),encoding='utf-8');print(p);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
