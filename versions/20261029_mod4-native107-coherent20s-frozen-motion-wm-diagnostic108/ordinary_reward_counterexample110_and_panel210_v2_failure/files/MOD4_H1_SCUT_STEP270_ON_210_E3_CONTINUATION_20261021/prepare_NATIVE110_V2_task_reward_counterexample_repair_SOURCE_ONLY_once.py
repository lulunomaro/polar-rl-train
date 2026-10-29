"""New110v2 reward source only, no saved model or physics execution."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'native110_preedge_monotone_reward_blend_source_v1'
B=L/'native110_preedge_monotone_task_reward_source_v2';assert not B.exists();B.mkdir();(B/'reports').mkdir()
src=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
H=lambda raw:hashlib.sha256(raw).hexdigest()
rn='mod4_fudan_contact_phase_reward_candidate_v2.py';an='native_fudan_step_adapter_candidate_v2.py';qn='OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'
original=(src/rn).read_bytes();v1=(A/rn).read_bytes()
eold=b"e=(m['body_forward_velocity']-m['command_forward_velocity']).square()"
enew=b"e=(m['task_planar_velocity']-m['task_command_planar_velocity']).square().sum(-1)"
assert v1.count(eold)==2
reward=v1.replace(eold,enew)
qold=b"quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.15**2-m['body_angular_velocity'].square().sum(-1)/.3**2)"
qnew=b"quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.15**2-m['world_vertical_velocity'].square()/.15**2-m['body_angular_velocity'].square().sum(-1)/.3**2)"
assert reward.count(qold)==1;reward=reward.replace(qold,qnew)
told=b"total=r+modes['jump']*mode_advantage+p.control_dt_s*placement"
tnew=b"total=r+modes['jump']*mode_advantage+12.*p.control_dt_s*placement"
assert reward.count(told)==1;reward=reward.replace(told,tnew)
assert reward.replace(tnew,told).replace(qnew,qold).replace(enew,eold)==v1
adapterold=(src/an).read_bytes();changes=[
 (b"max_step_reward=.1385",b"max_step_reward=.15"),
 (b"body_forward_velocity=body_v[...,0],body_yaw_velocity=body_w[...,2],",b"body_forward_velocity=body_v[...,0],body_yaw_velocity=body_w[...,2],\n            task_planar_velocity=v[...,:2],task_command_planar_velocity=torch.stack((modes['command_forward_velocity'],torch.zeros_like(v[...,2])),-1),"),
 (b"not_unmodified_upstream_reward_or_two_policy_controller=True,source_candidate_not_installed=True,successful_skill=False)",b"reward_velocity_frame='fixed_platform_world_XY',own_top_quiet_placement_weight=12.,quiet_includes_world_vertical_velocity=True,\n            not_unmodified_upstream_reward_or_two_policy_controller=True,source_candidate_not_installed=True,successful_skill=False)")]
adapter=adapterold
for a,b in changes:assert adapter.count(a)==1;adapter=adapter.replace(a,b)
inverse=adapter
for a,b in reversed(changes):inverse=inverse.replace(b,a)
assert inverse==adapterold
for name,data in [(rn,reward),(an,adapter),(qn,(src/qn).read_bytes())]:
 if name.endswith('.py'):ast.parse(data)
 (B/name).write_bytes(data)
contract=dict(kind='SOURCE_ONLY_NATIVE107_TO110V2_TASK_REWARD_COUNTEREXAMPLE_REPAIR',epoch=time.time(),
 source_model_metadata_only=dict(SHA='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef',bytes=256234249,iteration=17272,WM=172720,Pi=16632),
 baseline_reward_SHA=H(original),baseline_adapter_SHA=H(adapterold),candidate_reward_SHA=H(reward),candidate_adapter_SHA=H(adapter),reference_unchanged_SHA=H((src/qn).read_bytes()),
 changes=[
 'Use original recovery common baseline plus nonnegative mode advantage, not blend different total baselines.',
 'Approach mode monotone before leading-edge crossing, continuous decay after edge, original top-support recovery.',
 'Task planar velocity error is worldXY versus (+0.5,0) before top support and (0,0) on top, matching fixed platform goal. Original actual raw command/observations and body-frame diagnostics remain unchanged.',
 'Top quiet placement includes vertical speed as well as planar speed and angular speed.',
 'Placement weight12 gives0.12/control, strictly greater than bounded six jump bonuses0.0985/control. Conservative total bound0.15; max_step_reward changed only for log normalization.'],
 algebra=dict(J_nonnegative_upper=.0985,E_nonpositive='base_height_clipped + base_height_enhance + lin_vel_z - dt',common_upper=.02,w_bounds='0<=w<=1-P where P=top_support',total='C+dt+(1-w)*E+w*J+12*dt*P*quiet',upper='.03+.0985*(1-P)+.12*P <=.15',perfect_quiet_top_can_reach=.15,any_zero_top_support_upper=.1285,placement_coefficient_is_engineering_selection_not_measured_or_optimal=True),
 scope=['Not unchanged Fudan reward; task-specific adaptation with explicit source/adapter frame binding.',
 'Preedge positional monotonicity holds for unchanged supported floor pose with no top support/command change. No claim across physical landing/contact/reset or postedge decay.',
 'Priority repair is the user-provided mode-blend counterexample.109 geometry/vz gate proposal is NOT_SELECTED; extension0.31/tuck0.16/old positive-vz extension gate stay unchanged here.',
 'No new force/action trajectory/airborne reset/network/RNG/replay/physics/normalizer/optimizer.20s/request200..1999/private4096/horizon32/goal10/native100Hz/400plant/actual270acceptance retained.',
 'Source bounded algebra and synthetic checks cannot prove physical success, all reward correctness, WM accuracy or learned-policy gain.',
 'No candidate payload/producer/Task/GO or actualSDK/fullstate/resource admission yet; GPU training remains prohibited until those checks.'],
 adapter_exact_inverse_bytes=True,reward_exact_inverse_to_V1_bytes=True,reference_bytes_unchanged=True,
 saved_model_reads=0,raw_reads=0,remote_calls=0,source_only=True,CPU_tests_pending=True,actual_training_not_authorized_by_source_alone=True)
(B/'SOURCE_DELTA_TYPED_CONTRACT_110_V2.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,path=str(B),reward_SHA=H(reward),adapter_SHA=H(adapter))))

