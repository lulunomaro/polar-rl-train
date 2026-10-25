"""V6A reward-only check, including actual installed SDK compute when supplied.

Does not import Isaac, construct an environment, load a model, initialize CUDA,
touch RNG/optimizer, change commands, or start a worker. Root may install this
beside the candidate reward only after its ordinary source review.
"""
from pathlib import Path
import ast, hashlib, importlib.util, sys, types
import torch

V5_SHA='42909a5e40334e21a6bc7df83950756207f8366fce975662ab08ced1dea41193'
ACTUAL_INSTALLED_REWARD_MANAGER_SHA='6be44a98df5aed8a0ebac2913ebea33010633e007e816697a6d99f7ccfd731db'
LOCAL_FIXTURE_REWARD_MANAGER_SHA='2ff82f8e385593e4c2206446ab4ef8de7c72dc0ef444f3e02f60df321d71919e'

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

V8_DEFINITIONS="def policy_sampled_leg_excess_cost(raw):\n    # Original policy action units. Never edit the sampled or executed action.\n    if raw.ndim!=2 or raw.shape[1]!=6 or not torch.isfinite(raw).all():\n        raise RuntimeError('Expected finite original six-action policy sample')\n    return (raw[:,:4].abs()-6.).clamp_min(0.).square().mean(-1)\n\ndef sampled_leg_action_excess_rate(env):\n    # Initial source/SDK probes are outside an actor control step.\n    if not getattr(env,'h1_stepping',False):\n        return torch.zeros(env.num_envs,device=env.device)\n    raw=getattr(env,'_h1_sampled_actions_for_reward',None)\n    if raw is None or raw.shape[0]!=env.num_envs:\n        raise RuntimeError('Missing current policy sample during H1 control reward')\n    return policy_sampled_leg_excess_cost(raw)\n"
V8_CONFIG="cfg.rewards.h1_step270_sampled_leg_action_excess=RewardTermCfg(func=sampled_leg_action_excess_rate,weight=RECIPE['sampled_leg_action_excess_weight'],params={})"

def normalize_V8_reward_AST(tree):
    recipe=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
    entries={k.arg:k for k in recipe.keywords}
    assert ast.literal_eval(entries['version'].value)=='step270_sampled_leg_excess_v8_reward_only'
    entries['version'].value=ast.Constant('step270_near_edge_takeoff_gate_v7_reward_only')
    assert ast.literal_eval(entries['sampled_leg_action_excess_weight'].value)==-.001
    recipe.keywords.remove(entries['sampled_leg_action_excess_weight'])
    expected={n.name:n for n in ast.parse(V8_DEFINITIONS).body if isinstance(n,ast.FunctionDef)}
    actual={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for name,node in expected.items():assert name in actual and ast.dump(actual[name])==ast.dump(node)
    tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name not in expected]
    configure=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='configure')
    expected_stmt=ast.parse(V8_CONFIG).body[0]
    matches=[n for n in configure.body if ast.dump(n)==ast.dump(expected_stmt)]
    assert len(matches)==1;configure.body.remove(matches[0])
    return tree

def allowlist(candidate,reference):
    """Only one existing function plus one pure helper and recipe version."""
    a=ast.parse(Path(reference).read_text('utf8'));b=ast.parse(Path(candidate).read_text('utf8'))
    b=normalize_V8_reward_AST(b)
    recipe=next(n for n in b.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in n.targets)).value
    entries={k.arg:k for k in recipe.keywords}
    expected={'version':('step270_near_edge_takeoff_gate_v7_reward_only','step270_sagittal_tuck_geometry_v6a_unused'),'takeoff_gate_start_front_x_m':(.10,-.05),'takeoff_gate_full_front_x_m':(.25,.15)}
    for key,(actual,prior) in expected.items():
        assert ast.literal_eval(entries[key].value)==actual
        entries[key].value=ast.parse(repr(prior),mode='eval').body
    old={n.name:n for n in a.body if isinstance(n,ast.FunctionDef)}
    current={n.name:n for n in b.body if isinstance(n,ast.FunctionDef)}
    assert set(current)==set(old)|{'sagittal_leg_lengths'}
    changed=[n for n in sorted(old) if ast.dump(old[n])!=ast.dump(current[n])]
    assert changed==['airborne_tuck_rate']
    b.body=[old[n.name] if isinstance(n,ast.FunctionDef) and n.name=='airborne_tuck_rate' else n for n in b.body if not isinstance(n,ast.FunctionDef) or n.name!='sagittal_leg_lengths']
    for n in ast.walk(b):
        if isinstance(n,ast.Constant) and n.value=='step270_sagittal_tuck_geometry_v6a_unused':n.value='step270_airborne_feasible_target_v5'
    assert ast.dump(a)==ast.dump(b),'Outside V6A single-metric AST allowlist'
    return dict(passed=True,changed_existing_functions=changed,new_functions=['sagittal_leg_lengths'],all_other_reward_function_config_weight_and_gate_AST_exact=True)

