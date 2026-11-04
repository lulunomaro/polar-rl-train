"""STDLIB-ONLY FAKE, not Isaac/torch, physical evidence or numerical parity.

It exposes the same cache/argument lifecycle needed to test the passive wrapper.
Only this fixture may generate randomness/observations or drive a fake step.
"""
from collections import Counter
import random
from types import SimpleNamespace
from source_api import CHANNELS, SCALES


def copy(value):
    if isinstance(value, dict):
        return {k: copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [copy(v) for v in value]
    if isinstance(value, tuple):
        return tuple(copy(v) for v in value)
    return value


class SensorCorruption:
    def __init__(self, n, seed=31, profile='noise_bias_mild_v1'):
        self.n, self.profile = n, profile
        self.cache = {}
        self.bias = [[0.] * 4 for _ in range(n)]
        self.episode = [0] * n
        self.draw_counts = {k: 0 for k in CHANNELS}
        self.rng = {key: random.Random(seed + i) for i, key in enumerate(CHANNELS)}
        self.bias_rng = random.Random(seed + 9000)
        self.batch_draws = Counter()
        self.calls = Counter()
        self.last_return = None

    def reset(self, ids):
        self.calls['reset'] += 1
        for row in ids:
            self.bias[row] = [self.bias_rng.uniform(-.0075, .0075) if self.profile != 'off' else 0. for _ in range(4)]
            self.episode[row] += 1
            for last, _ in self.cache.values():
                last[row] = -1
        return None

    def apply(self, key, value, tick):
        self.calls['apply'] += 1
        assert key in CHANNELS
        assert len(value) == self.n and all(len(row) == CHANNELS[key] for row in value)
        if self.profile == 'off':
            self.last_return = value
            return value
        if key not in self.cache:
            self.cache[key] = ([-1] * self.n, [[0.] * CHANNELS[key] for _ in range(self.n)])
        last, noise = self.cache[key]
        due = [i for i in range(self.n) if last[i] != int(tick)]
        if due:
            self.batch_draws[key] += 1
            for i in due:
                noise[i] = [self.rng[key].uniform(-.125, .125) for _ in range(CHANNELS[key])]
                last[i] = int(tick)
            self.draw_counts[key] += len(due)
        out = [[v + noise[i][j] + (self.bias[i][j] if key == 'leg_pos' else 0.)
                for j, v in enumerate(row)] for i, row in enumerate(value)]
        self.last_return = out
        return out

    def evidence(self):
        return dict(bias=copy(self.bias), episode=self.episode[:], cache=copy(self.cache),
                    draws=dict(self.draw_counts), batches=dict(self.batch_draws),
                    calls=dict(self.calls), rng={k: r.getstate() for k, r in self.rng.items()},
                    bias_rng=self.bias_rng.getstate())


class FeedbackDelay:
    def __init__(self, n, seed=888, enabled=True):
        self.n, self.enabled = n, enabled
        self.delay = [i % 2 for i in range(n)]
        self.episode = [0] * n
        self.cache = {}
        self.rng = random.Random(seed)
        self.calls = Counter()
        self.last_return = None

    def reset(self, ids):
        self.calls['reset'] += 1
        for i in ids:
            self.delay[i] = self.rng.randrange(2) if self.enabled else 0
            self.episode[i] += 1
            for cache in self.cache.values():
                cache['last'][i] = cache['sample_tick'][i] = -1
                cache['ready'][i] = False
        return None

    def apply(self, key, x, tick):
        self.calls['apply'] += 1
        assert key in CHANNELS
        if not self.enabled:
            self.last_return = x
            return x
        if key not in self.cache:
            self.cache[key] = dict(last=[-1] * self.n,
                cur=[[0.] * CHANNELS[key] for _ in range(self.n)],
                out=[[0.] * CHANNELS[key] for _ in range(self.n)],
                sample_tick=[-1] * self.n, ready=[False] * self.n)
        cache = self.cache[key]
        due = [i for i in range(self.n) if cache['last'][i] != tick]
        for i in due:
            old = cache['last'][i]
            initial = old < 0
            assert initial or old == tick - 1, 'Skipped/reversed feedback sample clock'
        for i in due:
            old = cache['last'][i]
            initial = old < 0
            delayed = self.delay[i] == 1 and not initial
            cache['out'][i] = cache['cur'][i][:] if delayed else x[i][:]
            cache['cur'][i] = x[i][:]
            cache['sample_tick'][i] = old if delayed else tick
            cache['last'][i] = tick
            cache['ready'][i] = not initial
        out = copy(cache['out'])
        self.last_return = out
        return out

    def evidence(self):
        return dict(delay=self.delay[:], episode=self.episode[:], cache=copy(self.cache),
                    calls=dict(self.calls), rng=self.rng.getstate())


def feedback(env, key, raw):
    env.counts['feedback'] += 1
    tick = getattr(env, '_feedback_100hz_tick', env.common_step_counter)
    noisy = env._sensor_mild.apply(key, raw, tick)
    return env._feedback_delay_mild.apply(key, noisy, tick)


def term(env, key):
    # The original fixture caller already computes raw before entering feedback.
    return feedback(env, key, env.original_raw_getter(key))


class FakeEnv:
    def __init__(self, n=3):
        self.num_envs = n
        self._sim_step_counter = self.common_step_counter = self._feedback_100hz_tick = 0
        self._physics_handles_decimation = False
        self._sensor_mild = SensorCorruption(n)
        self._feedback_delay_mild = FeedbackDelay(n)
        self.counts = Counter()
        self.physical_episode = [0] * n
        self.action_queue = []
        self.last_action = [0.] * 6
        self.scene = SimpleNamespace(update=self.original_scene_update)
        self.termination_manager = SimpleNamespace(compute=self.original_terminal,
            terminated=[False] * n, time_outs=[False] * n)
        self._install_feedback_100hz_sampling()
        self.last_step_return = None

    def original_scene_update(self, dt):
        self.counts['scene_update'] += 1
        return None

    def _install_feedback_100hz_sampling(self):
        previous = self.scene.update
        def update(dt):
            previous(dt)
            tick = int(self._sim_step_counter)
            if tick % 4 == 0:
                self._feedback_100hz_tick = tick // 4
                for key in CHANNELS:
                    term(self, key)
        self.scene.update = update

    def original_raw_getter(self, key):
        self.counts['raw_getter'] += 1
        return [[self._sim_step_counter * .3 + i * .7 + self.physical_episode[i] * 100 + j * .02
                 for j in range(CHANNELS[key])] for i in range(self.num_envs)]

    def original_terminal(self):
        self.counts['terminal'] += 1
        return self.termination_manager.terminated

    def _reset_idx(self, ids):
        self.counts['reset'] += 1
        self._sensor_mild.reset(ids)
        self._feedback_delay_mild.reset(ids)
        for i in ids:
            self.physical_episode[i] += 1
        return None

    def observe(self):
        self.counts['observe'] += 1
        values = {key: term(self, key) for key in CHANNELS}
        # FAKE35 only: 16 observed feedback plus 19 unchanged fixture channels.
        return [[v * SCALES[key] for key in CHANNELS for v in values[key][i]]
                + [float(self.common_step_counter)] * 19 for i in range(self.num_envs)]

    def step(self, action, terminal_ids=()):
        self.counts['step'] += 1
        self.last_action = list(action)
        self.action_queue.append(list(action))
        self.action_queue = self.action_queue[-2:]
        for _ in range(8):
            self._sim_step_counter += 1
            self.scene.update(.0025)
        self.common_step_counter += 1
        self.termination_manager.terminated[:] = [i in terminal_ids for i in range(self.num_envs)]
        result = self.termination_manager.compute()
        assert result is self.termination_manager.terminated
        if terminal_ids:
            self._reset_idx(list(terminal_ids))
        obs = self.observe()
        self.last_step_return = (obs, [1.] * self.num_envs, self.termination_manager.terminated, {})
        return self.last_step_return

    def evidence(self):
        return dict(sensor=self._sensor_mild.evidence(), delay=self._feedback_delay_mild.evidence(),
                    counts=dict(self.counts), physics=self._sim_step_counter,
                    feedback_tick=self._feedback_100hz_tick, control=self.common_step_counter,
                    action_queue=copy(self.action_queue), physical_episode=self.physical_episode[:])


class FakeBridge:
    def __init__(self, env):
        self.real = env
        self._oldterm = env.termination_manager.compute
        self.pre = None
        self.pack_calls = self.capture_calls = 0
        env.termination_manager.compute = self._termination_capture

    def pack(self):
        self.pack_calls += 1
        return dict(tick=self.real._sim_step_counter,
                    physical_episode=self.real.physical_episode[:])

    def _termination_capture(self, *a, **k):
        self.capture_calls += 1
        out = self._oldterm(*a, **k)
        tm = self.real.termination_manager
        self.pre = dict(s1=self.pack(), term=tm.terminated[:], trunc=tm.time_outs[:])
        return out
