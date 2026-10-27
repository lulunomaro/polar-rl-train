"""Fresh target CPU validators. No model load, learner, replay or forward here."""
from pathlib import Path
import ast, sys, math
from dataclasses import dataclass, asdict
from native88_source_guard_v1 import require,H,read,contained,finite_tree,R5_NATIVE_CONTRACT,exact_plain

def exact(a,b):
    import torch
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b

def extract(path,names,namespace=None):
    t=ast.parse(Path(path).read_bytes());nodes=[];found=set()
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names:nodes.append(n);found.add(n.name)
        elif isinstance(n,ast.Assign):
            ids={x.id for x in n.targets if isinstance(x,ast.Name)}
            if ids&set(names):nodes.append(n);found|=ids
    require(set(names)<=found,'pure AST definitions missing '+str(path))
    ns=dict(namespace or {});exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns

def frozen_bootstrap(full,witness):
    from native88_source_guard_v1 import validate_whole_policy
    validate_whole_policy(full);validate_whole_policy(witness)
    require('UniSuperMimic_H1_test' not in witness,'normal86 witness cannot be native')
    for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
        require(exact(full[name],witness[name]),'frozen RSL witness differs '+name)
    return dict(passed=True,actor9_critic8_STD6_17Adam832460_literal_exact=True,normal86_environment_state_not_restored=True)

def validate_native_optimizer(module,state,betas):
    import torch
    optimizer=torch.optim.Adam(module.parameters(),lr=2e-4,betas=betas);optimizer.load_state_dict(state)
    parameters=list(module.parameters());require(len(optimizer.state)==len(parameters)>0,'native optimizer incomplete')
    require(all(tuple(g['betas'])==betas for g in optimizer.param_groups),'native optimizer betas changed')
    steps=[]
    for p in parameters:
        value=optimizer.state[p];require({'step','exp_avg','exp_avg_sq'}<=set(value),'native Adam moments missing')
        require(value['exp_avg'].shape==value['exp_avg_sq'].shape==p.shape and value['exp_avg'].dtype==value['exp_avg_sq'].dtype==p.dtype,'native moment shape/dtype')
        require(int(value['step'])>0,'native optimizer positive completed step');steps.append(int(value['step']))
    return dict(passed=True,state_count=len(steps),min_step=min(steps),max_step=max(steps),betas=list(betas))

