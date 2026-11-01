"""True saved qualified metadata -> pending eval Task/source package. No SDK/model."""
from pathlib import Path
import argparse,hashlib,json,time
from contract_latest32 import *
N=Path(__file__).resolve().parent
FILES=('evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','contract_latest32.py','guard_latest32.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def make_task(run,purpose,gpu,binding,refs,sdk_python,rows):
 shas={x['relative']:x['SHA'] for x in rows}
 task=dict(kind=KIND,epoch=time.time(),run_id=run,purpose_id=purpose,model_SHA=SHA,model_bytes=BYTES,model_iteration=ITER,Adam17=ADAM,
  model_new_PPO_updates=UPDATES,actual_saved_LR=LR,model_path=SOURCE_MODEL,qualified_latest227D_job_root=SOURCE_JOB,
  num_envs=20000,controls_max=1600,seconds_max=32.,physics_max=12800,feedback_max=3200,GPU_UUID=gpu,sdk_python=sdk_python,
  no_new_learning_or_GO=True,worker_seconds=3600,parent_seconds=3780,model_physical_byte_reads=1,model_decodes=1,model_copies=0,
  legacy_mimic_radians=.05,planned_mimic_radians=.01,closure_m=.01,previous_closure_m=.002,user_authorized_closure10mm=True,explicit_mimic_guard_tightening=True,full_SuperMimic=False,
  original_entry_SHA='58e1b87ee594fa3a85a3591878c06fc5c5d03b5cfe4ffdc31bb42b2598e5ddb9',
  worker_SHA=shas[FILES[0]],guard_wrapper_SHA=shas['guard_latest32.py'],current_authority_binding=binding,
  actual_current_authority_private_shared_resources_admitted=False,original_eval_parent_holds_private_and_validation_EX=False,
  formal_qualification_refs=refs,telemetry_producer=dict(format='mod4.227.lossless_fieldset_positional_jsonl.v1',
   worker_SHA=shas[FILES[0]],observer_SHA=shas['rm70_intervals227.py'],writer_SHA=shas['positional_rows227.py'],decoder_SHA=shas['decode227_positional.py'],
   retained_byte_limit=192*1024**2,all_original_fields_values_masks_and_union_retained=True,actual_byte_coverage='UNKNOWN_UNTIL_NEW_ACTUAL_CASE'),
  threshold_source='189 original along/cross max(.03,.1V);signedyaw .2;all original failed/pre-reset/reset/leftcensored union retained',
  no_old_raw_read_or_default_artifact_transfer=True,full_expert_skill='UNKNOWN;rough original domain only;other modes unexposed')
 validate_task(task);return task
def main():
 p=argparse.ArgumentParser()
 for k in ('closing','new-cpu','authority-binding','out-new'):p.add_argument('--'+k,type=Path,required=True)
 for k in ('run-id','purpose-id','GPU-UUID','sdk-python'):p.add_argument('--'+k,required=True)
 a=p.parse_args();closed,cr=metadata(a.closing);cpu,qr=metadata(a.new_cpu);qualified(closed,cpu,qr['SHA']);binding,br=metadata(a.authority_binding)
 assert binding['kind']==KNOWN_BINDING_KIND and binding['run_id']==KNOWN_ACTIVE_RUN
 a.out_new.mkdir(exist_ok=False);rows=[]
 for name in FILES:
  b=(N/name).read_bytes()
  with (a.out_new/name).open('xb') as f:f.write(b)
  rows.append(dict(relative=name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 task=make_task(a.run_id,a.purpose_id,a.GPU_UUID,binding,[cr,qr,br],a.sdk_python,rows)
 path=a.out_new/'TASK_LATEST32_PENDING_ADMISSION.json';put(path,task);b=path.read_bytes();rows.append(dict(relative=path.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 put(a.out_new/'PACKAGE_LATEST32_SOURCE_AND_TASK.json',dict(files=rows,model_metadata_only=True,asset_copies=0,actual_target_admission=False,no_new_GO=True))
 print(json.dumps(dict(source_task_prepared=True,actual_target_admission=False,model_reads=0,new_GO=False)))
if __name__=='__main__':main()
