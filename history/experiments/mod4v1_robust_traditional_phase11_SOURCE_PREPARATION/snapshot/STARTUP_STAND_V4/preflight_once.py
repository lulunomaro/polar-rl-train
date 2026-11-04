"""Fresh synthetic fixtures only; never imports a real ground/model/old test runner."""
from pathlib import Path
from types import SimpleNamespace as NS, ModuleType
import json, sys, math, copy, hashlib, traceback, os
import numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
D=Path(__file__).resolve().parent/'preflight001'
COUNT=dict(enabled_commands=0,disabled_and_oracle_commands=0,typed_cases=0,checks=0,
    fake_ground_constructors=0,fake_ground_commands=0,pure_new_goal_calls=0,pure_new_reference_calls=0)
CHECKPOINT={}; PREFIX=[]

def check(ok,label):
    COUNT['checks']+=1
    if not bool(ok):raise AssertionError(label)

def save(name,obj):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def pins(paths):
    return [dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]

class FakeGroundController:
    """Fixture matrix and constant trim ONLY; not MOD4 dynamics or nominal K."""
    def __init__(self,g,c):
        COUNT['fake_ground_constructors']+=1
        self.eq=np.r_[np.asarray(g['q'],float),np.zeros(7)]
        self.ref=self.eq.copy();self.previous=np.zeros(6)
        self.K=np.zeros((6,14));self.K[[2,5],2]=-20.;self.K[[2,5],9]=-4.
        self.shaper=NS(v=0.,w=0.,a=0.)
        self.yaw_integral=self.old_shaped_w=0.;self.valid_command=True
        self.trim=np.array(g['tau'],float)
    def command(self,e,v,w):
        COUNT['fake_ground_commands']+=1
        self.valid_command=True
        return self.trim.copy()

class Poison:
    def __getattribute__(self,key):raise AssertionError('Disabled extra read: '+key)

FLAGS=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False,support_geometry_enable=True)

def sample(t,q,qd=None,pitch=0.,pitchrate=0.,wheels=None):
    q=np.asarray(q,float).copy();qd=np.zeros(4) if qd is None else np.asarray(qd,float).copy()
    x=np.zeros(14);x[2]=pitch;x[9]=pitchrate
    x[3:7]=[q[0],q[1]-q[0],q[2],q[3]-q[2]]
    x[10:14]=[qd[0],qd[1]-qd[0],qd[2],qd[3]-qd[2]]
    aq=np.array([math.cos(pitch/2),0.,math.sin(pitch/2),0.])
    omega=np.array([0.,pitchrate,0.])
    p=NS(validity=True,time_s=t,arrival_s=t,joint_pos4=q,joint_vel4=qd,
        accel_proper_body=np.array([-9.81*math.sin(pitch),0.,9.81*math.cos(pitch)]),
        gyro_body=omega.copy(),wheel_vel2=np.zeros(2) if wheels is None else np.asarray(wheels,float))
    e=NS(state14=x,roll=0.,omega_body=omega,sensor_age_s=0.,estimated_time_s=t)
    est=NS(upright_prior=False,wheel_measurement_enabled=False,ground_kinematic_constraint_enabled=False,
        accel_correction=0.,q=aq,v=np.zeros(3),P=np.eye(3),distance=0.)
    return e,p,est

def command(c,t,arguments,kind='enabled_commands',prepare=True):
    e,p,est=arguments
    before=(est.q.tobytes(),est.v.tobytes(),est.P.tobytes(),est.distance,p.joint_pos4.tobytes())
    if prepare:c.prepare_estimator(est,t)
    COUNT[kind]+=1
    tau=c.command(e,p,t,est.q)
    check(before==(est.q.tobytes(),est.v.tobytes(),est.P.tobytes(),est.distance,p.joint_pos4.tobytes()),'no estimator state/encoder mutation')
    check(np.array_equal(tau,c.last_tau),'actual returned tau equals last_tau')
    return tau,est

