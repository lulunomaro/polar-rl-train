from pathlib import Path
import ast,hashlib,json,sys,math
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));D=R/'ROUGH_WORLD_LEG_V1'/'preflight001';D.mkdir(exist_ok=False)
paths=['ROUGH_WORLD_LEG_V1/controller.py','run_world_leg_case_v1.py','ROUGH_WORLD_LEG_V1/preflight.py']
source=[]
for name in paths:
    raw=(R/name).read_bytes();ast.parse(raw);source.append(dict(path=name,SHA=hashlib.sha256(raw).hexdigest()))
(D/'SOURCE_PREEXEC.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
# The initial derived PREPARATION hash preceded two result-label edits only.
(R/'ROUGH_WORLD_LEG_V1/PRE_EXEC_LABEL_ADDENDUM.json').write_text(json.dumps(dict(physics_steps=0,legacy_labels_corrected_before_first_physics=True,
    corrections=['R03 result kind -> R40','terrain flat label -> exact SCUT box family'],control_equations_unchanged=True,actual_runner_SHA=source[1]['SHA']),indent=2),encoding='utf-8')
from physics_bridge import geometry,load_gain
from ground_controller_v4 import GroundController
from ROUGH_WORLD_LEG_V1.controller import WorldLegController
from sensor_core_v4 import Estimate,rotation,quat_from_rpy
checks=0

def check(v):
    global checks
    checks+=1;assert bool(v),f'check {checks}'
geom=geometry()
for delta in(0,20):
    g=load_gain(R/f'TALL_ROUGH_BANK_V1/gain_delta{delta}.json')
    a=GroundController(g,dict(position_weight=25.,position_leash=1.));b=WorldLegController(g,dict(position_weight=25.,position_leash=1.,world_pitch_gain=0.))
    for k in range(100):
        x=np.r_[g['q'],np.zeros(7)];x[2]=.1*math.sin(k*.1);x[7]=.3*math.sin(k*.05)
        e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,k*.01,0.,0.)
        check(np.array_equal(a.command(e,1.,0.),b.command(e,1.,0.)))
    b=WorldLegController(g,dict(position_weight=25.,position_leash=1.,world_pitch_gain=.75))
    previous=0.
    for k in range(200):
        x=np.r_[g['q'],np.zeros(7)];x[2]=.8*math.sin(k*.03)
        e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,k*.01,0.,0.)
        tau=b.command(e,1.,0.);check(np.isfinite(tau).all()and np.all(np.abs(tau)<=b.effort))
        check(abs(b.shift)<=.30+1e-12 and abs(b.shift-previous)<=.02+1e-12);previous=b.shift
        check(np.array_equal(b.ref[[4,6]],b.eq[[4,6]])and np.all(abs(b.ref[[3,5]])<=.48))
        json.dumps(b.world_log,allow_nan=False)
    for pitch in(-.2,-.1,.1,.2):
        h=float(g['q'][3]);c=h+float(g['q'][4]);base,_=geom.pose(h,c,'left');comp,_=geom.pose(h-pitch,c-pitch,'left')
        check(np.max(np.abs(rotation(quat_from_rpy(0.,pitch,0.))@comp-base))<1e-10)
result=dict(kind='WORLD_LEG_REFERENCE_NEW_MATH_ONLY',checks=checks,failures=0,physics_steps=0,
            gain0_bitidentical_to_old_controller_on_200_synthetic_commands=True,delta_preserved=True,
            geometric_pure_counterrotation_test_only_not_dynamic_height_guarantee=True)
(D/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
