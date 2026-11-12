from pathlib import Path
import argparse,json,hashlib,torch
p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--out',required=True);a=p.parse_args()
f=Path(a.checkpoint);d=torch.load(f,map_location='cpu',weights_only=False)
required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','domain_randomization_state','terrain_curriculum_state']
assert all(k in d and d[k] is not None for k in required)
actor=d['actor_state_dict'];critic=d['critic_state_dict']
assert list(actor['mlp.0.weight'].shape)==[256,35] and list(actor['mlp.6.weight'].shape)==[6,64]
assert list(critic['mlp.0.weight'].shape)==[256,78]
assert d['action_order']==['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']
assert len(d['optimizer_state_dict']['state'])>0
assert d['reward_recipe']['profile']=='rough_scut_v1'
assert d['terrain_curriculum_state']['attempts'].shape==(11,10)
assert d['terrain_curriculum_state']['course']=='SCUT-Rough-v1-unified'
def finite(v):
 if torch.is_tensor(v):return bool(torch.isfinite(v).all())
 if isinstance(v,dict):return all(finite(x) for x in v.values())
 if isinstance(v,(list,tuple)):return all(finite(x) for x in v)
 return True
assert finite(actor) and finite(critic) and finite(d['optimizer_state_dict'])
w=d['reward_recipe']['weights'];coefficient=w['track_lin_vel_xy_square']*d['reward_recipe']['lin_vel_xy_square_sigma']**2
assert coefficient==-1.5 and w['track_lin_vel_xy']==1.2
r=dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),iteration=d['iter'],full_ppo_rng_present=True,all_policy_critic_optimizer_tensors_finite=True,interface=[35,78,6],num_envs=d['num_envs'],optimizer_entries=len(d['optimizer_state_dict']['state']),velocity_square_coefficient=coefficient,unified_terrain_state=list(d['terrain_curriculum_state']['attempts'].shape),action_order=d['action_order'])
Path(a.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False))
