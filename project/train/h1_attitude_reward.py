"""Human-approved H1 attitude scale; all other tracking terms stay unchanged."""
import torch

PROTOCOL = dict(kind='GEODESIC_REFERENCE_ATTITUDE_V1', scale_rad=.2,
                weight=.5, total_cost_reward_denominator=5.,
                human_approval='2026-11-03: 同意这项姿态奖励修复并继续RL验证')


def normalized_attitude_cost(actual_rotation, reference_rotation):
    cosine = ((actual_rotation*reference_rotation).sum((-1, -2))-1)*.5
    angle = torch.acos(cosine.clamp(-1., 1.))
    return (angle/PROTOCOL['scale_rad']).square()


def tracking_cost_attitude(state, label, leg_ids, wheel_body_ids, previous, action):
    from tracking_reference389 import tracking_cost389
    cost, terms = tracking_cost389(state, label, leg_ids, wheel_body_ids, previous, action)
    replacement = normalized_attitude_cost(state[1], label['state'][:, 3:12].reshape_as(state[1]))
    cost = cost+PROTOCOL['weight']*(replacement-terms['rotation'])
    assert torch.isfinite(cost).all()
    return cost, dict(terms, rotation=replacement)
