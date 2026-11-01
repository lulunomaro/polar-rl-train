"""One necessary selected2050 full-PPO CPU decode + actual ONNX initializer identity."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,math,time,traceback
T=Path(__file__).resolve().parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def main():
 p=N/'source_model/model_2050_from_selected_export.pt'
 assert p.is_file() and read(N/'onnx_identity/reports/ROOT240_ONNX_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 put('ROOT240_SELECTED2050_FULLPPO_ONNX_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),selected_PT_byte_read_decode_max=1,
  ONNX_graph_external_local_byte_reads_each_max=1,ONNX_parse_max=1,other_PT_or_old_raw_reads=0,
  CUDA_allowed=False,optimizer_steps=0,real_model_writes=0,purpose='Confirm the human-selected ONNX actor has an identical complete PPO checkpoint and preserve its actual architecture/counters/LR before400N50 continuation'))
 import torch
 import torch.nn.functional as F
 import numpy as np
 import onnx
 from onnx import numpy_helper
 assert not torch.cuda.is_initialized();rng=torch.random.get_rng_state().clone()
 with p.open('rb') as f:b=f.read()
 sha=hashlib.sha256(b).hexdigest();ck=torch.load(io.BytesIO(b),map_location='cpu',weights_only=False);del b
 count=0;bad=[];tensor_rows=[]
 def inspect(v,path='root'):
  nonlocal count
  if torch.is_tensor(v):
   count+=1
   if (v.is_floating_point() or v.is_complex()) and not torch.isfinite(v).all():bad.append(path)
   tensor_rows.append(dict(key=path,shape=list(v.shape),dtype=str(v.dtype),SHA=hashlib.sha256(v.detach().contiguous().numpy().tobytes()).hexdigest()))
  elif isinstance(v,float):
   if not math.isfinite(v):bad.append(path)
  elif isinstance(v,dict):
   for k,x in v.items():inspect(x,path+'.'+str(k))
  elif isinstance(v,(list,tuple)):
   for i,x in enumerate(v):inspect(x,path+'.'+str(i))
 inspect(ck)
 actor=ck.get('actor_state_dict',{});critic=ck.get('critic_state_dict',{})
 opt=ck.get('optimizer_state_dict',{});steps=[float(x['step']) for x in opt.get('state',{}).values()]
 schema=dict(root_keys=list(ck),iteration=ck.get('iter'),actor_keys_shapes={k:list(v.shape) for k,v in actor.items()},
  critic_keys_shapes={k:list(v.shape) for k,v in critic.items()},optimizer_groups=opt.get('param_groups'),Adam_steps=steps,finite_tensors=count,nonfinite_paths=bad)
 put('ROOT240_SELECTED2050_ACTUAL_FULLSTATE_SCHEMA_BEFORE_IDENTITY_CHECK.json',dict(epoch=time.time(),source_path=str(p),source_bytes=p.stat().st_size,source_SHA=sha,**schema))
 assert not bad and ck['iter']==2050 and len(actor)==9 and len(critic)==8
 assert list(actor['mlp.0.weight'].shape)==[128,35] and list(actor['mlp.2.weight'].shape)==[64,128] and list(actor['mlp.4.weight'].shape)==[32,64] and list(actor['mlp.6.weight'].shape)==[6,32]
 assert list(critic['mlp.0.weight'].shape)==[128,38] and list(critic['mlp.6.weight'].shape)==[1,32]
 std=actor['distribution.std_param'];assert list(std.shape)==[6] and (std>0).all()
 assert len(steps)==17 and min(steps)==max(steps) and min(steps)>0
 refs=read(N/'onnx_identity/reports/ROOT240_ONNX_EXPORT_TRAINING_PLAY_TEXTS_ACTUAL.json')['artifacts']
 blobs={}
 for ref in refs:
  q=Path(ref['local_path'])
  with q.open('rb') as stream:b=stream.read()
  assert len(b)==ref['bytes'] and hashlib.sha256(b).hexdigest()==ref['SHA'];blobs[q.name]=b
 graph_name='mod4_fudan_recovery_model2050.onnx';data_name=graph_name+'.data'
 graph=onnx.load_model_from_string(blobs[graph_name]);initializer_matches=[]
 for item in graph.graph.initializer:
  ext={x.key:x.value for x in item.external_data}
  if ext:
   assert ext['location']==data_name
   offset=int(ext.get('offset','0'));length=int(ext.get('length',str(len(blobs[data_name])-offset)))
   item.raw_data=blobs[data_name][offset:offset+length];item.ClearField('external_data');item.data_location=onnx.TensorProto.DEFAULT
  arr=np.array(numpy_helper.to_array(item),copy=True)
  matches=[]
  for key,value in actor.items():
   source=value.numpy()
   if arr.shape==source.shape and np.array_equal(arr,source):matches.append(dict(actor_key=key,transform='identity'))
   elif source.ndim==2 and arr.shape==source.T.shape and np.array_equal(arr,source.T):matches.append(dict(actor_key=key,transform='transpose_only'))
  initializer_matches.append(dict(ONNX_name=item.name,shape=list(arr.shape),matches=matches))
 linear={k for k in actor if k!='distribution.std_param'}
 matched={m['actor_key']for row in initializer_matches for m in row['matches']}
 identity=dict(epoch=time.time(),all8_actor_linear_weight_and_bias_tensors_equal=linear<=matched,
  source_actor_linear_keys=sorted(linear),matched_keys=sorted(matched),initializers=initializer_matches,
  graph_nodes=[dict(op=x.op_type,inputs=list(x.input),outputs=list(x.output)) for x in graph.graph.node],
  input=[dict(name=x.name,shape=[d.dim_value or d.dim_param for d in x.type.tensor_type.shape.dim])for x in graph.graph.input],
  output=[dict(name=x.name,shape=[d.dim_value or d.dim_param for d in x.type.tensor_type.shape.dim])for x in graph.graph.output])
 put('ROOT240_SELECTED2050_ONNX_AND_PPO_ACTOR_TENSOR_IDENTITY_ACTUAL.json',identity)
 assert identity['all8_actor_linear_weight_and_bias_tensors_equal'],'Selected fullPPO actor does not match actual2050 ONNX'
 x=torch.zeros(1,35)
 for i in (0,2,4,6):
  x=F.linear(x,actor[f'mlp.{i}.weight'],actor[f'mlp.{i}.bias'])
  if i!=6:x=F.elu(x)
 assert torch.equal(rng,torch.random.get_rng_state()) and not torch.cuda.is_initialized()
 result=dict(epoch=time.time(),passed=True,source_path=str(p),source_bytes=p.stat().st_size,source_SHA=sha,
  human_selected_ONNX_actor_identity_passed=True,training_directory_same_number_PT_byte_mismatch_preserved=True,
  trained_checkpoint_to_selected_export_PT_tensor_identity='UNKNOWN; only initial byte hash mismatch observed, original training PT not decoded',
  actor35_critic38_STD6=True,hidden=[128,64,32],activation='elu',source_iteration=2050,Adam17_step=steps[0],
  source_optimizer_LR=[x['lr'] for x in opt['param_groups']],learned_STD6=std.tolist(),
  zero_input_actor_mean_diagnostic_only=x[0].tolist(),all_tensors_finite=True,finite_tensors=count,whole_state_tensor_fingerprints=tensor_rows,
  selected_PT_reads=1,selected_PT_decodes=1,ONNX_graph_parse=1,ONNX_external_decode=1,old_model_or_raw_reads=0,
  CUDA_initialized=False,global_CPU_RNG_unchanged=True,optimizer_steps=0,source_model_writes=0,
  no_new_DR_state_claimed=True,new_target_physics_DR_queues_and_commands_required=True)
 put('ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json',result)
 print(json.dumps({k:result[k] for k in ('passed','source_SHA','source_bytes','source_iteration','Adam17_step','source_optimizer_LR','learned_STD6','finite_tensors','zero_input_actor_mean_diagnostic_only')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT240_SELECTED2050_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_repeat=True));raise
