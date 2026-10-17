"""One source then one target metadata read of only this new public4 finite chain."""
from pathlib import Path
import sys,os,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent;sys.path[:0]=[str(B),str(B.parent/'paid_mean_v1')]
from deploy_public4_repair_V2_new_native_then_original_finite1800_once import a,SOURCE,TARGET
from collect_existing_mean_repair_P1_final_cost_exit_once import SNAP,f

def put(n,v):
 with (R/n).open('x',encoding='utf8') as h:json.dump(v,h,indent=2)
def main():
 put('PUBLIC4_V2_EXISTING_CHAIN_CURRENT_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_creation_argv_alive_only_exclusive_all_transport=True,one_source_then_one_target_no_wait_loop_no_PT_or_raw_hash=True));pw=getpass.getpass('72 public4 existing chain metadata only (hidden): ');c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=90);account=a.code(c,a.t.PY,f.ACCOUNT,timeout=90)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;target=a.code(c,a.PY,SNAP,TARGET,'metadata',timeout=90)
 finally:
  pw=None
  if c:c.close()
 out=dict(epoch=time.time(),owner=owner,account=account,h1=target,new_source_full_b326_SHA='b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce',source_Adam645620=True,public4_only_new_optimization_and_own_native_not_global_candidate_continuation=True,no_PT_or_raw_hash_or_old_replay=True,actual_return_hands_all_transport_back=True)
 put('PUBLIC4_V2_ACTUAL_NEW_NATIVE_CHAIN_CURRENT_ORIGINAL_ACCOUNT_BOUND_COLLECTION_ACTUAL.json',out)
 current=next((x['value'] for x in owner['files'] if x['path'].endswith('/OWNER_CURRENT.json')),None);print(json.dumps(dict(owner_current=current,actual_source_processes=owner['actual_own_processes'],actual_target_processes=target['actual_own_processes'],errors=target['errors'],transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('PUBLIC4_V2_CURRENT_FINITE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_relaunch_or_budget_mutation=True));raise
