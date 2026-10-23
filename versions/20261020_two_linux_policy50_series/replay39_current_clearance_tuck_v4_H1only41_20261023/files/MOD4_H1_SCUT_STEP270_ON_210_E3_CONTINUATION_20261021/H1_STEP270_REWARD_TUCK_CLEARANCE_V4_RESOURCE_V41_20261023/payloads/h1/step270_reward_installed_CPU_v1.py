"""Only the new tuck scalar/configuration is exercised; previous unchanged
runtime400/strict events/forward-push contracts are reused, not re-executed.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,types,sys
import torch

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def check(B,sdk_reward_path):
    B=Path(B);sdk_reward_path=Path(sdk_reward_path);rng=torch.get_rng_state().clone()
    reward=module(B/'h1_step270_path_reward_v1.py','airborne_tuck_candidate_cpu')
    prior=json.loads((B/'reference_sources/PREVIOUS_INSTALLED_AIRBORNE_TUCK_V3_REWARD_CPU_ACTUAL.json').read_bytes());assert prior['passed']
    before=(B/'reference_sources/h1_step270_path_reward_airborne_tuck_v3_reference.py').read_text('utf8');after=(B/'h1_step270_path_reward_v1.py').read_text('utf8')
    def normalize(source,new):
        tree=ast.parse(source)
        tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='airborne_tuck_rate']
        if new:
            for node in ast.walk(tree):
                if isinstance(node,ast.Constant) and node.value=='step270_current_clearance_airborne_tuck_v4':node.value='step270_forward_clearance_airborne_tuck_v3'
        return ast.dump(tree)
    assert normalize(before,False)==normalize(after,True)
    source=B/'job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py'
    if not source.is_file():source=B/'reference_sources/h1_takeoff_progress_environment_v2.py'
    adapter=next(n for n in ast.parse(source.read_text('utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='tensor')
    stub=types.ModuleType('h1_takeoff_progress_environment_v2');stub.torch=torch
    exec(compile(ast.Module(body=[adapter],type_ignores=[]),str(source),'exec'),stub.__dict__)
    saved=sys.modules.get(stub.__name__);sys.modules[stub.__name__]=stub
    try:
        n=10;root=torch.zeros(n,13);root[:,6]=1.;positions=torch.zeros(n,2,3);positions[:,:,2]=-.22;positions[1,:,2]=-.447;positions[7,1,2]=-.447
        robot=types.SimpleNamespace(data=types.SimpleNamespace(root_state_w=root,body_pos_w=positions),body_names=['left_wheel','right_wheel'])
        phase=types.SimpleNamespace(attempt=torch.ones(n,dtype=torch.bool),air_ticks=torch.ones(n,dtype=torch.long),landed=torch.zeros(n,dtype=torch.bool),crossed=torch.zeros(n,2,dtype=torch.bool),request_for_action=torch.tensor([True,True,True,False,True,True,True,True,True,True]))
        phase.last_measured={'step_wheel_min':torch.zeros(n,2,3)};phase.last_measured['step_wheel_min'][:,:,2]=.02;phase.last_measured['step_wheel_min'][8,:,2]=.0003;phase.last_measured['step_wheel_min'][9,1,2]=.0003
        phase.air_ticks[0]=0;phase.crossed[4]=True;phase.landed[5]=True;phase.attempt[6]=False
        env=types.SimpleNamespace(scene={'robot':robot},h1_phase=phase,num_envs=n,device='cpu')
        oldroot=root.clone();oldpose=positions.clone();out=reward.airborne_tuck_rate(env)
        expected=torch.tensor([0.,__import__('math').exp(-8*.227),1.,1.,0.,0.,0.,__import__('math').exp(-4*.227),0.,0.])
        assert torch.allclose(out,expected,atol=1e-7,rtol=0)
        terms=types.SimpleNamespace()
        for name in ('h1_control_events','h1_scut_fudan_air_wheel_zero_torque','h1_scut_fudan_leg_tuck','h1_scut_fudan_wheel_below_base','h1_scut_fudan_push_vz'):setattr(terms,name,types.SimpleNamespace(weight=1.,func=lambda env:None,params={}))
        fake=types.ModuleType('isaaclab.managers');fake.RewardTermCfg=lambda **kw:types.SimpleNamespace(**kw);savedman=sys.modules.get('isaaclab.managers');sys.modules['isaaclab.managers']=fake
        try:reward.configure(types.SimpleNamespace(rewards=terms))
        finally:
            if savedman is None:sys.modules.pop('isaaclab.managers',None)
            else:sys.modules['isaaclab.managers']=savedman
        term=terms.h1_scut_fudan_leg_tuck;assert term.weight==1.7 and term.func is reward.airborne_tuck_rate and term.params=={}
        tree=ast.parse(sdk_reward_path.read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RewardManager');fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='compute');ns={'torch':torch};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(sdk_reward_path),'exec'),ns)
        manager=types.SimpleNamespace(_env=env,_term_names=['tuck'],_term_cfgs=[term],_reward_buf=torch.zeros(n),_step_reward=torch.zeros(n,1),_episode_sums={'tuck':torch.zeros(n)})
        actual=ns['compute'](manager,.01);assert torch.allclose(actual,expected*1.7*.01,atol=1e-7,rtol=0)
        assert torch.equal(root,oldroot) and torch.equal(positions,oldpose)
        count=20000;env.scene['robot'].data.root_state_w=torch.zeros(count,13);env.scene['robot'].data.body_pos_w=torch.zeros(count,2,3);env.scene['robot'].data.body_pos_w[:,:,2]=torch.linspace(-.45,-.20,count)[:,None]
        env.h1_phase=types.SimpleNamespace(attempt=torch.ones(count,dtype=torch.bool),air_ticks=torch.ones(count,dtype=torch.long),landed=torch.zeros(count,dtype=torch.bool),crossed=torch.zeros(count,2,dtype=torch.bool))
        env.h1_phase.last_measured={'step_wheel_min':torch.zeros(count,2,3)};env.h1_phase.last_measured['step_wheel_min'][:,:,2]=.02
        many=reward.airborne_tuck_rate(env);assert many.shape==(count,) and many.dtype==torch.float32 and torch.isfinite(many).all() and 0<=many.min()<=many.max()<=1
    finally:
        if saved is None:sys.modules.pop(stub.__name__,None)
        else:sys.modules[stub.__name__]=saved
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    return dict(passed=True,new_airborne_tuck_contract=True,new_current_clearance_tuck_contract=True,existing_runtime_wheel_bottom_clearance_m=.005,no_new_physics_health_or_skill_threshold=True,actual_SDK_reward_compute_SHA=hashlib.sha256(sdk_reward_path.read_bytes()).hexdigest(),actual_SDK_compute_control_rewards=actual.tolist(),cases=['ground_zero','extended_airborne','compact_airborne','compact_after_request','both_crossed_release','landed_release','no_attempt_zero','one_leg_extended','near_ground_after_flight_zero','one_wheel_near_ground_zero'],float32_vectorized_environments=20000,configured_original_weight_restored=1.7,original_target_length_and_exp_formula=True,all_other_reward_AST_exact=True,previous_runtime400_strict_events_and_forward_push_CPU_reused=prior,previous_cases_not_reexecuted=True,no_scene_GPU_actor_optimizer_RNG_command_or_goal_write=True,synthetic_not_skill_proof=True)
