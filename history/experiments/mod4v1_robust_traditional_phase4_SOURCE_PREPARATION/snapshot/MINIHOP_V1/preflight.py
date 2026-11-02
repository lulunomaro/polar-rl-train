"""New mini-hop math/schema admission: 0 physics, no previous trials replayed."""
from pathlib import Path
import ast,hashlib,json,sys
from types import SimpleNamespace
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));D=R/'MINIHOP_V1'/'preflight001';D.mkdir(exist_ok=False)
source=['MINIHOP_V1/controller.py','MINIHOP_V1/contact_grade.py','run_minihop_case_v1.py','physics_bridge_minihop_flat_v1.py','physics_bridge_minihop_rm_v1.py','MINIHOP_V1/preflight.py']
refs=[]
for name in source:
    raw=(R/name).read_bytes();ast.parse(raw);refs.append(dict(path=name,SHA=hashlib.sha256(raw).hexdigest()))
(D/'SOURCE_PREEXEC.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
import mujoco
original=mujoco.mj_step
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('mj_step prohibited'))
from physics_bridge import geometry,load_gain
from sensor_core_jump_v1 import Estimate,SensorPacket,StateEstimator
from MINIHOP_V1.controller import MiniHop,absolute_q,EFFORT
bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())
cv=lambda g:{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}
g=cv(bank['gains']['crouch']);geom=geometry();geom.radius=.0625;checks=0

def check(value):
    global checks
    checks+=1;assert bool(value),f'check {checks}'

def fixture(now=0.):
    x=np.r_[g['q'],np.zeros(7)]
    e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,now,0.,0.)
    p=SensorPacket(now,now,np.zeros(3),np.array([0.,0.,9.81]),absolute_q(g),np.zeros(4),np.zeros(2),np.zeros(6))
    return e,p

for delta in(0,20):
    end=load_gain(R/f'TALL_ROUGH_BANK_V1/gain_delta{delta}.json')
    for push in(.10,.14):
        h=MiniHop(g,end,geom,dict(operator_enable=True,push_for_s=push));fake_est=SimpleNamespace()
        seen=set()
        for k in range(231):
            now=k*.01;e,p=fixture(now);h.prepare_estimator(fake_est,now);tau=h.command(e,p,now,np.array([1.,0.,0.,0.]))
            check(tau.shape==(6,)and np.isfinite(tau).all()and np.all(np.abs(tau)<=EFFORT))
            check(not h.log['contact_or_flight_trusted']and not h.fault)
            json.dumps(h.log,allow_nan=False)
            if h.log['phase']=='timed_push':
                q=h.log['target_q4']
                for j,s in enumerate(('left','right')):check(np.isfinite(geom.pose(q[2*j],q[2*j+1],s)[0]).all())
            seen.add(h.log['phase'])
        check(seen=={'supported_approach','timed_push','predicted_flight_retract','timed_capture'})
        check(h.launched and h.captured)
end=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta0.json')
h=MiniHop(g,end,geom,{})
for k in range(231):
    e,p=fixture(k*.01);h.prepare_estimator(fake_est,k*.01);tau=h.command(e,p,k*.01,np.array([1.,0.,0.,0.]))
    check(h.log['phase']=='supported_approach'and not h.launched and fake_est.wheel_measurement_enabled)
for bad in('old','negative_age','nan_age','nan_state','q_shape','bad_attitude','missed_trigger','pitch_guard','rollback','gap'):
    h=MiniHop(g,end,geom,dict(operator_enable=True));e,p=fixture();now=0.;q=np.array([1.,0.,0.,0.])
    if bad=='old':e.sensor_age_s=.06
    elif bad=='negative_age':e.sensor_age_s=-.01
    elif bad=='nan_age':e.sensor_age_s=float('nan')
    elif bad=='nan_state':e.state14[7]=float('nan')
    elif bad=='q_shape':p=SensorPacket(0.,0.,p.gyro_body,p.accel_proper_body,np.zeros(3),p.joint_vel4,p.wheel_vel2)
    elif bad=='bad_attitude':q[:]=0.
    elif bad=='missed_trigger':now=2.
    elif bad=='pitch_guard':now=1.5;e.state14[2]=.2
    elif bad in('rollback','gap'):
        h.command(e,p,0.,q);now=0. if bad=='rollback'else .1
    tau=h.command(e,p,now,q);check(h.fault and np.array_equal(tau,np.zeros(6)))
    e,p=fixture(now+.01);check(np.array_equal(h.command(e,p,now+.01,np.array([1.,0.,0.,0.])),np.zeros(6)))
# Real full-model boot namespace test; mj_step still forbidden.
from physics_bridge_minihop_flat_v1 import MiniHopAuditPlant
p=MiniHopAuditPlant(False);p.reset(g['symmetric'],0.)
est=StateEstimator(geom,p.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.)
h=MiniHop(g,end,geom,dict(operator_enable=True));h.prepare_estimator(est,0.);packet=p.sensor_packet();e=est.update(packet)
check(np.isfinite(h.command(e,packet,0.,est.q)).all());check(p.tick_phys==0 and len(p.audit)==0)
result=dict(kind='MINIHOP_NEW_MATH_PROFILE_AND_MODEL_BOOT_PRECHECK',checks=checks,failures=0,physics_steps=0,old_trial_scores_updated=False,
            operator_default_disabled=True,contact_confidence_promoted=False,actual_trajectory_not_tested=True)
(D/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');mujoco.mj_step=original;print(json.dumps(result,indent=2))
