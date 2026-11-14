"""Check the changed reward and guidance without an optimizer or simulator."""
import ast
import json
from pathlib import Path
import sys
import time
import torch

T=Path(__file__).resolve().parent
sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.jump_height_objective import required_upward_speed,push_height_reward,measured_height_bonus
from mod4v3_ppo_v1.jump_bc import JumpGuidance

for path in (T/'support').rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8-sig'))
velocity=torch.tensor([1.,1.5,2.,2.4],requires_grad=True)
z=torch.full_like(velocity,.38)
reference=torch.full_like(velocity,.28)
target=torch.full_like(velocity,.32)
reward=push_height_reward(z,velocity,reference,target)
assert bool(torch.all(reward[1:]>reward[:-1])),reward
reward.sum().backward()
assert bool(torch.isfinite(velocity.grad).all())
speed=required_upward_speed(torch.tensor([.3,.6,.8]),torch.tensor([.6,.6,.6]))
assert torch.allclose(speed,torch.tensor([(2.*9.81*.3)**.5,0.,0.]))
increment=torch.tensor([0.,.01,.02])
bonus=measured_height_bonus(increment,torch.zeros(3),torch.full((3,),.32),torch.full((3,),.35),torch.ones(3))
assert bonus[0]==0 and bool(torch.all(bonus[1:]>bonus[:-1]))
assert measured_height_bonus(torch.tensor(.01),torch.tensor(.01),torch.tensor(.32),torch.tensor(.35),torch.tensor(0.))==0

class Actor:
    def __init__(self):
        self.output=torch.nn.Parameter(torch.zeros(6,6))
    def __call__(self,observations,stochastic_output=False):
        return self.output

class Algorithm:
    actor=Actor()

policy=torch.zeros(6,35)
policy[:,28]=1.
policy[1,32]=1.
policy[2,33]=1.
policy[3:5,30]=1.
policy[4,31]=1.
policy[5,31]=1.
spec=dict(initial=.1,final=.02,decay_seconds=3600.,demo_coefficient=0.,phase_weights=[1.,0.,0.,0.,1.])
guidance=JumpGuidance(spec,'cpu')
algorithm=Algorithm()
loss=guidance.compute(algorithm,dict(policy=policy,jump_target=torch.ones(6,6)))
loss.backward()
gradient=algorithm.actor.output.grad
assert bool((gradient[1:5]==0).all()),'Old labels must not constrain crouch, push or flight'
assert bool((gradient[[0,5]].abs().sum(1)>0).all())
result=dict(epoch=time.time(),passed=True,optimizer_created=False,optimizer_updates=0,
            upward_speeds_m_s=velocity.detach().tolist(),push_rewards=reward.detach().tolist(),
            reward_improves_above_old_1_5_m_s_cap=True,required_speed_zero_above_target=True,
            actual_body_height_increment_reward=True,old_demo_replay_disabled=True,
            crouch_push_flight_guidance_gradient_zero=True,approach_landing_guidance_active=True,
            guidance=guidance.finish(),source_AST_passed=True)
(T/'evidence/OBJECTIVE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
