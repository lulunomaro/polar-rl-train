"""OPTIONAL PARENT CPU FIXTURE. Not executed by the delegated child.

No target import/load/CLI/native/stager. Parent explicitly supplies its CPU
`torch` module and two already-loaded, reviewed original source classes. The
private tap attachment intentionally does NOT satisfy native preflight. This
checks the real CPU sensor/delay tensors, not Isaac, an actor or the plant.
"""
from collections import Counter
import fake_runtime as fake
from passive_capture import PassiveCapture, BoundedRecorder, tensor_snapshot_adapter


def run_cpu_reference_tap_fixture(torch, SensorCorruption, FeedbackDelay):
    if not hasattr(torch, 'Tensor'):
        raise ValueError('Parent must supply reviewed CPU torch module')
    n = 3
    baseline, observed = fake.FakeEnv(n), fake.FakeEnv(n)
    tracker = {}
    for label, env in (('baseline', baseline), ('observed', observed)):
        env._sensor_mild = SensorCorruption(n, 'cpu', 137, 'noise_bias_mild_v1')
        env._feedback_delay_mild = FeedbackDelay(n, 'cpu', 137, True)
        env._feedback_delay_mild.delay[:] = torch.tensor([0, 1, 1])
        state = dict(calls=Counter(), sensor_return=None, delay_return=None)
        tracker[label] = state
        original_s, original_d = env._sensor_mild.apply, env._feedback_delay_mild.apply
        def sensor(*args, _original=original_s, _state=state, **kwargs):
            _state['calls']['sensor'] += 1
            out = _original(*args, **kwargs)
            _state['sensor_return'] = out
            return out
        def delay(*args, _original=original_d, _state=state, **kwargs):
            _state['calls']['delay'] += 1
            out = _original(*args, **kwargs)
            _state['delay_return'] = out
            return out
        env._sensor_mild.apply, env._feedback_delay_mild.apply = sensor, delay
    bridge = fake.FakeBridge(observed)
    rec = BoundedRecorder(first=32, last=32, max_events=128)
    witness_ids = torch.tensor([0, 1, 2], dtype=torch.long, device='cpu')
    snapshot = tensor_snapshot_adapter(torch.Tensor, witness_ids, n)
    tap = PassiveCapture(observed, bridge, fake, rec, snapshot,
        {'kind': 'REAL_TORCH_CPU_CLASSES_IN_FAKE_CLOSURE_NOT_NATIVE_PREFLIGHT',
         'native_enabled': False, 'exact': False}).attach()
    global_rng = torch.get_rng_state().clone()  # fixture evidence only, not callback
    comparisons = 0
    identity_checks = 0
    def equal(a, b):
        if isinstance(a, torch.Tensor):
            return isinstance(b, torch.Tensor) and a.dtype == b.dtype and a.shape == b.shape and torch.equal(a, b)
        if isinstance(a, dict):
            return set(a) == set(b) and all(equal(a[k], b[k]) for k in a)
        if isinstance(a, (list, tuple)):
            return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
        return a == b
    try:
        # Two fresh100Hz sample ticks, then cache-hit/changed raw, partialreset
        # at the SAME tick followed by a fresh row, then the next fresh tick.
        for ordinal, tick in enumerate((1, 2, 2, 2, 3)):
            if ordinal == 3:
                for env in (baseline, observed):
                    env._reset_idx([1])
                    env._feedback_delay_mild.delay[1] = 1
            for env in (baseline, observed):
                env._sim_step_counter = tick * 4
                env._feedback_100hz_tick = tick
            outputs = {}
            for key, width in fake.CHANNELS.items():
                raw = torch.arange(n * width, dtype=torch.float32).reshape(n, width) * .03 + ordinal
                a = fake.feedback(baseline, key, raw)
                b = fake.feedback(observed, key, raw)
                assert equal(a, b), key
                assert b is tracker['observed']['delay_return']
                assert a is tracker['baseline']['delay_return']
                identity_checks += 2
                comparisons += 1
                outputs[key] = b
                assert equal(baseline._sensor_mild.state_dict(), observed._sensor_mild.state_dict())
                assert equal(baseline._feedback_delay_mild.state_dict(), observed._feedback_delay_mild.state_dict())
        assert tracker['baseline']['calls'] == tracker['observed']['calls'] == {'sensor': 25, 'delay': 25}
        assert torch.equal(global_rng, torch.get_rng_state())
        assert rec.capture_errors == 0
        result = dict(kind='OPTIONAL_REAL_TORCH_CPU_CLASS_PASSIVE_TAP_FIXTURE',
            source_only=True, native_enabled=False, exact=False,
            real_torch_CPU_classes_executed=True, SDK_executed=False,
            native_binding_preflight_executed=False, actor35_equality_test=False,
            bitwise_class_output_comparisons=comparisons, return_identity_checks=identity_checks,
            original_call_counts={k: dict(v['calls']) for k, v in tracker.items()},
            source_rng_and_queue_state_equal=True, global_torch_rng_unchanged=True,
            dtype='torch.float32', capture_errors=rec.capture_errors)
    finally:
        tap.close()
    return result
