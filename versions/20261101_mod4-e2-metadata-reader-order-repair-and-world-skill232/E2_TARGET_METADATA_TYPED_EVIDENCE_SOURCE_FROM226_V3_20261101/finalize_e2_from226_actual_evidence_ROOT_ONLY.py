"""JSON-only typed213 Task from real metadata/wait and current authority.

No model/asset/SDK/network calls. No current GPU holding proof means READY only.
Unlike frozen226's CNone-only finalizer,this does not relabel227D active asNone.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
from contract_e2_from226 import (MODEL,WORKER,EXPECTED,PENDING_TASK,KIND,read_metadata,
                                authority,runtime_admission,require)


def put(p,value):
 with p.open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)


def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True)
 p.add_argument('--actual-wait',type=Path,required=True);p.add_argument('--actual-authority',type=Path,required=True)
 p.add_argument('--purpose-id',required=True);p.add_argument('--actual-runtime-admission',type=Path)
 a=p.parse_args();J=a.job_root.resolve()
 report,rref=read_metadata(J/'E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json')
 wait,wref=read_metadata(a.actual_wait);expected,eref=read_metadata(J/'EXPECTED_E2_FROM226_V3_TARGET_METADATA.json')
 require(eref['SHA']==EXPECTED and report['passed'] and report['kind']==KIND and report['source_SHA']==MODEL,'Actual unchanged226 metadata report')
 require(report['expected226_SHA']==EXPECTED and report['source213_worker_SHA']==WORKER,'Actual fixed source graph')
 require(report['model_reads']==report['model_decodes']==report['physical_binary_reads']==report['GPU_calls']==report['App_or_actor_constructions']==0,'Metadata read counts')
 require(wait['purpose']==KIND and wait['purpose_id']==a.purpose_id and wait['passed'] is True and wait['actual_waited'] is True and wait['returncode']==0,'Original new waited CPU child')
 require(wait['all_own_children_waited'] is True and not wait['timed_out'] and wait['original_child_identity']['pid']==wait['original_Popen_PID'],'Own actual child identity/wait,not a fabricated marker')
 require(wait['report_SHA']==rref['SHA'],'Original child report hash')
 auth,ar=read_metadata(a.actual_authority);current=authority(auth,a.purpose_id,J)
 proof=dict(wait,passed=True,actual_waited=True,returncode=0,not_old_V5_wait=True)
 legacy=J/'E2_NEW86_CPU_ORIGINAL_WAIT_PROOF.json'
 if legacy.exists():require(read_metadata(legacy)[0]==proof,'Existing different proof remains immutable')
 else:put(legacy,proof)
 pending,pref=read_metadata(J/'FROZEN_CASE_TASK_PENDING226.json');require(pref['SHA']==PENDING_TASK,'Frozen226 pending typed Task')
 task=dict(pending,actual_target_SDK_new213_source_admission_passed=True,
  actual_CPU_report_SHA=rref['SHA'],actual_CPU_waited_proof_SHA=read_metadata(legacy)[1]['SHA'],
  current_authority_mode=current['mode'],actual_current_authority_report=ar,
  actual_metadata_entry_wait=wref,no_new_learning_GO_or_budget_writer=True)
 name='FROZEN_CASE_TASK_READY_FROM226_CURRENT_AUTHORITY.json';runtime_ref=None
 if a.actual_runtime_admission:
  resource,runtime_ref=read_metadata(a.actual_runtime_admission)
  runtime_admission(resource,a.purpose_id,J,ar['SHA'],current,wait['finished_epoch'])
  task.update(GPU_UUID=resource['GPU_UUID'],actual_private_GPU_EX_held_by_parent=True,
   canonical72_known_owner_readonly_passed=True,actual_current_runtime_admission=runtime_ref)
  name='FROZEN_CASE_TASK.json'
 else:
  require(task['actual_private_GPU_EX_held_by_parent'] is False and task['canonical72_known_owner_readonly_passed'] is False,'Metadata-only Task cannot claim a future held lock')
 put(J/name,task)
 put(J/('E2_FROM226_TYPED_EVIDENCE_'+('RUNTIME' if runtime_ref else 'METADATA_READY')+'_ACTUAL.json'),dict(
  epoch=time.time(),passed=True,purpose_id=a.purpose_id,task=str(J/name),source_SHA=MODEL,
  original213_worker_SHA=WORKER,current_authority_mode=current['mode'],authority=ar,
  actual_metadata_report=rref,actual_wait=wref,runtime_admission=runtime_ref,
  actual_GPU_case_run=False,full24s_E2_skill='PENDING',full_SuperMimic=False,
  model_asset_raw_SDK_GPU_network_or_account_calls=0))
 print(json.dumps(dict(passed=True,task=str(J/name),runtime_admitted=bool(runtime_ref),authority_mode=current['mode'],model_reads=0)),flush=True)


if __name__=='__main__':
 try:main()
 except BaseException:
  args=sys.argv;job=None
  if '--job-root' in args:job=Path(args[args.index('--job-root')+1])
  if job and job.is_dir():put(job/('E2_FROM226_TYPED_JOIN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_automatic_retry=True))
  raise
