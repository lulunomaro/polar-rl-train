from pathlib import Path
import json, torch, hashlib
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
P=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
c=torch.load(P,map_location='cpu',weights_only=False)
out={'source':{'path':str(P),'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest()},'states':{},'perenv_tensor_fields':[]}
def walk(v,path=''):
 if torch.is_tensor(v):
  if 20000 in v.shape:out['perenv_tensor_fields'].append({'path':path,'shape':list(v.shape),'dtype':str(v.dtype)})
 elif isinstance(v,dict):
  for k,x in v.items():walk(x,path+'/'+str(k))
 elif isinstance(v,(tuple,list)):
  for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(c)
for k in ('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):
 out['states'][k]={n:({'shape':list(v.shape),'dtype':str(v.dtype)} if torch.is_tensor(v) else v) for n,v in c[k].items()}
O=Path(__file__).parent/'reports';O.mkdir(exist_ok=True)
(O/'D05C_BINDING_CPU_INVENTORY_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'source':out['source'],'perenv_fields':len(out['perenv_tensor_fields']),'states':out['states']},indent=2))
