from pathlib import Path
import json,hashlib,time,torch
from left_exploration_resume_contract_v1 import same,KEY
D=Path(__file__).resolve().parent
j=json.loads((D/'reports/LEFT_FRESH_RETAINED_POSTEXIT_ACTUAL_COLLECTION.json').read_bytes());v=j['independent_review']
assert v['passed'] and v['original_parent_passed'] is False and v['PPO_updates']==v['physical_controls']==0
row=next(x for x in j['two_host_byteSHA_exact'] if x['remote_path']==v['checkpoint']);p=Path(row['local_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
ck=torch.load(p,map_location='cpu',weights_only=False);old=torch.load(D/'left_native_own0PPO_actual/4_model_own_repaired0PPO.pt',map_location='cpu',weights_only=False)
for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict',KEY):assert same(ck[k],old[k]),k
def walk(x):
 if isinstance(x,torch.Tensor):yield x
 elif isinstance(x,dict):
  for z in x.values():yield from walk(z)
 elif isinstance(x,(tuple,list)):
  for z in x:yield from walk(z)
tensors=list(walk(ck));f=[x for x in tensors if x.is_floating_point()]
assert len(f)==107 and all(bool(torch.isfinite(x).all()) for x in f)
assert ck['E1_terrain_state']['num_envs']==20000 and ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
assert len(v['thirteen_actual_CPUCUDA_markers'])==13 and not torch.cuda.is_initialized()
q=D/'reports/LEFT_FRESH_RETAINED_LOCAL_CPU_PASSED.json';assert not q.exists()
out=dict(epoch=time.time(),passed=True,own_source=row,fullfloating107_finite=True,all_actor_critic_optimizer_branch_exact_native0PPO=True,thirteen_actual_sameidentity_CPUCUDA_markers_verified=True,original_parent_passed=False,independent_saved_source_admitted=True,PPO_updates=0,qualified50=False)
q.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
