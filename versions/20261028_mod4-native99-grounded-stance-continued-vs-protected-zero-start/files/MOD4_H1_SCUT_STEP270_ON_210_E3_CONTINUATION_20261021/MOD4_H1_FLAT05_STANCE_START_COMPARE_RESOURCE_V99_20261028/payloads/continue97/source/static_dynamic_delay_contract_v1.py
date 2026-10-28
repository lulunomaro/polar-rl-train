"""CPU/source candidate. Separate episode parameters from evolving physical state.

No SDK imports, action scaling, CAD projection, force integration or model loading.
The six targets are already processed in original action-term order: four legs,
then two wheels. This is a new model interface, not old actor128 compatibility.
"""
from dataclasses import dataclass
from typing import Mapping
import torch

PHYSICS_US = 2500
CONTROL_US = 10000
SUBSTEPS = 4
DYNAMIC_AUX_FIELDS = (('contact_history', 18), ('applied_torque', 30), ('old_processed_applied', 6))
DYNAMIC_AUX_DIM = 54
TASK_RELATIVE_FIELDS = ('target_dx', 'target_dy', 'target_dz', 'edge_dx', 'platform_top_dz', 'public_request', 'age_s')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_tensor(x, shape, *, name, device=None, dtype=torch.float32):
    require(torch.is_tensor(x), name + ': tensor required')
    require(tuple(x.shape) == tuple(shape), name + ': shape mismatch')
    require(x.dtype == dtype, name + ': dtype mismatch')
    require(device is None or x.device == torch.device(device), name + ': device mismatch')
    require(bool(torch.isfinite(x).all()), name + ': nonfinite')
    return x


def age_tensor(age):
    require(torch.is_tensor(age) and age.ndim == 1 and age.dtype == torch.int64, 'age: int64[N] required')
    require(bool((age >= 0).all()), 'age: negative')
    return age


def request_from_age(age):
    age_tensor(age)
    return (age >= 100) & (age < 180)


def advance_age(age, reset_mask=None):
    """One completed original control, then selected episode reset. No time warp."""
    age_tensor(age)
    require(bool((age < torch.iinfo(torch.int64).max).all()), 'age overflow')
    result = age + 1
    if reset_mask is not None:
        finite_tensor(reset_mask, age.shape, name='reset_mask', device=age.device, dtype=torch.bool)
        result = torch.where(reset_mask, torch.zeros_like(result), result)
    return result


def pack_dynamic_aux(contact_history, applied_torque, old_processed_applied):
    require(torch.is_tensor(contact_history) and contact_history.ndim == 4, 'contact_history: [N,3,2,3] required; no truncation to12')
    n = contact_history.shape[0]
    finite_tensor(contact_history, (n, 3, 2, 3), name='contact_history')
    finite_tensor(applied_torque, (n, 30), name='applied_torque', device=contact_history.device)
    finite_tensor(old_processed_applied, (n, 6), name='old_processed_applied', device=contact_history.device)
    return torch.cat((contact_history.flatten(1), applied_torque, old_processed_applied), -1)


def unpack_dynamic_aux(aux):
    require(torch.is_tensor(aux) and aux.ndim == 2, 'dynamic_aux: [N,54] required')
    finite_tensor(aux, (aux.shape[0], 54), name='dynamic_aux')
    return dict(contact_history=aux[:, :18].reshape(-1, 3, 2, 3), applied_torque=aux[:, 18:48], old_processed_applied=aux[:, 48:54])


def task_relative_observation(root_xyz, target_xyz, edge_x, platform_top_z, age):
    """All positions must share the original task/world frame and length units.

    Spatial translations cancel. Explicit edge distance is visible even when
    proprioception and absolute goal alone would alias different task locations.
    """
    age_tensor(age)
    n = age.numel()
    finite_tensor(root_xyz, (n, 3), name='root_xyz', device=age.device)
    finite_tensor(target_xyz, (n, 3), name='target_xyz', device=age.device)
    finite_tensor(edge_x, (n,), name='edge_x', device=age.device)
    finite_tensor(platform_top_z, (n,), name='platform_top_z', device=age.device)
    return torch.cat((target_xyz-root_xyz, (edge_x-root_xyz[:, 0])[:, None],
                      (platform_top_z-root_xyz[:, 2])[:, None],
                      request_from_age(age).to(root_xyz.dtype)[:, None],
                      (age.to(root_xyz.dtype)*.01)[:, None]), -1)


