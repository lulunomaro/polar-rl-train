"""Use the already loaded new-purpose WM, without a net forward or extra file read."""
import torch
from native111_prior_WM_input_source_v1 import AugmentedWheelLegWorldModel as Original

def check(wm,state,normalized_context):
 n=state[0].shape[0]
 assert n>0 and len(state)==7 and normalized_context.shape==(n,31)
 before={k:v.detach().clone() for k,v in wm.state_dict().items() if k.startswith(('in_norm.','out_norm.'))}
 action=torch.zeros(n,6,device=state[0].device,dtype=state[0].dtype)
 old=Original.inputs(wm,state,action,normalized_context);new=wm.inputs(state,action,normalized_context)
 keep=torch.ones(167,dtype=torch.bool,device=old.device);keep[[1,3]]=False
 assert torch.equal(old[:,keep],new[:,keep]) and torch.isfinite(new).all()
 raw=(new-old).abs().amax(0);z=(wm.in_norm(new)-wm.in_norm(old)).abs().amax(0)
 assert raw[1]<=.0100002 and raw[3]<=.0050002
 assert wm.in_norm.eps==.01 and (wm.in_norm.std()>=.01).all()
 assert z[1]<=1.00002 and z[3]<=.50002 and torch.isfinite(z).all()
 # Separate synthetic pure-yaw pair validates this installed inputs dispatch.
 p=state[0][:1].expand(2,-1);R=torch.stack((torch.eye(3,device=p.device),torch.diag(torch.tensor([-1.,-1.,1.],device=p.device))))
 q=state[4][:1].expand(2,-1);zero=torch.zeros(2,3,device=p.device)
 pair=(p,R,zero,zero,q,torch.zeros_like(q),torch.zeros(2,54,device=p.device))
 a=torch.zeros(2,6,device=p.device);xi=normalized_context[:1].expand(2,-1)
 oldpair=Original.inputs(wm,pair,a,xi);newpair=wm.inputs(pair,a,xi)
 assert torch.equal(oldpair[0],oldpair[1]) and not torch.equal(newpair[0],newpair[1])
 assert all(torch.equal(v,wm.state_dict()[k]) for k,v in before.items())
 return dict(passed=True,rows=n,input_width=167,other165_columns_literal_unchanged=True,
  actual_loaded_normalizer_slots_1_3=dict(mean=wm.in_norm.mean[[1,3]].tolist(),std=wm.in_norm.std()[[1,3]].tolist(),count=float(wm.in_norm.count),eps=wm.in_norm.eps),
  actual_measurement_max_raw_shift=raw[[1,3]].tolist(),actual_measurement_max_normalized_shift=z[[1,3]].tolist(),
  synthetic_opposite_heading_pair_input_separated=True,normalizer_buffers_literal_unchanged=True,
  model_forward_or_normupdate_or_extra_model_read=False,not_dynamic_accuracy_or_real270_skill=True)
