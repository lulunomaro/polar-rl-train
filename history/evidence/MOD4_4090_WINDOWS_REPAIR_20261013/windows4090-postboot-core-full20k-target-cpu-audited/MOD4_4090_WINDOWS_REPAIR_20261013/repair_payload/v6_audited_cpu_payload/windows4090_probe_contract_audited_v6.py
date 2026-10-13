"""New readback-only facade; original V5 query/recipe/reset checks untouched."""
from pathlib import Path
import json,os,time
from windows4090_probe_contract import birth_inputs as original_birth,end_contract as original_end
from windows4090_substep_readback_v6 import attach,H,PROFILE

def birth_inputs(env,O,write,source,placement):
 result=original_birth(env,O,write,source,placement)
 auditor=attach(env,O,write)
 write('ZERO_CONTROL_BIRTH_AND_READBACK_V6_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),original_V5_birth_receipt=result,observer_profile=PROFILE,observer_source_SHA=H(Path(__file__).with_name('windows4090_substep_readback_v6.py')),attached_before_first_probe_control=True,no_step_reset_request_or_RNG=True))
 return result
def audit_control_window_boundary(env,controls,mode,O):
 auditor=env._windows4090_substep_readback_v6
 return auditor.finish_physical_controls(controls,mode)
def end_contract(env,O,write,source,controls,ground_error,height_error,initial_birth):
 auditor=env._windows4090_substep_readback_v6
 mode='sdk' if env.num_envs==10 else 'native' if controls==144 else 'fullrestore'
 readback=auditor.finish_physical_controls(controls,mode)
 original=original_end(env,O,write,source,controls,ground_error,height_error,initial_birth)
 phase=auditor.final_phase_receipt()
 result=dict(original)
 result.update(actual_substep_readback_V6=readback,actual_post_probe_reset_cache_phase_V6=phase,all_env_substep_contact_integral_COM_hardware_checked=True)
 write('PROBE_D0D7_GEOMETRY_COMMAND_AND_SUBSTEP_CONTRACT_V6_ACTUAL.json',result)
 return result
