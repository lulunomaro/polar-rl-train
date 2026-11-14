"""Keep the pinned SCUT equations and the existing standing task substitutions."""
import ast
import inspect
from pathlib import Path
import textwrap
import torch
from mod4v1_scut.rewards import ScutRewards as Base
from mod4v1_scut.config import reward_config as original_config
from mod4v1_scut.math_ops import quat_apply_inverse, euler_xyz_from_quat, wrap_to_pi


def configuration():
    cfg = original_config('trained_stair')
    cfg.use_absolute_height = False
    cfg.use_leg_length_as_height = True
    cfg.vel_height_gate_enabled = False
    cfg.height_upright_gate_enabled = False
    cfg.enable_state_machines = False
    for name in ('airborne_state_machine_cfg','jump_takeoff_state_machine_cfg',
                 'stair_state_machine_cfg','wheel_forward_scan_cfg'):
        getattr(cfg,name)['enabled'] = False
    cfg.height_range = (.334,.334)
    cfg.episode_length_s = 10.
    cfg.rewards.update(pen_theta_no0=-2., stand32_heading=1., stand32_wheel_distance=1.)
    return cfg


def make_reward_class(meta):
    names = {**meta['spec']['source_to_v3']['joints'], **meta['spec']['source_to_v3']['bodies']}
    class Names(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and node.value in names:
                return ast.copy_location(ast.Constant(names[node.value]),node)
            return node
    node = ast.parse(textwrap.dedent(inspect.getsource(Base.__init__)))
    node = Names().visit(node); ast.fix_missing_locations(node)
    scope = dict(Base.__init__.__globals__)
    scope.update(LEGS=tuple(meta['runtime']['policy_action_order'][:4]),
        WHEELS=tuple(meta['runtime']['policy_action_order'][4:]),
        WHEEL_BODIES=tuple(meta['spec']['frames']['wheel_order']),
        GUIDE_BODIES=tuple(meta['spec']['contact_groups']['guides']),
        STRUCTURAL_BODIES=tuple(meta['spec']['contact_groups']['structural']))
    exec(compile(node,__file__,'exec'),scope)
    constructor = scope['__init__']

    class StandingRewards(Base):
        def __init__(self,robot,n,device):
            constructor(self,robot,meta,n,device,profile='trained_stair',
                        cfg=configuration(),quaternion_order='wxyz')
            self._left_right_leg_joint_pair_idx = (
                [robot.joint_names.index(s) for s in ('left_front1_joint','left_rear1_joint')],
                [robot.joint_names.index(s) for s in ('right_front1_joint','right_rear1_joint')])
            self._hip_anchors = torch.tensor([meta['joints'][s+'_rear1_joint']['local_pos0']
                for s in ('left','right')],device=device)
            self.length = torch.zeros(n,2,device=device)
            self.theta = torch.zeros_like(self.length)

        def virtual_legs(self):
            d = self.robot.data
            rel = d.body_pos_w[:,self._wheel_link_idx]-d.root_pos_w[:,None]
            v = quat_apply_inverse(d.root_quat_w[:,None].expand(-1,2,-1),rel)-self._hip_anchors[None]
            return v.norm(dim=-1),torch.atan2(v[...,0],-v[...,2])

        def _get_observed_height(self,*args): return self.virtual_legs()[0].mean(-1)
        def _get_height_reward_reference_height(self,*args): return self._get_observed_height()
        def _get_height_reward_target_height(self): return self.height_cmd.new_full((self.num_envs,),.334)

        def motor_stop_terms(self,airborne=False):
            # The standing V40 task disables motor-stop shaping. Actual CAD
            # stops remain in the asset and are independently read in the probe.
            z = self.height_cmd.new_zeros(self.num_envs)
            return z,z.clone(),z.clone()

        def _get_wheel_motor_z_axis_align_error_sq(self):
            _,theta = self.virtual_legs()
            d = self.robot.data
            rel = d.body_pos_w[:,self._wheel_link_idx]-d.root_pos_w[:,None]
            v = quat_apply_inverse(d.root_quat_w[:,None].expand(-1,2,-1),rel)-self._hip_anchors[None]
            direction = v/v.norm(dim=-1,keepdim=True).clamp_min(1e-6)
            gravity = d.projected_gravity_b[:,None].expand(-1,2,-1)
            error = (1-(direction*gravity).sum(-1).clamp(-1,1).square()).clamp_min(0).mean(-1)
            tolerance = float(getattr(self.cfg,'wheel_motor_z_axis_align_tolerance',0.))
            return (error-tolerance*tolerance).clamp_min(0)

        def _postprocess_reward_terms(self,terms):
            values = super()._postprocess_reward_terms(terms)
            d = self.robot.data
            yaw = wrap_to_pi(euler_xyz_from_quat(d.root_quat_w)[2])
            delta = d.body_pos_w[:,self._wheel_link_idx[0]]-d.body_pos_w[:,self._wheel_link_idx[1]]
            span = -yaw.sin()*delta[:,0]+yaw.cos()*delta[:,1]
            self.length,self.theta = self.virtual_legs()
            err = (torch.abs(span-meta['nominal_span_m'])-.02).clamp_min(0)
            values.update(pen_theta_no0=self.theta.square().sum(-1),
                stand32_heading=-(yaw/.35).square(),
                stand32_wheel_distance=-(err/.05).square().clamp_max(4.))
            structural = [i for i in self._undesired_contact_link_idx if i not in self._reset_contact_link_idx]
            values['undesired_contact'] = (self.contact_sensor.data.net_forces_w[:,structural].norm(dim=-1)>1.).any(-1).float()
            missing = [k for k,w in self.cfg.rewards.items() if w and k not in values]
            if missing:
                raise KeyError('Enabled reward terms missing: '+str(missing))
            return values

    # Same standing-task removal of contact-triggered resets as V40/V42.
    raw = textwrap.dedent(inspect.getsource(Base._get_dones))
    old = 'terminate = torch.any(reset_contact_force > 1.0, dim=-1)'
    if raw.count(old) != 1:
        raise ValueError('Pinned standing termination source changed')
    raw = raw.replace(old,'terminate = torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)')
    scope = dict(Base._get_dones.__globals__)
    exec(compile(raw,__file__,'exec'),scope)
    StandingRewards._get_dones = scope['_get_dones']
    return StandingRewards
