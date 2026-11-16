"""Pull back the complete MOD4 MJCF onto Serial's 5 rolling coordinates.
Uses all native moving bodies, closed-chain FK, native axes and the same bias/passive
compensated VMC input as the runner. Ideal rolling/fixed-length reduction is for LQR
linearization only; acceptance still runs the unmodified compliant MJCF and native PD.
"""
from pathlib import Path
import sys,json,time
import numpy as np,mujoco as mj
from scipy.optimize import brentq,least_squares,minimize
from scipy.linalg import expm,solve_discrete_are
ROOT=Path(__file__).resolve().parent;sys.path[:0]=[str(ROOT),str(ROOT/'sim')]
from native_geometry import G,PLANT
class NativeReduced:
 def __init__(self,Ll,Lr):
  self.lengths=np.array([Ll,Lr]);self.m=mj.MjModel.from_xml_path(str(PLANT/'mjcf/scene.xml'));self.d=mj.MjData(self.m);self.m.geom_contype[:]=0;self.m.geom_conaffinity[:]=0
  self.q0=[]
  for side,L in zip(['left','right'],self.lengths):
   delta=brentq(lambda delta:np.linalg.norm(G.fk(side,delta,0.)[2])-L,.17265192458887935,1.7508937980913823,xtol=1e-13)
   wheel=G.fk(side,delta,0.)[2];angle=-np.arctan2(wheel[0],-wheel[1]);self.q0.append(np.array([delta-angle,-angle]))
  self.ad=np.array([self.m.jnt_dofadr[self.m.joint(n).id]for n in ['left_front1_joint','right_front1_joint','left_rear1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']]);self.wb=[self.m.body(s+'_wheel_link').id for s in ['left','right']]
 def pose(self,q):
  x,yaw,pitch,tl,tr=q;pos=self.m.qpos0.copy();p=[]
  for i,(s,theta)in enumerate(zip(['left','right'],[tl,tr])):
   active=self.q0[i]+theta-pitch;native=G.configuration(s,*active);pos[G.qadr[G.side_indices[i]]]=native[G.side_indices[i]]
   point=G.fk(s,*active)[2];p.append([point[0],G.dy[i],point[1]])
  p=np.asarray(p);dp=p[0]-p[1];aa=np.cos(pitch)*dp[1];bb=np.cos(pitch)*dp[2];cc=np.sin(pitch)*dp[0]
  roll=np.arcsin(np.clip(cc/np.hypot(aa,bb),-1,1))-np.arctan2(bb,aa)
  sr,cr=np.sin(roll),np.cos(roll);sp,cp=np.sin(pitch),np.cos(pitch);sy,cy=np.sin(yaw),np.cos(yaw)
  R=np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])
  pos[:3]=[x,0.,.0625-np.mean(p@R[2])];mj.mju_mat2Quat(pos[3:7],R.ravel());return pos
 def tangent(self,q):
  eps=1e-6;S=np.zeros((self.m.nv,5),order="F")
  for j in range(5):
   delta=np.eye(5)[j]*eps;mj.mj_differentiatePos(self.m,S[:,j],2*eps,self.pose(q-delta),self.pose(q+delta))
  # x is the accumulated forward coordinate, not a fixed global X velocity.
  S[0:2,:]=np.array([[np.cos(q[1]),-np.sin(q[1])],[np.sin(q[1]),np.cos(q[1])]])@S[0:2,:]
  self.d.qpos[:]=self.pose(q);mj.mj_kinematics(self.m,self.d);mj.mj_comPos(self.m,self.d)
  forward=np.array([np.cos(q[1]),np.sin(q[1]),0.]);bottom=np.array([0.,0.,-.0625])
  for i,b in enumerate(self.wb):
   jp=np.zeros((3,self.m.nv));jr=jp.copy();mj.mj_jacBody(self.m,self.d,jp,jr,b)
   rolling=forward@(jp+np.cross(jr.T,bottom).T);idx=self.ad[4+i];S[idx,:]-=(rolling@S)/rolling[idx]
  return S
 def terms(self,q,qd):
  S=self.tangent(q);self.d.qpos[:]=self.pose(q);self.d.qvel[:]=S@qd;mj.mj_forward(self.m,self.d);M=np.zeros((self.m.nv,self.m.nv));mj.mj_fullM(self.m,self.d,M);Mr=S.T@M@S
  U=np.zeros((self.m.nv,4));comp=np.zeros(self.m.nv)
  for i,side in enumerate(['left','right']):
   active=self.q0[i]+q[3+i]-q[2];eps=1e-6
   def polar(a):
    v=G.fk(side,*a)[2];return np.array([np.linalg.norm(v),-np.arctan2(v[0],-v[1])])
   J=np.column_stack([(polar(active+np.eye(2)[j]*eps)-polar(active-np.eye(2)[j]*eps))/(2*eps)for j in range(2)])
   ids=self.ad[[i,i+2]];U[ids,i]=J[1];Qj=G.q_jacobian(side,*active)
   comp[ids]=Qj.T@(self.d.qfrc_bias[G.dadr]-self.d.qfrc_passive[G.dadr])+J[0]*(.5*self.m.body_mass.sum()*9.81)
  U[self.ad[4],2]=U[self.ad[5],3]=1.
  force=S.T@(comp+self.d.qfrc_passive-self.d.qfrc_bias)
  if np.linalg.norm(qd)>1e-10:
   eps=1e-5;Sdot=(self.tangent(q+eps*qd)-self.tangent(q-eps*qd))/(2*eps);force-=S.T@M@Sdot@qd
  return Mr,force,S.T@U
 def acceleration(self,q,qd,u):
  M,b,B=self.terms(q,qd);return np.linalg.solve(M,b+B@u)
 def equilibrium(self,guess=None):
  def residual(v):
   q=np.r_[0.,0.,0.,v[:2]];_,b,B=self.terms(q,np.zeros(5));return b+B@v[2:]
  initial=np.r_[.13,.13,-2.3,-2.3,0.,0.] if guess is None else guess.copy()
  initial[:2]=np.mean(initial[:2])
  fit=minimize(lambda v:float(v[2:]@v[2:]+1e-4*v[:2]@v[:2]),initial,method='SLSQP',constraints={'type':'eq','fun':residual},bounds=[(-.8,.8)]*2+[(-40.,40.)]*4,options={'ftol':1e-8,'eps':1e-4,'maxiter':40})
  if np.max(abs(residual(fit.x)))>1e-5:raise RuntimeError(('Native static residual',fit.x,residual(fit.x)))
  return fit.x,float(np.max(abs(residual(fit.x))))
 def linearize(self,eq):
  q=np.r_[0.,0.,0.,eq[:2]];u=eq[2:];A=np.zeros((10,10));A[:5,5:]=np.eye(5)
  for j in range(10):
   eps=2e-4;step=np.eye(10)[j]*eps;a=np.r_[q,np.zeros(5)]+step;b=np.r_[q,np.zeros(5)]-step;A[5:,j]=(self.acceleration(a[:5],a[5:],u)-self.acceleration(b[:5],b[5:],u))/(2*eps)
  M,_,B=self.terms(q,np.zeros(5));Bc=np.vstack([np.zeros((5,4)),np.linalg.solve(M,B)])
  return A,Bc

