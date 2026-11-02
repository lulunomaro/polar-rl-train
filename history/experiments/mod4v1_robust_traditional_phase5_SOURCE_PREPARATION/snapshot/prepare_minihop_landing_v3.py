"""Create a new landing-schedule runner and test only mathematics; zero physics."""
from pathlib import Path
import ast,hashlib,json,math
import numpy as np
from types import SimpleNamespace
R=Path(__file__).resolve().parent;D=R/'MINIHOP_LANDING_V3';A=D/'preflight001';A.mkdir(exist_ok=False)
base=(R/'run_minihop_observer_v2.py').read_text(encoding='utf-8')
s=base.replace('from MINIHOP_OBSERVER_V2.controller import MiniHop','from MINIHOP_LANDING_V3.controller import MiniHop')
s=s.replace('Future mini-hop runner: v2 private all-contact grade, unchanged control.','New landing-reference/gain TRAIN runner; sealed v2 private all-contact grade.')
s=s.replace("kind='NEW_MINIHOP_WHEEL_OBSERVER_QUARANTINE_OVERLAY'","kind='NEW_MINIHOP_LANDING_REFERENCE_AND_GAIN_SCHEDULE'")
s=s.replace("changed='wheel_and_ground_kinematic_observations_quarantined_longer_not_torque_phase'","changed='keep_V2_observer_quarantine_add_capture_only_nominal_K_feedforward_leg_reference_schedule'")
s=s.replace('torque_phase_math_and_plant_unchanged=True','legacy_phase_times_and_plant_unchanged=True,ground_control_law_changed=True')
s=s.replace("file_record(ROOT/'MINIHOP_OBSERVER_V2/controller.py')]","file_record(ROOT/'MINIHOP_OBSERVER_V2/controller.py'),file_record(ROOT/'MINIHOP_LANDING_V3/controller.py'),file_record(ROOT/cfg['landing_gain']['file'])]")
old="hop=MiniHop(start,end,geom,cfg.get('hop',{}))"
new="""spec=cfg['landing_gain'];gp=(ROOT/spec['file']).resolve();assert gp.is_relative_to(ROOT)
        lg=json.loads(gp.read_bytes());landing=arrays(lg['gains'][spec['bank_key']]if 'bank_key'in spec else lg)
        hop=MiniHop(start,end,geom,cfg.get('hop',{}),landing_gain=landing)"""
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("kind='MINIHOP_AUDIT_V2_PRIVATE_GRADE_UNCHANGED_OPERATOR_TIMER_NOT_CONTACT_RELEASE'","kind='NEW_MINIHOP_CAPTURE_LEG_REFERENCE_AND_GAIN_SCHEDULE_TRAIN'")
ast.parse(s)
def control_loop(txt):
    main=next(x for x in ast.parse(txt).body if isinstance(x,ast.FunctionDef)and x.name=='main')
    return ast.dump(next(x for x in ast.walk(main)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='k'),include_attributes=False)
assert control_loop(s)==control_loop(base)
with(R/'run_minihop_landing_v3.py').open('x',encoding='utf-8')as f:f.write(s)
refs=[]
for p in('MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py','run_minihop_landing_v3.py',Path(__file__).name,'JUMP270_V1/GAIN_BANK.json','nominal_gain_v1.json'):
    raw=(R/p).read_bytes();refs.append(dict(path=p,SHA=hashlib.sha256(raw).hexdigest()))
with(A/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2)
import mujoco
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('physics prohibited'))
from physics_bridge import geometry,load_gain
from sensor_core_jump_v1 import Estimate,SensorPacket
from MINIHOP_V1.controller import absolute_q,EFFORT
from MINIHOP_OBSERVER_V2.controller import MiniHop as V2
from MINIHOP_LANDING_V3.controller import MiniHop as V3

def arrays(g):return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}
bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes());g=arrays(bank['gains']['crouch']);end=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta20.json')
landings=[arrays(bank['gains']['landing']),load_gain(R/'nominal_gain_v1.json')]
geo=geometry();geo.radius=.0625;n=0;cohorts=[]
def check(v):
    global n
    n+=1;assert bool(v),f'check{n}'
def estimate(now):
    x=np.r_[g['q'],np.zeros(7)]
    e=Estimate(x,0.,np.zeros(3),np.array([0.,0.,9.81]),.01,np.zeros(2),0.,now,0.,0.)
    p=SensorPacket(now,now,np.zeros(3),np.array([0.,0.,9.81]),absolute_q(g),np.zeros(4),np.zeros(2),np.zeros(6))
    return e,p
cfg=dict(operator_enable=True,push_for_s=.14,predicted_air_after_push_s=.35,observer_quarantine_after_push_s=.5)
for lg in landings:
    old=V2(g,end,geo,cfg);disabled=V3(g,end,geo,cfg,lg);enabled=V3(g,end,geo,dict(cfg,landing_transition_enable=True,landing_transition_s=.2),lg)
    oldest=SimpleNamespace();newest=SimpleNamespace();prev=absolute_q(g);maxstep=0.;changed=[]
    for k in range(600):
        t=k*.01;e,p=estimate(t);old.prepare_estimator(oldest,t);enabled.prepare_estimator(newest,t)
        check(vars(oldest)==vars(newest))
        a=old.command(e,p,t,np.array([1.,0.,0.,0.]));b=disabled.command(e,p,t,np.array([1.,0.,0.,0.]));c=enabled.command(e,p,t,np.array([1.,0.,0.,0.]))
        check(np.array_equal(a,b));check(np.isfinite(c).all()and np.all(np.abs(c)<=EFFORT))
        if k<200:check(np.array_equal(a,c))
        if not np.array_equal(a,c):changed.append(k)
        qr=np.asarray(enabled.log['landing_position_ref4']);maxstep=max(maxstep,float(np.max(np.abs(qr-prev))));prev=qr
        check(not enabled.log['contact_or_flight_trusted']);json.dumps(enabled.log,allow_nan=False)
    check(np.array_equal(enabled.ctrl.K,enabled.K1));check(np.array_equal(enabled.ctrl.tau_eq,enabled.ff1))
    check(np.array_equal(enabled.ctrl.ref[3:7],np.asarray(lg['q'])[3:7]));check(enabled.landing_weight==1.)
    check(maxstep<=1.5*.01/.2*float(np.max(np.abs(absolute_q(lg)-absolute_q(g))))+1e-12)
    for u in np.linspace(0.,1.,51):
        q=(1-u)*absolute_q(g)+u*absolute_q(lg)
        for side,sl in(('left',slice(0,2)),('right',slice(2,4))):
            a,b=q[sl];_,pos,J,_=geo.wheel_kinematics(float(a),float(b),0.,0.,0.,np.zeros(3),side)
            check(np.isfinite(pos).all()and np.isfinite(J).all())
    cohorts.append(dict(landing_delta=float(lg['q'][4]),disabled600_bitmatch=True,enabled_pre_capture200_bitmatch=True,
                         first_changed_math_tick=changed[0],last_reference_exact=True,max_reference_step_rad=maxstep))
result=dict(kind='NEW_LANDING_SCHEDULE_MATH_ONLY',checks=n,failures=0,physics_steps=0,control_loop_AST_unchanged=True,
            operator_and_transition_default_disabled=True,cohorts=cohorts,stability_or_hardware_qualification=False)
with(A/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
