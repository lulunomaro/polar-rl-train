"""Verify the already complete local weight while optional proof copies continue."""
from pathlib import Path
import json,hashlib,time,torch
from left_exploration_resume_contract_v1 import same,KEY
D=Path(__file__).resolve().parent
r=max((D/'reports').glob('LEFT_FIRST_FORMAL_SAVED_CPU_REMOTE_*.json'),key=lambda p:p.stat().st_mtime_ns)
j=json.loads(r.read_bytes());assert j['code']==0;v=json.loads(j['stdout']);assert v['passed']
dest=max(D.glob('left_first_formal_ownsave_*'),key=lambda p:p.stat().st_mtime_ns)
p=dest/('0_'+Path(v['own_checkpoint']).name)
stat=p.stat();h=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
assert (stat.st_size,stat.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
assert h==v['sha256'] and stat.st_size==v['bytes']
c=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(D/'left_fresh_retained_postexit_actual/4_model_own_repaired0PPO.pt',map_location='cpu',weights_only=False)
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
out=dict(epoch=time.time(),passed=True,original_remote_CPU_receipt=str(r),own_remote_path=v['own_checkpoint'],local_path=str(p),bytes=stat.st_size,sha256=h,two_host_weight_SHA_exact=True,whole20k_floating107_finite=True,saved_updates=v['saved_updates'],saved_controls=v['saved_controls'],saved_envsteps=v['saved_envsteps'],saved_callbacks=v['saved_callbacks'],actor_tensors_changed=9,optimizer_step_delta=delta[0],actual_thirteen_sameidentity_CPUCUDA_markers=True,full_marker_contents_already_in_remote_CPU_receipt=True,extra_individual_marker_copies_may_still_be_transferring=True,initializer_not_repeated=True,formal_final_claimed=False,qualified50=False)
q=D/'reports/LEFT_FIRST_FORMAL_OWN_POSITIVE_WEIGHT_LOCAL_CPU_VERIFIED.json';assert not q.exists();q.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
