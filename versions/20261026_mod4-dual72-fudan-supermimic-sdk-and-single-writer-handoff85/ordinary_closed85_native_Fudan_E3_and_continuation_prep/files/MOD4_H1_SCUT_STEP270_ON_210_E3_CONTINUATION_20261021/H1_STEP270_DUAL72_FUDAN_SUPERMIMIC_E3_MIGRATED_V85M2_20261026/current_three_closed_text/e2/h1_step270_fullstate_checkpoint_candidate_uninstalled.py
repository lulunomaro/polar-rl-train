"""Explicit H1 old-task to step270 state migration, not a production admission."""
from pathlib import Path
import hashlib,json,time
import torch

SOURCE_SHA='cb118b2ac27cca44466fba9014f4583ee8db23fc2cb2d83c4034b15961178765'
COMMAND_FIELDS=('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','vel_command_b')
RETAINED_GROUPS=('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_DR_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','sensor_global_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state')

def exact(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return type(a)==type(b) and a==b

def validate_source(ck,n):
    assert n==20000 and all(k in ck for k in RETAINED_GROUPS)
    assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8
    assert ck['actor_state_dict']['distribution.std_param'].shape==(6,)
    assert len(ck['optimizer_state_dict']['state'])==17
    assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={674740}
    for name in ('sensor_DR_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state'):assert ck[name]['n']==n
    for name in ('COM','PD'):assert ck['chassis_PD_state'][name]['num_envs']==n
    def finite(v):
        if torch.is_tensor(v):assert torch.isfinite(v).all()
        elif isinstance(v,dict):
            for x in v.values():finite(x)
        elif isinstance(v,(list,tuple)):
            for x in v:finite(x)
    finite(ck)

def validate_new_phase(p,n):
    assert p['version']==270 and p['num_envs']==n and p['geometry']==dict(height=.270,edge_x=.35,depth=.8,width=1.2)
    assert set(p)=={'version','num_envs','geometry','tensors','goal'}
    assert p['tensors']['previous_front'].shape==(n,2) and p['tensors']['previous_front'].dtype==torch.float32
    for group in ('tensors','goal'):
        for value in p[group].values():assert torch.is_tensor(value) and value.shape[0]==n and torch.isfinite(value).all()

def migrate_reference(ck,new_phase,n):
    """CPU reference only. Keep all old fields and provenance alongside new task state."""
    validate_source(ck,n);validate_new_phase(new_phase,n)
    assert 'H1_step270_task_state' not in ck and ck['H1_public_request_phase_state']['version']==1
    old=ck['H1_public_request_phase_state'];assert set(old['external_command'])==set(COMMAND_FIELDS)
    assert old['private_command_mode_rng'].dtype==torch.uint8 and old['private_command_mode_rng'].numel()>0
    out=dict(ck)
    out['H1_step270_task_state']=dict(version=270,phase=new_phase,external_command=old['external_command'],private_command_mode_rng=old['private_command_mode_rng'])
    out['H1_step270_explicit_migration']=dict(source_SHA=SOURCE_SHA,source_Adam=674740,source_old_phase_retained_as_historical_provenance=True,new_phase_zero_credit_and_fresh_schedule=True,old_public_phase_not_interpreted_as_step270=True,terrain='true_270mm_vertical_step',reward='SCUT_ballistic_release_and_actual_step_events',command='original0/4_schedule_with_authorized_public4_forward0.8m_s',policy_hz=100,physics_dt=.0025,actor35_critic38_actions6_unchanged=True,all_six_STD_and17Adam_inherited=True,source_D0_D7_and_command_private_rng_literal_exact=True,no_PhysX_exact_resume_claim=True,CPU_reference_not_production_source=True)
    assert all(exact(out[k],ck[k]) for k in ck)
    return out

def state(env):
    term=env.command_manager.get_term('twist')
    return dict(version=270,phase=env.h1_phase.state_dict(),external_command={k:getattr(term,k).clone() for k in COMMAND_FIELDS},private_command_mode_rng=term._mode_rng.get_state().clone())

def load(env,s):
    assert s['version']==270;validate_new_phase(s['phase'],env.num_envs)
    env.h1_phase.load_state_dict(s['phase']);term=env.command_manager.get_term('twist')
    assert set(s['external_command'])==set(COMMAND_FIELDS)
    for k,v in s['external_command'].items():
        a=getattr(term,k);assert a.shape==v.shape and a.dtype==v.dtype;a.copy_(v.to(a.device))
    term._mode_rng.set_state(s['private_command_mode_rng'].cpu())
    assert exact(state(env),s)

def resume_step270_new_episode(runner,env,path,log_dir):
    log_dir=Path(log_dir);log_dir.mkdir(parents=True,exist_ok=True)
    from chassis_pd_checkpoint import resume_chassis_pd_new_episode
    ck=torch.load(path,map_location='cpu',weights_only=False)
    if 'H1_step270_task_state' in ck:
        load(env,ck['H1_step270_task_state']);migration='same_new_task_state_restored'
    else:
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==SOURCE_SHA
        migrated=migrate_reference(ck,env.h1_phase.state_dict(),env.num_envs)
        load(env,migrated['H1_step270_task_state']);migration=migrated['H1_step270_explicit_migration']
    current=state(env);tmp=Path(log_dir)/'STEP270_FULLSTATE_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt'
    torch.save(current,tmp);load(env,torch.load(tmp,map_location='cpu',weights_only=False));assert exact(state(env),current)
    # Existing D0-D7 path restores all streams/core first, then resets exactly one physical episode.
    proof=resume_chassis_pd_new_episode(runner,env,path,log_dir)
    assert not env.h1_phase.age_control.any() and not env.h1_phase.attempt.any() and not env.h1_phase.public_request().any()
    assert not env.h1_phase.goal.success.any() and not env.h1_phase.crossed.any()
    row=dict(epoch=time.time(),source_SHA=hashlib.sha256(Path(path).read_bytes()).hexdigest(),explicit_new_task_migration=migration,complete_D0_D7_original_proof=proof,actual_CUDA_new_task_roundtrip_exact=True,new_physical_episode_zeroes_goal_credit=True,not_PhysX_exact_resume=True)
    Path(log_dir,'STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(row,indent=2))
    return row

def install_step270_save_contract(runner,env):
    from chassis_pd_checkpoint import install_chassis_pd_save_contract
    install_chassis_pd_save_contract(runner,env);original=runner.save
    def save(path,*a,**kw):
        original(path,*a,**kw);ck=torch.load(path,map_location='cpu',weights_only=False);ck['H1_step270_task_state']=state(env)
        ck['H1_step270_runtime_contract']=dict(version=270,geometry=env.h1_phase.state_dict()['geometry'],actual_step_event_credit=True,source_hour16_SHA=SOURCE_SHA,original_D0_D7_STD_optimizer_save_chain_retained=True)
        torch.save(ck,path)
    runner.save=save
