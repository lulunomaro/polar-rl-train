"""Own flat jump analytic task; source candidate, not a demonstrated skill.

Keeps native127/dynamic54/static31/obs86/goal146/action6. The reference is a
task-space low-jump primitive, NOT a measured Fudan joint motion or a 270mm
step reference. Physical callbacks and the independent real counter decide skill.
"""
import math
import torch
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4JumpMdp, require
from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
from static_dynamic_delay_contract_v1 import task_relative_observation
from flat_jump_phase_objective_source_v1 import FlatJumpPhase, flat_jump_terms

from private_phase_frame_v1 import encode as encode_frame, decode as decode_private_frame

def decode_frame(frames):
    row = decode_private_frame(frames)
    return row['public_age'], row['delay_ticks']

class OwnFlatJumpReference:
    def __init__(self, document, device='cpu', *, order_scope='unbound'):
        require(document.get('schema') == 'mod4.own_flat_jump_reference.v1', 'typed own flat reference required')
        self.document = document
        self.device = torch.device(device)
        self.order_scope = order_scope
        self.names = tuple(document['joint_names'])
        require(len(self.names) == len(set(self.names)) == 30, 'actual named30 required')
        self.metadata = document['metadata']
        require(self.metadata['control_dt_s'] == .01, 'flat course native100Hz required')
        require(self.metadata['foreign_transitions_for_world_model'] is False, 'own plant transitions only')
        require(self.metadata['physical270_success_unchanged'] is True, 'separate unchanged270 goal')
        require(self.metadata['source_is_measured_successful_Fudan_joint_motion'] is False, 'no invented demonstration')
        self.phase = FlatJumpPhase(height_m=float(self.metadata['height_m']))
        self.neutral = torch.tensor(document['neutral_packed73'], device=device, dtype=torch.float32)
        require(self.neutral.shape == (73,) and torch.isfinite(self.neutral).all(), 'finite neutral73')
        self.joint_scale = torch.tensor(self.metadata['joint_position_range_scale30'], device=device, dtype=torch.float32)
        require(self.joint_scale.shape == (30,) and (self.joint_scale > 0).all(), 'positive joint scale30')
        self.leg_ids = [self.names.index(n) for n in self.metadata['actuator_leg_joint_names']]

    def bind_named_order(self, actual_joint_names, *, scope):
        require(scope in ('source_CPU_fixture', 'actual_SDK_readback'), 'explicit mapping scope')
        actual = tuple(actual_joint_names)
        require(len(actual) == 30 and set(actual) == set(self.names), 'actual joint name set differs')
        perm = [self.names.index(n) for n in actual]
        cols = [*range(13), *[13+i for i in perm], *[43+i for i in perm]]
        doc = dict(self.document, joint_names=list(actual), neutral_packed73=self.neutral[cols].cpu().tolist())
        doc['metadata'] = dict(self.metadata, joint_position_range_scale30=self.joint_scale[perm].cpu().tolist())
        return OwnFlatJumpReference(doc, self.device, order_scope=scope)

    def to(self, device):
        return OwnFlatJumpReference(self.document, device, order_scope=self.order_scope)

    def target(self, frames):
        age, delay = decode_frame(frames)
        return self.phase.targets(age, delay)

    def query(self, frames):
        target = self.target(frames)
        value = self.neutral.expand(*frames.shape, 73).clone()
        value[..., :2] = 0  # Stationary own-floor task, not a forward step motion.
        value[..., 2] = self.neutral[2] + target['height']
        value[..., 3:7] = value.new_tensor([1., 0., 0., 0.])
        value[..., 7:13] = 0
        value[..., 9] = target['vertical_v']
        value[..., 43:73] = 0
        mask = torch.zeros_like(value)
        mask[..., :13] = 1
        # Neutral q is a shape witness only; no invented measured jump limb path.
        return value, mask

    def future_goal(self, frames, num_frames):
        require(num_frames >= 1, 'positive goal horizon')
        result = []
        for offset in range(num_frames):
            value, mask = self.query(frames + offset)
            result.append(torch.cat((value * mask, mask), -1))
        return torch.cat(result, -1)

