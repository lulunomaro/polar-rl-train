from pathlib import Path
import json,time,sys,torch,numpy as np
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(B))
from h1_step270_path_reward_v1 import path_increment
rng=torch.get_rng_state().clone();n=20000;front=torch.zeros(n,2);origin=torch.linspace(-175,175,n);last=None;total=torch.zeros(n)
# Closed rectangle in position/height: unlike a weighted transport integral,
# the joint potential pays no net cycle reward, including vertical-only legs.
for x,h in [(0.,0.),(.2,0.),(.2,.30),(0.,.30),(0.,0.)]:
 current=torch.full((n,2),x)+origin[:,None]
 result=path_increment(previous_front=current if last is None else front,current_front=current,wheel_bottom=torch.full((n,2),h),origin_x=origin,active=torch.ones(n,dtype=torch.bool),airborne=torch.ones(n,dtype=torch.bool),launched=torch.ones(n,dtype=torch.bool),clean_upright=torch.ones(n,dtype=torch.bool),vx=torch.zeros(n),takeoff=torch.zeros(n,dtype=torch.bool),edge_event=torch.zeros(n,dtype=torch.bool),landing=torch.zeros(n,dtype=torch.bool),recovery=torch.zeros(n,dtype=torch.bool),previous_joint_potential=last)
 total+=result['total'];last=result['next_joint_potential'];front=current
assert float(total.abs().max())<2e-6 and torch.isfinite(total).all()
D=T/'H1_STEP270_REPLAY_DIAG_20261022_V105';a=np.load(D/'SELECTED_RECORDED_MOTION.npz')
index=json.loads((T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V13_20261022/current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());names=index['reward_terms'];cases=[]
for eid in (1912,17789,16932):
 col=int(np.flatnonzero(a['env_ids']==eid)[0]);values={k:float(a['reward_term_contribution'][:,col,names.index(k)].sum()) for k in ('h1_control_events','h1_scut_fudan_air_wheel_zero_torque','track_lin_vel')}
 cases.append(dict(env_id=eid,old_actual_48frame_contributions=values,new_air_zero_weight_only_same_actions_reweight=values['h1_scut_fudan_air_wheel_zero_torque']*.5/20,not_new_policy_performance=True))
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,float32_batch_environments=n,signed_position_height_closed_loop_max_abs=float(total.abs().max()),test_is_reward_arithmetic_not_geometry_gate=True,recorded_old_actual_reward_contributions=cases,selection_extremes_not_unbiased_eval=True,no_new_actor_optimizer_GPU_or_RNG=True,no_skill_or_success_claim=True)
with (B/'reports/RECORDED_REWARD_CONTRIBUTIONS_AND_SIGNED_LOOP_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
