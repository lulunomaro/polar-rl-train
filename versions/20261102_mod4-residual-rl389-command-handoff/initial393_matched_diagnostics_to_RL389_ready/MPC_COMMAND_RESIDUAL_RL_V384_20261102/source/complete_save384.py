"""Validate complete Adam state, including an explicitly fresh zero-step optimizer."""
def complete_adam_steps384(optimizer,updates,expected_slots=8):
    slots=list(optimizer.state.values())
    if updates==0:
        assert not slots, 'fresh tracking critic must have no fabricated Adam state'
        return dict(step_min=0,step_max=0,state_slots=0,fresh_zero_step=True)
    assert len(slots)==expected_slots
    steps=[int(v['step'])for v in slots]
    assert min(steps)==max(steps)==updates
    return dict(step_min=min(steps),step_max=max(steps),state_slots=len(slots),fresh_zero_step=False)
