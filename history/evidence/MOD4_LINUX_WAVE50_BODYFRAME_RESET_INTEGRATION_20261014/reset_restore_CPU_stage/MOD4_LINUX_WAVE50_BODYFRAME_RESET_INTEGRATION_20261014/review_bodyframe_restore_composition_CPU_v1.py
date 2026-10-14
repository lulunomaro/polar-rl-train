"""Two restore/save compositions in a labelled CPU scene, never native proof."""
from pathlib import Path
import copy
import importlib.util
import json
import os
import sys
import time
import traceback
from types import SimpleNamespace as NS
import numpy as np
import torch

B = Path(__file__).resolve().parent; W = B.parent
sys.path.insert(0, str(B / 'payload_v1'))
import birth_bodyframe_state_v1 as state
import birth_bodyframe_full_checkpoint_v1 as checkpoint
import review_bodyframe_reset_chain_CPU_v1 as component


class DictObject:
    def __init__(self, value): self.value = state.clone(value)
    def state_dict(self): return self.value


class TypedFixture:
    """Checks sequence and identity only; not the real CUDA receipt validator."""
    def __init__(self, schema): self.REQUIRED_BOOLEAN_SCHEMA = schema
    def validate_set(self, paths, pid, source):
        assert len(paths) == 13 and {p.name for p in paths} == set(self.REQUIRED_BOOLEAN_SCHEMA)
        for p in paths:
            v = json.loads(p.read_bytes())
            assert v['CPU_fixture_only'] is True and v['pid'] == pid and v['source_sha256'] == source
            if p.name == 'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json':
                assert v['actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact'] is False
        return [dict(name=p.name, CPU_fixture_sequence_only=True, CUDA_receipt_admitted=False) for p in paths]


def stage(source_path, folder, points, schemas):
    source = torch.load(source_path, map_location='cpu', weights_only=False)
    env = component.Env(source, points); ray = component.PlaneRay()
    runner = NS(alg=NS(actor=DictObject(source['actor_state_dict']), critic=DictObject(source['critic_state_dict']),
                       optimizer=DictObject(source['optimizer_state_dict'])))
    calls = []
    folder.mkdir(parents=True, exist_ok=False)
    def old_resume(actual_runner, actual_env, path, log_dir):
        assert actual_runner is runner and actual_env is env and not hasattr(env, '_birth_bodyframe_adapter')
        assert checkpoint.sha(path) == checkpoint.sha(source_path)
        # Emulate the old complete restore ownership, followed by its single
        # original new episode. No old production function is executed on CPU.
        calls.append('old_restore_before_new_adapter')
        env._reset_idx(torch.arange(state.N))
        for name in schemas:
            if name == 'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json': continue
            Path(log_dir, name).write_text(json.dumps(dict(CPU_fixture_only=True, pid=os.getpid(),
                source_sha256=checkpoint.sha(path), fixture_name=name,
                actual_GPU_or_CUDA_verified=False)), encoding='utf8')
        return dict(CPU_fixture_only=True, actual_original_GPU_restore_not_executed=True)
    def old_install(actual_runner, actual_env):
        assert hasattr(actual_env, '_birth_bodyframe_adapter')
        def save(path, *args, **kwargs):
            ck = state.clone(source)
            # The actual RSL save produces current fields afresh. This explicit
            # fixture does the same for the fields touched by episode/reset.
            for name in (state.KEY, checkpoint.GPU_OWN_MARK, 'BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE'):
                ck.pop(name, None)
            ck['E1_terrain_state']['episode'] = env._e1_episode.clone()
            for key in ('E1_WAVE50_episode_direction_state', 'E1_WAVE50_route_lifecycle_state', 'E1_WAVE50_episode_lifetime_state'):
                ck[key]['bound_episode'] = env._e1_episode.clone()
            ck['E1_retained_flat_command_state']['BODY_command'] = env.term.vel_command_b.clone()
            ck['E1_retained_flat_command_state']['family'] = env.term.family.clone()
            torch.save(ck, path)
        actual_runner.save = save
    module = NS(resume_e1_new_episode=old_resume, install_e1_save_contract=old_install)
    manifest = dict(scope_profile=state.PROFILE, num_envs=state.N, initial_whole20k_source_SHA=state.SOURCE,
        actual_source_SHA=checkpoint.sha(source_path), source_path=str(source_path), reinitialize_left_head=False,
        new_geometry=False, new_world_route_or_lifetime=False, new_entry_pose=True,
        new_BODY_direction_identity=True, new_RNG_draws=False, live_heading_position_correction=False,
        CPU_fixture_only=True, approved_GPU=False)
    checkpoint.patch(module, manifest, TypedFixture(schemas), lambda _: ray, fixture=True)
    module.resume_e1_new_episode(runner, env, source_path, folder)
    assert calls == ['old_restore_before_new_adapter'] and env.original_resets == 1
    assert env.original_normal_DR_reset_calls == state.N
    assert torch.equal(env._e1_episode, source['E1_terrain_state']['episode'] + 1)
    proof = json.loads((folder / 'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').read_bytes())
    assert proof['actual_GPU_fullrestore_passed'] is False
    assert proof['predecessor_all13_typed_restores_verified_before_new_pose'] is False
    assert proof['CPU_fixture_original13_sequence_exercised'] is True
    module.install_e1_save_contract(runner, env)
    destination = folder / 'CPU_fixture_fullcheckpoint_NOT_training_source.pt'
    runner.save(destination)
    saved = torch.load(destination, map_location='cpu', weights_only=False)
    assert saved['BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE'] is True
    assert saved[checkpoint.GPU_OWN_MARK]['actual_GPU_fullrestore'] is False
    for key in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', checkpoint.LEFT_KEY):
        assert checkpoint.same(saved[key], source[key])
    assert checkpoint.same(saved[state.KEY], env._birth_bodyframe_adapter.state_dict())
    return saved, destination, proof, manifest


