"""New small CPU API fixture. Never an actual4096 scene or production actor."""
def check(B,contract,task):
    import json,torch
    from pathlib import Path
    from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
    from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
    from supermimic_wheel_leg_v3.networks import Policy,Critic
    from native_own_fudan87_training import config_for
    from native87_protocol_v1 import METHOD
    document=json.loads((Path(B)/task['native_reference_relative']).read_bytes())
    provider=ConvertedMOD4Reference(document,'cpu').bind_named_order(contract['expected_runtime_joint_names'],scope='source_CPU_fixture')
    mdp=ConvertedMOD4JumpMdp(provider,contract['expected_leg_joint_names'])
    cfg=config_for(task['native_seed'])
    for name in ('buffer_steps','utd','horizon','goal_frames','hist','wm_batch','pi_batch','wm_only_iters','amp','compile'):
        assert getattr(cfg,name)==METHOD[name],name
    assert list(cfg.wm_hidden)==METHOD['wm_hidden'] and list(cfg.policy_hidden)==METHOD['policy_hidden']
    torch.manual_seed(87001);n=2;frames=torch.tensor([100,145]);z=lambda width:torch.zeros(n,width)
    state=(z(3),torch.eye(3)[None].expand(n,-1,-1).clone(),z(3),z(3),z(30),z(30),z(54))
    xi=torch.zeros(n,31);previous=z(6);obs=mdp.obs(state,previous,xi,frames);goal=mdp.goal(frames,10)
    assert obs.shape==(n,86) and goal.shape==(n,1460)
    wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=(8,8),num_joints=30,auxiliary_dim=54,action_dim=6)
    assert wm.in_dim==167 and wm.layout.pack(state).shape==(n,127)
    predicted=wm.step(state,z(6),mdp.normalize_context(xi));assert len(predicted)==7 and predicted[6].shape==(n,54)
    pi=Policy(86,1460,hist=10,z_dim=4,num_joints=6,hidden=(8,8))
    action=pi(obs[:,None,:].expand(-1,10,-1),goal);assert action.shape==(n,6)
    critic_input=torch.cat((mdp.critic_features(state,frames,mdp.normalize_context(xi)),goal),-1)
    critic=Critic(critic_input.shape[-1],hidden=(8,8));value=critic(critic_input)
    assert value.shape==(n,) and torch.isfinite(action).all() and torch.isfinite(value).all()
    assert torch.isfinite(mdp.reward(state,frames,action,previous)).all()
    return dict(passed=True,fixture_only=True,fixture_batch=2,fixture_hidden=[8,8],
        source_named_order_scope='source_CPU_fixture',actual_GPU_runtime_readback_passed=False,
        dimensions=dict(packed127=127,aux54=54,static31=31,obs86=86,goal_future10=1460,WMinput=167),
        original_method_config_source_checked=True,no_actual4096_environment_or_production_policy_forward=True)
