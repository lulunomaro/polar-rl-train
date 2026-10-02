"""List TensorBoard scalar tags for a run directory (optionally with the last value).

Usage:
    python scripts/tb_tags.py <logdir>
    python scripts/tb_tags.py <logdir> --last
    python scripts/tb_tags.py <logdir> --last --grep lr
"""
from __future__ import annotations

import glob
import os
import sys

from tensorboard.backend.event_processing import event_accumulator


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    logdir = argv[1]
    want_last = "--last" in argv
    needle = argv[argv.index("--grep") + 1] if "--grep" in argv else None
    series = argv[argv.index("--series") + 1] if "--series" in argv else None

    files = sorted(glob.glob(os.path.join(logdir, "**", "events.out.tfevents.*"), recursive=True))
    if not files:
        print("no event files under", logdir)
        return 1
    for path in files[-2:]:
        print("event file:", path, "(%d bytes)" % os.path.getsize(path))

    ea = event_accumulator.EventAccumulator(
        files[-1], size_guidance={event_accumulator.SCALARS: 0}
    )
    ea.Reload()

    if series:
        events = ea.Scalars(series)
        print("%s: %d point(s)" % (series, len(events)))
        head = events if len(events) <= 40 else events[:20]
        for event in head:
            print("  step=%6d  lr=%s" % (event.step, event.value))
        if len(events) > 40:
            print("  ...")
            for event in events[-20:]:
                print("  step=%6d  lr=%s" % (event.step, event.value))
        return 0
    tags = sorted(ea.Tags().get("scalars", []))
    if needle:
        tags = [t for t in tags if needle.lower() in t.lower()]
    print("%d scalar tag(s)" % len(tags))
    for tag in tags:
        if want_last:
            events = ea.Scalars(tag)
            print("%s  last=%.6g @step%d n=%d" % (tag, events[-1].value, events[-1].step, len(events)))
        else:
            print(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
