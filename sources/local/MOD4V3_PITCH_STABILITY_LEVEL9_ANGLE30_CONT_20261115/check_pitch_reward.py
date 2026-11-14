"""Regression checks for body attitude and hard transition exposure."""
from pathlib import Path
import importlib.util,math,json
import torch
T=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pitch_math',T/'support/mod4v3_ppo_v1/pitch_stability_math.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
def check(n,v):
 assert bool(v),n
 checks.append(n)
a=math.radians(20.)
g=torch.tensor([[math.sin(a),0.,-math.cos(a)],[-math.sin(a),0.,-math.cos(a)],[0.,math.sin(a),-math.cos(a)]])
p=m.body_pitch(g)
check('gravity-derived actual body pitch has correct20degree magnitude',abs(float(p[0])-a)<1e-6)
check('roll alone is not penalized as pitch',abs(float(p[2]))<1e-6)
c=m.stability_cost(p,torch.zeros(3),torch.ones(3,dtype=torch.bool))
check('nose up and nose down have equal square cost',abs(float(c[0]-c[1]))<1e-6)
check('five degree allowance leaves small necessary motion unpenalized',float(m.stability_cost(torch.tensor([math.radians(4.)]),torch.zeros(1),torch.tensor([True])))==0.)
check('grounded pitch-rate damping remains active with zero pitch',float(m.stability_cost(torch.zeros(1),torch.ones(1),torch.tensor([True])))<0.)
check('flight retained rough stairs and non-target tasks are exempt',float(m.stability_cost(torch.ones(1),torch.ones(1),torch.tensor([False])))==0.)
t=torch.tensor([1.9,2.,2.99,3.,4.99,5.,6.]);v,_,_=m.transition_command(t,torch.full_like(t,2.2))
check('start and stop commands are actual step changes without artificial ramp',torch.allclose(v,torch.tensor([0.,2.2,2.2,0.,0.,-2.2,0.])))
check('alternating motion remains within contract speeds',float(v.abs().max())<=2.20001)
check('angle-only cost equals30 times excess radians square',abs(float(c[0])-(-.02*30*(a-math.radians(5.))**2))<1e-7)
check('pitch-rate coefficient remains0.35',abs(float(m.stability_cost(torch.zeros(1),torch.ones(1),torch.tensor([True])))+.02*.35)<1e-7)
result=dict(passed=len(checks),checks=checks,no_policy_improvement_claim=True)
(T/'evidence/PITCH_REWARD_REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
