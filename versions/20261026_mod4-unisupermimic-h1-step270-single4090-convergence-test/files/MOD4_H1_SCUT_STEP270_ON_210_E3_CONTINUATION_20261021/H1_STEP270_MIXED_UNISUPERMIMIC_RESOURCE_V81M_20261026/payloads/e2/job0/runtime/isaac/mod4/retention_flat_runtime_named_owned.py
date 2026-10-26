"""Private command generator has explicit state ownership; legacy named streams stay exact."""
from retention_flat_runtime import RetainedFlatCommand
from retention_flat_runtime_sdk_reviewed import configure_retention as original_configure

class RetainedFlatNamedOwnedCommand(RetainedFlatCommand):
 @property
 def _retention_rng(self):
  return self._retention_rng_owner['generator']
 @_retention_rng.setter
 def _retention_rng(self,value):
  self._retention_rng_owner={'generator':value}

def configure_retention(cfg):
 recipe=original_configure(cfg)
 cfg.commands.twist.class_type=RetainedFlatNamedOwnedCommand
 recipe['private_command_rng_ownership']='Explicit E1 retained command state only; strict legacy named stream set unchanged.'
 return recipe
