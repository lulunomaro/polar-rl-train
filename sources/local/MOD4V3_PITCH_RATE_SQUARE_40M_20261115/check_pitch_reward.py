from pathlib import Path
import importlib.util,math,json,torch
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pitch_rate_math',T/'support/mod4v3_ppo_v1/pitch_stability_math.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(name,condition):
 if not bool(condition):raise AssertionError(name)
 checks.append(name)
v=torch.tensor([0.,.5,1.,2.,3.,-3.],requires_grad=True);z=torch.zeros_like(v);on=torch.ones_like(v,dtype=torch.bool)
r=m.stability_cost(z,v,on);check('Actual rad/s coefficient3.5 with dt0.02',torch.allclose(r,-.02*3.5*v.square()))
g=torch.autograd.grad(r.sum(),v)[0];check('Square cost derivative is -2*k*dt*omega',torch.allclose(g,-2*3.5*.02*v))
check('Double rate gives four times cost',torch.isclose(r[3],4*r[2]));check('Both pitch directions have symmetric cost',torch.isclose(r[4],r[5]))
check('No angular deadband lets early fast motion be penalized inside5deg',r[2]<0)
check('Non-target stairs planned flight and retention tasks receive zero extra',bool((m.stability_cost(torch.ones(6),v,~on)==0).all()))
a=math.radians(20);c=m.stability_cost(torch.tensor([a,-a]),torch.zeros(2),torch.ones(2,dtype=torch.bool));check('Existing angle30 cost retained',torch.allclose(c,torch.full((2,),-.02*30*(a-math.radians(5))**2)))
check('Four degree slow motion remains inside angle allowance',float(m.stability_cost(torch.tensor([math.radians(4)]),torch.zeros(1),torch.tensor([True])))==0)
t=torch.tensor([1.9,2.,2.99,3.,4.99,5.,6.]);cmd,_,_=m.transition_command(t,torch.full_like(t,2.2));check('Hard start stop commands unchanged',torch.allclose(cmd,torch.tensor([0.,2.2,2.2,0.,0.,-2.2,0.])))
target=torch.tensor([True,True,False]);contact=torch.tensor([True,False,True]);seen=torch.zeros(3,dtype=torch.bool);term=torch.zeros(3,dtype=torch.bool);age=torch.full((3,),2.)
seen,on=m.stability_active_mask(target,contact,seen,term,age);check('First actual contact arms target only; retained stair contact stays exempt',torch.equal(on,torch.tensor([True,False,False])))
seen,on=m.stability_active_mask(target,torch.zeros(3,dtype=torch.bool),seen,term,age);check('Momentary wheel unloading cannot escape squared pitch-rate cost',torch.equal(on,torch.tensor([True,False,False])))
_,on=m.stability_active_mask(target,torch.zeros(3,dtype=torch.bool),torch.zeros_like(seen),term,age);check('Reset-cleared history prevents carrying contact into another episode',not bool(on.any()))
_,on=m.stability_active_mask(target,contact,seen,torch.ones_like(term),age);check('Terminated episodes are excluded',not bool(on.any()))
result=dict(passed=len(checks),checks=checks,square_cost_gradient='-2*k*omega; the cost quadruples at double rate; no claim gradient itself is squared',no_policy_improvement_claim=True)
(T/'evidence/PITCH_REWARD_REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
