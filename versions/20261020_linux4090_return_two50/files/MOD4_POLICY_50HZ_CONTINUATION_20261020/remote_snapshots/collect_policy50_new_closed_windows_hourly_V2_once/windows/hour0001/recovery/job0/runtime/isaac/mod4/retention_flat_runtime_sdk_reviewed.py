"""Explicit installed SDK reward signature; original contribution stays zero."""
from retention_flat_runtime import configure_retention as original_configure
from retention_flat_runtime import inactive_retention_rolling
def inactive_retention_rolling_sdk(env,speed_scale=.15,yaw_min=3.5,support_weight=.25):
 return inactive_retention_rolling(env,speed_scale=speed_scale,yaw_min=yaw_min,support_weight=support_weight)
def configure_retention(cfg):
 recipe=original_configure(cfg)
 cfg.rewards.spin_contact_consistency.func=inactive_retention_rolling_sdk
 recipe['SDK_reward_signature_repair']='Explicit speed_scale,yaw_min,support_weight parameters; same zero contribution, no reward change.'
 return recipe