@dataclass(frozen=True)
class FieldSpec:
    name: str
    shape: tuple
    unit: str
    component: str

    @property
    def width(self):
        result = 1
        for x in self.shape:
            result *= x
        return result


def static_layout(*, body_names, joint_names, material_names, gas_joint_names,
                  motor_group_names=('legs', 'wheels')):
    """Episode parameter catalog; no defaults, sampled ranges or dynamic values.

    Caller must obtain actual installed component values after ALL reset hooks.
    Body/joint/material order is explicit and must be pinned by the next adapter.
    Constant values are permitted; absent components must not get fictitious zeros.
    """
    names = (body_names, joint_names, material_names, gas_joint_names, motor_group_names)
    require(all(len(x) == len(set(x)) and all(isinstance(s, str) and s for s in x) for x in names), 'unique nonempty component names required')
    b, j, m, g, a = map(len, names)
    require(b > 0 and j > 0 and m > 0 and g > 0 and a == 2, 'explicit actual component order required')
    return (
        FieldSpec('material_static_friction', (m,), '1', 'PhysX material'),
        FieldSpec('material_dynamic_friction', (m,), '1', 'PhysX material'),
        FieldSpec('material_restitution', (m,), '1', 'PhysX material'),
        FieldSpec('body_mass', (b,), 'kg', 'rigid body'),
        FieldSpec('body_inertia', (b, 9), 'kg*m2', 'rigid body local tensor'),
        FieldSpec('body_com', (b, 3), 'm', 'rigid body local COM'),
        FieldSpec('joint_armature', (j,), 'kg*m2', 'joint'),
        FieldSpec('joint_friction', (j,), 'Nm', 'joint'),
        FieldSpec('joint_stiffness', (j,), 'original joint units', 'actual PD/spring drive'),
        FieldSpec('joint_damping', (j,), 'original joint units', 'actual PD/spring drive'),
        FieldSpec('motor_episode_scale', (a,), '1', 'Mod4DCMotor.episode_scale; excludes step_scale'),
        FieldSpec('gas_preload_target', (g,), 'm', 'actual gas spring preload'),
        FieldSpec('action_lag_steps', (2,), '2500us ticks', 'original queue legs,wheels'),
        FieldSpec('leg_encoder_episode_bias', (4,), 'rad', 'sensor_mild.bias'),
    )


class EpisodeStaticContext:
    """Own immutable-by-copy episode snapshots; no randomization is performed.

    selected_reset receives full-batch READBACK and rejects even one modified
    nonselected row, including a changed lag. Successful update is atomic.
    """
    def __init__(self, layout, values: Mapping[str, torch.Tensor], episode_ids):
        self.layout = tuple(layout)
        require(len({s.name for s in self.layout}) == len(self.layout), 'duplicate static field')
        allowed = {s.name for s in static_layout(body_names=('b',), joint_names=('j',), material_names=('m',), gas_joint_names=('g',))}
        require({s.name for s in self.layout} <= allowed and self.layout, 'unapproved static field; dynamic state forbidden in xi')
        age_tensor(episode_ids)
        self.n, self.device = len(episode_ids), episode_ids.device
        self._validate(values)
        self._values = {k: v.detach().clone() for k, v in values.items()}
        self._episode_ids = episode_ids.clone()

    def _validate(self, values):
        require(set(values) == {s.name for s in self.layout}, 'static field set mismatch')
        for s in self.layout:
            finite_tensor(values[s.name], (self.n, *s.shape), name=s.name, device=self.device)
        if 'action_lag_steps' in values:
            lag = values['action_lag_steps']
            require(bool(((lag >= 0) & (lag <= 2) & (lag == lag.round())).all()), 'static lag must be integer0/1/2')
        for name in ('body_mass',):
            if name in values:
                require(bool((values[name] > 0).all()), name + ': positive required')
        for name in ('material_static_friction', 'material_dynamic_friction', 'joint_armature', 'joint_friction', 'joint_stiffness', 'joint_damping'):
            if name in values:
                require(bool((values[name] >= 0).all()), name + ': negative')
        if 'material_restitution' in values:
            require(bool(((values['material_restitution'] >= 0) & (values['material_restitution'] <= 1)).all()), 'invalid restitution')

    def snapshot(self):
        return {k: v.clone() for k, v in self._values.items()}

    def xi(self):
        return torch.cat([self._values[s.name].flatten(1) for s in self.layout], -1)

    def selected_reset(self, ids, new_values, new_episode_ids):
        require(torch.is_tensor(ids) and ids.dtype == torch.int64 and ids.ndim == 1 and ids.device == self.device, 'reset ids int64 same device')
        require(len(ids.unique()) == len(ids) and bool(((ids >= 0) & (ids < self.n)).all()), 'invalid reset ids')
        self._validate(new_values)
        age_tensor(new_episode_ids)
        require(new_episode_ids.shape == self._episode_ids.shape and new_episode_ids.device == self.device, 'episode shape/device mismatch')
        selected = torch.zeros(self.n, dtype=torch.bool, device=self.device)
        selected[ids] = True
        require(torch.equal(new_episode_ids, self._episode_ids + selected.to(torch.int64)), 'episode must increment selected once only')
        for key in self._values:
            require(torch.equal(new_values[key][~selected], self._values[key][~selected]), 'nonreset xi changed: ' + key)
        self._values = {k: v.detach().clone() for k, v in new_values.items()}
        self._episode_ids = new_episode_ids.clone()
        return dict(selected_rows=len(ids), nonreset_xi_exact=True)

    def assert_unchanged(self, readback):
        self._validate(readback)
        require(all(torch.equal(readback[k], self._values[k]) for k in readback), 'episode static component changed mid-episode')
        return True


