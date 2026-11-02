"""Make ONLY NEW fixture V2; V1 adapter/fixture byte pins must remain exact."""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old_path = HERE / 'remote_cpu_embedded_teacher_synthetic_v1.py'
raw = old_path.read_bytes()
assert len(raw) == 11051 and hashlib.sha256(raw).hexdigest() == 'aa982495175d694b8327a545d4291f4bc8f0760d8a18df0fe0234c2d44a78d83'
adapter = (HERE / 'embedded_teacher_reference_v1.py').read_bytes()
assert len(adapter) == 16333 and hashlib.sha256(adapter).hexdigest() == '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'
old = raw.decode('utf-8')
start = old.index('    assert std_names and norm_names,')
end = old.index('    assert t.equal(before, t.get_rng_state()), \'negative tests consumed caller RNG\'')
new_block = '''    # Actual approved MLPModel legitimately has identity normalization and no
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
'''
new = old[:start] + new_block + old[end:]
new = new.replace('OWN_SYNTHETIC_CPU_TORCH_EMBEDDED_TEACHER_REFERENCE_NOT_NATIVE_EVAL_V1',
                  'OWN_SYNTHETIC_CPU_TORCH_EMBEDDED_TEACHER_REFERENCE_NOT_NATIVE_EVAL_V2')
new = new.replace('        mutated_buffer_name=buffer_name, mutated_std_name=std_name,\n        teacher_buffer_mutation_detected=buffer_mutation_detected, teacher_std_value_mutation_detected=std_value_mutation_detected,',
'''        actual_teacher_state_keys=teacher_state_keys, teacher_normalization=teacher_normalization,
        teacher_buffer_case=teacher_buffer_case, teacher_buffer_mutation_detected=teacher_buffer_mutation_detected,
        mutated_std_name=std_name, teacher_std_value_mutation_detected=std_value_mutation_detected,
        std_full_value_error=std_value_error, std_original_frozen_guard_detected=std_original_frozen_guard_detected,
        std_original_guard_error=std_original_guard_error,
        residual_buffer_case=dict(mutated_name='residual.obs_norm.mean', isolated=True,
            detected=residual_buffer_mutation_detected, error=residual_buffer_error),
        isolated_negative_cache_receipts=negative_cache_receipts,''')
new = new.replace('REMOTE_CPU_EMBEDDED_TEACHER_RESULTS_V1.json', 'REMOTE_CPU_EMBEDDED_TEACHER_RESULTS_V2.json')
new = new.replace('"""FUTURE parent-run CPU/Torch fixture; source review never executes this file.',
                  '"""NEW V2 parent-run CPU fixture: actual optional teacher norm/buffer schema.')
assert 'assert std_names and norm_names' not in new and 'buffer_mutation_detected=buffer_mutation_detected' not in new
compile(new, 'remote_cpu_embedded_teacher_synthetic_v2.py', 'exec')
with (HERE / 'remote_cpu_embedded_teacher_synthetic_v2.py').open('x', encoding='utf-8') as stream: stream.write(new)
with (HERE / 'REMOTE_CPU_FIXTURE_V1_TO_V2.patch').open('x', encoding='utf-8') as stream:
    stream.write(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile='remote_cpu_embedded_teacher_synthetic_v1.py', tofile='remote_cpu_embedded_teacher_synthetic_v2.py')))
new_raw = (HERE / 'remote_cpu_embedded_teacher_synthetic_v2.py').read_bytes()
result = dict(kind='NEW_FIXTURE_V2_ONLY_NO_REFERENCE_ALGORITHM_CHANGE', passed_source_compile=True,
    new_fixture=dict(file='remote_cpu_embedded_teacher_synthetic_v2.py', bytes=len(new_raw), SHA256=hashlib.sha256(new_raw).hexdigest()),
    old_adapter_and_fixture_exact_PIN_unchanged=True, Torch_imported=False, actual_CPU_Torch_execution=None)
with (HERE / 'BUILD_CPU_FIXTURE_V2.json').open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2); stream.write('\n')
print(json.dumps(result, indent=2))
