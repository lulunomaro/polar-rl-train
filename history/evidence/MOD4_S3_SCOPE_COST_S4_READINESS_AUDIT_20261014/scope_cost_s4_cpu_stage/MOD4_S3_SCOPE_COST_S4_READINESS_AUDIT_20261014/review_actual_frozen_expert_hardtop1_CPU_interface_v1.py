"""Actual frozen source tensors and actual saved35-vectors; zero policy updates."""
from pathlib import Path
import torch,numpy as np,json,time,hashlib,traceback
from torch.nn import functional as F
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35,Gate35CPU,choose_whole_action
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 out=R/'S4_E0_WAVE35_ACTUAL_SOURCE_CPU_INTERFACE_AND_GRADIENT_ISOLATION.json';assert not out.exists()
 try:
  manifest=sorted(R.glob('FROZEN_E0_WAVE35_CPU_INPUTS_ACTUAL_*.json'))[-1];m=json.loads(manifest.read_bytes());assert len(m['sources'])==2
  states=[];models=[];source_counts=[]
  for row in m['sources']:
   assert H(row['local_path'])==row['sha256'] and row['twohost_byteSHA_exact']
   s=torch.load(row['local_path'],map_location='cpu',weights_only=False)
   assert s.get('history_architecture',{}).get('variant','A0')=='A0'
   states.append(s);models.append(FrozenMean35(s['actor_state_dict']))
   count=[0,0]
   def walk(v):
    if torch.is_tensor(v):
     assert v.device.type=='cpu';count[0]+=1
     if v.is_floating_point():assert torch.isfinite(v).all();count[1]+=1
    elif isinstance(v,dict):
     for x in v.values():walk(x)
    elif isinstance(v,(tuple,list)):
     for x in v:walk(x)
   walk(s);source_counts.append(dict(expert=row['expert'],tensors=count[0],floating=count[1]))
  assert [x['floating'] for x in source_counts]==[94,102]
  rng=torch.get_rng_state().clone();gate=Gate35CPU();assert torch.equal(rng,torch.get_rng_state())
  source_runtime=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/frozen_history_policy.py'
  assert "6,[256,128,64],'elu'" in source_runtime.read_text(encoding='utf8')
  base=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json';b=json.loads(base.read_bytes())
  raw=Path(b['raw']['local_path']);assert H(raw)==b['raw']['sha256']
  with np.load(raw) as z:
   obs=np.stack([z['policy_obs'][t,e] for t in [0,99,499,999,1499] for e in [0,6,15,27,51,64,67,69]])
  x=torch.from_numpy(obs.copy());assert x.shape==(40,35) and x.dtype==torch.float32
  x_before=x.clone();frozen_before=[p.snapshot() for p in models];gate_before={k:v.detach().clone() for k,v in gate.state_dict().items()}
  actions=torch.stack([p(x) for p in models],1);assert actions.shape==(40,2,6)
  # The synthetic gate scores exercise both selections; they are not terrain labels.
  scores=gate(x);eligible=torch.ones((40,2),dtype=torch.bool)
  selected,choice,clipped=choose_whole_action(actions,scores,eligible)
  assert torch.equal(selected,actions[torch.arange(40),choice]) and torch.equal(clipped,selected.clamp(-6,6))
  forced=torch.stack([torch.arange(40)%2==0,torch.arange(40)%2==1],1)
  selected_forced,ids,_=choose_whole_action(actions,scores,forced)
  assert torch.equal(ids,torch.arange(40)%2) and torch.equal(selected_forced,actions[torch.arange(40),ids])
  sticky=torch.tensor([[0.,.1]]).repeat(40,1);old=torch.zeros(40,dtype=torch.int64)
  assert torch.equal(choose_whole_action(actions,sticky,eligible,old,.2)[1],old)
  assert torch.equal(choose_whole_action(actions,sticky,forced,old,.2)[1],torch.arange(40)%2)
  optimizer=torch.optim.Adam(gate.parameters(),lr=1e-4)
  assert {id(p) for g in optimizer.param_groups for p in g['params']}=={id(p) for p in gate.parameters()}
  assert not any(list(expert.parameters()) for expert in models)
  F.cross_entropy(scores,torch.arange(40)%2).backward()
  assert any(p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum()>0 for p in gate.parameters())
  assert all(getattr(expert,'frozen_'+str(i)).grad is None for expert in models for i in range(9))
  assert all(torch.equal(v,gate_before[k]) for k,v in gate.state_dict().items()) and not optimizer.state
  assert torch.equal(x,x_before) and torch.equal(rng,torch.get_rng_state())
  assert all(torch.equal(v,models[i].snapshot()[k]) for i,s in enumerate(frozen_before) for k,v in s.items())
  assert all(H(row['local_path'])==row['sha256'] for row in m['sources'])
  negatives=[]
  for name,fn in [('wrong38input',lambda:gate(torch.zeros(4,38))),('no_eligible_expert',lambda:choose_whole_action(actions,scores,torch.zeros_like(eligible))),('five_action_blend_input',lambda:choose_whole_action(actions[:,:,:5],scores,eligible)),('nonfinite_gate',lambda:choose_whole_action(actions,scores+float('nan'),eligible)),('negative_hysteresis',lambda:choose_whole_action(actions,scores,eligible,hysteresis=-1.)),('wrong_previous',lambda:choose_whole_action(actions,scores,eligible,torch.full((40,),2,dtype=torch.int64)))]:
   try:fn()
   except AssertionError:negatives.append(name)
   else:raise AssertionError('Negative accepted: '+name)
  report=dict(epoch=time.time(),passed_CPU_interface_isolation_only=True,sources=m['sources'],source_counts=source_counts,actor_dimensions=[35,256,128,64,6],activation='elu',mean_only_CPU_no_sampling=True,
   actual_saved_obs_source=dict(path=str(raw),sha256=H(raw),source_checkpoint=b['source_SHA'],selected40_vectors=True,dimensions=35),
   saved_E3_Wave50_inputs_are_fixed_CPU_counterfactual_not_E0_or_WAVE35_physical50mm_evidence=True,
   shared_same_observation35_exact=True,complete_six_action_hardtop1_exact=True,no_action_or_parameter_averaging=True,original_clip6_after_selection_exact=True,
   expert_all9_buffers_weights_and_std_unchanged=True,gate_optimizer_contains_only_gate_params=True,expert_gradients_absent=True,gate_gradients_finite_nonzero=True,optimizer_updates=0,
   deterministic_initial_fixture_gate_not_trained=True,no_global_CPU_RNG_advance=True,no_CUDA_initialization=not torch.cuda.is_initialized(),
   eligible_and_previous_hysteresis_math_only=True,synthetic_scores_not_oracle_terrain_inference=True,negative_inputs_rejected=negatives,
   backend_source=dict(path=str(source_runtime),sha256=H(source_runtime)),
   GPU_native_adapter=False,transition_route_contract=False,whole_system_behavior=False,gate_training_started=False,S4_GPU_or_PPO_admitted=False,qualified_all_RM=False,
   remaining=['Record limited expert domains and original failure/rollback evidence; no inference terrain IDs','Implement own source-bound live wrapper sharing actual obs/noise cache and previous applied whole action; no stale per-expert last_action','Actual switch/torque jump/hysteresis/latency/termination and original contactCOMhardware transition-route checks, then actual native/full checkpoint/source/budget admission before any bounded gate learning'],
   source_reader_SHA=H(__file__),component_SHA=H(A/'hard_top1_frozen_expert_CPU_component_v1.py'),Git_pending=True)
  out.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode());print(json.dumps(dict(passed_CPU=True,actual_frozen_sources=['E0','E1_WAVE35'],shared_obs35=True,whole6action_hardtop1=True,expert_gradient_isolation=True,optimizer_updates=0,GPU_admitted=False)))
 except BaseException:
  p=R/('S4_CPU_INTERFACE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO_or_budget=True),indent=2).encode());raise

if __name__=='__main__':main()
