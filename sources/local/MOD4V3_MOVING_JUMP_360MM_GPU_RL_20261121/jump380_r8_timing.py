"""Set R8 press distances from 400 Hz measurement of the deployed policy."""

from argparse import ArgumentParser
from pathlib import Path

from jump360_scene import HERE, json_save
from jump380_r6_scene import KINDS

RUN = HERE / "evidence/jump380_r8"
PARENT = HERE / "evidence/jump380_r7/ppo/model_006m.pt"
PARENT_SHA = "6a8b3d18aecf781085aebbc1e239727df47b1844653a33e351372b9743b5a40d"
PRESS_GAP_M = .06
JITTER_LOW_M, JITTER_HIGH_M = -.02, .06


def lead_center(geometry):
    low, high = geometry["landing_window_m"]
    return (low + high)/2. if high >= low else low + .035


def calibrate(checkpoint, workers, training=False):
    from jump380_r7_timing import calibrate as measure_flat_grid

    # Reuse the parent timing replay protocol to compare the same 21 cells.
    timing = measure_flat_grid(checkpoint, workers)
    if training and timing["checkpoint_sha256"] != PARENT_SHA:
        raise ValueError("R8 training timing must be measured on R7 model_006m")
    timing["training"] = training
    timing["experiment"] = "jump380_r8"
    timing["training_press_floor_m"] = PRESS_GAP_M
    timing["training_jitter_m"] = [JITTER_LOW_M, JITTER_HIGH_M]
    timing["lead_center_rule"] = "midpoint if high >= low, otherwise low + 0.035 m"
    cases = timing["cases"]
    height_count = len(timing["heights"])
    for kind in KINDS[1:]:
        measured = [i for i, row in enumerate(cases) if row["obstacles"][kind]["geometry"]]
        if training and len(measured) != len(cases):
            raise ValueError(f"R8 parent geometry is missing at {len(cases)-len(measured)} {kind} cells")
        table = []
        for i, row in enumerate(cases):
            cell = row["obstacles"][kind]
            geometry = cell["geometry"]
            if geometry is not None:
                center = lead_center(geometry)
                cell["center_source"] = "measured"
            elif measured:
                x, y = divmod(i, height_count)
                nearest = min(measured, key=lambda j: abs(j//height_count-x) + abs(j%height_count-y))
                center = lead_center(cases[nearest]["obstacles"][kind]["geometry"])
                cell["center_source"] = "nearest_measured_grid_cell"
                cell["center_reference"] = {key: cases[nearest][key] for key in ("speed", "height")}
            else:
                center = row["overhang_m"] + PRESS_GAP_M
                cell["center_source"] = "measured_overhang_plus_press_floor"
            cell["center_m"] = center
            table.append(center)
        timing[kind] = [table[i:i+height_count] for i in range(0, len(table), height_count)]
        print(kind, f"{len(measured)}/{len(cases)} measured", f"lead {min(table):.3f}–{max(table):.3f} m")
    return timing


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=PARENT)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--training", action="store_true")
    args = parser.parse_args()
    timing = calibrate(args.checkpoint, args.workers, args.training)
    json_save(args.out, timing)
