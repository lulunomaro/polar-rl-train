"""New TRAIN landing-equilibrium profile, not a height-only stability claim.
Keep position scheduler, duration/guards and full physical pipeline fixed.
"""
from pathlib import Path
import copy,hashlib,json,traceback,types
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
A=R/'MINIHOP_POSITION_TRIGGER_V1/preflight001';refs=json.loads((A/'SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
extra=[dict(path=str(p),SHA=sha(p))for p in(Path(__file__),R/'TALL_ROUGH_BANK_V1/gain_delta0.json')]
dump(D/'SOURCE_PREEXEC.json',dict(files=refs+extra,preparer_SHA=sha(Path(__file__)),new_physics_steps=0))
old=mujoco.mj_step;calls=0

def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('No integrator in new landing profile admission')
mujoco.mj_step=forbidden
try:
    from run_manual_position_v4 import arrays,load_landing_gain,MiniHop
    from physics_bridge import geometry,load_gain
    prior=json.loads((A/'PROTOCOL.json').read_bytes());base=copy.deepcopy(next(c for n,c in prior['configs']if c['scene']=='rm'))
    new=copy.deepcopy(base);new['landing_gain']={'file':'TALL_ROUGH_BANK_V1/gain_delta0.json'}
    cases=[]
    for scene in('flat','rm'):
        c=copy.deepcopy(new);name='r58_tall0_position_'+scene;c.update(case_id=name,scene=scene,cohort='R58_LANDING_EQUILIBRIUM_PROFILE_TRAIN_NOT_HOLDOUT')
        if scene=='flat':c.pop('terrain_seed',None);c.pop('terrain_difficulty',None)
        cases.append((name,c))
    dump(D/'PROTOCOL.json',dict(kind='R58_POSITION_TALL0_LANDING_PROFILE_TRAIN',configs=cases,max_workers=1,
        selection_after_R57_TRAIN='R57same8 local6/8, firstflight7/8 and joint5/8 vsR55joint3/8; retains4504regression and4505failure. Choose position scheduler for next experiment, not independent validation.',
        hypothesis='New nominal reference geometry query reports greater guide05 clearance for delta0 than delta-.2 under ideal level support; it does NOT describe actual DR tracking or prove cure. Test delta0 landing equilibrium profile.',
        changed='Only landing gain spec from nominaldelta-.2 to existing TALLdelta0; V3 simultaneously interpolates K,ff,eq/ref, so not pureheight-only ablation',
        scheduler_and_push_gains_and_relative_times_unchanged=True,guard_and_output_and_DR_and_success_thresholds_unchanged=True,
        no_new_model_linearization_or_online_DARE=True,no_true_DR_parameters_in_control=True,flat_actual_gate_before_matching_RM=True,
        scope='nominal LOCAL first6cmbar manualodometry plan; no fullDR or dynamic stability or hardware claim',H1_H2_H4_H5_frozen=True,PH7_pending=True))
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch'])
    end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(new['landing_gain']);oldlanding=load_landing_gain(base['landing_gain']);g=geometry();g.radius=.0625
    a=MiniHop(start,end,g,base['hop'],landing_gain=oldlanding);b=MiniHop(start,end,g,new['hop'],landing_gain=landing)
    packet=types.SimpleNamespace(joint_pos4=np.array([start['q'][3],start['q'][3]+start['q'][4],start['q'][5],start['q'][5]+start['q'][6]]),joint_vel4=np.zeros(4))
    checks=0;prefix=0
    for k in range(600):
        t=k*.01;x=np.r_[start['q'],np.zeros(7)];x[0]=.61*t;x[7]=.9;e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
        ea=types.SimpleNamespace();eb=types.SimpleNamespace();a.prepare_estimator(ea,t);b.prepare_estimator(eb,t)
        cmd=.9 if t<2.5 else 0.;u=a.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd);v=b.command(e,packet,t,np.array([1.,0.,0.,0.]),cmd)
        assert np.isfinite(v).all()and not b.fault and vars(ea)==vars(eb);checks+=1
        if t<=2.35:
            assert np.array_equal(u.view(np.uint64),v.view(np.uint64));prefix+=1;checks+=1
    assert b.trigger==1.95 and b.landing_weight==1. and np.array_equal(b.ctrl.K,b.K1)and np.array_equal(b.ctrl.tau_eq,b.ff1);checks+=1
    for weight in np.linspace(0.,1.,51):
        q=(1-weight)*np.asarray(start['q'])+weight*np.asarray(landing['q'])
        for side,h,d in(('left',q[3],q[4]),('right',q[5],q[6])):
            pos,_=g.pose(float(h),float(h+d),side);assert np.isfinite(pos).all();checks+=1
    assert calls==0
    dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R58_LANDING_PROFILE',checks=checks,integrator_calls=calls,new_physics_steps=0,
        new_synthetic_commands=600,pre_capture_through2p35_s_commands_bitmatch=prefix,capture_started_s=b.capture_started_s,
        reference_FK_samples=102,position_trigger_s=b.trigger,actual_loader_used=True,no_dynamic_stability_or_clearance_claim=True))
    print(json.dumps(dict(status='PASS_ZERO_STEP_R58_LANDING_PROFILE',checks=checks,integrator_calls=calls,prefix_commands=prefix,capture_tick_s=b.capture_started_s),indent=2))
except BaseException:
    (D/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old
