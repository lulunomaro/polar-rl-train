"""Original CURB geometry plus deterministic, origin-bound entry identity."""
from pathlib import Path
import hashlib
import curb20_current_state as old
PROFILE='mod4_CURB_derived20mm_strip150_mirrored_entryreset_v2_origin_bound_v1'
def validate(state,n):
 assert state['profile']==PROFILE
 old.validate(dict(state,profile=old.PROFILE),n)
 assert state['entry_reset_profile']=='CURB20_actual_cell_entry_reset_v2'
 assert state['entry_origin_bound_cache'] and state['entry_no_new_rng']
 for k in ('entry_map_sha256','entry_assignment_sha256','entry_runtime_sha256'):assert isinstance(state[k],str) and len(state[k])==64
def current_state(env):
 from curb20_entry_v3_runtime import reset_entry_xy
 import torch
 reset_entry_xy(env,torch.arange(env.num_envs,device=env.device))
 s=old.current_state(env);r=env._curb_entry_map_receipt
 s.update(profile=PROFILE,entry_reset_profile=r['profile'],entry_origin_bound_cache=True,entry_no_new_rng=True,entry_map_sha256=r['map_sha256'],entry_assignment_sha256=env.scene.terrain.retention_assignment_sha,entry_runtime_sha256=hashlib.sha256(Path(__file__).with_name('curb20_entry_v3_runtime.py').read_bytes()).hexdigest())
 validate(s,env.num_envs);return s
def identity(state):return old.identity(state)
