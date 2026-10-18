"""Read actual native rejection exit and real locks; no model/raw hash or accounting write."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
from collect_ce3_own_native_and_first_missing_finite_once import META
from collect_existing_ce3_final_original_cost_exit_once import f,RES
B=d.B;R=d.R;a=d.a;SOURCE=d.SOURCE;TARGET=d.TARGET

def main():
 d.put('CE3_NATIVE_REJECTED_CLOSING_METADATA_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_identity_alive_only_exclusive_transport=True,no_GPU_or_raw_PT_hash_or_budget_write=True))
 pw=getpass.getpass('72 rejected native actual exit/locks only (hidden): ');c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,META,SOURCE,timeout=60);account=a.code(c,a.t.PY,f.ACCOUNT,timeout=60)
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None;target=a.code(c,a.PY,META,TARGET,timeout=60);resources=a.code(c,a.PY,RES,'target',timeout=60)
 finally:
  pw=None
  if c:c.close()
 canon=account['original_canonical'];assert not owner['own_processes'] and not target['own_processes'] and owner['rows']['COHORT_FINAL.json']['original_cost_settled'] and owner['rows']['OWNER_EXIT_ACTUAL.json']['original_cost_settled'];assert owner['rows']['COHORT_FINAL.json']['go']=={} and canon['active_segment'] is None
 assert all(x['actual_fcntl_free'] for x in account['actual_locks']) and all(x['actual_fcntl_free'] for x in resources['actual_target_private_shared_validation_locks'])
 assert not any(x.get('owner_parent_pid')==81434 for x in canon['completed_segments']);old=json.loads((R/'H1_NEW_ORIGINAL_O_WRITER_ACTUAL_HANDOFF_ADMISSION.json').read_bytes());assert canon['remaining_training_seconds']==old['original_budget_remaining_snapshot']
 out=dict(epoch=time.time(),actual_native_worker_CPU_node_original_owner_all_out=True,original_native_GPU_worker_EXIT0_but_CPU_reader_and_node_rejected=True,no_production_GO_worker_or_model=True,original_canonicalNone_two_real_fcntl_and_target_private_shared_free=True,new_paid_cost_seconds=0.,original_remaining_unchanged_snapshot=canon['remaining_training_seconds'],owner=owner,account=account,target=target,resources=resources,original_FP64_false_not_relabelled=True,actual_transport_returned=True,no_GPU_case_or_raw_PT_hash_replay=True)
 d.put('CE3_NATIVE_REJECTED_ZERO_GO_COST_ACTUAL_EXIT_FCNTL_HANDBACK_ACTUAL.json',out);print(json.dumps(dict(actual_all_out_locksfree=True,GO=0,charge=0,remaining_snapshot=canon['remaining_training_seconds'])),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_NATIVE_REJECTED_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_account_mutation=True));raise
