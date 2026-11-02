"""Frozen H2 Python64 numerical references. No physics/heldout/R27 imports."""
from pathlib import Path
import sys,json,math,csv,ast,hashlib,traceback
import numpy as np
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(WORK))
freeze=json.loads((HERE/'SOURCE_FREEZE.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for r in freeze['sources']+freeze['TRAIN']:assert sha(Path(r['path']))==r['sha256']
import sensor_core_v4 as sensor
from spin_base_v1 import GroundController as SpinBase
from spin_center_torque_v2 import GroundController as SpinH2
from robot_geometry_constants_v1 import PINS,TRACK
assert not any(k=='mujoco' or k.startswith('physics_bridge') for k in sys.modules)
GAIN0=json.loads((WORK/'nominal_gain_v1.json').read_text())['gain'];GAIN={k:np.asarray(v,float) if k in ['q','tau','K','A','B','Ad','Bd','P','Q','R'] else v for k,v in GAIN0.items()}
CONFIG=freeze['H2_controller'];RADIUS=.06369999796152115

def q32(a):return np.asarray(a,dtype=np.float32).astype(float)
class MatchedGeometry(sensor.LinkageGeometry):
 def wheel_kinematics(self,hip,crank,hipdot,crankdot,spin,omega,side):
  r,knee=self.pose(hip,crank,side);eps=float(np.float32(.001));der=[]
  for dh,dc in [(eps,0),(0,eps)]:
   a,ka=self.pose(hip+dh,crank+dc,side);b,kb=self.pose(hip-dh,crank-dc,side);der.append(np.r_[(a-b)/(2*eps),sensor.wrap(ka-kb)/(2*eps)])
  J=np.asarray(der).T;dq=np.array([hipdot,crankdot]);v=J[:3]@dq;kneedot=float(J[3]@dq);return self.radius*(omega[1]+hipdot+kneedot+spin)-v[0]-np.cross(omega,r)[0],r,J[:3],knee

def geometry(matched):
 pins={s:{k:(q32(v) if matched else np.asarray(v,float)) for k,v in p.items()} for s,p in PINS.items()}
 return MatchedGeometry(pins,float(np.float32(TRACK)),float(np.float32(RADIUS))) if matched else sensor.LinkageGeometry(pins,TRACK,RADIUS)
def estimator(matched,offset):return sensor.StateEstimator(geometry(matched),q32(offset) if matched else offset,0.,float(np.float32(.065)) if matched else .065,.5,'wheel_midpoint',1.,True)
def controller(matched,base=False):
 c=(SpinBase if base else SpinH2)(GAIN,CONFIG);assert np.max(np.abs(c.K-GAIN['K']))<1e-9
 if matched:
  c.K=q32(GAIN['K']);c.eq=q32(np.r_[GAIN['q'],np.zeros(7)]);c.tau_eq=q32(GAIN['tau']);c.ref=c.eq.copy();c.ref[:2]=0;c.previous=c.tau_eq.copy()
  if not base:c.geo=geometry(True);c.lead=float(np.float32(CONFIG['center_lead_s']));c.kt=float(np.float32(20.));c.tcap=float(np.float32(1.8))
 if not base:assert c.cap==0
 return c

def diag(c,e):
 log=c.center_log;target=log['target_pivot_xy'];psi=e.state14[1]+e.state14[8]*c.lead;error=np.asarray(log['error_xy']);projection=float(error@np.array([math.cos(psi),math.sin(psi)])) if log['active'] else 0
 pivot=np.mean([c.geo.pose(e.state14[2*j+3],e.state14[2*j+3]+e.state14[2*j+4],s)[0] for j,s in enumerate(['left','right'])],axis=0)
 return {'xy':log['estimated_root_xy'],'pivot_xy':log['estimated_pivot_xy'],'target':[0.,0.] if target is None else target,'error':error,'body_pivot':pivot,'vy':log['no_side_slip_vy'],'projection':projection,'corr':log['centering_torque_Nm'],'active':int(log['active']),'target_valid':int(target is not None)}
def train_case():
 records=[]
 for line in (WORK/'results/r11_k20_201/trace.jsonl').read_bytes().splitlines():
  r=json.loads(line);records.append({'t':r['sensor_timestamp_s'],'now':r['estimate_time'],'gyro':r['raw_gyro'],'acc':r['raw_accel'],'q':r['encoder4'],'dq':r['encoder_rate4'],'spin':r['wheel_rate2'],'v':r['request'][0],'w':r['request'][1],'logged14':r['estimated14'],'logged_tau':r['raw_requested_tau'],'logged_center':r['spin_center']})
 return {'name':'TRAIN_R11_k20_201','offset':[.03,0,.04],'window_metadata_from_uniform_sim_source':True,'records':records}
def ramp_piece(t,start,stop,sign):
 if t<start or t>=stop+4*math.pi/6:return 0.
 return sign*min(4*math.pi,max(0.,6*(t-start)),max(0.,6*(stop+4*math.pi/6-t)))
def synthetic_cases():
 geo=geometry(False);baseq=np.array([GAIN['q'][3],GAIN['q'][3]+GAIN['q'][4],GAIN['q'][5],GAIN['q'][5]+GAIN['q'][6]])
 for kind,count,lag in [('start_stop_reverse',2600,0.),('direct_reverse',1200,0.),('thresholds',400,0.),('age_view_proxy',400,.02)]:
  records=[];offset=[.06,-.02,.08];qtrue=np.array([1.,0,0,0]);previous=None;previous_t=None
  for i in range(count):
   now=i*.01;t=max(0.,now-lag);q=baseq.copy();dq=np.zeros(4);omega=np.zeros(3);v=.08*math.sin(.3*t);dv=.024*math.cos(.3*t);forward=0.
   if kind=='start_stop_reverse':
    request=(4*math.pi if 1<=now<7 or now>=20 else (-4*math.pi if 10<=now<16 else 0.));omega[2]=ramp_piece(t,1,7,1)+ramp_piece(t,10,16,-1)+ramp_piece(t,20,100,1)
   elif kind=='direct_reverse':request=4*math.pi if now<4 or now>=8 else -4*math.pi;omega[2]=4*math.pi*math.cos(math.pi*t/4)
   elif kind=='thresholds':
    block=i//80;request=[3.9,4.,4.1,-4.1,0.][block];forward=[0.,0.,.09,.1,.11][block];omega[2]=.5*math.sin(.5*t)
   else:request=4*math.pi;omega[2]=4*math.pi
   q[0]+=.02*math.sin(1.3*t);q[1]+=.01*math.sin(1.1*t);q[2]+=.016*math.sin(.9*t);q[3]+=.009*math.sin(1.4*t);dq=np.array([.026*math.cos(1.3*t),.011*math.cos(1.1*t),.0144*math.cos(.9*t),.0126*math.cos(1.4*t)])
   fresh=previous_t is None or t>previous_t+1e-10;dt=0. if previous_t is None or not fresh else t-previous_t
   alpha=np.zeros(3) if previous is None or not fresh else (omega-previous)/dt
   if fresh:qtrue=sensor.quat_step(qtrue,omega,dt)
   pivot=np.mean([geo.pose(q[2*j],q[2*j+1],s)[0] for j,s in enumerate(['left','right'])],axis=0)
   proper=sensor.G*sensor.rotation(qtrue).T[:,2]-np.cross(alpha,pivot)-np.cross(omega,np.cross(omega,pivot))+np.array([dv,omega[2]*v,0.])
   acc=proper+np.cross(alpha,offset)+np.cross(omega,np.cross(omega,offset));spin=[]
   for j,s in enumerate(['left','right']):spin.append((v-geo.wheel_kinematics(q[2*j],q[2*j+1],dq[2*j],dq[2*j+1],0,omega,s)[0])/RADIUS)
   records.append({'t':t,'now':now,'gyro':omega.tolist(),'acc':acc.tolist(),'q':q.tolist(),'dq':dq.tolist(),'spin':spin,'v':forward,'w':request})
   if fresh:previous=omega.copy();previous_t=t
  yield {'name':'SYNTH_'+kind,'offset':offset,'window_metadata_from_uniform_sim_source':False,'records':records}

SPEC={};NAMES=[]
def add(name,n=1):SPEC[name]=(len(NAMES),n);NAMES.extend([name] if n==1 else [f'{name}_{i}' for i in range(n)])
for name,n in [('CASE',1),('FIRST',1),('STAMP',1),('NOW',1),('SEQ',1),('MEAN_MODE',1),('MEAN_COUNT',1),('WINDOW_BEGIN',1),('OFFSET',3),('GYRO',3),('ACCEL',3),('Q4',4),('DQ4',4),('SPIN2',2),('FORWARD',1),('YAW',1),('ORIGINAL_X14',14),('MATCHED_X14',14),('ROLL',1),('ORIGINAL_TAU',6),('MATCHED_TAU',6),('ISOLATED_TAU',6),('BASE_TAU',6),('XY',2),('PIVOT_XY',2),('TARGET_XY',2),('ERROR_XY',2),('BODY_PIVOT',3),('VY',1),('PROJECTION',1),('CENTER_REQUEST',1),('ACTIVE',1),('TARGET_VALID',1),('ISO_XY',2),('ISO_PIVOT_XY',2),('ISO_TARGET_XY',2),('ISO_ERROR_XY',2),('ISO_VY',1),('ISO_PROJECTION',1),('ISO_CENTER_REQUEST',1),('ISO_REF14',14),('ISO_SHAPER',4)]:add(name,n)
def main():
 assert not (HERE/'REFERENCE_H2.csv').exists();cases=[train_case()]+list(synthetic_cases());meta=[];total=0
 with (HERE/'REFERENCE_H2.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.writer(f);writer.writerow(NAMES)
  for sid,case in enumerate(cases):
   so=estimator(False,case['offset']);sm=estimator(True,case['offset']);co=controller(False);cm=controller(True);ci=controller(True);cb=controller(True,base=True);maxlog14=maxlogtau=maxlogcenter=0.
   for index,r in enumerate(case['records']):
    stamp=int(round(r['t']*1e6));now=int(round(r['now']*1e6));po=sensor.SensorPacket(r['t'],r['now'],np.asarray(r['gyro']),np.asarray(r['acc']),np.asarray(r['q']),np.asarray(r['dq']),np.asarray(r['spin']));pm=sensor.SensorPacket(stamp*1e-6,now*1e-6,q32(r['gyro']),q32(r['acc']),q32(r['q']),q32(r['dq']),q32(r['spin']));eo=so.update(po);em=sm.update(pm)
    to=co.command(eo,r['v'],r['w']);tm=cm.command(em,float(np.float32(r['v'])),float(np.float32(r['w'])));tb=cb.command(em,float(np.float32(r['v'])),float(np.float32(r['w'])));ei=sensor.Estimate(q32(em.state14),float(np.float32(em.roll)),q32(em.omega_body),q32(em.proper_acc_origin),em.velocity_variance,q32(em.measured_wheel_forward2),em.sensor_age_s,em.estimated_time_s,em.slip_innovation,em.contact_confidence);ti=ci.command(ei,float(np.float32(r['v'])),float(np.float32(r['w'])));dm=diag(cm,em);di=diag(ci,ei)
    if 'logged14' in r:
     maxlog14=max(maxlog14,float(np.max(np.abs(eo.state14-r['logged14']))));maxlogtau=max(maxlogtau,float(np.max(np.abs(to-r['logged_tau']))))
     lc=r['logged_center'];oc=co.center_log
     for key in ['estimated_root_xy','estimated_pivot_xy','error_xy'] :maxlogcenter=max(maxlogcenter,float(np.max(np.abs(np.asarray(oc[key])-lc[key]))))
     if lc['target_pivot_xy'] is not None:maxlogcenter=max(maxlogcenter,float(np.max(np.abs(np.asarray(oc['target_pivot_xy'])-lc['target_pivot_xy']))))
     maxlogcenter=max(maxlogcenter,abs(oc['no_side_slip_vy']-lc['no_side_slip_vy']),abs(oc['centering_torque_Nm']-lc['centering_torque_Nm']));assert oc['active']==lc['active']
    mean=case['window_metadata_from_uniform_sim_source'] and stamp>=10000
    groups=[sid,int(index==0),stamp,now,stamp//10000+1,int(mean),20 if mean else 1,stamp-10000 if mean else stamp,case['offset'],r['gyro'],r['acc'],r['q'],r['dq'],r['spin'],r['v'],r['w'],eo.state14,em.state14,em.roll,to,tm,ti,tb,dm['xy'],dm['pivot_xy'],dm['target'],dm['error'],dm['body_pivot'],dm['vy'],dm['projection'],dm['corr'],dm['active'],dm['target_valid'],di['xy'],di['pivot_xy'],di['target'],di['error'],di['vy'],di['projection'],di['corr'],ci.ref,[ci.shaper.v,ci.shaper.w,ci.shaper.a,ci.yaw_integral]];values=[]
    for g in groups:
     if isinstance(g,(list,tuple,np.ndarray)):values.extend(float(v) for v in g)
     else:values.append(float(g))
    assert len(values)==len(NAMES) and np.isfinite(values).all();writer.writerow(format(v,'.17g') for v in values);total+=1
   if case['name'].startswith('TRAIN_'):assert maxlog14<1e-7 and maxlogtau<1e-7 and maxlogcenter<1e-7,(maxlog14,maxlogtau,maxlogcenter)
   meta.append({k:v for k,v in case.items() if k!='records'}|{'rows':len(case['records']),'logged14_max_abs':maxlog14,'logged_tau_max_abs':maxlogtau,'logged_center_max_abs':maxlogcenter})
 assert not any(k=='mujoco' or k.startswith('physics_bridge') for k in sys.modules)
 h=['#ifndef SH2_VECTOR_LAYOUT_H','#define SH2_VECTOR_LAYOUT_H',f'#define SH2_VECTOR_COLUMNS {len(NAMES)}u']+[f'#define SH2_COL_{name} {offset}u' for name,(offset,n) in SPEC.items()]+['#endif'];(HERE/'sh2_vector_layout.h').write_text('\n'.join(h)+'\n',encoding='utf-8')
 report={'rows':total,'columns':NAMES,'offsets':SPEC,'cases':meta,'source_nominalK_max_difference':float(np.max(np.abs(co.K-GAIN['K']))),'source_velocity_center_cap':co.cap,'dispatcher':'deferred','physics_steps':0,'physical_reverse_start_stop_qualified':False};(HERE/'REFERENCE_LAYOUT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'rows':total,'columns':len(NAMES),'cases':meta,'no_physics':True},indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'reference_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
