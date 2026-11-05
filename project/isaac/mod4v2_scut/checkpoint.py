"""Keep the complete learner/DR/RNG format, with an explicit v2 identity."""
from .shared import load, export
_source = load('checkpoint')
_source.FORMAT = 'MOD4V2_SCUT_HW300N60_FULL_V1'
_source.INTERFACE = 'actor35_critic78_scut__HW300N60_continuous_targets__full_learning_DR_RNG'
_original_learning_state = _source.learning_state


def _fudan_learning_state(runner):
    value = _original_learning_state(runner)
    value.update(reward_family='FUDAN_JUMP',
                 reward_source_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',
                 reward_memory='fudan contactfilter/airtime/virtuallegs in source_reward_state')
    return value


_source.learning_state = _fudan_learning_state
export(_source, globals())
