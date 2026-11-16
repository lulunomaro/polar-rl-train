"""Bilinear MOD4-specific ten-state gains; no upstream coefficient reuse."""
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
_TABLE=np.load(Path(__file__).resolve().parents[1]/'native_full_mjcf_gains.npz')
_GRID=_TABLE['grid']; N=len(_GRID)
_INTERP={k:RegularGridInterpolator((_GRID,_GRID),_TABLE[k].reshape(N,N,*_TABLE[k].shape[1:]),bounds_error=False,fill_value=None) for k in ('K','u_eq','equilibrium')}
def value(k,L_l,L_r):
 p=np.clip([L_l,L_r],_GRID[0],_GRID[-1]);return _INTERP[k](np.asarray([p]))[0]
def get_K(L_l,L_r):return value('K',L_l,L_r)
def get_e3(L_l,L_r):return tuple(value('equilibrium',L_l,L_r)[3:5])
def get_u_eq(L_l,L_r):return value('u_eq',L_l,L_r).reshape(4,1)
