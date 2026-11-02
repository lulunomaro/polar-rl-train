"""Finite control contrast for prolonged impossible air-wheel torque requests.

Physical actuator clip, PD, queue, plant and strict366 contact assessment stay.
Only group40..79 bounds push/flight/extend requested wheel torque before inverse
PD using already observed wheel speed. This does not turn MPC into an oracle.
"""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time,traceback
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
S=T/'MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V366_20261102';D=T/'MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a));return s.replace(a,b,1)
try:
    assert read(R/'ACTUAL367_366_MANIFOLD_CANDIDATES_AND_CONTROL_IDENTITY.json')['passed']
    assert read(S/'reports/ROOT366_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
    D.mkdir(exist_ok=False);(D/'reports').mkdir();rename=lambda s:re.sub(r'(?<=[A-Za-z_])366(?!\d)','368',s)
    for p in sorted(S.rglob('*')):
        rel=p.relative_to(S)
        if not p.is_file()or'__pycache__'in rel.parts or any(q.startswith(('reports','replay','RECORDED','VISIBLE'))for q in rel.parts)or p.name.startswith('INDEX366'):continue
        dest=D/rename(str(rel));dest.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix in('.py','.json'):dest.write_text(rename(p.read_text('utf8')),encoding='utf8')
        else:shutil.copyfile(p,dest)
    p=D/'source/source_event_mpc353.py';s=p.read_text('utf8')
    s=rep(s,"self.cfg=dict(bundle['config']);", "self.bound_air_wheel_request=bool(bundle.get('bound_air_wheel_request',False));self.cfg=dict(bundle['config']);")
    s=rep(s,'target=np.array(q6,float)+(tau+2.*np.array(v6,float))/60.', '''tau_source=tau.copy()
        if self.bound_air_wheel_request and phase in('push','flight','extend'):
            # Same nominal signed wheel DC envelope as source Plant.clip.
            # Uses observed speed only; original real actuator still applies
            # full per-envDR gain and its own clip on each physics tick.
            limit=5.775909774436091;stall=28.18532894736838;no_load=55.3557
            velocity=np.clip(np.asarray(v6)[[2,5]],-no_load*(1+limit/stall),no_load*(1+limit/stall))
            hi=np.minimum(limit,stall*(1-velocity/no_load));lo=np.maximum(-limit,stall*(-1-velocity/no_load))
            tau[[2,5]]=np.clip(tau[[2,5]],lo,hi)
        target=np.array(q6,float)+(tau+2.*np.array(v6,float))/60.''')
    s=rep(s,'return dict(tau=tau,processed_target=', 'return dict(tau=tau,tau_source_requested=tau_source,wheel_request_prebounded=self.bound_air_wheel_request and phase in(\'push\',\'flight\',\'extend\'),processed_target=')
    ast.parse(s);p.write_text(s,encoding='utf8')
    p=D/'source/evaluate368.py';w=p.read_text('utf8')
    w=rep(w,'selected_mask=ids>=40;selected_ids=ids[selected_mask]','selected_mask=ids>=0;selected_ids=ids[selected_mask]')
    w=rep(w,'controllers=[SourceEventMPC353(dict(bundle,actual_command_MPC_dt=.02))for i in range(80)]','controllers=[SourceEventMPC353(dict(bundle,actual_command_MPC_dt=.02,bound_air_wheel_request=i>=40))for i in range(80)]')
    w=w.replace('legacy_default_q_queue_hold','source_air_request_planned_hold').replace('planned_actual_q_queue_hold','bounded_air_wheel_request_planned_hold')
    w=w.replace('only_group40_79_heldtarget_seeded_to_actual_pose=True','all80_heldtarget_seeded_to_actual_pose=True')
    w=rep(w,"tau_requested=out['tau'].tolist(),processed_target=", "tau_requested=out['tau'].tolist(),tau_source_requested=out['tau_source_requested'].tolist(),wheel_request_prebounded=out['wheel_request_prebounded'],processed_target=")
    ast.parse(w);p.write_text(w,encoding='utf8')
    task=read(D/'TASK368_FROZEN.json');task.update(kind='MPC_AIR_WHEEL_REQUEST_ENVELOPE_COMPARISON368',worker_SHA=H(p),reset_hold_groups=['source_air_request_planned_hold','bounded_air_wheel_request_planned_hold'],all80_actualplannedq_queue_hold=True,only_group40_79_airwheel_requested_torque_prebounded=True,actual_manifold_strict366_preserved=True,human_request='Target MPC push/flight control transfer after actual366manifold9/80; noNNtraining, originalphysicalPDandclipuntouched. Compare source unboundedrequest vs nominalwheel DC-bound request BEFOREinversePD atsame50Hz andobservedwheelvelocity. Approach/recover unchanged.')
    (D/'TASK368_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    p=D/'contract368.py';c=p.read_text('utf8').replace('MPC_CONTACT_MANIFOLD_LATCHED_LANDING_AUDIT368','MPC_AIR_WHEEL_REQUEST_ENVELOPE_COMPARISON368');p.write_text(c,encoding='utf8')
    cpu='''from pathlib import Path
import copy,json,sys,numpy as np
D=Path(sys.argv[1]);sys.path.insert(0,str(D/'source'))
from source_event_mpc353 import SourceEventMPC353
b=json.loads((D/'source353_gains.json').read_bytes());base=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02));changed=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02,bound_air_wheel_request=True))
x=np.r_[base.g['q'],np.zeros(7)];x[0]=-.8;q=np.array([x[3],x[3]+x[4],0,x[5],x[5]+x[6],0]);v=np.zeros(6)
a=base.command(0.,x,q,v);r=changed.command(0.,x,q,v);assert np.array_equal(a['tau'],r['tau'])and np.array_equal(a['processed_target'],r['processed_target'])
fixtures=[]
for t in(.02,.2,.6):
 aa=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02));bb=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02,bound_air_wheel_request=True))
 for controller in(aa,bb):controller.launch_time=0.;controller.launch_pose=np.array([x[3],x[4],x[5],x[6]]);controller.launch_velocity=np.zeros(4)
 state=x.copy();state[2]=-.7;state[9]=-5.
 old=aa.command(t,state,q,v);new=bb.command(t,state,q,v)
 assert np.array_equal(new['tau_source_requested'],old['tau'])
 assert np.array_equal(new['tau'][[0,1,3,4]],old['tau'][[0,1,3,4]])
 assert np.max(np.abs(new['tau'][[2,5]]))<=5.775909774436091
 assert np.isfinite(new['processed_target']).all()
 fixtures.append(dict(phase=new['phase'],source_wheel=old['tau'][[2,5]].tolist(),bounded_wheel=new['tau'][[2,5]].tolist()))
print(json.dumps(dict(passed=True,approach_identical=True,leg_requests_identical=True,fixtures=fixtures,NN=0,SDK=0,physics=0)))
'''
    (D/'cpu368_control_request_no_step.py').write_text(cpu,encoding='utf8')
    out=subprocess.run([sys.executable,'-B','-X','utf8',str(D/'cpu368_control_request_no_step.py'),str(D)],capture_output=True,text=True,encoding='utf8');put(D/'reports/CPU368_CONTROL_REQUEST_NO_STEP.json',dict(epoch=time.time(),passed=out.returncode==0,returncode=out.returncode,stdout=out.stdout,stderr=out.stderr));assert out.returncode==0,out.stderr
    for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    ns={};exec(compile(c,str(D/'contract368.py'),'exec'),ns);assert ns['validate_task'](task)
    files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
    put(D/'INDEX368_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
    put(R/'STATIC368_AIR_WHEEL_ENVELOPE_READY.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX368_SOURCE_TASK_CALLERS_FROZEN.json'),runtime_started=False,CPU_no_step_pass=True,not_physical_success=True))
    print(json.dumps(dict(prepared=True,INDEX_SHA=H(D/'INDEX368_SOURCE_TASK_CALLERS_FROZEN.json'),root=str(D),GO=False)))
except BaseException:
    put(R/('LOCAL368_ORIGINAL_PREPARATION_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),NN=0,SDK=0,network=0,physics=0));raise
