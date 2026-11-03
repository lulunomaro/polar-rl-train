"""ONE NEW bounded synthetic proof. No simulation/old499/raw/entry execution."""
from pathlib import Path
from types import SimpleNamespace
import ast, copy, datetime, hashlib, json, math, os, sys, traceback

D=Path(__file__).resolve().parent;T=D.parent
COUNTS={'enabled_external_commands':0,'disabled_external_commands_including_base':0,
        'typed_cases':0,'checks':0,'base_command_calls':0,'ground_command_calls':0,
        'geometry_calls':0,'model_FK_PHY_DR_oldQA_Git_agents_calls':0}
PARTIAL=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    assert not p.exists(),str(p)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def ck(ok,label):
    COUNTS['checks']+=1
    if not bool(ok):raise AssertionError(label)
def meta(p):return {'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)}


def main():
    assert not(D/'SOURCE_PREEXEC.json').exists(),'Consumed new proof: inspect evidence, never replay'
    plan=json.loads((D/'SYNTHETIC_PLAN.json').read_text(encoding='utf-8'))
    assert plan['enabled_external_command_max']==420 and plan['disabled_external_command_max_including_base_comparator']==40 and plan['typed_cases_max']==12
    source_paths=[D/'METHOD.md',D/'SYNTHETIC_PLAN.json',D/'controller.py',Path(__file__),D/'derive_entry.py',D/'ENTRY_DERIVATION.json',T/'run_startup_stand_case_v4.py',T/'run_startup_stand_case_v3.py',T/'STARTUP_STAND_V1/controller.py',T/'ground_controller_v4.py',T/'TALL_ROUGH_BANK_V1/gain_delta0.json',T.parent/'traditional_control_20261101/dr_components.py']
    before=[meta(p) for p in source_paths]
    assert next(x['SHA'] for x in before if x['path']==str(T/'STARTUP_STAND_V1/controller.py'))=='e0f8105b32f69738b681a0d442da07e07021b22cbae7f1f993d33e1643aa7c52'
    for name in ('controller.py','preflight_once.py','derive_entry.py'):ast.parse((D/name).read_text(encoding='utf-8'))
    ck('runtime_receipt' not in (T/'run_startup_stand_case_v4.py').read_text(encoding='utf-8'),'no old report API regression')
    save(D/'SOURCE_PREEXEC.json',{'status':'NEW_SOURCE_AND_BUDGET_LOCK_BEFORE_NUMPY_CONTROLLER_CONSTRUCTORS_OR_COMMANDS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':before,'plan':plan,'initial_counts':dict(COUNTS),'no_source_program_or_entry_executed':True})
    snapshots=D/'preexec_sources';snapshots.mkdir(exist_ok=False)
    for p in (D/'controller.py',Path(__file__),D/'SYNTHETIC_PLAN.json',T/'run_startup_stand_case_v4.py'):(snapshots/p.name).write_bytes(p.read_bytes())
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
    sys.path.insert(0,str(T))
    import numpy as np
    from STARTUP_STAND_V1.controller import StartupStand as Base, project_reference, quintic, LEG, WHEEL, EFFORT
    from STARTUP_STAND_V2.controller import StartupStand as New
    from ground_controller_v4 import GroundController
    ck('mujoco' not in sys.modules,'no MuJoCo imported')
    class UnusedGeometry:
        def __getattr__(self,name):
            COUNTS['geometry_calls']+=1
            raise AssertionError('No geometry allowed: '+name)
    geom=UnusedGeometry()
    gain=json.loads((T/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_text(encoding='utf-8'))
    raw_gain=gain.get('gain',gain);target=np.array([raw_gain['q'][3],raw_gain['q'][3]+raw_gain['q'][4],raw_gain['q'][5],raw_gain['q'][5]+raw_gain['q'][6]])
    q0=np.array(plan['main_q0_absolute4_rad']);q0p=project_reference(q0)
    def equal(a,b):
        if isinstance(a,np.ndarray)or isinstance(b,np.ndarray):
            a,b=np.asarray(a),np.asarray(b)
            return a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes()
        if isinstance(a,dict)and isinstance(b,dict):return a.keys()==b.keys()and all(equal(a[k],b[k])for k in a)
        if isinstance(a,(list,tuple))and isinstance(b,(list,tuple)):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
        if isinstance(a,float)and isinstance(b,float):return np.float64(a).tobytes()==np.float64(b).tobytes()
        return type(a)is type(b)and a==b
    def switches():return SimpleNamespace(upright_prior=False,wheel_measurement_enabled=True,ground_kinematic_constraint_enabled=True,accel_correction=9.,q=np.array([.9,.1,.1,.1]),P=np.eye(3),distance=77.)
    def frame(t,pose=None,speed=None,pitch=None,roll=None,omega=None,wheels=None):
        s,ds=quintic((t-.25)/2.)
        q=(q0.copy() if t<=.25 else q0p+(target-q0p)*s) if pose is None else np.asarray(pose,float)
        v=(np.zeros(4) if t<=.25 else (target-q0p)*ds/2.) if speed is None else np.asarray(speed,float)
        p=plan['main_initial_pitch_rad']*(1-s) if pitch is None else float(pitch)
        r=plan['main_initial_roll_rad']*(1-s) if roll is None else float(roll)
        w=np.array([-plan['main_initial_roll_rad']*ds/2.,-plan['main_initial_pitch_rad']*ds/2.,0.]) if omega is None else np.asarray(omega,float)
        x=np.zeros(14);x[0]=.1*t;x[1]=.02*t;x[2]=p;x[7]=.1;x[8]=.02;x[9]=w[1]
        x[3:7]=[q[0],q[1]-q[0],q[2],q[3]-q[2]];x[10:14]=[v[0],v[1]-v[0],v[2],v[3]-v[2]]
        cr,sr,cp,sp=math.cos(r/2),math.sin(r/2),math.cos(p/2),math.sin(p/2)
        aq=np.array([cr*cp,sr*cp,cr*sp,-sr*sp])
        proper=9.81*np.array([-math.sin(p),math.sin(r)*math.cos(p),math.cos(r)*math.cos(p)])
        rates=np.array([8*math.sin(2.1*t),-5*math.cos(1.7*t)]) if wheels is None else np.asarray(wheels)
        e=SimpleNamespace(state14=x,roll=r,omega_body=w,sensor_age_s=0.,estimated_time_s=t)
        packet=SimpleNamespace(validity=True,time_s=t,arrival_s=t,joint_pos4=q.copy(),joint_vel4=v.copy(),gyro_body=w.copy(),accel_proper_body=proper,wheel_vel2=rates)
        return e,packet,aq
    def prime(c,phase):
        c.phase=phase;c.started=0.;c.entered={'SHAPE_TO_STAND':.25,'VERIFY':2.25,'BLEND':2.75,'BALANCE':3.25}.get(phase,0.)
        c.measured_q0=q0.copy();c.q0=q0p.copy();c.static_q0=q0.copy();c.project_delta=q0p-q0;c.last_tau=np.array([1.,-1.,.3,.7,-.8,-.2]);c.blend_from=c.last_tau.copy()
    original_base,original_ground=Base.command,GroundController.command
    def base_spy(self,*a,**kw):COUNTS['base_command_calls']+=1;return original_base(self,*a,**kw)
    def ground_spy(self,*a,**kw):COUNTS['ground_command_calls']+=1;return original_ground(self,*a,**kw)
    Base.command,GroundController.command=base_spy,ground_spy
    def call(c,e,p,t,aq,disabled=False):
        key='disabled_external_commands_including_base' if disabled else 'enabled_external_commands'
        limit=40 if disabled else 420
        assert COUNTS[key]<limit,'External command budget stop before call'
        COUNTS[key]+=1
        return c.command(e,p,t,aq)
    def formula(c,e,p):
        scale=c.log['nominal_ff_scale'];err=e.state14.copy()-c.ctrl.ref.copy();err[[0,1,7,8]]=0.;err[[2,9]]*=scale
        r=float(np.clip(-20*e.roll-2*e.omega_body[0],-8,8));out=np.zeros(6)
        out[LEG]=scale*c.ff[LEG]-c.ctrl.K[LEG,:]@err+np.array([-r,r,r,-r]);out[WHEEL]=np.clip(-.30*p.wheel_vel2,-2.,2.)
        return np.clip(out,-EFFORT,EFFORT)
    mainrows=[];disabled_rows=[];mathrows=[];typed=[]
    try:
        c=New(gain,geom,{'operator_enable':True,'recovery_actuation_enable':True});est=switches()
        authority={'meaning':'Existing nominal K already used in this same main constructor, not a new solve or chosen gain',
            'LEG_rows':[int(x)for x in LEG],'K_LEG_pitch_column2':c.ctrl.K[LEG,2].tolist(),
            'K_LEG_pitch_rate_column9':c.ctrl.K[LEG,9].tolist(),
            'leg_angle_columns':[3,4,5,6],'K_LEG_angle_block':c.ctrl.K[np.ix_(LEG,[3,4,5,6])].tolist(),
            'leg_rate_columns':[10,11,12,13],'K_LEG_rate_block':c.ctrl.K[np.ix_(LEG,[10,11,12,13])].tolist(),
            'ff6_Nm':c.ff.tolist(),'rate_angle_state_columns_are_crank_minus_hip_at4_6_11_13':True}
        for k in range(340):
            t=k*.01;e,p,aq=frame(t);c.prepare_estimator(est,t)
            ck(not est.upright_prior and equal(est.q,np.array([.9,.1,.1,.1]))and equal(est.P,np.eye(3))and est.distance==77.,'no estimator state reset')
            oldphase=c.phase;previous=c.last_tau.copy();base0=COUNTS['base_command_calls'];gc0=COUNTS['ground_command_calls']
            clones=[]
            if k==100:
                for j,delta in ((0,100.),(1,2.),(7,3.),(8,4.)):
                    z=copy.deepcopy(c,{id(geom):geom});ee=copy.deepcopy(e);ee.state14[j]+=delta;clones.append((j,z,ee))
            out=call(c,e,p,t,aq)
            ck(c.fault_reason is None,'main analytic stream fault: '+str(c.fault_reason))
            ck(COUNTS['base_command_calls']-base0==1,'exactly one base command')
            ck(COUNTS['ground_command_calls']-gc0==(0 if c.phase=='OBSERVE' else 1),'no extra GroundController command')
            ck(equal(c.last_tau,out)and equal(np.array(c.log['output_tau6_Nm']),out),'actual output/last_tau/log equality')
            ck(np.isfinite(out).all()and np.all(abs(out)<=EFFORT),'original six-axis bounds')
            if c.phase in ('SHAPE_TO_STAND','VERIFY'):
                ck(equal(out,formula(c,e,p)),'exact K/FF/roll/wheel replacement')
                ck('startup_wheel_scale' not in c.log and c.log['no_added_parallel_leg_PD'],'no misleading old scaled-wheel/parallel-PD log')
                ck(np.all(abs(out[WHEEL])<=2.)and np.all(out[WHEEL]*p.wheel_vel2<=0.),'wheel damping sign/cap')
            else:ck(not c.log.get('recovery_actuation_override',False),'no override outside recovery phases')
            if oldphase=='VERIFY'and c.phase=='BLEND':ck(equal(c.blend_from,previous)and equal(out,previous),'first blend actual previous replacement bit exact')
            if c.phase=='BALANCE' and oldphase!='BALANCE':ck(not est.wheel_measurement_enabled,'restore only next prepare after BALANCE')
            if k>=326:ck(est.wheel_measurement_enabled and est.ground_kinematic_constraint_enabled,'original post-BALANCE observer restore')
            for j,z,ee in clones:
                frozen=ee.state14.copy();v=call(z,ee,p,t,aq)
                ck(equal(v,out)and equal(frozen,ee.state14),'ignored copied coordinate '+str(j))
                mathrows.append({'test':'independent ignored coordinate','index':j,'time_s':t,'equal_tau_bits':True})
            if k==120:
                z=copy.deepcopy(c,{id(geom):geom});z.last_prepare=z.last_command=1.19;z.prepared=None
                ee,pp,qq=frame(t,pose=p.joint_pos4+np.array([.015,-.012,.014,-.013]),speed=p.joint_vel4+np.array([.04,-.06,.05,-.03]),roll=.2,omega=[5.,e.omega_body[1],0.],wheels=[100.,-100.])
                z.prepare_estimator(switches(),t);v=call(z,ee,pp,t,qq)
                ck(z.fault_reason is None and equal(v,formula(z,ee,pp)),'nonzero tracking-error exact K formula')
                ck(equal(v[WHEEL],np.array([-2.,2.]))and z.log['recovery_roll_scalar_Nm']==-8.,'wheel/roll caps')
                legacy=60*(z.qref-pp.joint_pos4)+3*(z.vref-pp.joint_vel4)
                augmented=z.log['recovery_preclip_tau6_Nm'].copy();augmented=np.array(augmented);augmented[LEG]+=legacy
                ck(not equal(v,np.clip(augmented,-EFFORT,EFFORT)),'no parallel60/3 leg PD')
                mathrows.append({'test':'nonzero tracking/caps/no extra PD','legacy_PD_not_added4':legacy.tolist(),'actual6':v.tolist()})
            mainrows.append({'time_s':t,'phase':c.phase,'output6':out.tolist(),'nominal_ff_scale':c.log['nominal_ff_scale'],'observer':copy.deepcopy(c.observer),'blend':c.log['handoff_blend']})
            PARTIAL.append({'main_frame':k,'time_s':t,'phase':c.phase,'output6':out.tolist()})
        phases=[x['to'] for x in c.transitions]
        ck(phases==['SHAPE_TO_STAND','VERIFY','BLEND','BALANCE'],'original phase order')
        ck([x['time_s']for x in c.transitions]==[.25,2.25,2.75,3.25],'analytic original phase times')
        main_transitions=copy.deepcopy(c.transitions)
        specs=[('DISARMED',.0)]*4+[('OBSERVE',.1)]*4+[('SHAPE_TO_STAND',.6)]*4+[('VERIFY',2.3)]*4+[('BLEND',3.)]*2+[('BALANCE',3.3)]*2
        for i,(phase,t) in enumerate(specs):
            op=phase!='DISARMED';cfg={'operator_enable':op};newcfg=dict(cfg)
            # Includes operator-off + feature-on to prove inactive path does not read packet.
            if i<4:newcfg['recovery_actuation_enable']=True
            elif i%2:newcfg['recovery_actuation_enable']=False
            a=Base(gain,geom,cfg);b=New(gain,geom,newcfg);ea,eb=switches(),switches()
            if phase not in ('DISARMED','OBSERVE'):prime(a,phase);prime(b,phase)
            e,p,aq=frame(t,pose=target if phase in ('VERIFY','BLEND','BALANCE')else None,speed=np.zeros(4)if phase in ('VERIFY','BLEND','BALANCE')else None,pitch=0. if phase in ('VERIFY','BLEND','BALANCE')else None,roll=0. if phase in ('VERIFY','BLEND','BALANCE')else None,omega=[0,0,0]if phase in ('VERIFY','BLEND','BALANCE')else None)
            a.prepare_estimator(ea,t);b.prepare_estimator(eb,t)
            aa=call(a,None if not op else e,None if not op else p,t,None if not op else aq,True)
            bb=call(b,None if not op else e,None if not op else p,t,None if not op else aq,True)
            ck(equal(aa,bb)and equal(a.log,b.log),'default-off output and log exact pair '+str(i))
            for field in ('phase','fault_reason','entered','last_command','last_sensor','ready_since','last_tau','blend_from','transitions'):
                ck(equal(getattr(a,field),getattr(b,field)),'disabled base state '+field)
            for field in ('ref','previous','yaw_integral','old_shaped_w'):
                ck(equal(getattr(a.ctrl,field),getattr(b.ctrl,field)),'disabled ground math state '+field)
            disabled_rows.append({'pair':i,'fixture_phase':phase,'tau_bits_and_logs_equal':True,'base_and_new_external_calls':2})
        def typed_case(label,fn):
            assert COUNTS['typed_cases']<12
            COUNTS['typed_cases']+=1;fn();typed.append({'case':label,'passed':True})
        def bad_constructor(cfg):
            try:New(gain,geom,cfg)
            except ValueError:return
            raise AssertionError('Expected constructor ValueError')
        typed_case('nonbool recovery flag',lambda:bad_constructor({'operator_enable':True,'recovery_actuation_enable':1}))
        typed_case('unknown config rejected by original base',lambda:bad_constructor({'operator_enable':True,'teacher_force':True}))
        def bad_wheel(value,missing=False,sticky=False):
            z=New(gain,geom,{'operator_enable':True,'recovery_actuation_enable':True});e,p,aq=frame(0.);z.prepare_estimator(switches(),0.)
            if missing:del p.wheel_vel2
            else:p.wheel_vel2=value
            state=(z.last_command,z.last_sensor,z.q0,copy.deepcopy(z.transitions),z.ctrl.ref.copy(),z.ctrl.previous.copy());before_base=COUNTS['base_command_calls']
            v=call(z,e,p,0.,aq)
            ck(z.phase=='INHIBIT'and np.array_equal(v,np.zeros(6))and COUNTS['base_command_calls']==before_base,'invalid wheel before base command')
            after=(z.last_command,z.last_sensor,z.q0,z.transitions,z.ctrl.ref,z.ctrl.previous)
            ck(all(equal(a,b)for a,b in zip(state,after)),'wheel invalid does not advance scheduler/GC')
            if sticky:
                e,p,aq=frame(.01);v=call(z,e,p,.01,aq);ck(z.phase=='INHIBIT'and not np.any(v),'sticky inhibit')
        for label,value in (('wheel shape',[1.]),('wheel bool',[True,False]),('wheel nan',[float('nan'),0]),('wheel inf',[0,float('inf')])):typed_case(label,lambda v=value:bad_wheel(v))
        typed_case('missing wheel',lambda:bad_wheel(None,True))
        def bad_base(kind):
            z=New(gain,geom,{'operator_enable':True,'recovery_actuation_enable':True});e,p,aq=frame(0.)
            if kind!='no_prepare':z.prepare_estimator(switches(),0.)
            if kind=='nan_state':e.state14[2]=float('nan')
            if kind=='bad_quaternion':aq=np.zeros(4)
            v=call(z,e,p,0.,aq);ck(z.phase=='INHIBIT'and not np.any(v),'base validation still inhibits '+kind)
        for kind in ('nan_state','bad_quaternion','no_prepare'):typed_case(kind,lambda k=kind:bad_base(k))
        typed_case('sticky fault',lambda:bad_wheel([float('nan'),0],sticky=True))
        def lost_blend():
            z=New(gain,geom,{'operator_enable':True,'recovery_actuation_enable':True});prime(z,'BLEND');e,p,aq=frame(3.,pose=target,speed=np.zeros(4),pitch=.2,roll=0.,omega=[0,0,0]);z.prepare_estimator(switches(),3.);v=call(z,e,p,3.,aq)
            ck(z.phase=='INHIBIT'and not np.any(v),'old blend readiness withdrawal retained')
        typed_case('blend loses readiness',lost_blend)
        ck(COUNTS['typed_cases']==12 and COUNTS['disabled_external_commands_including_base']==40,'typed and disabled exact counts')
        ck(COUNTS['enabled_external_commands']<=420 and COUNTS['geometry_calls']==0,'budget and no geometry')
        ck('mujoco' not in sys.modules,'no simulator import at completion')
    finally:
        Base.command,GroundController.command=original_base,original_ground
    ck(all(sha(Path(x['path']))==x['SHA']for x in before),'all locked small sources unchanged')
    result={'status':'PASS_NEW_BOUNDED_V2_MATH_PHASE_API_SYNTHETIC_NOT_STANDUP',
        'counts':dict(COUNTS),'main_enabled_frames':340,'main_phase_transitions':main_transitions,
        'main_fixture_is_analytic_NOT_robot_or_sensor_estimation':True,'disabled_pairs':disabled_rows,
        'math_checks':mathrows,'typed_cases':typed,'main_synthetic_rows':mainrows,
        'existing_nominal_controller_authority_summary':authority,
        'source_inputs_before_after_equal':True,'entry_execution':False,
        'original_failed_V1_case_601controls12020steps_not_replayed_or_regraded':True,
        'old499_not_replayed':True,'physical_support_stability_or_standup_qualified':False,'PH10pending':True}
    save(D/'PREFLIGHT_RESULT.json',result)
    report='''# Startup V2：一次新synthetic数学/phase/API检查，不是起立成功\n\n- 状态：PASS_NEW_BOUNDED_V2_MATH_PHASE_API_SYNTHETIC_NOT_STANDUP；METHOD与预算在命令前锁定。\n- 新enabled external commands：{enabled}；disabled20对(base+V2共40calls)；typed12；主轨迹340帧。嵌套base/GC调用另记，不冒机器人试验。\n- 处方轨迹仅解析q/pitch/roll跟踪：.25 SHAPE、2.25 VERIFY、2.75 BLEND、3.25 BALANCE，下一prepare3.26恢复原observer；不是模型积分或真实站起。\n- SHAPE/VERIFY exact K[LEG]反馈：距离/纵速/yaw4坐标局部副本清零，pitch/rate按原scale，nominalFF+原roll20/2±8；无并联60/3/120/4。\n- samepacket轮速阻尼−.30、cap±2；四独立忽略坐标、非零腿误差/roll轮cap、真实last_tau/log和firstBLEND捕获验证通过。\n- feature缺省False严格delegate；operatorFalse即使featureTrue不读packet；20对覆盖DISARMED/OBSERVE/SHAPE/VERIFY/BLEND/BALANCE，输出/log/相关数学状态bit相同(非wall成本)。\n- bad轮型/NaN/Inf/missing在base command前INHIBIT，未推进last_command/source/phase队列/GC；其余原输入/prepare/BLEND gate仍保留，fault sticky。\n- 新entry V4未import/run；V3 loop/healthy/good/complete/passed/原2k支持gate与driver不变；静态核FullDR.queue_receipt(self)，未call_DR._self_test。\n- 所有小源SHA前后相同；0geometry/model/FK/MuJoCo/PHY/DR/旧499/旧raw/Git/newagent。V1原失败与后处理ERROR不改、不补result。\n- 该线性反馈超出旧upright域仍待新nominal物理；未证明稳定、stop/真实支持、背躺/侧躺/DR/hardware；父独立review+新ID批准后才另行新PHY。\n- [plan](<SYNTHETIC_PLAN.json>) / [preexec](<SOURCE_PREEXEC.json>) / [result](<PREFLIGHT_RESULT.json>) / [core](<controller.py>) / [entryAST](<ENTRY_DERIVATION.json>)。PH10pending，整体Goal仍active。\n'''.format(enabled=COUNTS['enabled_external_commands'])
    assert len(report.splitlines())<=70
    with (D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
    receipt={'status':result['status'],'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'counts':dict(COUNTS),'source_inputs_unchanged':before,'source_preexec_SHA':sha(D/'SOURCE_PREEXEC.json'),
        'core_SHA':sha(D/'controller.py'),'unexecuted_entry_SHA':sha(T/'run_startup_stand_case_v4.py'),
        'result_SHA':sha(D/'PREFLIGHT_RESULT.json'),'report_SHA':sha(D/'REPORT.md'),'report_lines':len(report.splitlines()),
        'ready_for_physics_by_this_receipt':False,'automatic_physics_or_retry':False,
        'new_model_FK_PHY_DR_oldQA_Git_agents_calls':0,'PH10pending':True}
    save(D/'RECEIPT.json',receipt)
    print(json.dumps({'status':result['status'],'counts':COUNTS,'transitions':main_transitions,'core_SHA':receipt['core_SHA'],'entry_SHA':receipt['unexecuted_entry_SHA'],'report_SHA':receipt['report_SHA'],'receipt_SHA':sha(D/'RECEIPT.json'),'entry_executed':False},ensure_ascii=True))

if __name__=='__main__':
    try:main()
    except BaseException:
        trace=traceback.format_exc();print(trace,file=sys.stderr)
        for name,raw in (('FAILURE.txt',trace.encode('utf-8')),('FAILURE_SOURCE.py',Path(__file__).read_bytes())):
            p=D/name
            if not p.exists():p.write_bytes(raw)
        p=D/'FAILURE_RECEIPT.json'
        if not p.exists():save(p,{'status':'STOPPED_NEW_PROOF_NO_AUTOMATIC_RERUN','counts':COUNTS,'partial':PARTIAL,'raw_model_PHY_oldQA_Git_agent_calls':0,'PH10pending':True})
        raise
