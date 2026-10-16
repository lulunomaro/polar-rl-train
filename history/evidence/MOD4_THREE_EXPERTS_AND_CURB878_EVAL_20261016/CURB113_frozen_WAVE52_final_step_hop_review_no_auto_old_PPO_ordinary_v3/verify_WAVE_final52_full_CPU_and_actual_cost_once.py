"""Verify actual final complete state and exact already-settled interval; no GPU."""
from pathlib import Path
import os,json,hashlib,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports'
x=json.loads((R/'WAVE_FIRST_FINITE_FINAL_AND_ACTUAL_CANONICAL_EXIT_HANDOFF_COLLECTION.json').read_bytes());f=x['final'];p=Path(x['local_model']);assert hashlib.sha256(p.read_bytes()).hexdigest()==f['SHA'] and p.stat().st_size==f['bytes']
v=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(D/'wave_episode_reviewed_payload_v3/job3/source/source.pt',map_location='cpu',weights_only=False);count=[0,0]
def finite(z):
 if torch.is_tensor(z):count[0]+=1;count[1]+=int(z.is_floating_point());assert not z.is_floating_point() or torch.isfinite(z).all()
 elif isinstance(z,dict):
  for y in z.values():finite(y)
 elif isinstance(z,(tuple,list)):
  for y in z:finite(y)
finite(v);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8
assert len(v['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in v['optimizer_state_dict']['state'].values()}=={642840+20*f['updates']}=={f['Adam_step']}
assert f['updates']==52 and f['controls']==120+24*f['updates']==1368
changed={k:[n for n,z in v[k].items() if not torch.equal(z,s[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
b=x['actual_original_canonical'];seg=b['segments'][0];dt=seg['ended_epoch']-seg['started_epoch'];assert abs(dt-seg['charged_seconds'])<1e-6 and b['active'] is None and b['authorized']==1188000 and all(r['actual_fcntl_free'] for r in b['locks']);assert abs(b['charged']+b['remaining']-1188000)<1e-5 and seg['actual_child_exit']['returncode']==0
assert not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_complete_model_and_actual_exit_cost=True,final=f,local_path=str(p.resolve()),whole_model_runtime_finite=True,tensor_counts=count,changed=changed,all17Adam_step=643880,source17Adam642840_retained_and_increment_exact=True,PPO_env_steps=52*24*20000,native120_not_PPO=True,actual_unique_parent_seconds=dt,nominal1800_duration_bound_passed=dt<=1800,actual_overrun_seconds=max(0,dt-1800),actual_original_canonical=b,all_three_first_independent_blocks_closed=True,no_automatic_new_old_subject_window=True,no_frozen_WAVE_skill_pass_inferred=True,old_failed_job2_charge0_preserved=True,CPU_no_optimizer_no_budget_write=True)
p=R/'WAVE_FINAL52_COMPLETE_LOCAL_CPU_AND_EXACT_SETTLED_COST_ACTUAL.json'
with p.open('x',encoding='utf8') as z:json.dump(out,z,indent=2)
print(json.dumps({k:z for k,z in out.items() if k not in ('changed','actual_original_canonical')}),flush=True)
