"""New necessary one-read CPU384 fullrestore + RL residual differentiability admission."""
from pathlib import Path
import ast
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V384_20261102'
s=(T/'REFERENCE_H8_DIRECT_TRACKING_REPAIR_V344_20261102/test344_final324_H8_direct_no_step_CPU_once.py').read_text('utf8')
s=s.replace('CPU344','CPU384').replace('tracking_reference324 import Reference324','tracking_reference384 import Reference384').replace('tracking_learner344 import TrackingLearner344','tracking_learner384 import TrackingLearner384').replace('tracking_wm324 import TrackingWM324','tracking_wm384 import TrackingWM384').replace("N/'reference324.npz'","N/'reference384.npz'").replace('target324=torch.tensor','target384=torch.tensor')
needle=" before={k:v.detach().clone()for k,v in learner.actor.state_dict().items()}"
block=""" # The inherited actor remains byte exact; its residual starts exactly0.
 phase=torch.arange(80,dtype=torch.long)%250
 aa=learner.action(policy,ctx[:,31:],packed,phase)
 baseline=learner.residual_policy.baseline(phase).clamp(-6,6)
 assert torch.equal(aa,baseline)
 probe=torch.randn(8,103,requires_grad=True)
 raw_live=forward(learner.actor,probe);raw_origin=forward(learner.residual_origin_actor,probe)
 value=learner.residual_policy.raw(raw_live,raw_origin,torch.arange(8)).sum()
 input_grad=torch.autograd.grad(value,probe,retain_graph=True)[0]
 assert torch.count_nonzero(input_grad)==0, 'Zero residual must havezero state derivative beforelearning'
 parameter_grad=torch.autograd.grad(value,tuple(p for p in learner.actor.parameters()if p.requires_grad),allow_unused=True)
 assert sum(float(g.abs().sum())for g in parameter_grad if g is not None)>0
 assert all(p.grad is None and not p.requires_grad for p in learner.residual_origin_actor.parameters())
"""
assert needle in s;s=s.replace(needle,block+needle)
s=s.replace("report=dict(epoch=time.time(),passed=True,", "report=dict(epoch=time.time(),passed=True,learner_SHA=hashlib.sha256((S/'tracking_learner384.py').read_bytes()).hexdigest(),RL_residual=True,initial_action_exact_fixedfeedforward=True,residual_origin_params_frozen=True,residual_input_gradient_correct=True,residual_parameter_gradient_nonzero=True,online_MPC=False,")
s=s.replace("CPU384_RESTORED324_H8_DIRECT_NO_STEP.json","CPU384_RESIDUAL_RL_NO_STEP.json")
ast.parse(s)
with(N/'test384_residual_RL_fullrestore_no_step_CPU_once.py').open('x',encoding='utf8')as f:f.write(s)
print('CPU384 prepared;one necessary final324read,zero optimizer/SDK/physics')
