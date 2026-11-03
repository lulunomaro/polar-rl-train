"""Own stdlib-only N80 lifecycle fixture. No torch/SDK/physical evidence.

The inherited fake's RNG, sample and delay rules remain fake rules. This module
adds tensor-shaped owned objects and int32 original-entry reset IDs solely to
exercise the V3 codec call sites. It is never an admitted native environment.
"""
from copy import deepcopy
from fake_tensor import FakeTensor
import fake_runtime as original_fake


def plain(value):
    if isinstance(value, FakeTensor):
        return deepcopy(value.values)
    if type(value) is dict:
        return {key: plain(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return type(value)(plain(item) for item in value)
    return value


class TypedSensor(original_fake.SensorCorruption):
    def __init__(self, n):
        super().__init__(n)
        self.bias = FakeTensor(self.bias, 'torch.float32')
        self.episode = FakeTensor(self.episode, 'torch.int64')

    def apply(self, key, value, tick):
        out = super().apply(key, value, tick)
        if self.profile != 'off':
            last, noise = self.cache[key]
            if not isinstance(last, FakeTensor):
                self.cache[key] = (FakeTensor(last, 'torch.int64'), FakeTensor(noise, value.dtype))
            out = FakeTensor(plain(out), value.dtype)
        self.last_return = out
        return out


class TypedDelay(original_fake.FeedbackDelay):
    def __init__(self, n):
        super().__init__(n)
        self.delay = FakeTensor(self.delay, 'torch.int64')
        self.episode = FakeTensor(self.episode, 'torch.int64')

    def apply(self, key, x, tick):
        out = super().apply(key, x, tick)
        if self.enabled:
            cache = self.cache[key]
            for name, dtype in (('last', 'torch.int64'), ('sample_tick', 'torch.int64'),
                                ('ready', 'torch.bool'), ('cur', x.dtype), ('out', x.dtype)):
                if not isinstance(cache[name], FakeTensor):
                    cache[name] = FakeTensor(cache[name], dtype)
            out = FakeTensor(plain(out), x.dtype)
        self.last_return = out
        return out


class TypedEnv(original_fake.FakeEnv):
    def __init__(self):
        super().__init__(80)
        self._sensor_mild, self._feedback_delay_mild = TypedSensor(80), TypedDelay(80)
        self.termination_manager.terminated = FakeTensor([False] * 80, 'torch.bool')
        self.termination_manager.time_outs = FakeTensor([False] * 80, 'torch.bool')
        self.last_reset_ids = None
        self.last_reset_return = None
        self.reset_return = None

    def original_raw_getter(self, key):
        return FakeTensor(super().original_raw_getter(key), 'torch.float64')

    def observe(self):
        return FakeTensor(super().observe(), 'torch.float64')

    def _reset_idx(self, ids):
        self.last_reset_ids = ids
        super()._reset_idx(ids)
        self.last_reset_return = self.reset_return
        return self.last_reset_return

    def step(self, action, terminal_ids=(), trunc_ids=(), force_empty_callback=False):
        self.counts['step'] += 1
        self.last_action = list(action)
        self.action_queue.append(list(action))
        self.action_queue = self.action_queue[-2:]
        for _ in range(8):
            self._sim_step_counter += 1
            self.scene.update(.0025)
        self.common_step_counter += 1
        self.termination_manager.terminated[:] = [i in terminal_ids for i in range(80)]
        self.termination_manager.time_outs[:] = [i in trunc_ids for i in range(80)]
        result = self.termination_manager.compute()
        assert result is self.termination_manager.terminated
        # FAKE ORIGINAL process, not an observer-derived nonzero/mask.
        original_ids = sorted(set(terminal_ids) | set(trunc_ids))
        if original_ids or force_empty_callback:
            self._reset_idx(FakeTensor(original_ids, 'torch.int32'))
        actor = self.observe()
        self.last_step_return = (actor, [1.] * 80, self.termination_manager.terminated,
                                 self.termination_manager.time_outs, {})
        return self.last_step_return


class TypedBridge(original_fake.FakeBridge):
    def pack(self):
        self.pack_calls += 1
        return FakeTensor([[self.real._sim_step_counter, self.real.physical_episode[i], i]
                           for i in range(80)], 'torch.float64')

    def _termination_capture(self, *args, **kwargs):
        self.capture_calls += 1
        out = self._oldterm(*args, **kwargs)
        tm = self.real.termination_manager
        self.pre = dict(s1=self.pack(), term=tm.terminated.clone(), trunc=tm.time_outs.clone())
        return out
