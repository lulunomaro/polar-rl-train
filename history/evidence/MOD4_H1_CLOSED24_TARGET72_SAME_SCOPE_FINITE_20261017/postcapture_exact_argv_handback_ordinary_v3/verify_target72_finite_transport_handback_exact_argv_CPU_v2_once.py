"""A command containing a collector filename is not that collector; exact script argv only."""
from pathlib import Path
import os,json,time,psutil
B=Path(__file__).resolve().parent;R=B/'reports'
bad=dict(epoch=time.time(),id='TARGET72_CIM_SUBSTRING_OBSERVER_SELF_FALSE_V1_20261017',actual_original_exception='AssertionError: substring scan returned observer PID56224',actual_original_observer_pid=56224,actual_original_observer_entry='python -c inline app verification and CIM query',original_predicate="Name like python* and CommandLine like *collector_filename*",original_false_selected_self_because_query_contains_those_filenames=True,app_prompt_exact_verification_already_succeeded=True,no_training_process_transport_or_budget_mutation=True,correction='Exclude self and require an exact standalone .py argv item matching the owned finite script basename; retain original false')
with (R/'TARGET72_LOCAL_CIM_V1_OBSERVER_SELF_FALSE_PRESERVED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(bad,f,indent=2)
names={'collect_target72_H1_new_native_first_existing_finite_chain_once.py','collect_only_missing_target72_H1_native_first_after_actual_handback_v2_once.py','read_existing_target72_H1_actual_native_prefix_timing_once.py','read_current_H1_original_canonical_real_OSlocks_native_raw_index_once.py','deploy_H1_closed24_target72_new_native_original_handoff_once.py'}
live=[];unknown=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
 try:
  if p.pid==os.getpid() or not (p.info['name'] or '').lower().startswith('python'):continue
  argv=p.info['cmdline'] or []
  if any(x.lower().endswith('.py') and Path(x).name in names for x in argv[1:]):live.append(p.info)
 except psutil.Error as e:unknown.append(dict(pid=p.pid,error_type=type(e).__name__))
assert not live,live
out=dict(epoch=time.time(),actual_known_owned_finite_processes_exact_argv=live,observer_self_explicitly_excluded=True,exact_python_script_argv_not_substring_rule=True,unreadable_processes_not_claimed_globally_idle=unknown,all_current_own_collectors_deployer_returned=True,actual_root_transport_handback=True,not_permanent_PID_owner_or_all_other_process_idle_claim=True,no_remote_GPU_or_account_action=True)
with (R/'TARGET72_ALL_FINITE_LOCAL_CIM_ACTUAL_TRANSPORT_HANDBACK_V2.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(own_finite_count=0,actual_transport_handback=True,old_observer_false_preserved=True)))
