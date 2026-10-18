"""One requested current-state snapshot, no polling, model transfer or runtime mutation."""
from pathlib import Path
import os,sys,json,time,getpass,traceback
import deploy_H1_one_hour_8a7c_native_then_timed_training_once as d
sys.path.insert(0,str(d.E));from collect_ce3_own_native_and_first_missing_finite_once import META
META=META.replace("'job0/production/FINAL.json'","'job0/production/FINAL.json','job0/production/latest_complete.json','job0/production/OWN_STORAGE_OR_UPDATE_BOUND_SAVED_STOP_ACTUAL.json'")
def main():
 d.put('H1_ONE_HOUR_HUMAN_STATUS_1646_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exact_CIM_alive_only_transport_exclusive=True,no_poll_or_model_raw_hash_or_GPU_or_budget_mutation=True))
 pw=getpass.getpass('72 current one-hour training status (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;target=d.a.code(c,d.a.PY,META,d.TARGET,timeout=90)
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=d.a.t.connect();owner=d.a.code(c,d.a.t.PY,META,d.SOURCE,timeout=90)
 finally:
  if c:c.close()
 v=dict(epoch=time.time(),target=target,owner=owner,actual_transport_returned=True,no_model_raw_or_GPU_or_budget_mutation=True)
 d.put('H1_ONE_HOUR_HUMAN_STATUS_1646_READONLY_ACTUAL.json',v)
 row=target['rows'].get('NODE_CURRENT.json',{}).get('row',{});progress=target['rows'].get('job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json')
 print(json.dumps(dict(epoch=v['epoch'],target_phase=row.get('phase'),worker=row.get('worker'),production_progress=progress,source_go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go'),target_errors=target['errors'],owner_errors=owner['errors'],own_target_processes=target['own_processes'],compute=target['compute'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  d.put('H1_ONE_HOUR_HUMAN_STATUS_1646_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_or_budget_write=True));raise
