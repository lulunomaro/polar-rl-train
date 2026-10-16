"""Isolated-process D3-only diagnostic hook. Never imported by production training."""
import hashlib
from pathlib import Path
import torch

class CurrentFeedbackFactor:
 def __init__(self,env,module):
  if hasattr(env,'_io_dr_feedback_current_factor'):raise RuntimeError('D3 factor already installed')
  self.env=env;self.module=module;self.original=module.feedback
  self.calls={};self.max_current_formula_error=0.;self.actual_nonzero_baseline_current_differences=0
  self.last_tick=None;self.original_source_path=getattr(module,'__file__',None)
  self.original_source_sha=hashlib.sha256(Path(self.original_source_path).read_bytes()).hexdigest() if self.original_source_path else None
  module.feedback=self.feedback
  env._io_dr_feedback_current_factor=self
 def feedback(self,env,key,raw):
  assert env is self.env
  queued=self.original(env,key,raw)
  sensor=self.module.sensor_state(env);delay=self.module.delay_state(env)
  tick=int(env.common_step_counter)
  if sensor.profile=='off':current=raw.clone()
  else:
   last,noise=sensor.cache[key]
   assert bool((last==tick).all()),'Original current noisy feedback sample missing'
   current=raw+noise+(sensor.bias if key=='leg_pos' else 0.)
  if delay.enabled:
   cached=delay.cache[key]
   assert bool((cached['last']==tick).all()),'Original delay queue did not sample current frame'
   error=float((current-cached['cur']).abs().max())
   assert error<=2e-6,('Current noisy value mismatches actual original queue input',key,error)
   self.max_current_formula_error=max(self.max_current_formula_error,error)
  assert bool(torch.isfinite(current).all()) and current.shape==queued.shape
  self.actual_nonzero_baseline_current_differences+=int(bool((queued!=current).any()))
  self.calls[key]=self.calls.get(key,0)+1;self.last_tick=tick
  return current
 def receipt(self):
  sensor=self.module.sensor_state(self.env);delay=self.module.delay_state(self.env)
  return dict(factor_id='D3_current_noisy_feedback_only',diagnostic_only=True,production_thresholds_unchanged=True,
   original_feedback_source_path=self.original_source_path,original_feedback_source_sha256=self.original_source_sha,
   original_sensor_noise_bias_RNG_and_delay_queue_side_effects_retained=True,
   output_changed_only_from_queued_noisy_to_current_noisy=True,clean_or_privileged_actor_feedback=False,
   actor_dimensions_unchanged=35,calls=dict(self.calls),last_actual_tick=self.last_tick,
   current_noisy_vs_actual_original_queue_input_max_error=self.max_current_formula_error,
   original_formula_tolerance=2e-6,actual_calls_with_nonzero_queued_current_difference=self.actual_nonzero_baseline_current_differences,
   actual_noise_draw_counts=dict(sensor.draw_counts),actual_delay_enabled_metadata_retained=delay.enabled,
   actual_requested_original_delay_us=(delay.delay*10000).detach().cpu().tolist(),
   original_delay_assignment_not_relabelled_as_zero=True)

def install(env,module=None):
 if module is None:
  import feedback_delay_runtime as module
 return CurrentFeedbackFactor(env,module)
