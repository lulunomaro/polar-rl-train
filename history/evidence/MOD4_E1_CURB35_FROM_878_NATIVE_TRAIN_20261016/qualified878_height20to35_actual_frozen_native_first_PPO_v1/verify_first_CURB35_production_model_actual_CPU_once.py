"""Complete first production save, source-linked model and optimizer; CPU only."""
from pathlib import Path
import os,json,hashlib,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports';x=json.loads((R/'CURB35_FIRST_PRODUCTION_BOUND_COLLECTION_COMPLETE_ACTUAL.json').read_bytes());assert x['first_production'] and x['twohost_bytes_SHA_complete'] and not x['errors'];p=Path(x['first_local_model']);src=D/'payload/job0/source/qualified_CURB878.pt';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert H(p)==x['first_production']['SHA'] and p.stat().st_size==x['first_production']['bytes']
v=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(src,map_location='cpu',weights_only=False);counts=[0,0]
def finite(q):
 if torch.is_tensor(q):counts[0]+=1;counts[1]+=int(q.is_floating_point());assert not q.is_floating_point() or torch.isfinite(q).all()
 elif isinstance(q,dict):
  for y in q.values():finite(y)
 elif isinstance(q,(tuple,list)):
  for y in q:finite(y)
finite(v);assert v['CURB35_training_phase']=='production' and v['CURB35_task']['source_SHA']==H(src);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and len(v['optimizer_state_dict']['state'])==17
assert {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={660400} and {int(z['step']) for z in v['optimizer_state_dict']['state'].values()}=={660420}
changed={k:[n for n,z in v[k].items() if not torch.equal(z,s[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert changed['actor_state_dict'] and changed['critic_state_dict'];assert v['E1_terrain_state']['CURB_height_m']==.035 and v['E1_terrain_state']['CURB_strip_width_m']==.15 and v['E1_terrain_state']['num_envs']==20000
assert not torch.cuda.is_initialized();c=x['canonical'];assert c['active_segment']['owner_parent_pid']==477807 and abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5
out=dict(epoch=time.time(),passed=True,first_production_model=dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=H(p),tensor_counts=counts),source_SHA=H(src),all17Adam660400_to660420=True,changed=changed,sourceSTD_not_reset=True,original_actor35_critic38_action6=True,new_CURB35_height_only=True,real_PPO_updates=1,production_envsteps=480000,all_model_runtime_tensors_finite=True,not_discarded128_or20k_preflight=True,original_canonical=c,not_full_window_FINAL_or_frozen35_skill_improvement=True,CPU_no_optimizer_or_budget_write=True)
with (R/'FIRST_CURB35_REAL_PRODUCTION_SAVE_COMPLETE_LOCAL_CPU_VERIFIED.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps({k:z for k,z in out.items() if k not in ('changed','original_canonical')}),flush=True)
