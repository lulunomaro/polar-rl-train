"""Keep the complete learner/DR/RNG format, with an explicit v2 identity."""
from .shared import load, export
_source = load('checkpoint')
_source.FORMAT = 'MOD4V2_SCUT_HW300N60_FULL_V1'
_source.INTERFACE = 'actor35_critic78_scut__HW300N60_continuous_targets__full_learning_DR_RNG'
export(_source, globals())