def read_actual_episode_parameters(env):
    """Fail closed until reviewed installed SDK/component getter mapping exists."""
    raise NotImplementedError('Actual SDK DR mapping/readback and reset-order admission pending; CPU fixtures are not admission')


@dataclass(frozen=True)
class QueueControlResult:
    applied_substeps: torch.Tensor  # N,4,6, before each integration substep
    next_old_applied: torch.Tensor  # N,6 at next control boundary
    first_transition_tick: torch.Tensor  # N,2
    next_last_apply_tick: int


def unroll_processed_target_control(processed_targets, old_applied, lag_steps, *,
                                    issue_tick=0, last_apply_tick=-1,
                                    pending_valid=None, physics_us=PHYSICS_US,
                                    control_us=CONTROL_US):
    """Exact original queue projection at a clean policy-decision boundary.

    Original queue stays deployed; this differentiable expression is for the new
    modeled state/action path. Reject a mid-control/pending boundary rather than
    discard state. Lag is episode-static and discrete, gradients concern targets.
    """
    require(torch.is_tensor(processed_targets) and processed_targets.ndim == 2, 'processed targets required')
    n = len(processed_targets)
    finite_tensor(processed_targets, (n, 6), name='processed_targets')
    finite_tensor(old_applied, (n, 6), name='old_applied', device=processed_targets.device)
    finite_tensor(lag_steps, (n, 2), name='lag_steps', device=processed_targets.device, dtype=torch.int64)
    require(bool(((lag_steps >= 0) & (lag_steps <= 2)).all()), 'lag outside0/1/2')
    require(physics_us == 2500 and control_us == 10000, 'original physical clock required')
    require(isinstance(issue_tick, int) and not isinstance(issue_tick, bool) and issue_tick >= 0 and issue_tick % 4 == 0, 'clean control issue tick required')
    require(isinstance(last_apply_tick, int) and not isinstance(last_apply_tick, bool) and last_apply_tick == issue_tick-1, 'continuous original apply clock required')
    if pending_valid is not None:
        finite_tensor(pending_valid, (n, 2), name='pending_valid', device=processed_targets.device, dtype=torch.bool)
        require(not bool(pending_valid.any()), 'pending command cannot be dropped')
    lag6 = torch.cat((lag_steps[:, :1].expand(-1, 4), lag_steps[:, 1:].expand(-1, 2)), -1)
    substep = torch.arange(4, device=processed_targets.device)[None, :, None]
    result = torch.where(substep >= lag6[:, None, :], processed_targets[:, None, :], old_applied[:, None, :])
    return QueueControlResult(result, result[:, -1, :], issue_tick + lag_steps, issue_tick+3)


def reset_old_applied(old_applied, ids, neutral):
    """Selected original default leg q / zero wheel targets; other rows survive."""
    finite_tensor(old_applied, (len(old_applied), 6), name='old_applied')
    finite_tensor(neutral, old_applied.shape, name='neutral', device=old_applied.device)
    require(torch.is_tensor(ids) and ids.dtype == torch.int64 and ids.device == old_applied.device and ids.ndim == 1, 'reset ids required')
    require(len(ids.unique()) == len(ids) and bool(((ids >= 0) & (ids < len(old_applied))).all()), 'invalid reset ids')
    selected = torch.zeros(len(old_applied), dtype=torch.bool, device=old_applied.device)
    selected[ids] = True
    return torch.where(selected[:, None], neutral, old_applied)
