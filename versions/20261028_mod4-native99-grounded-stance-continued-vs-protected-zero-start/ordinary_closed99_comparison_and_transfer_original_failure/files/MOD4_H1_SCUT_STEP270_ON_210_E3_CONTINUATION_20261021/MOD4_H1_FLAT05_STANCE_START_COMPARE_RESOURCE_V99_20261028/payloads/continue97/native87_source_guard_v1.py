"""Exact inventory/source/GO and actual precontrol gates; no I/O on import."""
from pathlib import Path,PurePosixPath
import ast,json,hashlib
from native87_protocol_v1 import SOURCE_SHA,SOURCE_ADAM,KIND,SEEDS,METHOD

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def require(v,message):
    if not v:raise ValueError(message)

def validate_task_go(task,go,manifest_SHA):
    require(task['key'] in SEEDS and task['native_seed']==SEEDS[task['key']],'typed slot seed')
    require(task['source_SHA']==task['bootstrap_source_SHA']==go['source_SHA']==go['bootstrap_SHA']==SOURCE_SHA,'latest qualified normal H1 bootstrap')
    require(task['source_Adamstep']==go['bootstrap_Adam']==SOURCE_ADAM and task['source_normal_PPO_update']==138,'qualified update138/Adam832460')
    require(task['bootstrap_source_kind']==go['bootstrap_source_kind']=='closed_production_policy_only','explicit policy-only bootstrap')
    require(task['fresh_environment_resume_scope']==go['fresh_environment_resume_scope']=='policy_only_no_source_environment_state','no source20k environment restore')
    require(go['native87_policy_only'] is True and go['new_native_architecture_fresh'] is True and go['native_continuation_restore_required'] is False,'fresh native architecture scope')
    require(go['source_qualification_kind']==KIND,'new CPU-only before GPU readback kind')
    require(go['manifest_SHA']==manifest_SHA and go['native87_contract_SHA']==task['native87_contract_SHA'],'manifest/contract binding')
    require(go['seed']==task['native_seed'] and go['num_envs']==4096 and task['method_config']==METHOD,'new method exact config')
    require(go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300 and go['nominal_end_epoch']-go['save_deadline']==300,'original finite deadlines')
    return True

def check_payload(B,*,verify_model_bytes=True):
    B=Path(B).resolve();manifest=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');task=read(B/'job0/TASK.json')
    contract_path=B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'
    require(H(contract_path)==task['native87_contract_SHA'],'source contract SHA')
    c=read(contract_path);require(c['schema']=='mod4.native87.policy_only_fresh4096.source_contract.v1','typed contract schema')
    require(c['source_SHA']==manifest['source_SHA']==task['source_SHA']==SOURCE_SHA,'source binding')
    require(c['source_Adamstep']==task['source_Adamstep']==832460,'source counter binding')
    require(c['method_config']==task['method_config']==METHOD,'method config')
    require(c['original_runtime_pins'],'original runtime pins required')
    for relative,digest in c['original_runtime_pins'].items():
        pure=PurePosixPath(relative);path=B/relative
        require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in relative and path.resolve().is_relative_to(B) and not path.is_symlink(),'unsafe original runtime pin')
        require(H(path)==digest,'original runtime changed '+relative)
    from native87_role_metadata_closure_v1 import validate_role_metadata_closure
    role_metadata=validate_role_metadata_closure(B,task,c,manifest)
    approved=c['approved_python'];seen=set();model_checks=[]
    for row in manifest['files']:
        relative=row['relative'];pure=PurePosixPath(relative)
        require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in relative and relative not in seen,'unsafe duplicate path')
        path=B/relative;require(path.resolve().is_relative_to(B) and not path.is_symlink() and path.is_file(),'contained regular file required')
        require(path.stat().st_size==row['bytes'],'file size '+relative)
        if path.suffix=='.py':
            require(approved.get(relative)==row['SHA'],'unapproved Python '+relative);ast.parse(path.read_text('utf8'))
        if verify_model_bytes or path.suffix.lower() not in ('.pt','.pth','.npz'):
            require(H(path)==row['SHA'],'file SHA '+relative)
        else:model_checks.append(relative)
        seen.add(relative)
    require({p.relative_to(B).as_posix() for p in B.rglob('*.py')}==set(approved),'Python inventory differs; no blanket exception')
    require(set(approved)<=seen,'approved Python missing')
    for relative,digest in c['candidate_pins'].items():require(relative in seen and H(B/relative)==digest,'candidate pin '+relative)
    require((B/'job0/source'/task['source_filename']).resolve().is_relative_to((B/'job0/source').resolve()),'source path containment')
    return dict(manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),contract=c,task=task,
        model_bytes_verified=verify_model_bytes,unverified_model_rows=model_checks,role_metadata_closure=role_metadata)

