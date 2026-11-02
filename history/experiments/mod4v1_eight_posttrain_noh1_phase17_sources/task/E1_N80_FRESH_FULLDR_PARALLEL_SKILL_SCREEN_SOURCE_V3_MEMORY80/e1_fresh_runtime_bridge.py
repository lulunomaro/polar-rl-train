"""FutureADMITTED SDK bridge. No SDK/Torch import atmoduleimport/source-test time.
OwnoriginalN80factory retained; onlyA0 inferencevec avoids an implicitextrareset.
"""
from e1_identity_cache import PURPOSE
HOLDER={}


def attach_fresh_guard(env,identity,torch_module,tensor):
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


class A0NoResetDecisionVec:
    """Onlydata bridge, neverconstructsSDKvec/runner orcallsreset.
    Sameoriginalmanualcommand->managerpolicy35->A0andclip_actions6 path;
    originalA0doesnotconsume history175 orcritic, no new history/RNG state.
    """
    def __init__(self,env,actor,digest,torch_module,TensorDict,tensor):
        self.env=self.unwrapped=env;self.actor=actor;self.checkpoint_sha256=digest
        self.num_envs=env.num_envs;self.device=env.device;self.t=torch_module;self.TD=TensorDict;self.tensor=tensor
        self.actor_calls=0;self.command_error=0.;self.env_reset_calls=0
    def get_observations(self):
        clean=self.env.observation_manager.compute()
        assert tuple(clean['policy'].shape)==(80,35) and tuple(clean['critic'].shape)==(80,38)
        self.command_error=max(self.command_error,float((clean['policy'][:,:3]-self.env.command_manager.get_term('twist').command).abs().max()))
        assert self.command_error<=1e-6
        return self.TD(dict(policy=clean['policy']),batch_size=[80])
    def policy(self,obs):
        self.actor_calls+=1
        with self.t.inference_mode():return self.actor(obs,stochastic_output=False)
    def step(self,action):
        obs,reward,terminated,truncated,extra=self.env.step(self.t.clamp(action,-6.,6.))
        return obs,reward,terminated|truncated,extra
    def audit(self):
        return dict(variant='A0',actual_command_error=self.command_error,actor_calls=self.actor_calls,current_actor_dimension=35,actor_receives_critic=False,actor_receives_history=False,optimizer_updates=0,extra_explicit_env_resets=self.env_reset_calls,clip_actions=6.,scope=PURPOSE)


def build_cached_frozen_policy(env,cache,torch_module,tensor):
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    # ExactA0 constructorarguments fromoriginalfrozen_history_policy.load_frozen_actor.
    obs=TensorDict(dict(policy=torch_module.zeros(80,35),critic=torch_module.zeros(80,38),feedback_history=torch_module.zeros(80,175)),batch_size=[80])
    with torch_module.random.fork_rng(devices=[]):
        cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar')
        actor=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=cfg)
        actor.load_state_dict(cache.core('actor_state_dict'),strict=True)
    actor.to(env.device).eval();actor.requires_grad_(False)
    expected=cache.core('actor_state_dict')
    assert set(actor.state_dict())==set(expected)
    for k,v in actor.state_dict().items():assert torch_module.equal(v.detach().cpu(),expected[k]),k
    cache.assert_entire_root_unchanged();cache.live_actor_STD_loaded=True;vec=A0NoResetDecisionVec(env,actor,cache.SHA,torch_module,TensorDict,tensor)
    HOLDER.update(actor=actor,vec=vec,cache=cache)
    return vec,vec.policy,vec
