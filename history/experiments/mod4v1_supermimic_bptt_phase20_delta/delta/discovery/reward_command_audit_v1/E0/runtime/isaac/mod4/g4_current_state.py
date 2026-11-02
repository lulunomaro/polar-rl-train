import hashlib
import e1_terrain_checkpoint as old
PROFILE='mod4_G4_CAD_derived_50mm_v1'
def validate(state, n):
    assert state['profile'] == PROFILE and state['G4_height_peak_to_trough_m'] == 0.05
    assert len(state['G4_profile_sha256']) == 64 and state['G4_is_derived_not_real_RM70mm']
    copy = dict(state, profile='mod4_intro_gentle_v1')
    return old.validate(copy, n)
def current_state(env):
    from g4_cad_wave_geometry import PROFILE as path
    state = old.current_state(env)
    state.update(profile=PROFILE, G4_height_peak_to_trough_m=0.05, G4_profile_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), G4_is_derived_not_real_RM70mm=True)
    validate(state, env.num_envs)
    return state
def identity(state):
    return old.identity(state)
