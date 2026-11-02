"""Operator-triggered timed mini-hop prototype, sensor-only, NOT contact FSM.
No simulator/DR/terrain/true contact imports. Ground P25 is a local instance;
all sealed source/gain files are read-only. Flight phase is a timer hypothesis.
"""
import math
import numpy as np
from ground_controller_v4 import GroundController
from sensor_core_jump_v1 import rotation,quat_step

LEG=np.array([0,1,3,4])
WHEEL=np.array([2,5])
EFFORT=np.array([40.,40.,5.775909774436091]*2)

def absolute_q(g):
    q=np.asarray(g['q'],float)
    return np.array([q[3],q[3]+q[4],q[5],q[5]+q[6]])

class MiniHop:
    def __init__(self,start_gain,end_gain,geometry,config):
        self.g=start_gain;self.end=end_gain;self.geom=geometry;self.c=dict(config)
        self.ctrl=GroundController(start_gain,dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,roll_kp=20.,roll_kd=2.))
        self.q_start=absolute_q(start_gain);self.q_end=absolute_q(end_gain)
        self.enabled=self.c.get('operator_enable',False)
        assert type(self.enabled)is bool
        self.trigger=float(self.c.get('trigger_time_s',1.5))
        self.push=float(self.c.get('push_for_s',.10))
        self.air=float(self.c.get('predicted_air_after_push_s',.35))
        self.blend=float(self.c.get('capture_blend_s',.10))
        assert all(math.isfinite(v)and v>0 for v in (self.trigger,self.push,self.air,self.blend))
        self.last_time=None;self.launched=False;self.launch=None;self.captured=False
        self.last_tau=np.asarray(start_gain['tau'],float).copy()
        self.capture_from=None;self.fault=False;self.log={}

    def prepare_estimator(self,estimator,now):
        # Set BEFORE the packet update. This is predicted phase, not contact truth.
        active=self.enabled and now>=self.trigger
        air=active and now>=self.trigger+self.push and now<self.trigger+self.push+self.air
        estimator.wheel_measurement_enabled=not air
        estimator.ground_kinematic_constraint_enabled=not air
        estimator.accel_correction=0. if active and now<self.trigger+self.push+self.air else 1.5

    def command(self,e,packet,now,attitude_q,forward=0.):
        now=float(now)
        if self.last_time is not None and (now<=self.last_time or now-self.last_time>.05):
            self.fault=True
        self.last_time=now
        if (not math.isfinite(now)or now<0 or not math.isfinite(forward)
            or not math.isfinite(e.sensor_age_s)or not 0.<=e.sensor_age_s<=.05
            or np.shape(e.state14)!=(14,)or not np.isfinite(e.state14).all()
            or np.shape(packet.joint_pos4)!=(4,)or not np.isfinite(packet.joint_pos4).all()
            or np.shape(packet.joint_vel4)!=(4,)or not np.isfinite(packet.joint_vel4).all()
            or np.shape(e.omega_body)!=(3,)or not np.isfinite(e.omega_body).all()
            or not math.isfinite(e.roll)or np.shape(attitude_q)!=(4,)
            or not np.isfinite(attitude_q).all()or abs(float(np.linalg.norm(attitude_q))-1.)>1e-6):self.fault=True
        if self.fault:
            self.log=dict(phase='INHIBIT',contact_or_flight_trusted=False)
            return np.zeros(6)
        x=e.state14;actual_q=np.asarray(packet.joint_pos4,float);actual_v=np.asarray(packet.joint_vel4,float)
        tau=None;targets=self.q_start.copy();vels=np.zeros(4);since=now-self.trigger
        if self.enabled and since>=self.push and not self.launched:
            self.fault=True;self.log=dict(phase='INHIBIT',reason='missed_operator_trigger_window',contact_or_flight_trusted=False)
            return np.zeros(6)
        if not self.enabled or since<0:
            phase='supported_approach';tau=self.ctrl.command(e,forward,0.)
        elif since<self.push:
            phase='timed_push'
            if not self.launched:
                if abs(x[2])>.15 or abs(e.roll)>.15 or abs(x[7])>float(self.c.get('max_trigger_speed_m_s',.2)):
                    self.fault=True;self.log=dict(phase='INHIBIT',reason='operator_trigger_state_guard',contact_or_flight_trusted=False)
                    return np.zeros(6)
                self.launched=True;self.launch=now
            u=float(np.clip(since/self.push,0.,1.));s=3*u*u-2*u*u*u;ds=6*u*(1-u)/self.push
            targets=(1-s)*self.q_start+s*self.q_end;vels=ds*(self.q_end-self.q_start)
            tau=(1-s)*np.asarray(self.g['tau'],float)+s*np.asarray(self.end['tau'],float)
            tau[LEG]+=float(self.c.get('push_kp',300.))*(targets-actual_q)+float(self.c.get('push_kd',3.))*(vels-actual_v)
            tau[LEG]=np.clip(tau[LEG],-32.,32.) # 8Nm explicit roll allocation reserve
            tau[WHEEL]=float(self.c.get('wheel_push_Nm',0.))+25.*x[2]+4.*x[9]
            moment=float(np.clip(-40.*e.roll-5.*e.omega_body[0],-8.,8.))
            R=rotation(quat_step(np.asarray(attitude_q,float),e.omega_body,e.sensor_age_s))
            for side,indices,qq in (('left',[0,1],actual_q[:2]),('right',[3,4],actual_q[2:])):
                _,_,J,_=self.geom.wheel_kinematics(float(qq[0]),float(qq[1]),0.,0.,0.,np.zeros(3),side)
                fz=moment/.4376*(1. if side=='left'else -1.)
                tau[indices]-=J.T@(R.T@np.array([0.,0.,fz]))
            diff=float(np.clip(-1.2*x[8]-.4*x[1],-.5,.5));tau[2]-=diff;tau[5]+=diff
        elif since<self.push+self.air:
            phase='predicted_flight_retract'
            tau=np.zeros(6);tau[LEG]=140.*(targets-actual_q)-3.*actual_v
            tau[WHEEL]=25.*x[2]+4.*x[9]
            diff=float(np.clip(-1.2*x[8]-.4*x[1],-.5,.5));tau[2]-=diff;tau[5]+=diff
        else:
            phase='timed_capture'
            if not self.captured:
                self.captured=True;self.capture_from=self.last_tau.copy()
                self.ctrl.ref[0]=x[0]+.15*x[7]
                self.ctrl.ref[1]=x[1]
            ground=self.ctrl.command(e,forward,0.)
            weight=float(np.clip((since-self.push-self.air)/self.blend,0.,1.))
            tau=(1-weight)*self.capture_from+weight*ground
        tau=np.clip(tau,-EFFORT,EFFORT)
        if not np.isfinite(tau).all():self.fault=True;tau=np.zeros(6);phase='INHIBIT'
        self.last_tau=tau.copy()
        self.log=dict(phase=phase,phase_source='operator_timer_not_contact',contact_or_flight_trusted=False,
                      target_q4=targets.tolist(),target_qd4=vels.tolist(),since_operator_trigger_s=since,
                      wheel_measurement_disabled_predicted=bool(self.push<=since<self.push+self.air),
                      fault_latched=bool(self.fault))
        return tau
