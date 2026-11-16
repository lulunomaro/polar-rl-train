"""Wheel-only native finite-hold inverse during idle riser engagement.
Cartesian phases and leg actions are untouched. Prediction runs the unchanged
2.5 ms MJCF and original native PD/envelope; only one 50Hz action is executed.
"""
import numpy as np, mujoco as mj
from scipy.optimize import least_squares
from native_actuation import envelope, LOW, HIGH

class PreliftWheelInverse:
    def __init__(self,t):
        self.t=t;self.pred=mj.MjData(t.m);self.start=mj.MjData(t.m);self.records=[]
    def torque(self,a,d):
        t=self.t;q,v=d.qpos[t.qa],d.qvel[t.va]
        target=t.default+.5*np.clip(a[:4],-6.,6.)
        target=target.copy()
        for f,r in ((0,2),(1,3)):
            delta=target[f]-target[r]
            delta+=np.round((q[f]-q[r]-delta)/(2*np.pi))*2*np.pi
            hip=target[r]+np.round((q[r]-target[r])/(2*np.pi))*2*np.pi
            target[r],target[f]=hip,hip+np.clip(delta,LOW,HIGH)
        raw=np.r_[60.*(target-q[:4])-2.*v[:4],.6*(np.clip(a[4:]*10.,-60.,60.)-v[4:])]
        return np.clip(raw,*envelope(v))
    def solve(self,action,requested):
        t=self.t;mj.mj_copyData(self.start,t.m,t.d)
        def residual(wheels):
            a=action.copy();a[4:]=wheels;mj.mj_copyData(self.pred,t.m,self.start);actual=[]
            for j in range(8):
                tau=self.torque(a,self.pred)
                if j%4==0:self.pred.ctrl[t.env.act_ids[:4]]=tau[:4]
                self.pred.ctrl[t.env.act_ids[4:]]=tau[4:]
                actual.append(tau[4:]);mj.mj_step(t.m,self.pred)
            return (np.mean(actual,axis=0)-requested[4:])/t.controller.args.wheel_torque_limit
        before=residual(action[4:]);fit=least_squares(residual,np.clip(action[4:],-6.+1e-8,6.-1e-8),bounds=(-6.,6.),diff_step=1e-3,max_nfev=12,ftol=1e-3,xtol=1e-4,gtol=1e-3)
        self.records.append(dict(time=float(t.d.time),requested_nm=requested[4:].tolist(),before_error_nm=(before*t.controller.args.wheel_torque_limit).tolist(),after_error_nm=(fit.fun*t.controller.args.wheel_torque_limit).tolist(),nfev=fit.nfev,converged=bool(fit.success)))
        out=action.copy();out[4:]=fit.x;return out
