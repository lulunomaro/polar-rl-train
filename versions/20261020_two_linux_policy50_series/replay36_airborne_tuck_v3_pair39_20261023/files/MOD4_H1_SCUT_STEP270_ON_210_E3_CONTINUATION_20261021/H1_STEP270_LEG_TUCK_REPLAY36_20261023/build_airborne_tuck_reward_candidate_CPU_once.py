from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
import numpy as np

D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';C=D/'candidate_reward';P=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

try:
    extracted=read(R/'EXTRACTION_SOURCE_CPU_ACTUAL.json');geo=read(R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json')
    with np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
        pos=k['body_pose'][:,:,:,:3,3];names=geo['body_names'];delta=np.take(pos,[names.index('left_wheel'),names.index('right_wheel')],axis=2)-pos[:,:,None,0,:];length=np.linalg.norm(delta,axis=-1)
        j=extracted['reward_terms'].index('h1_scut_fudan_leg_tuck');con=z['reward_term_contribution'][:,:,j];cases=[]
        for c in sorted(geo['case_summaries'],key=lambda c:c['both_wheel_bottom_max_m'],reverse=True)[:8]:
            f=c['apex_row'];e=c['column'];cases.append(dict(c,body_to_wheel_axle_3D_m_at_apex=length[f,e].tolist(),request_at_apex=bool(z['public_request'][f,e]),actual_weighted_tuck_contribution_at_apex=float(con[f,e])))
    put('NEW36_RECORDED_LEG_EXTENSION_AND_REWARD_SCOPE_ACTUAL.json',dict(epoch=time.time(),source_scope='New closed36 prefixes113/114, 48 controls/.48s; stochastic PPO records before last updates, not FINAL policy evaluation or whole-window count.',sources=extracted['sources'],source_artifact=extracted['artifact'],derived_kinematics_artifact=geo['artifact'],all20k_request_world_vx_quantiles=extracted['requested_world_vx_m_s_quantiles'],actual_weighted_tuck=extracted['actual_weighted_reward_contributions']['h1_scut_fudan_leg_tuck'],selected_cases=cases,selected_positive_tuck_contribution_frames=int((con>0).sum()),interpretation='Several high-lift selected cases remain around447mm while actual tuck shaping is already positive; request cutoff alone cannot explain all extension. The original .5 rate weight makes extended-airborne contribution around.00081 per10ms. Original reward source gates tuck by request AND actual air_ticks; after-request contribution is0 in this clip. This supports a bounded scalar shaping revision, not a unique global cause or predicted success.',joint_order_derived_not_new_PhysX_readback=True,not_original31_raw_reread=True,no_PT_actor_optimizer_RNG_GPU_or_new_physics=True))
    assert not C.exists();shutil.copytree(P/'repair_sources',C)
    refs=C/'reference_sources';refs.mkdir(exist_ok=True)
    original=C/'h1_step270_path_reward_v1.py';old=original.read_text('utf8');shutil.copy2(original,refs/'h1_step270_path_reward_replay_v2_reference.py')
    prior=read(P/'reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json')['new_reward_integration_CPU']
    (refs/'PREVIOUS_INSTALLED_REPLAY_V2_REWARD_CPU_ACTUAL.json').write_text(json.dumps(prior,indent=2),encoding='utf8')
    # The exact inherited tensor adapter is included for isolated local CPU checks.
    shutil.copy2(P/'payloads/h1/job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py',refs/'h1_takeoff_progress_environment_v2.py')
    function='''def airborne_tuck_rate(env):
    from h1_takeoff_progress_environment_v2 import tensor
    p=env.h1_phase;r=env.scene['robot'];data=r.data
    root=tensor(data.root_state_w)
    ids=[r.body_names.index(x) for x in ('left_wheel','right_wheel')]
    delta=tensor(data.body_pos_w)[:,ids]-root[:,None,:3]
    active=p.attempt & (p.air_ticks>0) & ~p.landed & ~p.crossed.all(-1)
    # Same original SCUT/Fudan measured body-to-wheel length formula.
    # Request expiry must not end retraction shaping during measured flight.
    # Stop before landing extension once both wheels actually crossed.
    compact=torch.exp(-torch.sum(torch.abs(delta.norm(dim=-1)-.22),dim=1)*4.)
    return active.to(root.dtype)*compact


'''
    new=old.replace("version='step270_forward_clearance_replay_v2'","version='step270_forward_clearance_airborne_tuck_v3'").replace('leg_tuck_weight=.5','leg_tuck_weight=1.7')
    anchor='def configure(cfg):';assert new.count(anchor)==1;new=new.replace(anchor,function+anchor)
    anchor="    cfg.rewards.h1_scut_fudan_leg_tuck.weight=RECIPE['leg_tuck_weight']";assert new.count(anchor)==1
    extra="\n    cfg.rewards.h1_scut_fudan_leg_tuck.func=airborne_tuck_rate\n    cfg.rewards.h1_scut_fudan_leg_tuck.params={}"
    new=new.replace(anchor,anchor+extra)
    restored=new.replace(function,'').replace(extra,'').replace("version='step270_forward_clearance_airborne_tuck_v3'","version='step270_forward_clearance_replay_v2'").replace('leg_tuck_weight=1.7','leg_tuck_weight=.5')
    assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(old))
    original.write_text(new,encoding='utf8');ast.parse(new)
    put('AIRBORNE_TUCK_REWARD_V3_CANDIDATE_AST_SCOPE_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,original_reward_SHA=H(refs/'h1_step270_path_reward_replay_v2_reference.py'),new_reward_SHA=H(original),only_new_tuck_function_config_func_params_weight_and_recipe_version=True,all_other_reward_AST_exact=True,tuck_weight_restored_original_SCUT_1_7=True,same_original_length_target_and_exp_formula=True,scope='attempt AND existing actual air_ticks>0 AND not landed AND not both wheels crossed; no dependence on expired command request',runtime_goal_physics_command_actorinputs_PPO_STD_Adam_save_account_bytes_unchanged=True,no_forces_or_action_script_or_air_reset=True,not_installed_or_GO=True))
    print(json.dumps(dict(candidate=True,new_reward_SHA=H(original),no_GO=True)))
except BaseException:
    put('BUILD_TUCK_CANDIDATE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
