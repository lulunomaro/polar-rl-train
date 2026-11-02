"""New observer-only overlay, all plant/actuator/grade code remains sealed V2."""
from pathlib import Path
import ast,hashlib,json,sys
import numpy as np
from types import SimpleNamespace
R=Path(__file__).resolve().parent;D=R/'MINIHOP_OBSERVER_V2';A=D/'preflight001';A.mkdir(exist_ok=False)
s=(R/'MINIHOP_AUDIT_V2/run_minihop_case_v2.py').read_text(encoding='utf-8')
s=s.replace("sys.path.insert(0,str(Path(__file__).resolve().parents[1]))","sys.path.insert(0,str(Path(__file__).resolve().parent))")
s=s.replace('from MINIHOP_V1.controller import MiniHop','from MINIHOP_OBSERVER_V2.controller import MiniHop')
s=s.replace('from MINIHOP_AUDIT_V2.provenance_v2 import source_manifest,error_receipt',
'''from MINIHOP_AUDIT_V2.provenance_v2 import source_manifest as base_manifest,error_receipt,file_record

def source_manifest(scene,cfg):
    result=base_manifest(scene,cfg)
    result.update(kind='NEW_MINIHOP_WHEEL_OBSERVER_QUARANTINE_OVERLAY',controller_changed=True,
                  changed='wheel_and_ground_kinematic_observations_quarantined_longer_not_torque_phase',
                  torque_phase_math_and_plant_unchanged=True,contact_confidence_promoted=False)
    result['files'] += [file_record(Path(__file__).resolve()),file_record(ROOT/'MINIHOP_OBSERVER_V2/controller.py')]
    return result
''')
s=s.replace("kind='OPERATOR_TIMED_MINIHOP_TRAIN_NOT_CONTACT_FSM_RELEASE'","kind='NEW_OBSERVER_QUARANTINE_MINIHOP_TRAIN_NOT_CONTACT_FSM_RELEASE'")
ast.parse(s)
with(R/'run_minihop_observer_v2.py').open('x',encoding='utf-8')as f:f.write(s)
refs=[]
for rel in('MINIHOP_V1/controller.py','MINIHOP_OBSERVER_V2/controller.py','run_minihop_observer_v2.py',Path(__file__).name):
    raw=(R/rel).read_bytes();ast.parse(raw);refs.append(dict(path=rel,SHA=hashlib.sha256(raw).hexdigest()))
with(A/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2)
import mujoco
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('physics prohibited'))
from physics_bridge import geometry,load_gain
from sensor_core_jump_v1 import Estimate,SensorPacket
from MINIHOP_V1.controller import MiniHop as V1,absolute_q
from MINIHOP_OBSERVER_V2.controller import MiniHop as V2
bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())
g={k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in bank['gains']['crouch'].items()}
end=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta20.json');geo=geometry();geo.radius=.0625
n=0

def check(v):
    global n
    n+=1;assert bool(v),f'check{n}'
cfg=dict(operator_enable=True,push_for_s=.14,predicted_air_after_push_s=.35,observer_quarantine_after_push_s=.5)
a=V1(g,end,geo,cfg);b=V2(g,end,geo,cfg);ea=SimpleNamespace();eb=SimpleNamespace();differences=[]
for k in range(600):
    now=k*.01;a.prepare_estimator(ea,now);b.prepare_estimator(eb,now)
    x=np.r_[g['q'],np.zeros(7)];e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,now,0.,0.)
    p=SensorPacket(now,now,np.zeros(3),np.array([0.,0.,9.81]),absolute_q(g),np.zeros(4),np.zeros(2),np.zeros(6))
    ta=a.command(e,p,now,np.array([1.,0.,0.,0.]));tb=b.command(e,p,now,np.array([1.,0.,0.,0.]))
    check(np.array_equal(ta,tb));check(ea.accel_correction==eb.accel_correction)
    different=ea.wheel_measurement_enabled!=eb.wheel_measurement_enabled
    if different:differences.append(now)
    check(different==bool(1.99<=now<2.14));check(eb.wheel_measurement_enabled==eb.ground_kinematic_constraint_enabled)
    check(not b.log['contact_or_flight_trusted']);json.dumps(b.log,allow_nan=False)
check(len(differences)==15)
b=V2(g,end,geo,{})
for k in range(220):
    b.prepare_estimator(eb,k*.01);check(eb.wheel_measurement_enabled and eb.ground_kinematic_constraint_enabled and not b.quarantine_active)
result=dict(kind='NEW_WHEEL_OBSERVER_QUARANTINE_MATH_CONTRACT',checks=n,failures=0,physics_steps=0,
            torque_math_for_identical_estimates_bitmatch600=True,only_15_expected_observer_ticks_changed=True,
            gravity_correction_schedule_unchanged=True,operator_default_disabled=True,no_new_contact_permission=True)
with(A/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
