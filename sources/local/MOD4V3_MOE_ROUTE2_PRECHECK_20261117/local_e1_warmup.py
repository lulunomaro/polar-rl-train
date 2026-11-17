"""Bounded local E1-only prewarm: teacher BC plus qualified E1 startup anchors; zero PPO."""
from pathlib import Path
import json,sys,subprocess,time,copy
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'));from mod4v3_ppo_v1.route2_common import LocalRoute2Actor
out=T/'local_probes/e1_warmup_v1';out.mkdir(exist_ok=False);start=time.perf_counter();torch.set_num_threads(1);torch.manual_seed(67);seed=torch.load(T/'weights/model_cold.pt',map_location='cpu',weights_only=False);actor=LocalRoute2Actor().load_checkpoint(seed);raw=dict(np.load(T/'skill_dataset/qualified_filtered.npz'));parts=[raw];ep=int(raw['episode'].max())+1
for stance in [.28,.35,.4091]:
 dest=out/f'cold_start_{round(stance*1000):03d}'
 with(out/f'cold_start_{round(stance*1000):03d}.log').open('wb')as log:subprocess.run([sys.executable,str(T/'evaluate_student200.py'),'--model',str(T/'weights/model_cold.pt'),'--out',str(dest),'--height','.2','--offsets','0','--stance',str(stance)],cwd=T,stdout=log,stderr=subprocess.STDOUT,check=True)
 d=np.load(dest/'start_+000mm/rollout.npz');o=d['obs'];tr=d['trace'];valid=(tr[:,1]<.75)&(np.abs(np.rad2deg(tr[:,6]))<15)&(tr[:,5]<=.65);n=int(np.where(~valid)[0][0])if np.any(~valid)else len(tr);o=o[:n];a=d['actions'][:n];h=np.stack([o[np.maximum(0,np.arange(k-11,k+1))]for k in range(n)]);target=np.zeros((n,5),np.float32);target[:,0]=tr[:n,4];target[:,3:]=1.;part=dict(obs=o,actions=a,history=h,targets=target,episode=np.full(n,ep),offset=np.zeros(n,np.int64),semantic_id=np.where(o[:,0]==0,0,9),origin=np.full(n,99),sampling_weight=np.ones(n,np.float32));parts.append(part);ep+=1;print('SELF_STARTUP_ANCHOR',stance,n,'pre1s',float(tr[49,1]),flush=True)
merged={k:np.concatenate([v[k]for v in parts])for k in raw};weights=np.zeros(len(merged['obs']),np.float32);fractions=[.10,.15,.05,.18,.13,.08,.08,.07,.06,.10]
for sid,amount in enumerate(fractions):
 ids=np.where(merged['semantic_id']==sid)[0]
 if len(ids):weights[ids]=amount/len(ids)
merged['sampling_weight']=weights;np.savez_compressed(T/'skill_dataset/e1_warmup_pool.npz',**merged)
x=torch.from_numpy(merged['obs']);h=torch.from_numpy(merged['history'].reshape(-1,420));y=torch.from_numpy(merged['actions']);target=torch.from_numpy(merged['targets']);w=torch.from_numpy(weights);opt=torch.optim.Adam([{'params':actor.mlp.e1.head.parameters(),'lr':.0003},{'params':actor.mlp.e1.encoder.parameters(),'lr':.0001}]);rows=[]
for step in range(1,12001):
 ids=torch.multinomial(w,256,replacement=True);pred=actor(x[ids],h[ids]).clamp(-6,6);z=actor.mlp.e1.encoder(h[ids]);bc=(pred-y[ids]).square().sum(-1).mean();enc=(z[:,:3]-target[ids,:3]).square().mean()+.5*(z[:,3:5]-target[ids,3:5]).square().mean();loss=bc+.1*enc;opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(actor.mlp.e1.parameters(),5.);opt.step()
 if step in [2000,6000,12000]:
  ck=copy.deepcopy(seed);ck['actor_state_dict']=actor.state_dict();ck['iter']=0;ck['local_e1_warmup']=dict(actual_optimizer_steps=step,PPO_updates=0,E0_updates=0,STD_optimizer_steps=0,encoder_end_to_end=True,wall_seconds=time.perf_counter()-start);torch.save(ck,out/f'model_e1_{step:05d}.pt')
  delta=max(float((v-seed['actor_state_dict'][k]).abs().max())for k,v in actor.state_dict().items()if k.startswith('mlp.e0.')or k=='distribution.e0_std');assert delta==0
  row=dict(step=step,BC=float(bc),encoder_loss=float(enc),E0_parameter_delta=delta,wall_seconds=time.perf_counter()-start);rows.append(row);print('E1_WARMUP',json.dumps(row),flush=True)
(out/'FIT.json').write_text(json.dumps(dict(actual_E1_optimizer_steps=12000,actual_encoder_steps=12000,E0_optimizer_steps=0,PPO_updates=0,STD_optimizer_steps=0,frames=len(x),self_startup_anchor_frames=sum(len(v['obs'])for v in parts[1:]),semantic_sampling=fractions,c874_keep_loss=0,paired_keep_loss=0,rows=rows,wall_seconds=time.perf_counter()-start),indent=2)+'\n')
