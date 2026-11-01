"""A frozen current observed-support belief, not a future camera or GT terrain.

Raw context40 = raw static31 + raw9. No normalization occurs in this module.
Native poses use env-local WORLD axes and wxyz, as the pinned255/268 geometry.
"""
from dataclasses import dataclass
import torch

FEATURES = ('edge_distance_m', 'step_height_m', 'lateral_center_m', 'target_yaw_rad',
            'visible_width_m', 'visible_depth_m', 'confidence', 'depth_age_seconds', 'valid')
SCHEMA = 'OBSERVED_STATIC_SUPPORT_ANCHOR_RAW_CONTEXT40_V271'
FRAME = 'gravity_level_heading_rootWORLD_XY_zWORLD0'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def field(value, shape, name, *, reference=None, dtype=torch.float32):
    require(torch.is_tensor(value) and tuple(value.shape) == tuple(shape), name + ': explicit tensor shape required')
    require(value.dtype == dtype, name + ': wrong dtype')
    require(reference is None or value.device == reference.device, name + ': wrong device')
    require(bool(torch.isfinite(value).all()), name + ': nonfinite')
    return value


@dataclass(frozen=True)
class Producer271:
    kind: str
    plant: str
    run_id: str
    generation: str | int
    source_admission_SHA: str
    sensor_id: str
    environment_ids: tuple
    episode_ids: tuple

    def validate(self, n, *, synthetic_CPU_test=False):
        expected = 'SYNTHETIC_CPU_CURRENT_DEPTH263_PACKET_ONLY' if synthetic_CPU_test else 'ACTUAL_OWN_MOD4_CURRENT_DEPTH263_PACKET'
        require(self.kind == expected and self.plant == 'own_MOD4_live_USD', 'Actual own-plant current-depth producer required')
        require(all(isinstance(v, str) and v for v in (self.run_id, self.sensor_id)), 'Missing run/sensor identity')
        require((type(self.generation) is str and bool(self.generation))
                or (type(self.generation) is int and self.generation > 0), 'Missing generation identity')
        require(self.sensor_id == 'D435i_front_fixed', 'Wrong sensor source')
        require(isinstance(self.source_admission_SHA, str) and len(self.source_admission_SHA) == 64
                and all(c in '0123456789abcdef' for c in self.source_admission_SHA), 'Missing admitted source SHA')
        require(type(self.environment_ids) is tuple and len(self.environment_ids) == n
                and len(set(self.environment_ids)) == n
                and all(type(i) is int and i >= 0 for i in self.environment_ids), 'Ordered actual environment IDs required')
        require(type(self.episode_ids) is tuple and len(self.episode_ids) == n
                and all(type(i) is int and i >= 0 for i in self.episode_ids), 'Actual per-env episode IDs required')
        return self


@dataclass(frozen=True)
class CurrentDepthPacket271:
    producer: Producer271
    packet_id: str
    found: torch.Tensor
    feature9: torch.Tensor
    visible_floor_z_m: torch.Tensor
    sensor_time_s: torch.Tensor
    control_time_s: torch.Tensor
    sensor_pose_time_s: torch.Tensor
    sensor_pose_native13: torch.Tensor
    environment_origins_world: torch.Tensor
    T_world_heading: torch.Tensor
    frame_definition: str
    pose_quaternion_order: str


