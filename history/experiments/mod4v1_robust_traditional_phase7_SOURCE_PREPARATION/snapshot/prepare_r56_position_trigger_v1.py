"""New manual odometry-scheduled TRAIN candidate; no holdout or physics replay.
Freeze new entry+controller then exercise actual loader and phase ordering.
"""
from pathlib import Path
import ast,copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MINIHOP_POSITION_TRIGGER_V1/preflight001';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
original=R/'run_manual_capture_v3.py';s=original.read_text(encoding='utf-8')
assert s.count('from MINIHOP_LANDING_V3.controller import MiniHop')==1
s=s.replace('from MINIHOP_LANDING_V3.controller import MiniHop','from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop')
s=s.replace('NEW_BAR_SPECIFIC_TIMED_CAPTURE_TRAIN','NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN')
s=s.replace('controller_equations_unchanged=True','controller_equations_unchanged=False,relative_V3_push_flight_capture_equations_unchanged=True')
s=s.replace('operator_timer_only=True','operator_timer_only=False,operator_relative_odometry_trigger=True')
s=s.replace("v['files'] += [file_record(Path(__file__)),","v['files'] += [file_record(ROOT/'MINIHOP_POSITION_TRIGGER_V1/controller.py'),file_record(Path(__file__)),")
s=s.replace('Bar-specific capture time and stop/operator configuration are new.','Manual relative odometry schedules a future trigger; phase durations and torque equations are V3.')
runner=R/'run_manual_position_v4.py';assert not runner.exists();ast.parse(s);runner.write_text(s,encoding='utf-8')
def control_loop(text):
    main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='main')
    return ast.dump(next(n for n in ast.walk(main)if isinstance(n,ast.For)and ast.unparse(n.iter)=='range(N)'),include_attributes=False)
