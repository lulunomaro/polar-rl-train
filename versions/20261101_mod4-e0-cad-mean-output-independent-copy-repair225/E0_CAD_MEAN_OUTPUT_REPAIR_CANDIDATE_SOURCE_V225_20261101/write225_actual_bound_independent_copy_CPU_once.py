"""One necessary source read and independent repair copy, pending physics."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import copy,hashlib,io,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 q=read(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert q['passed'];f=q['roles']['e0_72']
 p=T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101/reports/ROOT229_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json';proofbytes=p.read_bytes();actual=json.loads(proofbytes)
 assert actual['passed_execution'];proof=actual['original_parent']['result']['proof'];assert proof['actual_original_action_term_verified']and proof['original_process_receiver_verified']
 assert read(T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101/reports/ROOT229_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 source=Path(f['path']);out=N/'actual_cpu_candidate_from_e629';out.mkdir(exist_ok=False);dest=out/'model_candidate225.pt'
 put('ROOT225_ACTUAL_COPY_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),source=dict(path=str(source),bytes=f['bytes'],SHA=f['SHA']),
  actual_action_optimizer_proof=dict(path=str(p),bytes=len(proofbytes),SHA=hashlib.sha256(proofbytes).hexdigest()),
  maximum_source_model_byte_read_decode=1,maximum_new_candidate_readback=1,maximum_new223_small_JSON_read=1,
  frozen_a92_reference_reads_and_writes=0,original_source_writes=0,neural_CUDA_or_remote_calls=0,output=str(dest),no_training_or_deployment=True))
 import torch as t
 from candidate225_copy_only import repair_copy
 assert not t.cuda.is_initialized();rng=t.random.get_rng_state().clone();before=source.stat()
 raw=source.read_bytes();assert len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA'];ck=t.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 assert ck['iter']==32341 and ck['actual_new_PPO_updates']==275 and len(ck['optimizer_state_dict']['state'])==17
 assert [g['params']for g in ck['optimizer_state_dict']['param_groups']]==proof['optimizer_param_groups_IDs']
 bindings=proof['optimizer_parameter_ID_by_actor_key']
 for k,pid in bindings.items():assert tuple(ck['optimizer_state_dict']['state'][pid]['exp_avg'].shape)==tuple(ck['actor_state_dict'][k].shape)
 with t.no_grad():candidate=repair_copy(ck,proof,bindings)
 def equal(a,b):
  if t.is_tensor(a):return t.equal(a,b)
  if isinstance(a,dict):return set(a)==set(b)and all(equal(a[k],b[k])for k in a)
  if isinstance(a,(tuple,list)):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
  return a==b
 assert equal(candidate['critic_state_dict'],ck['critic_state_dict'])
 affected={'mlp.6.weight','mlp.6.bias','distribution.std_param'}
 for key,value in ck['actor_state_dict'].items():
  assert t.equal(candidate['actor_state_dict'][key][1:],value[1:])if key in affected else t.equal(candidate['actor_state_dict'][key],value)
 for pid,value in ck['optimizer_state_dict']['state'].items():
  if pid not in bindings.values():assert equal(candidate['optimizer_state_dict']['state'][pid],value)
 steps=[float(x['step'])for x in candidate['optimizer_state_dict']['state'].values()];assert len(steps)==17 and set(steps)=={648340.}
 assert equal(candidate['optimizer_state_dict']['param_groups'],ck['optimizer_state_dict']['param_groups'])
 record=read(T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101/reports/ROOT223_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json');assert record['passed_execution']
 x=t.tensor([r['policy_observation35']for r in record['original_parent']['result']['rows']],dtype=t.float32)
 predictions=[]
 with t.random.fork_rng(devices=[]):
  for state in (ck,candidate):
   net=t.nn.Sequential(t.nn.Linear(35,256),t.nn.ELU(),t.nn.Linear(256,128),t.nn.ELU(),t.nn.Linear(128,64),t.nn.ELU(),t.nn.Linear(64,6));net.load_state_dict({k.removeprefix('mlp.'):v for k,v in state['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
   with t.inference_mode():predictions.append(net(x))
 def processed(y):
  pa=y[:,:4].clamp(-6,6)*t.tensor(proof['leg_scales'])+t.tensor(proof['leg_default_offsets'])
  for c,h in ((0,1),(2,3)):
   pa[:,c]=t.maximum(pa[:,c],pa[:,h]+proof['diff_min']);pa[:,c]=t.minimum(pa[:,c],pa[:,h]+proof['diff_max'])
  return pa
 target_residual=float((processed(predictions[0])-processed(predictions[1])).abs().max());assert target_residual<1e-5
 new_left=predictions[1][:,0];assert (new_left.abs()<=6).all()
 count=0
 def finite(v):
  nonlocal count
  if t.is_tensor(v):
   count+=1
   if v.is_floating_point()or v.is_complex():assert t.isfinite(v).all()
  elif isinstance(v,dict):
   for z in v.values():finite(z)
  elif isinstance(v,(tuple,list)):
   for z in v:finite(z)
 finite(candidate)
 candidate['candidate225_repair_metadata'].update(status='ACTUAL_BOUND_COPY_PENDING_PHYSICAL_REGRESSION_NOT_LEARNING_ADMITTED',
  actual_action_proof_SHA=hashlib.sha256(proofbytes).hexdigest(),parent_input_SHA=f['SHA'],
  actual_optimizer_binding=bindings,source_iteration=32341,source_Adam17=648340,
  actual_same_input32_mean_target_max_residual=target_residual,source_clock_physics_reward_unchanged=True)
 with dest.open('xb')as stream:t.save(candidate,stream)
 saved=dest.read_bytes();sha=hashlib.sha256(saved).hexdigest();restored=t.load(io.BytesIO(saved),map_location='cpu',weights_only=False);size=len(saved);del saved
 assert equal(restored,candidate)
 assert source.stat().st_mtime_ns==before.st_mtime_ns and source.stat().st_size==before.st_size
 assert t.equal(rng,t.random.get_rng_state())and not t.cuda.is_initialized()
 put('ROOT225_ACTUAL_BOUND_COPY_AND_OWN_READBACK_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,
  status='CPU_QUALIFIED_COPY_PENDING_PHYSICAL;NOT_LATEST_LEARNED_POLICY',
  candidate=dict(path=str(dest),bytes=size,SHA=sha,producer='One actual225 exclusive save and own same-byte hash/decode readback'),
  parent_input=dict(path=str(source),bytes=f['bytes'],SHA=f['SHA'],file_unchanged=True),frozen_a92_file_reads=0,frozen_a92_file_writes=0,
  source_model_byte_reads=1,source_model_decodes=1,own_candidate_byte_read_decode=1,actual229_small_proof_read=1,actual223_small_JSON_read=1,
  finite_tensors=count,iteration=32341,Adam17_step=648340,all17_steps_LR_preserved=True,other5_output_rows_trunk_critic_unchanged=True,
  source_left_STD=float(ck['actor_state_dict']['distribution.std_param'][0]),candidate_left_STD=float(candidate['actor_state_dict']['distribution.std_param'][0]),
  candidate_same_input32_left_mean_range=[float(new_left.min()),float(new_left.max())],conditional_original_mean_target_max_residual=target_residual,
  no_rollout_or_sampled_behavior_equivalence_claim=True,physical_rollouts=0,optimizer_steps=0,new_learning_GO=False,global_RNG_unchanged=True,CUDA_initialized=False,
  next='Standing/forward/reverse walking and original plane jump regression with real candidate;physical success not inferred from CPU.'))
 print(json.dumps(dict(passed=True,candidate_path=str(dest),bytes=size,SHA=sha,left_mean_range=[float(new_left.min()),float(new_left.max())],left_STD=float(candidate['actor_state_dict']['distribution.std_param'][0]),conditional_target_residual=target_residual,physical_validated=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT225_ACTUAL_COPY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry_or_promotion=True));raise
