"""Independent 270mm Isaac scene on the complete frozen-E0 D0--D7 plant."""
import torch
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnv
import isaaclab.sim as sim
from chassis_pd_training_env import ChassisPDMod4Env
import mod4_task as task
from isaaclab.managers import RewardTermCfg
from isaaclab.utils import configclass

def physical_alive(env):return torch.ones(env.num_envs,device=env.device)
@configclass
class PhysicalRewardsCfg:
    physical_alive=RewardTermCfg(func=physical_alive,weight=1.)

def configure(cfg,num_envs,seed):
    cfg.rewards=PhysicalRewardsCfg()
    cfg.scene.num_envs=num_envs;cfg.scene.env_spacing=5.;cfg.seed=seed;cfg.decimation=8;cfg.sim.dt=.0025;cfg.episode_length_s=5.
    cfg.terminations.closure.params['threshold']=.01;cfg.terminations.mimic.params['threshold']=.01
    cfg.scene.step270=AssetBaseCfg(prim_path='{ENV_REGEX_NS}/step270',spawn=sim.CuboidCfg(size=(3.,2.,.27),collision_props=sim.CollisionPropertiesCfg(),physics_material=sim.RigidBodyMaterialCfg(static_friction=.9,dynamic_friction=.9,restitution=0.)),init_state=AssetBaseCfg.InitialStateCfg(pos=(1.5,0,.135)))
    cfg.scene.robot.init_state.pos=(-.8,0.,float(task.CONTRACT['spawn_height_m']))
    cfg.commands.twist.heading_command=False;cfg.commands.twist.rel_standing_envs=0.;cfg.commands.twist.rel_heading_envs=0.;cfg.commands.twist.resampling_time_range=(10.,10.)
    cfg.commands.twist.ranges.lin_vel_x=(1.4,1.4);cfg.commands.twist.ranges.ang_vel_z=(0.,0.)
    cfg.events.reset_base.params['pose_range']={'x':(-.02,.02),'y':(-.01,.01),'yaw':(-.03,.03)}
    cfg.events.reset_base.params['velocity_range']={k:(0.,0.) for k in ['x','y','z','roll','pitch','yaw']}
    cfg.curriculum.gyro_window=None
    return cfg

class LQRStepEnv(ChassisPDMod4Env):
    def _reset_idx(self,ids):
        # Preserve the true terminal physical state before inherited automatic reset.
        if hasattr(self,'capture_terminal') and self.capture_terminal is not None:self.capture_terminal(ids)
        super()._reset_idx(ids)
        self._mod4_mode_bit=torch.ones(self.num_envs,device=self.device,dtype=torch.long)
    def binding_receipt(self):
        r=self.scene['robot']
        return {'num_envs':self.num_envs,'num_bodies':r.num_bodies,'num_joints':r.num_joints,'joint_names':r.joint_names,'body_names':r.body_names,'physics_dt':self.physics_dt,'policy_dt':self.step_dt,'closure_episode_threshold_m':self.cfg.terminations.closure.params['threshold'],'mimic_episode_threshold_rad':self.cfg.terminations.mimic.params['threshold'],'model':task.USD_PATH,'action_order':task.ACTION_ORDER,'D3':self.feedback_delay_recipe(),'D4':self.action_delay_recipe(),'D5':self.spring_pressure_recipe(),'D6':self.gas_damping_recipe(),'D7':self.chassis_pd_recipe(),'scalar_step_height_m':.27,'solver_position':32,'solver_velocity':4,'complete_closed_chain':True,'rl_root_state_teleport_after_reset':False}
