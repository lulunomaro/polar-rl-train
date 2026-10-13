"""D2-only episode encoder-bias ablation. Original noise/delay/RNG remain active."""
import hashlib
from pathlib import Path
import torch
class ZeroEncoderBiasFactor:
 def __init__(self,env,module):
  if hasattr(env,'_io_dr_encoder_bias_zero_factor') or hasattr(env,'_io_dr_feedback_current_factor'):raise RuntimeError('One feedback factor per isolated case')
  self.env=env;self.module=module;self.original=module.feedback;self.calls={};self.changed_calls=0;self.max_bias_abs=0.
  self.source_path=getattr(module,'__file__',None);self.source_sha=hashlib.sha256(Path(self.source_path).read_bytes()).hexdigest() if self.source_path else None
  module.feedback=self.feedback;env._io_dr_encoder_bias_zero_factor=self
 def feedback(self,env,key,raw):
  assert env is self.env
  value=self.original(env,key,raw);sensor=self.module.sensor_state(env);delay=self.module.delay_state(env)
  self.calls[key]=self.calls.get(key,0)+1
  if key!='leg_pos' or sensor.profile=='off':return value
  # Bias is constant inside a physical episode; originalreset clears old queue rows.
  assert torch.equal(sensor.episode,delay.episode),'Sensor/delay physical episode identity mismatch'
  assert bool(torch.isfinite(sensor.bias).all()) and float(sensor.bias.abs().max())<=.0075+1e-7
  if delay.enabled:assert bool((delay.cache[key]['last']==int(env.common_step_counter)).all())
  self.max_bias_abs=max(self.max_bias_abs,float(sensor.bias.abs().max()));self.changed_calls+=int(bool((sensor.bias!=0).any()))
  return value-sensor.bias
 def receipt(self):
  sensor=self.module.sensor_state(self.env);delay=self.module.delay_state(self.env)
  return dict(factor_id='D2_zero_fixed_episode_leg_encoder_bias_only',diagnostic_only=True,
   original_feedback_source_path=self.source_path,original_feedback_source_sha256=self.source_sha,
   original_sensor_uniform_noise_delay_queue_RNG_side_effects_retained=True,
   output_changed_only_by_subtracting_current_physical_episode_fixed_leg_bias=True,
   no_clean_other_channel_or_privileged_actor_feedback=True,actor_dimensions_unchanged=35,
   calls=dict(self.calls),actual_changed_leg_calls=self.changed_calls,max_original_bias_abs_rad=self.max_bias_abs,
   original_bias_bound_rad=.0075,actual_noise_draw_counts=dict(sensor.draw_counts),
   actual_requested_original_delay_us=(delay.delay*10000).detach().cpu().tolist(),
   original_bias_and_delay_assignment_metadata_not_relabelled=True)
def install(env,module=None):
 if module is None:
  import feedback_delay_runtime as module
 return ZeroEncoderBiasFactor(env,module)
