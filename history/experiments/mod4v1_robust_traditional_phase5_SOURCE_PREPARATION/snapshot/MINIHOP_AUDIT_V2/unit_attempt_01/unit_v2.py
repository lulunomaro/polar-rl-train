"""New v2 synthetic tests only: no model constructor/forward/step/old test run."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ast,copy,hashlib,json,math,shutil,traceback
from types import SimpleNamespace as NS
import numpy as np
import mujoco
from MINIHOP_AUDIT_V2.contact_grade_v2 import ReadOnlyGrade
from MINIHOP_AUDIT_V2.schema_v2 import InstrumentationError,validate_grade_row,PHYSICS_DT_S
from MINIHOP_AUDIT_V2.provenance_v2 import error_receipt
from streamed_trace_rows_v1 import StreamedRows
HERE=Path(__file__).resolve().parent
CHECKS=0;CASES=[]

def check(v,message=''):
    global CHECKS
    CHECKS+=1
    if not bool(v):raise AssertionError(f'check {CHECKS}: {message}')
def error(fn,code=None):
    try:fn()
    except InstrumentationError as e:
        check(code is None or e.code==code,(e.code,code));return e
    raise AssertionError('expected explicit InstrumentationError')

def ct(a=0,b=1,fn=0.,t1=0.,t2=0.,frame=None):
    F=np.array([[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]])if frame is None else np.asarray(frame,float)
    return NS(geom1=a,geom2=b,pos=np.array([.1,.2,.3]),frame=F.reshape(9).copy(),force=np.array([fn,t1,t2,0.,0.,0.]))
class Support:
    def __init__(self):self.vertices={1:np.array([[0.,0.,.01],[0.,.1,.02],[.1,0.,.03]]),2:np.array([[0.,0.,.02],[0.,.1,.03],[.1,0.,.04]])}
    def envelopes(self,d):return{str(i):dict(geom_id=i,world_vertices=v.copy())for i,v in self.vertices.items()}
class Base:
    def __init__(self):
        names=['ground','left_tire','right_tire','guide_wheel_small','chassis_collision','mask0_environment','self_link','second_world']
        ids=np.array([0,1,2,3,4,0,5,0]);self.m=NS(ngeom=len(ids),geom_bodyid=ids,geom_contype=np.array([1,2,2,2,2,0,2,0]),body_mass=np.array([0.,2.,3.,1.,4.,5.]))
        self.m.geom=lambda i:NS(name=names[i]);self.m.body=lambda i:NS(name='body'+str(i))
        self.d=NS(time=0.,qpos=np.array([.1,.2,.3,1.,0.,0.,0.]),qvel=np.arange(6,dtype=float),ctrl=np.arange(6,dtype=float),contact=[],xmat=np.tile(np.eye(3).reshape(1,9),(6,1)),subtree_com=np.arange(18,dtype=float).reshape(6,3))
        self.dt=.0005;self.tick_phys=0;self.tires=[1,2];self.chassis=1;self.mass=999.;self.exact_support=Support();self.dr=NS(marker=np.arange(4));self.imu_window_count=9
class Plant(ReadOnlyGrade,Base):pass

def fingerprint(p):
    return dict(time=p.d.time,qpos=p.d.qpos.tobytes(),qvel=p.d.qvel.tobytes(),ctrl=p.d.ctrl.tobytes(),mass=p.m.body_mass.tobytes(),xmat=p.d.xmat.tobytes(),com=p.d.subtree_com.tobytes(),geomids=p.m.geom_bodyid.tobytes(),dr=p.dr.marker.tobytes(),imu=p.imu_window_count,tick=p.tick_phys,contacts=[(c.geom1,c.geom2,c.pos.tobytes(),c.frame.tobytes(),c.force.tobytes())for c in p.d.contact],vertices={i:v.tobytes()for i,v in p.exact_support.vertices.items()})
def sample(p,contacts=(),post_root=None):
    p.d.contact=list(contacts)
    pre=fingerprint(p);dq=np.arange(6,dtype=float)+.25;tau=np.arange(6,dtype=float)-2.
    dq0=dq.copy();tau0=tau.copy();p._capture_drivepoint(dq,tau)
    check(pre==fingerprint(p),'capture must not write plant/DR/IMU')
    check(np.array_equal(dq,dq0)and np.array_equal(tau,tau0),'input arrays unchanged')
    # Only the test clock advances; this is NOT a simulation step.
    p.tick_phys+=1;p.d.time=p.tick_phys*PHYSICS_DT_S
    if post_root is not None:p.d.qpos[:3]=post_root
    before=fingerprint(p);p._grade_minihop_sample();check(before==fingerprint(p),'grade must not write plant/DR/IMU')
    row=p.audit[-1];validate_grade_row(row);check(json.loads(json.dumps(row,allow_nan=False))==row)
    return row

def basics():
    p=Plant();row=sample(p,[ct(0,1,.4),ct(0,2,.4),ct(0,3,.4)])
    check(row['all_world_normal_N']==math.fsum([.4]*3)and row['air_run_s']==0.)
    check(len(row['contacts'])==3 and row['main_normal_N2']==[.4,.4]and row['guide_normal_N']==.4)
    for _ in range(45):sample(p,[ct(0,1,.4),ct(0,2,.4),ct(0,3,.4)])
    check(p.first_air is None and p.max_air==0.)
    q=Plant()
    for _ in range(41):sample(q,[ct(0,3,2.)])
    check(q.first_air is None and q.audit[-1]['guide_normal_N']==2.)
    r=Plant();row=sample(r,[ct(5,1,2.)]);check(row['all_world_normal_N']==2. and 5 in r._world,'contype0 environment retained')
    s=Plant();row=sample(s,[ct(1,2,100.),ct(0,5,100.)]);check(row['all_world_normal_N']==0. and row['self_contact_count']==row['world_world_contact_count']==1)
    check(row['private_contact_diagnostic']['contact_external_force_world_N3']==[0.,0.,0.])

def air_landing():
    p=Plant()
    for k in range(39):sample(p,[])
    check(p.first_air is None and p.air_run==39*.0005)
    row=sample(p,[],post_root=[9.,8.,7.]);check(p.first_air==0. and p.first_air_confirmed_s==.02 and p.air_run==.02)
    check(row['main_mesh_min_z_world2_m']==[.01,.02]and row['root_xyz_post_m']==[9.,8.,7.])
    check(p.peak_air_main_clearance_m==.01)
    row=sample(p,[ct(0,1,.4),ct(0,3,.4),ct(5,4,.4)])
    landing=copy.deepcopy(p.first_landing);check(landing['stage_time_s']==.02 and len(landing['contacts'])==3)
    check([x['kind']for x in landing['contacts']]==['main_wheel','guide_roller','hard_other'])
    check(all(0.<x['normal_N']<1. for x in landing['contacts'])and p.air_run==0.)
    check(landing['all_world_normal_N']==row['all_world_normal_N'])
    sample(p,[ct(0,2,200.)]);check(p.first_landing==landing,'first landing identity frozen')
    q=Plant()
    for _ in range(40):sample(q,[ct(0,1,.5),ct(0,2,.5)])
    check(q.first_air==0. and q.audit[-1]['all_world_normal_N']==1.,'declared <=1N boundary')
    r=Plant();sample(r,[ct(0,1,-.4)]);check(r.audit[-1]['all_world_normal_N']==0. and r.audit[-1]['environment_contacts'][0]['normal_signed_N']==-.4)

def forces_mass():
    p=Plant();a=ct(0,1,2.,.3,-.2);row=sample(p,[a]);F=np.array(row['private_contact_diagnostic']['contact_external_force_world_N3'])
    check(np.array_equal(F,np.array([.3,-.2,2.])))
    q=Plant();frame=np.diag([-1.,-1.,1.])@a.frame.reshape(3,3);row=sample(q,[ct(1,0,2.,.3,.2,frame)])
    check(row['private_contact_diagnostic']['contact_external_force_world_N3']==F.tolist()and not row['contacts'][0]['robot_is_geom2'])
    r=Plant();r.m.body_mass[1:3]*=2.;row=sample(r,[a,ct(0,2,1.,-.1,.2),ct(1,2,100.),ct(0,5,100.)])
    check(np.allclose(row['private_contact_diagnostic']['contact_external_force_world_N3'],[.2,0.,3.],rtol=0,atol=1e-16))
    check(row['private_contact_diagnostic']['actual_model_body_mass_sum_kg']==20. and r.mass==999.)
    check(row['private_contact_diagnostic']['chassis_subtree_com_world_m3_pre']==[3.,4.,5.])
    check(row['private_contact_diagnostic']['root_rotation_world_from_body33_pre']==np.eye(3).tolist())
    q=Plant();del q.d.xmat;del q.d.subtree_com
    # Explicit unavailable optional caches are None, never manufactured zeros.
    q._capture_drivepoint(np.zeros(6),np.zeros(6));q.tick_phys=1;q.d.time=.0005;q._grade_minihop_sample()
    check(q.audit[-1]['private_contact_diagnostic']['root_rotation_world_from_body33_pre']is None)

def faults():
    mutations={
      'fn_nan':lambda p:setattr(p.d.contact[0],'force',np.array([np.nan,0,0,0,0,0.])),
      'fn_inf':lambda p:setattr(p.d.contact[0],'force',np.array([np.inf,0,0,0,0,0.])),
      'friction_nan':lambda p:setattr(p.d.contact[0],'force',np.array([1.,np.nan,0,0,0,0.])),
      'position_nan':lambda p:setattr(p.d.contact[0],'pos',np.array([np.nan,0,0.])),
      'position_shape':lambda p:setattr(p.d.contact[0],'pos',np.zeros(2)),
      'frame_inf':lambda p:setattr(p.d.contact[0],'frame',np.full(9,np.inf)),
      'frame_shape':lambda p:setattr(p.d.contact[0],'frame',np.zeros(8)),
      'bad_geomid':lambda p:setattr(p.d.contact[0],'geom1',999),
      'negative_geomid':lambda p:setattr(p.d.contact[0],'geom1',-1),
      'post_time_nan':lambda p:setattr(p.d,'time',np.nan),
      'post_rollback':lambda p:setattr(p.d,'time',0.),
      'post_gap':lambda p:setattr(p.d,'time',.01),
      'post_tick':lambda p:setattr(p,'tick_phys',9),
      'post_root_inf':lambda p:p.d.qpos.__setitem__(0,np.inf),
      'mesh_nan':lambda p:p.exact_support.vertices[1].__setitem__((0,2),np.nan),
      'mesh_empty':lambda p:p.exact_support.vertices.__setitem__(1,np.zeros((0,3))),
      'sum_overflow':lambda p:setattr(p.d,'contact',[ct(0,1,1e308),ct(0,2,1e308)]),
    }
    results=[]
    for name,mutate in mutations.items():
        p=Plant();sample(p,[]);saved=copy.deepcopy(p.audit);duration=p.air_run
        p.d.contact=[ct(0,1,1.)];p._capture_drivepoint(np.zeros(6),np.zeros(6));p.tick_phys+=1;p.d.time=p.tick_phys*.0005;mutate(p)
        error(p._grade_minihop_sample);check(p.audit==saved and p.air_run==duration and p.instrumentation_error is not None,name)
        error(p._grade_minihop_sample,'INSTRUMENTATION_LATCHED');check(p.audit==saved)
        results.append(dict(case=name,first_error=p.instrumentation_error,prefix_rows=len(p.audit)))
    capture_mutations={
      'drive_time_nan':lambda p:setattr(p.d,'time',np.nan),
      'drive_time_negative':lambda p:setattr(p.d,'time',-1.),
      'drive_root_nan':lambda p:p.d.qpos.__setitem__(1,np.nan),
      'mass_nan':lambda p:p.m.body_mass.__setitem__(1,np.nan),
      'mass_negative':lambda p:p.m.body_mass.__setitem__(1,-1.),
      'mass_zero':lambda p:p.m.body_mass.__setitem__(slice(None),0.),
      'rotation_nan':lambda p:p.d.xmat.__setitem__((1,0),np.nan),
      'COM_inf':lambda p:p.d.subtree_com.__setitem__((1,0),np.inf),
    }
    for name,mutate in capture_mutations.items():
        p=Plant();mutate(p);error(lambda:p._capture_drivepoint(np.zeros(6),np.zeros(6)));check(len(p.audit)==0 and p._drivepoint is None,name)
        results.append(dict(case=name,first_error=p.instrumentation_error,prefix_rows=0))
    for field,dq,tau in [('dq_nan',np.full(6,np.nan),np.zeros(6)),('tau_inf',np.zeros(6),np.full(6,np.inf)),('dq_shape',np.zeros(5),np.zeros(6)),('dq_bool',np.ones(6,dtype=bool),np.zeros(6))]:
        p=Plant();error(lambda:p._capture_drivepoint(dq,tau));check(not p.audit);results.append(dict(case=field,first_error=p.instrumentation_error,prefix_rows=0))
    p=Plant();error(p._grade_minihop_sample);check(not p.audit)
    p=Plant();p._capture_drivepoint(np.zeros(6),np.zeros(6));error(lambda:p._capture_drivepoint(np.zeros(6),np.zeros(6)))
    p=Plant();sample(p,[]);p.d.time+=.002;error(lambda:p._capture_drivepoint(np.zeros(6),np.zeros(6)))
    return results

def schemas():
    p=Plant();r=sample(p,[ct(0,1,.4)])
    changes=[lambda x:x.__setitem__('all_world_normal_N',0.),lambda x:x.__setitem__('contacts',[]),lambda x:x.__setitem__('air_qualified',True),lambda x:x['cache_stages'].__setitem__('force_s',1.),lambda x:x['private_contact_diagnostic'].__setitem__('actual_model_body_mass_sum_kg',float('nan')),lambda x:x.__setitem__('sample_index',True),lambda x:x.__setitem__('unknown',0),lambda x:x['environment_contacts'][0].__setitem__('position_world_m',[float('nan'),0.,0.])]
    for change in changes:
        bad=copy.deepcopy(r);change(bad);error(lambda:validate_grade_row(bad))
    # Captured input copies cannot be changed by caller aliasing.
    p=Plant();dq=np.arange(6,dtype=float);tau=dq.copy();p._capture_drivepoint(dq,tau);dq[:]=99;tau[:]=88;p.d.time=.0005;p.tick_phys=1;p._grade_minihop_sample()
    check(p.audit[0]['drivepoint']['velocity6_rad_s']==list(range(6))and p.audit[0]['drivepoint']['actual_tau6_Nm']==list(range(6)))

def prefix_case(out):
    p=Plant();p.audit=StreamedRows(out/'synthetic_physics_prefix.jsonl');controls=StreamedRows(out/'synthetic_control_prefix.jsonl')
    sample(p,[]);before=p.audit.path.read_bytes();p.d.contact=[ct(0,1,float('nan'))];p._capture_drivepoint(np.zeros(6),np.zeros(6));p.tick_phys=2;p.d.time=.001
    try:p._grade_minihop_sample()
    except InstrumentationError:
        receipt=error_receipt(traceback.format_exc(),controls,p.audit,p)
    else:raise AssertionError('nonfinite must fault')
    check(p.audit.path.read_bytes()==before and len(p.audit)==1)
    check(receipt['physics_prefix']['SHA']==hashlib.sha256(before).hexdigest()and receipt['physics_prefix']['actual_prefix_matches_producer'])
    check('nan'in receipt['instrumentation_error']['observed_repr']and not receipt['partial_trial_passed'])
    with(out/'synthetic_ERROR.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2,allow_nan=False)
    class Broken(list):
        def append(self,row):raise OSError('controlled append failure')
    q=Plant();q.audit=Broken();q._capture_drivepoint(np.zeros(6),np.zeros(6));q.tick_phys=1;q.d.time=.0005;error(q._grade_minihop_sample)
    check(q.air_run==0. and q.first_air is None and len(q.audit)==0,'no state commit before stream success')
    return receipt

def main():
    out=HERE/'unit_attempt_01';out.mkdir(exist_ok=False)
    names=['unit_v2.py','contact_grade_v2.py','schema_v2.py','provenance_v2.py','run_minihop_case_v2.py','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py','GRADING_CONTRACT.json','BRIDGE_AST.json','RUNNER_AST.json']
    for n in names:shutil.copy2(HERE/n,out/n)
    sources={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest()for n in names}
    old_step=mujoco.mj_step;old_forward=mujoco.mj_forward;old_force=mujoco.mj_contactForce;calls={'step':0,'forward':0,'force':0}
    def forbidden_step(*a,**kw):calls['step']+=1;raise AssertionError('mj_step prohibited in synthetic unit')
    def forbidden_forward(*a,**kw):calls['forward']+=1;raise AssertionError('mj_forward prohibited in synthetic unit')
    def force(model,data,index,target):calls['force']+=1;target[:]=data.contact[index].force
    mujoco.mj_step=forbidden_step;mujoco.mj_forward=forbidden_forward;mujoco.mj_contactForce=force
    failures=[];fault_records=[];prefix=None
    try:
        for name,fn in [('all_small_points_and_environment',basics),('zero20ms_and_first_landing',air_landing),('force_sign_friction_actual_mass',forces_mass),('nonfinite_clock_shapes_latch',faults),('schema_and_copy',schemas),('streamed_prefix_transaction',lambda:prefix_case(out))]:
            start=CHECKS
            try:
                result=fn()
                if name=='nonfinite_clock_shapes_latch':fault_records=result
                if name=='streamed_prefix_transaction':prefix=result
                CASES.append(dict(case=name,checks=CHECKS-start,passed=True))
            except BaseException:
                text=traceback.format_exc();failures.append(dict(case=name,error=text));CASES.append(dict(case=name,checks=CHECKS-start,passed=False));print(text)
        check(calls['step']==calls['forward']==0,'no real physics function calls')
        check('physics_bridge'not in sys.modules and 'full_lqr'not in sys.modules,'no full-model boot before unit admission')
    finally:mujoco.mj_step=old_step;mujoco.mj_forward=old_forward;mujoco.mj_contactForce=old_force
    record=dict(kind='NEW_MINIHOP_V2_SYNTHETIC_UNIT_NOT_OLD_PREFLIGHT',checks=CHECKS,failures=len(failures),cases=CASES,errors=failures,instrumentation_fault_records=fault_records,sources=sources,mujoco_version=mujoco.__version__,calls=calls,physics_steps=0,full_model_constructed=False,old_preflight_reexecuted=False,old_scores_updated=False,contact_or_FSM_cue_promoted=False,prefix_receipt=prefix)
    with(HERE/'UNIT_RESULT_01.json').open('x',encoding='utf-8')as f:json.dump(record,f,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in record.items()if k not in ('sources','instrumentation_fault_records','prefix_receipt','errors')},indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
