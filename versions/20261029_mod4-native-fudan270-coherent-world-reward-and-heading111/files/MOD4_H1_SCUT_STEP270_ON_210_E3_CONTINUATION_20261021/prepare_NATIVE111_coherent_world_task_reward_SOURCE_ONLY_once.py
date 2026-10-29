"""NEW source preparation only. No model, raw case, SDK, remote, or GPU operation."""
from pathlib import Path
import ast,hashlib,json,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
OLD=L/'native110_task_reward_contact_semantics_source_v4'
B=L/'native111_coherent_world_task_reward_source_v1'
SRC=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27'
assert not B.exists();B.mkdir();(B/'reports').mkdir()
def H(x):return hashlib.sha256(x).hexdigest()
def put(n,x):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:
  f.write(x if isinstance(x,str) else json.dumps(x,indent=2,ensure_ascii=False))
def replace(s,a,b):
 assert s.count(a)==1,a[:70]
 return s.replace(a,b)
try:
 reward=(OLD/'mod4_fudan_contact_phase_reward_candidate_v2.py').read_text(encoding='utf8')
 adapter=(OLD/'native_fudan_step_adapter_candidate_v2.py').read_text(encoding='utf8')
 rr=reward;aa=adapter
 reward=replace(reward,'    approach_speed_m_s: float=.5','    platform_half_width_m: float=.6\n    approach_speed_m_s: float=.5')
 reward=replace(reward,'        assert self.step_top_z_m>0 and self.control_dt_s==.01','        assert self.step_top_z_m>0 and self.control_dt_s==.01 and self.platform_half_width_m==.6')
 reward=replace(reward,'    z=(m[\'relative_base_height\']-p.standing_body_height_m).square()',
 '''    # Two authored support planes, never a fictitious interpolated plane.
    zg=(m['root_height']-p.standing_body_height_m).square()
    zt=(m['root_height']-p.standing_body_height_m-p.step_top_z_m).square()
    P=m['top_support']
    height=(1-P)*1.5*torch.exp(-zg*1000)+P*1.5*torch.exp(-zt*1000)
    height_extra=(1-P)*(torch.exp(-zg/.01)-1)+P*(torch.exp(-zt/.01)-1)''')
 reward=replace(reward,'        base_height=1.5*torch.exp(-z*1000),base_height_enhance=torch.exp(-z/.01)-1,',
 '        base_height=height,base_height_enhance=height_extra,')
 reward=replace(reward,'    footprint=torch.sigmoid(full_rear_gap/.02)*torch.sigmoid(far_gap/.02)',
 '''    side_low_gap=wheel_low[...,1].amin(-1)+p.platform_half_width_m
    side_high_gap=p.platform_half_width_m-wheel_high[...,1].amax(-1)
    def inside(gap):
        t=(gap/.02).clamp(0,1)
        return t*t*(3-2*t)
    # Exact zero outside any authored XY bound. Differentiable C1 interior ramp.
    footprint=inside(full_rear_gap)*inside(far_gap)*inside(side_low_gap)*inside(side_high_gap)''')
 reward=replace(reward,"                footprint=footprint,full_rear_gap=full_rear_gap,",
 "                footprint=footprint,full_rear_gap=full_rear_gap,side_low_gap=side_low_gap,side_high_gap=side_high_gap,")
 reward=replace(reward,"                support_surface_height=p.step_top_z_m*top_support)",
 "                support_surface_height=p.step_top_z_m*top_support)  # diagnostic expectation only; never used as a reward plane")
 reward=replace(reward,"    quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.15**2-m['world_vertical_velocity'].square()/.15**2-m['body_angular_velocity'].square().sum(-1)/.3**2)",
 '''    # Physical success still uses its exact contact/footprint/12+200 counters.
    # These smooth planning cues now include static heading and tilt, not only motion.
    tilt_error=(1-m['upright_cos']).clamp_min(0)
    heading_error=(1-m['heading_cos']).clamp_min(0)
    quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.03**2
        -m['world_vertical_velocity'].square()/.03**2
        -m['body_angular_velocity'].square().sum(-1)/.3**2
        -tilt_error/(1-0.984807753012208)
        -heading_error/(1-0.9800665778412416))
    # Dense task cues share the recovery baseline; neither is mode-blended.
    task_alignment=.5*p.control_dt_s*(torch.exp(-heading_error/(1-0.9800665778412416))
        +torch.exp(-m['root_lateral_position'].square()/.3**2))*m['request_active']''')
 reward=replace(reward,"    total=r+modes['jump']*mode_advantage+12.*p.control_dt_s*placement",
 "    total=r+modes['jump']*mode_advantage+12.*p.control_dt_s*placement+task_alignment")
 reward=replace(reward,"                nonpositive_recovery_extra=recovery_extra,mode_advantage=mode_advantage)",
 "                nonpositive_recovery_extra=recovery_extra,mode_advantage=mode_advantage,task_alignment=task_alignment,top_quiet=quiet)")
 adapter=replace(adapter,'import torch\n','import torch\nfrom supermimic_wheel_leg_v3.geometry import mat_to_6d\n')
 adapter=replace(adapter,'    max_step_reward=.15', '    max_step_reward=.16')
 adapter=replace(adapter,'    def relative_features(self,state,frames):',
 '''    # Goal and goal normalizer stay byte-identical. Supply the previously
    # removed heading through the existing six orientation slots, without an
    # architecture change or normalizer reset. Current raw norms remain inherited.
    def obs(self,state,previous_action,context,frames):
        value=super().obs(state,previous_action,context,frames)
        return torch.cat((value[...,:1],mat_to_6d(state[1]),value[...,7:]),-1)
    def critic_features(self,state,frames,normalized_context):
        value=super().critic_features(state,frames,normalized_context)
        return torch.cat((value[...,:1],mat_to_6d(state[1]),value[...,7:]),-1)
    def relative_features(self,state,frames):''')
 adapter=replace(adapter,"            relative_base_height=p[...,2]-modes['support_surface_height'],action=action,previous_action=previous_action,",
 '''            relative_base_height=p[...,2],top_support=modes['top_support'],
            upright_cos=R[...,2,2],heading_cos=R[...,0,0]/R[...,:2,0].norm(dim=-1).clamp_min(1e-6),
            root_lateral_position=p[...,1],request_active=active,
            action=action,previous_action=previous_action,''')
 oldsoft='''        height=torch.sigmoid((.12-state[0][...,2])/.02);tilt=torch.sigmoid((math.cos(.75)-state[1][...,2,2])/.04)
        timeout=(decode_private_frame(frames)['public_age']>=2000).to(height.dtype)
        return 1-(1-height)*(1-tilt)*(1-timeout)'''
 newsoft='''        # Physical low_base is disabled at -1m; do not invent a .12m hard failure.
        # Declare the sigmoid as a 32-control horizon risk (engineering surrogate),
        # not the same full risk repeated every 10ms. Exact physical tilt/timeout
        # masks remain certain here; all real physics termination functions stay unchanged.
        cos_tilt=state[1][...,2,2]
        horizon_risk=torch.sigmoid((math.cos(.75)-cos_tilt)/.04)
        soft=-torch.expm1(torch.log1p(-horizon_risk.clamp_max(1-1e-6))/32.)
        certain=(cos_tilt<math.cos(.75))|(decode_private_frame(frames)['public_age']>=2000)
        return torch.where(certain,torch.ones_like(soft),soft)'''
 adapter=replace(adapter,oldsoft,newsoft)
 adapter=replace(adapter,"            reward_velocity_frame='fixed_platform_world_XY',own_top_quiet_placement_weight=12.,quiet_includes_world_vertical_velocity=True,",
 '''            reward_velocity_frame='fixed_platform_world_XY',actor_orientation_frame='full_world_rotation6d',
            goal_and_goal_normalizer_unchanged=True,own_top_quiet_placement_weight=12.,
            task_alignment_bonus_max_per_control=.01,platform_full_XY_bounds=True,
            height_rewards_two_actual_planes_not_interpolated=True,soft_tilt_risk_controls=32,
            physical_low_base_disabled_minus1=True,quiet_includes_world_vertical_velocity_heading_and_tilt=True,''')
 doc=json.loads((OLD/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes())
 # Reference bytes deliberately unchanged; width comes from actual authored source.
 put('OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json',(OLD/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_text(encoding='utf8'))
 put('mod4_fudan_contact_phase_reward_candidate_v2.py',reward)
 put('native_fudan_step_adapter_candidate_v2.py',adapter)
 changes=[]
 for name,old,new in [('mod4_fudan_contact_phase_reward_candidate_v2.py',rr,reward),('native_fudan_step_adapter_candidate_v2.py',aa,adapter)]:
  ast.parse(new);changes.append(dict(name=name,input_SHA=H((OLD/name).read_bytes()),output_SHA=H((B/name).read_bytes()),only_source_not_runtime=True))
 task=(SRC/'job0/runtime/isaac/mod4/mod4_task.py').read_text(encoding='utf8')
 assert 'low_base = DoneTerm(func=low_base_relative, params={"minimum_height": -1.0})' in task
 runtime=(SRC/'h1_step270_sdk_runtime_candidate.py').read_text(encoding='utf8')
 assert 'height=.270,edge_x=.35,depth=.8,width=1.2' in runtime
 put('SOURCE_DELTA_AND_BEFORE_USE_CONTRACT_111_V1.json',dict(epoch=time.time(),kind='SOURCE_ONLY_NEW_HUMAN_TASK_COHERENCE_REPAIR',changes=changes,
  source107='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef',
  human_before_use_gate=True,actual_target_SDK_fullstate_reward_readback_pending=True,
  no_new_H1_learning_GO=True,goal_reference_bytes_unchanged=True,model_norm_threeopts_architecture_unchanged=True,
  obs_and_critic_orientation_semantics_changed=True,goal_normalizer_count_may_already_be_frozen=True,
  raw_obs_normalizer_preserved_not_claimed_distribution_preserving=True,
  reward_upper_bound=.16,zero_top_support_upper_bound=.1385,
  physical_low_base_source=-1.,physical_tilt_limit=.75,imagined_tilt_risk_is_declared_32_step_engineering_calibration_not_measured_probability=True,
  height_reward_planes=[doc['metadata']['bound_own_step_reward']['standing_body_height_m'],doc['metadata']['bound_own_step_reward']['standing_body_height_m']+.27],
  authored_platform_XY=[[.35,-.6],[1.15,.6]],actual_target_geometry_and_config_readback_required=True,
  preserved=['2000control20s','request200..1999','private4096','age_seconds','32horizon10goals','50percentfocus/max8/fallback','gamma.99/TDlambda','WM/Pi/critic/3optimizers','400plant/2.5ms/TGS32/4/100Hz/clip6/PD/DR/delay/reset','true270cross/fullfootprint/top12/stable200'],
  excluded=['no .31/.16 geometry retune','no scripted action/force/airborne reset','no old model/raw read','no SDK/GPU/remote','no universal reward-correctness or skill claim']))
 print(json.dumps(dict(prepared_source_only=True,path=str(B),changes=changes)))
except BaseException:
 put('reports/SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_runtime_or_model_read=True));raise