def main():
    reports = B / 'reports'; reports.mkdir(exist_ok=True)
    output = reports / 'BODYFRAME_TWO_STAGE_OLD_RESTORE_FIRST_SAVE_RESUME_COMPOSITION_CPU_ACTUAL.json'
    assert not output.exists()
    try:
        torch.set_num_threads(4)
        p = W / 'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt'
        assert checkpoint.sha(p) == state.SOURCE
        ck = torch.load(p, map_location='cpu', weights_only=False)
        before = component.tree_hash(ck); rng = torch.get_rng_state().clone()
        bank = W / 'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
        assert checkpoint.sha(bank) == ck['E1_terrain_state']['reset_bank_sha256']
        with np.load(bank) as z:
            pick = int(np.argmin(abs(z['root_height'] - .25)))
            points = torch.from_numpy(z['points_root'][pick].astype(np.float32).copy())
        typed_source = W / 'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/payload_v1/left_sameidentity_typed13_receipts.py'
        spec = importlib.util.spec_from_file_location('actual_typed13_schema_only', typed_source)
        typed = importlib.util.module_from_spec(spec); spec.loader.exec_module(typed)
        first, first_path, first_proof, first_manifest = stage(p, B / 'CPU_fixtures/first_transition', points, typed.REQUIRED_BOOLEAN_SCHEMA)
        second, second_path, second_proof, second_manifest = stage(first_path, B / 'CPU_fixtures/same_new_scope_resume', points, typed.REQUIRED_BOOLEAN_SCHEMA)
        assert first_proof['first_declared_new_entry_and_BODYdirection'] is True
        assert second_proof['first_declared_new_entry_and_BODYdirection'] is False
        assert torch.equal(second[state.KEY]['births'], first[state.KEY]['births'] + 1)
        mask = first[state.KEY]['wave_mask']
        assert torch.equal(second[state.KEY]['flip_pi'][mask], ~first[state.KEY]['flip_pi'][mask])
        assert (first[state.KEY]['flip_pi'][~mask] == False).all() and (second[state.KEY]['flip_pi'][~mask] == False).all()
        assert torch.equal(second['E1_terrain_state']['episode'], ck['E1_terrain_state']['episode'] + 2)
        negatives = []
        def rejected(name, action):
            try: action()
            except AssertionError: negatives.append(name)
            else: raise AssertionError('Incorrectly admitted ' + name)
        for key, wrong in [('approved_GPU', True), ('reinitialize_left_head', True), ('new_entry_pose', False),
                           ('new_BODY_direction_identity', False), ('new_RNG_draws', True), ('num_envs', 512),
                           ('initial_whole20k_source_SHA', '0' * 64)]:
            bad = dict(first_manifest); bad[key] = wrong
            rejected('CPU_manifest_' + key, lambda bad=bad: checkpoint.guard_manifest(bad, True))
        rejected('CPU_template_cannot_enter_actual_GPU_path', lambda: checkpoint.guard_manifest(first_manifest, False))
        assert component.tree_hash(ck) == before and checkpoint.sha(p) == state.SOURCE
        assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
        report = dict(epoch=time.time(), passed_CPU_restore_save_resume_composition=True,
            actual_whole20k_source_SHA=state.SOURCE, actual_source_all19510799_unchanged=True,
            two_new_physical_births_in_two_independent_CPU_fixtures_only=True,
            first_transition_old_restore_before_adapter=True, same_new_scope_predecessor_restored_before_binding=True,
            no_extra_reset_or_DR_draw_calls_by_new_adapter=True, old_initializer_never_repeated=True,
            old_actor_critic_std_Adam_and_initialization_metadata_exact=True,
            selected_new_direction_and_entry_identity_declared=True,
            first_and_second_per_env_pi_alternation_exact=True,
            fixture_startup_files_not_accepted_as_actual_GPU_proofs=True,
            actual_13_GPU_CUDA_receipt_validation_not_claimed=True,
            CPU_fixture_checkpoint_forbidden_in_production=True,
            fixture_files=[dict(path=str(x), bytes=x.stat().st_size, sha256=checkpoint.sha(x)) for x in (first_path, second_path)],
            actual_typed13_schema_source=dict(path=str(typed_source), sha256=checkpoint.sha(typed_source)),
            negatives_rejected=negatives, CPU_RNG_unchanged=True, no_CUDA_GPU_PPO_or_budget=True,
            source_SHA={str(x.relative_to(B)): checkpoint.sha(x) for x in (B / 'payload_v1').glob('*.py')},
            reader_SHA=checkpoint.sha(__file__),
            limits='Synthetic CPU original-restore callback uses actual source structure and bank; original PhysX/fullD0D7 restore has not run for the new scope. Own new native ABI/resource/fullstate admission and typed actual13+body14 proof still required.',
            Git_pending=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
        print(json.dumps(dict(passed_CPU_composition=True, actual_N20000=True, first_and_own_resume_tested=True,
                              original_source_unchanged=True, negatives=len(negatives), actual_GPU_PPO_admitted=False)))
    except BaseException:
        (reports / ('BODYFRAME_RESTORE_COMPOSITION_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).write_text(
            json.dumps(dict(epoch=time.time(), error=traceback.format_exc(), reader_SHA=checkpoint.sha(__file__),
                            source_SHA={str(x.relative_to(B)): checkpoint.sha(x) for x in (B / 'payload_v1').glob('*.py')},
                            original_source_unchanged=True, no_GPU_PPO_or_budget=True, Git_pending=True), indent=2), encoding='utf8')
        raise


if __name__ == '__main__':
    main()
