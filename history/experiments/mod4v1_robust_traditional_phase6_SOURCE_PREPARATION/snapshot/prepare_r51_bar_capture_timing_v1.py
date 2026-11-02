"""New bar-specific timed landing preparation from R49 TRAIN, not H5.
Two predeclared RM nominal profiles. No source/guard/DR/model weakening.
"""
from pathlib import Path
import ast,copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_BAR_CAPTURE_TIMING_V1';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
s=(R/'run_manual_air_retract_v2.py').read_text(encoding='utf-8')
s=s.replace('from MINIHOP_AIR_RETRACT_V4.controller import MiniHop','from MINIHOP_LANDING_V3.controller import MiniHop')
s=s.replace(",file_record(ROOT/'MINIHOP_AIR_RETRACT_V4/controller.py')",'')
s=s.replace('controller_equations_unchanged=False','controller_equations_unchanged=True')
s=s.replace('NEW_SMOOTH_AIR_REFERENCE_MOVING_HOP_TRAIN','NEW_BAR_SPECIFIC_TIMED_CAPTURE_TRAIN').replace('NEW_SMOOTH_AIR_LOCAL_MOVING_HOP_TRAIN','NEW_BAR_SPECIFIC_TIMED_CAPTURE_TRAIN')
s=s.replace('New smooth-air subclass; original V3/observer and v2 force audit remain read-only.\nForward/stop/operator configuration and flight position-reference schedule are new.','Frozen V3/observer and v2 force audit remain read-only.\nBar-specific capture time and stop/operator configuration are new.')
runner=R/'run_manual_capture_v3.py';assert not runner.exists();ast.parse(s);runner.write_text(s,encoding='utf-8')
src=[runner,R/'MINIHOP_LANDING_V3/controller.py',R/'MINIHOP_OBSERVER_V2/controller.py',R/'MINIHOP_V1/controller.py',R/'MANUAL_FIRST_BAR_V1/grade_rows.py',R/'MANUAL_FIRST_BAR_V1/grade_rows_v2.py']
dump(D/'SOURCE_PREEXEC.json',dict(files=[dict(path=str(p),SHA=sha(p))for p in src],preparer_SHA=sha(Path(__file__)),physics_steps=0))
old=mujoco.mj_step;calls=0

def no_step(*a,**k):
    global calls;calls+=1;raise AssertionError('Zero-step admission')
mujoco.mj_step=no_step
try:
    from run_manual_capture_v3 import arrays,load_landing_gain,MiniHop
    from physics_bridge import geometry,load_gain
    prev=json.loads((R/'MANUAL_FIRST_BAR_V1/long_runway002/PROTOCOL.json').read_bytes())
    base=copy.deepcopy(next(c for n,c in prev['configs']if n=='r49_long_rm_t210'));base.update(brake_at_s=2.7,cohort='NEW_BAR_SPECIFIC_CAPTURE_TRAIN_NOT_H5')
    cases=[]
    for name,air in(('r51_bar_air180',.18),('r51_bar_air250',.25)):
        c=copy.deepcopy(base);c['case_id']=name;c['hop']['predicted_air_after_push_s']=air;cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='NEW_BAR_SPECIFIC_CAPTURE_TIMING_TRAIN',configs=cases,max_workers=2,
        source_hypothesis='R49 TRAIN bar-top touchdown2.4955 then guideground2.507 precede oldcapture2.59; earlier manual timed stance preparation',
        planned_capture_boundaries_s=[2.42,2.49],observer_nominal_boundary_s=2.74,actual_100Hz_ticks_may_differ_due_float_boundary=True,
        guards_unchanged=True,original_V3_reference_and_gains=True,
        no_smooth_air_retraction=True,stop_at_s=2.7,not_contact_FSM=True,
        admission='real loader/typed synthetic and prior geometry/driver boot; bar-specific landing height profile directly tested on RM, not requiring same-time flat gate',
        scope='two nominal LOCAL first6cmbar tests only; no wholeRM/270mm/independentDR/hardware',H5_not_read_or_retuned=True,PH6_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    x=np.r_[start['q'],np.zeros(7)];x[7]=.8;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
    packet=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4))
    checks=0;seen=[]
    for name,c in cases:
        h=MiniHop(start,end,g,c['hop'],landing_gain=landing)
        for k in range(800):
            t=k*.01;est=types.SimpleNamespace();h.prepare_estimator(est,t);u=h.command(e,packet,t,np.array([1.,0.,0.,0.]),1. if t<2.7 else 0.)
            assert np.isfinite(u).all()and not h.fault;checks+=1
            if 2.42<=t<2.74:assert est.wheel_measurement_enabled is False and est.ground_kinematic_constraint_enabled is False;checks+=1
        assert h.captured and h.landing_weight==1.;checks+=1;seen.append(dict(case=name,capture_started_s=h.capture_started_s))
    assert calls==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_BAR_CAPTURE_TIMING',checks=checks,integrator_calls=calls,new_physics_steps=0,
        synthetic_command_calls=1600,capture_times=seen,guards_unchanged=True,contact_confidence_not_promoted=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_BAR_CAPTURE_TIMING',checks=checks,integrator_calls=calls,capture_times=seen),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
