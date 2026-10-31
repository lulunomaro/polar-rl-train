from source_cache208_v3 import cached_load,cached_H
"""Complete D7 state on top of actual D6 saved contract; one fresh episode."""
from pathlib import Path
import os,json,time,torch
from chassis_com_component import PROFILE as COM_PROFILE
from explicit_pd_component import PROFILE as PD_PROFILE
from gas_damping_checkpoint208_v3 import validate_saved_damping
from spring_pressure_checkpoint208_v3 import exact
def validate_saved_chassis_pd(state,n):
    assert state['version']==1 and state['rng_device_type']=='cuda'
    com=state['COM'];pd=state['PD']
    for st,profile in ((com,COM_PROFILE),(pd,PD_PROFILE)):
        assert st['version']==1 and st['profile']==profile and st['num_envs']==n and st['enabled']
        assert st['episode'].shape==(n,) and st['episode'].dtype==torch.long and bool((st['episode']>=0).all())
    delta=com['delta_m'];assert delta.shape==(n,3) and torch.isfinite(delta).all() and bool((delta.abs()<=.005001).all())
    assert len(com['private_xyz_RNG'])==3
    assert set(pd['factor'])==set(pd['private_group_RNG'])=={'leg_kp','leg_kd','wheel_kd'}
    for k,width in (('leg_kp',4),('leg_kd',4),('wheel_kd',2)):
        v=pd['factor'][k];assert v.shape==(n,width) and torch.isfinite(v).all() and bool(((v>=.949999)&(v<=1.050001)).all())
    for rng in list(com['private_xyz_RNG'])+list(pd['private_group_RNG'].values()):assert rng.dtype==torch.uint8 and rng.ndim==1 and rng.numel()>0
    return True
def current_state(env):
    return dict(version=1,rng_device_type=env.device.split(':')[0] if isinstance(env.device,str) else env.device.type,COM=env._chassis_com.state_dict(),PD=env._explicit_pd.state_dict())
def install_chassis_pd_save_contract(runner,env):
    from gas_damping_checkpoint208_v3 import install_damping_save_contract
    install_damping_save_contract(runner,env);original=runner.save
    def save(path,*args,**kw):
        original(path,*args,**kw);ck=cached_load(path,map_location='cpu',weights_only=False);state=current_state(env);validate_saved_chassis_pd(state,env.num_envs)
        ck['chassis_PD_state']=state;ck['chassis_PD_recipe']=env.chassis_pd_recipe();ck['chassis_PD_resume_contract']='Restore full D1-D6 and COM/PD private CUDA streams, then one fresh physics episode; not PhysX exactresume.';torch.save(ck,path)
    runner.save=save
def resume_chassis_pd_new_episode(runner,env,path,log_dir):
    from gas_damping_checkpoint208_v3 import resume_damping_new_episode
    ck=cached_load(path,map_location='cpu',weights_only=False);has='chassis_PD_state' in ck
    if has:
        validate_saved_chassis_pd(ck['chassis_PD_state'],env.num_envs);assert ck['chassis_PD_recipe']==env.chassis_pd_recipe()
        env._chassis_com.load_state_dict(ck['chassis_PD_state']['COM']);env._explicit_pd.load_state_dict(ck['chassis_PD_state']['PD']);assert exact(current_state(env),ck['chassis_PD_state'])
    else:
        assert os.environ.get('RM_CHASSIS_PD_INITIAL_ADMISSION')=='D6_to_D7';validate_saved_damping(ck['gas_damping_state'],env.num_envs)
    saved=current_state(env);tmp=Path(log_dir)/'CHASSIS_PD_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt';torch.save(saved,tmp);loaded=cached_load(tmp,map_location='cpu',weights_only=False)
    env._chassis_com.load_state_dict(loaded['COM']);env._explicit_pd.load_state_dict(loaded['PD']);assert exact(current_state(env),saved)
    ce=env._chassis_com.component.episode.clone();pe=env._explicit_pd.component.episode.clone()
    row=resume_damping_new_episode(runner,env,path,log_dir)
    assert torch.equal(env._chassis_com.component.episode,ce+1) and torch.equal(env._explicit_pd.component.episode,pe+1)
    audit=env.chassis_pd_audit()
    proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_chassis_PD_state=has,COM_PD_factors_episodes_six_CUDA_RNG_restored_exact=has,
               explicitly_new_D7_groups=not has,actual_CUDA_chassis_PD_disk_roundtrip_exact=True,COM_PD_episode_incremented_once=True,complete_D1_D6_optimizer_global_named_streams_verified=True,
               actual_chassis_PD_audit=audit,new_physical_episode=True,PhysX_exact_resume_claimed=False)
    Path(log_dir,'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2));return proof
