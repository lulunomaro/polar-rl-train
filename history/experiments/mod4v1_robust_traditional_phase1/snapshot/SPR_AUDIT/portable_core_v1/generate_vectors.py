"""Independent Python stdlib reference vectors; no frozen-source import/exec.
Only algebraic sensor fixtures, not a plant/robot simulator or training job.
All generated files stay beside this script. Source provenance is read-only.
"""
from pathlib import Path
import hashlib, json, math, random, traceback
ROOT=Path(__file__).resolve().parent
FROZEN=ROOT.parents[1]/'source_snapshots'/'r00'/'sensor_core.py'
HAL=ROOT.parent/'portable_hal_proposal.h'

def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):return math.sqrt(sum(x*x for x in a))
def clip(x,lo,hi):return min(hi,max(lo,x))
def mul(a,b):
 w,x,y,z=a;v,i,j,k=b
 return [w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v]
def qfrom(r,p,y):
 cr,sr=math.cos(r/2),math.sin(r/2);cp,sp=math.cos(p/2),math.sin(p/2);cy,sy=math.cos(y/2),math.sin(y/2)
 return [cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy]
def step(q,w,dt):
 a=[x*dt for x in w];n=norm(a);k=math.sin(n/2)/n if n>1e-12 else .5
 out=mul(q,[math.cos(n/2)]+[x*k for x in a]);return [x/norm(out) for x in out]
def rotation(q):
 w,x,y,z=q
 return [1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]
def rpy(q):
 R=rotation(q);return [math.atan2(R[7],R[8]),math.atan2(-R[6],math.hypot(R[0],R[3])),math.atan2(R[3],R[0])]
def wrap(x):return math.atan2(math.sin(x),math.cos(x))
def lever(f,w,a,r):
 ar=cross(a,r);wwr=cross(w,cross(w,r));return [f[i]-ar[i]-wwr[i] for i in range(3)]

class Observer:
 def __init__(self):
  self.q=None;self.prev=None;self.wprev=None;self.alpha=[0.,0.,0.];self.wp=0.;self.wa=0.;self.vb=[0.,0.];self.P=[.05,0.,0.,.1];self.yaw=0.;self.yawprev=0.;self.dist=0.;self.offset=[.03,-.02,.04]
 def update(self,p):
  dt=0. if self.prev is None else (p['stamp']-self.prev)*1e-6;w=p['gyro']
  if self.wprev is not None:self.alpha=[a+dt/(.06+dt)*((w[i]-self.wprev[i])/dt-a) for i,a in enumerate(self.alpha)]
  proper=lever(p['proper'],w,self.alpha,self.offset)
  if self.q is None:
   u=[x/max(norm(proper),1e-9) for x in proper];self.q=qfrom(math.atan2(u[1],u[2]),math.atan2(-u[0],math.hypot(u[1],u[2])),0.)
  wm=sum(p['wheel'])/2;ra=0. if self.prev is None else (wm-self.wp)/dt
  self.wa+=dt/(.12+dt)*(clip(ra,-8.,8.)-self.wa)
  expected=[self.wa,w[2]*self.vb[0],0.];candidate=[a-b for a,b in zip(proper,expected)];n=norm(candidate)
  confidence=max(0.,1.-abs(n-9.81)/(9.81*.35));up=rotation(self.q)[6:9]
  err=cross([x/max(n,1e-9) for x in candidate],up)
  self.q=step(self.q,[w[i]+1.5*confidence*clip(err[i],-.3,.3) for i in range(3)],dt)
  angles=rpy(self.q);self.yaw+=wrap(angles[2]-self.yawprev);self.yawprev=angles[2]
  R=rotation(self.q);linear=[proper[i]-9.81*R[6+i] for i in range(3)]
  self.vb[0]+=dt*(linear[0]-self.vb[1])
  p00=self.P[0]-dt*(self.P[1]+self.P[2])+dt*dt*self.P[3]+(.5*dt)**2
  p01=self.P[1]-dt*self.P[3];p10=self.P[2]-dt*self.P[3];p11=self.P[3]+(.015*dt)**2
  diff=abs(p['wheel'][0]-p['wheel'][1]);rv=.065**2*(1+min(30.,(diff/.15)**2));S=p00+rv;k0=p00/S;k1=p10/S;innovation=wm-self.vb[0]
  self.vb[0]+=k0*innovation;self.vb[1]+=k1*innovation;aa=1-k0
  self.P=[aa*aa*p00+rv*k0*k0,aa*(p01-k1*p00)+rv*k0*k1,aa*(p10-k1*p00)+rv*k1*k0,p11-k1*(p01+p10)+k1*k1*p00+rv*k1*k1]
  self.dist+=self.vb[0]*dt
  roll,pitch=angles[:2];q=p['joint_q'];v=p['joint_v']
  x=[self.dist,self.yaw,pitch,q[0],q[1]-q[0],q[2],q[3]-q[2],self.vb[0],(w[1]*math.sin(roll)+w[2]*math.cos(roll))/max(math.cos(pitch),.15),w[1]*math.cos(roll)-w[2]*math.sin(roll),v[0],v[1]-v[0],v[2],v[3]-v[2]]
  age=(p['now']-p['stamp'])*1e-6
  for i in range(7):x[i]+=age*x[i+7]
  self.prev=p['stamp'];self.wprev=w[:];self.wp=wm
  return {'state14':x,'q':self.q[:],'proper':proper,'alpha':self.alpha[:],'linear':linear,'variance':self.P[0],'roll':roll,'contact':clip(confidence*(1-min(1.,diff/.7)),0,1),'innovation':innovation}

