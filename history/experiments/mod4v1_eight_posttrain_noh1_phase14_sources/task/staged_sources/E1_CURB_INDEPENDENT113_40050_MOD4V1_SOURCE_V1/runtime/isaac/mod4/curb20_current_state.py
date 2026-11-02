"""New CURB geometry identity only; this module does not implement full resume."""
import hashlib
import e1_terrain_checkpoint as original
from curb20_geometry import PROFILE as PROFILE_PATH
PROFILE='mod4_CURB_derived20mm_strip150_mirrored_v1'
def validate(state,n):
    assert state['profile']==PROFILE and state['CURB_height_m']==.020
    assert state['CURB_strip_width_m']==.150 and state['CURB_vertical_unsmoothed']
    assert state['CURB_derived_not_actual_RM002'] and len(state['CURB_profile_sha256'])==64
    return original.validate(dict(state,profile='mod4_intro_gentle_v1'),n)
def current_state(env):
    s=original.current_state(env)
    s.update(profile=PROFILE,CURB_height_m=.020,CURB_strip_width_m=.150,
        CURB_vertical_unsmoothed=True,CURB_derived_not_actual_RM002=True,
        CURB_profile_sha256=hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest())
    validate(s,env.num_envs);return s
def identity(state):return original.identity(state)
