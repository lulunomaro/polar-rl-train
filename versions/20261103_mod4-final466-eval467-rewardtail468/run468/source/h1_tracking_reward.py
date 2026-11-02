"""Bounded tracking reward with a slower tail for the same nonnegative cost."""
import torch


PROTOCOL = dict(kind='RECIPROCAL_TOTAL_TRACKING_COST_V1', denominator=5.,
                formula='1/(1+cost/5)',
                cost='Unchanged attitude464 plus wheel-world-height466 cost',
                optimum='One at zero cost; strictly decreasing for positive cost')


def tracking_reward(cost):
    return torch.reciprocal(1.+cost/PROTOCOL['denominator'])