@dataclass(frozen=True)
class ObservedStaticSupport271:
    """Detached clones isolate the anchor from later sensor buffers.

    The private values are an immutable-by-contract belief; callers receive
    cloned corner metadata. They may not mutate this object as future depth.
    """
    producer: Producer271
    packet_id: str
    _corners_world: torch.Tensor
    _floor_world_z: torch.Tensor
    _step_height: torch.Tensor
    _confidence: torch.Tensor
    _initial_age: torch.Tensor
    _sensor_time: torch.Tensor
    _anchor_control_time: torch.Tensor
    _environment_origins_world: torch.Tensor
    _static31_raw: torch.Tensor
    synthetic_CPU_test: bool

    def context40(self, predicted_native_state, *, producer, imagination_step, geometry):
        """Only a predicted native state enters after static31/depth anchoring.

        No future-depth argument or sequence is accepted. Step0..32 is the
        original50Hz H32 span. The belief age is elapsed since the real packet,
        not a claimed future-camera freshness test or a new image timestamp.
        """
        n = self._corners_world.shape[0]
        require(type(producer) is Producer271 and producer == self.producer,
                'Anchor cannot cross run/generation/source/sensor/environment/episode scope')
        producer.validate(n, synthetic_CPU_test=self.synthetic_CPU_test)
        require(type(imagination_step) is int and 0 <= imagination_step <= 32,
                'Original bounded H32 prediction step0..32 required')
        require(isinstance(predicted_native_state, tuple) and len(predicted_native_state) == 7,
                'Explicit native224 state tuple required')
        p, R, v, w, q, dq, aux = predicted_native_state
        field(p, (n, 3), 'predicted native position')
        for value, shape, name in ((R, (n, 3, 3), 'predicted native rotation'),
                (v, (n, 3), 'predicted WORLD velocity'), (w, (n, 3), 'predicted WORLD angular velocity'),
                (q, (n, 30), 'predicted q30'), (dq, (n, 30), 'predicted dq30'),
                (aux, (n, 151), 'predicted aux151')):
            field(value, shape, name, reference=p)
        require(p.device == self._corners_world.device, 'Anchor/prediction device differs')
        heading_world = geometry.yaw_mat(R)
        root_world = p + self._environment_origins_world
        # Same source263 heading origin: WORLD(root.x,root.y,0), gravity level.
        origin = torch.cat((root_world[:, :2], torch.zeros_like(root_world[:, 2:3])), -1)
        corners_heading = torch.einsum('nji,nkj->nki', heading_world, self._corners_world - origin[:, None])
        x, y = corners_heading[..., 0], corners_heading[..., 1]
        near, far = x.amin(-1), x.amax(-1)
        left, right = y.amin(-1), y.amax(-1)
        lateral = (left + right) * .5
        # A bearing exactly at the heading origin is undefined. Report its mask
        # and supply a finite neutral summary, not a fictitious direction.
        bearing_defined = near.square() + lateral.square() > 1e-12
        yaw = torch.atan2(torch.where(bearing_defined, lateral, torch.zeros_like(lateral)),
                          torch.where(bearing_defined, near, torch.ones_like(near)))
        age = self._initial_age + imagination_step * .02
        raw9 = torch.stack((near, self._step_height, lateral, yaw, right-left,
                            far-near, self._confidence, age, torch.ones_like(age)), -1)
        field(raw9, (n, 9), 'raw belief9', reference=p)
        context = torch.cat((self._static31_raw, raw9), -1)
        return dict(context40_raw=context, raw9=raw9,
            support_corners_world=self._corners_world.clone(), support_corners_predicted_heading=corners_heading,
            visible_floor_world_z_m=self._floor_world_z.clone(),
            belief_age_seconds=age, target_bearing_defined=bearing_defined,
            metadata=dict(schema=SCHEMA, packet_id=self.packet_id, imagination_step=imagination_step,
                policy_us=20000, static_terrain_assumption=True, current_or_future_camera=False,
                sensor_frame_time_fixed=True, source='one current263 observed support packet',
                observed_range_lower_bound_only=True, complete_footprint_certified=False,
                feature0_semantics='near boundary of fixed observed belief projected into predicted heading; not real platform front edge',
                width_depth_semantics='axis projection spans of observed corners; AABB interior not certified observed/supportable',
                valid_semantics='fixed observed belief exists; not current camera visibility/freshness',
                confidence_semantics='original observation confidence held; no new visibility/occlusion claim',
                height_semantics='original observed floor-relative support height, unchanged by root height',
                normalization='NONE; existing normalize_context40 once only'))


