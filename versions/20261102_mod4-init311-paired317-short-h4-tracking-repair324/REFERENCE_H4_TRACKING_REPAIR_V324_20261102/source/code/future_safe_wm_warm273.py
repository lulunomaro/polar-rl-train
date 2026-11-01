"""WM-only native224 H32 supervision with one observed anchor per start.

Teacher Pi/Critic/STD/17Adam are not owned, loaded or optimized here. No SDK,
checkpoint loader, GT map or future-depth fallback exists in this module.
"""
from dataclasses import dataclass, replace
import torch
from native_measured_depth_world_model50_v268 import MeasuredDepthTeacherWM50
from native_depth_world_model50_v255 import normalize_context40
from measured_state224_v268 import SCHEMA_ID, tensor_field, require
from observed_support_context271 import CurrentDepthPacket271, Producer271, FRAME, make_anchor


@dataclass(frozen=True)
class FrozenTeacherContract273:
    checkpoint_SHA: str
    whole_fullstate_receipt_SHA: str
    actor35_critic38_STD6_full17Adam_verified: bool

    def validate(self):
        for value in (self.checkpoint_SHA, self.whole_fullstate_receipt_SHA):
            require(isinstance(value, str) and len(value) == 64 and
                    all(c in '0123456789abcdef' for c in value), 'Pinned qualified teacher metadata required')
        require(self.actor35_critic38_STD6_full17Adam_verified is True, 'Complete frozen teacher contract required')


class AnchorReplay273:
    """Parallel64-row packet storage; UNKNOWN floor/corners are NaN, never zero.

    Raw current packet fields, scope and eligibility are retained even if a
    physical transition lacks a supported anchor. Only eligible starts sample.
    """
    def __init__(self, T, N, device):
        self.N = N
        tails = dict(feature9=(9,), visible_floor_z_m=(), sensor_time_s=(), control_time_s=(),
            sensor_pose_time_s=(), sensor_pose_native13=(13,), environment_origins_world=(3,),
            T_world_heading=(4, 4), static31_raw=(31,), corners_world=(4, 3),
            floor_world_z=(), step_height=(), confidence=(), initial_age=())
        self.data = {k: torch.full((T, N, *shape), float('nan'), device=device) for k, shape in tails.items()}
        self.data['found'] = torch.zeros(T, N, dtype=torch.bool, device=device)
        self.data['valid_anchor'] = torch.zeros(T, N, dtype=torch.bool, device=device)
        self.data['start_physics_tick'] = torch.full((T, N), -1, dtype=torch.int64, device=device)
        self.scopes = [None] * T

    def write(self, slot, values, packet):
        for name, value in values.items():
            self.data[name][slot].copy_(value)
        # True identities remain true, including repeated envs at different times.
        self.scopes[slot] = (packet.producer, packet.packet_id)

    def gather(self, slots, envs):
        out = {k: v[slots, envs].detach().clone() for k, v in self.data.items()}
        pairs = zip(slots.detach().cpu().tolist(), envs.detach().cpu().tolist())
        records = []
        for slot, env in pairs:
            p, packet_id = self.scopes[slot]
            records.append(dict(kind=p.kind, plant=p.plant, run_id=p.run_id, generation=p.generation,
                source_admission_SHA=p.source_admission_SHA, sensor_id=p.sensor_id,
                environment_id=p.environment_ids[env], episode_id=p.episode_ids[env],
                packet_id=packet_id, slot=slot))
        out['scope_records'] = tuple(records)
        require(bool(out['valid_anchor'].all()), 'Only supported admitted first anchors may sample')
        return out


def context_from_start_anchor273(anchor, state, step, geometry):
    """Vectorized271 projection semantics for gathered heterogeneous real starts.

    Admission and unique live environment IDs were checked at ingress. Sampling
    with replacement legitimately repeats env/time pairs. scope_records preserves
    those identities; no fake unique IDs are supplied to271.make_anchor.
    """
    require(type(step) is int and 0 <= step <= 32, 'Original H32 span required')
    p, R = state[:2]
    require(bool(anchor['valid_anchor'].all()) and len(anchor['scope_records']) == p.shape[0],
            'Missing admitted sampled scope')
    heading = geometry.yaw_mat(R)
    world = p + anchor['environment_origins_world']
    origin = torch.cat((world[:, :2], torch.zeros_like(world[:, 2:3])), -1)
    corners = torch.einsum('nji,nkj->nki', heading, anchor['corners_world'] - origin[:, None])
    x, y = corners[..., 0], corners[..., 1]
    near, far = x.amin(-1), x.amax(-1)
    lo, hi = y.amin(-1), y.amax(-1)
    lateral = (lo + hi) * .5
    bearing_defined = near.square() + lateral.square() > 1e-12
    yaw = torch.atan2(torch.where(bearing_defined, lateral, torch.zeros_like(lateral)),
                      torch.where(bearing_defined, near, torch.ones_like(near)))
    age = anchor['initial_age'] + step * .02
    raw9 = torch.stack((near, anchor['step_height'], lateral, yaw, hi-lo, far-near,
                        anchor['confidence'], age, torch.ones_like(age)), -1)
    return torch.cat((anchor['static31_raw'], raw9), -1)