def finite_tree(x):
    import torch
    if torch.is_tensor(x):require(not x.is_floating_point() or bool(torch.isfinite(x).all()),'nonfinite checkpoint tensor')
    elif isinstance(x,dict):
        for v in x.values():finite_tree(v)
    elif isinstance(x,(list,tuple)):
        for v in x:finite_tree(v)

def validate_whole_policy(source):
    finite_tree(source)
    require(len(source['actor_state_dict'])==9 and len(source['critic_state_dict'])==8,'whole actor9/critic8 required')
    require(tuple(source['actor_state_dict']['distribution.std_param'].shape)==(6,),'STD6 required')
    opt=source['optimizer_state_dict'];require(len(opt['state'])==17,'17 original Adam states required')
    require({int(x['step']) for x in opt['state'].values()}=={832460},'all17Adam832460 required')
    require(source['H1_step270_task_state']['version']==270,'normal source phase270 required')
    require('UniSuperMimic_H1_test' not in source,'native86 is not a policy-only normal source')
    return True

def validate_precontrol_actual(runner,env,task,go,B):
    import torch
    from fresh_policy_only_bootstrap87_v1 import verify_loaded_policy_only_fresh_environment
    # The bootstrap helper already compared loaded PPO tensors to the qualified
    # source. Do not reread that model here. This gate is actual fresh plant only.
    require(env.num_envs==4096 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4,'actual4096 original clock')
    require(float(env.cfg.episode_length_s)==5. and env.cfg.seed==task['native_seed'],'actual5s seed')
    require(env._sim_step_counter==0 and not bool(env.h1_phase.age_control.any()),'before first physical control')
    require(float(runner.env.clip_actions)==6.,'actual RSL clip6')
    config=env.cfg.scene.robot.spawn.articulation_props
    require(config.solver_position_iteration_count==32 and config.solver_velocity_iteration_count==4,'actual original articulation32/4')
    require(env.cfg.sim.physics.solver_type==1,'actual TGS solver')
    contract=read(Path(B)/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json')
    require(list(env.scene['robot'].joint_names)==contract['expected_runtime_joint_names'],'actual runtime30joint order')
    require(len(env.scene['robot'].body_names)==31,'actual31 bodies')
    audit=env._mild_dr.audit() # original installed patched D0-D7 auditors, actual backend readback, no setters
    require(audit['actual_parameters_pass'] is True,'actual DR backend audit')
    states=dict(sensor=env._sensor_mild.state_dict(),queue=env._physics_action_delay.state_dict(),spring=env._spring_pressure.state_dict(),
        gas=env._gas_damping.state_dict(),COM=env._chassis_com.state_dict(),PD=env._explicit_pd.state_dict())
    require(all(s.get('n',s.get('num_envs'))==4096 for s in states.values()),'fresh actual DR populations4096')
    require(env._physics_action_delay.queue.control_us==10000,'queue original control clock')
    require(not torch.is_inference_mode_enabled(),'training entry cannot inherit global inference mode')
    return dict(passed=True,actual_environment_count=4096,actual_runtime30joint_order_passed=True,
        actual_fresh_D0_D7_backend_readback_passed=True,actual_solver_original32_4_passed=True,before_first_control_and_Pi=True,
        source20k_environment_state_not_restored=True,actual_DR_audit=audit)