def strict_native_restore(full,B,c,task):
    import torch
    from native88_protocol_v1 import SOURCES
    B=Path(B);finite_tree(full)
    require(exact_plain(full['UniSuperMimic_test_contract'],task['source_native_contract']) and exact_plain(task['source_native_contract'],R5_NATIVE_CONTRACT),'old source contract literal exact')
    required=('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_DR_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','sensor_global_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state','H1_step270_task_state','H1_step270_runtime_contract')
    require(all(k in full for k in required),'full original save groups missing')
    native=full['UniSuperMimic_H1_test'];source=SOURCES[task['key']]
    require(type(native['iteration']) is int and native['iteration']==source['updates'] and native['sim_steps']>0,'native iteration/sim counters')
    publication=full['UniSuperMimic_publication']
    require(publication['native_iteration']==source['updates'] and publication['world_updates']==source['world_updates'] and publication['policy_updates']==source['policy_updates'],'native published counters')
    history=full['UniSuperMimic_obs_history'];ep=full['UniSuperMimic_bridge_ep_step']
    require(tuple(history.shape)==(4096,10,86) and tuple(ep.shape)==(4096,),'source history/episode shape only; never restored')
    cls=extract(B/'source/supermimic_wheel_leg_v3/learner.py',('SuperMimicConfig',),dict(dataclass=dataclass))['SuperMimicConfig']
    config=extract(contained(B,c.get('native_config_relative','source/native_own_fudan88_gas400_training_v2.py')),('config_for',),dict(SuperMimicConfig=cls))['config_for'](task['native_seed'])
    args=asdict(config);require(exact(native['args'],args),'native full source config differs from actual pinned config_for')
    from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
    from supermimic_wheel_leg_v3.networks import Policy,Critic
    wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
    pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden'])
    critic=Critic(73+54+31+7+1460,hidden=args['critic_hidden'])
    require(wm.in_dim==167 and wm.out_dim==126,'WM167/126 dimensions')
    results={};stepkeys={'opt_wm':'world_updates','opt_pi':'policy_updates'}
    for name,opt,module,betas in (('wm','opt_wm',wm,(.9,.999)),('pi','opt_pi',pi,(.9,.95)),('critic','opt_v',critic,(.9,.999))):
        module.load_state_dict(native[name],strict=True)
        require(exact(module.state_dict(),native[name]),'strict loaded state including norms differs '+name)
        norms={k:tuple(v.shape) for k,v in module.state_dict().items() if any(x in k for x in ('norm.mean','norm.var','norm.count'))}
        require(norms,'saved normalizer buffers missing '+name)
        summary=validate_native_optimizer(module,native[opt],betas)
        if opt in stepkeys:require(summary['min_step']==summary['max_step']==source[stepkeys[opt]],'native optimizer/source global counter')
        results[name]=dict(strict_state_and_all_norms_literal_exact=True,normalizer_buffers=norms,optimizer=summary)
    return dict(passed=True,models=results,iteration=native['iteration'],sim_steps=native['sim_steps'],full_configuration_exact=True,
        no_replay_or_learner_constructed=True,no_actor_WM_or_critic_forward=True,no_native_PPO20Adam_rule=True,
        old_environment_replay_history_and_RNG_not_restored=True)

