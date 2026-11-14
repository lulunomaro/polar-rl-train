"""Concrete regression checks for floor-only rear shift and the observed drop-back pose."""
from pathlib import Path
import torch,importlib.util,json
T=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('coupled',T/'support/mod4v3_ppo_v1/coupled_transfer.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
x=torch.tensor([[-.25,-.25]]);stage=torch.tensor([0]);inside=torch.tensor([[.2,.2]]);no=torch.zeros(1,2,dtype=torch.bool);yes=~no
floor=torch.full((1,2),.0625);high=torch.full((1,2),.2775)
a,l=m.transfer_scores(x,floor,stage,inside,no);assert torch.equal(a,torch.zeros_like(a)), 'Rearward-only floor pose earns no transfer credit'
b,lb=m.transfer_scores(x,high,stage,inside,yes);assert torch.allclose(b,torch.ones_like(b)), 'Rear/up plus clear placement has full finite score'
g,best=m.transfer_credit(b,torch.zeros_like(b),torch.tensor([True]));assert torch.allclose(g,torch.ones_like(g))
g2,_=m.transfer_credit(b,best,torch.tensor([True]));assert float(g2)==0., 'No repeated credit for holding or oscillating below best'
g0,unchanged=m.transfer_credit(b,torch.zeros_like(b),torch.tensor([False]));assert float(g0)==0. and torch.equal(unchanged,torch.zeros_like(b)), 'Inactive flat/rough excluded'
aux=torch.full((1,2),.16);aux_score,aux_lift=m.transfer_scores(x,aux,stage,inside,no);g,_=m.transfer_credit(aux_score,aux_score.clone(),torch.tensor([True]));assert float(g)==0., 'Existing reset pose is not free reward'
loss=m.lift_regression(torch.zeros_like(aux_lift),aux_lift,torch.tensor([True]));assert float(loss)>0., 'Observed auxiliary drop to lower floor has regression cost'
one=torch.tensor([[.2775,.0625]]);c,_=m.transfer_scores(x,one,stage,inside,torch.tensor([[True,False]]));gain,_=m.transfer_credit(c,torch.zeros_like(c),torch.tensor([True]));assert 0<float(gain)<1, 'One wheel can clear before the other'
second,_=m.transfer_scores(x,aux+.2,torch.tensor([1]),inside,no);assert torch.allclose(second,aux_score,atol=1e-6), 'Same lower-relative pose at second stage keeps absolute tread semantics'
assert torch.isfinite(b).all()and 0<=float(.6*g2)<=.6
result=dict(passed=8,scope=['floor-only rearward no credit','finite complete transfer','no repeated best credit','retained-task mask','reset-state baseline','drop-back regression','asymmetric per-wheel clearing','second-stage absolute world-height consistency'])
(T/'evidence/COUPLED_REWARD_REGRESSION.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps(result))
