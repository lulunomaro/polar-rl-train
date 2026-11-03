"""NEW 3x500 fixed sensor-only math frames; not old QA/PHY. First failure stops."""
from pathlib import Path
import sys,json,math,struct,copy,traceback,shutil,collections,hashlib
from types import SimpleNamespace
O=Path(__file__).resolve().parent;ROOT=O.parent;sys.path.insert(0,str(ROOT))
import numpy as np
from sensor_core import LinkageGeometry
from sensor_core_jump_v1 import SensorPacket,rotation,quat_step
from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop as Base
from SPRING_PUSH_RELEASE_V1.controller import MiniHop as New
from SPRING_PUSH_DECOMPOSITION_V1.spring_push import load_precomputed
import ground_controller_v4 as gc
A=O/'unit_attempt_001';A.mkdir()
for n in('controller.py','binding.py','PREEXEC_UNIT_PLAN.json','SOURCE_LOCK.json','run_unit_once.py'):shutil.copyfile(O/n,A/n)
checks=0;geom_calls=0;Jcache={};phases=collections.Counter();rows=[];typed=0;formula_error=0.;first_push=None
book=load_precomputed();pub=json.loads((ROOT/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json').read_bytes())
def arrays(g):return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}
start=arrays(json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);end=arrays(json.loads((ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json').read_bytes())['gain']);landing=arrays(json.loads((ROOT/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_bytes())['gain'])
allbytes={(j,k):v.tobytes()for j,g in enumerate((start,end,landing))for k,v in g.items()if isinstance(v,np.ndarray)}
plan=json.loads((O/'PREEXEC_UNIT_PLAN.json').read_bytes());cfg=plan['config'];enabled=dict(cfg,release_spring_compensation_during_push=True)
def check(v,msg):
 global checks
 checks+=1
 if not bool(v):raise AssertionError(msg)
def same(a,b):
 if isinstance(a,np.ndarray)or isinstance(b,np.ndarray):return np.asarray(a).shape==np.asarray(b).shape and np.asarray(a).dtype==np.asarray(b).dtype and np.asarray(a).tobytes()==np.asarray(b).tobytes()
 if isinstance(a,dict):return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if isinstance(a,(tuple,list)):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 if isinstance(a,(float,np.floating)):return struct.pack('<d',float(a))==struct.pack('<d',float(b))
 return type(a)==type(b)and a==b
class Geometry(LinkageGeometry):
 def wheel_kinematics(self,h,c,hd,cd,spin,w,side):
  global geom_calls
  check(geom_calls<128,'Geometry128 before actual old call');geom_calls+=1
  r=super().wheel_kinematics(h,c,hd,cd,spin,w,side);Jcache[(side,float(h),float(c))]=r[2].copy();return r
geom=Geometry(pub['pins_xz_m'],radius=.0625)
clock=gc.time.perf_counter_ns;gc.time.perf_counter_ns=lambda:0
status='FAIL_FIRST_ATTEMPT';error=None;controllers=[]
try:
 controllers=[Base(start,end,geom,cfg,landing),New(start,end,geom,cfg,landing),New(start,end,geom,enabled,landing,start_gas_tau6=book.endpoint('crouch').tauGas6_Nm,end_gas_tau6=book.endpoint('pushend').tauGas6_Nm)]
 q0=controllers[0].q_start.copy();flags=[SimpleNamespace()for _ in controllers];prevq=None
 for k in range(500):
  now=k*.01;p=float(k%3-1);q=q0+.0008*p*np.array([1.,-1.,-1.,1.]);dq=np.zeros(4)if prevq is None else(q-prevq)/.01;prevq=q.copy()
  x=np.zeros(14);x[0]=.1*now;x[1]=.005*p;x[2]=.01*p;x[3]=q[0];x[4]=q[1]-q[0];x[5]=q[2];x[6]=q[3]-q[2];x[7]=.1;x[8]=.01*p;x[9]=.02*p;x[10]=dq[0];x[11]=dq[1]-dq[0];x[12]=dq[2];x[13]=dq[3]-dq[2]
  age=0. if k==0 else .01;omega=np.array([.02*p,.02*p,.01*p]);att=np.array([1.,0.,0.,0.]);e=SimpleNamespace(state14=x,roll=.01*p,omega_body=omega,sensor_age_s=age)
  packet=SensorPacket(now-age,now,omega.copy(),np.array([0.,0.,9.81]),q.copy(),dq.copy(),np.zeros(2));packet.validate();before=[a.tobytes()for a in(x,omega,att,packet.joint_pos4,packet.joint_vel4)]
  prelaunched=controllers[2].launched;out=[]
  for hop,f in zip(controllers,flags):hop.prepare_estimator(f,now);out.append(hop.command(e,packet,now,att,.1))
  b,d,on=controllers;phase=b.log['phase'];phases[phase]+=1
  check(phase!='INHIBIT','no synthetic fault');check(same(out[0],out[1]),'disabled torque bit parity');check(same(b.log,{key:d.log[key]for key in b.log}),'disabled legacy log parity')
  check(same(b.log,{key:on.log[key]for key in b.log}),'enabled targets/phase/legacy logs unchanged');check(same(vars(flags[0]),vars(flags[1]))and same(vars(flags[0]),vars(flags[2])),'prepare flags parity')
  for name in('ref','K','tau_eq','previous','yaw_integral','old_shaped_w','envelope_clips','valid_command'):
   check(same(getattr(b.ctrl,name),getattr(d.ctrl,name))and same(getattr(b.ctrl,name),getattr(on.ctrl,name)),'ground state '+name)
  for hop in controllers:check(hop.g is start and hop.end is end,'g/end identities restored')
  if phase=='timed_push':
   if first_push is None:first_push=dict(time_s=now,was_launched=prelaunched,applied=on.log['spring_release_applied_this_command']);check(not prelaunched and first_push['applied'],'first push overlay not gated by launched')
   since=now-on.trigger;u=float(np.clip(since/on.push,0.,1.));s=3*u*u-2*u*u*u;ds=6*u*(1-u)/on.push;target=(1-s)*on.q_start+s*on.q_end;vel=ds*(on.q_end-on.q_start)
   expected=(1-s)*np.asarray(book.endpoint('crouch').new_static_FF6_Nm)+s*np.asarray(book.endpoint('pushend').new_static_FF6_Nm)
   expected[[0,1,3,4]]+=300.*(target-q)+3.*(vel-dq);expected[[0,1,3,4]]=np.clip(expected[[0,1,3,4]],-32.,32.)
   expected[[2,5]]=25.*x[2]+4.*x[9];moment=float(np.clip(-40.*e.roll-5.*omega[0],-8.,8.));rot=rotation(quat_step(att,omega,age))
   for side,ix,qq in(('left',[0,1],q[:2]),('right',[3,4],q[2:])):expected[ix]-=Jcache[(side,float(qq[0]),float(qq[1]))].T@(rot.T@np.array([0.,0.,moment/.4376*(1. if side=='left'else -1.)]))
   diff=float(np.clip(-1.2*x[8]-.4*x[1],-.5,.5));expected[2]-=diff;expected[5]+=diff;expected=np.clip(expected,-np.array([40.,40.,5.775909774436091]*2),np.array([40.,40.,5.775909774436091]*2))
   err=float(np.max(np.abs(expected-out[2])));formula_error=max(formula_error,err);check(err<=1e-12,'original push FF/PD32/roll/yaw/final40 formula')
   check(same(out[0][[2,5]],out[2][[2,5]]),'push wheels same input bit parity')
   check(np.shares_memory(on.ctrl.tau_eq,start['tau']),'ground tau_eq original alias not overlay')
  else:check(same(out[0],out[2]),'enabled nonpush same-input equation output parity')
  check([a.tobytes()for a in(x,omega,att,packet.joint_pos4,packet.joint_vel4)]==before,'sensor inputs unchanged')
  rows.append(dict(k=k,phase=phase,requested_off=out[1].tolist(),requested_on=out[2].tolist(),spring_delta=on.log['nominal_endpoint_feedforward_delta6_before_PD_clip']))
 check(sum(phases.values())==500 and all(phases[k]>0 for k in('supported_approach','timed_push','predicted_flight_retract','timed_capture')),'measured all phase counts')
 check(controllers[0].scheduler.latch_time==controllers[0].scheduler.decision_time+.01,'position next tick')
 for label,gas,feature in [('missing',None,True),('shape',[0.]*5,True),('nan',[float('nan')]*6,True),('inf',[float('inf')]*6,True),('bool',[True]*6,True),('complex',[1j]*6,True),('wheel',[0.,0.,1.,0.,0.,0.],True),('flag',None,1)]:
  typed+=1
  try:New(start,end,geom,dict(cfg,release_spring_compensation_during_push=feature),landing,start_gas_tau6=gas,end_gas_tau6=gas)
  except ValueError:check(True,'typed '+label)
  else:check(False,'bad ctor '+label)
 # One guard case on the existing instance; no second500 replay or extra geometry.
 hop=controllers[2];saved=(hop.g,hop.end);hop.fault=False;hop.launched=False;hop.last_time=None;hop.position_active=False;xx=x.copy();xx[2]=.2;bad=SimpleNamespace(state14=xx,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
 typed+=1;guard=hop.command(bad,packet,hop.trigger,np.array([1.,0.,0.,0.]));check(hop.fault and hop.log['phase']=='INHIBIT'and np.all(guard==0.),'original trigger guard remains');check((hop.g,hop.end)==saved,'guard finally restores gains')
 # A deliberate inner exception verifies finally, without re-running Base logic.
 oldcommand=Base.command;hop.fault=False
 def explode(*a,**kw):raise RuntimeError('EXPECTED_INNER_EXCEPTION')
 Base.command=explode
 try:
  try:hop.command(e,packet,hop.trigger+.01,att)
  except RuntimeError:check(hop.g is saved[0]and hop.end is saved[1],'exception finally restoration')
  else:check(False,'expected inner exception')
 finally:Base.command=oldcommand
 check(all(g[k].tobytes()==v for(j,k),v in allbytes.items()for g in[(start,end,landing)[j]]),'all original gain array bytes unchanged')
 check(typed<=20 and geom_calls<=128,'typed/geometry caps');check(not any(n=='mujoco'or n.startswith('mujoco.')or n.endswith('nominal_model')for n in sys.modules),'no SDK/NominalModel imported')
 status='PASS_NEW_500X3_SYNTHETIC_NOT_PHY'
except Exception:error=traceback.format_exc()
finally:gc.time.perf_counter_ns=clock
result=dict(status=status,checks=checks,error=error,frames_each=500,phase_counts=dict(phases),Geometry_wheel_kinematics_calls=geom_calls,internal_planar_pose_calls=5*geom_calls,NominalModel_FK=0,MuJoCo_boot_forward_RNE_step=0,typed_cases=typed,first_push=first_push,formula_max_abs_error_Nm=formula_error,oldQA_replayed=False,source_SHA=hashlib.sha256((O/'run_unit_once.py').read_bytes()).hexdigest(),core_SHA=hashlib.sha256((O/'controller.py').read_bytes()).hexdigest())
for n,val in [('UNIT_RESULT.json',result),('UNIT_ROWS.json',rows)]:
 with(O/n).open('x',encoding='utf-8')as f:json.dump(val,f,indent=2,allow_nan=False)
print(json.dumps(result,indent=2))
if error:raise SystemExit(1)