def rsl_roundtrip(B,witness):
    import torch
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    from rsl_rl.algorithms import PPO
    from types import SimpleNamespace
    obs=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38)),batch_size=[1]);groups=dict(actor=['policy'],critic=['critic'])
    cfg=read(Path(B)/'job0/original_run_manifest.json')['env'];hidden=[int(x) for x in cfg['RM_HIDDEN_DIMS'].split(',')]
    actor=MLPModel(obs,groups,'actor',6,hidden_dims=hidden,activation='elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=float(cfg['RM_INIT_STD']),std_type='scalar'))
    critic=MLPModel(obs,groups,'critic',1,hidden_dims=hidden,activation='elu');optimizer=torch.optim.Adam(list(actor.parameters())+list(critic.parameters()),lr=.0001)
    holder=SimpleNamespace(actor=actor,critic=critic,optimizer=optimizer,rnd=None)
    require(PPO.load(holder,witness,None,True) is True,'installed RSL strict roundtrip')
    for name,obj in [('actor_state_dict',actor),('critic_state_dict',critic),('optimizer_state_dict',optimizer)]:require(exact(obj.state_dict(),witness[name]),'installed RSL state exact '+name)
    return dict(passed=True,installed_RSL_PPO_load=True,all_state_literal_exact=True,no_actor_forward=True)

def asset_composition_readback(B,c,asset_report):
    from pxr import Usd,UsdPhysics
    path=contained(B,c.get('asset_stage_relative','job0/assets/robot.usd'))
    stage=Usd.Stage.Open(str(path),Usd.Stage.LoadAll);require(stage is not None,'new private composed USD failed')
    rows=[]
    for expected in asset_report['actual_gas_authored_values']:
        prim=stage.GetPrimAtPath('/Robot/joints/'+expected['name']);require(prim and prim.IsA(UsdPhysics.PrismaticJoint),'gas prismatic prim')
        value=dict(name=expected['name'],nominal_k_N_m=prim.GetAttribute('drive:linear:physics:stiffness').Get(),hard_q_lower_m=prim.GetAttribute('physics:lowerLimit').Get(),hard_q_upper_m=prim.GetAttribute('physics:upperLimit').Get())
        require(all(value[k]==expected[k] for k in ('nominal_k_N_m','hard_q_lower_m','hard_q_upper_m')),'fresh USD authored readback differs')
        require(value['nominal_k_N_m']==2000.,'old3500 plant refused');rows.append(value)
    require(len(rows)==2 and {r['name'] for r in rows}=={'left_gas_slide','right_gas_slide'},'both own gas readbacks')
    return dict(passed=True,actual_installed_private_USD_CPU_parsed=True,gas=rows,only_four_changes_proved_by_pinned_original_comparison=True,
        actual_PhysX_runtime_readback_passed=False,hardware_force_curve_measured=False)

def objective_source_CPU_check(B,c,task):
    """New installation-purpose math checks; no recorded motion/raw/model load."""
    import torch,hashlib,json
    from own_step_differentiable_objective_v2 import build_own_step_mdp
    from supermimic_wheel_leg_v3.geometry import unflatten_state
    B=Path(B);geometry=contained(B,c.get('own_step_geometry_relative','source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'))
    require(geometry.stat().st_size==34263 and H(geometry)=='461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d','own wheel geometry source pin')
    mdp=build_own_step_mdp(read(B/'job0/assets/import_contract.json'),read(geometry),read(contained(B,c['reference_relative'])),c['expected_runtime_joint_names'],c['actual_encoder_joint_names'],device='cpu',order_scope='source_CPU_fixture')
    frames=torch.tensor([120,145,200]);ref,_=mdp.provider.query(frames);aux=torch.zeros(3,54);aux[:,:6]=torch.tensor([0.,0.,1.,0.,0.,1.])
    state=unflatten_state(torch.cat((ref,aux),-1));action=torch.zeros(3,6);context=torch.zeros(3,31)
    result=mdp.objective_terms(state,frames,action,action)
    require(torch.isfinite(result['total']).all() and (result['total']>0).all() and (result['total']<=.06).all(),'selected bounded-positive objective')
    require(mdp.obs(state,action,context,frames).shape==(3,86) and mdp.goal(frames,10).shape==(3,1460),'unchanged obs86/future1460')
    # At post-contact age200 a root-only elevated, short-of-edge pose cannot
    # receive the own geometric goal score. A differentiable input X error
    # must produce a finite correcting gradient without actor/WM invocation.
    goal=tuple(x[2:3].clone() for x in state);failed=list(goal);failed[0]=failed[0].clone();failed[0][:,0]-=.15;failed[0].requires_grad_()
    good=mdp.reward(goal,frames[2:3],action[2:3],action[2:3]);bad=mdp.reward(tuple(failed),frames[2:3],action[2:3],action[2:3])
    require((good>bad).all(),'task geometric target dominates short-of-edge counterexample')
    grad=torch.autograd.grad(bad.sum(),failed[0])[0];require(torch.isfinite(grad).all() and (grad[:,0]>0).all(),'finite forward correcting source gradient')
    actual_manifest=mdp.contract_manifest();require(actual_manifest['reference_order_scope']=='source_CPU_fixture','CPU order scope honest')
    expected=dict(c['objective_runtime_contract']);source_expected=dict(expected);source_expected['reference_order_scope']='source_CPU_fixture'
    require(exact_plain(actual_manifest,source_expected),'source recomputed objective contract differs from predeclared runtime contract except scope')
    require(hashlib.sha256(json.dumps(expected,indent=2).encode()).hexdigest()==task['objective_contract_SHA'],'effective runtime objective contract pin')
    return dict(passed=True,new_installation_purpose_synthetic_math_checks=True,scope='SOURCE_CPU_no_scene_no_recorded_motion_no_models',
        goal_score=good.detach().tolist(),short_edge_score=bad.detach().tolist(),forward_gradient=grad[:,0].tolist(),
        source_contract=actual_manifest,runtime_contract_expected=expected,actual_runtime_contract_still_requires_actual_order=True,
        actual_contact_or_training_gain_proved=False)
