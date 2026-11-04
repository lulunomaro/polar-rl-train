"""One new timing-feature proof, fake GC injected before imports; no model/old test execution."""
from pathlib import Path
from types import SimpleNamespace as NS,ModuleType
import ast,datetime,hashlib,json,math,os,sys,traceback
D=Path(__file__).resolve().parent;R=D.parent;O=D/'preflight001'
COUNT=dict(enabled_external_new_and_V4_oracle=0,disabled_external_new_and_V4_oracle=0,typed_contexts=0,checks=0,fake_GC_constructors=0,fake_GC_commands=0,V4_command_nested=0,V3_command_nested=0,V1_command_nested=0,new_active_permission_body_calls=0,geometry_calls=0,model_FK_PHY_DARE_DR_oldQA_native_Git_agents=0)
PREFIX=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
 p=O/name
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def ck(v,label):
 COUNT['checks']+=1
 if not bool(v):raise AssertionError(label)
def main():
 assert not O.exists(),'Proof consumed or partial; inspect, never replay'
 plan=json.loads((D/'SYNTHETIC_PLAN.json').read_text(encoding='utf-8'));assert plan['budgets']==dict(enabled_external_calls_new_plus_all_enabled_V4_oracles_max=320,disabled_external_calls_new_plus_V4_oracles_total=40,typed_cases_max=16)
 paths=[D/x for x in('PARENT_METHOD_AND_PREP_SCOPE.json','PARENT_GENERATION_REPAIR_002.json','SYNTHETIC_PLAN.json','controller.py','preflight_once.py','derive_sources_v2.py','SOURCE_DERIVATION.json','GENERATION_REPAIR_002_DERIVATION.json')]+[R/'run_startup_stand_case_v7.py',R/'run_startup_stand_case_v6.py',R/'STARTUP_STAND_V4/controller.py',R/'STARTUP_STAND_V3/controller.py',R/'STARTUP_STAND_V1/controller.py',R/'TALL_ROUGH_BANK_V1/gain_delta0.json',R/'TALL_ROUGH_BANK_V1/gain_delta20.json']
 before=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))for p in paths]
 assert sha(D/'controller.py')=='209c0385d1501021b05822f0222228ae78b012570f73fb526a435e8c02b2045a'
 assert sha(R/'STARTUP_STAND_V4/controller.py')=='9dec4f858524aad034fb287ac31f864299d86a00bd6aaad4f38f04e5063a2bd4'
 assert sha(R/'TALL_ROUGH_BANK_V1/gain_delta20.json')=='f97040665db51c4bc1686187f14aa46579d8d6f6eabff6ef2ee69dea5328d099'
 ast.parse(Path(__file__).read_text(encoding='utf-8'));O.mkdir()
 save('SOURCE_PREEXEC.json',dict(status='ONE_NEW_SOURCE_BUDGET_LOCK_BEFORE_NUMPY_OR_FAKE_CONTROLLER_IMPORTS',files=before,plan=plan,counts_before=COUNT.copy(),created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 (O/'preexec_sources').mkdir()
 for p in(D/'controller.py',D/'preflight_once.py',D/'SYNTHETIC_PLAN.json',R/'run_startup_stand_case_v7.py'):
  with(O/'preexec_sources'/p.name).open('xb')as f:f.write(p.read_bytes())
 for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
 import numpy as np
 class FakeGC:
  def __init__(self,g,c):
   COUNT['fake_GC_constructors']+=1;self.eq=np.r_[np.asarray(g['q'],float),np.zeros(7)];self.ref=self.eq.copy();self.previous=np.zeros(6);self.K=np.zeros((6,14));self.K[[2,5],2]=-4.;self.K[[2,5],9]=-2.;self.shaper=NS(v=0.,w=0.,a=0.);self.yaw_integral=self.old_shaped_w=0.;self.valid_command=True;self.trim=np.asarray(g['tau'],float).copy()
  def command(self,e,v,w):COUNT['fake_GC_commands']+=1;self.valid_command=True;return self.trim.copy()
 fake=ModuleType('ground_controller_v4');fake.GroundController=FakeGC;sys.modules['ground_controller_v4']=fake;sys.path.insert(0,str(R))
 from STARTUP_STAND_V1.controller import StartupStand as V1,LEG,WHEEL,EFFORT,quintic
 from STARTUP_STAND_V3.controller import StartupStand as V3
 from STARTUP_STAND_V4.controller import StartupStand as V4
 from STARTUP_STAND_V5.controller import StartupStand as V5
 assert 'mujoco'not in sys.modules and 'scipy'not in sys.modules
 nominal=json.loads((R/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_text(encoding='utf-8'))['gain'];support=json.loads((R/'TALL_ROUGH_BANK_V1/gain_delta20.json').read_text(encoding='utf-8'))['gain']
 target=np.array([nominal['q'][3],nominal['q'][3]+nominal['q'][4],nominal['q'][5],nominal['q'][5]+nominal['q'][6]])
 class Poison:
  def __getattribute__(self,key):COUNT['geometry_calls']+=1;raise AssertionError('Forbidden geometry or disabled packet read: '+key)
 geometry=Poison();FLAGS=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False,support_geometry_enable=True)
 def make(cls=V5,feature=True,operator=True):
  f=dict(FLAGS);f['operator_enable']=operator
  if cls is V5:f['lift_pose_enable']=feature
  return cls(nominal,geometry,f,support_reference=support)
 def bits(a,b):
  if isinstance(a,np.ndarray)and isinstance(b,np.ndarray):return a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes()
  if type(a)is float and type(b)is float:return np.float64(a).tobytes()==np.float64(b).tobytes()
  if isinstance(a,dict)and isinstance(b,dict):return set(a)==set(b)and all(bits(a[k],b[k])for k in a)
  if isinstance(a,(list,tuple))and isinstance(b,(list,tuple)):return type(a)is type(b)and len(a)==len(b)and all(bits(x,y)for x,y in zip(a,b))
  return type(a)is type(b)and a==b
 def primed(c,phase='LIFT_WORLD_SUPPORT',t=1.,latched=False):
  c.phase=phase;c.started=0.;c.entered=.25 if phase=='LIFT_WORLD_SUPPORT'else t;c.last_command=t-.01;c.last_prepare=t-.01;c.last_sensor=t-.01;c.prepared=None;c._ref_time=t-.01;c._travel_time=t-.01;c.encoder_travel_m=0.;c.capture_latched=latched;c.capture_first_s=None;c.last_tau=np.array([1.,-1.,.25,1.,-1.,.25]);c.blend_from=c.last_tau.copy()
  q=c.support_q-.1 if phase in('OBSERVE','LIFT_WORLD_SUPPORT','CAPTURE_WORLD_SUPPORT')else target.copy();c.q0=q.copy();c.qref=q.copy();c.vref=np.zeros(4);c.return_from=q.copy();c._ground_reference()
  if phase=='INHIBIT':c.fault_reason='fixture_latched_fault'
  return c
 def frame(t,q,pitch=.1,rate=0.,qd=None,wheels=None,proper_scale=1.,stamp=None,age=0.):
  q=np.array(q,float);vel=np.zeros(4)if qd is None else np.array(qd,float);ws=np.zeros(2)if wheels is None else np.array(wheels,float);x=np.zeros(14);x[2]=pitch;x[9]=rate;x[3:7]=[q[0],q[1]-q[0],q[2],q[3]-q[2]];x[10:14]=[vel[0],vel[1]-vel[0],vel[2],vel[3]-vel[2]];stamp=t if stamp is None else stamp
  e=NS(state14=x,roll=0.,omega_body=np.array([0.,rate,0.]),sensor_age_s=age,estimated_time_s=t)
  p=NS(validity=True,time_s=stamp,arrival_s=t,joint_pos4=q,joint_vel4=vel,accel_proper_body=proper_scale*9.81*np.array([-math.sin(pitch),0.,math.cos(pitch)]),gyro_body=np.array([0.,rate,0.]),wheel_vel2=ws)
  return e,p,np.array([math.cos(pitch/2),0.,math.sin(pitch/2),0.])
 def prepare(c,t):
  est=NS(upright_prior=False,wheel_measurement_enabled=True,ground_kinematic_constraint_enabled=True,accel_correction=9.)
  c.prepare_estimator(est,t);return est
 original={}
 for cls,key in((V4,'V4_command_nested'),(V3,'V3_command_nested'),(V1,'V1_command_nested'),(V5,'new_active_permission_body_calls')):
  name='_command_lift_permission'if cls is V5 else'command';fn=getattr(cls,name);original[(cls,name)]=fn
  def spy(self,*args,_fn=fn,_key=key,**kwargs):COUNT[_key]+=1;return _fn(self,*args,**kwargs)
  setattr(cls,name,spy)
 def invoke(c,t,f,off=False):
  k='disabled_external_new_and_V4_oracle'if off else'enabled_external_new_and_V4_oracle';limit=40 if off else 320
  ck(COUNT[k]<limit,'Stop BEFORE external command budget');COUNT[k]+=1;e,p,aq=f;out=c.command(e,p,t,aq)
  PREFIX.append(dict(label=k,t=t if math.isfinite(float(t)) else 'NONFINITE_INPUT_FIXTURE',class_name=type(c).__module__,phase=c.phase,fault=c.fault_reason,tau=out.tolist(),gate=getattr(c,'capture_gate',None),latch=getattr(c,'capture_latched',None),early=c.log.get('lift_pose_branch_on_this_command')))
  return out
 def legacy_log(d):return{k:v for k,v in d.items()if not k.startswith('lift_pose_')and k not in('earlier_lift_latch_carryover_is_timing_change','no_new_contact_or_hardware_permission')}
 records=[];typed=[]
 try:
  c=primed(make());b=primed(make(V4));fired=0
  for i in range(12):
   t=(100+i)*.01;pitch=.8 if i==5 else .1;rate=4. if i==5 else 0.;q=c.qref.copy();vel=np.ones(4)*.41 if i==2 else np.zeros(4);w=[14.,-14.]if i==5 else[0.,0.];q=q+.09 if i==1 else q;ps=0. if i==3 else 1.;stamp=c.last_sensor if i==4 else t;age=.01 if i==4 else 0.
   f=frame(t,q,pitch,rate,vel,w,ps,stamp,age);prepare(c,t);prepare(b,t);u=invoke(c,t,f);v=invoke(b,t,f)
   ck(c.fault_reason is None and b.fault_reason is None,'Paired LIFT fixtures valid');ck(bits(u[LEG],v[LEG])and bits(c.qref,b.qref)and bits(c.vref,b.vref)and bits(c.nominal_mix,b.nominal_mix)and bits(c.ff_scale,b.ff_scale),'Same input exact leg/ref/trim math')
   ck(np.all(np.abs(u)<=EFFORT)and bits(u,c.last_tau)and bits(u,np.array(c.log['output_tau6_Nm'])),'Effort and actual log/lasttau')
   if i in(1,2,3,4):ck(c.capture_gate is False and c.capture_active is False,'False current gate never bypassed');ck(bits(u[WHEEL],np.clip(-.30*f[1].wheel_vel2,-2.,2.)),'Quiet on falsegate')
   else:ck(c.capture_active and c.log['lift_pose_branch_on_this_command'],'Actual new branch on');fired+=1
   if i==0:ck(not bits(u[WHEEL],v[WHEEL])and b.capture_latched is False,'Intervention acted before CAPTURE')
   if i==5:ck(c.soft_limited.tolist()==[True,False]and u[2]<0.and u[5]>0.,'Overspeed same-sign replacement/opposite braking retained')
   ck(np.max(np.abs(u[WHEEL]))<=3.,'Pose cap retained');records.append(dict(t=t,gate=c.capture_gate,latch=c.capture_latched,wheel_new=u[WHEEL].tolist(),wheel_V4=v[WHEEL].tolist()))
  # Initial latch must still respect all old eligibility conditions, including wheel quiet.
  for mode in('qerror','qrate','proper','wheelquiet','notfresh'):
   z=primed(make());q=z.qref.copy()+(.09 if mode=='qerror'else 0.);f=frame(1.,q,qd=np.ones(4)*.41 if mode=='qrate'else None,wheels=[2.1,0.]if mode=='wheelquiet'else None,proper_scale=0. if mode=='proper'else 1.,stamp=.99 if mode=='notfresh'else 1.,age=.01 if mode=='notfresh'else 0.);prepare(z,1.);invoke(z,1.,f);ck(z.fault_reason is None and not z.capture_latched and not z.capture_active,'No early latch '+mode)
  # Fresh same-state non-LIFT oracles, including an already-carried latch.
  for phase in('OBSERVE','CAPTURE_WORLD_SUPPORT','RETURN_NOMINAL','VERIFY','BLEND','BALANCE','INHIBIT'):
   z=primed(make(),phase,t=3.,latched=True);v=primed(make(V4),phase,t=3.,latched=True);f=frame(3.,z.qref,pitch=.1 if phase in('OBSERVE','CAPTURE_WORLD_SUPPORT')else 0.)
   prepare(z,3.);prepare(v,3.);u=invoke(z,3.,f);w=invoke(v,3.,f);ck(bits(u,w)and bits(legacy_log(z.log),v.log),'Non-LIFT actual V4 delegation '+phase)
  # Exact inactive output/log behavior across original phases; all comparator calls count.
  phases=['DISARMED']*4+['OBSERVE']*4+['LIFT_WORLD_SUPPORT']*4+['CAPTURE_WORLD_SUPPORT']*2+['RETURN_NOMINAL']*2+['VERIFY']*2+['BLEND','BALANCE']
  for phase in phases:
   enabled=phase!='DISARMED';z=make(feature=not enabled,operator=enabled);v=make(V4,operator=enabled)
   if enabled:primed(z,phase,t=3.);primed(v,phase,t=3.)
   f=frame(3.,z.qref,pitch=.1 if phase in('OBSERVE','LIFT_WORLD_SUPPORT','CAPTURE_WORLD_SUPPORT')else 0.)if enabled else(Poison(),Poison(),Poison())
   if enabled:prepare(z,3.);prepare(v,3.)
   u=invoke(z,3.,f,True);w=invoke(v,3.,f,True);ck(bits(u,w)and bits(z.log,v.log),'Inactive exact output/log '+phase)
   for name in('phase','last_tau','blend_from','last_command','last_sensor','qref','vref','_ref_time','encoder_travel_m','_travel_time','capture_latched'):ck(bits(getattr(z,name),getattr(v,name)),'Inactive state '+phase+'/'+name)
  def case(label,fn):
   ck(COUNT['typed_contexts']<16,'Typed budget stop');COUNT['typed_contexts']+=1;fn();typed.append(dict(case=label,passed=True))
  def bad_ctor(kind):
   f=dict(FLAGS);f['lift_pose_enable']=True
   if kind=='flag':f['lift_pose_enable']=1
   if kind=='requires':f['support_geometry_enable']=False
   if kind=='unknown':f['teacher_force']=True
   try:V5(nominal,geometry,f,support_reference=support)
   except ValueError:return
   raise AssertionError('Expected constructor ValueError '+kind)
  def bad_input(kind):
   t=6. if kind=='timeout'else 1.;phase='VERIFY'if kind=='travel_verify'else'LIFT_WORLD_SUPPORT';z=primed(make(),phase,t=t);f=frame(t,z.qref,pitch=0. if phase=='VERIFY'else .1);e,p,aq=f
   if kind=='nanwheel':p.wheel_vel2=np.array([float('nan'),0.])
   if kind=='boolq':p.joint_pos4=np.ones(4,bool)
   if kind=='infqd':p.joint_vel4[0]=float('inf')
   if kind=='nanstate':e.state14[2]=float('nan')
   if kind=='nangyro':p.gyro_body[0]=float('nan')
   if kind=='missingwheel':del p.wheel_vel2
   prepare(z,t)
   if kind=='nanclock':t=float('nan')
   if kind=='duplicate':z.last_command=t
   if kind=='age':e.sensor_age_s=.051
   if kind=='quaternion':aq[:]=0.
   if kind.startswith('travel_'):z.encoder_travel_m=.4999;p.wheel_vel2[:]=1.5;z.ready_since=0.
   protected={k:getattr(z,k).copy()if isinstance(getattr(z,k),np.ndarray)else getattr(z,k)for k in('last_command','last_sensor','qref','vref','_ref_time','encoder_travel_m','_travel_time','capture_latched')}
   u=invoke(z,t,(e,p,aq));ck(z.phase=='INHIBIT'and z.fault_reason is not None and bits(u,np.zeros(6)),'Typed inhibit '+kind)
   if kind in('nanwheel','boolq','infqd','nanstate','nangyro','nanclock','missingwheel'):
    ck(all(bits(getattr(z,k),v)for k,v in protected.items()),'Bad numeric/type before scheduler/reference/proxy/latch mutation '+kind)
   if kind=='nanwheel':
    reason=z.fault_reason;u=invoke(z,1.01,frame(1.01,z.qref));ck(z.fault_reason==reason and bits(u,np.zeros(6)),'Sticky fault')
  for label in('flag','requires','unknown'):case(label,lambda label=label:bad_ctor(label))
  for label in('nanwheel','boolq','infqd','nanstate','nangyro','nanclock','duplicate','age','quaternion','travel_lift','travel_verify','timeout','missingwheel'):case(label,lambda label=label:bad_input(label))
 finally:
  for(cls,name),fn in original.items():setattr(cls,name,fn)
 ck(COUNT['enabled_external_new_and_V4_oracle']<=320 and COUNT['disabled_external_new_and_V4_oracle']==40 and COUNT['typed_contexts']==16,'Total budgets')
 ck(COUNT['geometry_calls']==0 and 'mujoco'not in sys.modules and 'scipy'not in sys.modules,'No real solver/model/geometry import')
 ck(all(sha(Path(x['path']))==x['SHA']for x in before),'All source/data before-after equal')
 save('MINIMUM_RESULT.json',dict(status='NEW_V5_FEATURE_PROOF_MINIMUM_PERSISTED_BEFORE_PROSE',counts=COUNT,branch_fired=fired,paired_LIFT=records,typed=typed,prefix=PREFIX))
 result=dict(status='PASS_NEW_V5_TIMING_ONLY_FEATURE_SYNTHETIC_NOT_STANDUP',counts=COUNT,branch_fired_LIFT_commands=fired,first_lift_pose_branch_s=c.lift_pose_first_branch_s,no_new_K_or_stability_or_support_validation=True,same_input_leg_reference_and_FF_unchanged=True,non_LIFT_original_V4_delegate=True,inactive_20pairs_exact=True,typed=typed,paired_LIFT=records,source_before=before,source_after_equal=True,old551_not_replayed=True,V7_entry_not_imported_or_executed=True,model_FK_PHY_DARE_DR_oldQA_native_Git_agents=0,PH11pending=True)
 save('RESULT.json',result)
 report='''# V5：新timing permission合成验证，非站立证书
- 唯一新proof首次PASS；enabled（含所有enabled V4 oracle）{enabled}，disabled/oracle共40=20pairs，typed16，checks{checks}；FakeGC构造{ctors}/命令{cmds}，其矩阵只是fixture，不是nominal K/DARE。
- LIFT新pose分支实际起用{fired}个合成command；false qerror/qd/proper/fresh gate不绕过，初次wheelquiet仍需满足。早latch后可延续，current gate失效即quiet。
- 同输入leg/ref/trim位等V4；非LIFT旧policy/state、featureoff/operatoroff输出/log位等。保留quiet2/pose3、strict>12同向软制动/已反向制动、encoder.50、6s及原phase/success。
- 新路径typed/NaN在scheduler/ref/proxy/latch推进前INHIBIT；fault currentNone/lastpub和sticky/clock/timeout/旅行guard保留。非完整fake站立回放。
- 首静态generator manifest变量断言失败原source/trace/0命令保留；父只准新v2修provenance并断言partialcore原bytes，未修候选或重跑旧proof。
- [core](<../controller.py>) / [scope](<../PARENT_METHOD_AND_PREP_SCOPE.json>) / [source derivation](<../SOURCE_DERIVATION.json>) / [minimum](<MINIMUM_RESULT.json>) / [result](<RESULT.json>)。
- V7仅新flag/kind/ID/source metadata；完整loop/target/healthy/good/complete/passed AST同V6，queue_receipt与实际gain20 loader保留。未来sourceindex必须含gain20，entry未import/运行。
- 0model/FK/PHY/DR/真实solver/native/旧QA/551/Git/agent；不声称真实K、支撑、物理站立或动态稳定，不赋硬件send权限。
- PH11pending；需要独立review/config/sourcefreeze/父新front首案批准。此处停止，不自动物理或重放。
'''.format(enabled=COUNT['enabled_external_new_and_V4_oracle'],checks=COUNT['checks'],ctors=COUNT['fake_GC_constructors'],cmds=COUNT['fake_GC_commands'],fired=fired)
 assert len(report.splitlines())<=23
 with(O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
 save('RECEIPT.json',dict(status='SEALED_NEW_V5_FEATURE_PROOF_ONLY_NOT_PHYSICAL_READY',counts=COUNT,core_SHA=sha(D/'controller.py'),entry_SHA=sha(R/'run_startup_stand_case_v7.py'),result_SHA=sha(O/'RESULT.json'),report_SHA=sha(O/'REPORT.md'),all_source_before_after_equal=True,new_proof_actual_branch_fired=fired,physical_ready_or_launch_permission=False,old_files_or_gates_scores_modified=False,PH11pending=True))
 print(json.dumps(dict(status=result['status'],counts=COUNT,branch_fired=fired,result_path=str(O/'RESULT.json'),report_SHA=sha(O/'REPORT.md'),receipt_SHA=sha(O/'RECEIPT.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:
  O.mkdir(exist_ok=True);detail=traceback.format_exc();p=O/'FAILURE.txt'
  if not p.exists():p.write_text(detail,encoding='utf-8')
  p=O/'FAILURE_SOURCE.py'
  if not p.exists():p.write_bytes(Path(__file__).read_bytes())
  p=O/'FAILURE_RECEIPT.json'
  if not p.exists():p.write_text(json.dumps(dict(status='STOP_FIRST_V5_PROOF_ERROR_NO_FIX_OR_REPLAY',counts=COUNT,prefix=PREFIX,model_FK_PHY_oldQA_Git_agents=0,parent_decision_required=True,PH11pending=True),ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
  print(detail,file=sys.stderr);raise
