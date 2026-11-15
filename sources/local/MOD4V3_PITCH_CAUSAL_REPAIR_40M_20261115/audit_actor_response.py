"""Read-only frozen actor response audit on identical recorded transition observations."""
from pathlib import Path
import torch,json,numpy as np,sys
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';sys.path.insert(0,str(D/'runtime/core'));from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1)
switches=json.loads((T/'evidence/causal_full/RESULT.json').read_text())['switches'];switches=[x for x in switches if x['case'].endswith('_baseline')];x=torch.tensor([r['obs']for r in switches],dtype=torch.float32)
old=T.parent/'MOD4V3_PITCH_RATE_SQUARE_40M_20261115';models={'db6':old/'weights/parent_comprehensive.pt','starting25m':old/'weights/model_025m.pt','phase1_final':T/'weights/model_final.pt'};outputs={}
for label,path in models.items():
 ck=torch.load(path,weights_only=False,map_location='cpu');net=ActorMLP().eval();net.load_state_dict(ck['actor_state_dict'],strict=False)
 with torch.no_grad():outputs[label]=net(x).clamp(-6,6).numpy()
a=outputs['phase1_final']-outputs['starting25m'];b=outputs['db6']-outputs['starting25m'];cosine=float(np.sum(a*b)/max(np.linalg.norm(a)*np.linalg.norm(b),1e-12));projection=float(np.sum(a*b)/max(np.sum(b*b),1e-12));rows=[]
for i,row in enumerate(switches):rows.append({'case':row['case'],**{k:v[i].tolist()for k,v in outputs.items()},'phase1_change_from25m':a[i].tolist()})
result={'no_optimizer':True,'observations':'Identical actual db6 first-stop35-D observations across8cases, not separate rollouts','direction_cosine_toward_db6':cosine,'projection_fraction_toward_db6':projection,'rows':rows,'interpretation':'Function-space drift can show movement toward frozen teacher on these states; it does not identify what fraction of actual PPO gradients came from BC. No causal attribution to BC from MSE alone.'};(T/'evidence/ACTOR_RESPONSE_DRIFT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
