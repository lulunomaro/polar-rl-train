"""Optional sampled-start accounting per Pi call, not per physical control.

This records attempted imagination starts, never successful optimizer updates or
physical task events. It preserves original sampling/actions/reward and RNG.
"""
from pathlib import Path
import json
import math


class NativePolicyPhaseCoverage:
    def __init__(self, path, *, window_start_iteration):
        self.path = Path(path)
        self.window_start_iteration = int(window_start_iteration)
        self.calls = 0
        self.samples = 0
        self.bands = [0, 0, 0, 0, 0]
        self.reaches_request = 0
        self.errors = []
        self.valid = True
        self.last = None
        self.io_errors = []

    @staticmethod
    def _counts(frames, horizon):
        if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 1:
            raise ValueError('invalid imagination horizon')
        bands = [0, 0, 0, 0, 0]
        reaches = 0
        for frame in frames:
            if isinstance(frame, bool) or not isinstance(frame, (int, float)) or not math.isfinite(frame) or int(frame) != frame or frame < 0:
                raise ValueError('invalid sampled frame')
            value = int(frame)
            index = 0 if value < 50 else 1 if value < 100 else 2 if value < 136 else 3 if value < 180 else 4
            bands[index] += 1
            reaches += int(value + horizon >= 100 and value + 1 < 180)
        return bands, reaches

    def snapshot(self):
        return dict(schema='mod4.native.sampled_policy_phase_coverage.v1',
                    diagnostic_valid=self.valid, window_start_iteration=self.window_start_iteration,
                    policy_sampling_calls=self.calls, sampled_starts=self.samples,
                    bands=dict(zip(('before50', '50to99', '100to135', '136to179', '180plus'), self.bands)),
                    imagined_horizon_intersects_request=self.reaches_request,
                    last=self.last, errors=list(self.errors), io_errors=list(self.io_errors),
                    counts_attempted_starts_not_completed_optimizer_updates=True,
                    not_a_training_or_model_or_skill_gate=True,
                    extra_GPU_transfer_only_once_per_policy_sampling_call_not_per_control=True,
                    no_sampling_distribution_action_reward_or_RNG_changes=True)

    def _persist(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(self.path.suffix + '.partial')
            temporary.write_text(json.dumps(self.snapshot(), indent=2), encoding='utf8')
            temporary.replace(self.path)
        except Exception as error:
            # Optional I/O is never allowed to hide a physical/optimizer failure.
            self.io_errors.append(type(error).__name__ + ': ' + str(error))
            self.io_errors[:] = self.io_errors[-8:]

    def note_error(self, error):
        self.valid = False
        self.errors.append(type(error).__name__ + ': ' + str(error))
        self.errors[:] = self.errors[-8:]
        self._persist()

    def record(self, frames, *, iteration, horizon):
        try:
            bands, reaches = self._counts(frames, horizon)
            if iteration < self.window_start_iteration:
                raise ValueError('iteration regressed before window start')
            self.calls += 1
            self.samples += len(frames)
            self.bands = [a + b for a, b in zip(self.bands, bands)]
            self.reaches_request += reaches
            self.last = dict(iteration=int(iteration), count=len(frames), min=min(frames) if frames else None,
                             max=max(frames) if frames else None, bands=bands, horizon=int(horizon))
            self._persist()
        except Exception as error:
            self.note_error(error)


def attach_optional_policy_phase_coverage(learner, path):
    """Wrap only the existing sample result, with identical object forwarding.

    Original exceptions escape unchanged. The additional frame transfer occurs
    only when Pi requests its existing start sample, outside physical controls.
    It is optional instrumentation with its own truthful invalid/error state.
    """
    if hasattr(learner, '_mod4_native_phase_coverage'):
        raise ValueError('phase coverage already attached')
    original = learner._sample_valid_starts
    diagnostic = NativePolicyPhaseCoverage(path, window_start_iteration=learner.iteration)

    def sample(batch_size):
        result = original(batch_size)
        try:
            frames = result[0]['f'].detach().cpu().tolist()
            diagnostic.record(frames, iteration=int(learner.iteration), horizon=int(learner.cfg.horizon))
        except Exception as error:
            diagnostic.note_error(error)
        return result

    learner._sample_valid_starts = sample
    learner._mod4_native_phase_coverage = diagnostic
    return diagnostic
