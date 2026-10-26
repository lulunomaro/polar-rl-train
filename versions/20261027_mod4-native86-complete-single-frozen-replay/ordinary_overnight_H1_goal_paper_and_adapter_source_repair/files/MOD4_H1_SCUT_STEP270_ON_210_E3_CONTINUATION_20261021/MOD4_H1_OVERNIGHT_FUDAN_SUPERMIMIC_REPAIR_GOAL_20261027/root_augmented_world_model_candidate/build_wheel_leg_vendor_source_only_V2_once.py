"""Build an isolated, explicit seven-component wheel-leg vendor candidate.

No model files, runtime payloads, controller or Task are created.
"""
from pathlib import Path
import ast, hashlib, json, shutil, traceback
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
T=ROOT.parent
SOURCE=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/source/supermimic_vendor_v2'
DEST=HERE/'v2/supermimic_wheel_leg_v3'
REPORT=ROOT/'reports/WHEEL_LEG_V3_ISOLATED_VENDOR_BUILD_SOURCE_V2_ACTUAL.json'
assert not REPORT.exists() and not DEST.exists(), 'one new source build only'
inputs={}
changes=[]
def read(name):
    raw=(SOURCE/name).read_bytes()
    inputs[name]={'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()}
    return raw.decode('utf8').replace('\r\n', '\n') if name.endswith('.py') else raw.decode('utf8')
def one(text,old,new,label):
    assert text.count(old)==1, (label,text.count(old))
    changes.append(label)
    return text.replace(old,new,1)
try:
    DEST.mkdir(parents=True)
    for name in ['__init__.py','contract.py','geometry.py','networks.py','replay.py','learner.py','logging.py','LICENSE','NOTICE']:
        original=read(name)
        text=original.replace('supermimic_vendor_v2','supermimic_wheel_leg_v3') if name.endswith('.py') else original
        if name=='geometry.py':
            start=text.index('def flatten_state(')
            end=text.index('\ndef invariant_features(',start)
            old=text[start:end]
            new='''def flatten_state(state: State) -> torch.Tensor:
    if len(state) != 7:
        raise ValueError("v3 requires six physical state parts plus explicit dynamic aux54")
    position, rotation, lin_vel, ang_vel, joint_pos, joint_vel, aux = state
    if joint_pos.shape[-1] != 30 or joint_vel.shape[-1] != 30 or aux.shape[-1] != 54:
        raise ValueError("v3 physical30/aux54 layout mismatch")
    return torch.cat((position, mat_to_quat(rotation), lin_vel, ang_vel, joint_pos, joint_vel, aux), -1)


def unflatten_state(value: torch.Tensor) -> State:
    if value.shape[-1] != 127:
        raise ValueError("v3 packed state is physical73 plus explicit dynamic54; legacy73 is not a resume")
    return (
        value[..., 0:3], quat_to_mat(value[..., 3:7]),
        value[..., 7:10], value[..., 10:13],
        value[..., 13:43], value[..., 43:73], value[..., 73:127],
    )

'''
            text=text[:start]+new+text[end:]
            changes.append('geometry explicit packed127/seven components; no fictitious joints')
        if name=='replay.py':
            text=one(text,'    action_dim: int | None = None,\n) -> dict','    action_dim: int | None = None,\n    state_dim: int | None = None,\n) -> dict','replay field explicit state width')
            text=one(text,'    state_dim = 13 + 2 * num_joints','    state_dim = 13 + 2 * num_joints if state_dim is None else state_dim','replay legacy default retained')
            text=one(text,'        action_dim: int | None = None,\n    ):','        action_dim: int | None = None,\n        state_dim: int | None = None,\n    ):','replay constructor explicit width')
            text=one(text,'self.fields = _make_fields(num_joints, context_dim, action_dim)','self.fields = _make_fields(num_joints, context_dim, action_dim, state_dim)','replay constructor passes explicit width')
        if name=='learner.py':
            text=one(text,'from .networks import Critic, Policy, WorldModel, mlp','from .networks import Critic, Policy, mlp\nfrom .augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel as WorldModel','new model factory binding')
            text=one(text,'            action_dim=getattr(self.mdp,"action_dim",self.mdp.num_joints),\n        )','            action_dim=getattr(self.mdp,"action_dim",self.mdp.num_joints),\n            state_dim=self.mdp.packed_state_dim,\n        )','learner passes physical+aux width')
            text=one(text,'                torch.full((self.mdp.num_joints,), 5e-2),','                torch.full((self.mdp.num_joints,), 5e-2),\n                torch.full((self.mdp.auxiliary_dim,), 1e-3),','explicit aux loss floor')
            text=one(text,'            "action_dim": getattr(self.mdp,"action_dim",self.mdp.num_joints),','            "action_dim": getattr(self.mdp,"action_dim",self.mdp.num_joints),\n            "auxiliary_dim": self.mdp.auxiliary_dim,\n            "edge_x_m": self.mdp.step_edge_x_m,\n            "platform_top_z_m": self.mdp.platform_top_z_m,','terrain/dynamic worldmodel factory contract')
            start=text.index('        return (\n            torch.stack([prediction[0]')
            end=text.index('\n\n    def _wm_err',start)
            text=text[:start]+'        return tuple(torch.stack([prediction[i] for prediction in predictions], 1) for i in range(7))'+text[end:]
            changes.append('autoregressive fit stacks seven true state components')
            text=one(text,'for index in range(6))','for index in range(7))','imagined reward/value batches carry aux state')
        if name=='contract.py':
            # Keep the original protocol source with a truthful runtime extension notice.
            text += '\n# Wheel-leg v3 State adds a seventh dynamic auxiliary54 tensor.\n# Physical joint count remains30; packed state width127.\n'
        if name.endswith('.py'):
            ast.parse(text, filename=name)
        (DEST/name).write_bytes(text.encode('utf8'))
    model=(HERE/'augmented_wheel_leg_world_model_v1.py').read_bytes()
    (DEST/'augmented_wheel_leg_world_model_v1.py').write_bytes(model.replace(b'supermimic_vendor_v2',b'supermimic_wheel_leg_v3'))
    outputs=[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(DEST.iterdir())]
    value={'schema':'source_only_isolated_wheel_leg_vendor_v3_build_v1','passed':True,'input_source':str(SOURCE),'inputs':inputs,'outputs':outputs,'changes':changes,'state_layout':'physical30 joints/73 scalar packed state plus auxiliary54, seven components','original_algorithm_loop':'collection,8-step autoregressive fitting,BPTT through frozen WM,critic bootstrap retained; no PPO hybrid','not_installed':True,'actual_SDK':False,'new_Task_GO':False,'checkpoint_migration':'Legacy native86 dimension/normalizer/optimizer shapes incompatible; explicit new architecture admission required, no claimed exact resume.'}
except BaseException:
    value={'passed':False,'error':traceback.format_exc(),'inputs':inputs,'changes_before_error':changes,'partial_source_preserved':str(DEST),'no_runtime':True}
    REPORT.write_text(json.dumps(value,indent=2),'utf8')
    raise
REPORT.write_text(json.dumps(value,indent=2),'utf8')
print(json.dumps({'passed':value['passed'],'outputs':len(outputs),'report':str(REPORT)}))


