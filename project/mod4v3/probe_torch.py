"""CPU tensor boundary regression; no simulator or training process is started."""
from pathlib import Path
import argparse
import json
import sys
import traceback
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import torch
from semantics import Semantics, ScutRobotView, weighted_rewards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise FileExistsError('Choose a new report; preserve earlier results')
    torch.set_num_threads(2)
    torch.manual_seed(53)
    api = Semantics(args.package)
    checks, errors = {}, []
    def ck(name, value):
        checks[name] = bool(value)
        if not checks[name]:
            raise AssertionError(name)
    try:
        q = torch.randn(2, 30, dtype=torch.float64, requires_grad=True)
        v = torch.randn_like(q)
        tau = torch.randn_like(q)
        ck('position_gradcheck', torch.autograd.gradcheck(api.positions, (q,)))
        ck('inverse_gradcheck', torch.autograd.gradcheck(api.native_positions, (q,)))
        ck('force_gradcheck', torch.autograd.gradcheck(api.generalized_forces, (q,)))
        ck('position_roundtrip', torch.allclose(api.native_positions(api.positions(q)), q))
        ck('force_roundtrip', torch.allclose(api.native_forces(api.generalized_forces(tau)), tau))
        ck('power_conjugate', torch.allclose((tau*v).sum(-1), (api.generalized_forces(tau)*api.velocities(v)).sum(-1)))
        perm = torch.randperm(30).tolist()
        names = [api.native_names[i] for i in perm]
        speed = torch.arange(1,31,dtype=q.dtype)[None]
        limits = torch.stack([-speed, 2*speed], dim=-1)
        packed = torch.tensor([[1.,2.,3.,.1,.2,.3,.9,4.,5.,6.,7.,8.,9.]], dtype=q.dtype, requires_grad=True)
        raw = SimpleNamespace(joint_names=names, body_names=list(api.spec['source_to_v3']['bodies'].values()),
            data=SimpleNamespace(joint_pos=api.to_newton_displacement(q)[...,perm],
                joint_pos_limits=limits[...,perm,:], joint_vel_limits=speed[...,perm],
                root_state_w=packed, default_root_state=packed, joint_armature=speed[...,perm]))
        view = ScutRobotView(raw,args.package,quaternion_order='xyzw',position_basis='newton_displacement')
        ck('shuffled_newton_view', torch.allclose(view.data.joint_pos,api.positions(q)))
        ck('shuffled_speed_limits', torch.allclose(view.data.joint_vel_limits,api.velocity_limits(speed)))
        ck('shuffled_newton_interval_limits', torch.allclose(view.data.joint_pos_limits,api.position_limits(limits,position_basis='newton_displacement')))
        ck('packed_root_quaternion', torch.equal(view.data.root_state_w[:,3:7],packed[:,[6,3,4,5]]))
        ck('packed_root_gradient', torch.allclose(torch.autograd.grad(view.data.root_state_w.sum(),packed)[0],torch.ones_like(packed)))
        ck('native_tensor_unmodified', torch.equal(raw.data.root_state_w,packed))
        rejected = False
        try:
            getattr(view.data,'joint_armature',None)
        except NotImplementedError:
            rejected = True
        ck('unsupported_armature_rejected',rejected)
        runtime = json.loads((args.package/'runtime_config.json').read_bytes())
        defaults = torch.tensor([[runtime['initial_joint_positions'][n] for n in api.spec['control']['policy_action_order'][:4]]],dtype=q.dtype)
        actions = torch.zeros(2,6,dtype=q.dtype,requires_grad=True)
        out = api.decode_actions(actions,defaults,leg_scale=.5,wheel_scale=10.,wheel_mode='torque',position_basis='newton_displacement')
        ck('zero_action_zero_newton_leg_target',all(torch.equal(x,torch.zeros(2,dtype=q.dtype)) for x in out['leg_position_targets'].values()))
        loss = sum(x.sum() for x in out['leg_position_targets'].values())+sum(x.sum() for x in out['wheel_targets'].values())
        ck('action_target_gradients',torch.equal(torch.autograd.grad(loss,actions)[0],torch.tensor([[.5,.5,.5,.5,10.,10.]]*2,dtype=q.dtype)))
        reward,_ = weighted_rewards(dict(posture=q.square().sum(-1)),dict(posture=-2.),.02)
        ck('reward_gradient_retained',torch.allclose(torch.autograd.grad(reward.sum(),q)[0],-.08*q))
        ck('dtype_device_retained',view.data.joint_pos.dtype==q.dtype and view.data.joint_pos.device==q.device)
    except Exception:
        errors.append(traceback.format_exc())
    result = dict(id='MOD4V3_R2_TORCH_BOUNDARY',passed=not errors,checks=checks,errors=errors,
                  torch=torch.__version__,device='cpu',dtype='float64',seed=53,training_started=False)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
    return result['passed']


if __name__=='__main__':
    sys.exit(0 if main() else 1)
