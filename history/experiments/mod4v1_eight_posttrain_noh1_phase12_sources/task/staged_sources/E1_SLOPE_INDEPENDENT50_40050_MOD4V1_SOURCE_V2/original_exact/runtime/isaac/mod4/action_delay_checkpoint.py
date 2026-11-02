"""Complete D4 queues/RNG restore before an explicit fresh physical episode."""
import json,os,time,torch
from pathlib import Path
from feedback_delay_checkpoint import exact

def restore_action_before_new_episode(env,ck):
    adapter=env._physics_action_delay;q=adapter.queue
    has='physical_action_delay_state' in ck
    if has:
        assert ck['physical_action_delay_recipe']==env.action_delay_recipe()
        adapter.load_state_dict(ck['physical_action_delay_state'])
        assert exact(adapter.state_dict(),ck['physical_action_delay_state'])
    else:
        assert os.environ.get('RM_ACTION_DELAY_INITIAL_ADMISSION')=='D3_to_D4'
        assert ck['feedback_delay_recipe']['profile']=='control_0_10ms_v1'
        assert ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
    episodes={k:g['episode'].clone() for k,g in q.groups.items()}
    # A fresh scene has its own physics clock. Rebase only after the saved state
    # and both queue RNG streams were verified exactly. The following env.reset
    # clears values and resamples the selected episode once through real terms.
    assert int(env._sim_step_counter)==0
    for g in q.groups.values():g['last_apply_tick'].fill_(-1)
    return has,episodes

def verify_action_new_episode(env,episodes):
    adapter=env._physics_action_delay
    for key,g in adapter.queue.groups.items():
        assert torch.equal(g['episode'],episodes[key]+1)
        assert not bool(g['pending_valid'].any()) and not bool(g['applied_valid'].any())
        assert torch.equal(g['applied'],adapter.neutral(key))
        assert torch.equal(g['pending'],adapter.neutral(key))
        for n in ('issued_tick','due_tick','applied_issue_tick','first_apply_tick','last_submit_tick','last_apply_tick'):
            assert bool((g[n]==-1).all()),n
    assert int(env._sim_step_counter)==0
    return True

def append_action_state(ck,env):
    adapter=env._physics_action_delay;s=adapter.state_dict();adapter.queue.validate_state(s)
    ck['physical_action_delay_state']=s
    ck['physical_action_delay_recipe']=env.action_delay_recipe()
    ck['physical_action_delay_resume_contract']='Exact queue/target/timestamp/RNG restore first, then new physics clock and one real episode reset; no PhysX exact resume.'
    return ck

def install_action_save_contract(runner,env):
    from feedback_delay_checkpoint import install_delay_save_contract
    install_delay_save_contract(runner,env);original=runner.save
    def save(path,*a,**kw):
        original(path,*a,**kw)
        ck=torch.load(path,map_location='cpu',weights_only=False)
        torch.save(append_action_state(ck,env),path)
    runner.save=save

def resume_action_new_episode(runner,env,path,log_dir):
    from feedback_delay_checkpoint import resume_delay_new_episode
    ck=torch.load(path,map_location='cpu',weights_only=False)
    has,episodes=restore_action_before_new_episode(env,ck)
    row=resume_delay_new_episode(runner,env,path,log_dir)
    verify_action_new_episode(env,episodes)
    v=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],
           predecessor_had_action_queue=has,action_queue_targets_timestamps_both_RNG_restored_exact=has,
           explicitly_new_D4_queue=not has,action_episode_incremented_once=True,
           restored_before_new_scene_clock_rebase=True,stale_targets_cleared=True,
           initial_hold_real_default_leg_q_and_zero_wheels=True,
           complete_D3_sensor_feedback_optimizer_global_named_streams_verified=True,
           new_physical_episode=True,PhysX_exact_resume_claimed=False,
           action_delay_recipe=env.action_delay_recipe())
    Path(log_dir,'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(v,indent=2))
    return v
