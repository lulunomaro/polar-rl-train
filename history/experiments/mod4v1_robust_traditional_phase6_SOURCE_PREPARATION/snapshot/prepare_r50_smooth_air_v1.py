"""New TRAIN flight-reference hypothesis from R49 contact/rebound evidence.
Original H5/V3/driver source is read-only. This admission performs no integration.
"""
from pathlib import Path
import ast,copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MINIHOP_AIR_RETRACT_V4';A=D/'preflight001';A.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
old=R/'run_manual_first_bar_v1.py';new=R/'run_manual_air_retract_v2.py';assert not new.exists()
s=old.read_text(encoding='utf-8')
s=s.replace('from MINIHOP_LANDING_V3.controller import MiniHop','from MINIHOP_AIR_RETRACT_V4.controller import MiniHop')
s=s.replace('from MANUAL_FIRST_BAR_V1.grade_rows import BoundsRows','from MANUAL_FIRST_BAR_V1.grade_rows_v2 import BoundsRows')
s=s.replace('controller_equations_unchanged=True','controller_equations_unchanged=False')
s=s.replace("file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py')]","file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py'),file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows_v2.py'),file_record(ROOT/'MINIHOP_AIR_RETRACT_V4/controller.py')]")
s=s.replace("clean_air_both_main_rear_crossing_bar_back_s=physical.clean_air_main_rear_crossing_s,","some_operational_air_main_rear_crossing_s=physical.clean_air_main_rear_crossing_s,\n            first_flight_main_rear_crossing_bar_back_s=physical.first_flight_main_rear_crossing_s,")
s=s.replace('NEW_MANUAL_LOCAL_FIRST_BAR_MOVING_HOP_TRAIN','NEW_SMOOTH_AIR_LOCAL_MOVING_HOP_TRAIN')
s=s.replace('NEW_MANUAL_FIRST_BAR_MOVING_HOP_TRAIN','NEW_SMOOTH_AIR_REFERENCE_MOVING_HOP_TRAIN')
s=s.replace('Reuses frozen V3 hop/observer and v2 force audit. Only forward/stop/operator\nconfiguration is new.','New smooth-air subclass; original V3/observer and v2 force audit remain read-only.\nForward/stop/operator configuration and flight position-reference schedule are new.')
ast.parse(s);new.write_text(s,encoding='utf-8')
files=[new,R/'MINIHOP_AIR_RETRACT_V4/controller.py',R/'MANUAL_FIRST_BAR_V1/grade_rows_v2.py',old,R/'MINIHOP_LANDING_V3/controller.py',R/'MINIHOP_OBSERVER_V2/controller.py',R/'MINIHOP_V1/controller.py']
dump(A/'SOURCE_PREEXEC.json',dict(files=[dict(path=str(p),SHA=sha(p))for p in files],preparer_SHA=sha(Path(__file__)),physics_steps=0))
origstep=mujoco.mj_step;calls=0

def forbid(*a,**k):
    global calls;calls+=1;raise AssertionError('Admission must not integrate')
