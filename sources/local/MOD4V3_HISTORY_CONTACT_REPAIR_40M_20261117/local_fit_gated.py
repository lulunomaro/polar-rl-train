"""CPU warmup of a learned contact-conditioned single policy. No PPO updates."""
from pathlib import Path
import sys,json,time,copy,subprocess
import numpy as np,torch
from torch import nn
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.history_common import LocalHistoryActor,HistoryQueue
out=T/'local_probes/gated_v1';out.mkdir(exist_ok=False);torch.set_num_threads(1);torch.manual_seed(67);start=time.perf_counter()
seed=torch.load(T/'weights/source_step000.pt',map_location='cpu',weights_only=False);fitted=torch.load(T/'local_probes/direct/model_fit_04000.pt',map_location='cpu',weights_only=False);actor=LocalHistoryActor();base={k.removeprefix('mlp.'):v.clone()for k,v in seed['actor_state_dict'].items()if k.startswith('mlp.')};base['0.weight']=base['0.weight'][:,:35].clone();actor.mlp.normal.load_state_dict(base,strict=True);actor.mlp.skill.load_state_dict({k.removeprefix('mlp.'):v for k,v in fitted['actor_state_dict'].items()if k.startswith('mlp.')},strict=True);actor.encoder.load_state_dict(torch.load(T/'weights/encoder_pretrained.pt',map_location='cpu',weights_only=True));actor.encoder.requires_grad_(False);actor.mlp.history_mean.copy_(actor.encoder.mean);actor.mlp.history_scale.copy_(actor.encoder.scale)
def save(name,steps):
 ck=copy.deepcopy(seed);ck['actor_state_dict']={**actor.state_dict(),'distribution.std_param':seed['actor_state_dict']['distribution.std_param']};ck.pop('optimizer_state_dict',None);ck['format']='MOD4V3_HISTORY_CONTACT_GATED_V1';ck['contact_repair_warmup']=dict(gate_steps=2000 if steps else 0,skill_steps=steps,optimizer_steps=2000+steps if steps else 0,PPO_updates=0,wall_seconds=time.perf_counter()-start,normal_weights_frozen=True,normal_source='original010m/37dbe178',learned_gate_inputs='history420 only',external_teacher_assistance=False);torch.save(ck,out/name);return out/name
actor.mlp.gate[-1].bias.data.fill_(-30.);initial=save('model_base_only.pt',0)
with(out/'base_only.log').open('xb')as log:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'evaluate_student200.py'),'--model',str(initial),'--out',str(out/'base_only')],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,(out/'base_only.log').read_text();actor.mlp.gate[-1].bias.data.fill_(-6.)
data=np.load(T/'skill_dataset/history_skills.npz');x=torch.from_numpy(data['obs']);h=torch.from_numpy(data['history'].reshape(-1,420));y=torch.from_numpy(data['actions']);weights=torch.from_numpy(data['sampling_weight']);labels=torch.from_numpy(np.isin(data['semantic_id'],[3,4,5,6,7]).astype(np.float32)).unsqueeze(-1);pos=torch.where(labels[:,0]>.5)[0];neg=torch.where(labels[:,0]<.5)[0];extra=[]
for f in(out/'base_only').glob('start_*/rollout.npz'):
 a=np.load(f);o=a['obs'];hist=np.stack([o[np.maximum(0,np.arange(k-11,k+1))]for k in range(len(o))]).reshape(len(o),420);extra.append(hist[a['trace'][:,1]<.8])
negative=torch.from_numpy(np.concatenate(extra).astype(np.float32));opt=torch.optim.Adam(actor.mlp.gate.parameters(),lr=.001)
for k in range(2000):
 pi=pos[torch.randint(len(pos),(128,))];ni=neg[torch.randint(len(neg),(64,))];ei=torch.randint(len(negative),(64,));hi=torch.cat((h[pi],h[ni],negative[ei]));target=torch.cat((labels[pi],labels[ni],torch.zeros(64,1)));loss=nn.functional.binary_cross_entropy_with_logits(actor.mlp.gate_logit(hi),target);opt.zero_grad();loss.backward();opt.step()
with torch.no_grad():
 g=actor.mlp.gate_logit(h).sigmoid();gn=actor.mlp.gate_logit(negative).sigmoid();gate_report=dict(positive_accuracy=float((g[pos]>.5).float().mean()),negative_accuracy=float((g[neg]<.5).float().mean()),fresh_closed_loop_prewall_count=len(negative),fresh_prewall_max_gate=float(gn.max()),fresh_prewall_mean_gate=float(gn.mean()))
print('GATE_WARM',json.dumps(gate_report),flush=True);actor.mlp.gate.requires_grad_(False);opt=torch.optim.Adam(actor.mlp.skill.parameters(),lr=.0003);log=[]
for k in range(1,4001):
 ids=torch.multinomial(weights,256,replacement=True);pred=actor(x[ids],h[ids]).clamp(-6,6);skill=actor.mlp.skill(torch.cat((x[ids],actor.encoder(h[ids]).detach()),-1)).clamp(-6,6);active=labels[ids][:,0]>.5;loss=(pred-y[ids]).square().sum(-1).mean()+.5*(skill[active]-y[ids][active]).square().sum(-1).mean();opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(actor.mlp.skill.parameters(),5.);opt.step()
 if k in [1000,2000,4000]:
  ck=save(f'model_fit_{k:05d}.pt',k)
  with torch.no_grad():err=(actor(x,h).clamp(-6,6)-y).square().sum(-1);row=dict(step=k,contact_MSE=float(err[data['semantic_id']==3].mean()),lift_MSE=float(err[data['semantic_id']==4].mean()),weighted_action_MSE=float((err*weights/weights.sum()).sum()),normal_bank_unchanged=True,wall_seconds=time.perf_counter()-start)
  log.append(row);print('GATED_FIT',json.dumps(row),flush=True)
report=dict(PPO_updates=0,gate_optimizer_steps=2000,skill_optimizer_steps=4000,encoder_optimizer_steps=0,total_optimizer_steps=6000,wall_seconds=time.perf_counter()-start,normal_exact_old010m=True,gate_report=gate_report,fit=log)
(out/'FIT.json').write_text(json.dumps(report,indent=2)+'\n');print('GATED_COMPLETE',flush=True)
