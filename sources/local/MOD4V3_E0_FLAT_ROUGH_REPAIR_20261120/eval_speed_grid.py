"""Measure signed speed tracking and stopping across the full stance range."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
import hashlib
from itertools import product
import json
from pathlib import Path

from eval_drive import COLUMNS, FAMILIES, load_showcase, np, run_case, torch

HEIGHTS = (.20, .28, .32, .36, .40, .42)
SPEEDS = (.20, .35, .50, .90, 1.20, 1.50, 2.00, 2.20)


def evaluate_group(item):
    checkpoint, output, terrain, height, direction, manifest = item
    torch.set_num_threads(1)
    output.mkdir(parents=True)
    show = load_showcase(output, checkpoint)
    rows, traces = [], {}
    family, level = FAMILIES[terrain]
    simulation = show.Replay(level=level, family=family)
    if manifest is not None:
        from play_e0_candidate import manifest_drive
        simulation.actor = manifest_drive(simulation.actor, manifest, json.loads(manifest.read_text(encoding='utf-8')))
    for speed in SPEEDS:
        command = direction * speed
        key = f'{terrain}_h{round(height*100):02}_v{command:+.2f}'
        seconds = 2.6 if speed <= .90 else 2.1
        row, trace = run_case(show, terrain, height, key, (-2.1*direction, .18*direction),
                              ((3.6, 0.), (seconds, command), (1.8, 0.)), simulation=simulation)
        row['speed_command_m_s'] = command
        rows.append(row)
        traces[key] = trace
    simulation.close()
    return rows, traces


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--blend-manifest', type=Path, help='Evaluate its E0 blend on the actor loaded by --model.')
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    model = args.model.resolve(strict=True)
    args.out.mkdir(parents=True)
    items = [(model, args.out/'scenes'/f'{terrain}_{round(h*100):02}_{sign:+d}', terrain, h, sign, args.blend_manifest)
             for terrain, h, sign in product(FAMILIES, HEIGHTS, (-1, 1))]
    rows, traces = [], {}
    with ProcessPoolExecutor(args.workers) as pool:
        for group, raw in pool.map(evaluate_group, items):
            rows.extend(group)
            traces.update(raw)
            example = group[0]
            print(example['terrain'], example['height'], int(np.sign(example['speed_command_m_s'])),
                  sum(row['complete'] for row in group), len(group), flush=True)
    np.savez_compressed(args.out/'rollouts.npz', **traces)
    result = dict(checkpoint=str(model), sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                  blend_manifest=str(args.blend_manifest) if args.blend_manifest else None,
                  trace_columns=COLUMNS, heights=list(HEIGHTS), absolute_speeds=list(SPEEDS), rows=rows)
    (args.out/'RESULT.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
