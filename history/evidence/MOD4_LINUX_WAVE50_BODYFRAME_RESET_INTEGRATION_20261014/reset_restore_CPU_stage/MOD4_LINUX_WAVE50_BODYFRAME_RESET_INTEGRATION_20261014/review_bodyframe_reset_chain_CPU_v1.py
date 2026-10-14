"""Actual whole20k state + actual collision bank, explicitly synthetic CPU scene.

Exercises the new call chain; does not credit a PhysX/native/GPU admission.
All original source and failed reports remain immutable.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import sys
import time
import traceback
from types import SimpleNamespace as NS
import numpy as np
import torch

B = Path(__file__).resolve().parent
W = B.parent
sys.path.insert(0, str(B / 'payload_v1'))
import birth_bodyframe_state_v1 as state
import birth_bodyframe_reset_adapter_v1 as reset


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree_hash(value):
    h = hashlib.sha256()
    def visit(v):
        h.update(type(v).__name__.encode() + b'\0')
        if torch.is_tensor(v):
            h.update(str(v.dtype).encode()); h.update(str(tuple(v.shape)).encode())
            h.update(v.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(v, np.ndarray):
            h.update(str(v.dtype).encode()); h.update(str(v.shape).encode()); h.update(v.tobytes())
        elif isinstance(v, dict):
            for k in sorted(v, key=repr): visit(k); visit(v[k])
        elif isinstance(v, (list, tuple)):
            for x in v: visit(x)
        else: h.update(repr(v).encode())
    visit(value)
    return h.hexdigest()


class PlaneRay:
    """CPU contract fixture only; not a replacement query engine."""
    def __init__(self):
        self.geometry = NS(vertices=torch.tensor([[0., 0., 0.]]))
        self.calls = 0; self.points = 0; self.missing = False
    def cast(self, starts, distance):
        assert starts.shape[-1] == 3 and distance == 10.
        self.calls += 1; self.points += starts.numel() // 3
        shape = starts.shape[:-1]
        normal = torch.zeros_like(starts); normal[..., 2] = 1.
        return dict(hit=torch.full(shape, not self.missing, dtype=torch.bool),
                    height=torch.zeros(shape), normal=normal)


class Robot:
    def __init__(self, source, points):
        e = source['E1_terrain_state']; self.default = torch.zeros((state.N, 13))
        self.default[:, :2] = e['spawn_xy']
        self.default[:, 2] = .002 - points[:, 2].min()
        self.default[:, 6] = 1.
        self.expected = e['reset_expected_q'].clone()
        self.data = NS(root_state_w=self.default.clone(), joint_pos=self.expected.clone(),
                       joint_vel=torch.zeros((state.N, 30)))
        self.setter_ids = []; self.bad_setter = False
    def write_root_state_to_sim(self, value, env_ids):
        self.setter_ids.append(env_ids.clone())
        self.data.root_state_w[env_ids] = value
        if self.bad_setter:
            self.data.root_state_w[env_ids[0], 0] += .01


class Command:
    def __init__(self, source, env):
        d = source['E1_WAVE50_episode_direction_state']
        self.env = env; self.saved = state.clone(d)
        self.wave_mask = d['wave_mask'].clone(); self.entry_sign = d['entry_sign'].clone()
        self.bound_episode = d['bound_episode'].clone()
        self.family = torch.where(self.wave_mask, 4, 0)
        self.is_standing_env = torch.arange(state.N) % 5 == 0
        self.vel_command_b = torch.zeros((state.N, 3))
        self.manual_evaluation_mode = False
        self.ordinary_draw_calls = 0
    def _write_dynamic(self, ids):
        # Stand-in for the original WORLD-directed producer. It neither reads
        # the new orientation state nor consumes new random numbers.
        self.vel_command_b[ids] = 0.
        selected = ids[self.wave_mask[ids] & ~self.is_standing_env[ids]]
        self.vel_command_b[selected, 0] = .3 * self.entry_sign[selected]
        self.bound_episode[ids] = self.env._e1_episode[ids]
    def state_dict_direction(self):
        out = state.clone(self.saved)
        out['wave_mask'] = self.wave_mask.clone()
        out['entry_sign'] = self.entry_sign.clone()
        out['bound_episode'] = self.bound_episode.clone()
        return out
    def audit_direction(self):
        active = self.wave_mask & (self.family == 4) & ~self.is_standing_env
        assert (self.vel_command_b[active, 0] * self.entry_sign[active] >= 0).all()
        return {'legacy_CPU_fixture': True}


class Scene(dict):
    pass


class Env:
    def __init__(self, source, points):
        self.num_envs = state.N; self.physics_dt = .0025; self.step_dt = .01; self.device = 'cpu'
        self._e1_episode = source['E1_terrain_state']['episode'].clone()
        self._sim_step_counter = 0; self.original_resets = 0; self.original_steps = 0
        self.original_normal_DR_reset_calls = 0
        self.scene = Scene(robot=Robot(source, points))
        self._rough_probe_bank = dict(points=points)
        self._rough_probe_expected_q = source['E1_terrain_state']['reset_expected_q'].clone()
        self._rough_spawn_xy = source['E1_terrain_state']['spawn_xy'].clone()
        self._rough_query_tick = 17
        self._rough_probe_reset_receipt = {'original_reset_fixture': True}
        self.term = Command(source, self)
        self.command_manager = NS(get_term=lambda name: self.term if name == 'twist' else None)
    def _reset_idx(self, ids):
        # Deliberately update commands BEFORE incrementing episode, as the
        # inherited manager may do; the adapter must bind after the whole reset.
        self.original_resets += 1
        self.original_normal_DR_reset_calls += len(ids)
        robot = self.scene['robot']
        robot.data.root_state_w[ids] = robot.default[ids]
        robot.data.joint_pos[ids] = robot.expected[ids]
        robot.data.joint_vel[ids] = 0.
        self.term._write_dynamic(ids)
        self._e1_episode[ids] += 1
    def step(self, actions):
        self.original_steps += 1
        self._sim_step_counter += 4
        return actions


def main():
    reports = B / 'reports'; reports.mkdir(parents=True, exist_ok=True)
    output = reports / 'BODYFRAME_WHOLE20K_RESET_COMMAND_SAVE_CHAIN_CPU_ACTUAL.json'
    assert not output.exists()
    try:
        torch.set_num_threads(4)
        p = W / 'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt'
        assert sha(p) == state.SOURCE
        source = torch.load(p, map_location='cpu', weights_only=False)
        original_hash = tree_hash(source); rng = torch.get_rng_state().clone()
        bank = W / 'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
        assert sha(bank) == source['E1_terrain_state']['reset_bank_sha256']
        with np.load(bank) as z:
            pick = int(np.argmin(abs(z['root_height'] - .25)))
            points = torch.from_numpy(z['points_root'][pick].astype(np.float32).copy())
        assert points.shape == (25200, 3)
        d = source['E1_WAVE50_episode_direction_state']; r = source['E1_WAVE50_route_lifecycle_state']; l = source['E1_WAVE50_episode_lifetime_state']
        bindings = {k: d[k] for k in ('assignment_sha256', 'entry_map_sha256', 'entry_origin_sha256')}
        bindings.update(parent_boundary_source_sha256=r['parent_boundary_source_sha256'], parent_timeout_source_sha256=l['parent_timeout_source_sha256'])
        s = state.from_whole_predecessor(source, state.SOURCE, bindings)
        env = Env(source, points); ray = PlaneRay(); allids = torch.arange(state.N)
        adapter = reset.BirthAdapter(env, s, ray, {'CPU_fixture_only': True}, fixture=True)
        # Original new episode is done first; the new adapter cannot call reset.
        env._reset_idx(allids)
        calls_before = env.original_resets
        original_receipt = copy.deepcopy(env._rough_probe_reset_receipt)
        birth = adapter.after_existing_birth(allids)
        assert env.original_resets == calls_before == 1
        assert env.original_normal_DR_reset_calls == state.N
        assert env._rough_probe_reset_receipt == original_receipt
        assert len(birth['pi_ids']) == 1410
        adapter.install()
        audit = env.term.audit_direction()
        negatives = []
        def rejected(name, fn, kinds=(AssertionError,)):
            try: fn()
            except kinds: negatives.append(name)
            else: raise AssertionError('Wrong admission: ' + name)
        rejected('legacy_BODY_WORLD_predicate_rejects_new_valid_axis', adapter.original_audit)
        ids = torch.nonzero(s['wave_mask']).flatten()[::197]
        before_command = env.term.vel_command_b.clone()
        for _ in range(3): env.term._write_dynamic(ids)
        assert torch.equal(env.term.vel_command_b, before_command)
        before_root = env.scene['robot'].data.root_state_w.clone()
        before_state = adapter.state_dict()
        not_selected = torch.ones(state.N, dtype=torch.bool); not_selected[ids] = False
        env._reset_idx(ids)
        assert env.original_resets == 2 and env.original_normal_DR_reset_calls == state.N + len(ids)
        assert torch.equal(env.scene['robot'].data.root_state_w[not_selected], before_root[not_selected])
        for key in ('births', 'bound_episode', 'flip_pi', 'BODY_coefficient'):
            assert torch.equal(adapter.state[key][not_selected], before_state[key][not_selected])
        assert torch.equal(adapter.state['flip_pi'][ids], ~before_state['flip_pi'][ids])
        assert env._rough_probe_reset_receipt == original_receipt
        for _ in range(3): env.step(torch.zeros((state.N, 6)))
        assert env.original_steps == 3 and env._sim_step_counter == 12
        assert adapter.state['completed_controls'] == 3
        assert int(adapter.state['completed_control_histogram'].sum()) == int(s['wave_mask'].sum()) * 3
        # Real whole checkpoint structure, but new episodes/commands below are
        # explicit synthetic fixture fields, not a real resumable training source.
        fixture = state.clone(source)
        fixture['E1_terrain_state']['episode'] = env._e1_episode.clone()
        for key in ('E1_WAVE50_episode_direction_state', 'E1_WAVE50_route_lifecycle_state', 'E1_WAVE50_episode_lifetime_state'):
            fixture[key]['bound_episode'] = env._e1_episode.clone()
        fixture['E1_retained_flat_command_state']['BODY_command'] = env.term.vel_command_b.clone()
        fixture['E1_retained_flat_command_state']['family'] = env.term.family.clone()
        old_fixture_hash = tree_hash(fixture)
        saved = state.bind_saved_checkpoint(fixture, adapter.state_dict())
        assert tree_hash({k: v for k, v in saved.items() if k != state.KEY}) == old_fixture_hash
        fixture_path = B / 'CPU_fixture_not_production_source_with_bodyframe.pt'
        assert not fixture_path.exists(); torch.save(saved, fixture_path)
        disk = torch.load(fixture_path, map_location='cpu', weights_only=False)
        assert tree_hash(disk) == tree_hash(saved)
        before_load = env.scene['robot'].data.root_state_w.clone()
        reset_calls_before_load = env.original_resets
        adapter.load_state_dict(disk[state.KEY])
        assert torch.equal(before_load, env.scene['robot'].data.root_state_w)
        assert reset_calls_before_load == env.original_resets
        bad = state.clone(adapter.state); bad['declared_transition']['new_entry_pose'] = False
        rejected('wrong_sameidentity_newentry_false', lambda: state.validate(bad, bindings))
        rejected('same_episode_rebind', lambda: state.next_birth(adapter.state, ids, env._e1_episode))
        rejected('duplicate_selected_births', lambda: state.next_birth(adapter.state, torch.tensor([ids[0], ids[0]]), env._e1_episode + 1))
        rejected('skipped_episode', lambda: state.next_birth(adapter.state, ids, env._e1_episode + 2))
        rejected('CPU_fixture_cannot_claim_GPU_native', lambda: reset.assert_backend(env, {'CPU_fixture_only': True}, False))
        rejected('wrong_quaternion_norm', lambda: reset.pi_xyzw(torch.ones((2, 4))))
        bad_disk = state.clone(adapter.state); bad_disk['source_bindings']['entry_map_sha256'] = '0' * 64
        rejected('wrong_saved_entry_map', lambda: adapter.load_state_dict(bad_disk))
        bad_command = env.term.vel_command_b.clone(); active = torch.nonzero(s['wave_mask'] & ~env.term.is_standing_env).flatten()[0]
        bad_command[active, 0] *= -1
        rejected('actual_BODY_wrong_WORLD_direction', lambda: state.audit_command(bad_command, env.term.family, env.term.is_standing_env, env._e1_episode, adapter.state))
        ray.missing = True
        flipped = torch.nonzero(adapter.state['flip_pi']).flatten()[:1]
        rejected('missing_ground_no_fallback', lambda: reset.place_selected_flipped_births(env, flipped, adapter.state, ray, {'CPU_fixture_only': True}, True))
        ray.missing = False
        env.scene['robot'].bad_setter = True
        rejected('root_setter_readback_mismatch', lambda: reset.place_selected_flipped_births(env, flipped, adapter.state, ray, {'CPU_fixture_only': True}, True))
        env.scene['robot'].bad_setter = False
        # CPU source integration ordering is pinned to the actual original file.
        e1 = W / 'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/ORIGINAL_LINUX_AND_V6_SOURCE_FAILURE_SNAPSHOTS/original_Linux20k_d05_continuation_runtime_assets_complete_v3/isaac/mod4/e1_terrain_training_env.py'
        parsed = ast.parse(e1.read_bytes()); fn = next(n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef) and n.name == '_reset_idx')
        assert isinstance(fn.body[0], ast.Expr) and 'super()._reset_idx(ids)' in ast.unparse(fn.body[0])
        assert '_e1_episode[ids] += 1' in ast.unparse(fn.body[1])
        assert tree_hash(source) == original_hash and sha(p) == state.SOURCE
        assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
        report = dict(epoch=time.time(), passed_CPU_reset_command_checkpoint_component=True,
            actual_whole20k_source=dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p), original_tree_SHA=original_hash),
            actual_collision_bank=dict(path=str(bank), bytes=bank.stat().st_size, sha256=sha(bank), points=25200),
            old_source_all195tensors107float99perenv_unchanged=True,
            original_actual_reset_source=dict(path=str(e1), sha256=sha(e1), episode_increment_after_original_super=True),
            first_birth1410pi1410unrotated_of2820=True,
            original_reset_called_once_per_birth_no_extra_DR_reset=True,
            original_legacy_receipt_preserved=True,
            selected_reset_other_rows_root_command_state_exact=True,
            repeated_subset_command_writes_idempotent=True,
            new_BODY_WORLD_direction_audit=True,
            physical_control_count_fixture=3, callback_count_fixture=12,
            histogram_pre_reset_command_phase=True,
            CPU_fullcheckpoint_disk_roundtrip=True,
            old_fixture_fields_exact_and_new_owned_state_only=True,
            load_state_no_pose_reset_or_RNG_side_effect=True,
            CPU_fixture=dict(path=str(fixture_path), bytes=fixture_path.stat().st_size, sha256=sha(fixture_path), forbidden_training_source=True),
            negatives_rejected=negatives, fixture_ray_calls=ray.calls, fixture_point_queries=ray.points,
            CPU_global_RNG_exact=True, CUDA_initialized=False, new_GPU_task=False,
            actual_native_ABI_passed=False, real_PhysX_placement_passed=False,
            new_production_worker_fullrestore_passed=False, learning_or_budget_admitted=False,
            limitation='Full20k state and real25200-point collider bank with synthetic CPU scene/flat query fixture; not a native, CUDA, physical route or learning pass.',
            remaining=['Actual own Linux quaternion/data/nativegetter ABI and selected setter witness',
                       'Bind the adapter after strict original whole predecessor restore; own first-transition and same-new-scope checkpoint restore integration',
                       'Own immutable runtime/source manifest, resource/budget/native-fullstate and all inherited13 typed receipts before any new-axis PPO'],
            source_sha={str(x.relative_to(B)): sha(x) for x in (B / 'payload_v1').glob('*.py')},
            reader_sha=sha(__file__), Git_pending=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
        print(json.dumps(dict(passed_CPU_component=True, source_envs=20000, selected_reset_rows=len(ids),
                              source_unchanged=True, negatives=len(negatives), GPU_PPO_admitted=False)))
    except BaseException:
        err = reports / ('BODYFRAME_RESET_CPU_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')
        err.write_text(json.dumps(dict(epoch=time.time(), error=traceback.format_exc(), reader_sha=sha(__file__),
            source_sha={str(x.relative_to(B)): sha(x) for x in (B / 'payload_v1').glob('*.py')},
            no_GPU_or_PPO_or_budget=True, original_sources_unchanged=True, Git_pending=True), indent=2), encoding='utf8')
        raise


if __name__ == '__main__':
    main()
