from pathlib import Path
import sys,json
import numpy as np
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from physics_bridge import geometry,load_gain
from MINIHOP_V1.controller import MiniHop as V1
from MINIHOP_OBSERVER_V2.controller import MiniHop as V2
bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes());g={k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in bank['gains']['crouch'].items()}
e=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta20.json');cfg=dict(operator_enable=True,push_for_s=.14,predicted_air_after_push_s=.35,observer_quarantine_after_push_s=.5)
a=V1(g,e,geometry(),cfg);b=V2(g,e,geometry(),cfg);rows=[]
for k in(198,199,200,213,214,215):
    t=k*.01;x=SimpleNamespace();y=SimpleNamespace();a.prepare_estimator(x,t);b.prepare_estimator(y,t)
    rows.append(dict(k=k,time_repr=repr(t),old_wheel_enabled=x.wheel_measurement_enabled,new_wheel_enabled=y.wheel_measurement_enabled,
                     old_gravity_gain=x.accel_correction,new_gravity_gain=y.accel_correction))
result=dict(kind='NEW_FLOAT_BOUNDARY_DIAGNOSTIC_NOT_PHYSICS',physics_steps=0,
 old_observer_end_repr=repr(a.trigger+a.push+a.air),new_observer_end_repr=repr(b.trigger+b.push+b.quarantine),rows=rows,
 prior_failure='preflight001 check998 expected hardcoded1p99 boundary; actual value not printed in failed run')
with(R/'MINIHOP_OBSERVER_V2/BOUNDARY_DIAGNOSTIC.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
