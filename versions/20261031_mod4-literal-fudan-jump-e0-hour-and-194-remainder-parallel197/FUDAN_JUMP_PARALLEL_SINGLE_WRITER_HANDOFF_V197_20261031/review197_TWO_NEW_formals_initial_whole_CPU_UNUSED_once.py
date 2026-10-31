from pathlib import Path
import hashlib,io,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 c=json.loads((R/'ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());s=json.loads((N/'SCHEDULE_PUBLIC.json').read_bytes())['experts']
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 for key,f in c['formals'].items():assert f['transfers']==1 and f['two_host_SHA_equal'] and c['roles'][key]['qualified_formal'] and c['roles'][key]['private_EX_free']
 assert c['formals'],'No complete formal to qualify'
 put('ROOT197_TWO_NEW_FORMALS_CPU_PURPOSE_CONSUMED.json',dict(epoch=time.time(),roles=list(c['formals']),one_byte_read_and_decode_per_NEW_formal=True,old194_input_E0_input_native_normal86_reads=0,CPU_only=True))
 import torch
 assert not torch.cuda.is_initialized();reports={}
 for key,f in c['formals'].items():
  p=Path(f['path']);assert p.stat().st_size==f['bytes']
  with p.open('rb') as stream:raw=stream.read()
  assert hashlib.sha256(raw).hexdigest()==f['SHA'];ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=True);del raw
  count=0;bad=[]
  def finite(v,path='root'):
   nonlocal count
   if torch.is_tensor(v):
    count+=1
    if (v.is_floating_point() or v.is_complex()) and not torch.isfinite(v).all():bad.append(path)
   elif isinstance(v,dict):
    for name,x in v.items():finite(x,path+'.'+str(name))
   elif isinstance(v,(list,tuple)):
    for i,x in enumerate(v):finite(x,path+'.'+str(i))
  finite(ck);assert not bad
  updates=ck['actual_new_PPO_updates'];steps=[float(x['step']) for x in ck['optimizer_state_dict']['state'].values()]
  assert updates>0 and len(steps)==17 and min(steps)==max(steps)==s[key]['source_Adamstep']+20*updates and ck['iter']==s[key]['source_iteration']+updates
  assert list(ck['actor_state_dict']['mlp.0.weight'].shape)==[256,35] and list(ck['critic_state_dict']['mlp.0.weight'].shape)==[256,38] and ck['actor_state_dict']['distribution.std_param'].shape==(6,)
  assert {'sensor','feedback','physical_action','spring','damping','COM','PD','mild','global_CPU_rng','global_CUDA_rng','command_rngs'}<=set(ck['target_DR_state'])
  assert {'base_air_time','last_contacts','contact_filt','was_in_flight','last_actions','last_root','episode_sums'}<=set(ck['original_jump_reward_memory'])
  t=ck['typed_E0_JUMP198_task'] if key=='e0_72' else ck['typed_JUMP197_resume_task']
  source=ck['source_E0_SHA'] if key=='e0_72' else ck['source_resume194_SHA'];assert source==s[key]['source_SHA']
  assert t['reward_weights_and_functions_no_edits'] and t['policy_hz']==50 and t['gas_nominal_k']==2000
  reports[key]=dict(passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,new_PPO_updates=updates,saved_iteration=ck['iter'],Adam17_step=steps[0],actor35_critic38_STD6=True,full_DR_and_original_jump_memory_present=True,
   actual_saved_epoch=c['roles'][key]['formal']['epoch'],actual_GO=c['owner_closed']['cohort_final']['go'][key],not_skill_success=True)
 put('ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=reports,new_formal_reads=len(reports),old_models_read=0,CUDA_initialized=torch.cuda.is_initialized(),no_270_skill_inferred=True))
 print(json.dumps(dict(passed=True,roles={k:dict(iteration=v['saved_iteration'],Adam=v['Adam17_step'],updates=v['new_PPO_updates']) for k,v in reports.items()})))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT197_TWO_NEW_FORMALS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_promotion=True));raise