mujoco.mj_step=forbid
try:
    from run_manual_air_retract_v2 import arrays,load_landing_gain,BoundsRows
    from physics_bridge import geometry,load_gain
    from MINIHOP_AIR_RETRACT_V4.controller import MiniHop
    from MINIHOP_LANDING_V3.controller import MiniHop as Old
    from rm_grid_terrain_v1 import configure
    from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant
    prev=json.loads((R/'MANUAL_FIRST_BAR_V1/long_runway002/PROTOCOL.json').read_bytes())
    cfg=copy.deepcopy(next(c for n,c in prev['configs']if n=='r49_long_flat_t210'))
    cfg.update(case_id='r50_smooth_flat',brake_at_s=2.7,cohort='NEW_SMOOTH_AIR_TRAIN_NOT_H5');cfg['hop'].update(smooth_air_retraction_enable=True,air_retraction_s=.16)
    rm=copy.deepcopy(cfg);rm.update(case_id='r50_smooth_rm6',scene='rm',terrain_seed=9001,terrain_difficulty=1.)
    dump(D/'PROTOCOL.json',dict(kind='NEW_SMOOTH_AIR_TRAIN_FIRST_BAR',configs=[(cfg['case_id'],cfg),(rm['case_id'],rm)],max_workers=1,
        hypothesis='quintic .16s position-only retraction replaces abrupt air reference; no new velocity FF or guard relaxation',
        braking='2.7s instead3s solely to scope stop before secondbar; first-flight and postlanding air diagnostics separated',
        flat_admission_before_RM=True,acceptance_unchanged_from_manual_first_bar=True,H5_read_for_tuning=False,PH6_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);end=load_gain(R/cfg['end_gain_file']);landing=load_landing_gain(cfg['landing_gain']);g=geometry();g.radius=.0625
    x=np.r_[start['q'],np.zeros(7)];x[7]=.8;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
    packet=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4))
    checks=0;changed_flight_ticks=0;max_ref_step=0.
    for enabled in(False,True):
        c=copy.deepcopy(cfg['hop']);c['smooth_air_retraction_enable']=enabled
        a=MiniHop(start,end,g,c,landing_gain=landing);b=Old(start,end,g,c,landing_gain=landing);previous_target=None
        for k in range(800):
            t=k*.01;cmd=1. if t<2.7 else 0.;a.prepare_estimator(types.SimpleNamespace(),t);b.prepare_estimator(types.SimpleNamespace(),t)
            ua=a.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd);ub=b.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd)
            assert np.isfinite(ua).all()and not a.fault;checks+=1
            flight=a.log.get('phase')=='predicted_flight_retract'
            if not enabled or not flight:assert np.array_equal(ua.view(np.uint64),ub.view(np.uint64));checks+=1
            elif not np.array_equal(ua.view(np.uint64),ub.view(np.uint64)):changed_flight_ticks+=1
            if enabled and flight:
                q=np.asarray(a.log['target_q4']);assert np.isfinite(q).all();checks+=1
                if previous_target is not None:max_ref_step=max(max_ref_step,float(np.max(np.abs(q-previous_target))))
                previous_target=q.copy()
                for side,z in(('left',q[:2]),('right',q[2:])):
                    r,v,J,aux=g.wheel_kinematics(float(z[0]),float(z[1]),0.,0.,0.,np.zeros(3),side)
                    assert np.isfinite(r).all()and np.isfinite(J).all();checks+=1
        assert np.array_equal(a.q_start.view(np.uint64),b.q_start.view(np.uint64));checks+=1
    assert changed_flight_ticks>0
    configure(9001,1.);p=MiniHopAuditPlant(False);p.reset(start['symmetric'],.1);rows=BoundsRows(A/'static_classifier_only.jsonl');rows.bind(p)
    assert p.tick_phys==0;checks+=1
    rows.first_bar=dict(back_x_m=-1.)
    rows.append(dict(stage_time_s=0.,air_qualified=True,synthetic_static_classifier_fixture=True))
    assert rows.first_flight_main_rear_crossing_s==0.;checks+=1
    rows.first_flight_main_rear_crossing_s=None;p.first_landing=dict(synthetic=True)
    rows.append(dict(stage_time_s=0.,air_qualified=True,synthetic_static_classifier_fixture=True))
    assert rows.first_flight_main_rear_crossing_s is None;checks+=1
    assert calls==0
    dump(A/'RESULT.json',dict(status='PASS_NEW_SMOOTH_AIR_ZERO_STEP_ADMISSION',checks=checks,integrator_calls=calls,new_physics_steps=0,
        synthetic_comparison_ticks=1600,changed_flight_ticks=changed_flight_ticks,disabled_and_nonflight_tau_bits_exact=True,
        max_flight_reference_step_rad=max_ref_step,original_qstart_restored=True,new_firstflight_not_rebound_classifier_checked=True,
        velocity_reference_used='still zero; no trajectory derivative FF',guards_unchanged=True))
    print(json.dumps(dict(status='PASS_NEW_SMOOTH_AIR_ZERO_STEP_ADMISSION',checks=checks,changed_flight_ticks=changed_flight_ticks,max_flight_reference_step_rad=max_ref_step,integrator_calls=calls),indent=2))
except BaseException:
    (A/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=origstep
