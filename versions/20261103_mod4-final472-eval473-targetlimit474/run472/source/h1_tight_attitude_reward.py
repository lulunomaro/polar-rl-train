"""Tighten reference attitude tracking after the observed pitch error."""
import torch

PROTOCOL = dict(kind='REFERENCE_ATTITUDE_SCALE_010_V1', scale_rad=.1, weight=.5,
                previous_scale_rad=.2, reference='Existing planned rotation')


def tracking_cost_tight_attitude(state, label, leg_ids, wheel_body_ids, previous, action, *, wheel_position):
    from h1_wheel_position_reward import tracking_cost_wheel_position
    cost, terms = tracking_cost_wheel_position(state, label, leg_ids, wheel_body_ids,
                                             previous, action, wheel_position=wheel_position)
    rotation = terms['rotation']*(PROTOCOL['previous_scale_rad']/PROTOCOL['scale_rad'])**2
    cost = cost+PROTOCOL['weight']*(rotation-terms['rotation'])
    assert torch.isfinite(cost).all()
    return cost, dict(terms, rotation=rotation)
