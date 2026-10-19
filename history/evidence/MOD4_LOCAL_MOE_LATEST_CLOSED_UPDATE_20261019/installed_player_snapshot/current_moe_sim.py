"""Latest manual expert bundle in the original October8 playground and adapter."""
from pathlib import Path
import hashlib, json
import mujoco
import numpy as np
from current_sim import CurrentSim
from sim_runtime import Mod4Sim, RuntimeConfig

D = Path(__file__).resolve().parent


class CurrentMoESim(CurrentSim):
    def __init__(self):
        self.reset_bank = json.loads((D/'src_snapshot/reset_bank.json').read_text())['poses']
        self.spawn = (-1., 0., 0.)
        policy = D/'latest_moe_20261018.onnx'
        self.delivery = json.loads(policy.with_suffix('.json').read_text(encoding='utf-8'))
        assert hashlib.sha256(policy.read_bytes()).hexdigest() == self.delivery['onnx_sha256']
        # The requested old UI's nominal60/2 PD, crank0.5, terrain, reset poses,
        # springs, model, sensors and action mapping are all retained.
        Mod4Sim.__init__(self, D/'playground.xml', policy,
            RuntimeConfig(**json.loads((D/'runtime_config.json').read_text())))
        fields = np.load(D/'terrain.npz')
        for name in fields.files:
            idx = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_HFIELD, name)
            start = self.model.hfield_adr[idx]
            self.model.hfield_data[start:start+fields[name].size] = fields[name].ravel()
        self.reset(*self.spawn)

    def reset(self, x=-1., y=0., yaw=0., ground_z=0.):
        super().reset(x, y, yaw, ground_z)
        self.jump_pending = False
        self.jump_ticks = 0

    def select_skill(self, mode):
        self.command.auto_mode = False
        self.command.mode = mode
        self.command.vx = self.command.vy = self.command.wz = 0.
        self.jump_pending = False
        self.jump_ticks = 0

    def request_jump(self):
        self.select_skill(0)
        if self.control_steps < 100:
            self.jump_pending = True
        else:
            self.command.mode = 4
            self.jump_ticks = 80

    @property
    def skill(self):
        if self.jump_pending:
            return 'H1 等待初次1秒普通站立'
        return {0:'E0/W35 普通驾驶', 3:'E3 恢复', 4:'H1 跳跃', 6:'E2 自旋'}.get(self.command.mode, '普通驾驶')

    def step_control(self, *a, **kw):
        action = super().step_control(*a, **kw)
        if self.jump_pending and self.control_steps >= 100:
            self.jump_pending = False
            self.command.mode = 4
            self.jump_ticks = 80
        elif self.jump_ticks:
            self.jump_ticks -= 1
            if self.jump_ticks == 0:
                self.command.mode = 0
        return action
