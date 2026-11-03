"""ONE new total-budget V3 synthetic proof; no old proof/entry/model execution."""
from pathlib import Path
from types import SimpleNamespace
import ast, copy, datetime, hashlib, json, math, os, sys, traceback
D=Path(__file__).resolve().parent;T=D.parent
N={'enabled_external_commands_total_A_and_B':0,'disabled_external_commands_including_base':0,'typed_cases':0,'checks':0,'base_command_calls':0,'ground_command_calls':0,'geometry_model_FK_PHY_DR_oldQA_Git_agent_calls':0}
PARTIAL=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    assert not p.exists(),str(p)
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def ck(ok,label):
    N['checks']+=1
    if not bool(ok):raise AssertionError(label)
def main():
    assert not(D/'SOURCE_PREEXEC.json').exists(),'Once consumed: inspect evidence, never replay'
    plan=json.loads((D/'SYNTHETIC_PLAN.json').read_text(encoding='utf-8'))
    assert (plan['enabled_external_commands_TOTAL_all_profiles_max'],plan['disabled_external_commands_including_Base_comparator_max'],plan['typed_cases_max'])==(420,40,12)
    paths=[D/'METHOD.md',D/'METHOD_CLARIFICATION_001.json',D/'SYNTHETIC_PLAN.json',D/'controller.py',Path(__file__),D/'derive_entry.py',D/'ENTRY_DERIVATION.json',T/'run_startup_stand_case_v5.py',T/'run_startup_stand_case_v4.py',T/'STARTUP_STAND_V1/controller.py',T/'STARTUP_STAND_V2/controller.py',T/'ground_controller_v4.py',T/'TALL_ROUGH_BANK_V1/gain_delta0.json']
    before=[{'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)}for p in paths]
    assert next(x['SHA']for x in before if x['path']==str(T/'STARTUP_STAND_V1/controller.py'))=='e0f8105b32f69738b681a0d442da07e07021b22cbae7f1f993d33e1643aa7c52'
    assert next(x['SHA']for x in before if x['path']==str(T/'STARTUP_STAND_V2/controller.py'))=='bff97574bb30a4a19cf3cd04186f5af9932f0e78471e0be66c9f3fa82b1493d4'
    ast.parse((D/'controller.py').read_text(encoding='utf-8'));ast.parse(Path(__file__).read_text(encoding='utf-8'))
    save(D/'SOURCE_PREEXEC.json',{'status':'V3_NEW_SOURCE_SPEC_AND_TOTAL_BUDGET_LOCK_BEFORE_CONSTRUCTORS_OR_COMMANDS','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':before,'plan':plan,'initial_counts':dict(N),'no_old_unit_or_raw_or_model_execution':True})
    snap=D/'preexec_sources';snap.mkdir(exist_ok=False)
    for p in (D/'controller.py',Path(__file__),D/'SYNTHETIC_PLAN.json',T/'run_startup_stand_case_v5.py'):(snap/p.name).write_bytes(p.read_bytes())
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
    sys.path.insert(0,str(T))
    import numpy as np
    from STARTUP_STAND_V1.controller import StartupStand as Base,project_reference,quintic,LEG,WHEEL,EFFORT
    from STARTUP_STAND_V3.controller import StartupStand as New
    from ground_controller_v4 import GroundController
    ck('mujoco'not in sys.modules,'No simulator import')
    class GeometryNeverUsed:
        def __getattr__(self,name):
            N['geometry_model_FK_PHY_DR_oldQA_Git_agent_calls']+=1
            raise AssertionError('Geometry forbidden: '+name)
    geom=GeometryNeverUsed();g=json.loads((T/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_text(encoding='utf-8'));gg=g.get('gain',g)
    target=np.array([gg['q'][3],gg['q'][3]+gg['q'][4],gg['q'][5],gg['q'][5]+gg['q'][6]])
    q0=np.array(plan['main']['q0_absolute4_rad']);projected=project_reference(q0)
    def bits(a,b):
        if isinstance(a,np.ndarray)or isinstance(b,np.ndarray):
            a,b=np.asarray(a),np.asarray(b);return a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes()
        if isinstance(a,dict)and isinstance(b,dict):return a.keys()==b.keys()and all(bits(a[k],b[k])for k in a)
        if isinstance(a,(list,tuple))and isinstance(b,(list,tuple)):return len(a)==len(b)and all(bits(x,y)for x,y in zip(a,b))
        if isinstance(a,float)and isinstance(b,float):return np.float64(a).tobytes()==np.float64(b).tobytes()
        return type(a)is type(b)and a==b
    def est():return SimpleNamespace(upright_prior=False,wheel_measurement_enabled=True,ground_kinematic_constraint_enabled=True,accel_correction=9.,q=np.array([.9,.1,.1,.1]),P=np.eye(3),distance=77.)
    def frame(t,q=None,qd=None,pitch=None,roll=None,omega=None,wheel=None):
        s,ds=quintic((t-.25)/2.)
        q=(q0.copy()if t<=.25 else projected+(target-projected)*s)if q is None else np.asarray(q,float)
        qd=(np.zeros(4)if t<=.25 else(target-projected)*ds/2.)if qd is None else np.asarray(qd,float)
        p=plan['main']['pitch0_rad']*(1-s)if pitch is None else float(pitch);r=plan['main']['roll0_rad']*(1-s)if roll is None else float(roll)
        w=np.array([-plan['main']['roll0_rad']*ds/2.,-plan['main']['pitch0_rad']*ds/2.,0.])if omega is None else np.asarray(omega,float)
        x=np.zeros(14);x[0]=.1*t;x[1]=.02*t;x[2]=p;x[7]=.1;x[8]=.02;x[9]=w[1];x[3:7]=[q[0],q[1]-q[0],q[2],q[3]-q[2]];x[10:14]=[qd[0],qd[1]-qd[0],qd[2],qd[3]-qd[2]]
        cr,sr,cp,sp=math.cos(r/2),math.sin(r/2),math.cos(p/2),math.sin(p/2);aq=np.array([cr*cp,sr*cp,cr*sp,-sr*sp])
        proper=9.81*np.array([-math.sin(p),math.sin(r)*math.cos(p),math.cos(r)*math.cos(p)])
        wheel=np.array([.4*math.sin(2.1*t),-.3*math.cos(1.7*t)])if wheel is None else np.asarray(wheel)
        e=SimpleNamespace(state14=x,roll=r,omega_body=w,sensor_age_s=0.,estimated_time_s=t)
        packet=SimpleNamespace(validity=True,time_s=t,arrival_s=t,joint_pos4=q.copy(),joint_vel4=qd.copy(),gyro_body=w.copy(),accel_proper_body=proper,wheel_vel2=wheel)
        return e,packet,aq
    def new(alignment=False):return New(g,geom,{'operator_enable':True,'recovery_tracking_enable':True,'alignment_wheel_enable':alignment})
    def prime(c,phase='VERIFY'):
        c.phase=phase;c.started=0.;c.entered={'SHAPE_TO_STAND':.25,'VERIFY':2.25,'BLEND':2.75,'BALANCE':3.25}.get(phase,0.);c.q0=projected.copy();c.measured_q0=q0.copy();c.project_delta=projected-q0;c.last_tau=np.array([1.,-1.,.3,.7,-.8,-.2]);c.blend_from=c.last_tau.copy()
    original_base,original_gc=Base.command,GroundController.command
    def base_spy(self,*a,**kw):N['base_command_calls']+=1;return original_base(self,*a,**kw)
    def gc_spy(self,*a,**kw):N['ground_command_calls']+=1;return original_gc(self,*a,**kw)
    Base.command,GroundController.command=base_spy,gc_spy
    def invoke(c,e,p,t,aq,off=False):
        key='disabled_external_commands_including_base'if off else'enabled_external_commands_total_A_and_B';lim=40 if off else 420
        assert N[key]<lim,'Budget: stop BEFORE extra command';N[key]+=1
        return c.command(e,p,t,aq)
    def formula(c,e,p):
        r=float(np.clip(-20.*e.roll-2.*e.omega_body[0],-8.,8.));u=np.zeros(6)
        u[LEG]=c.log['nominal_ff_scale']*c.ff[LEG]+120.*(c.qref-p.joint_pos4)+4.*(c.vref-p.joint_vel4)
        u[LEG]+=np.array([-r,r,r,-r]);u[WHEEL]=np.clip(-.30*p.wheel_vel2,-2.,2.)
        if c.alignment_wheel_active and c.alignment_latched:
            common=float(np.mean(-c.ctrl.K[WHEEL,2]*e.state14[2]-c.ctrl.K[WHEEL,9]*e.state14[9]));u[WHEEL]=np.clip(common-.30*p.wheel_vel2,-3.,3.)
            for j,row in enumerate(WHEEL):
                w=p.wheel_vel2[j]
                if abs(w)>12. and u[row]*w>0.:u[row]=np.clip(-.30*np.sign(w)*(abs(w)-12.),-3.,3.)
        return np.clip(u,-EFFORT,EFFORT)
    records=[];maths=[];typed=[];pairs=[]
    try:
        c=new(False);s=est()
        for k in range(340):
            t=k*.01;e,p,aq=frame(t);c.prepare_estimator(s,t);oldphase=c.phase;oldtau=c.last_tau.copy();oldtravel=c.encoder_travel_m;oldt=c._travel_time;b0=N['base_command_calls'];g0=N['ground_command_calls'];u=invoke(c,e,p,t,aq)
            ck(c.fault_reason is None,'Main analytic A fault: '+str(c.fault_reason));ck(N['base_command_calls']==b0+1,'Exactly one base command');ck(N['ground_command_calls']-g0==(0 if c.phase=='OBSERVE' else 1),'No extra GC call')
            ck(bits(c.last_tau,u)and bits(np.array(c.log['output_tau6_Nm']),u),'Actual last_tau/log match')
            ck(bits(s.q,np.array([.9,.1,.1,.1]))and bits(s.P,np.eye(3))and s.distance==77.,'No estimator reset')
            ck(np.isfinite(u).all()and np.all(abs(u)<=EFFORT),'Final original bounds')
            recovery=c.phase in('SHAPE_TO_STAND','VERIFY')
            if recovery:ck(bits(u,formula(c,e,p))and not c.alignment_latched,'A exact tracking/quiet, no Kleg/parallel-PD')
            if recovery or(oldphase=='VERIFY'and c.phase=='BLEND'):
                expected=oldtravel if oldt is None else oldtravel+(t-oldt)*.0625*float(np.mean(abs(p.wheel_vel2)))
                ck(c.encoder_travel_m==expected,'Actual dt proxy including final VERIFY interval')
            if oldphase=='VERIFY'and c.phase=='BLEND':ck(bits(c.blend_from,oldtau)and bits(u,oldtau),'First BLEND captures previous actual recovery')
            if k>=326:ck(s.wheel_measurement_enabled and s.ground_kinematic_constraint_enabled,'Observer restores only after original BALANCE')
            records.append({'time_s':t,'phase':c.phase,'tau6':u.tolist(),'encoderTravel':c.encoder_travel_m,'eligible':c.log.get('alignment_candidate_eligible_this_command',False),'eligibleEver':c.alignment_eligible_ever,'blend':c.log.get('handoff_blend')});PARTIAL.append(records[-1])
        ck([x['time_s']for x in c.transitions]==[.25,2.25,2.75,3.25],'Original analytic phase times');ck(c.alignment_eligible_ever,'A records eligibility without activating B')
        transitions=copy.deepcopy(c.transitions)
        for phase,t,qextra,qdextra in(('SHAPE_TO_STAND',1.,0.,0.),('VERIFY',2.31,.10,.45)):
            a,b=new(False),new(True);prime(a,phase);prime(b,phase);ee,pp,aa=frame(t,q=None if phase=='SHAPE_TO_STAND'else target+qextra,qd=None if phase=='SHAPE_TO_STAND'else np.full(4,qdextra),pitch=.3,roll=.01,omega=[0,0,0],wheel=[13.,-13.]);ua=[]
            for z in(a,b):z.prepare_estimator(est(),t);ua.append(invoke(z,ee,pp,t,aa));ck(not z.alignment_latched,'No B before eligibility')
            ck(bits(ua[0],ua[1])and a.encoder_travel_m==b.encoder_travel_m,'A/B same actuation/guard prefix');maths.append({'test':'A/B preeligible prefix','phase':phase,'output_bit_equal':True})
        # Fixed actual nominal K; no coefficient edit or fitted control parameter.
        b=new(True);prime(b);b._travel_time=2.30;b.encoder_travel_m=.02
        e,p,aq=frame(2.31,q=target+.02,qd=np.full(4,.1),pitch=.8,roll=.2,omega=[5.,4.,0.],wheel=[13.,13.]);b.prepare_estimator(est(),2.31);u=invoke(b,e,p,2.31,aq)
        ck(b.fault_reason is None and b.alignment_latched and b.alignment_eligible_ever,'VERIFY eligibility/latch');ck(bits(u,formula(b,e,p)),'B exact tracking/pose-wheel formula');ck(all(b.log['alignment_soft_overspeed_limited2']),'Both accelerating overspeed directions replaced');ck(np.all(u[WHEEL]<0.)and np.all(abs(u[WHEEL])<=3.),'Opposing softlimit damping');ck(b.log['recovery_roll_scalar_Nm']==-8.,'Original bounded roll')
        maths.append({'test':'B eligible soft overspeed','pose_common':b.log['alignment_pose_common_before_damping_Nm'],'wheel2':u[WHEEL].tolist(),'leg4':u[LEG].tolist()})
        for k,(w,pitch,wy)in enumerate((([-14.,-14.],.8,4.),([12.,12.],.8,4.),([0.,0.],.8,4.),([.5,-.5],.3,0.))):
            t=2.32+k*.01;e,p,aq=frame(t,q=target+.10,qd=np.zeros(4),pitch=pitch,roll=0.,omega=[0,wy,0],wheel=w);b.prepare_estimator(est(),t);u=invoke(b,e,p,t,aq)
            ck(b.alignment_latched and not b.log['alignment_candidate_eligible_this_command'],'Latch persists after eligibility loss');ck(bits(u,formula(b,e,p)),'B fixed pose/damping formula')
            if k==0:ck(not any(b.log['alignment_soft_overspeed_limited2'])and np.all(u[WHEEL]>0.),'Already braking preserved')
            if k==1:ck(not any(b.log['alignment_soft_overspeed_limited2']),'Strict >12, not >=12')
            if k==2:ck(np.all(abs(u[WHEEL])==3.),'B wheel cap')
        for i in(0,1,7,8):
            z=new(True);prime(z);ee,pp,aa=frame(2.31,q=target+.02,qd=np.zeros(4),pitch=.3,roll=0.,omega=[0,0,0],wheel=[.5,-.5]);z.prepare_estimator(est(),2.31);zz=copy.deepcopy(z,{id(geom):geom});other=copy.deepcopy(ee);other.state14[i]+=3.
            a=invoke(z,ee,pp,2.31,aa);v=invoke(zz,other,pp,2.31,aa);ck(bits(a,v),'Pose-only B ignores coordinate'+str(i));maths.append({'test':'B pose-only coordinate exclusion','index':i,'output_bit_equal':True})
        # Extra readiness is stricter, not a replacement for the old predicate.
        z=new(True);prime(z);z.ready_since=2.;ee,pp,aa=frame(2.75,q=target,qd=np.zeros(4),pitch=0.,roll=0.,omega=[0,0,0],wheel=[3.,0.]);ck(Base._ready(z,ee.state14,ee.roll,ee.omega_body,pp.joint_pos4,pp.joint_vel4,True),'Original ready alone true');z.prepare_estimator(est(),2.75);invoke(z,ee,pp,2.75,aa);ck(z.phase=='VERIFY'and z.ready_since is None,'Wheelquiet blocks otherwise-ready handoff')
        z=new(False);prime(z);z.encoder_travel_m=.50;z._travel_time=2.30;ee,pp,aa=frame(2.31,q=target,qd=np.zeros(4),pitch=.3,roll=0.,omega=[0,0,0],wheel=[0.,0.]);z.prepare_estimator(est(),2.31);invoke(z,ee,pp,2.31,aa);ck(z.fault_reason is None and z.encoder_travel_m==.50,'Strict >.50 threshold')
        specs=[('DISARMED',0.)]*4+[('OBSERVE',.1)]*4+[('SHAPE_TO_STAND',.6)]*4+[('VERIFY',2.3)]*4+[('BLEND',3.)]*2+[('BALANCE',3.3)]*2
        for i,(phase,t)in enumerate(specs):
            op=phase!='DISARMED';a=Base(g,geom,{'operator_enable':op});cfg={'operator_enable':op}
            if i<4:cfg.update(recovery_tracking_enable=True,alignment_wheel_enable=True)
            elif i%2:cfg.update(recovery_tracking_enable=False,alignment_wheel_enable=False)
            b=New(g,geom,cfg)
            if phase not in('DISARMED','OBSERVE'):prime(a,phase);prime(b,phase)
            ready=phase in('VERIFY','BLEND','BALANCE');e,p,aq=frame(t,q=target if ready else None,qd=np.zeros(4)if ready else None,pitch=0. if ready else None,roll=0. if ready else None,omega=[0,0,0]if ready else None,wheel=[99.,-99.]if ready else None)
            a.prepare_estimator(est(),t);b.prepare_estimator(est(),t);u=invoke(a,e if op else None,p if op else None,t,aq if op else None,True);v=invoke(b,e if op else None,p if op else None,t,aq if op else None,True)
            ck(bits(u,v)and bits(a.log,b.log),'Disabled output/log exactly delegate');ck(b.encoder_travel_m==0. and b._travel_time is None and b._ready_wheel_rate is None,'Disabled proxy untouched/no extra quiet gate')
            for f in('phase','last_command','last_sensor','ready_since','last_tau','blend_from','transitions'):ck(bits(getattr(a,f),getattr(b,f)),'Disabled original state'+f)
            pairs.append({'phase':phase,'bit_equal':True,'calls_including_base':2})
        def typedcase(label,fn):
            assert N['typed_cases']<12;N['typed_cases']+=1;fn();typed.append({'test':label,'passed':True})
        def ctor_bad(cfg):
            try:New(g,geom,cfg)
            except ValueError:return
            raise AssertionError('Expected constructor failure')
        typedcase('tracking exact bool',lambda:ctor_bad({'recovery_tracking_enable':1}));typedcase('alignment exact bool',lambda:ctor_bad({'alignment_wheel_enable':1}));typedcase('alignment needs tracking',lambda:ctor_bad({'alignment_wheel_enable':True}))
        def badpacket(kind,sticky=False):
            z=new(True);prime(z);z._travel_time=1.;z.encoder_travel_m=.123;e,p,aq=frame(1.01)
            if kind=='wheelNaN':p.wheel_vel2=np.array([float('nan'),0.])
            if kind=='qbool':p.joint_pos4=np.array([True]*4)
            if kind=='qdInf':p.joint_vel4=np.array([float('inf'),0,0,0])
            if kind=='wheelshape':p.wheel_vel2=np.array([1.,2.,3.])
            if kind=='missingq':del p.joint_pos4
            z.prepare_estimator(est(),1.01);ref=z.ctrl.ref.copy();prev=z.ctrl.previous.copy();b0=N['base_command_calls'];u=invoke(z,e,p,1.01,aq)
            ck(z.phase=='INHIBIT'and not np.any(u)and N['base_command_calls']==b0,'Bad numeric packet before base');ck(z.last_command is None and z._travel_time==1. and z.encoder_travel_m==.123 and bits(ref,z.ctrl.ref)and bits(prev,z.ctrl.previous),'Invalid input does not advance proxy/scheduler/GC')
            if sticky:e,p,aq=frame(1.02);u=invoke(z,e,p,1.02,aq);ck(z.phase=='INHIBIT'and not np.any(u)and z.encoder_travel_m==.123,'Fault sticky')
        for kind in('wheelNaN','qbool','qdInf','wheelshape','missingq'):typedcase(kind,lambda k=kind:badpacket(k,k=='wheelNaN'))
        def lastinterval(alignment):
            z=new(alignment);prime(z);z.ready_since=2.25;z.last_command=z.last_prepare=z.last_sensor=2.74;z._travel_time=2.74;z.encoder_travel_m=.4995
            e,p,aq=frame(2.75,q=target,qd=np.zeros(4),pitch=0.,roll=0.,omega=[0,0,0],wheel=[1.5,1.5]);z.prepare_estimator(est(),2.75);u=invoke(z,e,p,2.75,aq)
            ck(z.phase=='INHIBIT'and not np.any(u)and z.encoder_travel_m>.50,'Last VERIFY interval trips same A/B travel guard');ck(any(x['to']=='BLEND'for x in z.transitions),'Fault after valid base scheduling, no rollback claim')
        typedcase('A last VERIFY-toBLEND travel trip',lambda:lastinterval(False));typedcase('B last VERIFY-toBLEND travel trip',lambda:lastinterval(True))
        def lostblend():
            z=new(False);prime(z,'BLEND');e,p,aq=frame(3.,q=target,qd=np.zeros(4),pitch=.2,roll=0.,omega=[0,0,0],wheel=[0,0]);z.prepare_estimator(est(),3.);u=invoke(z,e,p,3.,aq);ck(z.phase=='INHIBIT'and not np.any(u),'Original blend readiness not weakened')
        typedcase('original blend readiness withdraws',lostblend);typedcase('unknown truth config',lambda:ctor_bad({'teacher_force':True}))
        ck(N['typed_cases']==12 and N['disabled_external_commands_including_base']==40 and N['enabled_external_commands_total_A_and_B']<=420,'Total proof budgets')
        ck(N['geometry_model_FK_PHY_DR_oldQA_Git_agent_calls']==0 and 'mujoco'not in sys.modules,'Zero forbidden calls/imports')
    finally:Base.command,GroundController.command=original_base,original_gc
    ck(all(sha(Path(x['path']))==x['SHA']for x in before),'Small sources before/after identical')
    result={'status':'PASS_NEW_V3_TRACKING_ALIGNMENT_MATH_PHASE_API_SYNTHETIC_NOT_PHYSICAL_STANDUP','counts':dict(N),'main_A_frames':340,'analytic_transition_times':transitions,'main_analytic_NOT_simulated_or_estimated_trajectory':True,'main_records':records,'small_math_contexts':maths,'disabled_pairs':pairs,'typed_cases':typed,'all_locked_sources_unchanged':True,'entry_import_or_execution':False,'old499_V2proof_cases_not_replayed':True,'nominal_A_not_executed_B_not_admitted':True,'support_speed_path_stability_hardware_qualified':False,'PH10pending':True}
    save(D/'PREFLIGHT_RESULT.json',result)
    report='''# Startup V3 — 新synthetic数学/phase/API，不是站起验证\n\n- 一次新proof：{enabled} enabled external commands(全体A/B总量)，20对合计40 disabled/base calls，12 typed；主A解析340帧。不是独立试验数。\n- 恢复LEG为120/4 packet跟踪+原scaleFF/roll20/2±8，无Kleg并联；A quiet −.30wheel/±2，B仅VERIFY qerr≤.08/qd≤.40 eligible latch后用原K的pitch/rate common、±3、>12同向加速改为制动。\n- A/B在eligible前同动作/guard；A记录eligible但不启用B；latch/当前packet/cap/保留已有制动/排除距离yaw误差已验证。不是实际A已eligible/B准入。\n- 两profile共享dt*.0625*mean|wheel|轮转proxy，严格>.50m；坏包不推进proxy或base；末VERIFY进入BLEND的区间仍计，可在base调度后fault(不声称rollback)。\n- 原ready全部保留并加wheelquiet≤2，featureFalse无额外门；u0BLEND捕获前一actual替换；解析.25SHAPE/2.25VERIFY/2.75BLEND/3.25BALANCE，3.26原observer恢复。非模型/物理轨迹。\n- 缺省False与operatorFalse literal delegate；20对跨六phase输出/log/原数学状态bit相同，不含wall性能成本；last_tau/log对应实际返回。\n- 新entryV5只静态派生，拒旧V1/V2 ID、三exactbool；原loop/driver/private healthy/good/complete/passed AST与queue_receipt保留，未import/run。\n- 源前后SHA相同；0model/FK/Geometry/PHY/DR/旧499/V2proof/新raw/Git/agent，V1/V2原失败/源/分数未改。\n- 保留线性/PD域、unknown支持/真实位移/实际softspeed限制缺口；A先父审+新ID名义case，B仅实际A传感器eligible出现后父另批，不自动启动/背躺/DR。\n- [core](<controller.py>) / [spec](<METHOD.md>) / [clarification](<METHOD_CLARIFICATION_001.json>) / [plan](<SYNTHETIC_PLAN.json>) / [preexec](<SOURCE_PREEXEC.json>) / [result](<PREFLIGHT_RESULT.json>) / [entryAST](<ENTRY_DERIVATION.json>)。PH10pending，Goal active。\n'''.format(enabled=N['enabled_external_commands_total_A_and_B'])
    assert len(report.splitlines())<=70
    with(D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
    receipt={'status':result['status'],'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':dict(N),'source_before_after_unchanged':before,'source_preexec_SHA':sha(D/'SOURCE_PREEXEC.json'),'core_SHA':sha(D/'controller.py'),'unexecuted_entry_SHA':sha(T/'run_startup_stand_case_v5.py'),'result_SHA':sha(D/'PREFLIGHT_RESULT.json'),'report_SHA':sha(D/'REPORT.md'),'report_lines':len(report.splitlines()),'automatic_replay_or_PHY':False,'independent_parent_review_and_new_case_approval_needed':True,'B_only_later_if_actual_A_eligibility_observed':True,'new_model_FK_PHY_DR_raw_oldQA_Git_agent_calls':0,'PH10pending':True}
    save(D/'RECEIPT.json',receipt)
    print(json.dumps({'status':result['status'],'counts':N,'transitions':transitions,'core_SHA':receipt['core_SHA'],'entry_SHA':receipt['unexecuted_entry_SHA'],'report_SHA':receipt['report_SHA'],'receipt_SHA':sha(D/'RECEIPT.json'),'entry_executed':False},ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except BaseException:
        trace=traceback.format_exc();print(trace,file=sys.stderr)
        for name,raw in(('FAILURE.txt',trace.encode('utf-8')),('FAILURE_SOURCE.py',Path(__file__).read_bytes())):
            p=D/name
            if not p.exists():p.write_bytes(raw)
        if not(D/'FAILURE_RECEIPT.json').exists():save(D/'FAILURE_RECEIPT.json',{'status':'STOP_NEW_V3_PROOF_NO_AUTOMATIC_RERUN_OR_METHOD_CHANGE','counts':N,'partial_main':PARTIAL,'new_model_PHY_oldQA_Git_agent_calls':0,'PH10pending':True})
        raise
