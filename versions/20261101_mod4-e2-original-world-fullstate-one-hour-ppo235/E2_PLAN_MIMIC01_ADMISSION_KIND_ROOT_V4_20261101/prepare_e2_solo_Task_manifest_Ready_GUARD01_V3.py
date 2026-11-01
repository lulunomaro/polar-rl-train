"""ROOT metadata-only generator. Requires real saved/fresh receipts;never GO."""
from pathlib import Path,PurePosixPath
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'))
from e2_guard01_repair_contract_v3 import prior_failed_closed,new_read_admission
import argparse,hashlib,json
from e2_solo_contract import (KIND,ROLE,SHA,BYTES,ITER,ADAM,LR,CPU_SHA,MODEL,
                             metadata,qualified_cpu,scoped232,fresh,task_base,validate_task,valid_ready_value)


def raw(v):return json.dumps(v,indent=2,allow_nan=False).encode()
def main():
 p=argparse.ArgumentParser()
 for name in ('saved-cpu','scoped-actual232','fresh-admission','install','out-new','failed235-closing','actual235-work-order'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--new-source-read-purpose-id',required=True);p.add_argument('--run-id',required=True);p.add_argument('--job-root',required=True);a=p.parse_args()
 cpu,cr=metadata(a.saved_cpu);qualified_cpu(cpu,cr['SHA'])
 scope,sr=metadata(a.scoped_actual232);scoped232(scope)
 admission,fr=metadata(a.fresh_admission);fresh(admission)
 closed,closedref=metadata(a.failed235_closing);order,orderref=metadata(a.actual235_work_order)
 prior=prior_failed_closed(closed,order);repair=new_read_admission(prior,a.new_source_read_purpose_id,a.run_id)
 assert admission['checked_epoch']>=prior['closed_epoch']
 require_actual=[cpu,scope,admission]
 assert all(not x.get('synthetic_fixture_only') for x in require_actual)
 assert admission['checked_epoch']>=scope['closed_epoch'] and admission['run_id']==a.run_id and admission['job_root']==a.job_root
 job=PurePosixPath(a.job_root);assert job.is_absolute() and str(job)!=str(PurePosixPath(MODEL).parent.parent)
 installation,ir=metadata(a.install);assert installation['kind']=='E2_SOLO_ORIGINAL_FULLSTATE_SOURCE_INSTALL_V1'
 files=[{k:r[k] for k in ('relative','bytes','SHA')} for r in installation['files']]
 names={r['relative']:r for r in files};assert all(not r['relative'].endswith(('.pt','.partial','.active')) for r in files)
 evidence=dict(kind='ROOT_E2_SOLO_QUALIFIED_SCOPE_AND_FRESH_ACTUAL_JOIN',saved_CPU_ref=cr,
  actual232_scoped=scope,actual232_scoped_ref=sr,guard01_repair_admission=repair,prior235_failed_closing_ref=closedref,prior235_work_order_ref=orderref,fresh_actual=admission,fresh_actual_ref=fr,installation_ref=ir)
 eb=raw(evidence);esha=hashlib.sha256(eb).hexdigest()
 task=task_base();task.update(run_id=a.run_id,GPU_UUID=admission['GPU_UUID'],worker_SHA=names['worker_e2_original_fullPPO.py']['SHA'],
  manifest_file='E2_SOLO_MANIFEST.json',launch_evidence_SHA=esha)
 task.update(explicit_mimic_guard_tightening=True,original_inherited_mimic_threshold_radians=.05,planned_mimic_threshold_radians=.01,closure_threshold_m=.002,guard_entry_SHA=names['runtime/isaac/mod4/train_e2_213.py']['SHA'],new_selected_source_read_purpose_id=a.new_source_read_purpose_id,legacy232_not_mimic01_proof=True)
 validate_task(task);tb=raw(task)
 files.append(dict(relative='TASK.json',bytes=len(tb),SHA=hashlib.sha256(tb).hexdigest()))
 manifest=dict(kind=KIND,files=files,input_model_metadata=dict(path=MODEL,SHA=SHA,bytes=BYTES,iteration=ITER,Adam17=ADAM))
 manifest.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id','legacy232_not_mimic01_proof')})
 mb=raw(manifest);msha=hashlib.sha256(mb).hexdigest()
 ready=dict(passed=True,kind=KIND,manifest_SHA=msha,source_SHA=SHA,source_iteration=ITER,Adam_step=ADAM,source_LR=LR,
  source_saved_fullstate_CPU_SHA=CPU_SHA,source_fullstate_CPU_passed=True,all_actor_critic_optimizer_tensors_finite=True,
  actual_35_38_6_shapes=True,launch_evidence_SHA=esha,original232_scoped_fullrestore_native24_reused=True,
  original232_outer_false_preserved=True,fresh_CNone_CIM_resources_passed=True,
  status='ROOT_ACTUAL_METADATA_READY_FOR_ORIGINAL_OWNER_NO_GO')
 ready.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id','legacy232_not_mimic01_proof')})
 ready['V3_native24_under_mimic01_pending_before_PPO']=True
 spec=dict(key=ROLE,execution_backend='target72',GPU_UUID=task['GPU_UUID'],num_envs=20000,
  source_SHA=SHA,source_iteration=ITER,source_Adamstep=ADAM,source_LR=LR,source_kind=KIND,
  max_parent_seconds=3900,exit_headroom_seconds=300,no_physics_change=False,no_other_physics_change=True,
  prelaunch_control_snapshot_id=admission['control_snapshot_id'],manifest_SHA=msha,launch_evidence_SHA=esha,
  manifest_file='E2_SOLO_MANIFEST.json',worker_script='worker_e2_original_fullPPO.py',job_root=str(job),role='node',run_id=a.run_id)
 spec.update({k:task[k] for k in ('explicit_mimic_guard_tightening','original_inherited_mimic_threshold_radians','planned_mimic_threshold_radians','closure_threshold_m','guard_entry_SHA','new_selected_source_read_purpose_id')})
 assert valid_ready_value(ready,spec)
 a.out_new.mkdir(exist_ok=False)
 for name,data in [('TASK.json',tb),('PRELAUNCH_E2_SOLO_ACTUAL_EVIDENCE.json',eb),('E2_SOLO_MANIFEST.json',mb),
                   ('ADMISSION_E2_SOLO_READY.json',raw(ready)),('E2_SOLO_ORIGINAL_OWNER_SPEC_FIELDS.json',raw(spec))]:
  with (a.out_new/name).open('xb') as f:f.write(data)
 print(json.dumps(dict(metadata_only=True,manifest_SHA=msha,launch_evidence_SHA=esha,model_reads=0,GO=False)))


if __name__=='__main__':main()
