"""Projected Adam proposal on measured start observations; no reward edits."""
from copy import deepcopy
import torch


def bounded_actor_step(actor, optimizer, predict, observed, ground, target,
                       *, apply_step=True, radius=.05, retention_radius=.5):
    parameters=tuple(actor.parameters())
    with torch.no_grad():
        old=tuple(p.detach().clone() for p in parameters)
        before=predict(observed).detach().clone()
        ground_before=predict(ground).detach().clone()
        old_ground=float((ground_before-target).abs().max())
    if not apply_step:
        return dict(applied=False,no_step_admission=True,radius=radius,
                    ground_reference_max_abs=old_ground)
    saved_optimizer=deepcopy(optimizer.state_dict())
    optimizer.step()
    with torch.no_grad():
        proposed=tuple(p.detach().clone() for p in parameters)
        proposal_delta=float((predict(observed)-before).abs().max())
        accepted=False;alpha=1.
        for attempt in range(12):
            if attempt:
                for p,a,b in zip(parameters,old,proposed,strict=True):p.copy_(a+alpha*(b-a))
            after=predict(observed);now_ground=predict(ground)
            delta=float((after-before).abs().max())
            ground_error=float((now_ground-target).abs().max())
            finite=bool(torch.isfinite(after).all() and torch.isfinite(now_ground).all())
            if finite and delta<=radius and ground_error<=max(retention_radius,old_ground)+1e-6:
                accepted=True;break
            alpha*=.5
        if not accepted:
            for p,a in zip(parameters,old,strict=True):p.copy_(a)
            optimizer.load_state_dict(saved_optimizer)
            delta=0.;ground_error=old_ground;alpha=0.
    return dict(applied=accepted,proposal_action_max_delta=proposal_delta,
                applied_action_max_delta=delta,parameter_interpolation_alpha=alpha,
                radius=radius,ground_reference_max_abs_before=old_ground,
                ground_reference_max_abs_after=ground_error,
                retention_radius=retention_radius,optimizer_restored_if_rejected=not accepted,
                scope='sampled real starting observations; no guarantee on unobserved states')