def main():
    assert not D.exists(),'once directory exists: inspect, never replay'
    D.mkdir(parents=True)
    paths=[Path(__file__),R/'STARTUP_STAND_V4/controller.py',R/'STARTUP_STAND_V4/METHOD.md',
        R/'STARTUP_STAND_V1/controller.py',R/'STARTUP_STAND_V3/controller.py',
        R/'TALL_ROUGH_BANK_V1/gain_delta0.json',R/'TALL_ROUGH_BANK_V1/gain_delta20.json']
    before=pins(paths);save('SOURCE_PREEXEC.json',before)
    save('STARTED.json',dict(status='FRESH_SYNTHETIC_ONLY',budgets=dict(enabled=600,disabled_and_oracle_total=40,typed=16),
        no_real_ground_or_model_or_old_test_runner=True))
    fake=ModuleType('ground_controller_v4');fake.GroundController=FakeGroundController;fake.fixture_only=True
    check('ground_controller_v4' not in sys.modules and 'mujoco' not in sys.modules,'fresh process before fake import')
    sys.modules['ground_controller_v4']=fake
    from STARTUP_STAND_V4.controller import StartupStand as V4, RATE_CAP
    from STARTUP_STAND_V3.controller import StartupStand as V3
    from STARTUP_STAND_V1.controller import legal_reference,quintic,project_reference,EFFORT
    nominal=json.loads(paths[-2].read_text(encoding='utf-8'))
    support=json.loads(paths[-1].read_text(encoding='utf-8'))
    new=lambda:V4(nominal,Poison(),dict(FLAGS),support_reference=support)
    c=new();initial=np.array([.40797836065,.90000028595,.40798298142,.90000031384])
    transitions=[];phase_seen=set();old_ref=None;old_t=None;max_rate=0.
    for k in range(540):
        t=k*.01
        u=(t-.5)/2.1;s,ds=quintic(u)
        phi=.383686828731*(1.-s)
        phidot=-.383686828731*ds/2.1 if 0.<u<1. else 0.
        q=initial if c.phase=='OBSERVE' else c.qref.copy()
        qd=np.zeros(4) if c.phase=='OBSERVE' else c.vref.copy()
        old_phase=c.phase
        tau,est=command(c,t,sample(t,q,qd,phi,phidot))
        check(c.fault_reason is None,'main synthetic chain no fault: '+str(c.fault_reason))
        legal_reference(c.qref,c.vref)
        check(np.all(np.abs(tau)<=EFFORT),'request effort box')
        check(np.array_equal(np.array(c.log['output_tau6_Nm']),tau),'published actual output')
        check(c.log['contact_or_support_trusted'] is False and c.log['hardware_send_permission'] is False,'no support/send promotion')
        if old_ref is not None and old_phase!='OBSERVE':
            check(np.max(np.abs((c.qref-old_ref)/(t-old_t)-c.vref))<1e-8,'reference velocity actual finite difference')
        old_ref=c.qref.copy();old_t=t
        max_rate=max(max_rate,float(np.max(np.abs(c.vref))))
        if c.phase not in phase_seen:
            phase_seen.add(c.phase);transitions.append(dict(t=t,phase=c.phase))
        if old_phase=='BALANCE':check(est.wheel_measurement_enabled and est.ground_kinematic_constraint_enabled,'next prepare enables only BALANCE')
        else:check(not est.wheel_measurement_enabled and not est.ground_kinematic_constraint_enabled,'prebalance observer remains off')
        PREFIX.append(dict(k=k,t=t,phase=c.phase,qref=c.qref.tolist(),vref=c.vref.tolist(),tau=tau.tolist()))
    check({'OBSERVE','LIFT_WORLD_SUPPORT','CAPTURE_WORLD_SUPPORT','RETURN_NOMINAL','VERIFY','BLEND','BALANCE'}<=phase_seen,'all synthetic handoff phases')
    check(max_rate<=1.+1e-12,'published reference rate cap')
    CHECKPOINT['main_synthetic_transitions']=transitions
    CHECKPOINT['main_max_reference_rate']=max_rate
    CHECKPOINT['main_is_analytic_tracking_not_robot_or_real_gain_math']=True
    save('MAIN_MINIMUM.json',dict(counts=dict(COUNT),transitions=transitions,last=PREFIX[-1],physical_success_NOT_claimed=True))
    # 20 pairs =40 commands TOTAL, not40 pairs. Poison verifies inactive access.
    for j in range(20):
        cfg=dict(operator_enable=j>=10,recovery_tracking_enable=(j%2==0),alignment_wheel_enable=False)
        a=V4(nominal,Poison(),cfg,support_reference=Poison());b=V3(nominal,Poison(),cfg)
        if j<10:
            a.prepare_estimator(Poison(),Poison());b.prepare_estimator(Poison(),Poison())
            COUNT['disabled_and_oracle_commands']+=2
            ta=a.command(Poison(),Poison(),Poison(),Poison());tb=b.command(Poison(),Poison(),Poison(),Poison())
        else:
            ta,_=command(a,0.,sample(0.,initial,pitch=.3),kind='disabled_and_oracle_commands')
            tb,_=command(b,0.,sample(0.,initial,pitch=.3),kind='disabled_and_oracle_commands')
        check(ta.tobytes()==tb.tobytes() and a.log==b.log,'inactive exact V3 delegate output/log')
    # New direct reference helpers: rate/constrained convex steps, not FK/tests replay.
    h=new();h.qref=project_reference(initial);h._ref_time=0.
    for j,phi in enumerate([1.,-1.,.60,-.60,0.,.38,-.38,1.],start=1):
        goal=h._goal(phi);COUNT['pure_new_goal_calls']+=1
        legal_reference(goal,np.zeros(4));old=h.qref.copy()
        h._reference(goal,j*.01);COUNT['pure_new_reference_calls']+=1
        check(np.max(np.abs(h.qref-old))<=RATE_CAP*.01+1e-14,'one gamma bounded reference step')
    # Missing prepare + sticky fault, with no last-published reference fabricated.
    f=new();command(f,0.,sample(0.,initial),prepare=False)
    check(f.fault_reason is not None and f.log['last_published_reference_q4'] is None,'missing prepare fault has no invented reference')
    COUNT['enabled_commands']+=1;out=f.command(Poison(),Poison(),Poison(),Poison())
    check(np.array_equal(out,np.zeros(6)),'sticky fault no packet reads')
    # Invalid packet, then sticky.
    f=new();args=sample(0.,initial);args[1].validity=False
    command(f,0.,args)
    check(f.log['support_capture_gate_this_command'] is None,'fault current gate unknown')
    COUNT['enabled_commands']+=1;check(np.array_equal(f.command(Poison(),Poison(),Poison(),Poison()),np.zeros(6)),'invalid sticky no fields')
    # Two actual publications followed by duplicate-clock preparation fault.
    f=new();command(f,0.,sample(0.,initial));command(f,.01,sample(.01,initial))
    prior=f.log['last_published_reference_q4'];command(f,.01,sample(.01,initial))
    check(f.log['last_published_reference_q4']==prior and f.log['last_published_reference_time_s']==.01,'fault preserves only actual last published snapshot')
    check(f.log['support_goal_q4'] is None and f.log['recovery_preclip_tau6_Nm'] is None,'fault does not relabel stale computed data current')
    # Forced synthetic preconditions exercise guards; not reached physical states.
    def forced(phase,pitch=.1):
        v=new();v.started=0.;v.entered=0.;v.phase=phase
        v.last_command=v.last_prepare=v._ref_time=v._travel_time=0.
        v.qref=v._goal(pitch).copy();v.vref=np.zeros(4)
        return v
    f=forced('CAPTURE_WORLD_SUPPORT');command(f,.01,sample(.01,f.qref,pitch=.1,wheels=[1000.,1000.]))
    check('0.50m' in f.fault_reason and f.encoder_travel_m>.50,'unaltered encoder proxy guard')
    f=forced('CAPTURE_WORLD_SUPPORT');f.last_command=f.last_prepare=f._ref_time=f._travel_time=5.99
    command(f,6.,sample(6.,f.qref,pitch=.1))
    check(f.fault_reason=='startup timeout6s','global deadline not relaxed')
    f=forced('CAPTURE_WORLD_SUPPORT');f.capture_latched=True
    tau,_=command(f,.01,sample(.01,f.qref,pitch=.1,pitchrate=10.,wheels=[20.,20.]))
    check(f.capture_active and f.soft_limited.all() and np.max(np.abs(tau[[2,5]]+2.4))<1e-12,'bounded opposing soft overspeed request')
    f=forced('BLEND');f.qref=f.target.copy();command(f,.01,sample(.01,f.qref,pitch=.2))
    check(f.fault_reason=='handoff readiness lost during blend','no weakened handoff readiness')
    # Exactly16 NEW typed constructors. No old fixture invocation.
    bad=[]
    def typed(cfg=None,sp=None):
        bad.append((dict(FLAGS) if cfg is None else cfg,copy.deepcopy(support) if sp is None else sp))
    for val in [1,np.bool_(True)]:z=dict(FLAGS);z['support_geometry_enable']=val;typed(z)
    z=dict(FLAGS);z['recovery_tracking_enable']=False;typed(z)
    z=dict(FLAGS);z['alignment_wheel_enable']=True;typed(z)
    bad.append((dict(FLAGS),None))
    def altered(key,value):
        sp=copy.deepcopy(support);g=sp.get('gain',sp);g[key]=value;typed(sp=sp)
    sg=support.get('gain',support)
    qbad=list(sg['q']);qbad[4]=.21;altered('q',qbad)
    altered('q',[True]*7)
    tb=list(sg['tau']);tb[0]=float('nan');altered('tau',tb)
    z=dict(FLAGS);z['unknown_key']=True;typed(z)
    z=dict(FLAGS);z['operator_enable']=1;typed(z)
    z=dict(FLAGS);z['recovery_tracking_enable']=np.bool_(True);typed(z)
    z=dict(FLAGS);z['alignment_wheel_enable']=0;typed(z)
    altered('q',[0.]*6);altered('tau',[0.]*5);altered('q',['x']*7)
    qb=list(sg['q']);qb[3]=2.;altered('q',qb)
    check(len(bad)==16,'exact typed fixture budget')
    for cfg,sp in bad:
        COUNT['typed_cases']+=1
        try:V4(nominal,Poison(),cfg,support_reference=sp)
        except (ValueError,TypeError,KeyError):pass
        else:raise AssertionError('typed invalid constructor accepted')
    check(COUNT['enabled_commands']<=600 and COUNT['disabled_and_oracle_commands']==40 and COUNT['typed_cases']==16,'all new command/typed ceilings')
    check('mujoco' not in sys.modules and sys.modules['ground_controller_v4'] is fake,'no real ground/model import')
    after=pins(paths);check(before==after,'all small source/gain bytes unchanged')
    save('RESULT.json',dict(status='PASS_FRESH_SYNTHETIC_NO_PHYSICAL_SKILL_CLAIM',counts=COUNT,checkpoints=CHECKPOINT,
        source_before=before,source_after=after,model_compile_FK_integrator_DR_oldQA_ARM_Git_calls=0,
        fixture_matrix_and_tracking_are_NOT_real_GroundController_or_robot=True,whole_goal_active=True))
    save('PREFIX_SYNTHETIC.json',PREFIX)
    print(json.dumps(dict(status='PASS_FRESH_SYNTHETIC',counts=COUNT,checkpoints=CHECKPOINT),ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except Exception as ex:
        if D.exists():
            payload=dict(status='FAILED_FRESH_FIXTURE_PRESERVED_NO_AUTO_RETRY',error=repr(ex),traceback=traceback.format_exc(),counts=COUNT,
                checkpoints=CHECKPOINT,last_prefix=PREFIX[-1] if PREFIX else None,physical_calls=0)
            dest=D/'ERROR.json'
            if not dest.exists():
                with dest.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2,allow_nan=False)
            prefix=D/'PARTIAL_SYNTHETIC_PREFIX.json'
            if not prefix.exists():
                with prefix.open('x',encoding='utf-8') as f:json.dump(PREFIX,f,ensure_ascii=False,indent=2,allow_nan=False)
        raise
