"""Body-stability-first comparisons using own MOD4 K; not sealed controllers.
Coordinated common sagittal leg K with restored independent L/R stiffness;
separate balance and bounded speed-torque contributions, SPR structure only.
"""
import math
import numpy as np
from controller_base_v2 import GroundController as First


class GroundController(First):
    def __init__(self,gain,config=None,variant='body_priority'):
        self.mode=variant
        cfg=dict(config or {})
        if variant!='coord':
            cfg.update(accel=.6,jerk=2.,yaw_accel=2.)
        self.coordinated=variant in ('coord','coord_soft')
        super().__init__(gain,cfg,variant='park_fullsym' if self.coordinated else 'park_body')

    def command(self,e,forward,yaw_rate):
        x=e.state14
        # Near-stop local I should not accumulate IMU/wheel bias into a body lean.
        # This changes only the local controller term, never estimator odometry.
        if abs(forward)<.05 and abs(self.shaper.v)<.05 and abs(x[7])<.03 and abs(x[9])<.08:
            self.park_error*=math.exp(-self.dt/2.)
        tau=super().command(e,forward,yaw_rate)
        if not self.valid_command:
            return tau
        if self.coordinated:
            q=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]])
            qr=np.array([self.ref[3],self.ref[3]+self.ref[4],self.ref[5],self.ref[5]+self.ref[6]])
            qd=np.array([x[10],x[10]+x[11],x[12],x[12]+x[13]])
            pd=self.leg_kp*(qr-q)-self.leg_kd*qd
            # Only DIFFERENTIAL PD: do not overwrite common pitch balancing.
            dh=.5*(pd[0]-pd[2]);dc=.5*(pd[1]-pd[3])
            tau[[0,1,3,4]]+=np.array([dh,dc,-dh,-dc])
        if self.mode=='body_priority':
            err=x-self.ref
            err=err.copy();err[1]=err[8]=0.
            for a,b in ((3,5),(4,6),(10,12),(11,13)):
                err[a]=err[b]=.5*(err[a]+err[b])
            err[2]*=self.wheel_pitch_scale
            err[9]*=self.wheel_pitch_scale
            err[7]*=self.wheel_velocity_scale
            tracking=np.zeros(14);tracking[[0,7]]=err[[0,7]]
            balance=self.tau_eq-self.K@(err-tracking)
            balance_common=float(np.clip(np.mean(balance[[2,5]]),-self.effort[2],self.effort[2]))
            speed_common=float(np.mean((-self.K@tracking)[[2,5]]))
            # A bounded SPEED contribution; pitch/rate leg/balance remains first.
            speed_common=float(np.clip(speed_common,-1.,1.))
            common=balance_common+float(np.clip(speed_common,-self.effort[2]-balance_common,self.effort[2]-balance_common))
            available=max(0.,self.effort[2]-abs(common))
            diff=float(np.clip(.5*(tau[5]-tau[2]),-available,available))
            tau[2],tau[5]=common-diff,common+diff
        tau=np.clip(tau,-self.effort,self.effort)
        self.previous=tau.copy()
        return tau
