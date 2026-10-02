"""Analytic two-loop assembly, for consistent reset poses and topology audits."""
from pathlib import Path
import json
import numpy as np
import mujoco

MANIFEST=json.loads((Path(__file__).resolve().parent/'reports/reference_manifest.json').read_text(encoding='utf-8'))
P={k:np.array(v) for k,v in MANIFEST['neutral_skeleton_xz_m'].items()}
L=MANIFEST['measured_lengths_m']

def rotate(v,q):
    c,s=np.cos(q),np.sin(q)
    return np.array([[c,s],[-s,c]])@v

def angle(v,w):
    q=-(np.arctan2(w[1],w[0])-np.arctan2(v[1],v[0]))
    return (q+np.pi)%(2*np.pi)-np.pi

def intersect(a,ra,b,rb,near):
    d=np.linalg.norm(b-a)
    if not abs(ra-rb)+1e-8<d<ra+rb-1e-8:raise ValueError('Requested pose reaches a linkage singularity.')
    x=(ra*ra-rb*rb+d*d)/(2*d)
    h=np.sqrt(max(0,ra*ra-x*x))
    ex=(b-a)/d;ey=np.array([-ex[1],ex[0]])
    return min([a+x*ex+h*ey,a+x*ex-h*ey],key=lambda p:np.linalg.norm(p-near))

def leg_configuration(hip,difference):
    q={k:rotate(v,hip) for k,v in P.items()}
    q['A']=rotate(P['A'],hip+difference)
    q['B']=intersect(q['A'],L['AB'],q['P'],L['BPr'],q['B'])
    rocker=angle(P['B']-P['P'],q['B']-q['P'])
    q['C']=q['P']+rotate(P['C']-P['P'],rocker)
    q['D']=intersect(q['K'],L['KD'],q['C'],L['CD'],q['D'])
    shin=angle(P['D']-P['K'],q['D']-q['K'])
    q['W']=q['K']+rotate(P['W']-P['K'],shin)
    q['T']=q['K']+rotate(P['T']-P['K'],shin)
    vals={'hip':hip,'crank':hip+difference,'rocker_pin':rocker-hip,
          'coupler_pin':angle(P['B']-P['A'],q['B']-q['A'])-(hip+difference),
          'knee':shin-hip,'distal_pin':angle(P['D']-P['C'],q['D']-q['C'])-rocker,
          'gas_pin':angle(P['T']-P['S'],q['T']-q['S'])-hip,
          'gas_slide':np.linalg.norm(q['T']-q['S'])-np.linalg.norm(P['T']-P['S']),
          'drive_hip_spin':hip,'drive_input_spin':hip+difference,'wheel_spin':0.}
    # Passive joint angles need continuous relative branches; loop geometry does not depend on 2pi wrapping.
    for name in ['rocker_pin','coupler_pin','knee','distal_pin','gas_pin']:
        vals[name]=(vals[name]+np.pi)%(2*np.pi)-np.pi
    return vals,q

def set_configuration(model,data,left=(0.,0.),right=(0.,0.),check_limits=True):
    for side,active in [('left',left),('right',right)]:
        vals,_=leg_configuration(*active)
        for name,value in vals.items():
            joint=model.joint(side+'_'+name)
            if check_limits and model.jnt_limited[joint.id]:
                lo,hi=model.jnt_range[joint.id]
                if value<lo-1e-8 or value>hi+1e-8:raise ValueError(f'{side}_{name}={value:g} exceeds [{lo:g}, {hi:g}]')
            data.qpos[joint.qposadr[0]]=value
    mujoco.mj_forward(model,data)
