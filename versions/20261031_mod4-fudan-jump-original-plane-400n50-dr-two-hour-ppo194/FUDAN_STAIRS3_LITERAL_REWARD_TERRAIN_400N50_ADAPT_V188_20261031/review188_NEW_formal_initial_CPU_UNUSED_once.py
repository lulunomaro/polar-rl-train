from pathlib import Path
import hashlib,io,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 c=json.loads((R/'ROOT188_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
 assert c['passed_collection'] and c['source_node']['qualified_formal'] and c['formal'] and c['formal']['transfers']==1 and c['formal']['two_host_SHA_equal']
 assert c['owner_closed']['canonical_None'] and c['source_node']['private_EX_free']
 f=c['formal'];p=Path(f['path']);assert p.stat().st_size==f['bytes']
 put('ROOT188_NEW_FORMAL_INITIAL_CPU_PURPOSE_CONSUMED.json',dict(epoch=time.time(),one_NEW_formal_read=1,one_decode=1,old_input4999_or_other_models=0,normal86_witness_reads=0,CPU_only=True))
 with p.open('rb') as stream:raw=stream.read()
 assert hashlib.sha256(raw).hexdigest()==f['SHA']
 import torch
 assert not torch.cuda.is_initialized()
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=True)
 bad=[];count=0
 def check(v,path='root'):
  nonlocal count
  if torch.is_tensor(v):
   count+=1
   if (v.is_floating_point() or v.is_complex()) and not torch.isfinite(v).all():bad.append(path)
  elif isinstance(v,dict):
   for k,x in v.items():check(x,path+'.'+str(k))
  elif isinstance(v,(list,tuple)):
   for i,x in enumerate(v):check(x,path+'.'+str(i))
 check(ck);assert not bad
 updates=ck['actual_new_PPO_updates'];steps=[float(x['step']) for x in ck['optimizer_state_dict']['state'].values()]
 assert updates>0 and len(steps)==17 and min(steps)==max(steps)==100020+20*updates and ck['iter']==4999+updates
 assert ck['source_delivery_SHA']=='5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4'
 assert list(ck['actor_state_dict']['mlp.0.weight'].shape)==[256,35] and list(ck['critic_state_dict']['mlp.0.weight'].shape)==[256,38]
 assert ck['actor_state_dict']['distribution.std_param'].shape==(6,)
 assert {'sensor','feedback','physical_action','spring','damping','COM','PD','mild','global_CPU_rng','global_CUDA_rng','command_rngs'}<=set(ck['target_DR_state'])
 assert ck['typed_STAIRS3_188_task']['reward_weights_and_functions_no_edits'] and ck['typed_STAIRS3_188_task']['policy_hz']==50
 report=dict(epoch=time.time(),passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],one_NEW_formal_read_decode=True,old_models_read=0,tensors_finite=count,actual_new_PPO_updates=updates,saved_iteration=ck['iter'],Adam_step=steps[0],actor35_critic38_action6=True,target_DR_full_states_present=True,original_STAIRS3_task_source_retained=True,CUDA_initialized=torch.cuda.is_initialized(),skill270_success=False)
 put('ROOT188_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL.json',report);print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT188_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
