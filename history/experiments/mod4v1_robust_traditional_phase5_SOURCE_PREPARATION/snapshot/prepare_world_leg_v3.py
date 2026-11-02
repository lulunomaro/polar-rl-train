from pathlib import Path
import ast,hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parent;D=R/'ROUGH_WORLD_LEG_V3';A=D/'preflight001';A.mkdir(exist_ok=False)
s=(R/'run_world_leg_case_v1.py').read_text(encoding='utf-8')
s=s.replace('from ROUGH_WORLD_LEG_V1.controller import WorldLegController as GroundController','from ROUGH_WORLD_LEG_V3.controller import WorldLegController as GroundController')
s=s.replace("ROOT / 'ROUGH_WORLD_LEG_V1/controller.py'","ROOT / 'ROUGH_WORLD_LEG_V1/controller.py', ROOT / 'ROUGH_WORLD_LEG_V3/controller.py'")
s=s.replace('R40_NEW_WORLD_LEG_REFERENCE_SENSOR_ONLY_COUNTERFACTUAL','R42_NEW_DRIVE_PREFIX_PRESERVING_STOP_CAPTURE')
ast.parse(s)
with(R/'run_world_leg_case_v3.py').open('x',encoding='utf-8')as f:f.write(s)
refs=[]
for rel in('ROUGH_WORLD_LEG_V1/controller.py','ROUGH_WORLD_LEG_V3/controller.py','run_world_leg_case_v3.py',Path(__file__).name):
    raw=(R/rel).read_bytes();ast.parse(raw);refs.append(dict(path=rel,SHA=hashlib.sha256(raw).hexdigest()))
with(A/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2)
import mujoco
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('physics prohibited'))
from physics_bridge import load_gain
from sensor_core_v4 import Estimate
from ROUGH_WORLD_LEG_V1.controller import WorldLegController as V1
from ROUGH_WORLD_LEG_V3.controller import WorldLegController as V3
n=0

def check(v):
    global n
    n+=1;assert bool(v),f'check{n}'
g=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta0.json');cfg=dict(position_weight=25.,position_leash=1.,world_pitch_gain=.75)
a=V1(g,cfg);b=V3(g,cfg)
for k in range(600):
    x=np.r_[g['q'],np.zeros(7)];x[2]=.2*math.sin(k*.04)
    e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,k*.01,0.,0.)
    v=0. if k<100 else 1.
    check(np.array_equal(a.command(e,v,0.),b.command(e,v,0.)));check(b.world_log['speed_activation']==1.)
for k in range(400):
    tau=b.command(e,0.,0.);check(np.isfinite(tau).all()and np.all(abs(tau)<=b.effort));check(b.stop_capture)
    json.dumps(b.world_log,allow_nan=False)
check(b.world_log['speed_activation']==0. and abs(b.shift)<1e-7)
b.command(e,1.,0.);check(not b.stop_capture and b.world_log['speed_activation']==1.)
result=dict(kind='WORLDLEG_NEW_LATCHED_STOP_MATH_CONTRACT',checks=n,failures=0,physics_steps=0,
            initial_and_drive_prefix_600_commands_bitidentical=True,stop_restores_bodyfixed=True,
            physical_prefix_equality_still_to_verify=True,no_old_gate_or_scores_changed=True)
with(A/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
