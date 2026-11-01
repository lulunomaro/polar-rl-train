from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
a=read(R/'ROOT232_ACTUAL_E2_METADATA_AND_ORIGINAL_MEAN_CASE_RETURNED.json');free=read(R/'ROOT232_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json');assert free['global_serial_control_client_lease']=='FREE'
reports={}
for row in a['full_UTF8']:
 if row['path'].endswith('.json'):
  try:reports[Path(row['path']).name]=json.loads(row['UTF8'])
  except json.JSONDecodeError:pass
metadata=reports.get('E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json');cpuwait=reports.get('E2_FROM226_ORIGINAL_METADATA_CHILD_WAIT_ACTUAL.json');case=a.get('bounded_case');cycles=reports.get('E2_FULL_WORLD_CYCLES213_ACTUAL.json');profiles=reports.get('E2_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json')
out=dict(epoch=time.time(),kind='ACTUAL232_E2_LEXICAL_READER_AND_UNCHANGED_WORLD_MEAN_CASE',passed_execution=a['passed_execution'],wrapper_error=a['wrapper_error'],original_parent=a['parent'],
 prior231='ActualmetadataFALSE beforeGPU/model;originalstrictline-number order rejected same-line actor then step;alloriginalreports/source retained.',
 repair='Only reader uses strict(lineno,col_offset) order with counts=1 retained;original213worker91f7/reward/physics/TaskABI unchanged;V3 newkind/hash/newnamespace/purpose separate from consumed231.',
 actual_metadata=metadata,actual_original_CPU_wait=cpuwait,original_bounded_case=case,
 original_full_world_cycles=cycles,profile_domain=profiles,
 original_current_authority='Fresh227Dexactowner/run/fullGO/canonical matched beforetarget andmetadata/runtime;notanewwriter/GO. After227closes oldbindinghistorical.',
 all_SSH_closed_session_restored=free,binary_artifacts_metadata_only=a['artifacts_metadata_only'],raw_JSONL_NPZ_downloads_or_reads=0,
 no_new_training_or_optimizer_or_budget_account_action=True,full_E2_skill=False,full_SuperMimic=False,true270=False)
if case:
 out['coverage_interpretation']=dict(requested_controls=case['requested_controls'],actual_controls=case['controls'],seconds=case['simulated_seconds'],bounded24s_complete=case['controls']==1200,wall_time_limited=case['wall_time_limited'],complete_typed_WM_dataset=False,no_graduation_inferred_from_RC_or_metadata=True)
if cycles:
 out['original_cycle_interpretation']=dict(complete_sampled_spans=cycles['complete_cycle_events'],original_false_spans=cycles['original_false_cycle_events'],complete_nonterminal_with_original_bounds=cycles['complete_cycle_events']-cycles['original_false_cycle_events'],partial_spans=cycles['incomplete_events'],terminal_at_completed_endpoint=cycles['terminal_complete_events'],scope='SameUID/profile/episode spans. False is union of original kinematic bounds and terminal/truncation, not an independent population success-rate. No new aggregate threshold.',original_bounds=dict(world_along_target=.5,along_and_cross_tolerance=.05,signed_yaw_error_tolerance=.2))
out['next']='Useactualcoverage/originalfalse/unknown before selecting E2 remedy or nextfullwindow;do notrerun232or231. W35normal227D onlyateligiblewindow,afterthisfinite fullyreturned/globalFREE,originalcollector once andNEWformalCPU once. CurrentE0candidate225 remains separately repairedcopy with heading/landing unresolved.'
p=R/'CURRENT_ACTUAL232_E2_READER_AND_WORLD_SKILL_WORK_ORDER.json';assert not p.exists();p.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
print(json.dumps(dict(passed_execution=a['passed_execution'],metadata_passed=bool(metadata and metadata.get('passed')),coverage=out.get('coverage_interpretation'),cycles=out.get('original_cycle_interpretation'),new_learning=False)))
