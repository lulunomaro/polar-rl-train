"""The original MOD4 robot/reset/runtime on the supplied whole RM 7v7 terrain."""
from pathlib import Path
import json,hashlib
import mujoco
from current_moe_sim import CurrentMoESim
from sim_runtime import Mod4Sim,RuntimeConfig
D=Path(__file__).resolve().parent
routes=json.loads((D.parent/'rmuc2026_training/data/routes.json').read_text(encoding='utf-8'))
ROUTES={r['id']:r for r in routes}


class RM7V7MoESim(CurrentMoESim):
    def __init__(self):
        self.reset_bank=json.loads((D/'src_snapshot/reset_bank.json').read_text())['poses']
        self.spawn=(-9.,-1.,0.)
        self.delivery=json.loads((D/'latest_moe_hour4_20261018.json').read_text(encoding='utf-8'))
        policy=D/'latest_moe_hour4_20261018.onnx'
        assert hashlib.sha256(policy.read_bytes()).hexdigest()==self.delivery['onnx_sha256']
        Mod4Sim.__init__(self,D/'rm7v7_latest_moe.xml',policy,RuntimeConfig(**json.loads((D/'runtime_config.json').read_text())))
        self.reset_route('flat_run')

    def reset_route(self,key):
        r=ROUTES[key];x,y,z=r['spawn_ground_m']
        self.reset(x,y,r['spawn_yaw_rad'],ground_z=z)

    def reset(self,x=-9.,y=-1.,yaw=0.,ground_z=None):
        if ground_z is None:
            # This is a reset placement only, never a policy/control observation.
            # Nearby source route annotations disambiguate tunnel floor vs roof.
            candidates=sorted(routes,key=lambda r:(r['spawn_ground_m'][0]-x)**2+(r['spawn_ground_m'][1]-y)**2)
            r=candidates[0]
            ground_z=r['spawn_ground_m'][2] if (r['spawn_ground_m'][0]-x)**2+(r['spawn_ground_m'][1]-y)**2<1e-6 else 0.
        super().reset(x,y,yaw,ground_z)
