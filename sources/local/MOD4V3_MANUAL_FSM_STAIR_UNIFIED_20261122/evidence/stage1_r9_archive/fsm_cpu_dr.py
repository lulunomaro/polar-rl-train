"""Full-range SCUT samples for independent CPU validation, with explicit engine mapping.

Only ephemeral compiled-model parameters change. Original MJCF/USD files are never edited.
"""
from collections import deque
import math
import re
import numpy as np
import mujoco as mj
from fsm_paths import donor_imports
donor_imports()
from play_mod4v3 import ACTION_SCALE_LEG,ACTION_SCALE_WHEEL,LEG_DELTA_BOUNDS,STALL,NO_LOAD,PEAK,WHEEL_VEL_LIMIT

class CPUFullDR:
    def __init__(self,sim,seed):
        self.sim=sim;self.rng=np.random.default_rng(seed);r=self.rng;m=sim.m
        masses=np.ones(m.nbody)
        for i in range(1,m.nbody):
            name=m.body(i).name
            if name=='base_link':masses[i]=r.uniform(.9,1.3)
            elif re.fullmatch(r'.*_(?:front[1-4]|rear[1-2]|spring[1-2])_link|gimbal_(?:yaw|pitch)_link',name):
                masses[i]=r.uniform(.9,1.1)
            elif name in ('left_wheel_link','right_wheel_link'):masses[i]=r.uniform(.9,1.1)
        m.body_mass[:]*=masses;m.body_inertia[:]*=masses[:,None]
        com=r.uniform(-1.,1.,3)*[.04,.02,.02]
        m.body_ipos[sim.env.base_id]+=com
        material={}
        for gid in range(m.ngeom):
            name=m.body(m.geom_bodyid[gid]).name
            kind='wheel' if name in ('left_wheel_link','right_wheel_link') else 'guide' if name.endswith('_guide_link') else 'base' if name=='base_link' else None
            if kind is None:continue
            mu_range,dyn_range,rest_range={'wheel':((.5,1.2),(.4,1.),(.02,.2)),
                'guide':((.1,.7),(.1,.7),(.01,.1)),'base':((.01,.1),(.01,.1),(.02,.2))}[kind]
            static=r.uniform(*mu_range);dynamic=min(static,r.uniform(*dyn_range));rest=r.uniform(*rest_range)
            m.geom_friction[gid,0]=static
            # Keep contact time constant; map restitution to damping ratio.
            if m.geom_solref[gid,0]>0.:
                log=math.log(rest);m.geom_solref[gid,1]=-log/math.sqrt(math.pi**2+log**2)
            material[m.geom(gid).name]=[static,dynamic,rest]
        active=set(sim.env.qadr_all[sim.env.leg_ids].tolist())
        self.static=m.dof_frictionloss.copy();self.dynamic=self.static.copy()
        for j in range(m.njnt):
            if m.jnt_type[j]==mj.mjtJoint.mjJNT_FREE:continue
            name=m.joint(j).name;dof=m.jnt_dofadr[j]
            if name in ('left_wheel_joint','right_wheel_joint'):
                self.static[dof]+=r.uniform(.05,.25);self.dynamic[dof]=self.static[dof]
                m.dof_damping[dof]+=r.uniform(0.,.01)
            elif m.jnt_qposadr[j] in active:
                self.static[dof]+=r.uniform(.25,1.);self.dynamic[dof]+=r.uniform(.25,1.)
                m.dof_damping[dof]+=r.uniform(.05,.2)
            elif name.endswith(('_front2_joint','_front4_joint','_rear2_joint','_f3r1_joint')):
                self.static[dof]+=r.uniform(.05,.1);self.dynamic[dof]=self.static[dof]
                m.dof_damping[dof]+=r.uniform(.01,.025)
            if 'spring' in name:
                m.dof_damping[dof]=3.*r.uniform(.5,1.5)
                m.qpos_spring[m.jnt_qposadr[j]]+=r.uniform(-.025,.025)
        self.kp=r.uniform(.75,1.25,4);self.kd=r.uniform(.75,1.25,4);self.kw=r.uniform(.75,1.25,2)
        self.effort=np.r_[r.uniform(.8,1.1,4),r.uniform(.9,1.1,2)]
        self.torque_noise=r.uniform(0.,.025,6)
        self.action_delay=int(r.choice([2,4]));self.sensor_delay=int(r.choice([2,4,6]))
        self.actions=deque([np.zeros(6) for _ in range(self.action_delay+1)],maxlen=self.action_delay+1)
        self.sensors=deque(maxlen=8)
        self.next_push=r.uniform(5.,10.);self.next_wrench=r.uniform(5.,10.);self.wrench_end=-1.
        self.wrench=np.zeros(6)
        q=sim.d.qpos.copy();v=sim.d.qvel.copy()
        mj.mj_setConst(m,sim.d);sim.d.qpos[:]=q;sim.d.qvel[:]=v;mj.mj_forward(m,sim.d)
        self.summary=dict(profile='SCUT remaining full ranges / CPU port',fraction=1.,seed=seed,
            body_mass_scale=masses.tolist(),com_delta_m=com.tolist(),materials=material,
            kp=self.kp.tolist(),kd=self.kd.tolist(),wheel_kd=self.kw.tolist(),effort=self.effort.tolist(),
            action_delay_ms=self.action_delay*2.5,sensor_delay_ms=self.sensor_delay*2.5,
            contact_mapping='MuJoCo sliding friction uses static sample; restitution maps to damping ratio at unchanged contact time constant',
            joint_friction_mapping='Stribeck interpolation between sampled static/dynamic friction',
            external_wrench_n_nm=[10.,1.],wrench_hold_s=.2,push_delta_m_s=.25)

    def sample_sensors(self,obs):self.sensors.append(obs.copy())

    def observe(self,current):
        obs=self.sensors[-min(len(self.sensors),self.sensor_delay+1)].copy() if self.sensors else current.copy()
        obs[:4]=current[:4];obs[28:35]=current[28:35]
        r=self.rng
        for sl,amplitude in ((slice(3,4),.01),(slice(4,7),.25),(slice(7,10),.05),
                             (slice(10,16),.025),(slice(16,20),.5),(slice(20,22),1.)):
            obs[sl]+=r.uniform(-amplitude,amplitude,obs[sl].shape)
        return obs

    def torque(self,native,jump=False):
        s=self.sim;e=s.env;d=s.d;m=s.m;r=self.rng
        self.actions.append(native.copy());a=self.actions[0]
        q=d.qpos[e.qadr_all[e.leg_ids]].astype(np.float32)
        lv=d.qvel[e.dadr_all[e.leg_ids]].astype(np.float32)
        wv=d.qvel[e.dadr_all[e.wheel_ids]].astype(np.float32)
        target=e.default_q[e.leg_ids].numpy()+ACTION_SCALE_LEG*a[:4]
        for front,rear in ((0,2),(1,3)):
            delta=target[front]-target[rear]
            delta+=round(float((q[front]-q[rear]-delta)/(2*math.pi)))*2*math.pi
            if not jump:delta=np.clip(delta,*LEG_DELTA_BOUNDS)
            target[rear]+=round(float((q[rear]-target[rear])/(2*math.pi)))*2*math.pi
            target[front]=target[rear]+delta
        goal=np.clip(ACTION_SCALE_WHEEL*a[4:],-WHEEL_VEL_LIMIT,WHEEL_VEL_LIMIT)
        raw=np.r_[60.*self.kp*(target-q)-2.*self.kd*lv,.6*self.kw*(goal-wv)]*self.effort
        raw+=r.normal(0.,self.torque_noise)
        velocity=np.r_[lv,wv]
        hi=np.clip(STALL*(1.-velocity/NO_LOAD),0.,PEAK)
        lo=np.clip(-STALL*(1.+velocity/NO_LOAD),-PEAK,0.)
        m.dof_frictionloss[:]=self.dynamic+(self.static-self.dynamic)*np.exp(-(np.abs(d.qvel)/.01)**2)
        if d.time>=self.next_push:
            d.qvel[:2]+=r.uniform(-.25,.25,2);self.next_push=d.time+r.uniform(5.,10.)
        if d.time>=self.next_wrench:
            self.wrench=np.r_[r.uniform(-10.,10.,3),r.uniform(-1.,1.,3)]
            self.wrench_end=d.time+.2;self.next_wrench=d.time+r.uniform(5.,10.)
        d.xfrc_applied[e.base_id]=self.wrench if d.time<self.wrench_end else 0.
        return np.clip(raw,lo,hi)
