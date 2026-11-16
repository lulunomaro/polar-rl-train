"""Initial new-dataset gradients only: no optimizer creation/update."""
from pathlib import Path
import sys,json,hashlib,numpy as np,torch
T=Path(__file__).resolve().parent;R=T.parents[2];F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116';sys.path.insert(0,str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'));from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1);torch.manual_seed(0)
def load(p):
 c=torch.load(p,map_location='cpu',weights_only=False);m=ActorMLP();result=m.load_state_dict(c['actor_state_dict'],strict=False);assert not result.missing_keys;return m
m=load(T/'weights/parent_035m.pt');teacher=load(T/'comprehensive_keep_teacher.pt').eval().requires_grad_(False);params=list(m.parameters());before={k:v.clone()for k,v in m.state_dict().items()};a=np.load(T/'skill_dataset/qualified_mod4_skills.npz');x=torch.from_numpy(a['obs']);y=torch.from_numpy(a['actions']);w=torch.from_numpy(a['sampling_weight']).float();bank=np.load(F/'diagnosis_retention_01/fixed_normal_observation_bank.npz');normal=torch.from_numpy(bank['obs']);
with torch.no_grad():target=teacher(normal).clamp(-6,6)
def vector(loss):return torch.cat([v.flatten()for v in torch.autograd.grad(loss,params)])
skill=((m(x).clamp(-6,6)-y).square().sum(-1)*w).sum();gs=vector(skill);keep=(m(normal).clamp(-6,6)-target).square().sum(-1).mean();gk=vector(keep);ns=float(gs.norm());nk=float(gk.norm());dot=float(gs@gk);cos=dot/(ns*nk)if ns*nk else None;manifest=json.loads((T/'skill_dataset/MANIFEST.json').read_text());segments={}
for i,name in enumerate(manifest['semantic_names']):
 mask=a['semantic_id']==i;xx=x[mask];yy=y[mask];ww=w[mask];ww=ww/ww.sum();loss=((m(xx).clamp(-6,6)-yy).square().sum(-1)*ww).sum();g=vector(loss);n=float(g.norm());segments[name]=dict(loss_sum6=float(loss.detach()),gradient_norm=n,cosine_vs_keep=float(g@gk)/(n*nk)if n*nk else None,mass=manifest['semantic_sampling'][name]['mass'])
assert all(torch.equal(v,before[k])for k,v in m.state_dict().items())
result=dict(parent='model_035m',iteration=25455,dataset_sha256=manifest['sha256'],dataset_frames=len(x),normal_bank_samples=len(normal),skill_loss_sum6=float(skill.detach()),keep_loss_sum6=float(keep.detach()),gradient_skill_L2=ns,gradient_keep_L2=nk,skill_keep_gradient_dot=dot,skill_keep_gradient_cosine=cos,per_semantic_segment=segments,unweighted_losses_before_lambda=True,normal_bank='Frozen c874 fixed3task bank; not actual upcoming PPO minibatches',optimizer_steps=0)
(T/'evidence/INITIAL_GRADIENT_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('INITIAL_GRADIENT',json.dumps({k:v for k,v in result.items()if k!='per_semantic_segment'},ensure_ascii=False))
for name,row in segments.items():print('SEGMENT_GRADIENT',name,json.dumps(row))
