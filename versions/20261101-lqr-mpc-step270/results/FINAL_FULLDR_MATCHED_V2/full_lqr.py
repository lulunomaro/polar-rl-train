"""LQR on the actual asymmetric two-wheel no-slip closed-chain chart."""
import math,numpy as np,mujoco
from scipy.linalg import expm,solve_discrete_are
from control_core import Plant
class AsymmetricPlant(Plant):
    # chart: x,yaw,pitch,Lhip,Ldifference,Rhip,Rdifference.
    def q_from_full(self,q):
        x,yaw,theta,hl,dl,hr,dr=q;d=self.tmp;m=self.m
        import kinematics as kin
        mujoco.mj_resetData(m,d);kin.set_configuration(m,d,(hl,dl),(hr,dr),False)
        pL=d.xpos[self.wheels[0]]-d.qpos[:3];pR=d.xpos[self.wheels[1]]-d.qpos[:3]
        roll=-math.atan2(pL[2]-pR[2],pL[1]-pR[1])
        quat=np.empty(4);mujoco.mju_euler2Quat(quat,np.array([roll,theta,yaw]),'xyz')
        # Explicit yaw*pitch*roll quaternion for body-to-world orientation.
        cr,sr=np.cos(roll/2),np.sin(roll/2);cp,sp=np.cos(theta/2),np.sin(theta/2);cy,sy=np.cos(yaw/2),np.sin(yaw/2)
        quat[:]=[cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy]
        d.qpos[:3]=[x,0,0];d.qpos[3:7]=quat;mujoco.mj_forward(m,d)
        d.qpos[2]=self.radius-float(np.mean(d.xpos[self.wheels,2]))
        for side,h,lat in [('left',hl,.2188),('right',hr,-.2188)]:
            wc=d.xpos[m.body(side+'_wheel').id]
            knee=d.joint(side+'_knee').qpos[0]
            # Linearized nonholonomic circle support, exact at yaw=0.
            d.joint(side+'_wheel_spin').qpos[0]=(x+(wc[0]-x)*math.cos(yaw)+wc[1]*math.sin(yaw)-lat*yaw)/self.radius-theta-h-knee
        return d.qpos.copy()
    def full_chart(self,q,v=None):
        qp=self.q_from_full(q);G=np.zeros((self.m.nv,7));eps=1e-6
        for k in range(7):
            a=np.array(q,float);b=a.copy();a[k]+=eps;b[k]-=eps
            qa=self.q_from_full(a);qb=self.q_from_full(b);col=np.empty(self.m.nv);mujoco.mj_differentiatePos(self.m,col,2*eps,qb,qa);G[:,k]=col
        d=self.tmp;d.qpos[:]=qp;d.qvel[:]=G@v if v is not None else 0;mujoco.mj_forward(self.m,d)
        return qp,G
    def full_reduced(self,q,v=None):
        qp,G=self.full_chart(q,v);M=np.empty((self.m.nv,self.m.nv));mujoco.mj_fullM(self.m,self.tmp,M)
        BB=np.zeros((self.m.nv,6));BB[self.vids,np.arange(6)]=1
        return G.T@M@G,G.T@(self.tmp.qfrc_passive-self.tmp.qfrc_bias),G.T@BB
    def full_lqr(self,delta=-.2):
        base,tau,res=self.equilibrium(delta);q=np.array([0,0,base[1],base[2],delta,base[2],delta]);M,f,B=self.full_reduced(q);tau=np.linalg.lstsq(B,-f,rcond=None)[0]
        A=np.zeros((14,14));A[:7,7:]=np.eye(7);BB=np.zeros((14,6));BB[7:]=np.linalg.solve(M,B);eps=2e-5
        for k in range(7):
            p=q.copy();n=q.copy();p[k]+=eps;n[k]-=eps;mp,fp,bp=self.full_reduced(p);mn,fn,bn=self.full_reduced(n)
            A[7:,k]=(np.linalg.solve(mp,fp+bp@tau)-np.linalg.solve(mn,fn+bn@tau))/(2*eps)
            v=np.zeros(7);v[k]=eps;_,fp,_=self.full_reduced(q,v);_,fn,_=self.full_reduced(q,-v);A[7:,7+k]=np.linalg.solve(M,(fp-fn)/(2*eps))
        Q=np.diag([10,100,600,100,200,100,200,20,15,40,8,10,8,10]);R=np.diag([.08,.08,.1]*2)
        aug=np.zeros((20,20));aug[:14,:14]=A;aug[:14,14:]=BB;disc=expm(aug*.01);Ad=disc[:14,:14];Bd=disc[:14,14:]
        P=solve_discrete_are(Ad,Bd,Q,R);K=np.linalg.solve(R+Bd.T@P@Bd,Bd.T@P@Ad)
        return {'q':q,'tau':tau,'K':K,'A':A,'B':BB,'Ad':Ad,'Bd':Bd,'P':P,'Q':Q,'R':R,'eigenvalues':np.linalg.eigvals(Ad-Bd@K),'symmetric':{'q':base,'tau':np.array([tau[0],tau[1],tau[2]])}}
    def full_state(self,observed=False):
        s=self.observe() if observed else self.state();d=self.d;R=d.xmat[self.chassis].reshape(3,3);yaw=math.atan2(R[1,0],R[0,0]);roll=math.atan2(R[2,1],R[2,2])
        q=d.qpos[self.qids].copy();v=d.qvel[self.vids].copy()
        if observed:
            q[[1,0,4,3]]=self.observed['legq4'];v[[1,0,4,3]]=self.observed['legqd4']
            gravity=self.observed['gravity3'];roll=math.atan2(-gravity[1],-gravity[2]);omega=self.observed['omega3']
        else:omega=d.qvel[3:6]
        pitchdot=omega[1]*math.cos(roll)-omega[2]*math.sin(roll)
        yawdot=(omega[1]*math.sin(roll)+omega[2]*math.cos(roll))/max(math.cos(s[1]),.15)
        return np.array([d.qpos[0],yaw,s[1],q[0],q[1]-q[0],q[3],q[4]-q[3],d.qvel[0],yawdot,pitchdot,v[0],v[1]-v[0],v[3],v[4]-v[3]])
