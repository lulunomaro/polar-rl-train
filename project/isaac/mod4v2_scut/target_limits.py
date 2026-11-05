"""Use released continuous mechanical projection, preserving source delay ABI."""
import sys
from .hardware import adapter


def limited_action_type(original, contract):
    task = sys.modules['mod4_task']
    if original is not task.DelayedJointPositionAction or contract != task.CONTRACT:
        raise ValueError('Expected the original action class and the selected v2 contract')
    return adapter().make_mechanical_action_class(task)


def leg_target_projection_error(*args):
    raise RuntimeError('The old MOD4v1 projection reward is absent from this fresh SCUT recipe')