def check(B,sdk_reward_path=None,allow_local_fixture=False,reference_path=None):
    B=Path(B);rng=torch.get_rng_state().clone()
    reward_path=B/'h1_step270_path_reward_v1.py';reward=load(reward_path,'post67_v6a_reward_check')
    assert reward.RECIPE['version']=='step270_sampled_leg_excess_v8_reward_only' and reward.RECIPE['sampled_leg_action_excess_weight']==-.001
    assert reward.RECIPE['leg_tuck_weight']==1.7 and reward.RECIPE['airborne_leg_target_overdrive_weight']==-.05
    assert reward.RECIPE['takeoff_gate_start_front_x_m']==.10 and reward.RECIPE['takeoff_gate_full_front_x_m']==.25
    ast_check=None
    if reference_path is not None:
        assert hashlib.sha256(Path(reference_path).read_bytes()).hexdigest()==V5_SHA
        ast_check=allowlist(reward_path,reference_path)
    n=20000;dtype=torch.float32
    axis=torch.linspace(-1.,1.,n,dtype=dtype)
    roll=axis*.4;pitch=axis.flip(0)*.35;yaw=axis*3.0
    cr,sr=torch.cos(roll/2),torch.sin(roll/2);cp,sp=torch.cos(pitch/2),torch.sin(pitch/2);cy,sy=torch.cos(yaw/2),torch.sin(yaw/2)
    q=torch.stack((sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy,cr*cp*cy+sr*sp*sy),dim=-1)
    length=.22+.1*axis
    local=torch.stack((torch.zeros(n,2),torch.tensor([.2188,-.2188])[None,:].expand(n,2),-length[:,None].expand(n,2)),dim=-1)
    qv=q[:,None,:3].expand_as(local);qw=q[:,None,3:4]
    t=2*torch.cross(qv,local,dim=-1);world=local+qw*t+torch.cross(qv,t,dim=-1)
    snapshot=(q.clone(),world.clone())
    measured=reward.sagittal_leg_lengths(delta_world=world,root_quaternion_xyzw=q)
    error=float((measured-length[:,None]).abs().max())
    assert measured.shape==(n,2) and measured.dtype==dtype and error<2e-6
    assert torch.equal(q,snapshot[0]) and torch.equal(world,snapshot[1])
    # Same physical leg extension under arbitrary rigid orientation must have
    # the same compactness. The fixed lateral mounting width contributes zero.
    target=torch.tensor([[[.0,.2188,-.22],[.0,-.2188,-.22]]],dtype=dtype)
    identity=torch.tensor([[0.,0.,0.,1.]],dtype=dtype)
    exact=reward.sagittal_leg_lengths(delta_world=target,root_quaternion_xyzw=identity)
    assert torch.allclose(exact,torch.full_like(exact,.22),atol=1e-7,rtol=0)
    compact=torch.exp(-4*torch.abs(measured-.22).sum(-1))
    assert torch.isfinite(compact).all() and (compact>=0).all() and (compact<=1).all()

    # Exercise the actual wrapper's original phase masks, retaining retraction
    # shaping after request expiry and until both wheels have really crossed.
    m=10;root=torch.zeros(m,13);root[:,6]=1.
    body=torch.zeros(m,3,3);body[:,1:]=target.expand(m,2,3)
    p=types.SimpleNamespace(attempt=torch.ones(m,dtype=torch.bool),air_ticks=torch.ones(m,dtype=torch.long),landed=torch.zeros(m,dtype=torch.bool),crossed=torch.zeros(m,2,dtype=torch.bool),request_for_action=torch.ones(m,dtype=torch.bool),last_measured={'step_wheel_min':torch.zeros(m,2,3)})
    p.last_measured['step_wheel_min'][:,:,2]=.02
    p.air_ticks[0]=0;p.attempt[1]=False;p.landed[2]=True;p.crossed[3]=True;p.last_measured['step_wheel_min'][4,0,2]=0.
    p.request_for_action[5]=False;p.crossed[6,0]=True;p.last_measured['step_wheel_min'][7,:,2]=.0001
    robot=types.SimpleNamespace(body_names=['chassis','left_wheel','right_wheel'],data=types.SimpleNamespace(root_state_w=root,body_pos_w=body))
    env=types.SimpleNamespace(h1_phase=p,scene={'robot':robot},num_envs=m)
    helper=types.ModuleType('h1_takeoff_progress_environment_v2');helper.tensor=lambda v:v.torch if hasattr(v,'torch') else v
    manager=types.ModuleType('isaaclab.managers');manager.RewardTermCfg=lambda **kw:types.SimpleNamespace(**kw)
    stubs={v.__name__:v for v in (helper,manager)};old_modules={name:sys.modules.get(name) for name in stubs}
    sys.modules.update(stubs)
    try:
        expected=torch.tensor([0.,0.,0.,0.,0.,1.,1.,0.,1.,1.])
        saved={name:v.clone() for name,v in vars(p).items() if torch.is_tensor(v)}
        actual=reward.airborne_tuck_rate(env)
        assert torch.allclose(actual,expected,atol=2e-6,rtol=0)
        assert all(torch.equal(getattr(p,name),v) for name,v in saved.items())
        original_release_func=lambda env:torch.zeros(env.num_envs)
        release=types.SimpleNamespace(weight=-2.,func=original_release_func,params={'name':'release_shortfall'})
        cfg=types.SimpleNamespace(rewards=types.SimpleNamespace(h1_step270_release_shortfall=release))
        for name in ('h1_control_events','h1_scut_fudan_air_wheel_zero_torque','h1_scut_fudan_leg_tuck','h1_scut_fudan_wheel_below_base','h1_scut_fudan_push_vz'):
            setattr(cfg.rewards,name,types.SimpleNamespace(weight=1.,func=lambda env:None,params={}))
        reward.configure(cfg)
        assert release.func is original_release_func and release.weight==-2. and release.params=={'name':'release_shortfall'}
        assert cfg.rewards.h1_scut_fudan_leg_tuck.func is reward.airborne_tuck_rate
        assert cfg.rewards.h1_scut_fudan_leg_tuck.weight==1.7
        assert cfg.rewards.h1_step270_airborne_leg_target_overdrive.weight==-.05
        sdk_sha=None;out=None
        if sdk_reward_path is not None:
            sdk_reward_path=Path(sdk_reward_path);sdk_sha=hashlib.sha256(sdk_reward_path.read_bytes()).hexdigest()
            if allow_local_fixture:assert sdk_sha==LOCAL_FIXTURE_REWARD_MANAGER_SHA
            else:assert sdk_sha==ACTUAL_INSTALLED_REWARD_MANAGER_SHA,'Actual installed SDK SHA changed: root must review real source; no silent fallback'
            tree=ast.parse(sdk_reward_path.read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RewardManager')
            compute=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='compute');ns={'torch':torch}
            exec(compile(ast.Module(body=[compute],type_ignores=[]),str(sdk_reward_path),'exec'),ns)
            term=cfg.rewards.h1_scut_fudan_leg_tuck
            rm=types.SimpleNamespace(_env=env,_term_names=['sagittal_tuck'],_term_cfgs=[term],_reward_buf=torch.zeros(m),_step_reward=torch.zeros(m,1),_episode_sums={'sagittal_tuck':torch.zeros(m)})
            out=ns['compute'](rm,.01)
            assert torch.allclose(out,expected*1.7*.01,atol=1e-7,rtol=0)
            assert torch.allclose(rm._step_reward[:,0],expected*1.7,atol=1e-6,rtol=0)
    finally:
        for name,old in old_modules.items():
            if old is None:sys.modules.pop(name,None)
            else:sys.modules[name]=old
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    return dict(passed=True,retained_V6A_sagittal_metric_and_explicit_V7_gate_with_V8_excess_only=True,AST_allowlist=ast_check,
        vectorized_float32_environments=n,orientation_invariance_max_abs_length_error_m=error,
        sagittal_target_m=.22,leg_tuck_weight=1.7,original_release_shortfall_weight=-2.,
        original_release_shortfall_func_params_and_success_event_timing_unchanged=True,explicit_takeoff_reward_gate_retained=True,explicit_sampled_leg_excess_V8_reward_only=True,
        phase_mask_cases=['ground_zero','no_attempt_zero','landed_zero','both_crossed_zero','one_wheel_ground_zero','request_expired_still_active','one_crossed_still_active','near_ground_zero','airborne_active','airborne_active'],
        actual_installed_SDK_reward_compute_tested=sdk_reward_path is not None and not allow_local_fixture,
        local_saved_SDK_fixture_compute_tested=sdk_reward_path is not None and allow_local_fixture,
        SDK_compute_source_SHA=sdk_sha,SDK_control_rewards=out.tolist() if out is not None else None,
        actual_installed_SDK_compute_remains_pending=sdk_reward_path is None or allow_local_fixture,
        prior_V5_target_overdrive_formula_guarded_by_AST=True,
        no_actor_inputs_actor_critic_optimizer_RNG_GPU_command_goal_action_or_physics_write=True,
        not_PhysX_native_query_or_learning_outcome=True)
