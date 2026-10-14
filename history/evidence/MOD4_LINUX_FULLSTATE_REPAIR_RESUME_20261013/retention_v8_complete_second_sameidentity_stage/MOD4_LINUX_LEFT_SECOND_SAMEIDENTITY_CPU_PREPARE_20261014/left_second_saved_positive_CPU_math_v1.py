"""Pure saved-state math. No transport, SDK, RNG draws or CUDA calls."""
from pathlib import Path
import sys
P=Path(__file__).resolve().parent/'payload_v1'
sys.path.insert(0,str(P))
from second_target_CPU_pure_guard_v2 import logical_fullsave,same,walk,KEY
def verify_positive_state(c,source):
    import torch
    own=logical_fullsave(c);logical_fullsave(source)
    assert set(c)==set(source),'Saved fullstate schema cannot silently change'
    assert set(c['actor_state_dict'])==set(source['actor_state_dict'])
    delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(source['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
    assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0,'No genuine saved PPO optimizer advance'
    actor=sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in c['actor_state_dict'].items())
    assert actor==9,'Expected genuine full actor PPO updates'
    assert same(c[KEY],source[KEY]),'One-time initializer metadata must not repeat or change'
    assert c['independent_terrain_expert']==source['independent_terrain_expert']=='E1_WAVE50'
    assert c['E1_WAVE50_initial_source_sha256']==source['E1_WAVE50_initial_source_sha256']
    for k in ('sensor_DR_state','E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_retained_flat_command_state','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):
        assert c[k]['profile']==source[k]['profile'],k
    src=dict(walk(source));rows=dict(walk(c));assert set(src)==set(rows)
    assert all(not v.numel() or v.untyped_storage().data_ptr()!=src[k].untyped_storage().data_ptr() for k,v in rows.items())
    updates=int(delta[0]/20)
    return dict(actual_fullsave=own,actor_tensors_changed=actor,optimizer_step_delta=delta[0],saved_updates=updates,saved_controls=updates*24,saved_envsteps=updates*480000,saved_callbacks=updates*96,all195_saved_parent_tensors_independent_storage=True,old_left_initializer_metadata_exact_not_repeated=True)
def verify_latest_health(h):
    # Health is the current live snapshot and may be ahead of the saved model.
    assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
    assert h['nonfinite_observed'] is False and h['stop_reason'] is None
    assert h['termination_reason_coverage_exact'] is True and h['truncation_reason_coverage_exact'] is True
    return True