def shape(mode):
 v=w=a=aw=0.;answers=[]
 for i in range(300):
  tv,tw=(2.,4*math.pi) if i<100 else ((0.,0.) if i<200 else(-1.,-4*math.pi));dt=.005
  old=a;j=clip(16*(tv-v)-8*a,-10,10);a=clip(a+j*dt,-2,2);v+=(old+a)*dt/2
  if abs(tv-v)<1e-5 and abs(a)<10*dt:v=tv;a=0.
  if mode:
   old=aw;j=clip(16*(tw-w)-8*aw,-40,40);aw=clip(aw+j*dt,-8,8);w+=(old+aw)*dt/2
   if abs(tw-w)<1e-5 and abs(aw)<40*dt:w=tw;aw=0.
  else:
   old=w;w+=clip(tw-w,-8*dt,8*dt);aw=(w-old)/dt
  if i in (0,19,99,119,199,219,299):answers.append({'step':i,'v':v,'w':w,'a':a,'yaw_a':aw,'mode':mode})
 return answers

def fl(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def arr(v):return '{'+','.join(fl(x) for x in v)+'}'

def main():
 rng=random.Random(20261102);maths=[];levers=[];packets=[];obs=Observer()
 for i in range(16):
  rp=[rng.uniform(-1,1),rng.uniform(-1.3,1.3),rng.uniform(-math.pi,math.pi)];q=qfrom(*rp);w=[rng.uniform(-6,6) for _ in range(3)];dt=.0005+i*.001
  qn=step(q,w,dt);maths.append({'rpy':rp,'q':q,'omega':w,'dt':dt,'qnext':qn,'R':rotation(q),'next_rpy':rpy(qn)})
 for i in range(16):
  w=[rng.uniform(-14,14) for _ in range(3)];a=[rng.uniform(-20,20) for _ in range(3)];r=[rng.uniform(-.2,.2) for _ in range(3)];f=[rng.uniform(-10,15) for _ in range(3)]
  levers.append({'proper':f,'omega':w,'alpha':a,'offset':r,'expected':lever(f,w,a,r)})
 for i in range(80):
  p={'stamp':1000000000000+i*5000,'now':1000000000000+i*5000+(i%4)*300,
     'gyro':[.15*math.sin(i*.03),.18*math.cos(i*.04),1.2*math.sin(i*.02)],
     'proper':[.7*math.sin(i*.07),.25*math.cos(i*.05),9.81+.08*math.sin(i*.1)],
     'joint_q':[.1+.001*i,.4+.002*i,-.05+.001*i,.35+.002*i],
     'joint_v':[.2,.4,.2,.4],
     'wheel':[.015*i+.02*math.sin(i*.3),.015*i-.015*math.sin(i*.2)]}
  p['expected']=obs.update(p);packets.append(p)
 shapers=shape(0)+shape(1)
 result={'reference':'Independent stdlib re-expression of frozen sensor_core.py:14-32,98-128,130-136; no import/exec',
         'arithmetic':'Python float64 reference versus float32 C tolerances',
         'math':maths,'lever':levers,'observer':packets,'shaper':shapers}
 (ROOT/'python_vectors.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 lines=['/* Generated independent numeric fixtures, not model weights. */','#ifndef CT_TEST_VECTORS_H','#define CT_TEST_VECTORS_H',
 'typedef struct {float rpy[3],q[4],omega[3],dt,qnext[4],R[9],next_rpy[3];} ct_math_fixture;',
 'static const ct_math_fixture math_fixtures[]={']
 for v in maths:lines.append('{'+','.join([arr(v['rpy']),arr(v['q']),arr(v['omega']),fl(v['dt']),arr(v['qnext']),arr(v['R']),arr(v['next_rpy'])])+'},')
 lines+=['};','typedef struct {float f[3],w[3],a[3],r[3],expected[3];} ct_lever_fixture;','static const ct_lever_fixture lever_fixtures[]={']
 for v in levers:lines.append('{'+','.join(arr(v[k]) for k in('proper','omega','alpha','offset','expected'))+'},')
 lines+=['};','typedef struct {uint64_t stamp,now;float gyro[3],proper[3],jq[4],jv[4],wheel[2],state14[14],q[4],origin[3],alpha[3],linear[3],variance,roll,contact,innovation;} ct_obs_fixture;','static const ct_obs_fixture obs_fixtures[]={']
 for v in packets:
  e=v['expected'];values=[f"UINT64_C({v['stamp']})",f"UINT64_C({v['now']})"]+[arr(v[k]) for k in('gyro','proper','joint_q','joint_v','wheel')]+[arr(e[k]) for k in('state14','q','proper','alpha','linear')]+[fl(e[k]) for k in('variance','roll','contact','innovation')]
  lines.append('{'+','.join(values)+'},')
 lines+=['};','typedef struct {int step,mode;float v,w,a,yaw_a;} ct_shaper_fixture;','static const ct_shaper_fixture shaper_fixtures[]={']
 for v in shapers:lines.append('{'+','.join([str(v['step']),str(v['mode'])]+[fl(v[k]) for k in('v','w','a','yaw_a')])+'},')
 lines+=['};','#endif']
 (ROOT/'ct_test_vectors.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 provenance={'source':str(FROZEN),'bytes':FROZEN.stat().st_size,'sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
 'hal_header':str(HAL),'hal_sha256':hashlib.sha256(HAL.read_bytes()).hexdigest(),
 'source_read_method':'Host read tool before implementation; generation only hashes it, does not import or execute it.',
 'source_ranges':{'quaternion_rotation_rpy':[14,28],'lever_arm':[29,32],'observer':[98,128],'shaper':[130,136]},
 'vector_counts':{'math':len(maths),'lever':len(levers),'observer_packets':len(packets),'shaper_checkpoints':len(shapers)}}
 (ROOT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(provenance))

if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'vector_generation_error.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