class FutureSafeWarmWM273(MeasuredDepthTeacherWM50):
    def __init__(self, source, device, *, teacher_contract, **kwargs):
        teacher_contract.validate()
        super().__init__(source, device, **kwargs)
        self.teacher_contract = teacher_contract
        self.anchors = AnchorReplay273(64, self.envs, self.device)
        self.native_geometry = self.measured_layout.geometry
        self._live_scope = None
        self.protocol.update(kind='OWN_MEASURED224_FIRST_OBSERVED_ANCHOR_ONLY_H32_WM_WARM_V273',
            context40_time_semantics='Each sampled start has one real current packet; all H32 context uses that fixed anchor + predicted state only',
            WM_supervised_future_depth_input=False, WM_start_anchor_context_source_ready=True,
            policy_imagination_context_ready=False, policy_BPTT_updates=0,
            teacher_actor_critic_STD_17Adam_frozen_external_contract=teacher_contract.__dict__,
            optimizer_scope='one NEW WM Adam; no teacher/Pi/Critic optimizer access',
            complete_three_optimizer_conversion=False, replay_anchor_missing='explicit UNKNOWN/NaN, not eligible start',
            supported_start_sampling='uniform with replacement over valid(start,env) within original64/H32 replay',
            policy_imagination_context_pending='Actual current-packet admission and real Pi/Critic integration remain outside WM-only warm stage')

    def _anchor_values(self, packet, fields, start_tick):
        require(type(packet) is CurrentDepthPacket271 and type(packet.producer) is Producer271,
                'Complete typed current packet required')
        packet.producer.validate(self.envs, synthetic_CPU_test=self.synthetic_CPU_test)
        require(packet.frame_definition == FRAME and packet.pose_quaternion_order == 'native_wxyz', 'Wrong packet frame/pose convention')
        require(isinstance(packet.packet_id, str) and packet.packet_id, 'Actual packet ID required')
        n = self.envs
        f = tensor_field(packet.feature9, (n, 9), name='current feature9', reference=fields['s'])
        require(torch.is_tensor(packet.visible_floor_z_m) and packet.visible_floor_z_m.shape == (n,)
            and packet.visible_floor_z_m.dtype == torch.float32 and packet.visible_floor_z_m.device == self.device,
            'Explicit measured floor column required; unsupported rows use UNKNOWN NaN')
        require(torch.is_tensor(packet.found) and packet.found.shape == (n,)
                and packet.found.dtype == torch.bool and packet.found.device == self.device, 'Actual found mask required')
        for name, shape in (('sensor_time_s', (n,)), ('control_time_s', (n,)), ('sensor_pose_time_s', (n,)),
                ('sensor_pose_native13', (n, 13)), ('environment_origins_world', (n, 3)), ('T_world_heading', (n, 4, 4))):
            tensor_field(getattr(packet, name), shape, name=name, reference=fields['s'])
        age = packet.control_time_s - packet.sensor_time_s
        require(bool((age >= 0).all()), 'Future real packet forbidden')
        require(torch.allclose(f[:, 7], age, atol=1e-6, rtol=0.), 'Packet depth clock differs')
        require(torch.allclose(packet.sensor_time_s, packet.sensor_pose_time_s, atol=1e-6, rtol=0.), 'Sensor pose timestamp differs')
        require(torch.equal(packet.found, f[:, 8] == 1) and bool(((f[:, 8] == 0) | (f[:, 8] == 1)).all()), 'found/valid mask mismatch')
        require(bool(torch.isfinite(packet.visible_floor_z_m[packet.found]).all()), 'Found support is missing measured floor')
        require(bool(torch.isnan(packet.visible_floor_z_m[~packet.found]).all()), 'Unsupported floor must be UNKNOWN NaN, not filled0/held truth')
        require(torch.equal(f, fields['xi'][:, 31:]), 'Transition must record this current raw packet feature9')
        live_scope = (packet.producer.kind, packet.producer.plant, packet.producer.run_id, packet.producer.generation,
            packet.producer.source_admission_SHA, packet.producer.sensor_id, packet.producer.environment_ids)
        require(self._live_scope is None or live_scope == self._live_scope, 'Run/generation/source/env order changed within replay')
        valid = packet.found & (age <= .20)
        values = {k: getattr(packet, k).detach().clone() for k in (
            'feature9', 'visible_floor_z_m', 'sensor_time_s', 'control_time_s', 'sensor_pose_time_s',
            'sensor_pose_native13', 'environment_origins_world', 'T_world_heading', 'found')}
        values.update(static31_raw=fields['xi'][:, :31].detach().clone(), valid_anchor=valid,
            start_physics_tick=torch.full((n,), start_tick, device=self.device, dtype=torch.int64))
        for key, tail in (('corners_world', (4, 3)), ('floor_world_z', ()), ('step_height', ()),
                          ('confidence', ()), ('initial_age', ())):
            values[key] = torch.full((n, *tail), float('nan'), device=self.device)
        ids = valid.nonzero(as_tuple=False).flatten()
        if ids.numel():
            indices = ids.detach().cpu().tolist()
            p = replace(packet.producer, environment_ids=tuple(packet.producer.environment_ids[i] for i in indices),
                        episode_ids=tuple(packet.producer.episode_ids[i] for i in indices))
            sub = replace(packet, producer=p, **{k: getattr(packet, k)[ids] for k in (
                'found', 'feature9', 'visible_floor_z_m', 'sensor_time_s', 'control_time_s',
                'sensor_pose_time_s', 'sensor_pose_native13', 'environment_origins_world', 'T_world_heading')})
            anchor = make_anchor(sub, static31_raw=values['static31_raw'][ids], geometry=self.native_geometry,
                                 synthetic_CPU_test=self.synthetic_CPU_test)
            for key, source in (('corners_world', '_corners_world'), ('floor_world_z', '_floor_world_z'),
                    ('step_height', '_step_height'), ('confidence', '_confidence'), ('initial_age', '_initial_age')):
                values[key][ids] = getattr(anchor, source)
        return values, live_scope

    def add(self, transition, *, actual_anchor, physics_end_tick, physics_us, feedback_samples,
            producer, synthetic_CPU_test=False):
        require(synthetic_CPU_test == self.synthetic_CPU_test, 'Actual/synthetic mode changed')
        self.binding.validate(synthetic_CPU_test=synthetic_CPU_test)
        expected = 'SYNTHETIC_CPU_INTERFACE_ONLY' if synthetic_CPU_test else 'ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER'
        require(producer.get('kind') == expected and producer.get('plant') == 'own_MOD4_live_USD', 'Actual own measured producer required')
        require(producer.get('state_schema') == SCHEMA_ID and producer.get('binding_witness_SHA') == self.binding.witness_SHA
            and producer.get('measured_fields') == ['own_L0_theta4', 'contact_forces_BODY31x3'], 'Explicit measured224 provenance required')
        require(type(physics_end_tick) is int and physics_end_tick >= 8 and physics_end_tick % 8 == 0
            and physics_us == 2500 and feedback_samples == 2, 'Original50Hz/8physics/2feedback clock required')
        require(self.last_physics_tick is None or physics_end_tick == self.last_physics_tick + 8, 'Skipped/duplicate control clock')
        require(producer.get('s_physics_end_tick') == physics_end_tick - 8 and producer.get('s1_physics_end_tick') == physics_end_tick,
                'Measured endpoints differ from original clock')
        require(set(self.buffer.fields) <= set(transition), 'Incomplete original transition fields')
        fields = {}
        for key, (width, dtype) in self.buffer.fields.items():
            value = transition[key]
            tail = (width,) if isinstance(width, int) else width
            require(torch.is_tensor(value) and value.shape == (self.envs, *tail)
                and value.dtype == dtype and value.device == self.device, 'Wrong measured transition ' + key)
            require(not value.is_floating_point() or bool(torch.isfinite(value).all()), 'Nonfinite measured transition ' + key)
            fields[key] = value.detach()
        s = self.measured_layout.unpack(fields['s'])
        s1 = self.measured_layout.unpack(fields['s1'])
        values, scope = self._anchor_values(actual_anchor, fields, physics_end_tick - 8)
        p = actual_anchor.producer
        require(all(producer.get(k) == getattr(p, k) for k in ('run_id', 'generation', 'source_admission_SHA')),
                'Transition/anchor producer scope differs')
        ids = values['valid_anchor'].nonzero(as_tuple=False).flatten()
        if ids.numel():
            initial = {k: v[ids] for k, v in values.items()}
            initial['scope_records'] = tuple(dict(environment_id=p.environment_ids[i], episode_id=p.episode_ids[i])
                for i in ids.detach().cpu().tolist())
            ss, ss1 = tuple(v[ids] for v in s), tuple(v[ids] for v in s1)
            context = context_from_start_anchor273(initial, ss, 0, self.native_geometry)
            self.model.in_norm.update(self.model.inputs(ss, fields['a'][ids], normalize_context40(context)))
            self.model.out_norm.update(self.model.targets(ss, ss1))
        slot = self.buffer.ptr
        self.anchors.write(slot, values, actual_anchor)
        self.buffer.add(fields)
        self._live_scope = scope
        self.controls += 1
        self.last_physics_tick = physics_end_tick
        return dict(replay_controls=self.buffer.size, supported_current_anchors=int(ids.numel()),
                    unsupported_current_anchors=self.envs-int(ids.numel()))

    def sample(self):
        b, k = self.buffer, self.window
        require(b.size >= k, 'Original H32 replay not yet available')
        start_ages = torch.arange(b.size-k+1, device=self.device)
        eligibility = self.anchors.data['valid_anchor'][b._row(start_ages)]
        candidates = eligibility.nonzero(as_tuple=False)
        require(candidates.shape[0] > 0, 'NO_SUPPORTED_H32_START: no real first anchor, no update/READY')
        draw = torch.randint(0, candidates.shape[0], (self.batch,), device=self.device, generator=self.generator)
        selected = candidates[draw]
        start, env = selected[:, 0], selected[:, 1]
        rows = b._row(start[:, None] + torch.arange(k, device=self.device))
        ids = env[:, None].expand_as(rows)
        # No future xi/depth is gathered for a rollout.
        out = {key: b.data[key][rows, ids] for key in ('s', 's1', 'a', 'done')}
        done = out['done'].float()
        out['mask'] = torch.cumprod(torch.cat((torch.ones(self.batch, 1, device=self.device), 1-done[:, :-1]), -1), -1)
        out['anchor'] = self.anchors.gather(b._row(start), env)
        out['supported_start_candidates'] = candidates.shape[0]
        return out

    def ready_for_update(self):
        b = self.buffer
        if b.size < self.window:
            return False
        starts = torch.arange(b.size-self.window+1, device=self.device)
        return bool(self.anchors.data['valid_anchor'][b._row(starts)].any())

    def rollout_loss(self, batch, *, capture_context=False):
        state = self.measured_layout.unpack(batch['s'][:, 0])
        states, contexts = [], []
        for i in range(self.window):
            raw_context = context_from_start_anchor273(batch['anchor'], state, i, self.native_geometry)
            state = self.model.step(state, batch['a'][:, i], normalize_context40(raw_context))
            states.append(state)
            if capture_context:
                contexts.append(raw_context)
        prediction = tuple(torch.stack([value[i] for value in states], 1) for i in range(7))
        scale = torch.maximum(self.model.out_norm.std(), self.floor)
        error = (self.model.state_error(prediction, self.measured_layout.unpack(batch['s1'])) / scale).square().mean(-1)
        loss = (error * batch['mask']).sum() / self.batch
        require(bool(torch.isfinite(loss)), 'Nonfinite original H32 time-sum loss')
        return loss, prediction, (torch.stack(contexts, 1) if capture_context else None)

    def update(self):
        batch = self.sample()
        loss, _, _ = self.rollout_loss(batch)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.)
        require(bool(torch.isfinite(norm)), 'Nonfinite WM gradient norm')
        require(all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in self.model.parameters()), 'Nonfinite WM gradient')
        self.optimizer.step()
        require(all(bool(torch.isfinite(p).all()) for p in self.model.parameters()), 'Nonfinite WM parameters')
        self.updates += 1
        return dict(world_updates=self.updates, finite=True, loss=float(loss.detach()), preclip_grad_L2=float(norm),
            replay_controls=self.buffer.size, window=32, first_anchor_only=True,
            supported_start_candidates=batch['supported_start_candidates'], teacher_updates=0,
            policy_updates=0, critic_updates=0, WM_optimizer_count=1,
            actual_WM_updates=0 if self.synthetic_CPU_test else self.updates,
            synthetic_CPU_test=self.synthetic_CPU_test)

    def checkpoint(self):
        out = super().checkpoint()
        out.update(future_safe_WM_warm_schema='V273_FIRST_CURRENT_ANCHOR_ONLY',
            anchor_replay_saved=False, replay_resume_scope='fresh physical/anchor replay; WM params/norms/Adam/counters retained',
            teacher_contract=self.teacher_contract.__dict__, teacher_and_Pi_updates=0,
            complete_three_optimizer_conversion=False, actual_Pi_runtime_qualified=False)
        def finite_tree(value):
            if torch.is_tensor(value):
                return not value.is_floating_point() or bool(torch.isfinite(value).all())
            if isinstance(value, dict):
                return all(finite_tree(v) for v in value.values())
            if isinstance(value, (list, tuple)):
                return all(finite_tree(v) for v in value)
            return True
        require(finite_tree(out), 'Nonfinite WM checkpoint tree')
        return out
