"""D7 explicit-PD subgroup only; isolated from chassis-COM SDK preparation."""
import os
from gas_damping_training_env import GasDampingMod4Env
from explicit_pd_component import PROFILE
from explicit_pd_sdk_adapter import ExplicitPDSDK
class ExplicitPDMod4Env(GasDampingMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        profile=os.environ.get('RM_EXPLICIT_PD_PROFILE','off')
        if profile not in ('off',PROFILE):raise ValueError('Unapproved explicit-PD profile')
        self._explicit_pd=ExplicitPDSDK(self,profile==PROFILE,int(self.cfg.seed))
    def explicit_pd_recipe(self):
        return dict(profile=PROFILE if self._explicit_pd.component.enabled else 'off',factor_bounds=[.95,1.05],
                    leg_kp_nominal=60.,leg_kd_nominal=2.,wheel_kd_nominal=.6,wheel_kp_fixed0=True,
                    independent_episode_groups=True,no_chassis_COM_group_installed=True,no_implicit_drive_gas_passive_damping_or_output_gain_change=True)
