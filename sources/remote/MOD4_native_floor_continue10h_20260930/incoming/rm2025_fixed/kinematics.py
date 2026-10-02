"""Closed-loop reset coordinates relative to the repaired neutral assembly."""
import json
from pathlib import Path
import numpy as np
import mujoco
from kinematics_reference import leg_configuration as _reference

PARAMS=json.loads((Path(__file__).parent/'model_parameters.json').read_text())

def leg_configuration(hip,difference):
    vals,points=_reference(hip+PARAMS['neutral_hip_offset'],difference+PARAMS['neutral_difference_offset'])
    return {k:v-PARAMS['joint_offsets'][k] for k,v in vals.items()},points

def set_configuration(model,data,left=(0.,0.),right=(0.,0.),check_limits=True):
    for side,active in [('left',left),('right',right)]:
        vals,_=leg_configuration(*active)
        if check_limits:
            lo,hi=PARAMS['limits'][side]['input_difference_rad']
            if not lo-1e-8<=active[1]<=hi+1e-8:raise ValueError('Input difference exceeds CAD-safe branch.')
        for name,value in vals.items():
            j=model.joint(side+'_'+name)
            if check_limits and model.jnt_limited[j.id]:
                lo,hi=model.jnt_range[j.id]
                if not lo-1e-8<=value<=hi+1e-8:raise ValueError(f'{j.name} outside limits')
            data.qpos[j.qposadr[0]]=value
    mujoco.mj_forward(model,data)
