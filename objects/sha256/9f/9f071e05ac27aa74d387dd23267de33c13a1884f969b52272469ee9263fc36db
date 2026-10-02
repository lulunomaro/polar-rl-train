"""Patch rsl_rl's adaptive learning-rate controller so it steps ONCE per iteration.

Why this exists
---------------
rsl_rl 5.4 (``rsl_rl/algorithms/ppo.py``) applies the ``schedule="adaptive"`` update
inside the mini-batch loop.  With the config this project uses - 5 learning epochs and 4
mini-batches - a single iteration visits that block up to 20 times, and each visit can
divide the learning rate by 1.5.  Worst case in one iteration: 1.5**20 = 3325x.

Measured consequence (docs/DIAG_FLAT_V1_20260910.md): the CC warm start carried an Adam
state with lr = 3.8443e-4 into ``rm2025_later_flat_verify_v1``, which was configured for
1e-4.  The very first iteration drove it to the 1e-5 floor of the rsl_rl clamp and it
stayed there for the whole 300-iteration run, so the policy trained at one tenth of the
configured rate while ``Policy/mean_std`` barely moved.

What the patch does
-------------------
Keeps the KL computation where it is (it has to run per mini-batch) but applies the
actual lr change only on the first mini-batch of each epoch-sized group, and only once
per factor of 1.5, so one iteration can move the learning rate by at most 1.5x in either
direction.

Idempotent, and safe to re-run after a venv rebuild.  Usage:

    python scripts/patch_rsl_rl_adaptive_lr.py            # autodetect the vendored venv
    python scripts/patch_rsl_rl_adaptive_lr.py --path <.../rsl_rl/algorithms/ppo.py>
    python scripts/patch_rsl_rl_adaptive_lr.py --check    # exit 1 when NOT patched
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import shutil
import sys

MARK = "adaptive-lr fix (scripts/patch_rsl_rl_adaptive_lr.py)"
ANCHOR = 'if self.desired_kl is not None and self.schedule == "adaptive":'
START = "# Update the learning rate only on the main process"
END = 'param_group["lr"] = self.learning_rate'

GUARD = [
    "                    # --- adaptive-lr fix (scripts/patch_rsl_rl_adaptive_lr.py) ---",
    "                    # One lr step per iteration, not per mini-batch: 5 epochs x 4",
    "                    # mini-batches would otherwise allow 1.5**20 within a single",
    "                    # iteration, which is what pinned the flat run at 1e-5.",
    "                    self._kl_seen = getattr(self, \"_kl_seen\", 0) + 1",
    "                    _period = int(self.num_learning_epochs) * int(self.num_mini_batches)",
    "                    if (self._kl_seen - 1) % _period == 0:",
]

DEFAULT_CANDIDATES = [
    "third_party/rc_mjlab/.venv/lib/python3.12/site-packages/rsl_rl/algorithms/ppo.py",
]


def autodetect() -> pathlib.Path | None:
    here = pathlib.Path(__file__).resolve().parents[1]
    for rel in DEFAULT_CANDIDATES:
        p = here / rel
        if p.exists():
            return p
    for p in here.glob("**/site-packages/rsl_rl/algorithms/ppo.py"):
        return p
    return None


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    lines = text.splitlines(keepends=True)
    anchor = next((i for i, ln in enumerate(lines) if ANCHOR in ln), None)
    if anchor is None:
        raise SystemExit("anchor not found: %s" % ANCHOR)
    start = next((i for i in range(anchor, len(lines)) if START in lines[i]), None)
    if start is None:
        raise SystemExit("start marker not found after the anchor")
    end = next((i for i in range(start, len(lines)) if END in lines[i]), None)
    if end is None:
        raise SystemExit("end marker not found after the start marker")
    body = ["    " + ln if ln.strip() else ln for ln in lines[start:end + 1]]
    head = "".join(lines[:start])
    tail = "".join(lines[end + 1:])
    out = head + "\n".join(GUARD) + "\n" + "".join(body) + tail
    ast.parse(out)  # refuse to write anything that does not parse
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default="", help="path to rsl_rl/algorithms/ppo.py")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when the file is NOT patched; writes nothing")
    ap.add_argument("--no-backup", action="store_true")
    a = ap.parse_args()

    path = pathlib.Path(a.path) if a.path else autodetect()
    if path is None or not path.exists():
        print("could not locate rsl_rl/algorithms/ppo.py; pass --path", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    if a.check:
        patched = MARK in text
        print("%s : %s" % ("PATCHED" if patched else "NOT PATCHED", path))
        return 0 if patched else 1
    if MARK in text:
        print("already patched:", path)
        return 0
    out = patch_text(text)
    if not a.no_backup:
        shutil.copyfile(path, str(path) + ".orig")
    path.write_text(out, encoding="utf-8")
    print("patched:", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
