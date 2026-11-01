"""Explicit own-plant measured state. No SDK, simulation, checkpoint or fallback.

The original physical73/aux54 prefix is byte-for-byte tensor compatible with
255. Only contact forces in the NEW suffix are scaled, by a fixed400 N.
"""
from dataclasses import dataclass
import torch

SCHEMA_ID = 'OWN_MOD4_PHYSICAL73_AUX151_MEASURED224_V268'
MEASUREMENT_KIND = 'OWN_MOD4_MEASURED224_CONTROL_ENDPOINT_V268'
FORCE_SCALE_N = 400.0
MOTOR_NAMES_REWARD_ORDER = (
    'left_crank', 'left_hip', 'left_wheel_spin',
    'right_crank', 'right_hip', 'right_wheel_spin',
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def tensor_field(value, shape, *, name, reference=None):
    require(torch.is_tensor(value), name + ': measured tensor required')
    require(tuple(value.shape) == tuple(shape), name + ': wrong explicit shape')
    require(value.dtype == torch.float32, name + ': float32 required')
    if reference is not None:
        require(value.device == reference.device, name + ': device differs')
    require(bool(torch.isfinite(value).all()), name + ': nonfinite')
    return value


@dataclass(frozen=True)
class MeasurementBinding268:
    """Numeric motor IDs MUST be provided by the actual measured robot binding.

    No fixed numeric IDs or fabricated six efforts are supplied by this module.
    A synthetic witness is allowed only in a caller-labelled synthetic CPU case.
    """
    joint_names: tuple
    body_names: tuple
    motor_ids_reward_order: tuple
    witness_kind: str
    witness_SHA: str

    def validate(self, *, synthetic_CPU_test=False):
        require(len(self.joint_names) == len(set(self.joint_names)) == 30,
                'Actual ordered30 joint names required')
        require(len(self.body_names) == len(set(self.body_names)) == 31,
                'Actual ordered31 body names required')
        require(all(n in self.body_names for n in ('chassis', 'left_wheel', 'right_wheel')),
                'Own MOD4 named bodies required')
        require(len(self.motor_ids_reward_order) == 6 and
                all(type(i) is int and 0 <= i < 30 for i in self.motor_ids_reward_order),
                'Measured six motor IDs required')
        require(tuple(self.joint_names[i] for i in self.motor_ids_reward_order)
                == MOTOR_NAMES_REWARD_ORDER, 'Motor IDs do not match original reward order')
        kind = 'SYNTHETIC_CPU_BINDING_ONLY' if synthetic_CPU_test else 'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING'
        require(self.witness_kind == kind and isinstance(self.witness_SHA, str)
                and len(self.witness_SHA) == 64 and
                all(c in '0123456789abcdef' for c in self.witness_SHA),
                'Explicit actual/synthetic binding provenance required')
        return self

    def metadata(self):
        return dict(joint_names=list(self.joint_names), body_names=list(self.body_names),
                    motor_ids_reward_order=list(self.motor_ids_reward_order),
                    motor_names_reward_order=list(MOTOR_NAMES_REWARD_ORDER),
                    witness_kind=self.witness_kind, witness_SHA=self.witness_SHA)


class MeasuredStateLayout268:
    """Native state tuple and native SE3 representation; explicit224 pack/unpack."""
    num_joints = 30
    auxiliary_dim = 151
    packed_dim = 224

    def __init__(self, native_geometry, native_world):
        self.geometry = native_geometry
        self.native = native_world.WheelLegStateLayout(30, 151)

    def validate(self, state):
        self.native.validate(state)
        for i, value in enumerate(state):
            require(value.dtype == torch.float32 and bool(torch.isfinite(value).all()),
                    'Nonfinite/non-float32 native224 component ' + str(i))

    def unpack(self, value):
        require(torch.is_tensor(value) and value.ndim >= 2,
                'Explicit batched measured224 tensor required')
        require(value.shape[-1] == 224, 'Old127/partial state cannot stand for measured224')
        tensor_field(value, value.shape, name='measured224')
        require(bool((value[..., 3:7].square().sum(-1) > 0).all()), 'Missing quaternion')
        state = self.native.unpack(value)
        self.validate(state)
        return state

    unflatten_state = unpack

    def pack(self, state):
        self.validate(state)
        return self.native.pack(state)


def pack_measured224(base127, *, L0, theta0, contact_forces_world,
                     layout, binding, measurement, synthetic_CPU_test=False):
    """One same-endpoint measured sample; no FK guess, zero pad or held label.

    base127 uses native env-origin-local position, wxyz/world-v/world-w format.
    Source SDK xyzw
    must be converted by the admitted producer, not relabelled. Contact input is
    actual WORLD net_forces_w reordered into robot.body_names. R^T F/400 is
    stored in the NEW suffix. The original contact_history18 remains unchanged.
    """
    binding.validate(synthetic_CPU_test=synthetic_CPU_test)
    require(torch.is_tensor(base127) and base127.ndim == 2, 'Measured base127 required')
    n = base127.shape[0]
    tensor_field(base127, (n, 127), name='base127')
    require(bool((base127[:, 3:7].square().sum(-1) > 0).all()), 'Missing base quaternion')
    tensor_field(L0, (n, 2), name='own L0', reference=base127)
    tensor_field(theta0, (n, 2), name='own theta0', reference=base127)
    tensor_field(contact_forces_world, (n, 31, 3), name='ordered31 WORLD forces', reference=base127)
    expected = dict(kind=MEASUREMENT_KIND, state_schema=SCHEMA_ID,
                    packed_quaternion='wxyz', contact_input_frame='WORLD',
                    contact_body_order=list(binding.body_names),
                    virtual_leg_source='own_virtual_legs_MOD4_hip_anchor_to_wheel_origin_v2',
                    binding_witness_SHA=binding.witness_SHA)
    require(isinstance(measurement, dict) and all(measurement.get(k) == v for k, v in expected.items()),
            'Missing or incompatible same-endpoint measurement schema/binding')
    require(type(measurement.get('physics_end_tick')) is int
            and measurement['physics_end_tick'] >= 0
            and measurement['physics_end_tick'] % 8 == 0,
            'Measurement must name its original50Hz endpoint tick')
    R = layout.geometry.quat_to_mat(base127[:, 3:7])
    body_force = torch.einsum('nji,nkj->nki', R, contact_forces_world) / FORCE_SCALE_N
    out = torch.cat((base127, L0, theta0, body_force.flatten(1)), -1)
    layout.unpack(out)
    return out


def schema_metadata():
    return dict(schema_ID=SCHEMA_ID, state_dim=224, physical_dim=73, auxiliary_dim=151,
        native_quaternion_order='wxyz', SDK_ingress_quaternion='xyzw must explicitly convert once',
        fields=[
            dict(name='position_env_origin_local_world_axes', start=0, stop=3, unit='m'),
            dict(name='quaternion_wxyz', start=3, stop=7, unit='unit quaternion'),
            dict(name='linear_velocity_world', start=7, stop=10, unit='m/s'),
            dict(name='angular_velocity_world', start=10, stop=13, unit='rad/s'),
            dict(name='q30', start=13, stop=43, unit='original joint units'),
            dict(name='dq30', start=43, stop=73, unit='original joint units/s'),
            dict(name='original_contact_history18', start=73, stop=91, aux_start=0, aux_stop=18,
                 unit='unchanged original base127 history units/order; not the new force suffix'),
            dict(name='applied_torque30', start=91, stop=121, aux_start=18, aux_stop=48, unit='N m, SDK applied effort'),
            dict(name='old_processed_applied6', start=121, stop=127, aux_start=48, aux_stop=54, unit='original processed action units'),
            dict(name='own_L0_left_right', start=127, stop=129, aux_start=54, aux_stop=56, unit='m'),
            dict(name='own_theta0_left_right', start=129, stop=131, aux_start=56, aux_stop=58, unit='rad, original atan2-minus-pi/2 branch'),
            dict(name='contact_forces_BODY_31x3', start=131, stop=224, aux_start=58, aux_stop=151,
                 unit='actual N / fixed400N', flatten_order='robot.body_names then xyz')],
        added97='own L0/theta4 + BODY31x3 forces93', force_scale_N=FORCE_SCALE_N,
        applied_efforts='applied_torque30[:, measured motor IDs in original reward order]; no new six labels',
        measurements_missing='reject; never zero-pad/hold/derive fake contact',
        context40='unchanged static31 + depth9; dynamic measurements are not context',
        known_environment_origin='add actual static env_origins back only when reconstructing original WORLD root frame')
