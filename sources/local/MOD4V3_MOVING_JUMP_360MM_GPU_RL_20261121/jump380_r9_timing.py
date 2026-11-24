"""Use the R8 champion's measured geometry for training and recalibrate R9 for replay."""
from argparse import ArgumentParser
import json
from pathlib import Path

from jump360_scene import HERE, json_save, sha
from jump380_r6_scene import KINDS
from jump380_r8_timing import JITTER_HIGH_M, JITTER_LOW_M, PRESS_GAP_M, lead_center

EXPERIMENT = "jump380_r9"
RUN = HERE / "evidence" / EXPERIMENT
PARENT_RUN = HERE / "evidence/jump380_r8"
PARENT = PARENT_RUN / "ppo/model_012m.pt"
PARENT_SHA = "4958dc3830f5bee87810a16d17dcec6afc9088953a2670997e875efdcd98ba93"
TRAIN_TIMING = RUN / "calibration/TRAIN_TIMING.json"


def training_table():
    source = PARENT_RUN / "TIMING.json"
    timing = json.loads(source.read_text(encoding="utf-8"))
    if (sha(PARENT) != PARENT_SHA or timing["checkpoint_sha256"] != PARENT_SHA
            or timing["physics_hz"] != 400 or timing["training"]):
        raise ValueError("R9 needs the 400 Hz measurements of R8 model_012m")
    timing.update(experiment=EXPERIMENT, training=True, source_timing_sha256=sha(source))
    cases = timing["cases"]
    speeds, heights = timing["speeds"], timing["heights"]
    if [(row["speed"], row["height"]) for row in cases] != [(s, h) for s in speeds for h in heights]:
        raise ValueError("Timing cases do not match the speed and height grid")
    for kind in KINDS[1:]:
        centers = []
        for row in cases:
            cell = row["obstacles"][kind]
            if cell["geometry"] is None:
                raise ValueError(f"Missing {kind} measurement at {row['speed']} m/s, {row['height']} m")
            cell["center_m"] = lead_center(cell["geometry"])
            cell["center_source"] = "measured"
            centers.append(cell["center_m"])
        timing[kind] = [centers[i:i + len(heights)] for i in range(0, len(centers), len(heights))]
        print(kind, f"{len(centers)} measured cells, lead {min(centers):.3f} to {max(centers):.3f} m")
    return timing


def calibrate(checkpoint, workers):
    from jump380_r8_timing import calibrate as measure_grid

    timing = measure_grid(checkpoint, workers)
    timing["experiment"] = EXPERIMENT
    return timing


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if args.checkpoint is None:
        json_save(args.out or TRAIN_TIMING, training_table())
    else:
        json_save(args.out or RUN / "TIMING.json", calibrate(args.checkpoint, args.workers))
