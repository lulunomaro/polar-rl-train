"""New whole20k CPU-only repair candidate; no deployment, CUDA or budget action."""
from pathlib import Path
import copy,json,time,hashlib,torch
D=Path(__file__).resolve().parent;N=D/'left_exploration20k_CPU_only_v1';assert not N.exists();N.mkdir()
source=D/'ORIGINAL_LINUX20K_OWN_ACTIVE_SAVE/model_32447.pt';SHA=hashlib.sha256(source.read_bytes()).hexdigest()
assert SHA=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
ck=torch.load(source,map_location='cpu',weights_only=False)
assert ck['E1_terrain_state']['num_envs']==20000 and ck['independent_terrain_expert']=='E1_WAVE50'
assert ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
assert 'LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION' not in ck
def same(a,b):
 if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 if hasattr(a,'shape'):
  import numpy as np
  return type(a)is type(b) and np.array_equal(a,b)
 return type(a)is type(b) and a==b
def build(c,source_sha,offset,margin=.14,std=1.):
 assert source_sha==SHA and c['E1_terrain_state']['num_envs']==20000
 assert 'LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION' not in c
 assert same(offset,[0.,0.,0.,0.]) and .1<margin<.3 and 0<std<=1.
 a=c['actor_state_dict'];o=c['optimizer_state_dict'];assert a['mlp.6.weight'].shape==(6,64) and a['distribution.std_param'].shape==(6,)
 assert o['param_groups'][0]['params']==list(range(17)) and len(o['state'])==17
 before=torch.get_rng_state().clone();out=copy.deepcopy(c);b=out['actor_state_dict'];desired=-1.0843+margin
 b['mlp.6.weight'][0].copy_(a['mlp.6.weight'][1]);b['mlp.6.bias'][0].copy_(a['mlp.6.bias'][1]+desired/.5);b['distribution.std_param'][0]=std
 for pid in (0,7,8):
  for k in ('exp_avg','exp_avg_sq'):out['optimizer_state_dict']['state'][pid][k][0].zero_()
 for k,v in a.items():
  if k in ('mlp.6.weight','mlp.6.bias','distribution.std_param'):assert torch.equal(v[1:],b[k][1:])
  else:assert torch.equal(v,b[k])
 for k in c:
  if k not in ('actor_state_dict','optimizer_state_dict'):assert same(c[k],out[k]),k
 assert same(o['param_groups'],out['optimizer_state_dict']['param_groups'])
 for pid in range(17):
  old=o['state'][pid];new=out['optimizer_state_dict']['state'][pid];assert same(old['step'],new['step'])
  for k in ('exp_avg','exp_avg_sq'):
   if pid in (0,7,8):assert torch.equal(old[k][1:],new[k][1:])
   else:assert same(old[k],new[k])
 assert torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']=dict(profile='left_initial_joint_margin014_std1_v1',source_SHA=SHA,source_envs=20000,desired_crank_minus_hip_rad=desired,source_left_scalar_std=float(a['distribution.std_param'][0]),initial_left_scalar_std=std,initial_left_mean_only_row0_of_final_layer=True,one_time_parameter_initialization_not_live_action_coupling=True,other5_heads_std_shared_trunk_critic_initial_exact=True,only_left_Adam_moment_rows0_7_8_cleared=True,Adam_all_step_counters_preserved=True,all_nonpolicy20k_perenv_fullDR_RNG_history_retained_exact=True,no_512_128_or_other_expert_splice=True,offset_reference=[0.,0.,0.,0.],offset_reference_requires_actual_all20k_native_API_before_use=True,CPU_prepared_only=True,targetfullstate_CPU_CUDA_native_and_PPO_not_passed=True,no_running_trainer_or_installedSDK_change=True,no_new_RNG=True,qualified50=False)
 return out
out=build(ck,SHA,[0.,0.,0.,0.]);neg=[]
for label,args in [('wrong source',(ck,'0'*64,[0.,0.,0.,0.])),('wrong offset',(ck,SHA,[.01,0.,0.,0.])),('repeat initializer',(out,SHA,[0.,0.,0.,0.]))]:
 try:build(*args)
 except AssertionError:neg.append(label)
 else:raise AssertionError(label+' accepted')
def floats(x):
 if isinstance(x,torch.Tensor):return int(x.is_floating_point())
 if isinstance(x,dict):return sum(floats(v) for v in x.values())
 if isinstance(x,(list,tuple)):return sum(floats(v) for v in x)
 return 0
assert floats(ck)==floats(out)==107
path=N/'own20k_left_joint_margin014_std1_CPU_prepared.pt';torch.save(out,path)
proof=dict(epoch=time.time(),CPU_component_passed=True,source=dict(path=str(source),sha256=SHA,bytes=source.stat().st_size),candidate=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),full_source_envs=20000,finite_floating_fields_count107=True,all_20000_DR_RNG_and_private_state_retained_exact=True,other5_mean_heads_std_trunk_critic_initial_exact=True,three_strictnegative_cases=neg,mean_and_exploration_std_reopened_only_left_head=True,current_frozen_mean_margin014_alone_not_passability_fix=True,stochastic_coadaptation_learning_NOT_executed=True,actual_target_CPU_native_offset_defaultq_CUDA_fullstate_ownstartup_and_PPO_NOT_passed=True,no_production_deployment=True,no_RNG_or_CUDA_or_budget_action=True)
(N/'CPU_COMPONENT_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(dict(CPU_component_passed=True,candidate_SHA=proof['candidate']['sha256'],source_envs=20000,std0_old_new=[float(ck['actor_state_dict']['distribution.std_param'][0]),1.],GPU_PPO_deployed=False)))
