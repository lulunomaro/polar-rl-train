"""One finite transport owner: new full observations then original H1 post-save final."""
from pathlib import Path
import sys,json,time,os,getpass,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
 original=getpass.getpass;password=None
 try:
  save('COMBINED_NEW_FULL_AND_H1_POSTSAVE_FINAL_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_creation_exe_exact_argv_alive_only_exclusive_210_72_249=True,no_old_complete_native_first_PT_or_raw_recollected=True,all_H1_model_audit_only_after_actual_full_saved_FINAL=True,max_source_wait600_after_finite_full_collection=True));password=original('72 new full evidence and existing hour final (hidden): ');getpass.getpass=lambda prompt='':password
  full=module('unused_new_full_collection_functions',B/'collect_new_full15s_two_Linux_only_missing_complete_files_once.py');full.main()
  h=module('prepared_unused_existing_H1_hour_final_collection',W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/hour1_h1_8a7c_v1/collect_H1_one_hour_only_missing_final_cost_exit_once.py');h.main()
  save('COMBINED_NEW_FULL_AND_H1_FINAL_COLLECTION_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_transport_returned=True,no_runtime_signal_or_GPU_replay_or_budget_mutation=True))
 except BaseException:save('COMBINED_FULL_H1_FINAL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_partial_then_only_missing_no_replay=True));raise
 finally:getpass.getpass=original;password=None
