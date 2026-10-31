"""In-memory teacher transition collector, called at natural runtime boundaries.

The caller supplies cached observations and the original PRE-RESET termination
snapshot. No SDK read, actor call, RNG, dynamics, reset, or file I/O occurs here.
"""
import torch
from expert_teacher_port189 import require, validate_measured_pair


def copy_fields(value):
    return {key: item.detach().clone() for key, item in value.items()}


class MeasuredTeacherCollector:
    def __init__(self, identity, *, maximum_pairs):
        require(isinstance(maximum_pairs, int) and maximum_pairs > 0,
                "Declared positive collection bound required")
        self.identity = identity
        self.maximum_pairs = maximum_pairs
        self._completed_count = 0
        self._pending = None
        self._pairs = []

    def begin_original_decision(self, before):
        require(self._pending is None, "Previous decision has no terminal endpoint")
        require(self._completed_count < self.maximum_pairs, "Declared collection bound reached")
        self._pending = copy_fields(before)

    def complete_before_reset(self, terminal):
        require(self._pending is not None, "No original decision to join")
        # Failed validation retains the pending decision for original error review.
        frozen_terminal = copy_fields(terminal)
        pair = validate_measured_pair(self.identity, self._pending, frozen_terminal)
        self._pairs.append(dict(identity=self.identity, before=self._pending,
                                terminal=frozen_terminal, native=pair))
        self._completed_count += 1
        self._pending = None

    def completed(self):
        return self._completed_count

    def finish(self):
        require(self._pending is None, "Unpaired final decision; not a complete dataset")
        require(bool(self._pairs), "No measured transitions")
        # Consumer ownership is explicit; caller must not substitute reset states.
        pairs = self._pairs
        self._pairs = []
        return pairs
