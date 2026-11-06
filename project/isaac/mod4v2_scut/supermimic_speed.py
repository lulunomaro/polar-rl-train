"""Opt-in execution changes; optimizer tensors and checkpoints stay intact."""
import torch


def enable_fused_adam(learner):
    if torch.device(learner.device).type!='cuda':raise ValueError('Fused Adam requires CUDA')
    rows={}
    for name in ('wm','pi','v','aux'):
        optimizer=getattr(learner,'opt_'+name)
        if not isinstance(optimizer,torch.optim.Adam):raise TypeError('Expected existing Adam')
        optimizer.defaults.update(fused=True,foreach=False)
        optimizer._step_supports_amp_scaling=True
        for group in optimizer.param_groups:
            group.update(fused=True,foreach=False)
            for p in group['params']:
                state=optimizer.state.get(p)
                if state and 'step'in state:state['step']=state['step'].to(p.device)
        rows[name]=dict(state_entries=len(optimizer.state),fused=True,
            hooks_retained=True,weights_moments_and_steps_reset=False)
    return rows


def enable_scripted_geometry():
    """Compile pure tensor geometry without tracing changing model buffers."""
    from supermimic_vendor_v2 import networks,geometry
    import ctx_reward_learner
    names=('invariant_features','yaw_mat','so3_exp','so3_log')
    for name in names:
        setattr(networks,name,torch.jit.script(getattr(geometry,name)))
    ctx_reward_learner.invariant_features=networks.invariant_features
    return dict(implementation='TorchScript_pure_geometry',functions=list(names),
        AMP_changed=False,pinned_source_changed=False)