assert control_loop(s)==control_loop(original.read_text(encoding='utf-8'))
refs=json.loads((R/'MANUAL_FIRST_BAR_V1/t195_DR_train006/SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA']
newfiles=[dict(path=str(p),SHA=sha(p))for p in(Path(__file__),runner,R/'MINIHOP_POSITION_TRIGGER_V1/controller.py')]
dump(D/'SOURCE_PREEXEC.json',dict(files=refs+newfiles,old_control_loop_AST_unchanged=True,new_physics_steps=0))
old=mujoco.mj_step;calls=0

def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('No physics in position scheduling admission')
mujoco.mj_step=forbidden
try:
    from run_manual_position_v4 import arrays,load_landing_gain,MiniHop
    from MINIHOP_LANDING_V3.controller import MiniHop as V3
    from MINIHOP_POSITION_TRIGGER_V1.controller import PositionScheduler
    from physics_bridge import geometry,load_gain
    base=json.loads((R/'results/r54_t195_rm/result.json').read_bytes())['config']
    c=copy.deepcopy(base);c['hop'].update(position_trigger_enable=True,position_trigger_distance_m=1.18,position_trigger_min_time_s=1.,position_trigger_deadline_s=2.6)
    cases=[]
    for scene in('flat','rm'):
        v=copy.deepcopy(c);name='r56_position_'+scene;v.update(scene=scene,case_id=name,cohort='R56_NEW_MANUAL_ODOMETRY_TRIGGER_TRAIN_NOT_HOLDOUT')
        if scene=='flat':v.pop('terrain_seed',None);v.pop('terrain_difficulty',None)
        cases.append((name,v))
    dump(D/'PROTOCOL.json',dict(kind='R56_MANUAL_POSITION_TRIGGER_TRAIN',configs=cases,max_workers=1,
        hypothesis='R55 at fixed1.95 has estimated distance4503=1.25725 vs nominal1.19403. Schedule from measured relative odometry instead of fixed elapsed time; no unique cause or future success assumed.',
        target_selection='1.18m chosen from nominal TRAIN sensor distance just before original1.95 trigger, with one tick decision-to-push delay; no true-root/DR cancellation or heldout fitting',
        not_autonomous_obstacle_or_contact_or_absolute_world_position=True,default_disabled=True,
        inherited_trigger_guards_unchanged=True,relative_push_flight_capture_and_observer_durations_unchanged=True,
        wheel_observation_phase='Legacy keeps wheel update during push, disables during predicted post-push quarantine; not changed here',
        success_gates_unchanged=True,flat_gate_before_matched_RM=True,H1_H2_H4_H5_frozen=True,PH7_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch'])
    end=load_gain(R/base['end_gain_file']);land=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    default=copy.deepcopy(base['hop']);default.pop('position_trigger_enable',None)
    oldh=V3(start,end,g,default,landing_gain=land);disabled=MiniHop(start,end,g,default,landing_gain=land)
    enabled=MiniHop(start,end,g,c['hop'],landing_gain=land)
    packet=types.SimpleNamespace(joint_pos4=np.array([start['q'][3],start['q'][3]+start['q'][4],start['q'][5],start['q'][5]+start['q'][6]]),joint_vel4=np.zeros(4))
    checks=0;disabled_match=0;enabled_match=0;phase_order={}
    for k in range(600):
        t=k*.01;x=np.r_[start['q'],np.zeros(7)];x[0]=.61*t;x[7]=.9
        e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
        estimates=[types.SimpleNamespace()for _ in range(3)]
        for h,est in zip((oldh,disabled,enabled),estimates):h.prepare_estimator(est,t)
        cmd=.9 if t<2.5 else 0.;u=[h.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd)for h in(oldh,disabled,enabled)]
        assert np.array_equal(u[0].view(np.uint64),u[1].view(np.uint64));disabled_match+=1;checks+=1
        assert np.array_equal(u[0].view(np.uint64),u[2].view(np.uint64));enabled_match+=1;checks+=1
        assert vars(estimates[0])==vars(estimates[1])==vars(estimates[2])and not enabled.fault;checks+=1
        if k in(194,195):phase_order[str(t)]=dict(phase=enabled.log['phase'],prepared_accel_correction=estimates[2].accel_correction,latched_time=enabled.scheduler.latch_time)
    assert enabled.scheduler.decision_time==1.94 and enabled.trigger==1.95 and not disabled.position_active;checks+=1
    assert phase_order['1.94']['prepared_accel_correction']==1.5 and phase_order['1.95']['prepared_accel_correction']==0.;checks+=1
    # Position decision alone on actual nominal TRAIN trace: no torque replay,
    # no quaternion reconstruction, no simulator and no raw SHA recalculation.
    nomres=json.loads((R/'results/r54_t195_rm/result.json').read_bytes());sched=PositionScheduler();examined=0
    with (R/'results/r54_t195_rm/trace.jsonl').open(encoding='utf-8')as f:
        for line in f:
            r=json.loads(line);examined+=1;latched=sched.step(r['estimated14'][0],r['sensor_age_s'],r['command_time_s'])
            if latched is not None:break
    assert sched.latch_time==1.95 and sched.reason is None;checks+=1
    for vals,reason in [((float('nan'),0.,0.),'position_trigger_invalid_estimate_or_time'),((0.,.051,0.),'position_trigger_invalid_estimate_or_time'),((0.,0.,.005),'position_trigger_off_control_grid')]:
        a=PositionScheduler();assert a.step(*vals)is None and a.reason==reason;checks+=1
    a=PositionScheduler();a.step(5.,0.,0.);a.step(5.,0.,0.);assert a.reason=='position_trigger_clock_order_or_gap';checks+=1
    a=PositionScheduler()
    for k in range(261):a.step(0.,0.,k*.01)
    assert a.reason=='position_trigger_timeout'and a.latch_time is None;checks+=1
    off=copy.deepcopy(c['hop']);off['operator_enable']=False;h=MiniHop(start,end,g,off,landing_gain=land);assert not h.position_active;checks+=1
    assert calls==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R56_POSITION',checks=checks,integrator_calls=calls,new_physics_steps=0,
        disabled_math_commands_bitmatched=disabled_match,enabled_same_synthetic_latch_commands_bitmatched=enabled_match,
        actual_nominal_position_decision_only=dict(rows_examined=examined,decision_time_s=sched.decision_time,latched_push_time_s=sched.latch_time,trace_producer=nomres['trace_artifact']),
        phase_order=phase_order,loop_AST_unchanged=True,no_real_trajectory_rerun=True,no_stability_or_hardware_qualification=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_R56_POSITION',checks=checks,integrator_calls=calls,phase_order=phase_order,nominal_decision_s=sched.decision_time,nominal_latch_s=sched.latch_time),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
