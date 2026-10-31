"""Same-input counterfactuals are numeric diagnostics only; never control actions."""
import torch
SLOTS=dict(commands=(0,3),height=(3,4),angular_velocity=(4,7),gravity=(7,10),leg_position=(10,14),wheel_position_slots=(14,16),leg_velocity=(16,20),wheel_velocity=(20,22),previous_action=(22,28),mode_onehot=(28,35))
def diagnose(actor,obs,gradient=False):
 if obs.ndim!=2 or obs.shape[1]!=35 or not torch.isfinite(obs).all():raise ValueError('Expected finite fixedSI35 observation')
 original=obs.detach().clone();x=original.clone();mode0=x.clone();mode0[:,28:35]=0;mode0[:,28]=1
 mode1=x.clone();mode1[:,28:35]=0;mode1[:,29]=1
 no_previous=x.clone();no_previous[:,22:28]=0
 with torch.no_grad():
  actual=actor(x);m0=actor(mode0);m1=actor(mode1);p0=actor(no_previous)
  hidden=[];h=x
  for layer in actor:
   h=layer(h);hidden.append(float(h.abs().max()))
 result=dict(actual_mean=actual.detach().cpu().tolist(),counterfactual_mode0_mean=m0.detach().cpu().tolist(),counterfactual_mode1_mean=m1.detach().cpu().tolist(),counterfactual_previous_action_zero_mean=p0.detach().cpu().tolist(),layer_abs_max=hidden,
  changes_are_numeric_only_not_executed=True)
 if gradient:
  with torch.enable_grad():
   z=original.clone().requires_grad_(True);y=actor(z)[:,0].sum();g=torch.autograd.grad(y,z,only_inputs=True)[0]
  result['first_state_d_left_crank_mean_d_fixedSI35']=g.detach().cpu().tolist()
 assert torch.equal(obs,original)
 return result
