"""Zero-PPO gate-only warmup. Both experts, estimator and STD remain byte-identical."""
from pathlib import Path
import sys,json,time,copy,hashlib
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.history_common import LocalHistoryActor
out=T/'local_probes/router_fit';out.mkdir(exist_ok=False);torch.set_num_threads(1);torch.manual_seed(67);start=time.perf_counter()
seed=torch.load(T/'weights/model_expert_pair.pt',map_location='cpu',weights_only=False);actor=LocalHistoryActor().load_checkpoint(seed);prior=copy.deepcopy(actor).requires_grad_(False)
f=T/'skill_dataset/history_skills.npz';raw=dict(np.load(f));labels=np.isin(raw['semantic_id'],[3,4,5,6,7]).astype(np.float32)
for ep in np.unique(raw['episode']):
 ids=np.where((raw['episode']==ep)&(raw['semantic_id']==8))[0];labels[ids[:20]]=1.
raw['gate_target']=labels;np.savez_compressed(f,**raw)
x=torch.from_numpy(raw['obs']);h=torch.from_numpy(raw['history'].reshape(-1,420));y=torch.from_numpy(raw['actions']);weights=torch.from_numpy(raw['sampling_weight']);target=torch.from_numpy(labels)[:,None]
neg=[]
for f in(T/'local_probes/expert_pair').glob('start_*/rollout.npz'):
 d=np.load(f);o=d['obs'];hh=np.stack([o[np.maximum(0,np.arange(k-11,k+1))]for k in range(len(o))]).reshape(len(o),420);neg.append(hh[d['trace'][:,1]<.8])
negative=torch.from_numpy(np.concatenate(neg).astype(np.float32))
with torch.no_grad():
 z=actor.encoder(h);nx=x.clone();nx[:,28:35]=nx.new_tensor([1,0,0,0,0,0,0]);a0=actor.mlp.normal(nx).clamp(-6,6);a1=actor.mlp.skill(torch.cat((x,z),-1)).clamp(-6,6);delta=a1-a0;gstar=(((y-a0)*delta).sum(-1)/delta.square().sum(-1).clamp_min(1e-8)).clamp(0,1);best=a0+gstar[:,None]*delta;res=(best-y).square().sum(-1);gprior=actor.mlp.gate_logit(h).sigmoid()
projection={str(int(k)):dict(frames=int((raw['semantic_id']==k).sum()),best_possible_action_MSE=float(res[raw['semantic_id']==k].mean()))for k in np.unique(raw['semantic_id'])}
(out/'FROZEN_EXPERT_PROJECTION.json').write_text(json.dumps(projection,indent=2)+'\n')
opt=torch.optim.Adam(actor.mlp.gate.parameters(),lr=.0001);rows=[]
for step in range(1,2001):
 ids=torch.multinomial(weights,256,replacement=True);ei=torch.randint(len(negative),(64,));pred=actor(x[ids],h[ids]).clamp(-6,6);logits=actor.mlp.gate_logit(h[ids]);bce=nn.functional.binary_cross_entropy_with_logits(logits,target[ids]);flat=nn.functional.binary_cross_entropy_with_logits(actor.mlp.gate_logit(negative[ei]),torch.zeros(64,1));anchor=(logits.sigmoid()-gprior[ids]).square().mean();loss=(pred-y[ids]).square().sum(-1).mean()+.25*bce+.5*flat+.05*anchor;opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(actor.mlp.gate.parameters(),1.);opt.step()
 if step in [500,2000]:
  ck=copy.deepcopy(seed);ck['actor_state_dict']={**actor.state_dict(),'distribution.std_param':seed['actor_state_dict']['distribution.std_param']};ck['moe_local_warmup']=dict(actual_gate_steps=step,expert_updates=0,encoder_updates=0,PPO_updates=0,elapsed_seconds=time.perf_counter()-start);name=out/f'model_gate_{step:05d}.pt';torch.save(ck,name)
  frozen=max(float((v-seed['actor_state_dict'][k]).abs().max())for k,v in actor.state_dict().items()if not k.startswith('mlp.gate.'));assert frozen==0
  with torch.no_grad():err=(actor(x,h).clamp(-6,6)-y).square().sum(-1);row=dict(step=step,loss=float(loss),weighted_action_MSE=float((err*weights/weights.sum()).sum()),frozen_parameter_max_change=frozen,wall_seconds=time.perf_counter()-start)
  rows.append(row);print('ROUTER_FIT',json.dumps(row),flush=True)
(out/'FIT.json').write_text(json.dumps(dict(PPO_updates=0,actual_gate_optimizer_steps=2000,expert_optimizer_steps=0,encoder_optimizer_steps=0,negative_frames=len(negative),gate_label='contact through capture; first0.4s post-mount active; later post/cruise normal',rows=rows,wall_seconds=time.perf_counter()-start),indent=2)+'\n')
