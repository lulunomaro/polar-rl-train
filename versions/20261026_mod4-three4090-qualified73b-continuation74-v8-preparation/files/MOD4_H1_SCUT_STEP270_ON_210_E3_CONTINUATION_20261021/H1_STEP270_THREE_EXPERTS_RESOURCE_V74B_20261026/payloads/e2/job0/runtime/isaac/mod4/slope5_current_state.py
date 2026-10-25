"""Derived5degree slope identity; old full DR schema unchanged."""
import hashlib
import e1_terrain_checkpoint as original
from slope5_geometry import PROFILE as PROFILE_PATH,profile
PROFILE='mod4_SLOPE_derived5deg_2m_mirrored_v1'
def validate(state,n):
 assert state['profile']==PROFILE and state['SLOPE_angle_deg']==5. and state['SLOPE_length_m']==2.
 assert state['SLOPE_no_vertical_riser'] and state['SLOPE_derived_not_actual_RM'] and len(state['SLOPE_profile_sha256'])==64
 assert abs(state['SLOPE_height_m']-profile()['height_m'])<1e-12
 return original.validate(dict(state,profile='mod4_intro_gentle_v1'),n)
def current_state(env):
 s=original.current_state(env);s.update(profile=PROFILE,SLOPE_angle_deg=5.,SLOPE_length_m=2.,SLOPE_height_m=profile()['height_m'],SLOPE_no_vertical_riser=True,SLOPE_derived_not_actual_RM=True,SLOPE_profile_sha256=hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest());validate(s,env.num_envs);return s
def identity(state):return original.identity(state)
