"""NEW V2 parent-run CPU fixture: actual optional teacher norm/buffer schema.

Standalone NEW synthetic root only. No input-checkpoint argument, old model read,
SDK/native env, GPU, optimizer/replay restoration, subprocess or admission logic.
Use original reviewed frozen_a1_raw35_v1 + bridge/vendor/RSL on PYTHONPATH.
"""
import argparse
import hashlib
import json
from pathlib import Path
import embedded_teacher_reference_v1 as r
import frozen_a1_raw35_v1 as h
from a1_frozen_eval_runtime_v2 import OriginalEpisodeBoundary


def run(new_output):
    output = Path(new_output).resolve()
    h.need(not output.exists(), 'fresh own synthetic CPU output required')
    output.mkdir(parents=True)
    m = h._runtime_modules(); t = m.t  # Only THIS future parent-run fixture imports Torch.
    before = t.get_rng_state().clone()
    with t.inference_mode(False), t.no_grad(), t.random.fork_rng(devices=[]):
        t.manual_seed(1714)
        obs = m.TD(dict(policy=t.zeros(2, 35), critic=t.zeros(2, 38)), batch_size=[2])
        distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
        teacher = m.MLP(obs, dict(actor=['policy'], critic=['critic']), 'actor', 6, [256, 128, 64], 'elu', distribution_cfg=distribution)
        original = m.Wrapper(m.Policy(35, 3, hist=10, z_dim=32, num_joints=6, hidden=(512, 256, 128)), teacher, 0, scale=.05)
        original.residual.dec[-1].weight.fill_(.02)
        original.residual.dec[-1].bias.copy_(t.tensor([1., -1., 2., -2., 3., -3.]))
        original.obs_norm.mean.copy_(t.linspace(-.2, .2, 35)); original.obs_norm.var.fill_(.7); original.obs_norm.count.fill_(123.)
        original.goal_norm.mean.copy_(t.tensor([.1, .2, -.3])); original.goal_norm.var.fill_(.4); original.goal_norm.count.fill_(81.)
        original.eval().requires_grad_(False)
    assert t.equal(before, t.get_rng_state()), 'synthetic construction advanced caller RNG'
    teacher_snapshot = {k: v.detach().clone() for k, v in teacher.state_dict().items()}
    def original_teacher_unchanged():
        current = teacher.state_dict()
        assert set(current) == set(teacher_snapshot)
        assert all(t.equal(current[k], v) for k, v in teacher_snapshot.items())
        assert all(not p.requires_grad for p in teacher.parameters())
    counts = {k: 0 for k in h.COUNT_FIELDS}
    counts.update(policy_attempts=25, pi_optimizer_steps=24, pi_bptt_optimizer_steps=24, wm_optimizer_steps=40)
    bootstrap = dict(source_path='/OWN_SYNTHETIC_NEVER_OPENED_MOTHER.pt', source_SHA='a' * 64, source_bytes=1, teacher_frozen=True)
    provenance = dict(role='E3', role_key='OWN_SYNTHETIC_REFERENCE_ROLE', run_id='OWN_SYNTHETIC_REFERENCE_CPU',
                      actor_view=h.VIEW, algorithm_family=h.FAMILY, algorithm_variant='A1_RAW35_FRESH')
    root = dict(**provenance, pi=original.state_dict(), wm={'UNUSED': t.tensor([float('nan')])}, critic={},
        opt_wm={}, opt_pi={}, opt_v={}, iteration=24, new_algorithm_not_PPO_resume=True, asset_SHA='b' * 64, contract_SHA='c' * 64,
        bootstrap_teacher=bootstrap,
        args=dict(hist=10, z_dim=32, goal_frames=1, policy_hidden=(512, 256, 128), test_hidden_dims=None, amp='none', buffer_steps=128),
        context_reward_extension=dict(full_resume=True, counts=counts, aux={'UNUSED': t.zeros(2)}, opt_aux={},
            replay=dict(T=128, N=1024, data={}), obs_hist=t.zeros(1024, 10, 35),
            rng={'torch_cpu': t.get_rng_state(), 'python': ('NOT_RESTORED',)}, environment={'NOT_RESTORED': True},
            contract=dict(schema='mod4v1.ctx_task_reward.v1', num_joints=30, action_dim=6, obs_dim=35,
                          goal_frame_dim=3, context_dim=500, num_envs=1024, policy_dt_s=.02)))
    path = output / 'production/checkpoints/own_synthetic_000024_complete.pt'; path.parent.mkdir(parents=True)
    original_teacher_unchanged(); t.save(root, path)
    # The synthetic producer hashes its own newly-created file. Tested cache
    # subsequently performs exactly ONE own read/hash/CPU decode, not a mother read.
    raw = path.read_bytes()
    cp = dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(), iteration=24, counts=counts,
              teacher_source=bootstrap, teacher_unchanged=True, full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    original_teacher_unchanged()
    final = dict(**provenance, kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', passed_execution=True,
                 teacher_unchanged=True, counts=counts, actual_BPTT_policy_steps=24, checkpoint=cp, teacher=bootstrap)
    cache = h.FrozenA1CheckpointCache(final, own_job_root=output, role='E3', role_key=provenance['role_key'],
                                    run_id=provenance['run_id'], asset_SHA='b' * 64, contract_SHA='c' * 64)
    mean = cache.build_mean_policy('cpu', num_envs=80)
    own_source = Path(__file__).resolve(); own_bytes = own_source.read_bytes()
    guard = dict(kind=r.FREEZE_EVIDENCE_KIND, role='E3', role_key=provenance['role_key'], run_id=provenance['run_id'],
        source_A1_SHA=cp['SHA'], actual_staged_worker_source=dict(path=str(own_source), bytes=len(own_bytes), SHA256=hashlib.sha256(own_bytes).hexdigest()),
        parent_verified_actual_staged_source=True, state_dict_snapshot_all_parameters_and_buffers=True,
        torch_equal_before_each_complete_save=True, torch_equal_before_success_FINAL=True,
        producer_success_FINAL_and_checkpoint_teacher_unchanged=True,
        synthetic_only=True, source_kind='OWN_SYNTHETIC_CPU_FIXTURE_NOT_ACTUAL_TRAINING_PRODUCER')
    reference = r.EmbeddedTeacherMeanReference(mean, tensor_dict_cls=m.TD, producer_final=final,
                                             expected_rsl_source=r.APPROVED_RSL, producer_freeze_evidence=guard)
    caller = r.EmbeddedTeacherReferenceCaller(reference, boundary=OriginalEpisodeBoundary(t, mean.device))
    generator = t.Generator(device='cpu'); generator.manual_seed(183)
    history = t.zeros(80, 10, 35); maximum_teacher_error = 0.; maximum_candidate_teacher_difference = 0.
    for step in range(4):
        raw35 = t.randn(80, 35, generator=generator)
        start = caller.boundary.next_start.clone()
        with t.inference_mode():
            shifted = t.cat((history[:, 1:], raw35.unsqueeze(1)), 1)
            history = t.where(start[:, None, None], raw35.unsqueeze(1).expand_as(history), shifted)
            # Independent original RSL object/software math, NOT paired physics.
            expected_teacher = original.teacher(m.TD(dict(policy=raw35), batch_size=[80]), stochastic_output=False).clamp(-6., 6.)
            expected_candidate = original(history, raw35[:, :3]).clamp(-6., 6.)
        actual = caller(m.TD(dict(policy=raw35), batch_size=[80]), stochastic_output=False)
        err = float((actual - expected_teacher).abs().max()); maximum_teacher_error = max(maximum_teacher_error, err)
        assert t.allclose(actual, expected_teacher, rtol=1e-6, atol=1e-6), 'embedded teacher differs from original RSL mean'
        maximum_candidate_teacher_difference = max(maximum_candidate_teacher_difference, float((actual - expected_candidate).abs().max()))
        term, trunc = t.zeros(80, dtype=t.bool), t.zeros(80, dtype=t.bool)
        if step == 1: term[0] = True; trunc[1] = True
        caller.observe_transition(term, trunc)
        assert mean.calls == 0 and mean._history is None, 'reference called candidate/history'
    assert maximum_candidate_teacher_difference > 0., 'fixture residual did not discriminate candidate from teacher'
    assert t.equal(before, t.get_rng_state()), 'reference consumed/restored caller RNG'
    receipt = caller.receipt()
    semantic = r.validate_reference_semantics(receipt, expected_role='E3', expected_source_sha=cp['SHA'],
                                              expected_bootstrap_teacher_sha=bootstrap['source_SHA'], expected_actor_calls=4)
    assert receipt['source_cache']['physical_byte_opens'] == receipt['source_cache']['SHA_calculations'] == receipt['source_cache']['CPU_decodes'] == 1
    state = mean.pi.teacher.state_dict()
    std_names = [k for k in state if 'std' in k.lower()]
    norm_names = [k for k in state if 'norm' in k.lower()]
    # Actual approved MLPModel legitimately has identity normalization and no
    # persistent teacher norm state. Compare ALL actual keys; never add a layer.
    assert std_names, ('original teacher std state missing', list(state))
    teacher_state_keys = list(state)
    teacher_normalization = ('persistent_teacher_norm_state_present' if norm_names else
                             'identity_no_persistent_teacher_norm_state_observed')

    def fresh_negative_reference(tag):
        # build_mean_policy is deliberately one-shot per cache. Never rearm it.
        # Each isolated negative serializes THIS own synthetic root to a distinct
        # NEW case and builds ONE fresh own cache; no old model/PT is reopened.
        case = output / ('ISOLATED_OWN_SYNTHETIC_NEGATIVE_' + tag)
        dest = case / 'production/checkpoints/own_synthetic_negative_complete.pt'
        dest.parent.mkdir(parents=True)
        original_teacher_unchanged(); t.save(root, dest)
        data = dest.read_bytes()
        checkpoint = dict(cp, path=str(dest), bytes=len(data), SHA=hashlib.sha256(data).hexdigest())
        case_final = dict(final, checkpoint=checkpoint)
        case_cache = h.FrozenA1CheckpointCache(case_final, own_job_root=case, role='E3',
            role_key=provenance['role_key'], run_id=provenance['run_id'], asset_SHA='b' * 64, contract_SHA='c' * 64)
        case_mean = case_cache.build_mean_policy('cpu', num_envs=80)
        case_guard = dict(guard, source_A1_SHA=checkpoint['SHA'])
        case_reference = r.EmbeddedTeacherMeanReference(case_mean, tensor_dict_cls=m.TD,
            producer_final=case_final, expected_rsl_source=r.APPROVED_RSL, producer_freeze_evidence=case_guard)
        case_reference.assert_frozen()
        return case_reference, case_cache.receipt()

    # STD is the FIRST mutation. Require the exact full-value comparator error,
    # then separately prove the original mean guard fails before sticky state.
    assert reference._failed is False
    reference.assert_frozen()
    std_name = std_names[0]
    with t.no_grad(): state[std_name].add_(.25)
    try: reference._compare_full_teacher_state()
    except ValueError as exc:
        assert str(exc) == 'full embedded teacher value differs: ' + std_name, str(exc)
        std_value_mutation_detected = True
        std_value_error = str(exc)
    else: raise AssertionError('teacher std mutation escaped full cached pi comparison')
    assert reference._failed is False, 'std full-value comparison unexpectedly used sticky failure'
    try: reference.act(t.zeros(80, 35), episode_start=t.zeros(80, dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' not in str(exc), str(exc)
        std_original_frozen_guard_detected = True
        std_original_guard_error = str(exc)
    else: raise AssertionError('teacher std mutation escaped original whole-mean frozen guard')
    assert reference._failed is True
    try: reference.act(t.zeros(80, 35), episode_start=t.zeros(80, dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' in str(exc), str(exc)
        sticky_failure = True
    else: raise AssertionError('reference continued after std frozen-state failure')

    # No teacher buffers in the observed identity-normalized schema => explicit
    # N/A, not a claimed teacher-buffer measurement. If present, isolate a case.
    buffer_candidates = [(k, v) for k, v in mean.pi.teacher.named_buffers()
                         if k in state and v.is_floating_point() and v.numel()]
    teacher_buffer_mutation_detected = None
    teacher_buffer_case = dict(status='not_applicable', reason='no_floating_persistent_teacher_buffer_in_actual_schema',
                               actual_teacher_state_keys=teacher_state_keys,
                               actual_teacher_named_buffers=[k for k, _ in mean.pi.teacher.named_buffers()])
    negative_cache_receipts = []
    if buffer_candidates:
        buffer_name = buffer_candidates[0][0]
        buf_reference, buf_cache_receipt = fresh_negative_reference('TEACHER_BUFFER')
        negative_cache_receipts.append(dict(case='teacher_buffer', cache=buf_cache_receipt))
        buf = dict(buf_reference.pi.named_buffers())[buffer_name]
        with t.no_grad(): buf.add_(.125)
        try: buf_reference._compare_full_teacher_state()
        except ValueError as exc:
            assert str(exc) == 'full embedded teacher value differs: ' + buffer_name, str(exc)
            teacher_buffer_mutation_detected = True
        else: raise AssertionError('isolated teacher buffer escaped full cached pi comparison')
        teacher_buffer_case = dict(status='measured_in_isolated_own_synthetic_case', mutated_name=buffer_name,
                                   actual_teacher_state_keys=teacher_state_keys)

    # Residual obs/goal norms DO have persistent buffers in the real original
    # wrapper. This tests the retained WHOLE-mean guard, NOT a teacher norm layer.
    norm_reference, norm_cache_receipt = fresh_negative_reference('RESIDUAL_OBS_NORM')
    negative_cache_receipts.append(dict(case='residual_obs_norm', cache=norm_cache_receipt))
    assert norm_reference._failed is False
    norm_reference.assert_frozen()
    with t.no_grad(): norm_reference.mean.pi.obs_norm.mean.add_(.125)
    try: norm_reference.act(t.zeros(80, 35), episode_start=t.ones(80, dtype=t.bool))
    except ValueError as exc:
        assert 'previously failed' not in str(exc), str(exc)
        residual_buffer_mutation_detected = True
        residual_buffer_error = str(exc)
    else: raise AssertionError('isolated residual obs norm escaped original whole-mean frozen guard')
    assert t.equal(before, t.get_rng_state()), 'negative tests consumed caller RNG'
    result = dict(kind='OWN_SYNTHETIC_CPU_TORCH_EMBEDDED_TEACHER_REFERENCE_NOT_NATIVE_EVAL_V2', passed=True,
        actual_training_producer_evidence=None, actual_frozen_reference_evaluation=None, actual_paired_environment_comparison=None,
        CPU_reference_controls=4, maximum_original_RSL_teacher_error=maximum_teacher_error,
        maximum_candidate_math_teacher_difference=maximum_candidate_teacher_difference,
        candidate_math_difference_is_not_skill_or_reward_effect=True,
        teacher_norm_state_names=norm_names, teacher_std_state_names=std_names,
        actual_teacher_state_keys=teacher_state_keys, teacher_normalization=teacher_normalization,
        teacher_buffer_case=teacher_buffer_case, teacher_buffer_mutation_detected=teacher_buffer_mutation_detected,
        mutated_std_name=std_name, teacher_std_value_mutation_detected=std_value_mutation_detected,
        std_full_value_error=std_value_error, std_original_frozen_guard_detected=std_original_frozen_guard_detected,
        std_original_guard_error=std_original_guard_error,
        residual_buffer_case=dict(mutated_name='residual.obs_norm.mean', isolated=True,
            detected=residual_buffer_mutation_detected, error=residual_buffer_error),
        isolated_negative_cache_receipts=negative_cache_receipts,
        sticky_failure_detected=sticky_failure, caller_RNG_unchanged=True, receipt_before_negative=receipt,
        source_bindings=m.source_bindings, policy_semantic=semantic,
        SDK_GPU_actual_original_PT_optimizer_or_native_operations=0)
    with (output / 'REMOTE_CPU_EMBEDDED_TEACHER_RESULTS_V2.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--new-output', required=True)
    run(parser.parse_args().new_output)
