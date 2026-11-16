"""Finite-hold native action inverse for the Cartesian VMC teacher.
One bounded action is executed for 20 ms with original 100/400 Hz servos.
A shadow MJCF predicts the same hold; it is never used as an executed teacher.
The inverse balances the mean PD/VMC torque residual, rather than cancelling
native damping only at the first sample. No controller gains are retuned.
"""
import numpy as np
import mujoco as mj
from scipy.optimize import least_squares
from native_actuation import envelope, LOW, HIGH
from native_geometry import G
from data.lqr_gain_fit import get_K

class SampledVmcInverse:
    def __init__(self, teacher):
        self.t = teacher
        self.pred = mj.MjData(teacher.m)
        self.records = []

    def torque(self, action, d):
        t = self.t
        q, v = d.qpos[t.qa], d.qvel[t.va]
        target = t.default + .5*np.clip(action[:4], -6., 6.)
        target = target.copy()
        for f,r in ((0,2),(1,3)):
            delta = target[f]-target[r]
            delta += np.round((q[f]-q[r]-delta)/(2*np.pi))*2*np.pi
            delta = np.clip(delta, LOW, HIGH)
            hip = target[r]+np.round((q[r]-target[r])/(2*np.pi))*2*np.pi
            target[r], target[f] = hip, hip+delta
        raw = np.r_[60.*(target-q[:4])-2.*v[:4], .6*(np.clip(10.*action[4:],-60.,60.)-v[4:])]
        return np.clip(raw, *envelope(v))

    def requested(self, elapsed):
        t, d = self.t, self.pred
        c, sc = t.controller, t.controller.step_climb
        cmd = sc.cartesian_command
        R = d.xmat[t.env.base_id].reshape(3,3)
        forward = R[:2,0]/max(np.linalg.norm(R[:2,0]),1e-9)
        ex = np.r_[forward,0.]
        A = np.array([[ex@R[:,0],ex@R[:,2]],[R[2,0],R[2,2]]])
        gyro = d.sensor('native_teacher_gyro').data
        pitch = np.arcsin(np.clip(-R[2,0],-1.,1.))
        yaw = np.arctan2(R[1,0],R[0,0])
        yaw += np.round((c.last_state['yaw_continuous']-yaw)/(2*np.pi))*2*np.pi
        q, qd = d.qpos[t.qa],d.qvel[t.va]
        out = np.zeros(6)
        lengths=[]; jac_angles=[]
        context = G.context
        G.set_context(t.m,d)
        try:
            for i,side in enumerate(('left','right')):
                ids=[i,i+2]; qi=q[ids]; vi=qd[ids]
                bp=G.fk(side,*map(float,qi))[2]
                Jb=sc.geometry.jacobian(i,qi)
                J=A@Jb
                p=A@bp+np.array([ex@R[:,1],R[2,1]])*sc.geometry.dy[i]
                local=np.array([bp[0],sc.geometry.dy[i],bp[1]])
                v3=R@(np.cross(gyro,local)+np.array([(Jb@vi)[0],0.,(Jb@vi)[1]]))
                velocity=np.array([ex@v3,v3[2]])
                goal=cmd['goals'][i].copy()
                goal[1] += cmd['base_z']-d.xpos[t.env.base_id,2]
                if cmd.get('contact_lift') and t.surface_observer.edge is not None:
                    point,n=t.surface_observer.edge
                    edge_distance=float((point-d.xpos[t.wheels[i]])@n)/max(.1,float(n@ex))
                    goal[0]=p[0]+edge_distance-sc.direction*(sc.radius+.008)
                elif cmd['phase']=='lift':
                    goal[0] -= cmd['lift_speed']*elapsed
                elif t.surface_observer.edge is not None:
                    point,n=t.surface_observer.edge
                    edge_distance=float((point-d.xpos[t.wheels[i]])@n)/max(.1,float(n@ex))
                    goal[0]=sc.direction*max(sc.direction*goal[0],sc.direction*(p[0]+edge_distance))
                rate=np.clip(18.*(goal-p),cmd['lower'],cmd['upper'])
                if cmd['phase']=='lift': rate[0]-=cmd['body_speed'] if cmd.get('contact_lift') else cmd['lift_speed']
                force=cmd['gains']*(rate-velocity)
                if sc.quick_retract and cmd['phase'] in ('lift','swing') and pitch*sc.direction<-.04:
                    force[0]-=30.*gyro[1]
                out[ids]=J.T@force+G.projected(side,*map(float,qi),'qfrc_bias')-G.projected(side,*map(float,qi),'qfrc_passive')
                lengths.append(np.linalg.norm(bp))
                jac_angles.append(c.left_leg.jacobian(*qi)[1] if i==0 else c.right_leg.jacobian(*qi)[1])
                out[4+i]=cmd['wheel_torque'][i]
            err=np.array([yaw-c.cartesian_attitude_ref[0],pitch-c.target_pitch,gyro[2]-c.cartesian_attitude_ref[1],gyro[1]])
            K=get_K(*lengths)[:,[1,2,6,7]].copy()
            if not getattr(c,'cartesian_pitch_feedback',True):K[:,[1,3]]=0.
            attitude=-K@err
            for i in range(2):
                out[[i,i+2]]+=jac_angles[i]*attitude[i]
                if c.last_state.get('_native_contacts',{}).get('wheel_top_supported',(False,False))[i]:out[4+i]+=attitude[2+i]
        finally:
            G.context=context
        return np.clip(out, -np.r_[[40.]*4,[c.args.wheel_torque_limit]*2], np.r_[[40.]*4,[c.args.wheel_torque_limit]*2])

    def solve_wheels(self, initial, desired):
        """The velocity servo must also match torque while an axle is blocked."""
        t=self.t; start=mj.MjData(t.m); mj.mj_copyData(start,t.m,t.d)
        def residual(wheels):
            action=initial.copy();action[4:]=wheels
            mj.mj_copyData(self.pred,t.m,start);actual=[]
            for j in range(8):
                tau=self.torque(action,self.pred)
                if j%4==0:self.pred.ctrl[t.env.act_ids[:4]]=tau[:4]
                self.pred.ctrl[t.env.act_ids[4:]]=tau[4:]
                actual.append(tau[4:]);mj.mj_step(t.m,self.pred)
            return (np.mean(actual,axis=0)-desired[4:])/t.controller.args.wheel_torque_limit
        result=least_squares(residual,np.clip(initial[4:],-6.+1e-8,6.-1e-8),bounds=(-6.,6.),diff_step=1e-3,max_nfev=10,ftol=1e-3,xtol=1e-4,gtol=1e-3)
        self.records.append(dict(time=float(t.d.time),phase='wall_wheel_inverse',final_residual=result.fun.tolist(),nfev=result.nfev,success=bool(result.success)))
        out=initial.copy();out[4:]=result.x;return out

    def solve(self, initial):
        t=self.t; start=mj.MjData(t.m); mj.mj_copyData(start,t.m,t.d)
        def residual(action):
            mj.mj_copyData(self.pred,t.m,start)
            errors=[]
            for j in range(8):
                mj.mj_forward(t.m,self.pred)
                tau=self.torque(action,self.pred)
                if j%4==0:self.pred.ctrl[t.env.act_ids[:4]]=tau[:4]
                self.pred.ctrl[t.env.act_ids[4:]]=tau[4:]
                desired=self.requested(j*.0025)
                errors.append(self.pred.ctrl[t.env.act_ids]-desired)
                mj.mj_step(t.m,self.pred)
            return np.mean(errors,axis=0)/np.r_[[40.]*4,[t.controller.args.wheel_torque_limit]*2]
        initial=np.clip(initial,-6.+1e-8,6.-1e-8)
        before=residual(initial)
        result=least_squares(residual,initial,bounds=(-6.,6.),diff_step=1e-3,max_nfev=12,ftol=1e-3,xtol=1e-4,gtol=1e-3)
        self.records.append(dict(time=float(t.d.time),initial_residual=before.tolist(),final_residual=result.fun.tolist(),nfev=result.nfev,success=bool(result.success)))
        return result.x
