"""Check whether nominal forward drift predates stair shaping; frozen old actors."""
from pathlib import Path
import json,torch,time
import kinematics_audit as audit
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence/history_trend';E.mkdir(exist_ok=True);audit.E=E
paths={'roughv0_100m':R/'sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_100m.pt',**{f'roughv1_{m:03d}m':R/f'sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/weights/model_{m:03d}m.pt' for m in (60,80,95,100,105,110,115,120)}}
missing=[]
for name,p in paths.items():
 if not p.exists():missing.append(str(p));continue
 d=torch.load(p,map_location='cpu',weights_only=False);layers=[]
 for i,(x,y) in enumerate(zip((35,256,128,64),(256,128,64,6))):
  layers.append(torch.nn.Linear(x,y))
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers);actor.load_state_dict({k.removeprefix('mlp.'):v for k,v in d['actor_state_dict'].items() if k.startswith('mlp.')});actor.eval()
 audit.identities[name]=dict(path=str(p),sha256=audit.hashlib.sha256(p.read_bytes()).hexdigest(),iteration=d['iter']);audit.run(name,actor,5,(2.2,))
(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),missing=missing,no_optimizer=True)),encoding='utf8')
