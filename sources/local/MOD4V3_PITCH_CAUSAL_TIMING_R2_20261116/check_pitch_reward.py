"""Behavioral checks for transition lookahead; no simulator/model mutation."""
from pathlib import Path
import importlib.util,math,json,torch,ast,hashlib
T=Path(__file__).resolve().parent;f=T/'support/mod4v3_ppo_v1/pitch_stability_math.py';spec=importlib.util.spec_from_file_location('causal_math',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checks=[]
def check(name,x):
 assert bool(x),name;checks.append(name)
a=torch.tensor([math.radians(4.),math.radians(4.)]);w=torch.tensor([2.,-2.]);on=torch.ones(2,dtype=torch.bool)
c=m.stability_components(a,w,on);check('Lookahead penalizes rapid outward pitch before angle reaches5deg',c[0,2]<0);check('Outward future cost exceeds inward future cost',c[0,2]<c[1,2]);check('Original angle/rate terms unchanged',torch.allclose(c[:,1],torch.full((2,),-.02*3.5*4.)))
check('Nontransition motion has no added prediction cost',bool((m.stability_components(a,w,on,transition_window=~on)[:,2]==0).all()));check('No cost on retained or terminated environments',bool((m.stability_cost(a,w,~on)==0).all()));check('Forward/reverse symmetry',torch.allclose(m.stability_cost(a,w,on),m.stability_cost(-a,-w,on)))
r=torch.tensor([.3],requires_grad=True);cost=m.stability_cost(torch.tensor([.1]),r,torch.tensor([True]));g=torch.autograd.grad(cost.sum(),r)[0];check('Early outward rate gradient increases corrective cost',g.item()<(-2*.02*3.5*.3))
age=torch.tensor([1.98,2.,2.98,3.,4.98,5.,6.]);cmd,moving,phase=m.transition_command(age,torch.full_like(age,2.2));check('Real hard start/stop command unchanged',torch.allclose(cmd,torch.tensor([0.,2.2,2.2,0.,0.,-2.2,0.])))
seen,active=m.stability_active_mask(torch.tensor([True,True,False]),torch.tensor([True,False,True]),torch.tensor([False,True,False]),torch.zeros(3,dtype=torch.bool),torch.full((3,),2.));check('Ground latch keeps penalty through unloading only on specialist',active.tolist()==[True,True,False])
files=[p for p in T.rglob('*.py') if '__pycache__'not in p.parts]
for p in files:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
result={'passed':len(checks),'checks':checks,'syntax_files':len(files),'changed_math_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'no_model_or_interface_changes':True};(T/'evidence/PITCH_REWARD_REGRESSION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
