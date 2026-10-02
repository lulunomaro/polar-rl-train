"""Windowed trend of a TensorBoard run: is the curve still moving, and in which direction?

Prints, per tag: the mean over consecutive 50-iteration windows, the least-squares slope
over the last 100 iterations, and the min/max (for the learning-rate flatness claim).

    python scripts/_tb_trend.py <run_dir> [tag_substring ...]
"""
import sys

from tensorboard.backend.event_processing import event_accumulator

path = sys.argv[1]
wanted = sys.argv[2:] or ["mean_episode_length", "mean_reward", "mean_std",
                          "bad_orientation", "learning_rate"]
WINDOW = 50

ea = event_accumulator.EventAccumulator(path, size_guidance={"scalars": 200000})
ea.Reload()


def slope(pts):
    n = len(pts)
    if n < 3:
        return float("nan")
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    den = sum((p[0] - mx) ** 2 for p in pts)
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / den if den else float("nan")


for tag in sorted(ea.Tags()["scalars"]):
    if not any(w in tag for w in wanted):
        continue
    sv = ea.Scalars(tag)
    pts = [(e.step, float(e.value)) for e in sv]
    if not pts:
        continue
    last = pts[-1][0]
    win = []
    lo = pts[0][0]
    while lo <= last:
        sel = [v for s, v in pts if lo <= s < lo + WINDOW]
        if sel:
            win.append("[%d-%d]=%.4g" % (lo, lo + WINDOW - 1, sum(sel) / len(sel)))
        lo += WINDOW
    tail = [p for p in pts if p[0] > last - 100]
    vals = [v for _, v in pts]
    print("== %s  (n=%d, last step %d)" % (tag, len(pts), last))
    print("   windows : " + "  ".join(win))
    print("   last100 slope/iter = %+.5g   mean=%.5g" % (slope(tail), sum(v for _, v in tail) / len(tail)))
    print("   min=%.6g  max=%.6g" % (min(vals), max(vals)))