class OwnFlatJumpMdp(ConvertedMOD4JumpMdp):
    def __init__(self, provider, contract, geometry, leg_encoder_joint_names=None):
        super().__init__(provider, leg_encoder_joint_names)
        self.import_contract = contract
        self.authored_geometry = geometry
        self.wheel_geometry = OwnStepWheelGeometry(contract, geometry, provider.names).to(provider.device)

    def to(self, device):
        return OwnFlatJumpMdp(self.provider.to(device), self.import_contract,
                              self.authored_geometry, self.leg_encoder_joint_names)

    def relative_features(self, state, frames):
        target, _ = self.provider.query(frames)
        age, _ = decode_frame(frames)
        shape = frames.shape
        flat = age.reshape(-1)
        # Retain actual authored step distances in the old seven channels. The
        # flat primitive is in goal146; encoding is never mistaken for public age.
        edge = state[0].new_full((flat.numel(),), self.step_edge_x_m)
        top = state[0].new_full((flat.numel(),), self.platform_top_z_m)
        return task_relative_observation(state[0].reshape(-1, 3), target[..., :3].reshape(-1, 3),
                                         edge, top, flat).reshape(*shape, 7)

    def objective_terms(self, state, frames, action, previous_action):
        measured = self.wheel_geometry(state)
        # Dynamic aux54 is predicted/refreshed by the existing native127 WM.
        # This smooth planning signal is not actual floor contact certification.
        force_z = state[6][..., :6].reshape(*frames.shape, 2, 3)[..., 2]
        positive_force = force_z.clamp_min(0)
        support_probability = positive_force / (1 + positive_force)
        target = self.provider.target(frames)
        terms = flat_jump_terms(measured['low'][..., 2], measured['centre_velocity'][..., 2],
                                state[1][..., 2, 2], state[2][..., :2], support_probability,
                                target, action, previous_action)
        # Landing stability needs low angular motion and heading, as well as
        # upright height. Do not reward an upright spinning platform equally.
        ground = target['ground'].to(state[0].dtype)
        from flat_jump_phase_objective_source_v1 import huber
        angular_cost = huber(state[3]/.3).mean(-1)*ground
        yaw = torch.atan2(state[1][...,1,0], state[1][...,0,0])
        heading_cost = huber(yaw/.2)*ground
        cost = terms['nonnegative_cost']+angular_cost+heading_cost
        terms.update(angular_stability_cost=angular_cost,heading_stability_cost=heading_cost,
                     nonnegative_cost=cost,total=.06/(1+cost))
        return terms

    def soft_termination(self, state, frames):
        height_failure = torch.sigmoid((.12-state[0][..., 2])/.02)
        tilt_failure = torch.sigmoid((math.cos(.75)-state[1][..., 2, 2])/.04)
        age, _ = decode_frame(frames)
        timeout = (age >= 500).to(height_failure.dtype)
        return 1-(1-height_failure)*(1-tilt_failure)*(1-timeout)

    def valid_imagination_start(self, frames, horizon):
        age, delay = decode_frame(frames)
        return (frames >= 0) & (delay < 250) & (age + int(horizon) + 10 <= 500)

    def contract_manifest(self):
        return dict(schema='mod4.native_supermimic.own_flat_jump_mdp.v1', physical_joints=30,
                    packed_state=127, dynamic_aux=54, static_xi=31, actor_observation=86,
                    goal_frame=146, future_goal_frames_expected=10, action_dim=6,
                    private_replay_frame='(envID%250)*1024+original_public_age',
                    actual_public_age_reset_and_physics_unchanged=True,
                    reference_order_scope=self.provider.order_scope,
                    reference_metadata=self.provider.metadata,
                    target='both own wheel lowest points5cm then real floor support stable.5s',
                    physical270_success_unchanged=True,
                    dynamic_aux_predicted_each_imagined_step=True,
                    original_native_learner_WM_Pi_Critic_BPTT_unchanged=True,
                    source_candidate_not_installed=True, successful_skill=False)
