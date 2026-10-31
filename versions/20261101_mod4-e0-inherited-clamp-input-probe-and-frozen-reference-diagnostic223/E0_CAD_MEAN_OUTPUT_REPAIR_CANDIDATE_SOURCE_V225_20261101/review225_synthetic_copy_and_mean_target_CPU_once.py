"""New source-only candidate fixture;no actual checkpoint/model/raw/SDK reads."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import copy,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True)
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
def main():
 put('CPU225_SOURCE_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),synthetic_only=True,actual_model_raw_NPZ_SDK_GPU_remote_calls=0))
 import torch as t
 from candidate225_copy_only import repair_copy,ORDER
 assert not t.cuda.is_initialized();rng=t.random.get_rng_state().clone()
 def equal(a,b):
  if t.is_tensor(a):return t.equal(a,b)
  if isinstance(a,dict):return set(a)==set(b)and all(equal(a[k],b[k])for k in a)
  if isinstance(a,list):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
  return a==b
 with t.random.fork_rng(devices=[]):
  a={'mlp.6.weight':t.zeros(6,64),'mlp.6.bias':t.tensor([-100.,1.8,-.5,1.,0.,0.]),'distribution.std_param':t.tensor([24.,.12,.09,.10,.15,.13]),'mlp.0.weight':t.randn(256,35)}
  a['mlp.6.weight'][1]=t.linspace(-.002,.002,64)
  state=dict(actor_state_dict=a,critic_state_dict={'unchanged':t.randn(8)},optimizer_state_dict={'state':{},'param_groups':[{'params':list(range(17)),'lr':.00017}]})
  binding={'mlp.6.weight':0,'mlp.6.bias':1,'distribution.std_param':2}
  for i in range(17):
   shape=a[list(binding)[i]].shape if i<3 else (3,)
   state['optimizer_state_dict']['state'][i]=dict(step=t.tensor(649720.),exp_avg=t.full(shape,.01*i),exp_avg_sq=t.full(shape,.02*i))
  original=copy.deepcopy(state);proof=dict(synthetic_fixture_only=True,source_model_SHA='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538',policy_order=ORDER,leg_scales=[.5]*4,leg_default_offsets=[0.]*4,diff_min=-1.0843)
  result=repair_copy(state,proof,binding,allow_synthetic=True)
  assert equal(state,original)and equal(result['critic_state_dict'],state['critic_state_dict'])
  for k in ('mlp.6.weight','mlp.6.bias','distribution.std_param'):assert t.equal(result['actor_state_dict'][k][1:],a[k][1:])
  assert t.equal(result['actor_state_dict']['mlp.0.weight'],a['mlp.0.weight'])
  assert all(equal(result['optimizer_state_dict']['state'][i],state['optimizer_state_dict']['state'][i])for i in range(3,17))
  assert all(float(x['step'])==649720 for x in result['optimizer_state_dict']['state'].values())
  h=t.linspace(-1,1,64).repeat(32,1);old=h@a['mlp.6.weight'].T+a['mlp.6.bias'];new=h@result['actor_state_dict']['mlp.6.weight'].T+result['actor_state_dict']['mlp.6.bias']
  target=lambda u:t.maximum(u[:,0].clamp(-6,6)*.5,u[:,1].clamp(-6,6)*.5-1.0843)
  residual=float((target(old)-target(new)).abs().max());assert residual<1e-6
  rejects=0
  for p,b,allow in [(proof,binding,False),({**proof,'leg_scales':[1.]*4},binding,True),(proof,{},True),({**proof,'source_model_SHA':'foreign'},binding,True)]:
   try:repair_copy(state,p,b,allow_synthetic=allow)
   except ValueError:rejects+=1
   else:raise AssertionError('Bad or actual-unadmitted candidate accepted')
 assert t.equal(rng,t.random.get_rng_state())and not t.cuda.is_initialized()
 put('CPU225_COPY_ONLY_SYNTHETIC_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,groups=3,rejections=rejects,synthetic_states=32,conditional_original_mean_target_max_residual=residual,
  actual_model_or_original_E0_writes=0,actual_model_reads=0,physical_rollouts=0,global_RNG_unchanged=True,CUDA_initialized=False,
  source_only_not_selected_repaired_or_physical_pass=True,needs_actual_action_geometry_and_optimizer_binding=True))
 rows=[dict(path=str(p.relative_to(N)),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
 put('INDEX225_FROZEN_SOURCE_ONLY.json',dict(epoch=time.time(),files=rows,status='UNSELECTED_SOURCE_CANDIDATE;NO_ACTUAL_WEIGHT_WRITE_OR_TRAINING',actual_models_raw_SDK_GPU_remote_calls=0))
 print(json.dumps(dict(passed=True,groups=3,rejections=rejects,source_candidate_only=True,mean_target_residual=residual)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_CPU225_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
