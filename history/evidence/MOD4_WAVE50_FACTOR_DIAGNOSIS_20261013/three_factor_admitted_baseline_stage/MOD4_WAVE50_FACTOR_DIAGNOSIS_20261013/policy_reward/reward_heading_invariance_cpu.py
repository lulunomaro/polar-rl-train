"""Synthetic reward invariance, no physical or learned behavior claim."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,importlib.util,json,time
import torch
D=Path(__file__).resolve().parent;W=D.parents[1]
src=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/isaac/mod4/scut_flat_rescue.py'
spec=importlib.util.spec_from_file_location('isolated_heading_fixture',src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=torch.tensor([[.3,0.,0.],[.3,0.,0.]],dtype=torch.float64)
data=SimpleNamespace(root_lin_vel_b=torch.tensor([[.3,0.,0.],[.3,0.,0.]],dtype=torch.float64),
 projected_gravity_b=torch.tensor([[0.,0.,-1.],[0.,0.,-1.]],dtype=torch.float64),
 root_ang_vel_b=torch.zeros((2,3),dtype=torch.float64))
env=SimpleNamespace(scene={'robot':SimpleNamespace(data=data)},command_manager=SimpleNamespace(get_command=lambda _:c))
parts={'linear_exp':m.linear_exp(env,std=.25),'linear_tight':.2*m.linear_exp(env,std=.01),
       'linear_gap':-m.linear_gap(env),'linear_square':-m.linear_square(env),
       'yaw_exp':.5*m.yaw_exp(env),'pitch':-m.orientation(env,mode='pitch')}
assert all(torch.equal(x[0],x[1]) for x in parts.values())
total=sum(parts.values());assert not torch.cuda.is_initialized()
report=dict(epoch=time.time(),passed=True,source=dict(path=str(src),bytes=src.stat().st_size,sha256=hashlib.sha256(src.read_bytes()).hexdigest()),
 CPU_synthetic_same_BODY_velocity_gravity_yaw_rate=True,
 example0_heading_deg=0,example1_heading_deg=90,
 both_BODY_vx_m_s=.3,corresponding_world_route_X_vx_m_s=[.3,0],
 exact_reward_parts={k:v.tolist() for k,v in parts.items()},selected_reward_sum=total.tolist(),
 no_absolute_heading_read_by_these_reward_functions=True,
 conclusion='These scalar rewards accept a turned-but-no-longer-turning body as equal to route-aligned motion. This is an objective ambiguity, not a numerical sign bug.',
 only_selected_terms_not_total_reward=True,no_GPU_no_PPO=True,
 no_claim_of_feasible_turn_on_terrain_or_unique_forward_failure_cause=True,
 original_physics_route_qualification_unchanged=True)
p=D/'REWARD_HEADING_INVARIANCE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(p),passed=True,selected_terms_sum=total.tolist())))
