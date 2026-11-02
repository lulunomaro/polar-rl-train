from source_cache208_v3 import cached_load,cached_H
"""Full D6 state before one fresh physics episode; keep complete D1-D5 contract."""
from pathlib import Path
import os,time,json,torch
from gas_damping_factor import PROFILE
from spring_pressure_checkpoint208_v3 import exact,validate_saved_pressure

def validate_saved_damping(state,n,device_type='cuda'):
    assert state['physical_parameter']==PROFILE and state['version']==1 and state['n']==n
    assert state['enabled'] and state['rng_device_type']==device_type
    assert state['factor'].shape==(n,2) and state['episode'].shape==(n,) and state['episode'].dtype==torch.long
    assert torch.isfinite(state['factor']).all() and bool(((state['factor']>=.9)&(state['factor']<=1.1)).all())
    assert bool((state['episode']>=0).all())
    assert len(state['rng'])==2 and all(s.dtype==torch.uint8 and s.ndim==1 and s.numel()>0 for s in state['rng'])
    return True

def install_damping_save_contract(runner,env):
    from spring_pressure_checkpoint208_v3 import install_spring_save_contract
    install_spring_save_contract(runner,env);original=runner.save
    def save(path,*args,**kw):
        original(path,*args,**kw)
        ck=cached_load(path,map_location='cpu',weights_only=False);state=env._gas_damping.state_dict()
        validate_saved_damping(state,env.num_envs)
        ck['gas_damping_state']=state;ck['gas_damping_recipe']=env.gas_damping_recipe()
        ck['gas_damping_resume_contract']='Restore independent factor/episode/two CUDA RNG plus complete D1-D5/optimizer/global/named streams, then fresh physical episode. Not PhysX exactresume.'
        torch.save(ck,path)
    runner.save=save

def resume_damping_new_episode(runner,env,path,log_dir):
    from spring_pressure_checkpoint208_v3 import resume_spring_new_episode
    ck=cached_load(path,map_location='cpu',weights_only=False);adapter=env._gas_damping
    has='gas_damping_state' in ck
    if has:
        assert ck['gas_damping_recipe']==env.gas_damping_recipe()
        validate_saved_damping(ck['gas_damping_state'],env.num_envs)
        adapter.load_state_dict(ck['gas_damping_state']);assert exact(adapter.state_dict(),ck['gas_damping_state'])
    else:
        assert os.environ.get('RM_GAS_DAMPING_INITIAL_ADMISSION')=='D5_to_D6'
        validate_saved_pressure(ck['spring_pressure_state'],env.num_envs)
        assert ck['spring_pressure_recipe']['profile']=='gas_stiffness_independent_episode_090_110_v1'
    saved=adapter.state_dict();tmp=Path(log_dir)/'GAS_DAMPING_STATE_STARTUP_ROUNDTRIP.pt'
    torch.save(saved,tmp);adapter.load_state_dict(cached_load(tmp,map_location='cpu',weights_only=False))
    assert exact(adapter.state_dict(),saved)
    episodes=adapter.component.episode.clone()
    row=resume_spring_new_episode(runner,env,path,log_dir)
    assert torch.equal(adapter.component.episode,episodes+1)
    audit=adapter.audit();assert audit['actual_PhysX_buffer_implicit_model_exact']
    proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_gas_damping_state=has,
        gas_factor_episode_two_CUDA_RNG_restored_exact=has,explicitly_new_D6_damping=not has,
        actual_CUDA_gas_state_disk_roundtrip_exact=True,gas_episode_incremented_once=True,
        complete_D1_D5_optimizer_global_named_streams_verified=True,gas_parameter_audit=audit,
        new_physical_episode=True,PhysX_exact_resume_claimed=False)
    Path(log_dir,'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2))
    return proof
