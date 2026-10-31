"""D3 queue/RNG persistence; deliberately reset once into a new physical episode."""
from pathlib import Path
import json,os,time,torch
from feedback_delay_mild import WIDTHS

def exact(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    return a==b

def validate_delay_state(d,s):
    assert s['version']==1 and s['n']==d.n and s['enabled']==d.enabled
    assert s['delay'].shape==s['episode'].shape==(d.n,)
    assert s['delay'].dtype==s['episode'].dtype==torch.long
    assert bool(((s['delay']==0)|(s['delay']==1)).all()) and bool((s['episode']>=0).all())
    assert set(s['cache'])==set(WIDTHS) if d.enabled else not s['cache']
    for key,c in s['cache'].items():
        assert set(c)=={'last','cur','out','sample_tick','ready'}
        assert c['cur'].shape==c['out'].shape==(d.n,WIDTHS[key])
        assert bool(torch.isfinite(c['cur']).all()) and bool(torch.isfinite(c['out']).all())
        assert c['last'].shape==c['sample_tick'].shape==c['ready'].shape==(d.n,)
        assert c['last'].dtype==c['sample_tick'].dtype==torch.long and c['ready'].dtype==torch.bool
        live=c['last']>=0
        assert bool((c['sample_tick'][live]<=c['last'][live]).all())
        age=c['last'][live]-c['sample_tick'][live];assert bool(((age==0)|(age==1)).all())
    return True

def restore_delay_exact(d,s):
    validate_delay_state(d,s);d.load_state_dict(s);assert exact(d.state_dict(),s)
    return True

def install_delay_save_contract(runner,env):
    from sensor_a0_runtime import install_sensor_save_contract
    from feedback_delay_runtime import delay_state
    install_sensor_save_contract(runner,env)
    original=runner.save
    def save(path,*args,**kwargs):
        original(path,*args,**kwargs)
        ck=torch.load(path,map_location='cpu',weights_only=False);d=delay_state(env)
        saved=d.state_dict();validate_delay_state(d,saved)
        ck['feedback_delay_state']=saved
        ck['feedback_delay_recipe']=env.feedback_delay_recipe()
        ck['feedback_delay_resume_contract']='Restore all delay and sensor streams exactly before one fresh physical episode reset. Queue history is cleared by that reset; no PhysX exact resume claim.'
        torch.save(ck,path)
    runner.save=save

def resume_delay_new_episode(runner,env,path,log_dir):
    from feedback_delay_runtime import delay_state
    from sensor_resume_contract import resume_sensor_new_episode
    ck=torch.load(path,map_location='cpu',weights_only=False);d=delay_state(env)
    has_delay='feedback_delay_state' in ck
    if has_delay:
        assert ck['feedback_delay_recipe']==env.feedback_delay_recipe()
        restore_delay_exact(d,ck['feedback_delay_state'])
    else:
        assert 'sensor_DR_state' in ck and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
        # Explicit first D3 admission from the reviewed D1+D2 source, never pretend
        # that the predecessor checkpoint already contained a delay queue.
        assert os.environ.get('RM_DELAY_INITIAL_ADMISSION','')=='D1D2_to_D3'
    before=d.episode.clone()
    sensor=resume_sensor_new_episode(runner,env,path,log_dir)
    assert torch.equal(d.episode,before+1)
    assert d.enabled and set(d.cache)==set(WIDTHS)
    for key in WIDTHS:
        c=d.cache[key];assert bool((c['last']==env.common_step_counter).all())
        assert bool((d.receipt(key,env.common_step_counter)['actual_age_us']==0).all())
        assert not bool(c['ready'].any())
    row=dict(epoch=time.time(),pid=os.getpid(),source_sha256=sensor['source_sha256'],
             predecessor_had_delay_state=has_delay,delay_state_and_RNG_exactly_restored_before_reset=has_delay,
             explicitly_new_D3_stream=not has_delay,delay_recipe=env.feedback_delay_recipe(),
             full_sensor_optimizer_global_named_streams_verified=True,new_physical_episode=True,
             delay_episode_incremented_once=True,all_feedback_queue_warmup_age_us=0,
             sensor_bias_reset_once=True,PhysX_exact_resume_claimed=False)
    Path(log_dir,'DELAY_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(row,indent=2))
    return row
