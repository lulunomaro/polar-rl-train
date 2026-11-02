"""Fresh TRAIN profile changes from R48's observed guarded early trigger only.
No H5 inputs or controller/gain changes. Zero integrator admission first.
"""
from pathlib import Path
import copy,hashlib,json,types,traceback
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/long_runway002';D.mkdir(exist_ok=False)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
sources=json.loads((R/'MANUAL_FIRST_BAR_V1/preflight001/SOURCE_PREEXEC.json').read_bytes())['files']
for x in sources:assert digest(Path(x['path']))==x['SHA']
dump(D/'SOURCE_PREEXEC.json',dict(old_admitted_sources=sources,new_preparer_SHA=digest(Path(__file__)),H5_not_read=True))
old=mujoco.mj_step;integrations=0

def forbidden(*a,**k):
    global integrations;integrations+=1;raise AssertionError('No integrator in profile admission')
mujoco.mj_step=forbidden
try:
    from run_manual_first_bar_v1 import arrays,load_landing_gain,MiniHop,BoundsRows
    from physics_bridge import geometry,load_gain
    from rm_grid_terrain_v1 import configure
    from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant
    old_protocol=json.loads((R/'MANUAL_FIRST_BAR_V1/PROTOCOL.json').read_bytes());base=copy.deepcopy(old_protocol['configs'][0][1])
    cases=[]
    for label,trig in(('t200',2.),('t210',2.1)):
        for scene in('flat','rm'):
            c=copy.deepcopy(base);name=f'r49_long_{scene}_{label}';c.update(case_id=name,scene=scene,start_x_m=.1,brake_at_s=3.,cohort='NEW_LONG_RUNWAY_TRAIN_AFTER_R48_GUARD_NOT_H5')
            c['hop']['trigger_time_s']=trig
            if scene=='rm':c.update(terrain_seed=9001,terrain_difficulty=1.)
            cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='NEW_LONG_RUNWAY_OPERATOR_TIMED_TRAIN',configs=cases,max_workers=2,
        rationale='R48 TRAIN early at1s estimatedpitch.2197>unchanged.15 guard; later2/2.1s and longer actual runway startx.1, stop3s; no guard/algorithm relaxation',
        guards_unchanged=True,controller_equations_unchanged=True,only_timing_initialx_stop_changed=True,
        flat_admission_before_matching_RM=True,deferred_cases_not_robot_failures=True,H5_unchanged=True,PH6_pending=True))
    bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=arrays(bank['gains']['crouch']);end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    configure(9001,1.);plant=MiniHopAuditPlant(False);plant.reset(start['symmetric'],.1)
    bounds=BoundsRows(D/'static_geometry_only.jsonl');bounds.bind(plant);env=plant.exact_support.envelopes(plant.d)
    min_tire_x=min(v['rear_x_m']for v in env.values());assert min_tire_x>=0.,min_tire_x
    assert plant.tick_phys==0 and plant.d.time==0.;checks=3
    for name,c in cases:
        if c['scene']!='flat':continue
        h=MiniHop(start,end,g,c['hop'],landing_gain=landing);x=np.r_[start['q'],np.zeros(7)];x[7]=.8
        e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
        p=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4));est=types.SimpleNamespace()
        for k in range(800):
            t=k*.01;h.prepare_estimator(est,t);u=h.command(e,p,t,np.array([1.,0.,0.,0.]),1. if t<3. else 0.)
            assert np.isfinite(u).all()and not h.fault;checks+=1
        assert h.launched and h.captured and h.landing_weight==1.;checks+=1
    assert integrations==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_LONG_RUNWAY_ADMISSION',checks=checks,new_physics_steps=0,integrator_calls=integrations,
        synthetic_command_calls=1600,static_main_tire_rear_min_x_m=min_tire_x,controller_sources_unchanged=True,guard_limit_rad=.15))
    print(json.dumps(dict(status='PASS_ZERO_STEP_LONG_RUNWAY_ADMISSION',checks=checks,integrator_calls=integrations,static_main_tire_rear_min_x_m=min_tire_x),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
