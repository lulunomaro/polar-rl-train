"""Uninstalled successor rates: preserve actor35 and use measured gyro feedback.

The absolute takeoff heading remains a task success witness, not a newly exposed
actor observation. The old feed-forward actor cannot directly observe that
reference angle. Minimize observable yaw rate to prevent drift; do not claim an
unobserved heading error alone teaches reliable return-to-heading control.
"""
import torch
from step270_goal_and_scut_rates_candidate import Contract,Step270Events
from step270_goal_and_scut_rates_candidate import scut_phase_rates as previous

PROFILE=dict(version=2,uninstalled=True,actor_dimension=35,critic_dimension=38,
             action_dimension=6,new_actor_inputs=False,
             source_STD_and_all17_Adam_inherited_not_reset=True,
             observed_landing_feedback='body gyro z and projected gravity; planar speed remains original measured reward input',
             absolute_heading='original event/diagnostic witness only; no new teacher input',
             no_forces_or_PD_assist_or_air_reset=True,
             weights='not yet SDK normalized/admitted; retain original costs and explicitly log all successor weights before any GO')

def rates(*,angular_velocity_body,projected_gravity,**kw):
    if not torch.isfinite(angular_velocity_body).all() or not torch.isfinite(projected_gravity).all():
        raise ValueError('Nonfinite observed feedback')
    result=previous(**kw)
    # V1 CPU draft is preserved. Its heading cost is a diagnostic, not deployed.
    result.pop('landing_heading_error')
    landed=kw['landed'].float()
    result['landing_yaw_rate']=landed*angular_velocity_body[:,2].square()
    result['landing_tilt']=landed*projected_gravity[:,:2].square().sum(-1)
    return result
