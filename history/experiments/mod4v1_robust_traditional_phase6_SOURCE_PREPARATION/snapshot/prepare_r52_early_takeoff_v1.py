"""R52 new TRAIN approach profile, unmodified V3 algorithms/guards/gates.
R49 first-bar edge contact occurred during push BEFORE full air. R51 earlier
capture did not remove guides. Test avoiding that earlier strike, not relaxing
trigger or success guards. No H5 data, no physical integrator in this admission.
"""
from pathlib import Path
import copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/early_takeoff003';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
refs=json.loads((R/'MANUAL_BAR_CAPTURE_TIMING_V1/SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA']
oldrefs=json.loads((R/'MANUAL_FIRST_BAR_V1/preflight001/SOURCE_PREEXEC.json').read_bytes())['files']
for x in oldrefs:assert sha(Path(x['path']))==x['SHA']
dump(D/'SOURCE_PREEXEC.json',dict(preparer_SHA=sha(Path(__file__)),files=refs,additional_old_admitted_files=oldrefs,new_physics_steps=0))
old=mujoco.mj_step;calls=0

def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('No integrator in R52 preparation')
mujoco.mj_step=forbidden
try:
    from run_manual_capture_v3 import arrays,load_landing_gain,MiniHop,BoundsRows
    from physics_bridge import geometry,load_gain
    from rm_grid_terrain_v1 import configure
    from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant
    prev=json.loads((R/'MANUAL_FIRST_BAR_V1/long_runway002/PROTOCOL.json').read_bytes())
    base=copy.deepcopy(next(c for n,c in prev['configs']if n=='r49_long_rm_t210'))
    base.update(start_x_m=.2,forward_m_s=.9,brake_at_s=2.5,cohort='R52_NEW_EARLIER_TAKEOFF_TRAIN_NOT_H5')
    base['hop'].update(trigger_time_s=2.,predicted_air_after_push_s=.35)
    cases=[]
    for scene in('flat','rm'):
        c=copy.deepcopy(base);name='r52_early_'+scene;c.update(scene=scene,case_id=name)
        if scene=='flat':c.pop('terrain_seed',None);c.pop('terrain_difficulty',None)
        cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='R52_EARLIER_TAKEOFF_ORIGINAL_V3_TRAIN',configs=cases,max_workers=1,
        hypothesis='R49 hit firstbar edge during push2.131 BEFORE fullair2.246; reduce forward1 to.9, manual trigger2.1 to2.0, start.1 to.2 to plan pre-bar takeoff; not yet proved clearance',
        original_V3_controller_gains_and_observer=True,original_predicted_air_s=.35,
        trigger_guard_unchanged=dict(pitch_abs_rad=.15,speed_abs_m_s=1.2),success_gates_unchanged=True,
        early_stop_at_2p5_is_local_not_full_terrain=True,flat_admission_before_RM=True,
        software_abort_stops_robot_fail_does_not_get_relabelled=True,H5_not_read_or_retuned=True,
        scope='nominal local first6cmbar only; operator-timer not obstacle/contact FSM',PH6_pending=True))
    bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=arrays(bank['gains']['crouch'])
    end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    configure(9001,1.);plant=MiniHopAuditPlant(False);plant.reset(start['symmetric'],.2)
    br=BoundsRows(D/'STATIC_GEOMETRY_ONLY.jsonl');br.bind(plant);env=plant.exact_support.envelopes(plant.d)
    rear=min(v['rear_x_m']for v in env.values());assert rear>=0. and plant.d.time==0. and plant.tick_phys==0;checks=1
    assert base['hop']['max_trigger_speed_m_s']==1.2;checks+=1
    x=np.r_[start['q'],np.zeros(7)];x[7]=.9;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
    packet=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4))
    h=MiniHop(start,end,g,base['hop'],landing_gain=landing)
    for k in range(800):
        t=k*.01;est=types.SimpleNamespace();h.prepare_estimator(est,t)
        u=h.command(e,packet,t,np.array([1.,0.,0.,0.]),.9 if t<2.5 else 0.)
        assert np.isfinite(u).all()and not h.fault;checks+=1
    assert h.launched and h.captured and h.landing_weight==1. and calls==0;checks+=1
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R52_PROFILE',checks=checks,integrator_calls=calls,new_physics_steps=0,
        synthetic_commands=800,static_main_tire_rear_min_x_m=rear,capture_tick_s=h.capture_started_s,
        no_dynamic_clearance_claim=True,controller_sources_and_original_guards_unchanged=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_R52_PROFILE',checks=checks,integrator_calls=calls,capture_tick_s=h.capture_started_s,static_main_tire_rear_min_x_m=rear),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
