"""External H1 zero-twist request remains exact across selected resets; no terrain policy."""
import torch
from h1_original_directional_runtime import DirectionalSpinCommand,configure as original_configure,audit as original_audit
class H1ExternalOperatorCommand(DirectionalSpinCommand):
 def _resample_command(self,env_ids):
  super()._resample_command(env_ids)
  ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long);self.vel_command_b[ids]=0;self.is_pure_spin[ids]=False;self.is_moving_spin[ids]=False;self.is_transition_spin[ids]=False;self.manual_evaluation_mode=True
 def _write_dynamic(self,ids):
  self.vel_command_b[ids]=0
def configure(cfg):
 original_configure(cfg);cfg.commands.twist.class_type=H1ExternalOperatorCommand
def audit(env):
 result=original_audit(env);term=env.command_manager.get_term('twist');assert isinstance(term,H1ExternalOperatorCommand) and torch.equal(term.command,torch.zeros_like(term.command));result.update(stage='H1_external_operator_zero_twist_v1',no_position_or_terrain_command_generation=True,operator_mode_request_is_not_phase_truth=True);return result
