"""Independent target read; never retry the source's failed connect."""
from pathlib import Path
import sys,os,time,json,getpass,traceback
U=Path(__file__).resolve().parent;R=U/'reports'
import collect_existing_three_slot_after_local_collector_unreported_exit_v2_once as a
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 errs=sorted(R.glob('THREE_SLOT_HANDOFF_RECOVERY_COLLECTION_V2_ORIGINAL_ERROR_*.json'));assert errs and 'TimeoutError' in errs[-1].read_text('utf8');assert not (R/'THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json').exists();put('THREE_SLOT_TARGET72_ONLY_SOURCE_CONNECT_FAILED_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),prior_source_connect_failed_before_remote_command=True,no_source_retry=True,one_target72_connection_only=True,actual_alive_only_exclusive_transport=True));pw=getpass.getpass('Host72 existing first models, no source retry (hidden): ');conn=None;models={'h1':[]};out={k:dict(files=[],models=[],actual_own_processes_not_observed=True,source_timeout_unknown=True) for k in ('owner','h1')}
 try:
  conn=a.c.a.connect72(pw);pw=None
  for key in ('e2','recovery'):out[key]=a.c.a.code(conn,a.c.a.PY,a.c.READ,a.c.ROOTS[key],key);models[key]=a.get_models(conn,out[key],key)
 finally:
  pw=None
  if conn:conn.close()
 out.update(epoch=time.time(),downloaded_models=models,source210_original_timeout_path=str(errs[-1]),source_H1_final_cost_PID_locks_unknown_not_inferred=True,previous_local_collector_exit_reason_unknown_preserved=True,no_GPU_or_native_or_Task_replay=True);put('THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json',out);print(json.dumps(dict(epoch=out['epoch'],models={k:[dict(kind=r['kind'],SHA=r['SHA'],bytes=r['bytes']) for r in v] for k,v in models.items()},source_unknown=True,new_target_errors={k:[r['path'] for r in out[k]['files'] if 'ORIGINAL_ERROR' in r['path']] for k in ('e2','recovery')})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_SLOT_TARGET72_ONLY_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_native_or_once_replay=True));raise
