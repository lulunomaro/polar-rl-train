from nominal_d0_source_audit_v1 import mild_dr_present_or_nominal, capture_nominal_d0_reference, parameter_audit as s5_parameter_audit
"""Approved D7 chassis-only COM and explicit motor PD; all D0-D6 retained."""
import os
from gas_damping_training_env import GasDampingMod4Env
from chassis_com_component import PROFILE as COM_PROFILE
from explicit_pd_component import PROFILE as PD_PROFILE
from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK
from explicit_pd_sdk_adapter import ExplicitPDSDK
class ChassisPDMod4Env(GasDampingMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        com=os.environ.get('RM_CHASSIS_COM_PROFILE','off');pd=os.environ.get('RM_EXPLICIT_PD_PROFILE','off')
        if com not in ('off',COM_PROFILE) or pd not in ('off',PD_PROFILE):raise ValueError('Unapproved D7 scope')
        self._chassis_com=ChassisCOMSDK(self,com==COM_PROFILE,int(self.cfg.seed))
        self._explicit_pd=ExplicitPDSDK(self,pd==PD_PROFILE,int(self.cfg.seed))
    def chassis_pd_recipe(self):
        return dict(version=1,COM_profile=COM_PROFILE if self._chassis_com.component.enabled else 'off',PD_profile=PD_PROFILE if self._explicit_pd.component.enabled else 'off',
                    chassis_link_local_delta_m=[-.005,.005],chassis_only=True,PD_factor=[.95,1.05],leg_kp_nominal=60.,leg_kd_nominal=2.,wheel_kd_nominal=.6,wheel_kp0=True,
                    independent_COM_xyz_and_PD_groups=True,motor_implicit_drive_zero=True,complete_D0_D6_retained=True,engineering_pressure_not_hardware_calibration=True)
    def chassis_pd_audit(self):
        return dict(COM=self._chassis_com.audit(),PD=self._explicit_pd.audit(),parameter_auditor=s5_parameter_audit(self))
