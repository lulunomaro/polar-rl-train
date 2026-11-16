"""Bounded CPU actor repair: frozen physical encoder, skill supervision and c874 retention."""
from pathlib import Path
import sys,json,time,copy,argparse,hashlib
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.history_common import LocalHistoryActor
p=argparse.ArgumentParser();p.add_argument('--profile',choices=['direct','pcgrad'],default='direct');p.add_argument('--steps',type=int,default=4000);p.add_argument('--lr',type=float,default=.0003);a=p.parse_args()
torch.set_num_threads(1);torch.manual_seed(67);np.random.seed(67)
out=T/'local_probes'/a.profile;out.mkdir(exist_ok=False);start=time.perf_counter()
seed=torch.load(T/'weights/source_step000.pt',map_location='cpu',weights_only=False);actor=LocalHistoryActor().load_checkpoint(seed);actor.encoder.requires_grad_(False)
data=np.load(T/'skill_dataset/history_skills.npz');x=torch.from_numpy(data['obs']);h=torch.from_numpy(data['history'].reshape(-1,420));y=torch.from_numpy(data['actions']);w=torch.from_numpy(data['sampling_weight']);sem=data['semantic_id']
normal=np.load(T/'normal_bank.npz');nx=torch.from_numpy(normal['obs']);nh=nx[:,None,:].repeat(1,12,1).flatten(1);ny=torch.from_numpy(normal['target_actions'])
params=list(actor.mlp.parameters());opt=torch.optim.Adam(params,lr=a.lr);log=[]
def vec(loss):return torch.cat([v.reshape(-1)for v in torch.autograd.grad(loss,params)])
def metrics():
 with torch.no_grad():
  pred=actor(x,h).clamp(-6,6);err=(pred-y).square().sum(-1);keep=(actor(nx,nh).clamp(-6,6)-ny).square().sum(-1).mean()
  return dict(skill_sum6_MSE=float((err*w/w.sum()).sum()),keep_sum6_MSE=float(keep),contact_MSE=float(err[sem==3].mean()),lift_MSE=float(err[sem==4].mean()),cruise_MSE=float(err[sem==1].mean()),prewall_MSE=float(err[sem==9].mean()),latent_columns_norm=actor.mlp[0].weight[:,35:].norm().item())
initial=metrics();print('INITIAL',json.dumps(initial),flush=True)
for step in range(1,a.steps+1):
 ids=torch.multinomial(w,256,replacement=True);ni=torch.randint(len(nx),(256,));bc=(actor(x[ids],h[ids]).clamp(-6,6)-y[ids]).square().sum(-1).mean();keep=(actor(nx[ni],nh[ni]).clamp(-6,6)-ny[ni]).square().sum(-1).mean();opt.zero_grad(set_to_none=True)
 if a.profile=='direct':(bc+keep).backward()
 else:
  gs=vec(bc);gk=vec(keep);dot=torch.dot(gs,gk);cos=float(dot/(gs.norm()*gk.norm()+1e-12))
  if dot<0:gs=gs-dot/(gk.square().sum()+1e-12)*gk
  grad=gs+gk;offset=0
  for par in params:par.grad=grad[offset:offset+par.numel()].reshape_as(par).clone();offset+=par.numel()
 nn.utils.clip_grad_norm_(params,5.);opt.step()
 if step in sorted(set([500,1000,2000,a.steps])):
  ck=copy.deepcopy(seed);sd=actor.state_dict();ck['actor_state_dict']={**sd,'distribution.std_param':seed['actor_state_dict']['distribution.std_param']};ck['optimizer_state_dict_parent_architecture_only']=ck.pop('optimizer_state_dict',None);ck['repair_warmup']=dict(profile=a.profile,optimizer_steps=step,learning_rate=a.lr,encoder_frozen=True,paired_online_loss=False,wall_seconds=time.perf_counter()-start);f=out/f'model_fit_{step:05d}.pt';torch.save(ck,f);m=dict(step=step,**metrics(),wall_seconds=time.perf_counter()-start);log.append(m);print('FIT',json.dumps(m),flush=True)
report=dict(profile=a.profile,PPO_updates=0,actual_actor_optimizer_steps=a.steps,encoder_optimizer_steps=0,wall_seconds=time.perf_counter()-start,initial=initial,log=log,same_40_to256_to128_to64_to6_architecture=True,running_prior_run_modified=False,paired_unconditional_loss_removed_in_probe=True)
(out/'FIT.json').write_text(json.dumps(report,indent=2)+'\n');print('FIT_COMPLETE',flush=True)
