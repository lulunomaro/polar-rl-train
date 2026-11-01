"""Full closed-chain MuJoCo plant and constrained rolling-ground LQR.
All dynamics integration uses MuJoCo. Reduced coordinates only synthesize gains.
"""
from __future__ import annotations
import os,sys,json,math,time
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
from scipy.linalg import solve_continuous_are,solve_discrete_are,expm
from scipy.optimize import brentq,least_squares
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import kinematics as kin
ORDER=('left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin')
PAIRS=[('left_proximal_a','left_proximal_b'),('left_distal_a','left_distal_b'),('left_gas_end','left_gas_mount'),('right_proximal_a','right_proximal_b'),('right_distal_a','right_distal_b'),('right_gas_end','right_gas_mount')]

def make_model(step=True,dt=.0005):
    root=ET.parse(ROOT/'model/mod4_400N.xml').getroot()
    root.find('compiler').set('meshdir',str(ROOT/'model/assets'))
    root.find('option').set('timestep',str(dt))
    if step:
        ET.SubElement(root.find('worldbody'),'geom',name='step270',type='box',pos='1.5 0 .135',size='1.5 1 .135',contype='1',conaffinity='2',friction='.9 .003 .0001',rgba='.3 .5 .7 1')
    return mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'))

class Plant:
    def __init__(self,step=True):
        self.m=make_model(step);self.d=mujoco.MjData(self.m);self.tmp=mujoco.MjData(self.m)
        self.qids=np.array([self.m.joint(n).qposadr[0] for n in ORDER]);self.vids=np.array([self.m.joint(n).dofadr[0] for n in ORDER])
        self.chassis=self.m.body('chassis').id;self.wheels=[self.m.body(s+'_wheel').id for s in ('left','right')]
        self.tires=[self.m.geom(s+'_tire').id for s in ('left','right')]
        self.pairs=[(self.m.site(a).id,self.m.site(b).id) for a,b in PAIRS]
        self.mass=float(self.m.body_mass.sum());self.radius=.0625
        self.KP=60.;self.KD=2.;self.wKD=.6
        self.dt=float(self.m.opt.timestep);self.substeps=20
        self.max_tau=np.array([40,40,5.775909774436091]*2)
        self.stall=np.array([53.3333333333333,53.3333333333333,28.18532894736838]*2)
        self.no_load=np.array([16.755160819145562,16.755160819145562,55.3557]*2)
        self.history=[];self.applied=[];self.dr=None;self.observed=None;self.tick_phys=0
    def attach_dr(self,dr):
        self.dr=dr;return dr.sample(self)
    def observe(self):
        d=self.d;R=d.xmat[self.chassis].reshape(3,3)
        local_vel=np.empty(6);mujoco.mj_objectVelocity(self.m,d,mujoco.mjtObj.mjOBJ_BODY,self.chassis,local_vel,1)
        leg=np.array([1,0,4,3]);clean={'omega3':local_vel[:3].copy(),'gravity3':R.T@np.array([0.,0.,-1.]),'legq4':d.qpos[self.qids[leg]].copy(),'legqd4':d.qvel[self.vids[leg]].copy(),'wheelqd2':d.qvel[self.vids[[2,5]]].copy()}
        self.observed=self.dr.observe(clean) if self.dr else clean
        obs=self.observed;s=self.state();s[1]=math.atan2(obs['gravity3'][0],-obs['gravity3'][2]);s[5]=obs['omega3'][1]
        s[2]=float(np.mean(obs['legq4'][[1,3]]));s[3]=float(np.mean(obs['legq4'][[0,2]]))-s[2]
        s[6]=float(np.mean(obs['legqd4'][[1,3]]));s[7]=float(np.mean(obs['legqd4'][[0,2]]))-s[6]
        return s
    def q_from(self,q,derivative=False):
        # q=(base-x,pitch,hip,crank-minus-hip), symmetric two-wheel no-slip ground chart.
        x,theta,h,delta=q;d=self.tmp;m=self.m
        mujoco.mj_resetData(m,d)
        kin.set_configuration(m,d,(h,delta),(h,delta),check_limits=False)
        d.qpos[:3]=[x,0.,0.];d.qpos[3:7]=[np.cos(theta/2),0.,np.sin(theta/2),0.]
        mujoco.mj_forward(m,d)
        wc=np.mean(d.xpos[self.wheels],axis=0)
        d.qpos[2]=self.radius-wc[2]
        # Authored wheel spin includes the knee and thigh angles.
        for side in ('left','right'):
            knee=d.qpos[m.joint(side+'_knee').qposadr[0]]
            d.qpos[m.joint(side+'_wheel_spin').qposadr[0]]=wc[0]/self.radius-theta-h-knee
        mujoco.mj_forward(m,d)
        # Authored wheel angle includes travelled wheel-center displacement.
        return d.qpos.copy()
    def chart(self,q,v=None):
        qpos=self.q_from(q);eps=1e-6;G=np.zeros((self.m.nv,4))
        for k in range(4):
            qp=np.array(q,float);qm=qp.copy();qp[k]+=eps;qm[k]-=eps
            plus=self.q_from(qp);minus=self.q_from(qm)
            col=np.empty(self.m.nv);mujoco.mj_differentiatePos(self.m,col,2*eps,minus,plus);G[:,k]=col
        d=self.tmp;d.qpos[:]=qpos;d.qvel[:]=0 if v is None else G@v
        mujoco.mj_forward(self.m,d)
        return qpos,G
    def reduced(self,q,v=None):
        qp,G=self.chart(q,v);m=self.m;d=self.tmp
        M=np.empty((m.nv,m.nv));mujoco.mj_fullM(m,d,M)
        B=np.zeros((m.nv,3))
        for i,col in enumerate([0,1,2,0,1,2]):B[self.vids[i],col]=1
        return G.T@M@G,G.T@(d.qfrc_passive-d.qfrc_bias),G.T@B
    def equilibrium(self,delta=-.1):
        def misalign(h):
            self.chart([0,0,h,delta]);d=self.tmp
            return d.subtree_com[self.chassis,0]-np.mean(d.xpos[self.wheels,0])
        hs=np.linspace(-.49,.49,30);vals=[misalign(h) for h in hs]
        candidates=[brentq(misalign,a,b) for a,b,fa,fb in zip(hs[:-1],hs[1:],vals[:-1],vals[1:]) if fa*fb<0]
        h=candidates[0] if candidates else float(hs[np.argmin(np.abs(vals))])
        q=np.array([0,0,h,delta]);M,f,B=self.reduced(q);tau=np.linalg.lstsq(B,-f,rcond=None)[0]
        return q,tau,float(np.linalg.norm(B@tau+f))
    def lqr(self,delta=-.1):
        q,tau,res=self.equilibrium(delta);M,f,B=self.reduced(q);Mi=np.linalg.inv(M)
        A=np.zeros((8,8));A[:4,4:]=np.eye(4);eps=2e-5
        for k in range(4):
            qp=q.copy();qm=q.copy();qp[k]+=eps;qm[k]-=eps
            mp,fp,bp=self.reduced(qp);mm,fm,bm=self.reduced(qm)
            A[4:,k]=(np.linalg.solve(mp,fp+bp@tau)-np.linalg.solve(mm,fm+bm@tau))/(2*eps)
            vp=np.zeros(4);vp[k]=eps;vm=-vp
            _,fp,bp=self.reduced(q,vp);_,fm,bm=self.reduced(q,vm)
            A[4:,4+k]=Mi@(fp-fm)/(2*eps)
        BB=np.zeros((8,3));BB[4:]=Mi@B
        Q=np.diag([15,600,180,250,25,40,12,12]);R=np.diag([.035,.035,.06])
        aug=np.zeros((11,11));aug[:8,:8]=A;aug[:8,8:]=BB
        disc=expm(aug*.01);Ad=disc[:8,:8];Bd=disc[:8,8:]
        P=solve_discrete_are(Ad,Bd,Q,R);K=np.linalg.solve(R+Bd.T@P@Bd,Bd.T@P@Ad)
        eig=np.linalg.eigvals(Ad-Bd@K)
        return {'q':q,'tau':tau,'K':K,'A':A,'B':BB,'eigenvalues':eig,'static_residual':res}
    def reset(self,lqr,x=-.6):
        q=lqr['q'].copy();q[0]=x;qp,_=self.chart(q)
        mujoco.mj_resetData(self.m,self.d);self.d.qpos[:]=qp;self.d.qvel[:]=0
        self.d.qpos[2]-=.00015
        mujoco.mj_forward(self.m,self.d);self.history=[];self.applied=[];self.tick_phys=0;self.observed=None
        if self.dr:
            initial=self.d.qpos[self.qids].copy();initial[[2,5]]=0.;self.dr.reset(initial)
    def state(self):
        d=self.d;w,x,y,z=d.qpos[3:7];pitch=np.arctan2(2*(w*y+z*x),1-2*(y*y+x*x))
        h=float(np.mean(d.qpos[self.qids[[0,3]]]))
        c=float(np.mean(d.qpos[self.qids[[1,4]]]))
        hd=float(np.mean(d.qvel[self.vids[[0,3]]]))
        cd=float(np.mean(d.qvel[self.vids[[1,4]]]))
        return np.array([d.qpos[0],pitch,h,c-h,d.qvel[0],d.qvel[4],hd,cd-hd])
    def clip(self,tau):
        vel=np.clip(self.d.qvel[self.vids],-self.no_load*(1+self.max_tau/self.stall),self.no_load*(1+self.max_tau/self.stall))
        hi=np.minimum(self.max_tau,self.stall*(1-vel/self.no_load));lo=np.maximum(-self.max_tau,self.stall*(-1-vel/self.no_load))
        return np.clip(tau,lo,hi)
    def torque_control(self,symmetric_tau,dt=.01):
        # Desired torque is converted to processed PD position / velocity targets.
        # Actuator envelope is still enforced on every physics step.
        d=self.d;q=d.qpos[self.qids].copy();qd=d.qvel[self.vids].copy()
        if self.observed is not None:
            q[[1,0,4,3]]=self.observed['legq4'];qd[[1,0,4,3]]=self.observed['legqd4'];qd[[2,5]]=self.observed['wheelqd2']
        tau=np.tile(symmetric_tau,2) if np.asarray(symmetric_tau).size==3 else np.array(symmetric_tau,float).copy()
        R=d.xmat[self.chassis].reshape(3,3)
        roll=math.atan2(R[2,1],R[2,2]);yaw=math.atan2(R[1,0],R[0,0])
        roll_correction=-35*roll-4*d.qvel[3]
        yaw_correction=2.5*yaw+.5*d.qvel[5]
        tau[1]+=roll_correction;tau[0]-=roll_correction
        tau[4]-=roll_correction;tau[3]+=roll_correction
        tau[2]+=yaw_correction;tau[5]-=yaw_correction
        target=q+(tau+self.KD*qd)/self.KP
        for i in (2,5):target[i]=qd[i]+tau[i]/self.wKD
        target[[0,1,3,4]]=np.clip(target[[0,1,3,4]],-3,3)
        for i in (0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
        target[[2,5]]=np.clip(target[[2,5]],-60,60)
        for _ in range(round(dt/self.dt)):
            applied=self.dr.process_targets(target,self.tick_phys) if self.dr else target
            q=d.qpos[self.qids];qd=d.qvel[self.vids]
            kp=self.dr.KP6 if self.dr else np.array([60.,60.,0.,60.,60.,0.])
            kd=self.dr.KD6 if self.dr else np.array([2.,2.,.6,2.,2.,.6])
            raw=kp*(applied-q)-kd*qd
            raw[[2,5]]=kd[[2,5]]*(applied[[2,5]]-qd[[2,5]])
            bounded=self.clip(raw)
            d.ctrl[:]=self.clip(bounded*(self.dr.motor_gain6 if self.dr else 1.))
            mujoco.mj_step(self.m,d);self.tick_phys+=1
        return d.ctrl.copy()
    def health(self):
        d=self.d;R=d.xmat[self.chassis].reshape(3,3)
        closure=max(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]) for a,b in self.pairs)
        mimic=max(abs(d.joint(s+'_drive_'+kind+'_spin').qpos[0]-d.joint(s+'_'+other).qpos[0]) for s in ('left','right') for kind,other in [('hip','hip'),('input','crank')])
        return {'time':float(d.time),'state':self.state().tolist(),'xyz':d.qpos[:3].tolist(),'wheel_xyz':d.xpos[self.wheels].tolist(),'upright_cos':float(R[2,2]),'closure':float(closure),'mimic':float(mimic),'finite':bool(np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all())}

def ground_probe():
    p=Plant(step=False);g=p.lqr(-.1)
    print(json.dumps({'equilibrium':g['q'].tolist(),'tau':g['tau'].tolist(),'residual':g['static_residual'],'K':g['K'].tolist(),'eigenvalues':[[float(x.real),float(x.imag)] for x in g['eigenvalues']]}),flush=True)
    p.reset(g);ref=np.r_[g['q'],np.zeros(4)];ref[0]=-.6
    rows=[];reason='complete'
    for k in range(400):
        err=p.state()-ref;tau=g['tau']-g['K']@err
        p.torque_control(tau)
        h=p.health()
        if k%10==0:rows.append(h)
        if not h['finite'] or h['upright_cos']<.65 or h['closure']>.01 or h['mimic']>.01:
            reason='health';rows.append(h);break
    out={'reason':reason,'last':h,'rows':rows}
    (ROOT/'results/ground_lqr_v1.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'reason':reason,'last':h}),flush=True)
if __name__=='__main__':ground_probe()
