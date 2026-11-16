"""Compare all three frozen students on identical semantic demonstrations; no updates."""
from pathlib import Path
import sys,json,numpy as np,torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def audit():
 out=E/'DATASET_FIT_AUDIT.json'
 if out.exists():return json.loads(out.read_text())['rows']
 sys.path.insert(0,str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'));from play_ppo_flatv1 import ActorMLP
 torch.set_num_threads(1);manifest=json.loads((T/'skill_dataset/MANIFEST.json').read_text());data=np.load(T/'skill_dataset/qualified_mod4_skills.npz');x=torch.from_numpy(data['obs']);y=torch.from_numpy(data['actions']);rows=[]
 for name in ['parent_010m','model_005m','model_010m']:
  model=ActorMLP();model.load_state_dict(torch.load(T/'weights'/(name+'.pt'),map_location='cpu',weights_only=False)['actor_state_dict'],strict=False);model.eval()
  with torch.inference_mode():err=(model(x).clamp(-6,6)-y).square().sum(1).numpy()
  per={n:float(np.sum(err[data['semantic_id']==i]*data['sampling_weight'][data['semantic_id']==i])/data['sampling_weight'][data['semantic_id']==i].sum())for i,n in enumerate(manifest['semantic_names'])};rows.append(dict(checkpoint=name,weighted_sum6_MSE=float(np.sum(err*data['sampling_weight'])),per_semantic_sum6_MSE=per,optimizer_updates=0))
 out.write_text(json.dumps(dict(rows=rows,source_dataset_unchanged=True,all_MSE_sum6=True,optimizer_updates=0,additional_simulation=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');return rows
if __name__=='__main__':
 for row in audit():print('FROZEN_FIT',json.dumps(row))
