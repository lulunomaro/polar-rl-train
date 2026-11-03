"""One preregistered synthetic run; no plant/DR/model imports or old QA replay."""
from pathlib import Path
import ast,copy,hashlib,json,math,shutil,struct,sys,traceback
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;R=D.parents[1]
sys.path.insert(0,str(R));sys.path.insert(0,str(T))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=json.loads((D/'SOURCE_LOCK.json').read_bytes());method=json.loads((D/'METHOD.json').read_bytes())
assert sha(D/'METHOD.json')==lock['method_SHA']and sha(D/'ARCHITECTURE.md')==lock['architecture_SHA']
for x in lock['sources']:assert sha(Path(x['path']))==x['SHA']
assert sha(T/'fk_limits.py')==lock['unchanged_shared_FK_SHA']
assert json.loads((D/'LIMITS_RESULT.json').read_bytes())['status']=='PRECODE_DOMAIN_GATE_PASS'
A=D/'unit_attempt001';A.mkdir(exist_ok=False)
inputs=['controller.py','run_unit.py','test_support.py','run_manual_air_pitch_ref_v1.py','ENTRY_AST.json','METHOD.json','SOURCE_LOCK.json','ARCHITECTURE.md']
for n in inputs:shutil.copy2(D/n,A/n)
shutil.copy2(T/'fk_limits.py',A/'fk_limits.py')
with(A/'PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(dict(files=[dict(path=n,SHA=sha(D/n))for n in inputs],shared_FK_SHA=sha(T/'fk_limits.py')),f,indent=2)
from MINIHOP_AIR_PITCH_REF_V1.attempt002.controller import MiniHop,PITCH_K,PITCH_RATE_K,H_MIN,H_MAX,RATE,PERIOD
from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop as Old
from MINIHOP_AIR_PITCH_REF_V1.attempt002.test_support import gains,geometry,config,estimate_packet,observer
from fk_limits import PublicFK
stats=dict(assertions=0,legacy_nodes_compared=0,default_ticks=0,enabled_ticks=0,enabled_approach_push_ticks=0,flight_ticks=0,capture_ticks=0,reference_FK_rows=0,
           max_rate_step_rad=0.,max_reference_delta_error_rad=0.,max_capture_ref_continuity_error_rad=0.,fault_scenarios=[],phase_events=[],limits_violations=[])

def ck(v,n):
    stats['assertions']+=1
    if not bool(v):raise AssertionError(n)
def fb(x):return struct.pack('<d',float(x))
def bits(a,b,p=''):
    stats['legacy_nodes_compared']+=1
    if isinstance(a,np.ndarray):ck(isinstance(b,np.ndarray)and a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes(),p);return
    if isinstance(a,(float,np.floating)):ck(fb(a)==fb(b),p);return
    if isinstance(a,dict):
        for k,v in a.items():ck(k in b,p+'.'+k);bits(v,b[k],p+'.'+k)
    elif isinstance(a,(tuple,list)):
        ck(type(a)is type(b)and len(a)==len(b),p)
        for i,(u,v)in enumerate(zip(a,b)):bits(u,v,p+str(i))
    elif hasattr(a,'__dict__'):bits(vars(a),vars(b),p)
    else:ck(a==b,p)
def pair(c):
    gs=gains();g=geometry();return Old(*copy.deepcopy(gs[:2]),copy.deepcopy(g),c.copy(),landing_gain=copy.deepcopy(gs[2])),MiniHop(*copy.deepcopy(gs[:2]),copy.deepcopy(g),c.copy(),landing_gain=copy.deepcopy(gs[2]))
def absolute(r):return np.array([r[3],r[3]+r[4],r[5],r[5]+r[6]])
try:
    ck((PITCH_K,PITCH_RATE_K,H_MIN,H_MAX,RATE,PERIOD)==(.25,.04,-.10,.03,1.,.01),'fixed parent parameters')
    fk=PublicFK();curve_hash=hashlib.sha256()
    with patch('time.perf_counter_ns',return_value=0):
        # OFF means missing flag, not merely an explicitly supplied False.
        c=config();old,new=pair(c);oo,on=observer(),observer()
        ck(new.air_pitch_ref_enable is False,'default off')
        for k in range(600):
            t=k*.01;e,p,q=estimate_packet(t,old);old.prepare_estimator(oo,t);new.prepare_estimator(on,t);bits(vars(oo),vars(on),'off observer')
            a=old.command(copy.deepcopy(e),copy.deepcopy(p),t,q.copy(),.7 if t<4. else 0.)
            b=new.command(copy.deepcopy(e),copy.deepcopy(p),t,q.copy(),.7 if t<4. else 0.)
            bits(a,b,'off tau');ck(old.log.keys()==new.log.keys(),'off log key identity');bits(old,new,'off state')
            ck(not old.fault and not new.fault,'synthetic default healthy');stats['default_ticks']+=1
        c=config();c['air_pitch_ref_enable']=True;old,new=pair(c);oo,on=observer(),observer()
        fixed={n:getattr(new,n).copy()for n in ['K0','K1','ff0','ff1','eq1']};eq0original=new.eq0.copy()
        h_expected=0.;last_flight_ref=None;last_flight_h=None;first_capture=None;flight_snapshot=None;spy=[];previous_phase=None
        for k in range(600):
            t=k*.01;e,p,q=estimate_packet(t,old);old.prepare_estimator(oo,t);new.prepare_estimator(on,t);bits(vars(oo),vars(on),'enabled observer')
            since=t-new.trigger;predflight=bool(new.enabled and new.launched and new.push<=since<new.push+new.air)
            capture=bool(new.enabled and new.launched and since>=new.push+new.air)
            if capture and not spy and first_capture is None:
                real=new.ctrl.command
                def watch(*args,**kw):
                    item=dict(ref_entered=new.ctrl.ref.copy(),eq_entered=new.ctrl.eq.copy())
                    out=real(*args,**kw);item.update(ref_after=new.ctrl.ref.copy(),tau=out.copy());spy.append(item);return out
                new.ctrl.command=watch
            prior_h=new.air_h_rad;original=new.q_start;original_bits=original.tobytes()
            a=old.command(copy.deepcopy(e),copy.deepcopy(p),t,q.copy(),.7 if t<4. else 0.)
            b=new.command(copy.deepcopy(e),copy.deepcopy(p),t,q.copy(),.7 if t<4. else 0.)
            ck(new.q_start is original and new.q_start.tobytes()==original_bits,'finally restores original q_start')
            ck(np.isfinite(b).all()and not new.fault,'enabled healthy')
            for n,z in fixed.items():bits(z,getattr(new,n),'unchanged '+n)
            ck(old.log['phase']==new.log['phase'],'original phase schedule')
            ck(fb(old.landing_weight)==fb(new.landing_weight),'landing weight unchanged')
            phase=new.log['phase']
            if phase in ('supported_approach','timed_push'):
                bits(a,b,'enabled unchanged before flight tau');bits(old,new,'enabled unchanged legacy state');stats['enabled_approach_push_ticks']+=1
            if phase=='predicted_flight_retract':
                ck(predflight,'timing predicate matches actual flight')
                goal=max(H_MIN,min(H_MAX,.25*float(e.state14[2])+.04*float(e.state14[9])))
                h_expected=max(H_MIN,min(H_MAX,h_expected+max(-.01,min(.01,goal-h_expected))))
                ck(abs(new.air_h_rad-h_expected)<=1e-14,'independent rate/clip oracle')
                ck(abs(new.air_h_rad-prior_h)<=.01+1e-14,'rate bound per nominal .01s')
                ck(H_MIN<=new.air_h_rad<=H_MAX,'asymmetric domain')
                stats['max_rate_step_rad']=max(stats['max_rate_step_rad'],abs(new.air_h_rad-prior_h))
                bits(a[[2,5]],b[[2,5]],'original flight wheel torque unchanged')
                actual=np.asarray(new.log['target_q4']);expected=original+new.air_h_rad*np.ones(4)
                bits(actual,expected,'actual super flight target')
                der=max(abs(float(actual[1]-actual[0])-float(original[1]-original[0])),abs(float(actual[3]-actual[2])-float(original[3]-original[2])))
                stats['max_reference_delta_error_rad']=max(stats['max_reference_delta_error_rad'],der);ck(der<=1e-12,'flight delta invariant')
                ck(actual[:2].tobytes()==actual[2:].tobytes(),'flight L/R symmetry')
                last_flight_ref=actual.copy();last_flight_h=new.air_h_rad
                if flight_snapshot is None:flight_snapshot=copy.deepcopy(new)
                stats['flight_ticks']+=1
            elif phase=='timed_capture':
                actual=np.asarray(new.log['landing_position_ref4']);stats['capture_ticks']+=1
                ck(new.capture_anchor_rad==last_flight_h and new.air_h_rad==last_flight_h,'freeze h, no phase reset')
                bits(new.eq0[[4,6]],eq0original[[4,6]],'anchor delta unchanged')
                bits(new.ctrl.ref[[4,6]],old.ctrl.ref[[4,6]],'original capture delta trajectory')
                if first_capture is None:
                    first_capture=dict(t=t,anchor=new.capture_anchor_rad,weight=new.landing_weight,actual_ref=actual.tolist(),previous_flight_ref=last_flight_ref.tolist())
                    ck(new.landing_weight==0. and new.capture_started_s==t,'V3 actual first-capture u=0 exercised')
                    err=float(np.max(np.abs(actual-last_flight_ref)));stats['max_capture_ref_continuity_error_rad']=err;ck(err<=1e-12,'continuous first capture actual ref')
                    ck(len(spy)==1,'actual ground command called at first capture')
                    ck(float(np.max(np.abs(absolute(spy[0]['ref_entered'])-last_flight_ref)))<=1e-12,'anchor entered actual ground command, not log')
                    bits(spy[0]['eq_entered'],new.eq0,'anchored actual eq at u0')
                    w=float(np.clip((since-new.push-new.air)/new.blend,0.,1.))
                    expected=np.clip((1-w)*new.capture_from+w*spy[0]['tau'],-np.array([40.,40.,5.775909774436091]*2),np.array([40.,40.,5.775909774436091]*2))
                    bits(expected,b,'actual V1 blend, no post-super torque edit')
            if phase in ('predicted_flight_retract','timed_capture'):
                sample=fk.check(actual)
                if sample['violations']:
                    stats['limits_violations'].append(dict(t=t,phase=phase,q4=actual.tolist(),violations=sample['violations']));raise AssertionError('DOMAIN_FAIL: stop, no third hypothesis')
                stats['reference_FK_rows']+=1
            if phase!=previous_phase:
                stats['phase_events'].append(dict(t=t,phase=phase,h=new.air_h_rad,anchor=new.capture_anchor_rad,reference=(actual.tolist()if phase in ('predicted_flight_retract','timed_capture')else new.log['target_q4'])))
                previous_phase=phase
            curve_hash.update(np.asarray(b,dtype='<f8').tobytes());curve_hash.update(struct.pack('<dd',new.air_h_rad,new.landing_weight))
            stats['enabled_ticks']+=1
        ck(first_capture is not None and stats['flight_ticks']>0 and stats['capture_ticks']>0,'all phases exercised')
        ck(new.landing_weight==1.,'schedule reaches eq1');bits(new.ctrl.eq,new.eq1,'final exact eq1');bits(new.ctrl.K,new.K1,'final exact K1');bits(new.ctrl.tau_eq,new.ff1,'final exact ff1');bits(new.ctrl.ref[3:7],new.eq1[3:7],'final exact leg state refs')
        stats['first_capture']=first_capture;stats['curve_SHA']=curve_hash.hexdigest();stats['final_reference4']=absolute(new.ctrl.ref).tolist()
        # Default operator remains False even if the air feature is explicitly on.
        gs=gains();c0=dict(air_pitch_ref_enable=True,landing_transition_enable=True)
        off=MiniHop(*gs[:2],geometry(),c0,landing_gain=gs[2]);e,p,q=estimate_packet(5.,off);z=off.command(e,p,5.,q,0.)
        ck(not off.enabled and not off.launched and off.air_h_rad==0. and off.log['phase']=='supported_approach','operator defaults false')
        # Sixteen declared invalid-input/clock cases from a healthy flight prefix.
        scenarios=['pitch_nan','rate_inf','time_nan','negative_time','duplicate_time','large_gap','off_grid','state_shape','complex_state','bool_time','packet_nan','age_nan','bad_quat','forward_nan','omega_inf','roll_nan']
        for name in scenarios:
            z=copy.deepcopy(flight_snapshot);t=z.last_time+.01;e,p,q=estimate_packet(t,z);forward=.7
            if name=='pitch_nan':e.state14[2]=math.nan
            elif name=='rate_inf':e.state14[9]=math.inf
            elif name=='time_nan':t=math.nan
            elif name=='negative_time':t=-1.
            elif name=='duplicate_time':t=z.last_time
            elif name=='large_gap':t=z.last_time+.1
            elif name=='off_grid':t+=.005
            elif name=='state_shape':e.state14=e.state14[:-1]
            elif name=='complex_state':e.state14=e.state14.astype(complex)
            elif name=='bool_time':t=True
            elif name=='packet_nan':p.joint_pos4[0]=math.nan
            elif name=='age_nan':e.sensor_age_s=math.nan
            elif name=='bad_quat':q=np.zeros(4)
            elif name=='forward_nan':forward=math.nan
            elif name=='omega_inf':e.omega_body[0]=math.inf
            elif name=='roll_nan':e.roll=math.nan
            before=(z.air_h_rad,z.q_start.tobytes(),z.ctrl.ref.tobytes(),z.eq0.tobytes(),z.last_time,copy.deepcopy(vars(z.scheduler)))
            out=z.command(e,p,t,q,forward)
            after=(z.air_h_rad,z.q_start.tobytes(),z.ctrl.ref.tobytes(),z.eq0.tobytes(),z.last_time,vars(z.scheduler))
            ck(z.fault and z.air_fault_reason is not None and out.tobytes()==np.zeros(6).tobytes(),'finite/time inhibit '+name)
            ck(before==after,'fault before reference/scheduler mutation '+name)
            e2,p2,q2=estimate_packet(z.last_time+.01,z);ck(not z.command(e2,p2,z.last_time+.01,q2,.7).any(),'latched fault '+name)
            stats['fault_scenarios'].append(dict(name=name,fault_before_reference_mutation=True,fault_latched=True))
        z=copy.deepcopy(flight_snapshot);oldref=z.q_start;t=z.last_time+.01;e,p,q=estimate_packet(t,z)
        class DeliberateInnerError(Exception):pass
        caught=False
        with patch.object(Old,'command',side_effect=DeliberateInnerError('synthetic finally proof, no actuator')):
            try:z.command(e,p,t,q,.7)
            except DeliberateInnerError:caught=True
        ck(caught and z.q_start is oldref,'finally restores on inner exception')
        bad=None
        try:MiniHop(*gs[:2],geometry(),dict(air_pitch_ref_enable=True),landing_gain=gs[2])
        except ValueError:bad=True
        ck(bad,'no silently enabled landing transition')
    ck('mujoco'not in sys.modules,'unit did not import physics module')
    stats.update(status='PASS_PURE_SYNTHETIC_MATH_AND_REFERENCE_DOMAIN_NOT_DYNAMIC_ADMISSION',math_gate_pass=True,reference_limits_gate_pass=True,
                 model_boots=0,forward_calls=0,integrator_calls=0,linearizations=0,old_QA_replays=0,raw_reads=0,PH7_pending=True,
                 method_SHA=sha(D/'METHOD.json'),source_lock_SHA=sha(D/'SOURCE_LOCK.json'),core_SHA=sha(D/'controller.py'))
except BaseException:
    stats.update(status='FAILED_OR_UNKNOWN_PRESERVED_NO_RETRY',math_gate_pass=False,reference_limits_gate_pass=False,error=traceback.format_exc(),PH7_pending=True)
    with(D/'UNIT_RESULT.json').open('x',encoding='utf-8')as f:json.dump(stats,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(stats,indent=2,allow_nan=False));raise
with(D/'UNIT_RESULT.json').open('x',encoding='utf-8')as f:json.dump(stats,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(stats,indent=2,allow_nan=False))
