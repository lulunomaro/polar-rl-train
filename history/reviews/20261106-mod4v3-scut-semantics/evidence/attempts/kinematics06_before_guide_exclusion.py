"""MOD4 linkage solving with SCUT anatomical input/output coordinates."""
from functools import lru_cache
import importlib.util
from pathlib import Path
import numpy as np

from semantics import Semantics


@lru_cache(maxsize=1)
def _modules():
    root=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('_mod4v3_legacy_geometry',root/'legacy/kinematics_v2.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return Semantics(root),module


def mechanical_delta_bounds(side='left'):
    api,legacy=_modules()
    offsets=api.spec['coordinates']['native_from_v2']
    shift=offsets[side+'_front1_joint']['offset_si']-offsets[side+'_rear1_joint']['offset_si']
    return tuple(x+shift for x in legacy.mechanical_delta_bounds(side))


def leg_configuration(front1,rear1,*,side='left',check_limits=True):
    """Return all named SCUT leg angles for MOD4's actual closed linkage.

    Inputs are continuous anatomical front1 and rear1 angles, in radians. The
    original source solver handles its real limits, gas stroke and loop branch.
    """
    api,legacy=_modules()
    offsets=api.spec['coordinates']['native_from_v2']
    hip=rear1-offsets[side+'_rear1_joint']['offset_si']
    crank=front1-offsets[side+'_front1_joint']['offset_si']
    old_values,pins=legacy.leg_configuration(hip,crank,side=side,check_limits=check_limits)
    native=np.zeros(len(api.native_names))
    for i,n in enumerate(api.native_names):
        row=offsets[n]
        if n.startswith(side+'_') and row['source'].startswith(side+'_'):
            native[i]=old_values[row['source'][len(side)+1:]]+row['offset_si']
    semantic=api.positions(native)
    return {n:float(semantic[i])for i,n in enumerate(api.names)if n.startswith(side+'_')},pins


def set_configuration(model,data,*,left,right,check_limits=True):
    """Set both legs in v3 native simulation coordinates; root remains untouched."""
    api,_=_modules()
    for side,pair in [('left',left),('right',right)]:
        values,_=leg_configuration(*pair,side=side,check_limits=check_limits)
        semantic=np.zeros(len(api.names))
        for i,n in enumerate(api.names):
            if n in values:semantic[i]=values[n]
        native=api.native_positions(semantic)
        for i,n in enumerate(api.native_names):
            if n.startswith(side+'_') and '_guide_joint'not in n:
                data.qpos[model.joint(n).qposadr[0]]=native[i]
    import mujoco
    mujoco.mj_forward(model,data)
