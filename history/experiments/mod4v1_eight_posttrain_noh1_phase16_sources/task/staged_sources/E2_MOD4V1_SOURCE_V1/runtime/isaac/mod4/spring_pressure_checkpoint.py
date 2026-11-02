from source_cache208_v3 import cached_load,cached_H
"""Restore all D5 streams first, then one explicit new physical episode."""
from pathlib import Path
import torch,json,time,os

def exact(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b

def validate_saved_pressure(s,n):
    assert s['version']==1 and s['n']==n and s['enabled'] and s['rng_device_type']=='cuda'
    assert s['factor'].shape==(n,2) and s['episode'].shape==(n,) and s['episode'].dtype==torch.long
    assert torch.isfinite(s['factor']).all() and bool(((s['factor']>=.9)&(s['factor']<=1.1)).all()) and bool((s['episode']>=0).all())
    assert len(s['rng'])==2 and all(r.dtype==torch.uint8 and r.ndim==1 and r.numel()>0 for r in s['rng'])
    return True

def resume_spring_new_episode(runner,env,path,log_dir):
    from action_delay_checkpoint import resume_action_new_episode
    ck=cached_load(path,map_location='cpu',weights_only=False);adapter=env._spring_pressure
    has='spring_pressure_state' in ck
    if has:
        assert ck['spring_pressure_recipe']==env.spring_pressure_recipe()
        validate_saved_pressure(ck['spring_pressure_state'],env.num_envs)
        adapter.load_state_dict(ck['spring_pressure_state']);assert exact(adapter.state_dict(),ck['spring_pressure_state'])
    else:
        assert os.environ.get('RM_SPRING_INITIAL_ADMISSION')=='D4_to_D5'
        assert ck['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1'
    # Actual CUDA state disk roundtrip is independently verified at the live
    # scene. This is state evidence, never a pretrained policy selection.
    saved=adapter.state_dict();tmp=Path(log_dir)/'SPRING_STATE_STARTUP_ROUNDTRIP.pt'
    torch.save(saved,tmp);adapter.load_state_dict(cached_load(tmp,map_location='cpu',weights_only=False))
    assert exact(adapter.state_dict(),saved)
    episodes=adapter.component.episode.clone()
    row=resume_action_new_episode(runner,env,path,log_dir)
    assert torch.equal(adapter.component.episode,episodes+1)
    audit=adapter.audit();assert audit['actual_PhysX_buffer_implicit_model_exact']
    v=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_spring_pressure_state=has,
        spring_factor_episode_two_CUDA_RNG_restored_exact=has,explicitly_new_D5_pressure=not has,
        actual_CUDA_spring_state_disk_roundtrip_exact=True,spring_episode_incremented_once=True,
        complete_D1_D4_optimizer_global_named_streams_verified=True,spring_parameter_audit=audit,
        new_physical_episode=True,PhysX_exact_resume_claimed=False)
    Path(log_dir,'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(v,indent=2))
    return v

def install_spring_save_contract(runner,env):
    from action_delay_checkpoint import install_action_save_contract
    install_action_save_contract(runner,env);original=runner.save
    def save(path,*a,**kw):
        original(path,*a,**kw)
        ck=cached_load(path,map_location='cpu',weights_only=False);state=env._spring_pressure.state_dict()
        validate_saved_pressure(state,env.num_envs)
        ck['spring_pressure_state']=state;ck['spring_pressure_recipe']=env.spring_pressure_recipe()
        ck['spring_pressure_resume_contract']='Restore factor/episode/twoCUDA RNG and all D1-D4/optimizer/global-named state first, then new physical episode; not PhysX exactresume.'
        torch.save(ck,path)
    runner.save=save
