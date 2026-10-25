"""D6 environment component, inherited D0-D5 task/observations/hardware intact."""
import os
from spring_pressure_training_env import SpringPressureMod4Env
from gas_damping_sdk_adapter import GasDampingSDK
from gas_damping_factor import PROFILE
class GasDampingMod4Env(SpringPressureMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        profile=os.environ.get('RM_GAS_DAMPING_PROFILE')
        assert profile in ('off',PROFILE)
        self._gas_damping=GasDampingSDK(self,profile!= 'off',int(self.cfg.seed))
    def gas_damping_recipe(self):
        return dict(profile=PROFILE,nominal_damping_Ns_m=3.,independent_two_episode_factor_bounds=[.9,1.1],
                    actual_damping_bounds_Ns_m=[2.7,3.3],D5_stiffness_pressure_retained=True,
                    joint_friction_and_motor_PD_unchanged=True,actor35_cleancritic38_actions6_unchanged=True,
                    hardware_calibration=False,not_full_D6_joint_friction_coverage=True)
