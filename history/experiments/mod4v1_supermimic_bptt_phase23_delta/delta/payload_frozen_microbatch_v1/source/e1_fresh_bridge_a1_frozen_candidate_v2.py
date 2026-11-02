"""FutureADMITTED SDK bridge. No SDK/Torch import atmoduleimport/source-test time.
OwnoriginalN80factory retained; onlyA0 inferencevec avoids an implicitextrareset.
"""
from e1_identity_cache import PURPOSE
from a1_frozen_eval_runtime_v2 import install_paired_pose_before_original_reset,build_a1_original_vec
HOLDER={}


def attach_fresh_guard(env,identity,torch_module,tensor):
    install_paired_pose_before_original_reset(env)
    from mod4v1_fresh_dr_guard import FreshDRNominalGuard
    g=FreshDRNominalGuard(env,identity,torch_module=torch_module,tensor_converter=tensor)
    g.assert_new_nominals_unchanged();original=env.reset;count=[0]
    def once(*a,**k):
        assert count[0]==0,'No secondexplicitenv.reset inthisN80fresh purpose'
        value=original(*a,**k);count[0]+=1;g.assert_new_nominals_unchanged();return value
    env.reset=once;HOLDER.update(env=env,guard=g,explicit_reset_count=count,closed=False)
    return g


def fresh_full_dr_audit(env,guard,tensor):
    """CurrentalreadyusedAPI/component-memory auditing, notindependentbackendproof."""
    assert env.num_envs==80 and HOLDER['explicit_reset_count']==[1]
    assert env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
    assert env.cfg.sim.physics.solver_type==1
    assert env.cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and env.cfg.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4
    assert guard.restore_completed is False
    guard.assert_new_nominals_unchanged();api=guard.verify_live_parameters();assert api['actual_parameters_pass']
    assert env._mild_dr.profile=='white_v3' and len(env._mild_dr.factor)==80
    assert env._sensor_mild.profile=='noise_bias_mild_v1'
    assert env._feedback_delay_mild.enabled and env._physics_action_delay.queue.enabled
    assert env._spring_pressure.component.enabled and env._gas_damping.component.enabled
    assert env._chassis_com.component.enabled and env._explicit_pd.component.enabled
    q=env._physics_action_delay.queue;assert q.n==80 and q.control_us==20000 and q.physics_us==2500
    for name,width in [('legs',4),('wheels',2)]:
        s=q.groups[name];assert tuple(s['pending'].shape)==(80,width)
        assert tuple(s['lag_steps'].shape)==(80,) and bool(((s['lag_steps']>=0)&(s['lag_steps']<=2)).all())
    assert env.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
    assert env.spring_pressure_recipe()['actual_stiffness_bounds_N_m']==[1800,2200]
    sensor=env.sensor_sdk_audit();assert sensor['actor35'] and sensor['critic38_clean']
    pd=env.chassis_pd_audit();spring=env._spring_pressure.audit();gas=env._gas_damping.audit()
    return dict(purpose=PURPOSE,physical_scope='FreshN80ownsourceconstructor+originalONEreset, no20k DRrestore',actual_parameters=api,sensor_manager=sensor,chassis_PD=pd,spring=spring,gas=gas,action_recipe=env.action_delay_recipe(),feedback_recipe=env.feedback_delay_recipe(),spring_recipe=env.spring_pressure_recipe(),gas_recipe=env.gas_damping_recipe(),chassis_PD_recipe=env.chassis_pd_recipe(),original_seed=20260928,one_explicit_fresh_reset=1,fresh_N80_D0_D7_enabled=True,saved20k_history_physically_applied=False,backend_independent_qualification=False,D6_scope='Originalgasdamping_only_notalljointfriction',new_constructor_nominals_preserved=True)


def build_cached_frozen_policy(env,cache,torch_module,tensor):
    return build_a1_original_vec(env,cache,torch_module,tensor,HOLDER)
