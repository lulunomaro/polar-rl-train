"""Prepare new velocity-scheduled reference and math contract, 0 mj_step."""
from pathlib import Path
import ast,hashlib,json,sys,math
import numpy as np
R=Path(__file__).resolve().parent;D=R/'ROUGH_WORLD_LEG_V2';A=D/'preflight001';A.mkdir(exist_ok=False)
s=(R/'run_world_leg_case_v1.py').read_text(encoding='utf-8')
s=s.replace('from ROUGH_WORLD_LEG_V1.controller import WorldLegController as GroundController','from ROUGH_WORLD_LEG_V2.controller import WorldLegController as GroundController')
s=s.replace("ROOT / 'ROUGH_WORLD_LEG_V1/controller.py'","ROOT / 'ROUGH_WORLD_LEG_V1/controller.py', ROOT / 'ROUGH_WORLD_LEG_V2/controller.py'")
s=s.replace('R40_NEW_WORLD_LEG_REFERENCE_SENSOR_ONLY_COUNTERFACTUAL','R41_NEW_SCHEDULED_WORLD_LEG_SENSOR_ONLY_COUNTERFACTUAL')
ast.parse(s)
with(R/'run_world_leg_case_v2.py').open('x',encoding='utf-8')as f:f.write(s)
refs=[]
for rel in ('ROUGH_WORLD_LEG_V1/controller.py','ROUGH_WORLD_LEG_V2/controller.py','run_world_leg_case_v1.py','run_world_leg_case_v2.py',Path(__file__).name):
    raw=(R/rel).read_bytes();ast.parse(raw);refs.append(dict(path=rel,SHA=hashlib.sha256(raw).hexdigest()))
with(A/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2)
import mujoco
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('physics prohibited'))
from physics_bridge import load_gain
from sensor_core_v4 import Estimate
from ground_controller_v4 import GroundController
from ROUGH_WORLD_LEG_V1.controller import WorldLegController as V1
from ROUGH_WORLD_LEG_V2.controller import WorldLegController as V2
n=0

def check(x):
    global n
    n+=1;assert bool(x),f'check{n}'

def e_for(g,pitch=0.):return Estimate(np.r_[g['q'],np.zeros(7)]+np.r_[0.,0.,pitch,np.zeros(11)],0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,0.,0.,0.)
for delta in(0,20):
    g=load_gain(R/f'TALL_ROUGH_BANK_V1/gain_delta{delta}.json')
    cfg=dict(position_weight=25.,position_leash=1.,world_pitch_gain=0.)
    a=GroundController(g,cfg);b=V2(g,cfg)
    for k in range(100):
        e=e_for(g,.1*math.sin(k*.05));check(np.array_equal(a.command(e,1.,0.),b.command(e,1.,0.)))
    cfg['world_pitch_gain']=.75;a=V1(g,cfg);b=V2(g,cfg)
    a.shaper.v=b.shaper.v=1.
    for k in range(100):
        e=e_for(g,.1*math.sin(k*.05));check(np.array_equal(a.command(e,1.,0.),b.command(e,1.,0.)));check(b.world_log['speed_activation']==1.)
    b=V2(g,cfg);b.shaper.v=1.;old=0.
    for k in range(400):
        tau=b.command(e_for(g,.3),0.,0.)
        check(np.isfinite(tau).all()and np.all(abs(tau)<=b.effort))
        check(0.<=b.world_log['speed_activation']<=1. and abs(b.shift-old)<=.020000000001);old=b.shift
        check(np.array_equal(b.ref[[4,6]],b.eq[[4,6]]))
        json.dumps(b.world_log,allow_nan=False)
    check(abs(b.shift)<1e-7 and b.world_log['speed_activation']==0. and b.world_k==.75)
result=dict(kind='WORLDLEG_SPEED_SCHEDULE_NEW_MATH_CONTRACT',checks=n,failures=0,physics_steps=0,
            gain0_matches_original=True,at_full_speed_matches_v1=True,at_shaped_stop_returns_original_hip_target=True,
            dynamic_physics_unproven=True,acceptance_unchanged=True)
with(A/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
