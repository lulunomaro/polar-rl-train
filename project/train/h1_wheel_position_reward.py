"""Track both wheel centers in the reference plane as well as their heights."""
import torch

PROTOCOL = dict(kind='REFERENCE_WHEEL_PLANAR_POSITION_V1', scale_m=.1, weight=1.,
                reduction='Sum squared x/y errors per wheel, then mean two wheels',
                reference='Existing planned wheel_world positions',
                measurement='Current pre-reset wheel body centers minus environment origin')


def normalized_wheel_planar_cost(actual_position, reference_position):
    assert actual_position.shape == reference_position.shape
    assert actual_position.shape[-2:] == (2,3)
    return ((actual_position[...,:2]-reference_position[...,:2])/PROTOCOL['scale_m']).square().sum(-1).mean(-1)


def tracking_cost_wheel_position(state, label, leg_ids, wheel_body_ids, previous, action, *, wheel_position):
    from h1_wheel_height_reward import tracking_cost_wheel_height
    cost, terms = tracking_cost_wheel_height(state,label,leg_ids,wheel_body_ids,previous,action,
                                            wheel_height=wheel_position[:,:,2])
    planar = normalized_wheel_planar_cost(wheel_position,label['wheel_world'])
    cost = cost+PROTOCOL['weight']*planar
    assert torch.isfinite(cost).all()
    return cost,dict(terms,wheel_world_planar=planar)
