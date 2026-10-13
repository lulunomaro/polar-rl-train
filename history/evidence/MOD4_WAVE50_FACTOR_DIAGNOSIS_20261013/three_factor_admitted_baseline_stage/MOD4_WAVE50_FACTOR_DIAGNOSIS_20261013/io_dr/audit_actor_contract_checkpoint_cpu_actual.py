from pathlib import Path
import hashlib,json,time
import torch
D=Path(__file__).resolve().parent;W=D.parents[1]
P=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt'
torch.set_num_threads(1)
sha=hashlib.sha256(P.read_bytes()).hexdigest()
assert sha=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
c=torch.load(P,map_location='cpu',weights_only=False)
a=c['actor_state_dict'];q=c['critic_state_dict']
assert list(a['mlp.0.weight'].shape)==[256,35] and list(a['mlp.6.weight'].shape)==[6,64]
assert list(q['mlp.0.weight'].shape)==[256,38]
assert all(torch.isfinite(v).all() for v in a.values()) and all(torch.isfinite(v).all() for v in q.values())
assert not any(any(x in k.lower() for x in ('rnn','gru','lstm','encoder')) for k in a)
def walk(x):
 if torch.is_tensor(x):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,(list,tuple)):
  for v in x:yield from walk(v)
f=[t for t in walk(c) if t.is_floating_point()]
assert len(f)==107 and all(torch.isfinite(t).all() for t in f)
o=dict(id='own32396_A0_actor_contract_CPU_actual',epoch=time.time(),no_GPU_PPO_SDK=True,
checkpoint=dict(path=str(P),sha256=sha,bytes=P.stat().st_size,finite_floating_tensor_count=len(f)),
actor_weight_shapes={k:list(v.shape) for k,v in a.items()},critic_weight_shapes={k:list(v.shape) for k,v in q.items()},
actual_actor_first_layer35=True,actual_critic_first_layer38=True,no_saved_recurrent_or_history_encoder_tensors=True,
runner_actor_group=['policy'],heightscan_or_heading_channel_not_present_in35schema=True,
previous_requested_action_and_current_angvelocity_remain_indirect_signals=True,
missing_route_heading_not_declared_sufficient_causal_proof=True)
out=D/'OWN32396_ACTOR_CONTRACT_CPU_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(o,ensure_ascii=False,indent=2))
