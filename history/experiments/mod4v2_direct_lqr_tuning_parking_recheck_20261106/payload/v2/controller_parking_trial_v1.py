"""Opt-in MOD4v2 parking-priority LQR recipe from actual two-setting comparison.
Not a replacement for the formal default or hardware-qualified control.
Use actual v2 gain/geometry; R is re-solved by existing controller,not old K copied.
"""
from controller_heading_v2 import GroundController

# Exact baseline settings actually used by all compared cases (settings only,not old K).
BASE_CONFIG=dict(yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052,
                 position_weight=25.,position_leash=1.)

def build_controller(gain,config=None,*,geometry,profile='original'):
    c=dict(BASE_CONFIG)
    c.update(config or {})
    if profile=='parking_R4':
        c['effort_weight']=4.0
    elif profile!='original':
        raise ValueError('Choose original or parking_R4;rejected candidates are not exposed')
    return GroundController(gain,c,geometry=geometry)

# parking_R4: same Q/leg120-4/shaper/yaw/observer/PD-D4-DC;only R x4.
# Actual full-CAD low-speed stop RMS: .053773->.045809 and .065334->.054786m/s.
# Nominal flat +/-2m/s tracking was slightly worse than original;not a universal best.
# No root/contact/DR parameters in this module. Explicit supported initialization is
# handled by the existing simulator runtime,not natural-rise qualification.
