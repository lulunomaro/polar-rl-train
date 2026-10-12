from pathlib import Path
import json, math
import mujoco, numpy as np
from sim_runtime import Mod4Sim, RuntimeConfig, UserCommand

D=Path(__file__).resolve().parent
SERIES=json.loads((D/'SERIES.json').read_text(encoding='utf8'))
MODELS=json.loads((D/'DOWNLOAD_RECEIPT.json').read_text(encoding='utf8'))['models']

class SeriesSim(Mod4Sim):
    def __init__(self,scene_id='wave50',model_id='wave449',reverse=False):
        self.scene=next(s for s in SERIES['scenes'] if s['id']==scene_id)
        self.model_item=next(m for m in MODELS if m['id']==model_id)
        self.reverse=reverse
        self.reset_bank=json.loads((D/'src_snapshot/reset_bank.json').read_text(encoding='utf8'))['poses']
        super().__init__(self.scene['xml'],self.model_item['local_path'],RuntimeConfig(**json.loads((D/'runtime_config.json').read_text(encoding='utf8'))))
        with np.load(D/'terrain.npz') as fields:
            for i in range(self.model.nhfield):
                name=mujoco.mj_id2name(self.model,mujoco.mjtObj.mjOBJ_HFIELD,i)
                values=fields[name]
                adr=self.model.hfield_adr[i];size=self.model.hfield_nrow[i]*self.model.hfield_ncol[i]
                assert size==values.size
                self.model.hfield_data[adr:adr+size]=values.ravel()
        self.reset_entry(reverse)

    def reset(self,x=0.,y=0.,yaw=0.,ground_z=0.):
        super().reset(x,y,yaw,ground_z)
        pose=min(self.reset_bank,key=lambda p:abs(p['root_height_m']-.25)+.1*abs(p['wheel_x_m']))
        for name,value in pose['joint_pos'].items():
            j=self._joint(name);self.data.qpos[self.model.jnt_qposadr[j]]=value
        self.data.qpos[2]=ground_z+pose['root_height_m']
        self.command=UserCommand(height=.25,mode=0,auto_mode=False)
        mujoco.mj_forward(self.model,self.data)
        self._seed_observation_history(self.observation_frame())

    def reset_entry(self,reverse=False):
        self.reverse=bool(reverse)
        x,y,yaw=self.scene['spawn'];ground=0.;kind=self.scene['kind']
        if reverse:
            if kind in ('wave','rm70'):x=-x # Keep heading; S tests actual backwards motion
            elif kind=='curb':x=.8;yaw=math.pi;ground=self.scene['height']
            elif kind=='slope':x=2.;yaw=math.pi;ground=self.scene['height']
            elif kind=='stair':x=2.;yaw=math.pi;ground=3*self.scene['height']
            else:yaw=math.pi
        self.reset(x,y,yaw,ground)

    def switch_model(self,id):
        self.model_item=next(m for m in MODELS if m['id']==id)
        self.set_policy(self.model_item['local_path'])
        self.reset_entry(self.reverse)

    def parameter_readback(self):
        c=json.loads((D/'src_snapshot/import_contract.json').read_text(encoding='utf8'))
        errors={}
        for name,info in c['joints'].items():
            i=self._joint(name);dof=self.model.jnt_dofadr[i]
            errors[name]=dict(armature_error=float(abs(self.model.dof_armature[dof]-info['armature'])),range_error=float(np.max(np.abs(self.model.jnt_range[i]-info['limits_si']))) if info['limits_si'] is not None else 0.)
        assert all(v['armature_error']<1e-8 and v['range_error']<1e-8 for v in errors.values())
        assert self.model.nu==6 and self.model.neq==10 and self.model.nbody==32
        assert self.cfg.yaw_assist_gain==0 and not self.command.auto_mode
        return dict(nbody_excluding_world=31,actuators=6,equalities=10,joint_ranges_armatures_exact=True,robot_parameter_errors=errors,physics_dt_s=self.model.opt.timestep,policy_hz=self.cfg.policy_hz,decimation=self.decimation,observation_width=35,teacher=False,yaw_assist=False,automatic_terrain_truth=False,policy_sha256=self.policy.sha256)

    def body_velocity(self):
        # BODY local axes are principal inertia axes; XBODY is the chassis frame.
        # A rotated inertia tensor must not rotate displayed driving/yaw velocities.
        v=np.zeros(6)
        mujoco.mj_objectVelocity(self.model,self.data,mujoco.mjtObj.mjOBJ_XBODY,self.chassis_id,v,1)
        return v
