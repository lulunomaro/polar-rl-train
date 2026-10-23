from pathlib import Path
import json,math
import mujoco,numpy as np
from sim_runtime import Mod4Sim,RuntimeConfig,UserCommand
D=Path(__file__).resolve().parent
class CurrentSim(Mod4Sim):
    def __init__(self):
        self.reset_bank=json.loads((D/'src_snapshot/reset_bank.json').read_text())['poses']
        self.spawn=(-1.,0.,0.)
        receipt=json.loads((D/'BUILD_RECEIPT.json').read_text())
        super().__init__(D/'playground.xml',D/receipt['onnx'],RuntimeConfig(**json.loads((D/'runtime_config.json').read_text())))
        fields=np.load(D/'terrain.npz')
        for name in fields.files:
            idx=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_HFIELD,name);start=self.model.hfield_adr[idx]
            self.model.hfield_data[start:start+fields[name].size]=fields[name].ravel()
        self.reset(*self.spawn)
    def reset(self,x=-1.,y=0.,yaw=0.,ground_z=0.):
        super().reset(x,y,yaw,ground_z)
        pose=min(self.reset_bank,key=lambda p:abs(p['root_height_m']-.25)+.1*abs(p['wheel_x_m']))
        for name,value in pose['joint_pos'].items():
            idx=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_JOINT,name)
            if idx<0:raise ValueError('Missing reset joint: '+name)
            self.data.qpos[self.model.jnt_qposadr[idx]]=value
        self.data.qpos[2]=ground_z+pose['root_height_m']
        self.command=UserCommand(height=.25,mode=0,auto_mode=False)
        mujoco.mj_forward(self.model,self.data)
        self._seed_observation_history(self.observation_frame())
    def parameter_readback(self):
        contract=json.loads((D/'src_snapshot/import_contract.json').read_text());errors={}
        for name,info in contract['joints'].items():
            idx=self._joint(name);dof=self.model.jnt_dofadr[idx]
            errors[name]=dict(armature_error=float(abs(self.model.dof_armature[dof]-info['armature'])),range_error=float(np.max(np.abs(self.model.jnt_range[idx]-info['limits_si']))) if info['limits_si'] is not None else 0.)
        assert all(v['armature_error']<1e-8 and v['range_error']<1e-8 for v in errors.values()),errors
        assert self.model.nu==6 and self.model.neq==10 and self.model.nbody==32
        return dict(nbody_excluding_world=self.model.nbody-1,actuators=self.model.nu,equalities=self.model.neq,all_joint_ranges_armatures_match=True,initial_closure_m=self.closure_error(),initial_mimic_rad=self.mimic_error(),height_command=self.command.height)