def make_anchor(packet, *, static31_raw, geometry, synthetic_CPU_test=False):
    """Accept one actual current packet; no floor0/map/pose/producer default."""
    require(type(packet) is CurrentDepthPacket271, 'One typed current packet required, never a future-depth sequence')
    require(torch.is_tensor(packet.feature9) and packet.feature9.ndim == 2, 'One current feature9 batch required')
    n = packet.feature9.shape[0]
    require(n > 0, 'Nonempty current observation batch required')
    require(type(packet.producer) is Producer271, 'Explicit actual producer identity required')
    packet.producer.validate(n, synthetic_CPU_test=synthetic_CPU_test)
    require(isinstance(packet.packet_id, str) and packet.packet_id, 'Actual packet ID required')
    require(packet.frame_definition == FRAME and packet.pose_quaternion_order == 'native_wxyz',
            'Explicit source263 heading frame and native pose convention required')
    f = field(packet.feature9, (n, 9), 'current raw feature9')
    field(static31_raw, (n, 31), 'current raw episode static31', reference=f)
    field(packet.found, (n,), 'current found mask', reference=f, dtype=torch.bool)
    require(bool(packet.found.all()) and bool((f[:, 8] == 1).all()), 'No supported current visible surface to anchor')
    for value, shape, name in ((packet.visible_floor_z_m, (n,), 'measured visible_floor_z_m'),
            (packet.sensor_time_s, (n,), 'actual sensor time'), (packet.control_time_s, (n,), 'actual control time'),
            (packet.sensor_pose_time_s, (n,), 'corresponding sensor pose time'),
            (packet.sensor_pose_native13, (n, 13), 'corresponding actual native pose13'),
            (packet.environment_origins_world, (n, 3), 'actual environment origins'),
            (packet.T_world_heading, (n, 4, 4), 'actual heading-to-WORLD transform')):
        field(value, shape, name, reference=f)
    age = packet.control_time_s - packet.sensor_time_s
    require(bool(((age >= 0) & (age <= .20)).all()), 'Future or stale ACTUAL depth at anchor admission')
    require(torch.allclose(f[:, 7], age, rtol=0., atol=1e-6), 'Feature/time age differs')
    require(torch.allclose(packet.sensor_pose_time_s, packet.sensor_time_s, rtol=0., atol=1e-6),
            'Pose does not correspond to this sensor frame')
    require(bool((f[:, 0] > 0).all() & (f[:, 1] > 0).all() & (f[:, 4:6] > 0).all()
                 & ((f[:, 6] >= 0) & (f[:, 6] <= 1)).all()), 'Invalid raw observed support dimensions/confidence')
    require(torch.allclose(f[:, 3], torch.atan2(f[:, 2], f[:, 0]), rtol=0., atol=1e-5),
            'Raw263 target bearing differs from observed near/lateral summary')
    root = packet.sensor_pose_native13
    require(bool((root[:, 3:7].square().sum(-1) > 0).all()), 'Missing actual native quaternion')
    heading = geometry.yaw_mat(geometry.quat_to_mat(root[:, 3:7]))
    world = root[:, :3] + packet.environment_origins_world
    expected_origin = torch.cat((world[:, :2], torch.zeros_like(world[:, 2:3])), -1)
    T = packet.T_world_heading
    require(torch.allclose(T[:, :3, :3], heading, rtol=0., atol=1e-5)
            and torch.allclose(T[:, :3, 3], expected_origin, rtol=0., atol=1e-5)
            and torch.allclose(T[:, 3, :], f.new_tensor([0., 0., 0., 1.]).expand(n, -1), rtol=0., atol=1e-6),
            'Heading transform does not match actual pose/env origins/source263 frame')
    near, far = f[:, 0], f[:, 0] + f[:, 5]
    low, high = f[:, 2] - f[:, 4] * .5, f[:, 2] + f[:, 4] * .5
    top = packet.visible_floor_z_m + f[:, 1]
    corners = torch.stack((torch.stack((near, low, top), -1), torch.stack((near, high, top), -1),
                           torch.stack((far, high, top), -1), torch.stack((far, low, top), -1)), 1)
    corners_world = torch.einsum('nij,nkj->nki', T[:, :3, :3], corners) + T[:, None, :3, 3]
    floor_world = packet.visible_floor_z_m + T[:, 2, 3]
    freeze = lambda x: x.detach().clone()
    return ObservedStaticSupport271(packet.producer, packet.packet_id, freeze(corners_world),
        freeze(floor_world), freeze(f[:, 1]), freeze(f[:, 6]), freeze(age),
        freeze(packet.sensor_time_s), freeze(packet.control_time_s),
        freeze(packet.environment_origins_world), freeze(static31_raw), synthetic_CPU_test)
