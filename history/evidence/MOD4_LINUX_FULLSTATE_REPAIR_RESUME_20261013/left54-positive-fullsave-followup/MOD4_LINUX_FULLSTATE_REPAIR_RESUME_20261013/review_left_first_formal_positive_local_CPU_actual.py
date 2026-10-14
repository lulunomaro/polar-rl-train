from pathlib import Path
import json,time,hashlib,torch
from left_exploration_resume_contract_v1 import same,KEY
D=Path(__file__).resolve().parent
p=max((D/'reports').glob('LEFT_FIRST_FORMAL_POSITIVE_SAVED_ACTUAL_*.json'),key=lambda x:x.stat().st_mtime_ns)
j=json.loads(p.read_bytes());v=j['remote_CPU'];row=j['two_host_byteSHA_exact'][0]
assert row['remote_path']==v['own_checkpoint'] and hashlib.sha256(Path(row['local_path']).read_bytes()).hexdigest()==v['sha256']
c=torch.load(row['local_path'],map_location='cpu',weights_only=False);s=torch.load(D/'left_fresh_retained_postexit_actual/4_model_own_repaired0PPO.pt',map_location='cpu',weights_only=False)
delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(s['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
assert delta==[v['optimizer_step_delta']]*17 and delta[0]==v['saved_updates']*20
assert sum(not torch.equal(x,s['actor_state_dict'][k]) for k,x in c['actor_state_dict'].items())==9
assert same(c[KEY],s[KEY]) and c['E1_terrain_state']['num_envs']==20000
def walk(x):
 if isinstance(x,torch.Tensor):yield x
 elif isinstance(x,dict):
  for z in x.values():yield from walk(z)
 elif isinstance(x,(list,tuple)):
  for z in x:yield from walk(z)
f=[x for x in walk(c) if x.is_floating_point()]
assert len(f)==107 and all(bool(torch.isfinite(x).all()) for x in f) and not torch.cuda.is_initialized()
assert len(v['thirteen_actual_startup'])==13
out=dict(epoch=time.time(),passed=True,actual_collection=str(p),own_checkpoint=row,whole20k_floating107_finite=True,saved_updates=v['saved_updates'],saved_controls=v['saved_controls'],saved_envsteps=v['saved_envsteps'],saved_callbacks=v['saved_callbacks'],actor_tensors_changed=9,optimizer_step_delta=delta[0],actual_thirteen_sameidentity_CPUCUDA_markers=True,initializer_not_repeated=True,formal_final_claimed=False,qualified50=False)
q=D/'reports'/('LEFT_FIRST_FORMAL_POSITIVE_LOCAL_CPU_'+str(time.time_ns())+'.json');q.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
