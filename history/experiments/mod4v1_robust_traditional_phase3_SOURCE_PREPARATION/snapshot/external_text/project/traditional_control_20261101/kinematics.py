"""Continuous-branch MOD4 reset poses. Angles are relative to packaged neutral."""
from pathlib import Path
import json
import numpy as np
import mujoco
ROOT=Path(__file__).parent
PARAMS=json.loads((ROOT/'model_parameters.json').read_text(encoding='utf8'))
MANIFEST=json.loads((ROOT/'reports/model_manifest.json').read_text(encoding='utf8'))
PINS={s:{k:np.array(v) for k,v in p.items()} for s,p in MANIFEST['neutral_skeleton_xz_m'].items()}

def rotate(v,q):
    c,s=np.cos(q),np.sin(q);return np.array([[c,s],[-s,c]])@v
def angle(v,w):
    q=-(np.arctan2(w[1],w[0])-np.arctan2(v[1],v[0]));return (q+np.pi)%(2*np.pi)-np.pi
def intersect(a,ra,b,rb,sign):
    length=np.linalg.norm(b-a)
    if not abs(ra-rb)+1e-7<length<ra+rb-1e-7:raise ValueError('Linkage singularity or unreachable pose')
    t=(ra*ra-rb*rb+length*length)/(2*length);h=np.sqrt(ra*ra-t*t)
    x=(b-a)/length;y=np.array([-x[1],x[0]]);return a+t*x+sign*h*y

def leg_configuration(hip,difference,side='left'):
    p=PINS[side];L=lambda a,b:np.linalg.norm(p[a]-p[b]);cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
    q={k:rotate(v,hip) for k,v in p.items()};q['A']=rotate(p['A'],hip+difference)
    q['B']=intersect(q['A'],L('A','B'),q['P'],L('B','P'),np.sign(cross(p['P']-p['A'],p['B']-p['A'])))
    rocker=angle(p['B']-p['P'],q['B']-q['P']);q['C']=q['P']+rotate(p['C']-p['P'],rocker)
    q['D']=intersect(q['K'],L('K','D'),q['C'],L('C','D'),np.sign(cross(p['C']-p['K'],p['D']-p['K'])))
    shin=angle(p['D']-p['K'],q['D']-q['K'])
    for key in ['W','T']:q[key]=q['K']+rotate(p[key]-p['K'],shin)
    vals={'hip':hip,'crank':hip+difference,'rocker_pin':rocker-hip,
          'coupler_pin':angle(p['B']-p['A'],q['B']-q['A'])-hip-difference,'knee':shin-hip,
          'distal_pin':angle(p['D']-p['C'],q['D']-q['C'])-rocker,
          'gas_pin':angle(p['T']-p['S'],q['T']-q['S'])-hip,
          'gas_slide':np.linalg.norm(q['T']-q['S'])-L('T','S'),
          'drive_hip_spin':hip,'drive_input_spin':hip+difference,'wheel_spin':0.}
    for name in ['rocker_pin','coupler_pin','knee','distal_pin','gas_pin']:vals[name]=(vals[name]+np.pi)%(2*np.pi)-np.pi
    return vals,q

def set_configuration(model,data,left=(0.,0.),right=(0.,0.),check_limits=True):
    for side,active in [('left',left),('right',right)]:
        if check_limits:
            lo,hi=PARAMS['limits'][side]['input_difference_rad']
            if not lo-1e-8<=active[1]<=hi+1e-8:raise ValueError('Input difference exceeds MOD4 operating envelope')
        values,_=leg_configuration(*active,side=side)
        for name,value in values.items():
            joint=model.joint(side+'_'+name)
            if check_limits and model.jnt_limited[joint.id]:
                lo,hi=model.jnt_range[joint.id]
                if not lo-1e-8<=value<=hi+1e-8:raise ValueError(f'{joint.name}={value:g} outside [{lo:g}, {hi:g}]')
            data.qpos[joint.qposadr[0]]=value
    mujoco.mj_forward(model,data)
