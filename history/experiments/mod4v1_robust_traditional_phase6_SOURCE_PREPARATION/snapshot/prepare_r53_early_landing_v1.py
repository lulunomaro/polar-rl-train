"""New TRAIN timing pair after R52's failed flat gate, no old trial replay.
Only predAir changes from .35 to .18/.25 vs R52. Algorithms/guards stay frozen.
"""
from pathlib import Path
import copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/early_landing004';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
prior=R/'MANUAL_FIRST_BAR_V1/early_takeoff003'
rv=json.loads((prior/'PRE_EXEC_REVIEW.json').read_bytes());assert rv['ready_for_physics']is True
for x in rv['checked_sources']:assert sha(Path(x['path']))==x['SHA'],x['path']
closed=json.loads((prior/'RM_ADMISSION_DECISION.json').read_bytes());assert closed['passed_original_flat_gate']is False and closed['admitted_RM']==[]
dump(D/'SOURCE_PREEXEC.json',dict(preparer_SHA=sha(Path(__file__)),files=rv['checked_sources'],prior_review_SHA=sha(prior/'PRE_EXEC_REVIEW.json'),new_physics_steps=0))
old=mujoco.mj_step;calls=0

def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('No physical integrator in R53 timing admission')
mujoco.mj_step=forbidden
try:
    from run_manual_capture_v3 import arrays,load_landing_gain,MiniHop
    from physics_bridge import geometry,load_gain
    p=json.loads((prior/'PROTOCOL.json').read_bytes());base=copy.deepcopy(next(c for n,c in p['configs']if c['scene']=='rm'))
    cases=[]
    for label,air in(('air180',.18),('air250',.25)):
        for scene in('flat','rm'):
            name=f'r53_{label}_{scene}';c=copy.deepcopy(base);c.update(case_id=name,scene=scene,cohort='R53_EARLIER_LANDING_TRAIN_NOT_H5');c['hop']['predicted_air_after_push_s']=air
            if scene=='flat':c.pop('terrain_seed',None);c.pop('terrain_difficulty',None)
            cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='R53_EARLY_APPROACH_EARLIER_CAPTURE_TRAIN',configs=cases,max_workers=2,
        prior_actual='R52 flat complete but7guide ticks; originalflatgate failed and RM deferred. Firstlanding2.464 vs old timedcapture2.49. Guide exact timing not assumed here.',
        hypothesis='Prepare nominal landing stance earlier in moving hop; only predAir .18/.25 changes vs R52, not weakening trigger or success guard',
        original_algorithms=True,only_predicted_air_changed_vs_R52=True,forward_m_s=.9,start_x_m=.2,trigger_time_s=2.,stop_at_s=2.5,
        observer_quarantine_after_push_s=.5,guards_unchanged=dict(pitch_roll_abs_rad=.15,speed_abs_m_s=1.2),
        flat_admission_before_matched_RM=True,software_errors_stop_waves=True,no_replacement_of_failed_old_trials=True,
        no_dynamic_pass_or_contact_detection_claim=True,H5_not_read_or_retuned=True,PH6_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch'])
    end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    x=np.r_[start['q'],np.zeros(7)];x[7]=.9;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
    packet=types.SimpleNamespace(joint_pos4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]),joint_vel4=np.zeros(4))
    checks=0;before=0;seen=[]
    for name,c in cases:
        if c['scene']!='flat':continue
        a=MiniHop(start,end,g,base['hop'],landing_gain=landing);h=MiniHop(start,end,g,c['hop'],landing_gain=landing)
        for k in range(800):
            t=k*.01;ea=types.SimpleNamespace();eb=types.SimpleNamespace();a.prepare_estimator(ea,t);h.prepare_estimator(eb,t)
            cmd=.9 if t<2.5 else 0.;u0=a.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd);u=h.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd)
            assert np.isfinite(u).all()and not h.fault;checks+=1
            if t<2.32:
                assert np.array_equal(np.asarray(u0,dtype=np.float64).view(np.uint64),np.asarray(u,dtype=np.float64).view(np.uint64))and vars(ea)==vars(eb)
                before+=1;checks+=1
        assert h.captured and h.landing_weight==1. and h.c['max_trigger_speed_m_s']==1.2;checks+=1
        seen.append(dict(case=name,capture_tick_s=h.capture_started_s))
    assert calls==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R53_TIMING',checks=checks,integrator_calls=calls,new_physics_steps=0,
        new_profile_synthetic_commands=1600,fixed_input_prefix_before_2p32s_bitmatched_commands=before,capture_times=seen,
        no_real_trajectory_replay=True,controller_sources_unchanged=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_R53_TIMING',checks=checks,integrator_calls=calls,capture_times=seen),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
