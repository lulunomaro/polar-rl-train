"""Penalize executed leg position targets outside the existing joint limits."""
import torch

PROTOCOL = dict(kind='PROCESSED_LEG_TARGET_LIMIT_COST_V1', scale_rad=.1, weight=1.,
                leg_order=['left_crank','left_hip','right_crank','right_hip'],
                lower_rad=[-1.2,-.5,-1.2,-.5], upper_rad=[.9,.5,.9,.5],
                measurement='Same pre-reset endpoint robot joint_pos_target in leg order',
                changes_action_or_physics=False)


def normalized_leg_target_limit_cost(leg_target):
    assert leg_target.shape[-1]==4
    lower=leg_target.new_tensor(PROTOCOL['lower_rad'])
    upper=leg_target.new_tensor(PROTOCOL['upper_rad'])
    excess=torch.relu(lower-leg_target)+torch.relu(leg_target-upper)
    return (excess/PROTOCOL['scale_rad']).square().mean(-1)


def tracking_cost_target_limit(state, label, leg_ids, wheel_body_ids, previous, action, *, wheel_position, leg_target):
    from h1_tight_attitude_reward import tracking_cost_tight_attitude
    cost,terms=tracking_cost_tight_attitude(state,label,leg_ids,wheel_body_ids,
                                          previous,action,wheel_position=wheel_position)
    limit_cost=normalized_leg_target_limit_cost(leg_target)
    cost=cost+PROTOCOL['weight']*limit_cost
    assert torch.isfinite(cost).all()
    return cost,dict(terms,leg_target_limit=limit_cost)
