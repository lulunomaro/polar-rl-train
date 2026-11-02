"""Offline frozen Python64 math reference. NEVER imports a plant/MuJoCo.
Two fixed TRAIN streams + preregistered synthetic numerical packet sequences.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,json,math,csv,hashlib,traceback
import numpy as np
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def q32(a):return np.asarray(a,dtype=np.float32).astype(float)
freeze=json.loads((HERE/'SOURCE_FREEZE.json').read_text(encoding='utf-8'))
for record in freeze['sources']+freeze['fixed_train_inputs']:assert sha(Path(record['path']))==record['sha256']
sys.path.insert(0,str(WORK))
import sensor_core_v4 as sensor
import ground_controller_v4 as control
assert 'mujoco' not in sys.modules and not any(k.startswith('physics_bridge') for k in sys.modules)
constants={}
for node in ast.parse((WORK/'robot_geometry_constants_v1.py').read_text(encoding='utf-8')).body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name):constants[target.id]=ast.literal_eval(node.value)
PINS=constants['PINS'];TRACK=constants['TRACK'];RADIUS=json.loads((WORK/'nominal_gain_v1.json').read_text())['wheel_chart_radius_m']
GAIN_RAW=json.loads((WORK/'nominal_gain_v1.json').read_text())['gain'];GAIN={k:np.asarray(v,float) if k in ['q','tau','K','A','B','Ad','Bd','P','Q','R'] else v for k,v in GAIN_RAW.items()}
PACK=json.loads((WORK/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_text());CONFIG=PACK['controller']
class ParameterMatchedGeometry(sensor.LinkageGeometry):
 def wheel_kinematics(self,hip,crank,hipdot,crankdot,spin,omega,side):
  r,knee=self.pose(hip,crank,side);eps=float(np.float32(.001));der=[]
  for dh,dc in [(eps,0),(0,eps)]:
   a,ka=self.pose(hip+dh,crank+dc,side);b,kb=self.pose(hip-dh,crank-dc,side);der.append(np.r_[(a-b)/(2*eps),sensor.wrap(ka-kb)/(2*eps)])
  J=np.asarray(der).T;dq=np.array([hipdot,crankdot]);relative=J[:3]@dq;kneedot=float(J[3]@dq)
  return self.radius*(omega[1]+hipdot+kneedot+spin)-relative[0]-np.cross(omega,r)[0],r,J[:3],knee

def geometry(matched,radius):
 pins={s:{k:(q32(v) if matched else np.asarray(v,float)) for k,v in p.items()} for s,p in PINS.items()}
 return ParameterMatchedGeometry(pins,float(np.float32(TRACK)),float(np.float32(radius))) if matched else sensor.LinkageGeometry(pins,TRACK,radius)
def new_controller(matched):
 c=control.GroundController(GAIN,CONFIG);assert np.max(np.abs(c.K-np.asarray(PACK['K_6x14'])))<1e-9
 if matched:
  c.K=q32(PACK['K_6x14']);c.eq=q32(PACK['eq14']);c.tau_eq=q32(PACK['tau_eq6']);c.ref=c.eq.copy();c.ref[:2]=0;c.previous=c.tau_eq.copy()
 return c
class Reference:
 def __init__(self,matched,arm,ref,correction,offset,radius):
  self.geo=geometry(matched,radius);self.est=sensor.StateEstimator(self.geo,q32(offset) if matched else offset,correction,float(np.float32(.065)) if matched else .065,.5,'wheel_midpoint' if ref else 'chassis',1.,arm==1);self.diag=None
 def update(self,p):
  previous_stamp=self.est.prev_stamp;qpre=None if self.est.q is None else self.est.q.copy();vbpre=self.est.vb.copy();e=self.est.update(p)
  if previous_stamp is not None and p.time_s<=previous_stamp+1e-10:return e,self.diag
  proper=e.proper_acc_origin;omega=p.gyro_body;pivot=np.mean([self.geo.pose(p.joint_pos4[2*j],p.joint_pos4[2*j+1],side)[0] for j,side in enumerate(['left','right'])],axis=0)
  if qpre is None:
   norm=np.linalg.norm(proper);roll=math.atan2(proper[1],proper[2]);pitch=math.atan2(-proper[0],math.hypot(proper[1],proper[2]))
   if self.est.upright_prior or abs(norm-sensor.G)>.3*sensor.G:roll=pitch=0
   qpre=sensor.quat_from_rpy(roll,pitch,0)
  rotation=np.cross(self.est.alpha,pivot)+np.cross(omega,np.cross(omega,pivot)) if self.est.accel_reference=='wheel_midpoint' else np.zeros(3)
  candidate=proper+rotation-np.array([self.est.wheel_acc,omega[2]*vbpre[0],0]);cn=float(np.linalg.norm(candidate));innovation=float(np.linalg.norm(candidate-sensor.G*sensor.rotation(qpre).T[:,2]));conf_n=max(0.,1-abs(cn-sensor.G)/(sensor.G*.35));conf_v=max(0.,1-innovation)
  linear=proper+sensor.rotation(self.est.q).T@np.array([0.,0.,-sensor.G]);transverse=-np.cross(omega,pivot);ax=linear[0]
  if self.est.accel_reference=='wheel_midpoint':ax+=omega[2]*transverse[1]-omega[1]*transverse[2]
  self.diag={'P':self.est.P.ravel().copy(),'alpha':self.est.alpha.copy(),'pivot':pivot,'proxy':transverse[1],'linear':linear,'vxacc':ax,'conf':[conf_n,conf_v,conf_n*conf_v,innovation],'q':self.est.q.copy(),'wheel_acc':self.est.wheel_acc,'bias':self.est.vb[1]}
  return e,self.diag

def packet(t,now,gyro,acc,q,dq,spin):return sensor.SensorPacket(float(t),float(now),np.asarray(gyro,float),np.asarray(acc,float),np.asarray(q,float),np.asarray(dq,float),np.asarray(spin,float))
def raw_scenarios():
 for name in ['r04_spin_gyro_202','r11_k20_201']:
  rows=[json.loads(s) for s in (WORK/'results'/name/'trace.jsonl').read_bytes().splitlines()];records=[]
  for row in rows:
   records.append({'stamp':row['sensor_timestamp_s'],'now':row['estimate_time'],'gyro':row['raw_gyro'],'acc':row['raw_accel'],'q':row['encoder4'],'dq':row['encoder_rate4'],'spin':row['wheel_rate2'],'forward':0.,'yaw':4*math.pi if row['estimate_time']>=1-1e-8 else 0.,'logged14':row['estimated14']})
  yield {'name':'TRAIN_'+name,'arm':1,'reference':1,'correction':0.,'offset':[.03,0,.04],'radius':RADIUS,'records':records,'mean_from_uniform_sim_source':True}
def synthetic_scenarios():
 baseq=np.array([PACK['eq14'][3],PACK['eq14'][3]+PACK['eq14'][4],PACK['eq14'][5],PACK['eq14'][5]+PACK['eq14'][6]])
 for kind,count in [('stationary',120),('static_tilt',120),('vector_gate',160),('pivot_spin',360),('aged_dynamic',240),('lever_3d',200),('envelope',400)]:
  arm=2 if kind=='static_tilt' else 1;ref=0 if kind in ['static_tilt','aged_dynamic','lever_3d'] else 1;offset=[.06,-.02,.08] if kind in ['static_tilt','lever_3d'] else [.03,0,.04];radius=.0625 if kind=='static_tilt' else RADIUS;geo=geometry(False,radius);records=[];trueq=sensor.quat_from_rpy(.05,.04,0) if kind=='lever_3d' else sensor.quat_from_rpy(0,0,0);previous_w=None;previous_t=None
  for i in range(count):
   now=i*.01;t=max(0.,now-.02) if kind=='aged_dynamic' else now;q=baseq.copy();dq=np.zeros(4);omega=np.zeros(3);proper=np.array([0.,0.,sensor.G]);spin=np.zeros(2);forward=yaw=0.
   if kind=='static_tilt':proper=sensor.G*sensor.rotation(sensor.quat_from_rpy(.12,-.08,0)).T[:,2]
   if kind=='vector_gate' and i>=50:proper=np.array([sensor.G*math.sin(.15),0,sensor.G*math.cos(.15)])
   if kind=='pivot_spin':
    omega[2]=4*math.pi;pivot=np.mean([geo.pose(q[2*j],q[2*j+1],side)[0] for j,side in enumerate(['left','right'])],axis=0);proper-=np.cross(omega,np.cross(omega,pivot));yaw=4*math.pi
   if kind=='aged_dynamic':
    omega[2]=.5*math.sin(.7*t);q[0]+=.01*math.sin(.3*t);q[1]+=.006*math.sin(.5*t);q[2]+=.008*math.sin(.4*t);q[3]+=.004*math.sin(.6*t);dq=np.array([.003*math.cos(.3*t),.003*math.cos(.5*t),.0032*math.cos(.4*t),.0024*math.cos(.6*t)]);v=.3*math.sin(.4*t);proper=np.array([.12*math.cos(.4*t),omega[2]*v,sensor.G]);forward=.6*math.sin(.25*now);yaw=.7*math.sin(.4*now)
   else:v=0.
   if kind=='lever_3d':
    omega=np.array([.05*math.sin(.5*t),.03*math.cos(.7*t),.2*math.sin(.9*t)]);trueq=sensor.quat_step(trueq,omega,0 if i==0 else .01);proper=sensor.G*sensor.rotation(trueq).T[:,2];forward=.2*math.sin(.5*now);yaw=.4*math.sin(.8*now)
   if kind=='envelope':q[0]+=.02;q[2]-=.01;forward=20 if i<250 else -20;yaw=40 if i<200 else -40
   alpha=np.zeros(3) if previous_w is None or t==previous_t else (omega-previous_w)/(t-previous_t)
   acc=proper+np.cross(alpha,offset)+np.cross(omega,np.cross(omega,offset))
   if kind in ['pivot_spin','aged_dynamic','lever_3d']:
    for j,side in enumerate(['left','right']):
     v0=geo.wheel_kinematics(q[2*j],q[2*j+1],dq[2*j],dq[2*j+1],0,omega,side)[0];spin[j]=(v-v0)/radius
   records.append({'stamp':t,'now':now,'gyro':omega.tolist(),'acc':acc.tolist(),'q':q.tolist(),'dq':dq.tolist(),'spin':spin.tolist(),'forward':forward,'yaw':yaw})
   previous_w=omega.copy();previous_t=t
  yield {'name':'SYNTH_'+kind,'arm':arm,'reference':ref,'correction':1.5,'offset':offset,'radius':radius,'records':records,'mean_from_uniform_sim_source':False}

FIELDS={};columns=[]
def add(name,n=1):
 FIELDS[name]=(len(columns),n);columns.extend([name] if n==1 else [f'{name}_{i}' for i in range(n)])
for name,n in [('SCENARIO',1),('FIRST',1),('ARM',1),('ACCREF',1),('ACC_CORR',1),('OFFSET',3),('RADIUS',1),('STAMP',1),('NOW',1),('SEQUENCE',1),('MEAN_MODE',1),('MEAN_COUNT',1),('WINDOW_BEGIN',1),('GYRO',3),('ACCEL',3),('Q4',4),('DQ4',4),('SPIN2',2),('FORWARD',1),('YAW_COMMAND',1),('FROZEN_X14',14),('PARAM_X14',14),('ROLL',1),('PROPER',3),('P4',4),('WHEEL2',2),('SLIP',1),('CONTACT',1),('ALPHA',3),('PIVOT',3),('PROXY',1),('LINEAR',3),('VX_ACCEL',1),('CONF4',4),('QUAT',4),('WHEEL_ACC',1),('BIAS',1),('FROZEN_TAU',6),('PARAM_TAU',6),('ISOLATED_TAU',6),('ISOLATED_REF14',14),('ISOLATED_SHAPER',4)]:add(name,n)
def main():
 assert not (HERE/'REFERENCE_VECTORS.csv').exists(),'Preserve original vectors'
 definitions=list(raw_scenarios())+list(synthetic_scenarios());meta=[];total=0
 with (HERE/'REFERENCE_VECTORS.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.writer(f);writer.writerow(columns)
  for sid,d in enumerate(definitions):
   original=Reference(False,d['arm'],d['reference'],d['correction'],d['offset'],d['radius']);matched=Reference(True,d['arm'],d['reference'],d['correction'],d['offset'],d['radius']);co=new_controller(False);cm=new_controller(True);ci=new_controller(True);logged_max=0.;rows=0
   for i,r in enumerate(d['records']):
    ts=int(round(r['stamp']*1e6));now=int(round(r['now']*1e6));p=packet(r['stamp'],r['now'],r['gyro'],r['acc'],r['q'],r['dq'],r['spin']);pm=packet(ts*1e-6,now*1e-6,q32(r['gyro']),q32(r['acc']),q32(r['q']),q32(r['dq']),q32(r['spin']));eo,do=original.update(p);em,dm=matched.update(pm)
    if 'logged14' in r:logged_max=max(logged_max,float(np.max(np.abs(eo.state14-r['logged14']))))
    to=co.command(eo,r['forward'],r['yaw']);tm=cm.command(em,float(np.float32(r['forward'])),float(np.float32(r['yaw'])));ei=sensor.Estimate(q32(em.state14),float(np.float32(em.roll)),q32(em.omega_body),q32(em.proper_acc_origin),float(np.float32(em.velocity_variance)),q32(em.measured_wheel_forward2),em.sensor_age_s,em.estimated_time_s,em.slip_innovation,em.contact_confidence);ti=ci.command(ei,float(np.float32(r['forward'])),float(np.float32(r['yaw'])))
    mean=bool(d['mean_from_uniform_sim_source'] and ts>=10000);values=[]
    groups=[sid,int(i==0),d['arm'],d['reference'],d['correction'],d['offset'],d['radius'],ts,now,ts//10000+1,int(mean),20 if mean else 1,ts-10000 if mean else ts,r['gyro'],r['acc'],r['q'],r['dq'],r['spin'],r['forward'],r['yaw'],eo.state14,em.state14,em.roll,em.proper_acc_origin,dm['P'],em.measured_wheel_forward2,em.slip_innovation,em.contact_confidence,dm['alpha'],dm['pivot'],dm['proxy'],dm['linear'],dm['vxacc'],dm['conf'],dm['q'],dm['wheel_acc'],dm['bias'],to,tm,ti,ci.ref,[ci.shaper.v,ci.shaper.w,ci.shaper.a,ci.yaw_integral]]
    for group in groups:
     if isinstance(group,(list,tuple,np.ndarray)):values.extend(float(x) for x in group)
     else:values.append(float(group))
    assert len(values)==len(columns) and np.isfinite(values).all();writer.writerow(format(v,'.17g') for v in values);rows+=1;total+=1
   if d['name'].startswith('TRAIN_'):assert logged_max<1e-7,(d['name'],logged_max)
   meta.append({k:v for k,v in d.items() if k!='records'}|{'rows':rows,'frozen_Python64_vs_logged14_max_abs':logged_max})
 layout=['#ifndef PC3_VECTOR_LAYOUT_H','#define PC3_VECTOR_LAYOUT_H',f'#define PC3_VECTOR_COLUMNS {len(columns)}u']
 for name,(offset,n) in FIELDS.items():layout.append(f'#define PC3_COL_{name} {offset}u')
 layout.append('#endif');(HERE/'pc3_vector_layout.h').write_text('\n'.join(layout)+'\n',encoding='utf-8')
 assert not any(k=='mujoco' or k.startswith('mujoco.') or k.startswith('physics_bridge') for k in sys.modules)
 dump('REFERENCE_LAYOUT.json',{'columns':columns,'offsets':FIELDS,'reference':'original frozen V4/DARE P25 + config/pins/eps/K quantized float64 reference and isolated-controller reference','cases':meta,'rows':total,'mujoco_loaded':False,'physics_steps':0,'H2_feedback_ported':False,'P25_K_vs_recomputed_DARE_max':float(np.max(np.abs(co.K-np.asarray(PACK['K_6x14']))))})
 print(json.dumps({'rows':total,'columns':len(columns),'scenarios':meta,'P25_K_source_check':True,'mujoco_loaded':False,'physics_steps':0},indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'reference_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
