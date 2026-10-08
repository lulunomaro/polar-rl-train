"""Candidate D7 COM only; no trainer/controller/launch authority in this preparation."""
import os
from gas_damping_training_env import GasDampingMod4Env
from chassis_com_frame_sdk_adapter import ChassisCOMSDK
from chassis_com_component import PROFILE
class ChassisCOMMod4Env(GasDampingMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        selected=os.environ.get('RM_CHASSIS_COM_PROFILE','off')
        if selected not in ('off',PROFILE):raise ValueError('Unapproved chassis COM profile')
        self._chassis_com=ChassisCOMSDK(self,selected==PROFILE,int(self.cfg.seed))
    def chassis_com_recipe(self):
        return dict(profile=PROFILE if self._chassis_com.component.enabled else 'off',
                    local_translation_bounds_m=[-.005,.005],body='chassis',independent_episode_xyz=True,
                    original_quaternion_mass_inertia_PD_preserved=True,whole_system_shift_mass_weighted=True,
                    no_PD_group_installed=True,engineering_pressure_not_hardware_calibration=True)
