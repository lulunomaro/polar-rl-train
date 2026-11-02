"""8-state symmetric fixed-leg ground MPC, 15 scalar common-wheel inputs.
No simulator imports/inputs. Local zero-yaw model: highspin uses explicit LQR.
Box torque constraints only; not aerial/contact-aware nonlinear MPC.
"""
import math,time
import numpy as np
from scipy.linalg import expm,solve_discrete_are,block_diag
from ground_controller_v4 import GroundController as LQRFallback

def fixedleg_model(g,kp=120.,kd=4.,lag_fraction=.5,qposition=250.,r=.2):
 E=np.zeros((14,8));S=np.zeros((8,14))
 for a,b in((0,0),(2,1),(7,4),(9,5)):E[a,b]=1.;S[b,a]=1.
 for a,b,c in((3,5,2),(4,6,3),(10,12,6),(11,13,7)):E[a,c]=E[b,c]=1.;S[c,a]=S[c,b]=.5
 assert np.allclose(S@E,np.eye(8));L=np.zeros((6,14))
 for hip,crank,hs,ds,hd,dd in((0,1,3,4,10,11),(3,4,5,6,12,13)):
  L[hip,hs]=-kp;L[hip,hd]=-kd;L[crank,[hs,ds]]=-kp;L[crank,[hd,dd]]=-kd
 A=S@(g['A']+g['B']@L)@E;B=S@(g['B'][:,2:3]+g['B'][:,5:6]);z=np.zeros((9,9));z[:8,:8]=A;z[:8,8:]=B;d=expm(z*.01);Ad=d[:8,:8];Bd=d[:8,8:];Aa=np.zeros((9,9));Aa[:8,:8]=Ad;Aa[:8,8:]=lag_fraction*Bd;Ba=np.r_[(1-lag_fraction)*Bd,[[1.]]];Q=np.diag([qposition,600.,200.,400.,20.,40.,16.,20.,.005]);P=solve_discrete_are(Aa,Ba,Q,np.array([[r]]));K=np.linalg.solve(np.array([[r]])+Ba.T@P@Ba,Ba.T@P@Aa)
 return dict(A8=A,B8=B,Ad8=Ad,Bd8=Bd,A=Aa,B=Ba,Q=Q,R=r,P=P,K=K,projection=S,embedding=E,leg_feedback=L,lag_fraction=lag_fraction,eigenvalues=np.linalg.eigvals(Aa-Ba@K))

class ScalarMPC:
 def __init__(self,model,horizon=15,max_sweeps=80,tolerance=.002):
  self.m=model;self.N=horizon;self.max_sweeps=max_sweeps;self.tol=tolerance;A,B=model['A'],model['B'];self.F=np.vstack([np.linalg.matrix_power(A,k)for k in range(1,horizon+1)]);self.G=np.zeros((9*horizon,horizon))
  for k in range(horizon):
   for j in range(k+1):self.G[9*k:9*k+9,j:j+1]=np.linalg.matrix_power(A,k-j)@B
  self.W=block_diag(*([model['Q']]*(horizon-1)+[model['P']]));self.H=2*(self.G.T@self.W@self.G+model['R']*np.eye(horizon));self.invH=np.linalg.inv(self.H);self.grad_map=2*self.G.T@self.W;self.warm=np.zeros(horizon);self.last_u=0.;self.last={};self.calls=0
 def solve(self,x8,ref8,vref,lo,hi):
  t=time.perf_counter_ns();state=np.r_[x8,self.last_u];refs=np.tile(np.r_[ref8,0.],(self.N,1));refs[:,0]+=np.arange(1,self.N+1)*.01*vref;g=self.grad_map@(self.F@state-refs.ravel());free=-self.invH@g;z=np.clip(np.r_[self.warm[1:],self.warm[-1]],lo,hi);sweeps=0
  if np.all(free>=lo)and np.all(free<=hi):z=free;status='unconstrained_exact'
  else:
   status='iteration_limit'
   for sweep in range(self.max_sweeps):
    for i in range(self.N):z[i]=np.clip(z[i]-(g[i]+self.H[i]@z)/self.H[i,i],lo,hi)
    sweeps=sweep+1;gr=self.H@z+g;pr=gr.copy();pr[(z<=lo+1e-8)&(gr>0)]=0.;pr[(z>=hi-1e-8)&(gr<0)]=0.
    if np.max(abs(pr))<=self.tol:status='converged';break
  gr=self.H@z+g;pr=gr.copy();pr[(z<=lo+1e-8)&(gr>0)]=0.;pr[(z>=hi-1e-8)&(gr<0)]=0.;res=float(np.max(abs(pr)));elapsed=(time.perf_counter_ns()-t)*1e-6;feasible=bool(np.isfinite(z).all()and np.all(z>=lo-1e-8)and np.all(z<=hi+1e-8));self.last=dict(status=status,sweeps=sweeps,kkt=res,solve_ms=elapsed,feasible=feasible,accepted=feasible and res<=self.tol);self.warm=z.copy();self.calls+=1;return float(z[0])

class GroundController(LQRFallback):
 def __init__(self,gain,config=None):
  super().__init__(gain,config);c=config or{};self.local_model=fixedleg_model(gain,self.leg_kp,self.leg_kd,float(c.get('mpc_lag_fraction',.5)),float(c.get('mpc_qposition',250.)),float(c.get('mpc_r',.2)));self.mpc=ScalarMPC(self.local_model,15,int(c.get('mpc_sweeps',80)),float(c.get('mpc_tolerance',.002)));self.deadline_ms=float(c.get('mpc_deadline_ms',3.));self.usage={'mpc_accepted':0,'lqr_fallback':0,'reasons':{},'solve_ms_max':0.,'kkt_max':0.};self.last_mpc={}
 def command(self,estimate,forward,yaw_rate):
  start=time.perf_counter_ns();tau=super().command(estimate,forward,yaw_rate);x=estimate.state14;reason=None
  if abs(x[8])>2. or abs(x[2])>.25:reason='outside_zero_yaw_small_pitch_model'
  elif not self.fixed_legs:reason='fixed_leg_model_required'
  if reason is None:
   S=self.local_model['projection'];xe=S@(x-self.eq);ref=S@(self.ref-self.eq);diff=.5*(tau[5]-tau[2]);speed=(abs(x[7])+.2188*abs(x[8]))/.063699998+abs(estimate.omega_body[1]);dc=max(0.,min(5.775909774436091,28.18532894736838*(1.-speed/55.3557)));bound=dc-abs(diff)
   if bound<=.05:reason='frozen_speed_envelope_no_common_headroom'
   else:
    u=self.mpc.solve(xe,ref,float(self.ref[7]),-bound,bound);log=self.mpc.last;self.usage['solve_ms_max']=max(self.usage['solve_ms_max'],log['solve_ms']);self.usage['kkt_max']=max(self.usage['kkt_max'],log['kkt']);self.last_mpc=log.copy()
    if not log['accepted']:reason='QP_'+log['status']
    elif log['solve_ms']>self.deadline_ms:reason='host_solver_deadline'
    else:tau[2]=u-diff;tau[5]=u+diff;self.usage['mpc_accepted']+=1
  if reason is not None:self.usage['lqr_fallback']+=1;self.usage['reasons'][reason]=self.usage['reasons'].get(reason,0)+1;self.last_mpc={'fallback':reason}
  self.mpc.last_u=float(np.mean(tau[[2,5]]));self.previous=tau.copy();self.max_solve_ms=max(self.max_solve_ms,(time.perf_counter_ns()-start)*1e-6);return tau
