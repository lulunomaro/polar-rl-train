"""Encoder-only optimization, zero PPO updates; group-held-out physical estimation."""
from pathlib import Path
import json,sys,time,hashlib,copy
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'));from mod4v3_ppo_v1.history_common import *
torch.set_num_threads(2);torch.manual_seed(6717)
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def metrics(y,t):
 return dict(velocity_MAE_m_s=(y[:,:3]-t[:,:3]).abs().mean(0).tolist(),velocity_RMSE_m_s=(y[:,:3]-t[:,:3]).square().mean(0).sqrt().tolist(),contact_accuracy=((y[:,3:]>.5)==(t[:,3:]>.5)).float().mean().item(),contact_Brier=(y[:,3:]-t[:,3:]).square().mean().item(),contact_positive_fraction=t[:,3:].mean(0).tolist(),contact_TPR=(((y[:,3:]>.5)&(t[:,3:]>.5)).sum()/((t[:,3:]>.5).sum().clamp_min(1))).item(),contact_TNR=(((y[:,3:]<=.5)&(t[:,3:]<=.5)).sum()/((t[:,3:]<=.5).sum().clamp_min(1))).item())
def main():
 started=time.perf_counter();a=np.load(T/'skill_dataset/history_skills.npz');x=torch.from_numpy(a['history'].reshape(-1,H*35));target=torch.from_numpy(a['targets']);train=torch.from_numpy(a['offset']!=60);valid=~train
 enc=HistoryEncoder();enc.mean.copy_(torch.from_numpy(a['history'][train.numpy()].reshape(-1,35).mean(0)));enc.scale.copy_(torch.from_numpy(a['history'][train.numpy()].reshape(-1,35).std(0)).clamp_min(.05));opt=torch.optim.Adam(enc.parameters(),lr=.0005);ids=train.nonzero().flatten();weights=torch.from_numpy(a['sampling_weight'])[ids];initial=metrics(enc(x[valid]).detach(),target[valid]);log=[]
 for step in range(3000):
  sel=ids[torch.multinomial(weights,512,replacement=True)];y=enc(x[sel]);loss=(y[:,:3]-target[sel,:3]).square().mean()+.5*(y[:,3:]-target[sel,3:]).square().mean();opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(enc.parameters(),5.);opt.step()
  if step%300==299:
   log.append(dict(step=step+1,loss=float(loss.detach()),heldout=metrics(enc(x[valid]).detach(),target[valid])));print('ENCODER',step+1,log[-1]['heldout'],flush=True)
 enc.eval();z=enc(x).detach();group=(a['origin']==1)|np.isin(a['semantic_id'],[3,4]);label=torch.from_numpy((a['origin']==0).astype(np.float32));gt=train&torch.from_numpy(group);gv=valid&torch.from_numpy(group)
 def probe(features):
  torch.manual_seed(67);mean=features[gt].mean(0);std=features[gt].std(0).clamp_min(.05);f=(features-mean)/std;head=nn.Sequential(nn.Linear(f.shape[1],32),nn.Tanh(),nn.Linear(32,1));optimizer=torch.optim.Adam(head.parameters(),lr=.005)
  for _ in range(500):
   b=head(f[gt]).squeeze(-1);loss=nn.functional.binary_cross_entropy_with_logits(b,label[gt]);optimizer.zero_grad();loss.backward();optimizer.step()
  score=head(f[gv]).squeeze(-1).detach();truth=label[gv]>.5;pred=score>0
  return dict(validation_samples=int(gv.sum()),flat_accuracy=float((~pred[~truth]).float().mean()),wall_accuracy=float(pred[truth].float().mean()),balanced_accuracy=float(((~pred[~truth]).float().mean()+pred[truth].float().mean())/2))
 separation=dict(latent_only=probe(z),current_only=probe(torch.from_numpy(a['obs'])),current_plus_latent=probe(torch.cat((torch.from_numpy(a['obs']),z),-1)),protocol='hold out every +60mm episode, all sources; diagnostic classifier only, not part of actor')
 parent=torch.load(T/'weights/parent_010m.pt',map_location='cpu',weights_only=False);expanded=copy.deepcopy(parent);expanded['actor_state_dict']=warm_state(parent,enc.state_dict());expanded['history_policy']=json.loads((T/'PLAN.json').read_text())['history_policy'];expanded['format']='MOD4V3_HISTORY_SEQUENCE_PPO_V1';expanded['PPO_updates_in_experiment']=0;expanded['encoder_pretrain_steps']=3000;expanded['optimizer_state_dict_parent_architecture_only']=expanded.pop('optimizer_state_dict');expanded['optimizer_migration']='fresh Adam on expanded actor+encoder+copied critic, parent optimizer retained in source checkpoint';torch.save(expanded,T/'weights/model_step000.pt');torch.save(enc.state_dict(),T/'weights/encoder_pretrained.pt')
 local=LocalHistoryActor().load_checkpoint(expanded);original=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6));original.load_state_dict({k.removeprefix('mlp.'):v for k,v in parent['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
 with torch.no_grad():diff=(local(torch.from_numpy(a['obs']),x)-original(torch.from_numpy(a['obs']))).abs().max().item()
 report=dict(PPO_updates=0,encoder_optimizer_steps=3000,wall_seconds=time.perf_counter()-started,training_episode_count=int(torch.unique(torch.from_numpy(a['episode'])[train]).numel()),validation_episode_count=int(torch.unique(torch.from_numpy(a['episode'])[valid]).numel()),validation_offset_mm=60,initial_heldout=initial,final_heldout=metrics(z[valid],target[valid]),separation=separation,hot_actor_max_abs_error=diff,critic_identical=all(torch.equal(v,expanded['critic_state_dict'][k])for k,v in parent['critic_state_dict'].items()),new_latent_columns_zero=bool((expanded['actor_state_dict']['mlp.0.weight'][:,35:]==0).all()),log=log)
 report['physical_estimation_gate']=max(report['final_heldout']['velocity_MAE_m_s'])<.2 and report['final_heldout']['contact_accuracy']>.8 and separation['current_plus_latent']['balanced_accuracy']>.8
 put(T/'preflight/ENCODER_PREFLIGHT.json',report);print('ENCODER_REPORT',json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
