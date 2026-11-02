"""Track actual wheel world heights alongside the approved attitude reward."""
import torch

PROTOCOL = dict(kind='REFERENCE_WHEEL_WORLD_HEIGHT_V1', scale_m=.05, weight=1.,
                attitude_scale_rad=.2, attitude_weight=.5,
                total_cost_reward_denominator=5.,
                measurement='Current actual wheel body centers minus environment origin z',
                reference='Existing planned wheel_world heights; no new route or height target')


def normalized_wheel_height_cost(actual_height, reference_height):
    assert actual_height.shape == reference_height.shape and actual_height.shape[-1] == 2
    return ((actual_height-reference_height)/PROTOCOL['scale_m']).square().mean(-1)


def tracking_cost_wheel_height(state, label, leg_ids, wheel_body_ids, previous, action, *, wheel_height):
    from h1_attitude_reward import tracking_cost_attitude
    cost, terms = tracking_cost_attitude(state, label, leg_ids, wheel_body_ids, previous, action)
    height = normalized_wheel_height_cost(wheel_height, label['wheel_world'][:, :, 2])
    cost = cost+PROTOCOL['weight']*height
    assert torch.isfinite(cost).all()
    return cost, dict(terms, wheel_world_height=height)
