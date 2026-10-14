"""Restore the old whole scope first, then declare one new birth-pose axis.

The old twelve restore functions and normal learner are not edited. Own future
bodyframe checkpoints also run the unmodified old restore/new-episode chain
with this adapter uninstalled, then bind the saved orientation state to that
single new episode. No extra reset is used to re-enter the new scope.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import time
import torch
from birth_bodyframe_state_v1 import (SOURCE, KEY, PROFILE, N, clone, validate,
                                      from_whole_predecessor, bind_saved_checkpoint)
from birth_bodyframe_reset_adapter_v5 import BirthAdapter, tensor

LEFT_KEY = 'LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
LEFT_PROFILE = 'left_initial_joint_margin014_std1_v1'
GPU_OWN_MARK = 'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(a, b):
    if torch.is_tensor(a):
        return torch.is_tensor(b) and a.dtype == b.dtype and a.shape == b.shape and torch.equal(a.cpu(), b.cpu())
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return type(a) is type(b) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if hasattr(a, 'shape'):
        import numpy as np
        return type(a) is type(b) and np.array_equal(a, b)
    return type(a) is type(b) and a == b


def bindings_from_checkpoint(ck):
    d = ck['E1_WAVE50_episode_direction_state']; r = ck['E1_WAVE50_route_lifecycle_state']; l = ck['E1_WAVE50_episode_lifetime_state']
    out = {k: d[k] for k in ('assignment_sha256', 'entry_map_sha256', 'entry_origin_sha256')}
    out.update(parent_boundary_source_sha256=r['parent_boundary_source_sha256'],
               parent_timeout_source_sha256=l['parent_timeout_source_sha256'])
    return out


def guard_manifest(manifest, fixture):
    assert manifest['scope_profile'] == PROFILE and manifest['num_envs'] == N
    assert manifest['initial_whole20k_source_SHA'] == SOURCE
    assert len(manifest['actual_source_SHA']) == 64
    assert manifest['reinitialize_left_head'] is False
    assert manifest['new_geometry'] is False and manifest['new_world_route_or_lifetime'] is False
    assert manifest['new_entry_pose'] is True and manifest['new_BODY_direction_identity'] is True
    assert manifest['new_RNG_draws'] is False and manifest['live_heading_position_correction'] is False
    if fixture:
        assert manifest['CPU_fixture_only'] is True and manifest['approved_GPU'] is False
    else:
        assert manifest['CPU_fixture_only'] is False and manifest['approved_GPU'] is True
        assert manifest['actual_target_CPU_source_bound'] is True
        assert manifest['actual_resource_and_original_budget_admitted'] is True
        assert manifest['actual_unique_GPU_lease_held'] is True
        assert len(manifest['sourcefreeze_SHA']) == 64


def native_ABI(env, manifest):
    """Read only actual native transforms, with no extra simulation operation."""
    robot = env.scene['robot']
    native = tensor(robot.root_physx_view.get_root_transforms()).clone()
    data = tensor(robot.data.root_state_w)[:, :7].clone()
    assert native.shape == (N, 7)
    exact_bits = torch.equal(native, data)
    xyz_exact = torch.equal(native[:, :3], data[:, :3])
    nq = native[:, 3:7]; dq = data[:, 3:7]
    assert torch.isfinite(nq).all() and torch.isfinite(dq).all()
    assert torch.allclose(nq.square().sum(-1), torch.ones(N, device=env.device), atol=1e-6, rtol=0)
    nn = nq / nq.norm(dim=-1, keepdim=True); dn = dq / dq.norm(dim=-1, keepdim=True)
    rotation_error = torch.minimum((nn-dn).norm(dim=-1), (nn+dn).norm(dim=-1))
    witness_index = getattr(env, '_bodyframe_native_getter_witness_count', 0)
    env._bodyframe_native_getter_witness_count = witness_index + 1
    witness = Path(manifest['actual_target_root']) / ('NATIVE_ROOT_GETTER_DATA_WITNESS_'+str(witness_index)+'.pt')
    torch.save(dict(native=native.cpu(), data=data.cpu(), rotation_error=rotation_error.cpu(),
                    raw_bits_exact=exact_bits, XYZ_exact=xyz_exact,
                    quaternion_normalization_and_sign_equivalence_only=True), witness)
    assert xyz_exact, 'Native/data root XYZ differs; no spatial tolerance relaxation'
    assert (rotation_error <= 1e-6).all(), 'Native/data quaternion rotation differs beyond unit-rotation representation bound'
    assert torch.allclose(data[:, 3:7].square().sum(-1), torch.ones(N, device=env.device), atol=1e-6, rtol=0)
    x, y, z, w = data[:, 3:7].unbind(-1)
    expected_heading = torch.atan2(2 * (w * z + x * y), 1 - 2 * (y.square() + z.square()))
    delta = tensor(robot.data.heading_w) - expected_heading
    heading_error = torch.atan2(torch.sin(delta), torch.cos(delta)).abs()
    assert torch.isfinite(heading_error).all() and float(heading_error.max()) <= 1e-6, 'Native heading disagrees with xyzw rotation convention'
    return dict(actual_own_native_quaternion_ABI_verified=True, quaternion_convention='xyzw',
                own_source_SHA=SOURCE, scope_profile=PROFILE, extra_physics_steps_for_ABI_check=0,
                data_vs_native_root_getter_exact=exact_bits, data_native_XYZ_exact=xyz_exact,
                data_native_rotation_matches_normalized_sign_invariant=True,
                quaternion_rotation_error_max=float(rotation_error.max()),
                native_getter_witness=str(witness), native_getter_witness_SHA=sha(witness),
                native_setter_readback_required=True,
                independent_xyzw_heading_witness_verified=True, heading_error_max_rad=float(heading_error.max()),
                actual_native_transforms_SHA=hashlib.sha256(native.cpu().contiguous().numpy().tobytes()).hexdigest(),
                sourcefreeze_verified=True, sourcefreeze_SHA=manifest['sourcefreeze_SHA'])


def patch(module, manifest, typed13, ray_getter, fixture=False):
    guard_manifest(manifest, fixture)
    old_resume = module.resume_e1_new_episode
    old_install = module.install_e1_save_contract

    def resume(runner, env, path, log_dir):
        assert not hasattr(env, '_birth_bodyframe_adapter'), 'New scope adapter must not alter the original restore/reset chain'
        assert sha(path) == manifest['actual_source_SHA']
        ck = torch.load(path, map_location='cpu', weights_only=False)
        if not fixture:
            assert ck.get('BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE') is not True
        assert ck['sensor_DR_state']['n'] == N and ck['independent_terrain_expert'] == 'E1_WAVE50'
        mark = ck[LEFT_KEY]
        assert mark['profile'] == LEFT_PROFILE and mark['source_envs'] == N
        assert mark['source_SHA'] == '1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
        first = KEY not in ck
        bindings = bindings_from_checkpoint(ck)
        if first:
            assert sha(path) == SOURCE
            predecessor = from_whole_predecessor(ck, SOURCE, bindings)
        else:
            validate(ck[KEY], bindings)
            if not fixture:
                assert ck[GPU_OWN_MARK]['actual_GPU_fullrestore'] is True
                assert ck[GPU_OWN_MARK]['profile'] == PROFILE
                assert len(ck[GPU_OWN_MARK]['startup_receipt_SHA']) == 64
            predecessor = clone(ck[KEY])
            assert torch.equal(predecessor['bound_episode'], ck['E1_terrain_state']['episode'])
        # No adapter or new pose/command mutation is installed during old restore.
        result = old_resume(runner, env, path, log_dir)
        assert torch.equal(env._e1_episode.cpu(), ck['E1_terrain_state']['episode'] + 1)
        assert same(runner.alg.actor.state_dict(), ck['actor_state_dict'])
        assert same(runner.alg.critic.state_dict(), ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(), ck['optimizer_state_dict'])
        runner._left_bodyframe_immutable_mark = copy.deepcopy(mark)
        left = dict(epoch=time.time(), pid=os.getpid(), source_sha256=sha(path), passed=True,
                    explicit_one_time_left_mean_std_initialization=False, same_left_branch_restored_exact=True,
                    all_original_twelve_fullstate_contracts_precede_left_axis=True,
                    actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact=not fixture,
                    no_CPU_CUDA_RNG_draw_for_initializer=True, no_env_DR_command_or_history_mutation_by_initializer=True,
                    initial_other_five_heads_critic_exact=True, initializer_not_live_action_coupling=True,
                    source_episode_plus_one_checked_by_original_contract=True, PhysX_exact_resume_claimed=False,
                    qualified50=False, CPU_fixture_only=fixture)
        # Keep actual CUDA disk proof, even though no left re-initializer exists.
        left_disk = Path(log_dir) / 'LEFT_BRANCH_UNCHANGED_ACTUAL_ROUNDTRIP.pt'
        left_state = dict(actor=runner.alg.actor.state_dict(), optimizer=runner.alg.optimizer.state_dict(), mark=mark)
        torch.save(left_state, left_disk)
        assert same(left_state, torch.load(left_disk, map_location='cpu', weights_only=False))
        Path(log_dir, 'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(left, indent=2), encoding='utf8')
        paths = [Path(log_dir) / name for name in typed13.REQUIRED_BOOLEAN_SCHEMA]
        if not fixture:
            assert all(json.loads(p.read_bytes()).get('CPU_fixture_only') is not True for p in paths)
        typed = typed13.validate_set(paths, os.getpid(), sha(path))
        beforeCPU = torch.get_rng_state().clone()
        beforeCUDA = [] if fixture else [x.clone() for x in torch.cuda.get_rng_state_all()]
        owned = {k: v.to(env.device).clone() if torch.is_tensor(v) else clone(v) for k, v in predecessor.items()}
        old_body_disk = Path(log_dir) / 'BIRTH_BODYFRAME_PREDECESSOR_OWNED_STATE_ROUNDTRIP.pt'
        torch.save(owned, old_body_disk)
        assert same(owned, torch.load(old_body_disk, map_location='cpu', weights_only=False))
        backend = {'CPU_fixture_only': True} if fixture else native_ABI(env, manifest)
        adapter = BirthAdapter(env, owned, ray_getter(env), backend, fixture=fixture)
        ids = torch.arange(N, device=env.device)
        birth = adapter.after_existing_birth(ids)
        torch.save(birth, Path(log_dir) / 'BIRTH_BODYFRAME_ACTUAL_NATIVE_PLACEMENT_READBACK.pt')
        Path(log_dir, 'BIRTH_BODYFRAME_ACTUAL_NATIVE_ABI_BEFORE.json').write_text(json.dumps(backend, indent=2), encoding='utf8')
        adapter.install()
        env._birth_bodyframe_adapter = adapter
        env._birth_bodyframe_log_dir = str(log_dir)
        if not fixture:
            # Verify the setter against the actual native view after placement.
            native_ABI(env, manifest)
        own = adapter.state_dict()
        body_disk = Path(log_dir) / 'BIRTH_BODYFRAME_NEW_EPISODE_OWNED_STATE_ROUNDTRIP.pt'
        torch.save(own, body_disk)
        adapter.load_state_dict(torch.load(body_disk, map_location='cpu', weights_only=False))
        assert same(own, adapter.state_dict()) and torch.equal(beforeCPU, torch.get_rng_state())
        if not fixture:
            assert all(torch.equal(a, b) for a, b in zip(beforeCUDA, torch.cuda.get_rng_state_all()))
        assert same(runner.alg.actor.state_dict(), ck['actor_state_dict'])
        assert same(runner.alg.critic.state_dict(), ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(), ck['optimizer_state_dict'])
        proof = dict(epoch=time.time(), pid=os.getpid(), source_sha256=sha(path), profile=PROFILE,
                     passed=True, CPU_fixture_only=fixture, actual_GPU_fullrestore_passed=not fixture,
                     predecessor_all13_typed_restores_verified_before_new_pose=not fixture,
                     CPU_fixture_original13_sequence_exercised=fixture,
                     predecessor_bodyframe_state_present=not first, first_declared_new_entry_and_BODYdirection=first,
                     strict_actorcriticstdAdam_unchanged=True, source_episode_plus_one=True,
                     old_fullreset_used_once_no_extra_physical_birth=True,
                     own_bodyframe_predecessor_and_newbirth_disk_roundtrips=True,
                     no_initializer_repeat_or_new_RNG=True, no_PhysX_exactresume_claim=True,
                     actual_native_ABI_and_setter_verified=not fixture,
                     changed_pi_births=len(birth['pi_ids']), typed13=typed,
                     new_audit=env.command_manager.get_term('twist').audit_direction())
        Path(log_dir, 'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof, indent=2), encoding='utf8')
        return result

    def install(runner, env):
        assert hasattr(env, '_birth_bodyframe_adapter')
        old_install(runner, env)
        old_save = runner.save
        def save(path, *args, **kwargs):
            assert sha(manifest['source_path']) == manifest['actual_source_SHA']
            assert Path(path).resolve() != Path(manifest['source_path']).resolve()
            old_save(path, *args, **kwargs)
            old = torch.load(path, map_location='cpu', weights_only=False)
            old[LEFT_KEY] = copy.deepcopy(runner._left_bodyframe_immutable_mark)
            output = bind_saved_checkpoint(old, env._birth_bodyframe_adapter.state_dict())
            startup = Path(env._birth_bodyframe_log_dir) / 'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json'
            proof = json.loads(startup.read_bytes())
            assert proof['pid'] == os.getpid() and proof['source_sha256'] == manifest['actual_source_SHA']
            assert proof['CPU_fixture_only'] is fixture and proof['actual_GPU_fullrestore_passed'] is (not fixture)
            output[GPU_OWN_MARK] = dict(profile=PROFILE, actual_GPU_fullrestore=not fixture,
                own_pid=os.getpid(), startup_receipt_SHA=sha(startup))
            if fixture:
                output['BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE'] = True
            partial = Path(str(path) + '.bodyframe.saving.pt')
            assert not partial.exists(), 'Retain partial outcomes; do not overwrite'
            torch.save(output, partial)
            with partial.open('r+b') as stream:
                stream.flush(); os.fsync(stream.fileno())
            os.replace(partial, path)
        runner.save = save
    module.resume_e1_new_episode = resume
    module.install_e1_save_contract = install