def build():
 start=time.perf_counter();old=np.load(ROOT/'native_gains.npz');grid=old['grid'];data={k:[]for k in ['L_l','L_r','A','B','Ad','Bd','K','u_eq','equilibrium','poles']};res=[];Q=np.diag(json.loads((ROOT/'PHYSICAL_PARAMETERS.json').read_text())['source_Q']);R=np.asarray(json.loads((ROOT/'PHYSICAL_PARAMETERS.json').read_text())['source_R'])
 for ll in grid:
  for lr in grid:
   m=NativeReduced(ll,lr);i=len(res);seed=np.r_[old['equilibrium'][i,3:5],old['u_eq'][i]];eq,r=m.equilibrium(seed);A,B=m.linearize(eq);aug=np.zeros((14,14));aug[:10,:10]=A;aug[:10,10:]=B;Md=expm(aug*.02);Ad,Bd=Md[:10,:10],Md[:10,10:];P=solve_discrete_are(Ad,Bd,Q,R);K=np.linalg.solve(R+Bd.T@P@Bd,Bd.T@P@Ad);poles=abs(np.linalg.eigvals(Ad-Bd@K));res.append(r)
   for k,v in dict(L_l=ll,L_r=lr,A=A,B=B,Ad=Ad,Bd=Bd,K=K,u_eq=eq[2:],equilibrium=np.r_[0,0,0,eq[:2],np.zeros(5)],poles=poles).items():data[k].append(v)
   print('NATIVE_GAIN',i+1,'L',float(ll),float(lr),'eq',eq.tolist(),'rho',float(max(poles)),'residual',r,flush=True)
 np.savez_compressed(ROOT/'native_full_mjcf_gains.npz',grid=grid,**{k:np.asarray(v)for k,v in data.items()})
 (ROOT/'NATIVE_LINEARIZATION.json').write_text(json.dumps(dict(method='full MJCF constrained virtual-work pullback, five rolling coordinates; same bias/passive-compensated VMC input',points=len(res),wall_seconds=time.perf_counter()-start,max_static_residual_nm=max(res),max_pole=float(np.max(data['poles'])),limitations=['ideal rolling and fixed leg lengths in reduced model','PD action sample/hold assessed separately in real simulator']),indent=2)+chr(10))
if __name__=='__main__':build()
