"""R54 predeclared TRAIN trigger pair. No changed guard/gain/physics/gate.
R53 corner contact occurred in timed_push BEFORE first QUALIFIED20ms air;
that is not an assertion of simultaneous ground support. Advance takeoff plan.
"""
from pathlib import Path
import copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/takeoff_window005';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
oldD=R/'MANUAL_FIRST_BAR_V1/early_landing004';refs=json.loads((oldD/'SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
dump(D/'SOURCE_PREEXEC.json',dict(files=refs,preparer_SHA=sha(Path(__file__)),new_physics_steps=0))
old=mujoco.mj_step;calls=0

def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('No dynamics in R54 preparation')
mujoco.mj_step=forbidden
try:
    from run_manual_capture_v3 import arrays,load_landing_gain,MiniHop
    from physics_bridge import geometry,load_gain
    prior=json.loads((oldD/'PROTOCOL.json').read_bytes());base=copy.deepcopy(next(c for n,c in prior['configs']if n=='r53_air250_rm'))
    assert base['hop']['predicted_air_after_push_s']==.25
    cases=[]
    for label,trig in(('t190',1.9),('t195',1.95)):
        for scene in('flat','rm'):
            name=f'r54_{label}_{scene}';c=copy.deepcopy(base);c.update(case_id=name,scene=scene,cohort='R54_TAKEOFF_WINDOW_TRAIN_NOT_H5');c['hop']['trigger_time_s']=trig
            if scene=='flat':c.pop('terrain_seed',None);c.pop('terrain_difficulty',None)
            cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='R54_TAKEOFF_WINDOW_ORIGINAL_V3_TRAIN',configs=cases,max_workers=2,
        hypothesis='R53 TRAIN firstbar corner2.1355 in timed_push before firstqualified20msair2.1395, not a ground-support assertion. Advance only trigger2.0 to1.90/1.95 relative to air250 profile.',
        selection='air250 chosen after R53 TRAIN as lower observed peakpitch than air180 among equal nominal flatpass/RMfail. This rule was not preregistered before R53.',
        observed_guard_readiness='R53 TRAIN flat unchanged approach at1.9:estimatedpitch.01315/vx1.16670;1.95:.00631/1.16263, below originalguards. Not proof of future RM readiness.',
        original_controller_gains_and_guard=True,original_pred_air_s=.25,observer_quarantine_s=.5,
        start_x_m=.2,forward_m_s=.9,stop_at_s=2.5,flat_gate_before_matched_RM=True,
        geometry_contact_force_thresholds_not_weakened=True,no_H5_access_or_retuning=True,
        scope='nominal LOCAL first6cmbar TRAIN only; no robustwholeRM/270mm/hardware claim',PH6_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    x=np.r_[start['q'],np.zeros(7)];x[7]=.9;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
    packet=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4))
    checks=0;prefix=0;seen=[]
    for name,c in cases:
        if c['scene']!='flat':continue
        oldh=MiniHop(start,end,g,base['hop'],landing_gain=landing);h=MiniHop(start,end,g,c['hop'],landing_gain=landing)
        for k in range(300):
            t=k*.01;ea=types.SimpleNamespace();eb=types.SimpleNamespace();oldh.prepare_estimator(ea,t);h.prepare_estimator(eb,t)
            cmd=.9 if t<2.5 else 0.;a=oldh.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd);b=h.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd)
            assert np.isfinite(b).all()and not h.fault;checks+=1
            if t<1.9:
                assert np.array_equal(np.asarray(a,np.float64).view(np.uint64),np.asarray(b,np.float64).view(np.uint64))and vars(ea)==vars(eb);checks+=1;prefix+=1
        assert h.captured and h.landing_weight==1. and h.c['max_trigger_speed_m_s']==1.2;checks+=1
        seen.append(dict(case=name,capture_tick_s=h.capture_started_s))
    assert calls==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R54_WINDOW',checks=checks,integrator_calls=calls,new_physics_steps=0,
        new_profile_synthetic_commands=600,prefix_before1p9s_commands_bitmatch=prefix,capture_times=seen,no_dynamic_pass_claim=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_R54_WINDOW',checks=checks,integrator_calls=calls,capture_times=seen),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
