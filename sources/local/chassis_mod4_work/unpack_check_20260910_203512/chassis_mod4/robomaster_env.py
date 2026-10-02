"""Gymnasium torque-control task for the STEP-derived closed-link chassis.

Actions, in order: L hip, L crank, L wheel, R hip, R crank, R wheel.
Hip and crank torques both act between chassis and their respective input.
Joint positions are relative to the corrected neutral CAD assembly.
"""
from pathlib import Path
import json
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import mujoco

ROOT=Path(__file__).resolve().parent

class RoboMasterEnv(gym.Env):
    metadata={'render_modes':['rgb_array','human'],'render_fps':100}

    def __init__(self,render_mode=None,visual=False,frame_skip=20,max_episode_steps=2000,
                 command_velocity=0.,domain_randomization=False,model_path=None):
        super().__init__()
        self.render_mode=render_mode
        self.model=mujoco.MjModel.from_xml_path(str(model_path or ROOT/('scene.xml' if visual or render_mode else 'scene_training.xml')))
        self.data=mujoco.MjData(self.model)
        self.frame_skip=int(frame_skip)
        if self.frame_skip<1:raise ValueError('frame_skip must be positive')
        self.dt=self.frame_skip*self.model.opt.timestep
        self.max_episode_steps=int(max_episode_steps)
        self.command_velocity=float(command_velocity)
        self.domain_randomization=domain_randomization
        self._mass=self.model.body_mass.copy();self._inertia=self.model.body_inertia.copy()
        self._friction=self.model.geom_friction.copy()
        self._stiffness=self.model.jnt_stiffness.copy();self._damping=self.model.dof_damping.copy()
        self.torque_limits=self.model.actuator_ctrlrange[:,1].copy()
        self.action_space=spaces.Box(-1.,1.,shape=(6,),dtype=np.float32)
        self.observation_space=spaces.Box(-np.inf,np.inf,shape=(39,),dtype=np.float32)
        self.base_id=self.model.body('chassis').id
        self.drive_names=[s+'_'+j for s in ['left','right'] for j in ['hip','crank','wheel_spin']]
        actual=[self.model.joint(int(j)).name for j in self.model.actuator_trnid[:,0]]
        if actual!=self.drive_names:
            raise ValueError(f'Actuator order differs from six-action contract: {actual}')
        self.drive_qadr=np.array([self.model.joint(n).qposadr[0] for n in self.drive_names])
        self.drive_vadr=np.array([self.model.joint(n).dofadr[0] for n in self.drive_names])
        self.knee_ids=[self.model.joint(s+'_knee') for s in ['left','right']]
        self.gas_jids=[self.model.joint(s+'_gas_slide').id for s in ['left','right']]
        self.gas_dofs=[self.model.joint(s+'_gas_slide').dofadr[0] for s in ['left','right']]
        self.closure_pairs=[(self.model.site(s+'_'+a).id,self.model.site(s+'_'+b).id)
                            for s in ['left','right'] for a,b in [('proximal_a','proximal_b'),('distal_a','distal_b'),('gas_end','gas_mount')]]
        self.previous_action=np.zeros(6,dtype=np.float32)
        self.steps=0;self.renderer=None;self.viewer=None;self._done=False
        self.target_height=float(self.model.qpos0[2])
        parameters=json.loads((ROOT/'model_parameters.json').read_text())
        self.motor_parameters=parameters['leg_motor'];self.wheel_parameters=parameters['wheel_motor']

    def _observe(self):
        d=self.data
        R=d.xmat[self.base_id].reshape(3,3)
        # MuJoCo free-joint translation velocity is global; angular velocity is body-local.
        linear=R.T@d.qvel[:3]
        angular=d.qvel[3:6]
        gravity=R.T@np.array([0.,0.,-1.])
        q=d.qpos[self.drive_qadr]
        v=d.qvel[self.drive_vadr]
        legq=q[[0,1,3,4]]
        knee_q=np.array([d.qpos[j.qposadr[0]] for j in self.knee_ids])
        knee_v=np.array([d.qvel[j.dofadr[0]] for j in self.knee_ids])
        diff=q[[1,4]]-q[[0,3]]
        contacts=self._wheel_contact_flags()
        # 3+3+3+4+4+6+2+2+2+1+1+2+6 = 39
        obs=np.r_[linear,angular,gravity,np.sin(legq),np.cos(legq),v*.1,knee_q,knee_v*.1,
                  diff,d.qpos[2],self.command_velocity,contacts,self.previous_action]
        return obs.astype(np.float32)

    def _wheel_contact_flags(self):
        """Load-bearing external contact; proximity/self-contact is not grounding."""
        flags=np.zeros(2);force=np.zeros(6)
        tires=[self.model.geom(s+'_tire').id for s in ['left','right']]
        for i,c in enumerate(self.data.contact):
            if c.efc_address<0:continue
            for k,tire in enumerate(tires):
                if tire not in (c.geom1,c.geom2):continue
                other=c.geom2 if c.geom1==tire else c.geom1
                if self.model.body_rootid[self.model.geom_bodyid[other]]==self.base_id:continue
                mujoco.mj_contactForce(self.model,self.data,i,force)
                if force[0]>1e-4:flags[k]=1.
        return flags

    def closure_error(self):
        return max(float(np.linalg.norm(self.data.site_xpos[a]-self.data.site_xpos[b])) for a,b in self.closure_pairs)

    def reset(self,*,seed=None,options=None):
        super().reset(seed=seed)
        if self.domain_randomization:
            scale=self.np_random.uniform(.9,1.1)
            self.model.body_mass[:]=self._mass*scale
            self.model.body_inertia[:]=self._inertia*scale
            self.model.geom_friction[:]=self._friction
            self.model.jnt_stiffness[:]=self._stiffness;self.model.dof_damping[:]=self._damping
            for side in ['left','right']:
                self.model.geom_friction[self.model.geom(side+'_tire').id,0]=self.np_random.uniform(.65,1.15)
            self.model.jnt_stiffness[self.gas_jids]=self._stiffness[self.gas_jids]*self.np_random.uniform(.85,1.15,2)
            self.model.dof_damping[self.gas_dofs]=self.np_random.uniform(1.,8.,2)
            mujoco.mj_setConst(self.model,self.data)
        mujoco.mj_resetData(self.model,self.data)
        # Perturb the free base only: independently perturbing loop joints tears a closed assembly at reset.
        angle=self.np_random.uniform(-.018,.018,3)
        quat=np.zeros(4);mujoco.mju_euler2Quat(quat,angle,'xyz')
        self.data.qpos[3:7]=quat
        self.data.qpos[2]+=self.np_random.uniform(.002,.006)
        self.data.qvel[:6]=self.np_random.uniform(-.01,.01,6)
        self.data.ctrl[:]=0
        self.steps=0;self.previous_action[:]=0;self._done=False
        if options and 'command_velocity' in options:self.command_velocity=float(options['command_velocity'])
        mujoco.mj_forward(self.model,self.data)
        return self._observe(),{'closure_error_m':self.closure_error()}

    def step(self,action):
        if self._done:raise RuntimeError('Episode ended; call reset() before step().')
        a=np.asarray(action,dtype=np.float64)
        if a.shape!=(6,) or not np.isfinite(a).all():raise ValueError('Action must be six finite normalized torques.')
        a=np.clip(a,-1.,1.)
        requested=a*self.torque_limits
        # Current/voltage bounds must be refreshed every physics tick, not only at policy rate.
        legs=[0,1,3,4];wheels=[2,5];p=self.motor_parameters;wp=self.wheel_parameters
        for _ in range(self.frame_skip):
            velocity=self.data.qvel[self.drive_vadr[legs]]
            lo=np.clip(-p['envelope_intercept_nm']-p['envelope_slope_nm_s_rad']*velocity,-40.,40.)
            hi=np.clip(p['envelope_intercept_nm']-p['envelope_slope_nm_s_rad']*velocity,-40.,40.)
            self.data.ctrl[:]=requested
            self.data.ctrl[legs]=np.clip(requested[legs],lo,hi)
            wheel_velocity=self.data.qvel[self.drive_vadr[wheels]]
            wheel_lo=np.clip(-wp['envelope_intercept_nm']-wp['envelope_slope_nm_s_rad']*wheel_velocity,-wp['peak_torque_nm'],wp['peak_torque_nm'])
            wheel_hi=np.clip(wp['envelope_intercept_nm']-wp['envelope_slope_nm_s_rad']*wheel_velocity,-wp['peak_torque_nm'],wp['peak_torque_nm'])
            self.data.ctrl[wheels]=np.clip(requested[wheels],wheel_lo,wheel_hi)
            mujoco.mj_step(self.model,self.data)
        # Refresh sites and sensors for the newly integrated qpos (mj_step leaves them at the previous position).
        mujoco.mj_forward(self.model,self.data)
        self.steps+=1
        R=self.data.xmat[self.base_id].reshape(3,3)
        up=float(R[2,2]);height=float(self.data.qpos[2]);vx=float((R.T@self.data.qvel[:3])[0])
        closure=self.closure_error()
        finite=np.isfinite(self.data.qpos).all() and np.isfinite(self.data.qvel).all()
        warnings=sum(w.number for w in self.data.warning)
        failure=not finite or warnings>0 or closure>.002
        fallen=height<.22 or up<.5
        terminated=bool(failure or fallen)
        truncated=bool(self.steps>=self.max_episode_steps)
        tracking=np.exp(-((vx-self.command_velocity)/.5)**2)
        height_reward=np.exp(-((height-self.target_height)/.09)**2)
        power=np.sum(abs(self.data.ctrl*self.data.qvel[self.drive_vadr]))
        reward=float((1.5*tracking+1.5*max(0.,up)+height_reward-.03*np.sum(a*a)
                      -.02*np.sum((a-self.previous_action)**2)-.0005*power)*self.dt)
        if terminated:reward-=1.
        self.previous_action[:]=a
        self._done=terminated or truncated
        info={'closure_error_m':closure,'numerical_failure':bool(failure),'fallen':bool(fallen),
              'base_height_m':height,'upright':up,'velocity_m_s':vx,'warning_count':warnings}
        obs=self._observe()
        if failure:
            # MuJoCo may auto-reset an unstable state to finite numbers.
            # Warnings and excessive closure error must also stop training.
            raise FloatingPointError(f'MuJoCo numerical failure: {info}')
        if self.render_mode=='human':self.render()
        return obs,reward,terminated,truncated,info

    def render(self):
        if self.render_mode=='human':
            from mujoco import viewer as viewer_module
            if self.viewer is None:self.viewer=viewer_module.launch_passive(self.model,self.data)
            self.viewer.sync();return None
        if self.renderer is None:self.renderer=mujoco.Renderer(self.model,height=600,width=900)
        camera=mujoco.MjvCamera();camera.lookat[:]=self.data.xpos[self.base_id];camera.distance=1.3;camera.azimuth=130;camera.elevation=-18
        opt=mujoco.MjvOption();opt.geomgroup[3]=0;opt.sitegroup[:]=0
        self.renderer.update_scene(self.data,camera,scene_option=opt)
        return self.renderer.render()

    def close(self):
        if self.renderer is not None:self.renderer.close();self.renderer=None
        if self.viewer is not None:self.viewer.close();self.viewer=None

if __name__=='__main__':
    e=RoboMasterEnv()
    obs,info=e.reset(seed=0)
    print('observation',obs.shape,'actions',e.action_space,'reset',info)
    for i in range(2000):
        obs,reward,done,trunc,info=e.step(e.action_space.sample())
        if done or trunc:e.reset()
    print('Random policy completed.',info)
    e.close()
