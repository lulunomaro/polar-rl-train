"""One current-state read, no poll, model transfer, task launch or budget write."""
from pathlib import Path
import os,sys,json,time,getpass,traceback
import deploy_H1_one_hour_8a7c_native_then_timed_training_once as d
sys.path.insert(0,str(d.E));from collect_ce3_own_native_and_first_missing_finite_once import META
B=d.B;R=d.R;a=d.a
def main():
 d.put('H1_ONE_HOUR_CURRENT_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exact_CIM_actual_alive_only_exclusive_all_transport=True,no_poll_or_GPU_or_models_or_budget_write=True));pw=getpass.getpass('72 one-hour chain current metadata (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None;target=a.code(c,a.PY,META,d.TARGET,timeout=90)
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,META,d.SOURCE,timeout=90);account=a.code(c,a.t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());print(json.dumps(dict(epoch=time.time(),active_segment=v['active_segment'],remaining_snapshot=v['remaining_training_seconds'],authorized_training_seconds=v['authorized_training_seconds'],extensions=len(v['budget_extensions']),readonly=True)))",timeout=60)
 finally:
  if c:c.close()
 d.put('H1_ONE_HOUR_CHAIN_CURRENT_READONLY_ACTUAL.json',dict(epoch=time.time(),target=target,owner=owner,original_account=account,actual_transport_returned=True,no_model_raw_hash_or_new_GPU_or_budget_change=True))
 print(json.dumps(dict(target_phase=target['rows'].get('NODE_CURRENT.json',{}).get('row',{}).get('phase'),source_go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go'),errors=target['errors'],remaining_snapshot=account['remaining_snapshot'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('H1_ONE_HOUR_CURRENT_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
