"""Second bounded local candidate: independent original010m skill inheritance, full E1 history gradients."""
from pathlib import Path
import sys,json,time,copy
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T/'support'));from mod4v3_ppo_v1.route2_common import LocalRoute2Actor
out=T/'local_probes/e1_warmup_v2';out.mkdir(exist_ok=False);torch.set_num_threads(1);torch.manual_seed(67);start=time.perf_counter();seed=torch.load(T/'local_probes/e1_warmup_v1/model_e1_12000.pt',map_location='cpu',weights_only=False);actor=LocalRoute2Actor().load_checkpoint(seed);old=torch.load(R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116/weights/model_010m.pt',map_location='cpu',weights_only=False)
with torch.no_grad():
 actor.mlp.e1.head[0].weight.zero_();actor.mlp.e1.head[0].weight[:,:35].copy_(old['actor_state_dict']['mlp.0.weight']);actor.mlp.e1.head[0].bias.copy_(old['actor_state_dict']['mlp.0.bias']);actor.distribution.e1_log_std.copy_(torch.tensor([.3,.3,.3,.3,.6,.6]).log())
 for i in [2,4,6]:actor.mlp.e1.head[i].weight.copy_(old['actor_state_dict'][f'mlp.{i}.weight']);actor.mlp.e1.head[i].bias.copy_(old['actor_state_dict'][f'mlp.{i}.bias'])
for k,v in old['critic_state_dict'].items():
 if k.startswith('mlp.'):seed['critic_state_dict']['mlp.e1.'+k.removeprefix('mlp.')]=v.clone()
seed['actor_state_dict']=copy.deepcopy(actor.state_dict());seed['iter']=0;seed['route2_source']['E1_initialization']='Independent original010m35D skill weights;12k nominally pretrained trainable16D history encoder; latent actor columns zero at hot inheritance';torch.save(seed,out/'model_hot_init.pt')
raw=dict(np.load(T/'skill_dataset/qualified_filtered.npz'));valid=np.ones(len(raw['obs']),bool);settle_review=[]
for ep in np.unique(raw['episode']):
 ids=np.where((raw['episode']==ep)&(raw['semantic_id']==0))[0]
 if len(ids):
  drift=float(raw['targets'][ids,0].sum()*.02);okay=abs(drift)<=.025;settle_review.append(dict(episode=int(ep),frames=len(ids),integrated_body_vx_m=drift,admitted=okay));valid[ids]=okay
raw={k:v[valid]for k,v in raw.items()};parts=[raw];ep=int(raw['episode'].max())+1
sources=[R/'sources/local/MOD4V3_MOE_FIXED200_40M_20261117/local_probes/expert_pair/start_+000mm/rollout.npz',T/'local_probes/e1_v1_10cm/start_+000mm/rollout.npz',T/'local_probes/e1_warmup_v1/cold_start_350/start_+000mm/rollout.npz']
for f in sources:
 d=np.load(f);tr=d['trace'];assert abs(float(tr[49,1]))<=.025;obs=d['obs'][:50];hist=np.stack([obs[np.maximum(0,np.arange(k-11,k+1))]for k in range(50)]);target=np.zeros((50,5),np.float32);target[:,0]=tr[:50,4];target[:,3:]=1.;parts.append(dict(obs=obs,actions=d['actions'][:50],history=hist,targets=target,episode=np.full(50,ep),offset=np.zeros(50,np.int64),semantic_id=np.zeros(50,np.int64),origin=np.full(50,98),sampling_weight=np.ones(50,np.float32)));ep+=1
merged={k:np.concatenate([v[k]for v in parts])for k in raw};frac=[.20,.15,.05,.15,.12,.06,.06,.04,.02,.15];w=np.zeros(len(merged['obs']),np.float32)
for sid,amount in enumerate(frac):
 ids=np.where(merged['semantic_id']==sid)[0]
 if len(ids):w[ids]=amount/len(ids)
merged['sampling_weight']=w;np.savez_compressed(T/'skill_dataset/e1_warmup_pool_v2.npz',**merged);x=torch.from_numpy(merged['obs']);h=torch.from_numpy(merged['history'].reshape(-1,420));y=torch.from_numpy(merged['actions']);target=torch.from_numpy(merged['targets']);w=torch.from_numpy(w);opt=torch.optim.Adam([{'params':actor.mlp.e1.head.parameters(),'lr':.0001},{'params':actor.mlp.e1.encoder.parameters(),'lr':.0003}]);rows=[]
for step in range(1,6001):
 ids=torch.multinomial(w,256,replacement=True);pred=actor(x[ids],h[ids]).clamp(-6,6);z=actor.mlp.e1.encoder(h[ids]);bc=(pred-y[ids]).square().sum(-1).mean();enc=(z[:,:3]-target[ids,:3]).square().mean()+.5*(z[:,3:5]-target[ids,3:5]).square().mean();loss=bc+.1*enc;opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(actor.mlp.e1.parameters(),5.);opt.step()
 if step in [2000,6000]:
  ck=copy.deepcopy(seed);ck['actor_state_dict']=actor.state_dict();ck['local_e1_warmup']=dict(actual_new_optimizer_steps=step,encoder_inherited_steps=12000,PPO_updates=0,E0_updates=0,STD_optimizer_steps=0,wall_seconds=time.perf_counter()-start);torch.save(ck,out/f'model_e1_{step:05d}.pt');row=dict(step=step,BC=float(bc.detach()),encoder_loss=float(enc.detach()),wall_seconds=time.perf_counter()-start);rows.append(row);print('E1_HOT_WARMUP',json.dumps(row),flush=True)
(out/'FIT.json').write_text(json.dumps(dict(actual_new_E1_optimizer_steps=6000,actual_total_local_optimizer_steps=18000,E0_optimizer_steps=0,PPO_updates=0,STD_optimizer_steps=0,frames=len(x),settle_admission=settle_review,startup_anchors_frames=150,semantic_sampling=frac,c874_keep_loss=0,paired_keep_loss=0,rows=rows,wall_seconds=time.perf_counter()-start),indent=2)+'\n')
