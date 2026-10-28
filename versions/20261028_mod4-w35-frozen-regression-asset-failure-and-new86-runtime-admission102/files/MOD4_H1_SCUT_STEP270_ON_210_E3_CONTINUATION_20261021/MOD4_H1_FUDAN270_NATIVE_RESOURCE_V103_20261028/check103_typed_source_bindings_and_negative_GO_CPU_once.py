from pathlib import Path
import importlib,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 assert not torch.cuda.is_initialized()
 prepared=json.loads((R/'TWO103_FUDAN270_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());results={}
 for mode,spec in prepared['payloads'].items():
  B=Path(spec['payload']);sys.path[:0]=[str(B),str(B/'source')]
  for k in list(sys.modules):
   if k in ('native_flat90_source_guard_v1','native88C_to_flat_migration_v1','native103_fudan270_pins_v1'):sys.modules.pop(k)
  guard=importlib.import_module('native_flat90_source_guard_v1');mig=importlib.import_module('native88C_to_flat_migration_v1')
  checked=guard.check_payload(B,verify_model_bytes=False);task=checked['task']
  go=dict(task,payload_manifest_SHA=checked['manifest_SHA'],max_parent_seconds=3900,exit_headroom_seconds=300)
  mig.assert_declared_admission('h1',task,go);guard.validate_task_go(task,go,checked['manifest_SHA'])
  bad=[]
  import copy
  for field,value in [('native_reference_SHA','0'*64),('source_SHA','1'*64),('native_learning_seed',28),('native_seed',29),('fudan_step_task',dict(task['fudan_step_task'],step_top_z_m=.20))]:
   wrong=copy.deepcopy(go);wrong[field]=value
   try:mig.assert_declared_admission('h1',task,wrong)
   except ValueError:bad.append(field)
   else:raise AssertionError('wrong GO accepted '+field)
  for field,value in [('GPU_UUID','GPU-wrong'),('logical_slot','fake')]:
   wrong=copy.deepcopy(task);wrong[field]=value
   try:guard.validate_task_go(wrong,go,checked['manifest_SHA'])
   except ValueError:bad.append(field)
   else:raise AssertionError('wrong target accepted '+field)
  results[mode]=dict(source_guard_passed=True,manifest_SHA=checked['manifest_SHA'],negative_fields_rejected=bad,models_rehashed_or_loaded=0)
 put('TWO103_TYPED_SOURCE_AND_SIGNED_GO_NEGATIVE_CPU_ACTUAL.json',dict(passed_source_CPU_only=True,epoch=time.time(),results=results,no_Go_signed_no_SDK_no_remote_no_GPU=True))
 print(json.dumps(dict(passed_source_CPU_only=True,negative_fields_per_role=7,no_model_read=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO103_TYPED_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_read_or_GPU=True));raise
