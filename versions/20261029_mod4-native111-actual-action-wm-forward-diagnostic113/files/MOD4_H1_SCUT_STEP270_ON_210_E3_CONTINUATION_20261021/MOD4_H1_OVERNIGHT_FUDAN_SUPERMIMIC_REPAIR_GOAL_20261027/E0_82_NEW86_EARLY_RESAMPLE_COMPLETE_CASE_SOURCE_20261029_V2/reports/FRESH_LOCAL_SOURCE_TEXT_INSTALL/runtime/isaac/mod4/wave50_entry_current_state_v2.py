"""Strict original G4 state plus deterministic reset-entry disk identity."""
from pathlib import Path
import hashlib,torch
import g4_current_state as old
from wave50_entry_v1_math import PROFILE as ENTRY_PROFILE
PROFILE='mod4_G4_CAD_derived_50mm_entry_v1'
KEY='E1_WAVE50_entry_reset_identity'
def validate(state,n):
 assert state['profile']==PROFILE and state['entry_profile']==ENTRY_PROFILE
 for k in ('entry_map_sha256','entry_origin_sha256','entry_assignment_sha256','entry_input_sha256','entry_math_sha256','entry_runtime_sha256','entry_full_pose_sha256'):
  assert isinstance(state[k],str) and len(state[k])==64
 assert state['entry_assignment_sha256'] and state['entry_origin_cache_bound'] and state['entry_reset_XY_only'] and state['entry_no_new_RNG']
 old.validate(dict(state,profile=old.PROFILE),n)
def extend(state,receipt):
 A=Path(__file__).resolve().parent
 s=dict(state,profile=PROFILE,entry_profile=ENTRY_PROFILE,entry_map_sha256=receipt['map_sha256'],
  entry_origin_sha256=receipt['actual_origin_sha256'],entry_assignment_sha256=receipt['actual_assignment_sha256'],entry_input_sha256=receipt['actual_input_identity_sha256'],
  entry_math_sha256=receipt['math_sha256'],entry_runtime_sha256=hashlib.sha256((A/'wave50_entry_runtime_v2.py').read_bytes()).hexdigest(),
  entry_full_pose_sha256=receipt['full_pose_reset_sha256'],entry_origin_cache_bound=True,entry_reset_XY_only=True,entry_no_new_RNG=True)
 assert s['G4_profile_sha256']==receipt['geometry_profile_sha256'] and s['reset_bank_sha256']==receipt['complete_bank_sha256']
 validate(s,state['num_envs']);return s
def current_state(env):
 from wave50_entry_runtime_v2 import reset_entry_xy
 reset_entry_xy(env,torch.arange(env.num_envs,device=env.device))
 return extend(old.current_state(env),env._wave50_entry_map_receipt)
def identity(state):return old.identity(state)
def validate_complete_entry(ck,n):
 s=ck['E1_terrain_state'];validate(s,n);assert ck[KEY]==identity(s)
 assert hashlib.sha256(s['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==s['entry_map_sha256']
 assert ck['E1_retained_flat_command_state']['assignment_sha256']==s['entry_assignment_sha256']
