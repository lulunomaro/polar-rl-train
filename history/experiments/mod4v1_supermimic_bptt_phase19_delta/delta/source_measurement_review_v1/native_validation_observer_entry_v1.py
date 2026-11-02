"""Independent FUTURE native validation entry, not installed into active sources.

No environment, bridge, SDK, tensor library, checkpoint or process is imported.
The future owner calls submit() with detached scalar copies and real boundaries.
No step/resample/reset/update method is invoked or replaced by this module.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from observer_uid_ledger_v1 import (Capture, Command, ExclusiveJsonlSink,
                                   MeasurementObserver, Provenance)


class NativeValidationObserverEntry:
    def __init__(self, provenance: Provenance, new_ledger_path: Optional[str | Path] = None,
                 maximum_ledger_bytes: Optional[int] = None):
        self.writer = ExclusiveJsonlSink(new_ledger_path, maximum_ledger_bytes) if new_ledger_path is not None else None
        self.observer = MeasurementObserver(provenance, self.writer)
        self.finished = False

    def submit(self, event: dict[str, Any]) -> None:
        """Dispatch copied facts in original order; no live object arguments.

        Kinds:
          initial_packet: tick, command, exact_initial_packet_verified
          before_control: command, capture(stage=before_control)
          pre_reset_endpoint: capture(stage=after_control_pre_reset),
                              terminated, truncated, reason_masks/timeout_flags
          resample_before: tick, timer_before, within_reset
          resample_after: tick, command
          reset_before: tick
        All events require env_id. Unknown fields are errors, not ignored facts.
        """
        if self.finished:
            raise ValueError("Observer entry is closed")
        e = dict(event)
        kind, env_id = e.pop("kind"), e.pop("env_id")
        if kind == "initial_packet":
            e["command"] = Command(**e["command"])
            self.observer.initial_packet(env_id, **e)
        elif kind == "before_control":
            command, capture = Command(**e.pop("command")), Capture(**e.pop("capture"))
            if e:
                raise TypeError("Unexpected before_control event fields: " + str(sorted(e)))
            self.observer.begin(env_id, command, capture)
        elif kind == "pre_reset_endpoint":
            capture = Capture(**e.pop("capture"))
            self.observer.endpoint(env_id, capture, **e)
        elif kind == "resample_before":
            self.observer.resample_before(env_id, **e)
        elif kind == "resample_after":
            e["command"] = Command(**e["command"])
            self.observer.resample_after(env_id, **e)
        elif kind == "reset_before":
            self.observer.reset_before(env_id, **e)
        else:
            raise ValueError("Unknown explicit native observer event: " + str(kind))

    def finish(self) -> dict[str, Any]:
        if self.finished:
            raise ValueError("Observer entry is already closed")
        summary = self.observer.finish()
        self.finished = True
        summary["ledger"] = self.writer.finish() if self.writer is not None else None
        summary["independent_entry_only_no_active_source_patch"] = True
        return summary


def describe_future_call_sites() -> dict[str, Any]:
    return {
        "entry": "NativeValidationObserverEntry.submit(event)",
        "before_control": "Future validation owner before native real.step; original body command, root_pos_w/heading_w clones, event UIDs and both clocks",
        "pre_reset_endpoint": "Future owner after original termination compute and before any reset/resample; E2 original root_pos_w/heading_w, W35 original frame[root] xyzw, tm masks/reasons; not post-reset BridgeState.s",
        "resample_before": "Before ORIGINAL command resampler, original timer and reset nesting captured; close OLD UID before command writes",
        "resample_after": "After ORIGINAL sampler returns, capture sampled body/heading/standing/counter and increment observer command UID exactly once",
        "reset_before": "Before ORIGINAL reset, close old span and increment episode UID; preserve nested reset/resample order",
        "initial_packet": "W35 only known-start if exact original reset packet, tick=0, all-env ids, command/timer equality verified by future owner; otherwise false",
        "prohibited_by_design": ["automatic hook installation", "training bridge mutation", "extra env.step", "extra observation/reward/RNG/sampler/update", "checkpoint or old JSONL reads"],
        "runtime_points_validated": None,
        "actual_frozen_result": None,
    }
